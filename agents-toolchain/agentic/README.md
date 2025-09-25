Agentic Orchestrator — Phase 4 Quickstart
=========================================

This folder contains a small orchestration CLI to run Phase 4 (Agentic Augmentation) end-to-end for Qwen3 variants without CI.

Quickstart (Windows PowerShell)
- Create venv and install deps: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -U pip jsonschema`
- Run orchestrator with defaults (Qwen3 variants, threshold 0.05):
  - `python agents-toolchain/agentic/orchestrator.py`
- Outputs:
  - `reports/qwen3_phase4_<ts>/` with per-metric JSON, merged `current.json`, `diff.json`, and `summary.md`.
  - Markdown summaries in `docs/summaries/`.
  - QA log appended to `qa/qa_history.jsonl`.

Options
- `--models` Comma-separated models (default: Qwen3-4B,Qwen3-8B,Qwen3-30B-A3B,Qwen3-235B-A22B)
- `--threshold` Baseline diff threshold (default: 0.05)
- `--outdir` Output reports directory (default: auto `reports/qwen3_phase4_<ts>`)
- `--baseline` Path to baseline.json (default: latest under `reports/baselines/qwen3/*/baseline.json` if present)

