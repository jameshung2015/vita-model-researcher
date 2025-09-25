# Repository Guidelines

## Project Structure & Module Organization
- `indicators/` Metrics pool and templates (YAML/JSON definitions, runbooks, examples).
- `models/` Model specs and variants (JSON, schema: `templates/model_schema.json`).
- `benchmarks/` Benchmark catalogs and model references (JSON; index in `benchmarks/index.md`).
- `product_lines/` PRD-to-metric traceability entries (see `templates/product_line*.json`).
- `platforms/`, `tools/`, `agents-toolchain/` Operational docs and helper scripts.
- `scripts/` Runnable stubs and utilities used by the KB (eval, bench, estimates).
- `templates/` Canonical schemas and starter templates.
- `qa/qa_history.jsonl` Append-only Q&A log (written by tools/scripts).

## Build, Test, and Development Commands
- Python env (Windows PowerShell):
  - `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
  - `pip install -U pip jsonschema`
- Schema checks: `python scripts/validate_models.py` (validates `models/*.json` against schema).
- Heuristic VRAM sizing: `python scripts/estimate_vram.py --variant Qwen3-8B --seq_len 32768 --precision fp16`.
- Bench stubs: `python scripts/bench/latency_profiler.py --seed 42`, `python scripts/bench/load_test.py --concurrency 50`.
- Safety scan: `python tools/check_sensitive.py` (reports likely secrets or files to ignore).

## Coding Style & Naming Conventions
- Files: UTF-8 (no BOM). Prefer English/pinyin names with semantic prefixes, e.g. `indicators/accuracy/f1.yaml`.
- JSON/YAML: 2-space indent; snake_case keys; include `id`, `name`, `source/owner` where applicable.
- Python: PEP 8, 4-space indent; script names in `snake_case.py` under `scripts/`.
- IDs and references: use stable, lowercase identifiers (e.g., `pl_autonomous_navigation_v1`).

## Testing Guidelines
- Required: run schema checks before PRs (`scripts/validate_models.py`).
- Smoke tests: run bench/eval stubs in `scripts/` to verify examples execute.
- New entries: provide a sample in `templates/` if you introduce a new schema; keep `qa/qa_history.jsonl` append-only (updated by tooling).

## Commit & Pull Request Guidelines
- Commits: concise, imperative, Conventional-Commits style types used in this repo: `docs`, `chore`, `add`, `fix`, `refactor`, `sync`.
  - Example: `docs: expand layout and directory guidance`.
- PRs must include: purpose and scope, linked issue (if any), affected paths, validation output (schema check), and before/after snippets or screenshots for docs.

## Security & Configuration Tips
- Do not commit secrets or private data; keep `.env` local. Run `python tools/check_sensitive.py` before pushing.
- Document required environment variables in `README.md` or the relevant tool doc.

## Agent Playbook
- Day‑to‑day commands (PowerShell):
  - Validate models: `python agents-toolchain/governance/validate_models_cli.py --report`
  - Build taxonomy: `python agents-toolchain/governance/build_taxonomy.py`
  - Diff taxonomy: `python agents-toolchain/governance/diff_taxonomy.py taxonomy_versions/old.json taxonomy_versions/new.json --out reports`
  - Phase 5 checks: `python scripts/governance/run_phase5_checks.py --report --threshold 0.95`
- Add a new model:
  - Create `models/<name>.json` following `templates/model_schema.json`.
  - Run schema validation and update taxonomy snapshot.
- Add a new benchmark:
  - Create `benchmarks/<id>.json` (see `templates/benchmark_template.json`).
  - Link to upstream repo, tasks covered, and any model references.
- QA logging:
  - Append Q&A cases to `qa/qa_history.jsonl` as JSONL entries with fields like `{ ts, q, a, tags }`.
