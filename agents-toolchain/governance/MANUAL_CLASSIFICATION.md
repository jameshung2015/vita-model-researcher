## Manual Classification Playbook (<= 2 hours/model)

### Inputs
- Source: official model page/model card, press/release notes.
- Files to edit: `models/<model>.json` (or add new), ensure schema in `templates/model_schema.json`.

### Steps
- Identify basics (15 min)
  - Fill `model_name`, `input_types`, `output_types`, `architecture_family`.
  - Add 1–3 `variants` with `name`, approximate `params` (number), `context_windows`.
- Size & inference (15–25 min)
  - Capture `inference` summary: `latency_level`, `throughput_rps` (if known), `memory_gb` notes.
  - If uncertain, add notes and run `scripts/estimate_vram.py` for sanity.
- Tags & capabilities (10–15 min)
  - Populate `tags` (e.g., instruction-following, quantizable) and high-level `capabilities` (free-form object).
- Evaluation links (10–15 min)
  - Add `evaluation.benchmarks` keys from `benchmarks/*.json` filenames if available (e.g., `mmlu`, `gsm8k`).
- Cross-check (10 min)
  - Run: `python scripts/validate_models.py` and fix reported issues.

### Naming & formatting
- Use lowercase IDs in filenames; keep concise `model_name`.
- JSON: 2-space indent, UTF-8, no BOM.

### Acceptance checklist
- [ ] Required fields present; schema passes.
- [ ] At least one variant with numeric `params` and `context_windows`.
- [ ] Evaluation references point to existing `benchmarks/*.json`.
- [ ] Notes on inference memory or a pointer to model card.
- [ ] Taxonomy snapshot updated: `python agents-toolchain/governance/build_taxonomy.py`.

