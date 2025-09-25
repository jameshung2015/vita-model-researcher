# Phase 2 Quickstart

- Indicators (unified output):
  - `python scripts/eval/f1.py --gold gold.json --pred preds.json`
  - Output shape: `{ metric_id, value, ci, samples_used, meta }` (use `--legacy` for `{ precision, recall, f1 }`).
- Benchmark snapshot (LM Arena):
  - `python scripts/bench/lmarena_pull.py --out benchmarks/snapshots/lmarena/<ts>.json`
- Baseline diff:
  - `python scripts/bench/baseline_diff.py --prev <baseline.json> --curr <current.json> --threshold 0.05`
- Reports layout:
  - `reports/<model>_<scenario>_<ts>/{baseline.json,current.json,diff.json,summary.md}`

Validation
- Schema checks: `python scripts/validate_models.py`
- Safety: `python tools/check_sensitive.py`
