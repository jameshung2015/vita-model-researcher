# Phase 4 Quickstart (Agentic Augmentation)

Run the agentic orchestrator to plan, execute, and report Qwen3 metrics end-to-end.

Setup (Windows PowerShell)
- `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
- `pip install -U pip jsonschema`

Run
- Default Qwen3 variants, threshold 0.05:
  - `python agents-toolchain/agentic/orchestrator.py`

Outputs
- Reports: `reports/qwen3_phase4_<ts>/` (per-metric JSON, `current.json`, `diff.json`, `summary.md`)
- Summaries: `docs/summaries/*_<ts>.md`
- QA log: appended to `qa/qa_history.jsonl`

Notes
- No CI/GitHub Actions. Commit artifacts for historical traceability.

