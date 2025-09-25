# Agents Toolchain — Quickstart

This folder contains helper services and utilities to ingest sources, orchestrate tasks, and govern the knowledge base.

Prerequisites (PowerShell)
- Python 3.8+
- Create venv and install deps: `python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -U pip jsonschema`

Bring Up Services (optional)
- Docker Desktop running
- From repo root: `docker compose up -d --build`
- n8n UI: `http://localhost:5678/` (configure credentials as in `agents-toolchain/ingestion/README.md`)
- Chat router: `http://localhost:8080/`

Ingestion
- See `agents-toolchain/ingestion/README.md` for webhook and batch examples.

Orchestration
- See `agents-toolchain/orchestration/README.md` for router usage examples.

Validate Models (schema + xref)
- Quick check: `python scripts/validate_models.py`
- Report mode: `python agents-toolchain/governance/validate_models_cli.py --report`
  - Writes to `reports/validation_<ts>/{validation.log,summary.md}`

Governance Utilities
- Build taxonomy: `python agents-toolchain/governance/build_taxonomy.py`
- Check coverage: `python agents-toolchain/governance/check_coverage.py`
