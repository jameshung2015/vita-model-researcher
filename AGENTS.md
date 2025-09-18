# Repository Guidelines

## Project Structure & Module Organization
The repository tracks evaluation knowledge base assets. Core JSON/YAML sources live under `indicators/`, `models/`, `benchmarks/`, and `templates/`. Automation scripts sit in `scripts/` (validation, estimation, bench stubs) and `tools/` (QA logging, deployment notes). Scenario-specific assets go to `scenarios/` and product integrations to `product_lines/`. Keep auxiliary research notes in root Markdown files (`README.md`, `background.md`, `agentToolrequirement.md`); avoid mixing notes with structured data.

## Build, Test, and Development Commands
- `python scripts/validate_models.py` validates model entries against `templates/model_schema.json`.
- `python scripts/bench/latency_profiler.py --seed 42` runs the deterministic latency smoke test.
- `python scripts/eval/f1.py` computes reference F1 metrics used by indicator samples.
- `python tools/log_qa.py --question "..." --answer "..."` appends structured QA exchanges to `qa/qa_history.jsonl`.

## Coding Style & Naming Conventions
Prefer two-space indentation for JSON/YAML to match existing templates. Keep keys lowercase with snake_case identifiers (`metric_id`, `baseline_reference`). Markdown documents use ATX headers and sentence-case titles. Python scripts follow PEP 8, 88-character line width, and docstrings for public functions. File names should be descriptive and dash-separated (`deploy_bench_tools.md`) or snake_case for code (`estimate_vram.py`).

## Testing Guidelines
Add runnable stubs when contributing new metrics; mirror the command layout under `scripts/eval/` or `scripts/bench/`. Include example outputs inside the relevant README. Before submitting, execute schema validators for any JSON your change touches (extend `validate_models.py` or add sibling scripts). When adding tests, keep names aligned with the target metric (`test_latency_profile.json`, `test_toxicity_suite.md`) and update coverage notes in `TODO.md`.

## Commit & Pull Request Guidelines
Match the concise imperative style in history (`Type: summary with context`). Start commits with a capitalized category (`Docs`, `Add`, `Fix`) followed by a short description. Pull requests must list scope, impacted directories, validation commands run, and any follow-up tasks. Link internal issues where applicable and attach screenshots or logs for benchmark deltas.

## Security & Configuration Tips
Do not commit secrets or proprietary datasets. Reference external model cards instead of embedding weights. Document required environment variables in directory-level README files and scrub personal identifiers before uploading traces.
