#!/usr/bin/env python3
"""
Run a supported indicator by id and emit unified_v1 JSON to --out.

Supported ids:
  - win_rate (requires snapshot; will call lmarena_pull if --snapshot missing)
  - elo_rating (same as above)
  - latency_p99 (wraps latency_profiler.py)
  - throughput_rps (wraps load_test.py)
  - toxicity (wraps toxicity_check.py)
  - accuracy_f1 (delegates to scripts/eval/f1.py which already emits unified)
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args, check=True):
    proc = subprocess.run(args, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc


def ensure_snapshot(models: list[str], snapshot: Path|None) -> Path:
    if snapshot and snapshot.exists():
        return snapshot
    ts = int(time.time())
    out = ROOT / f"benchmarks/snapshots/lmarena/{ts}.json"
    args = [sys.executable, str(ROOT / 'scripts/bench/lmarena_pull.py'),
            '--models', ','.join(models), '--fields', 'model,elo,rank,votes,win_rate',
            '--out', str(out)]
    run_cmd(args)
    return out


def run_win_rate(models: list[str], out: Path, snapshot: Path|None):
    snap = ensure_snapshot(models, snapshot)
    args = [sys.executable, str(ROOT / 'scripts/bench/normalize_unified.py'),
            '--in', str(snap), '--out', str(out), '--metric', 'win_rate', '--models', ','.join(models)]
    run_cmd(args)


def run_elo(models: list[str], out: Path, snapshot: Path|None):
    snap = ensure_snapshot(models, snapshot)
    args = [sys.executable, str(ROOT / 'scripts/bench/normalize_unified.py'),
            '--in', str(snap), '--out', str(out), '--metric', 'elo_rating', '--models', ','.join(models)]
    run_cmd(args)


def run_latency_p99(seed: int|None, out: Path):
    args = [sys.executable, str(ROOT / 'scripts/bench/latency_profiler.py')]
    if seed is not None:
        args += ['--seed', str(seed)]
    proc = run_cmd(args)
    stats = json.loads(proc.stdout.strip())
    item = {"metric_id": "latency_p99", "value": stats.get('p99_ms'), "ci": None, "samples_used": None,
            "meta": {"p50_ms": stats.get('p50_ms'), "p90_ms": stats.get('p90_ms'), "seed": seed}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([item], ensure_ascii=False, indent=2), encoding='utf-8')


def run_throughput(concurrency: int, out: Path):
    args = [sys.executable, str(ROOT / 'scripts/bench/load_test.py'), '--concurrency', str(concurrency)]
    proc = run_cmd(args)
    res = json.loads(proc.stdout.strip())
    item = {"metric_id": "throughput_rps", "value": res.get('rps'), "ci": None, "samples_used": None,
            "meta": {"concurrency": res.get('concurrency'), "error_rate": res.get('error_rate')}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([item], ensure_ascii=False, indent=2), encoding='utf-8')


def run_toxicity(outputs: Path|None, out: Path):
    args = [sys.executable, str(ROOT / 'scripts/eval/toxicity_check.py')]
    if outputs:
        args += ['--outputs', str(outputs)]
    proc = run_cmd(args)
    res = json.loads(proc.stdout.strip())
    item = {"metric_id": "toxicity_rate", "value": res.get('toxicity_rate'), "ci": None,
            "samples_used": res.get('num_samples'),
            "meta": {"num_toxic": res.get('num_toxic')}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([item], ensure_ascii=False, indent=2), encoding='utf-8')


def run_f1(gold: Path, pred: Path, out: Path):
    args = [sys.executable, str(ROOT / 'scripts/eval/f1.py'), '--gold', str(gold), '--pred', str(pred)]
    proc = run_cmd(args)
    # f1.py emits unified_v1 (single item)
    item = json.loads(proc.stdout.strip())
    arr = item if isinstance(item, list) else [item]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(arr, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--id', required=True, help='indicator id, e.g., win_rate, elo_rating, latency_p99, throughput_rps, toxicity, accuracy_f1')
    ap.add_argument('--models', type=str, default='', help='comma-separated models (for win_rate/elo)')
    ap.add_argument('--model', type=str, default=None, help='single model tag for latency/throughput/toxicity/f1 meta')
    ap.add_argument('--snapshot', type=Path, default=None, help='existing leaderboard snapshot file')
    ap.add_argument('--seed', type=int, default=None, help='seed for latency stub')
    ap.add_argument('--concurrency', type=int, default=50, help='for throughput stub')
    ap.add_argument('--toxicity-outputs', type=Path, default=None)
    ap.add_argument('--gold', type=Path)
    ap.add_argument('--pred', type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()

    mid = args.id.strip().lower()
    models = [m.strip() for m in args.models.split(',') if m.strip()]

    def _inject_model(path: Path, model: str | None):
        if not model:
            return
        try:
            data = json.loads(path.read_text(encoding='utf-8-sig'))
        except Exception:
            data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, list):
            for it in data:
                meta = it.get('meta') or {}
                if 'model' not in meta:
                    meta['model'] = model
                    it['meta'] = meta
        else:
            meta = data.get('meta') or {}
            if 'model' not in meta:
                meta['model'] = model
                data['meta'] = meta
            data = [data]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    if mid == 'win_rate':
        if not models:
            raise SystemExit('win_rate requires --models')
        run_win_rate(models, args.out, args.snapshot)
    elif mid == 'elo_rating':
        if not models:
            raise SystemExit('elo_rating requires --models')
        run_elo(models, args.out, args.snapshot)
    elif mid == 'latency_p99':
        run_latency_p99(args.seed, args.out)
        _inject_model(args.out, args.model)
    elif mid == 'throughput_rps':
        run_throughput(args.concurrency, args.out)
        _inject_model(args.out, args.model)
    elif mid == 'toxicity':
        run_toxicity(args.toxicity_outputs, args.out)
        _inject_model(args.out, args.model)
    elif mid == 'accuracy_f1':
        if not (args.gold and args.pred):
            raise SystemExit('accuracy_f1 requires --gold and --pred')
        run_f1(args.gold, args.pred, args.out)
        _inject_model(args.out, args.model)
    else:
        raise SystemExit(f'Unsupported indicator id: {args.id}')


if __name__ == '__main__':
    main()
