"""
Improved VRAM estimator for Qwen3 variants.

Notes:
- This script uses simple, explainable heuristics to estimate memory needs for planning.
- It supports splitting weights across multiple GPUs (simple division), batch scaling, and a naive MoE overhead factor.
- For production use, run per-variant micro-benchmarks on target infra.
"""

import argparse
import json
import os
import re


ROOT = os.path.dirname(os.path.dirname(__file__))
MODEL_FILE = os.path.join(ROOT, 'models', 'qwen3.json')

with open(MODEL_FILE, 'r', encoding='utf-8') as f:
    qwen = json.load(f)

VARIANT_MAP = {v['name']: v for v in qwen['variants']}


def parse_params_str(pstr):
    m = re.search(r"(\d+(?:\.\d+)?)", str(pstr))
    if not m:
        return None
    return float(m.group(1))


def estimate_vram(variant_name, seq_len, batch, precision, num_gpus=1, assume_moe=None):
    v = VARIANT_MAP.get(variant_name)
    if not v:
        raise ValueError('Unknown variant: ' + variant_name)

    p = parse_params_str(v.get('params', ''))
    if p is None:
        # fallback: try to infer from name
        for key in ['235', '30', '8', '4', '1']:
            if key in variant_name:
                p = float(key)
                break
    if p is None:
        p = 30.0

    # Precision bytes per parameter (weights)
    bytes_per_param = 2 if precision == 'fp16' else 1  # int8 ~1 byte

    # Weight resident memory (GB) approx = params (billion) * bytes_per_param (bytes) / (1024^3) * 1e9 ~ p * bytes_per_param
    # Using p * bytes gives approximate GB (1e9 bytes ~ 1GB). Good enough for planning.
    weight_gb = p * bytes_per_param

    # Activation memory: heuristic per token scales with model size.
    # activ_mem_per_token_gb = base_activation_factor * p
    # choose base_activation_factor so that for 8B and seq 4096 we get a few GB
    base_activation_factor = 5e-7  # GB per token per billion params at fp16
    if precision == 'int8':
        base_activation_factor *= 0.6

    activations_gb = seq_len * batch * base_activation_factor * p

    # Key-value cache (for generation) roughly similar order as activations but often smaller per-token factor
    kv_factor = 2e-7
    kv_cache_gb = seq_len * batch * kv_factor * p

    # Overhead (optimizer state, workspace, CUDA context) - conservative floor
    overhead_gb = max(4.0, weight_gb * 0.08)

    total_gb = weight_gb + activations_gb + kv_cache_gb + overhead_gb

    # MoE adjustments
    is_moe = False
    if assume_moe is None:
        is_moe = 'A' in variant_name or 'MoE' in str(v.get('name', ''))
    else:
        is_moe = bool(assume_moe)
    moe_overhead = 0.0
    if is_moe:
        # routing tables and expert activations add overhead; estimate +20-40%
        moe_overhead = 0.30 * (activations_gb + kv_cache_gb)
        total_gb += moe_overhead

    # Distributed split: naive division of weight and activations across GPUs
    if num_gpus > 1:
        per_gpu_weights = weight_gb / num_gpus
        per_gpu_activations = activations_gb / num_gpus
        per_gpu_kv = kv_cache_gb / num_gpus
        per_gpu_overhead = overhead_gb / num_gpus
        per_gpu_total = per_gpu_weights + per_gpu_activations + per_gpu_kv + per_gpu_overhead + moe_overhead / max(1, num_gpus)
    else:
        per_gpu_total = total_gb

    # Quantization effect (weights already accounted by bytes_per_param). Apply small multiplier for runtime efficiency
    if precision == 'int8':
        # int8 reduces some activation/weight memory but runtime overhead may remain
        per_gpu_total *= 0.7

    return {
        'variant': variant_name,
        'params_estimate_billion': p,
        'seq_len': seq_len,
        'batch': batch,
        'precision': precision,
        'num_gpus': num_gpus,
        'is_moe': is_moe,
        'estimated_vram_gb_per_gpu': round(per_gpu_total, 2),
        'estimated_vram_gb_total': round(total_gb, 2),
        'breakdown': {
            'weight_gb': round(weight_gb, 2),
            'activations_gb': round(activations_gb, 2),
            'kv_cache_gb': round(kv_cache_gb, 2),
            'moe_overhead_gb': round(moe_overhead, 2),
            'overhead_gb': round(overhead_gb, 2)
        },
        'note': 'Estimates are heuristic. For production, benchmark on target infra and consult modelcard for exact requirements.'
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', required=True)
    parser.add_argument('--seq_len', type=int, default=None, help='sequence length (tokens). If omitted, read from model defaults')
    parser.add_argument('--batch', type=int, default=1)
    parser.add_argument('--precision', choices=['fp16', 'int8'], default='fp16')
    parser.add_argument('--num_gpus', type=int, default=None, help='number of GPUs to split model across (naive division). If omitted, read from model/defaults')
    parser.add_argument('--moe', action='store_true', help='assume MoE overhead (if not auto-detected)')
    args = parser.parse_args()

    # Resolve defaults from model metadata if seq_len or num_gpus not provided
    v = VARIANT_MAP.get(args.variant)
    if not v:
        raise SystemExit(f'Unknown variant: {args.variant}')

    def parse_token_count(s):
        if not s:
            return None
        s = str(s).lower()
        # look for patterns like '32k', '32,768', '256k', '1m', 'up to 1m'
        m = re.search(r"(\d+[\,\d]*\.?\d*)\s*([km]?)", s)
        if not m:
            return None
        num = m.group(1).replace(',', '')
        try:
            val = float(num)
        except ValueError:
            return None
        suf = m.group(2)
        if suf == 'k':
            return int(val * 1000)
        if suf == 'm':
            return int(val * 1000000)
        return int(val)

    # seq_len default: try explicit default, then parse first context_windows entry
    if args.seq_len is None:
        seq_len = None
        if 'default_seq_len' in v:
            seq_len = int(v['default_seq_len'])
        else:
            cw = v.get('context_windows') or []
            if cw:
                seq_len = parse_token_count(cw[0])
        if seq_len is None:
            seq_len = 4096
        used_seq_info = f'from model ({seq_len})' if args.seq_len is None else 'from CLI'
    else:
        seq_len = args.seq_len
        used_seq_info = 'from CLI'

    # num_gpus default: try explicit default, then infer from hardware_recommendations estimated_vram_fp16
    if args.num_gpus is None:
        # prefer explicit default in model metadata
        if 'default_num_gpus' in v:
            num_gpus = int(v['default_num_gpus'])
            used_gpu_info = f'from model.default_num_gpus ({num_gpus})'
        else:
            num_gpus = 1
            hr = v.get('hardware_recommendations') or {}
            est_vram = hr.get('estimated_vram_fp16')
            if est_vram:
                # extract first number from string
                m = re.search(r"(\d+(?:\.\d+)?)", str(est_vram))
                if m:
                    try:
                        per_gpu = float(m.group(1))
                        # compute weight_gb from params (assume fp16 bytes per param -> weight_gb = p*2)
                        p = parse_params_str(v.get('params', '')) or 30.0
                        weight_gb = p * 2
                        import math
                        num_gpus = max(1, math.ceil(weight_gb / per_gpu))
                    except Exception:
                        num_gpus = 1
            used_gpu_info = f'inferred from model ({num_gpus})'
    else:
        num_gpus = args.num_gpus
        used_gpu_info = 'from CLI'

    res = estimate_vram(args.variant, seq_len, args.batch, args.precision, num_gpus=num_gpus, assume_moe=args.moe if args.moe else None)
    # attach info about defaults used
    res['_defaults_used'] = {
        'seq_len_source': used_seq_info,
        'num_gpus_source': used_gpu_info
    }
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
