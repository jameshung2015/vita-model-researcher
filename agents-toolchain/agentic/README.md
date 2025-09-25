Agentic Orchestrator — Phase 4 Quickstart
=========================================

This folder contains a small orchestration CLI to run Phase 4 (Agentic Augmentation) end-to-end for Qwen3 variants without CI.

Quickstart (Windows PowerShell)
- Create venv and install deps: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -U pip jsonschema`
- Run orchestrator with defaults (Qwen3 variants, threshold 0.05):
  - `python agents-toolchain/agentic/orchestrator.py`
- Custom models/indicators:
  - Explicit models: `python agents-toolchain/agentic/orchestrator.py --models "ModelA,ModelB" --indicators "latency_p99,throughput_rps"`
  - From models file: `python agents-toolchain/agentic/orchestrator.py --modelset file:models/qwen3.json --indicators "wr,elo,latency_p99,f1"`
  - Named set (default 'qwen3'): `python agents-toolchain/agentic/orchestrator.py --modelset qwen3 --threshold 0.02`
- Outputs:
  - `reports/qwen3_phase4_<ts>/` with per-metric JSON, merged `current.json`, `diff.json`, and `summary.md`.
  - Markdown summaries in `docs/summaries/`.
  - QA log appended to `qa/qa_history.jsonl`.

Options
- `--models` Comma-separated explicit models
- `--modelset` Named set (e.g. `qwen3`), comma list, or `file:<models.json>`
- `--indicators` Comma list; supported: win_rate, elo_rating, latency_p99, throughput_rps, toxicity, accuracy_f1 (aliases: wr, elo, toxicity_rate, f1)
- `--threshold` Baseline diff threshold (default: 0.05)
- `--outdir` Output reports directory (default: auto `reports/qwen3_phase4_<ts>`)
- `--baseline` Path to baseline.json (default: latest under `reports/baselines/qwen3/*/baseline.json` if present)
