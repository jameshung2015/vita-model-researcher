# Phase 2 Roadmap — Metrics & Baselines (Draft)

Context
- Phase 1 complete; history at `docs/achive/todo-phase1.md`.
- This document is the actionable plan for Phase 2; to be reviewed before execution.

Objectives
- Map indicator entries to runnable scripts via `run_script_ref` and unify outputs.
- Operationalize benchmark pullers (seed with `lmarena_pull`) and local snapshots.
- Establish baseline snapshots and automated diff with thresholded alerts.
- Extend validation to cover new fields and cross-refs (models/indicators/benchmarks).
- Produce one model × one scenario diff summary end-to-end.

Deliverables
- Indicators: template update (add `run_script_ref`), examples, and runbook alignment.
- Benchmarks: runnable puller (`scripts/bench/lmarena_pull.py`) with snapshot artifacts.
- Baselines: baseline store convention under `reports/` and diff script/stub.
- Validation: extended checks in `scripts/validate_models.py` for new references.
- Reporting: minimal diff summary Markdown + JSON schema for result items.

Scope (what’s included)
- JSON schema/template updates limited to indicators and report items.
- One benchmark source wired (LM Arena) with local offline-friendly snapshots.
- Minimal evaluator stubs to ensure unified metric output shape.

Out of scope (Phase 2)
- Full orchestrator; multi-scenario pipelines; full dataset governance.
- Provider-specific integrations beyond the initial benchmark puller.

Acceptance Criteria
- AC1: `templates/indicator_template.json` includes `run_script_ref` and docs updated.
- AC2: Running `python scripts/bench/lmarena_pull.py` produces a local snapshot JSON.
- AC3: A baseline snapshot exists for 1 model × 1 scenario with ≥1 indicator value.
- AC4: `baseline_diff` script outputs top-N metric deltas with threshold flags.
- AC5: A Markdown summary is written under `reports/<model>_<scenario>_<ts>/`.

Milestones & Tasks

1) Indicator mapping & evaluator shape
- [x] Add `run_script_ref` to `templates/indicator_template.json` and docs
- [x] Normalize evaluator outputs: `{ metric_id, value, ci, samples_used, meta }`
- [x] Provide `scripts/eval/f1.py` example returning unified structure
- [x] Update indicators under `indicators/` to include `run_script_ref` (core coverage: accuracy_f1, robustness_adv, latency_p99, throughput_rps, toxicity, elo_rating, win_rate, human_exam_accuracy, multimodal_understanding_score, safety_alignment_score, agent_task_completion)

2) Benchmark puller bootstrap
- [x] Verify `scripts/bench/lmarena_pull.py` runnable; add README usage notes
- [x] Write snapshot artifacts under `benchmarks/snapshots/<source>/<ts>.json`
- [ ] Add `benchmarks/index.md` entry referencing the snapshot(s)

3) Baseline store & diff
- [x] Define baseline layout: `reports/<model>_<scenario>_<ts>/baseline.json`
- [x] Implement `scripts/bench/baseline_diff.py --prev <file> --curr <file> --threshold 0.05`
- [x] Emit diff JSON and Markdown summary (`diff.json`, `summary.md`)

4) Validation & safety
- [x] Extend `scripts/validate_models.py` to check indicator `run_script_ref` existence
- [ ] Cross-reference checks: model -> indicators -> evaluator script exists (deferred)
- [x] Run `python tools/check_sensitive.py` before publishing artifacts

5) Docs & examples
- [x] `reports/README.md` describing report/diff schemas and examples
- [ ] Update `README.md` quickstart for Phase 2 commands
- [ ] Append QA notes to `qa/qa_history.jsonl` via tooling

Verification Plan
- Schema checks pass: `python scripts/validate_models.py`
- Benchmark smoke: `python scripts/bench/lmarena_pull.py --seed 42`
- Diff smoke: run `baseline_diff.py` on two small JSON samples

Risks & Mitigations
- Upstream format drift → keep local snapshots; parser isolation
- Non-uniform metric outputs → enforce result schema + validator
- Time overruns → keep scope to one source and one E2E example

Review Checklist (for you)
- [ ] Scope and deliverables match Phase 2 intent
- [ ] ACs are testable with current repo layout
- [ ] Paths/commands align with repository guidelines
- [ ] Any renames/conflicts or blocking dependencies

After approval, tasks will be executed in the order above with updates per milestone.
﻿
