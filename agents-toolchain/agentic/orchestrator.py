#!/usr/bin/env python3
"""
Phase 4 Agentic Orchestrator

Plans and runs a Qwen3-first metrics sweep, merges results, diffs against a baseline,
and emits markdown summaries. Designed to be Windows-friendly (UTF-8, no shell utils).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUPPORTED = [
    'win_rate',
    'elo_rating',
    'latency_p99',
    'throughput_rps',
    'toxicity',
    'accuracy_f1',
]
ALIASES = {
    'wr': 'win_rate',
    'elo': 'elo_rating',
    'toxicity_rate': 'toxicity',
    'f1': 'accuracy_f1',
}


def run_cmd(args, check=True):
    proc = subprocess.run(args, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return proc


def now_ts() -> int:
    return int(time.time())


def latest_baseline_dir(model_name: str) -> Path | None:
    base = ROOT / 'reports' / 'baselines' / model_name
    if not base.exists():
        return None
    dirs = sorted([p for p in base.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0] if dirs else None


def ensure_snapshot(models: list[str]) -> Path:
    ts = now_ts()
    out = ROOT / f"benchmarks/snapshots/lmarena/{ts}.json"
    args = [sys.executable, str(ROOT / 'scripts/bench/lmarena_pull.py'),
            '--models', ','.join(models), '--fields', 'model,elo,rank,votes,win_rate', '--out', str(out)]
    run_cmd(args)
    return out


def load_variants_from_models_file(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
    except Exception:
        data = json.loads(path.read_text(encoding='utf-8'))
    vars = []
    for v in data.get('variants', []) or []:
        name = v.get('name')
        if name:
            vars.append(name)
    return vars


def resolve_models_arg(models_arg: str | None, modelset: str | None) -> list[str]:
    if models_arg:
        return [m.strip() for m in models_arg.split(',') if m.strip()]
    if modelset:
        if modelset.startswith('file:'):
            p = modelset.split(':', 1)[1]
            file_path = (ROOT / p) if not os.path.isabs(p) else Path(p)
            return load_variants_from_models_file(file_path)
        if modelset.lower() == 'qwen3':
            qpath = ROOT / 'models' / 'qwen3.json'
            if qpath.exists():
                return load_variants_from_models_file(qpath)
            return ['Qwen3-4B', 'Qwen3-8B', 'Qwen3-30B-A3B', 'Qwen3-235B-A22B']
        # treat comma-separated sets as explicit model list
        if ',' in modelset:
            return [m.strip() for m in modelset.split(',') if m.strip()]
    # default to Qwen3 set
    return ['Qwen3-4B', 'Qwen3-8B', 'Qwen3-30B-A3B', 'Qwen3-235B-A22B']


def normalize_indicators(indicators: list[str]) -> list[str]:
    out = []
    for k in indicators:
        k2 = ALIASES.get(k.strip().lower(), k.strip().lower())
        if k2 not in SUPPORTED:
            # skip unknown indicators silently to keep runs resilient
            continue
        out.append(k2)
    # preserve order and dedupe
    seen = set()
    res = []
    for k in out:
        if k not in seen:
            res.append(k)
            seen.add(k)
    return res


def write_qa(event: dict):
    qa_dir = ROOT / 'qa'
    qa_dir.mkdir(parents=True, exist_ok=True)
    qa_file = qa_dir / 'qa_history.jsonl'
    line = json.dumps(event, ensure_ascii=False)
    with qa_file.open('a', encoding='utf-8') as f:
        f.write(line + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--models', type=str, default=None, help='comma-separated explicit models')
    ap.add_argument('--modelset', type=str, default='qwen3', help="named set (e.g., 'qwen3'), comma list, or file:<models.json>")
    ap.add_argument('--indicators', type=str, default=','.join(SUPPORTED), help=f"which indicators to run (aliases: {','.join(ALIASES.keys())})")
    ap.add_argument('--threshold', type=float, default=0.05)
    ap.add_argument('--outdir', type=Path, default=None)
    ap.add_argument('--baseline', type=Path, default=None)
    args = ap.parse_args()

    models = resolve_models_arg(args.models, args.modelset)
    indicators = normalize_indicators([s for s in args.indicators.split(',') if s.strip()])
    ts = now_ts()
    outdir = args.outdir or (ROOT / f'reports/qwen3_phase4_{ts}')
    outdir.mkdir(parents=True, exist_ok=True)

    # Snapshot if needed
    needs_snapshot = any(mid in indicators for mid in ('win_rate', 'elo_rating'))
    snapshot = ensure_snapshot(models) if needs_snapshot else None

    # Metrics selected
    win_json = outdir / 'win_rate.json'
    elo_json = outdir / 'elo_rating.json'
    if 'win_rate' in indicators:
        run_cmd([sys.executable, str(ROOT / 'scripts/run_indicator.py'), '--id', 'win_rate',
                 '--models', ','.join(models), '--snapshot', str(snapshot), '--out', str(win_json)])
    if 'elo_rating' in indicators:
        run_cmd([sys.executable, str(ROOT / 'scripts/run_indicator.py'), '--id', 'elo_rating',
                 '--models', ','.join(models), '--snapshot', str(snapshot), '--out', str(elo_json)])

    # 2) latency_p99, throughput_rps, toxicity: per model
    per_metric = []
    for mid, extra in (
        ('latency_p99', ['--seed', '42']),
        ('throughput_rps', ['--concurrency', '50']),
        ('toxicity', []),
    ):
        if mid not in indicators:
            continue
        metric_files = []
        for m in models:
            out = outdir / f"{mid}_{m}.json"
            cmd = [sys.executable, str(ROOT / 'scripts/run_indicator.py'), '--id', mid, '--model', m, '--out', str(out)] + extra
            run_cmd(cmd)
            metric_files.append(out)
        # Merge per-model files into a combined metric file for convenience
        combined = outdir / f"{mid}.json"
        run_cmd([sys.executable, str(ROOT / 'scripts/report/merge_unified.py'), '--out', str(combined)] + [str(p) for p in metric_files])
        per_metric.append(combined)

    # 3) accuracy_f1: create tiny gold/pred demo and run once per model
    if 'accuracy_f1' in indicators:
        gold = outdir / 'f1_gold.json'
        pred = outdir / 'f1_pred.json'
        if not gold.exists():
            gold.write_text(json.dumps(["a", "b", "c"], ensure_ascii=False, indent=2), encoding='utf-8')
        if not pred.exists():
            pred.write_text(json.dumps(["a", "x", "c"], ensure_ascii=False, indent=2), encoding='utf-8')
        f1_files = []
        for m in models:
            f1_out = outdir / f"f1_{m}.json"
            run_cmd([sys.executable, str(ROOT / 'scripts/run_indicator.py'), '--id', 'accuracy_f1', '--model', m,
                     '--gold', str(gold), '--pred', str(pred), '--out', str(f1_out)])
            f1_files.append(f1_out)
        f1_combined = outdir / 'f1.json'
        run_cmd([sys.executable, str(ROOT / 'scripts/report/merge_unified.py'), '--out', str(f1_combined)] + [str(p) for p in f1_files])
    else:
        f1_combined = outdir / 'f1.json'  # may not exist, handled later

    # Merge all metric arrays into current.json
    metric_jsons = [win_json, elo_json, *(outdir.glob('latency_p99*.json')), *(outdir.glob('throughput_rps*.json')), *(outdir.glob('toxicity*.json')), f1_combined]
    # filter out per-model duplicates if both combined and per-model exist for the same metric
    # keep only the combined for latency/throughput/toxicity + per-model files remain for traceability
    merged_inputs = [str(p) for p in [win_json, elo_json, outdir / 'latency_p99.json', outdir / 'throughput_rps.json', outdir / 'toxicity.json', f1_combined] if p.exists()]
    current_json = outdir / 'current.json'
    run_cmd([sys.executable, str(ROOT / 'scripts/report/merge_unified.py'), '--out', str(current_json)] + merged_inputs)

    # Baseline diff
    baseline = args.baseline
    if baseline is None:
        latest = latest_baseline_dir('qwen3')
        baseline = latest / 'baseline.json' if latest else None
    diff_json = outdir / 'diff.json'
    summary_md = outdir / 'summary.md'
    if baseline and Path(baseline).exists():
        # Ensure diff.json path is not an existing directory from any previous runs
        if diff_json.exists() and diff_json.is_dir():
            try:
                os.rmdir(diff_json)
            except OSError:
                pass
        run_cmd([sys.executable, str(ROOT / 'scripts/bench/baseline_diff.py'), '--prev', str(baseline), '--curr', str(current_json), '--out_dir', str(outdir), '--threshold', str(args.threshold)])
        # Per-metric markdowns
        summary_inputs = []
        if 'win_rate' in indicators:
            summary_inputs.append(win_json)
        if 'elo_rating' in indicators:
            summary_inputs.append(elo_json)
        if 'latency_p99' in indicators:
            summary_inputs.append(outdir / 'latency_p99.json')
        if 'throughput_rps' in indicators:
            summary_inputs.append(outdir / 'throughput_rps.json')
        if 'toxicity' in indicators:
            summary_inputs.append(outdir / 'toxicity.json')
        if 'accuracy_f1' in indicators:
            summary_inputs.append(f1_combined)
        for p in summary_inputs:
            if p.exists() and p.is_file():
                md_out = ROOT / 'docs/summaries' / f"{p.stem}_{ts}.md"
                md_out.parent.mkdir(parents=True, exist_ok=True)
                run_cmd([sys.executable, str(ROOT / 'scripts/report/unified_to_md.py'), '--in', str(p), '--out', str(md_out)])
    else:
        # No baseline: just write per-metric markdowns and leave diff empty
        # If a previous run accidentally created a directory named diff.json, clear it
        if diff_json.exists() and diff_json.is_dir():
            try:
                os.rmdir(diff_json)
            except OSError:
                pass
        diff_json.write_text(json.dumps({"note": "no baseline"}, ensure_ascii=False, indent=2), encoding='utf-8')
        summary_inputs = []
        if 'win_rate' in indicators:
            summary_inputs.append(win_json)
        if 'elo_rating' in indicators:
            summary_inputs.append(elo_json)
        if 'latency_p99' in indicators:
            summary_inputs.append(outdir / 'latency_p99.json')
        if 'throughput_rps' in indicators:
            summary_inputs.append(outdir / 'throughput_rps.json')
        if 'toxicity' in indicators:
            summary_inputs.append(outdir / 'toxicity.json')
        if 'accuracy_f1' in indicators:
            summary_inputs.append(f1_combined)
        for p in summary_inputs:
            if p.exists() and p.is_file():
                md_out = ROOT / 'docs/summaries' / f"{p.stem}_{ts}.md"
                md_out.parent.mkdir(parents=True, exist_ok=True)
                run_cmd([sys.executable, str(ROOT / 'scripts/report/unified_to_md.py'), '--in', str(p), '--out', str(md_out)])
        summary_md.write_text("No baseline found; diff skipped.\n", encoding='utf-8')

    # Write QA log entry
    write_qa({
        "ts": ts,
        "phase": "phase4",
        "models": models,
        "outdir": str(outdir.relative_to(ROOT)),
        "snapshot": (str(snapshot.relative_to(ROOT)) if snapshot else None),
        "baseline": str(baseline.relative_to(ROOT)) if baseline else None,
        "threshold": args.threshold,
        "status": "ok"
    })

    print(str(outdir))


if __name__ == '__main__':
    main()
