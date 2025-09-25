# Reports and Baselines

- Baseline layout: `reports/<model>_<scenario>_<ts>/baseline.json`
- Diff artifacts: `diff.json`, `summary.md` written next to the current file by `baseline_diff.py`.

Unified metric item (unified_v1):
- Keys: `metric_id`, `value`, `ci`, `samples_used`, `meta`
- Example: `{ "metric_id": "accuracy_f1", "value": 0.80, "ci": null, "samples_used": 100, "meta": {"precision": 0.82, "recall": 0.78} }`

Quickstart (PowerShell):
- Create a baseline JSON (example):
  - `mkdir reports\\qwen3-8b_clsF1_0000000000`
  - `echo {\"metric_id\":\"accuracy_f1\",\"value\":0.80,\"ci\":null,\"samples_used\":100,\"meta\":{}} > reports\\qwen3-8b_clsF1_0000000000\\baseline.json`
- Run a new evaluation (unified):
  - `python scripts\\eval\\f1.py --gold gold.json --pred preds.json > reports\\qwen3-8b_clsF1_0000000000\\current.json`
- Diff:
  - `python scripts\\bench\\baseline_diff.py --prev reports\\qwen3-8b_clsF1_0000000000\\baseline.json --curr reports\\qwen3-8b_clsF1_0000000000\\current.json --threshold 0.05`
