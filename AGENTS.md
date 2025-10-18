# AGENTS.md

This file provides guidance to Qoder (qoder.com) when working with code in this repository.

## Project Overview

Chinese Large Language Model Evaluation Framework and Knowledge Base - a research-oriented project for systematically evaluating and cataloging AI models, with emphasis on automotive applications. Uses JSON/YAML-based structured storage with schema validation for traceable research workflows.

## Project Structure & Module Organization
- `indicators/` Metrics pool and templates (JSON definitions with runbooks and examples).
- `models/` Model specs and variants (JSON, schema: `templates/model_schema.json`).
- `benchmarks/` Benchmark catalogs (100+ benchmarks) and model references (JSON; index in `benchmarks/index.md`).
- `product_lines/` PRD-to-metric traceability entries (see `templates/product_line*.json`).
- `scripts/` Runnable evaluation, benchmark, and governance utilities (eval/, bench/, governance/, report/).
- `agents-toolchain/` Governance, ingestion, orchestration, and BI tools (governance/, agentic/, bi/).
- `templates/` Canonical schemas and starter templates for all data types.
- `tools/` Helper scripts (sensitive data check, examples, documentation).
- `qa/qa_history.jsonl` Append-only Q&A log (written by tools/scripts).
- `reports/` Generated validation reports and baselines.
- `taxonomy_versions/` Taxonomy snapshots for auditing.

## Key Commands

### Environment Setup (Windows PowerShell)
- `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
- `pip install -U pip jsonschema`

### Validation & Governance (Phase 5)
- Full governance checks: `python scripts/governance/run_phase5_checks.py --report --threshold 0.95`
- Model schema validation: `python scripts/validate_models.py` or `python agents-toolchain/governance/validate_models_cli.py --report`
- Taxonomy management:
  - Build snapshot: `python agents-toolchain/governance/build_taxonomy.py`
  - Diff snapshots: `python agents-toolchain/governance/diff_taxonomy.py taxonomy_versions/old.json taxonomy_versions/new.json --out reports`
- Coverage check: `python agents-toolchain/governance/check_coverage.py --threshold 0.95`
- Ownership validation: `python scripts/governance/validate_ownership.py --report`
- Sensitive data scan: `python tools/check_sensitive.py`

### Benchmarking & Evaluation
- Unified indicator runner: `python scripts/run_indicator.py --id <indicator_id> --out <path>` (supports: win_rate, elo_rating, latency_p99, throughput_rps, toxicity, accuracy_f1)
- Individual scripts:
  - F1 accuracy: `python scripts/eval/f1.py --gold <path> --pred <path>`
  - Toxicity: `python scripts/eval/toxicity_check.py --outputs <path>`
  - Robustness: `python scripts/eval/robustness_suite.py`
  - Latency profiling: `python scripts/bench/latency_profiler.py --seed 42`
  - Load testing: `python scripts/bench/load_test.py --concurrency 50`
  - LM Arena pull: `python scripts/bench/lmarena_pull.py --models <models> --out <path>`
- Orchestration: `python agents-toolchain/agentic/orchestrator.py --model <model> --metrics <metric_ids> --out reports/`
- VRAM estimation: `python scripts/estimate_vram.py --variant Qwen3-8B --seq_len 32768 --precision fp16`

### BI & Analytics (Optional)
- Start BI stack: `make up` (or `docker compose -f agents-toolchain/bi/infra/docker-compose.bi.yml up -d`)
- ETL: `make etl` (or `python agents-toolchain/bi/etl/extract_runs.py`)
- Metabase setup: `make metabase-setup`

## High-Level Architecture

### Data Flow & Knowledge Base Structure

The repository follows a dual-knowledgebase architecture:

1. **Model Specifications KB** (`models/`, `indicators/`, `benchmarks/`, `platforms/`)
   - Models are defined with variants, hardware requirements, and capability tags
   - Each model entry links to benchmarks via `evaluation.benchmarks` field
   - Indicators define metrics with executable runbooks (`run_script_ref` pointing to `scripts/`)
   - Benchmarks catalog external evaluation suites (100+ benchmarks from GSM8K to LM Arena)

2. **Scenario Research KB** (`scenarios/`, `product_lines/`, `registration/`)
   - Scenarios define automotive use cases mapped to required atomic abilities
   - Product lines trace PRD requirements to measurable metrics and production tests
   - Scenarios link to agents and toolchains needed for execution

### Unified Metric Output Format

All evaluation scripts produce `unified_v1` JSON format:
```json
{
  "metric_id": "accuracy_f1",
  "value": 0.85,
  "ci": [0.82, 0.88],
  "samples_used": 1000,
  "meta": {"model": "Qwen3-8B", "task": "qa"}
}
```

Scripts in `scripts/bench/normalize_unified.py` and `scripts/report/merge_unified.py` aggregate and transform these outputs.

### Validation Pipeline

Data integrity is enforced through:
1. **Schema validation**: `scripts/validate_models.py` checks all `models/*.json` against `templates/model_schema.json`
2. **Cross-reference checking**: Validates that `evaluation.benchmarks` entries exist in `benchmarks/`, and `required_capabilities` exist in `templates/abilities.json`
3. **Indicator script verification**: Ensures `run_script_ref.script` paths exist
4. **Ownership validation**: Checks all entries have valid owners via `scripts/governance/validate_ownership.py`
5. **Coverage reporting**: `agents-toolchain/governance/check_coverage.py` ensures models have sufficient benchmark coverage

### Orchestration & Automation

- **Agentic Orchestrator** (`agents-toolchain/agentic/orchestrator.py`): Plans and executes multi-metric evaluation sweeps, merges results, diffs against baselines
- **Phase 5 Governance** (`scripts/governance/run_phase5_checks.py`): Aggregates all validation checks for CI/CD gates
- **CI Integration** (`.github/workflows/phase5.yml`): Runs governance checks on PR/push to main

## Coding Style & Naming Conventions

- Files: UTF-8 (no BOM). Prefer English/pinyin names with semantic prefixes (e.g., `indicators/accuracy_f1.json`)
- JSON/YAML: 2-space indent; snake_case keys; include `id`, `name`, `source/owner` where applicable
- Python: PEP 8, 4-space indent; script names in `snake_case.py` under `scripts/`
- IDs and references: stable, lowercase identifiers (e.g., `pl_autonomous_navigation_v1`)

## Workflow Guidelines

### Adding a New Model
1. Create `models/<name>.json` following `templates/model_schema.json`
2. Required fields: `model_name`, `variants` (with `name`, `params`), `input_types`, `output_types`
3. Link to benchmarks via `evaluation.benchmarks` array (must exist in `benchmarks/`)
4. Run validation: `python scripts/validate_models.py`
5. Update taxonomy: `python agents-toolchain/governance/build_taxonomy.py`

### Adding a New Benchmark
1. Create `benchmarks/<id>.json` (see `templates/benchmark_template.json`)
2. Include upstream repo link, tasks covered, and evaluation metrics
3. Add model references if applicable
4. Update `benchmarks/index.md` if introducing new category

### Adding a New Indicator
1. Create `indicators/<name>.json` following `templates/indicator_template.json`
2. Implement evaluation script in `scripts/eval/` or `scripts/bench/` that outputs `unified_v1` format
3. Set `run_script_ref.script` to relative path (e.g., `scripts/eval/f1.py`)
4. Add runbook instructions in `run_script_ref.command` or `tooling` field
5. Test with: `python scripts/run_indicator.py --id <indicator_id> --out test.json`

### Logging Research Decisions
Use QA logging for important decisions and rationale:
- Append to `qa/qa_history.jsonl` with fields: `{ts, q, a, tags}`
- Example: `{"ts": "2025-01-15T10:00:00Z", "q": "Why use F1 over accuracy?", "a": "F1 handles imbalanced datasets better", "tags": ["metric-selection"]}`

## Testing & Validation Requirements

- **Before PR**: Run `python scripts/governance/run_phase5_checks.py --report --threshold 0.95`
- **Smoke tests**: Execute benchmark/eval stubs to verify they run without errors
- **New schemas**: Provide sample in `templates/` if introducing new data type
- **CI gate**: `.github/workflows/phase5.yml` blocks merge on validation failures

## Commit & Pull Request Guidelines

- Commit style: Conventional Commits with types used in this repo: `docs`, `chore`, `add`, `fix`, `refactor`, `sync`
  - Example: `add: new indicator for hallucination detection`
- PRs must include:
  - Purpose and scope
  - Affected paths (models/, indicators/, benchmarks/, etc.)
  - Validation output (schema check passing)
  - Before/after snippets for data changes

## Security & Configuration

- Never commit secrets or credentials; keep `.env` local
- Run `python tools/check_sensitive.py` before pushing
- Document environment variables in README.md or tool-specific docs
- Example files provided: `.env.example`, `gemini.env.example`, `agents-toolchain/bi/infra/metabase.env.example`
