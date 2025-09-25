Phase 3 (Qwen3-first) TODO
--------------------------

Scope
- Run smoke metrics for all Qwen3 variants: Qwen3-4B, Qwen3-8B, Qwen3-30B-A3B, Qwen3-235B-A22B.
- Keep LM Arena snapshots as history; no CI/GitHub Actions.

Work Items
1) Indicators & Tools
- [x] Add normalizer: scripts/bench/normalize_unified.py (win_rate, elo -> unified_v1)
- [x] Add runner: scripts/run_indicator.py (wraps snapshot + normalize + stubs)
- [ ] Render helper: scripts/report/unified_to_md.py usage in docs
- [x] Update indicators/win_rate.json, indicators/elo_rating.json to unified_v1 via runner

2) Qwen3 Smoke Metrics (from public perf themes)
- [x] Human preference: win_rate (LM Arena snapshot)
- [x] Ranking: elo_rating (LM Arena snapshot)
- [x] Safety: toxicity_rate (stub)
- [x] Efficiency: latency_p99 (stub), throughput_rps (stub)
- [x] Accuracy example: accuracy_f1 (existing unified evaluator)

3) Snapshots & Reports
- [x] Generate new LM Arena snapshot for all Qwen3 variants
- [x] Normalize to unified_v1 JSON under reports/
- [x] Add summary.md via scripts/report/unified_to_md.py
- [x] Establish/update baselines and run baseline_diff as needed
- [x] Publish stable baseline for Qwen3 at `reports/baselines/qwen3/1758819673/`

4) Docs
- [x] Add docs/PHASE3_QUICKSTART.md
- [x] Add snapshots blurb (benchmarks/index.md)
- [x] Update README with Phase 3 quickstart link

5) Validation
- [ ] Run scripts/validate_models.py; fix any schema issues
- [ ] Run safety scan (tools/check_sensitive.py) before push

Notes
- Do not add GitHub Actions. Commit snapshots for history under benchmarks/snapshots/lmarena/.

Phase 4 (Agentic Augmentation) TODO
-----------------------------------

Scope
- Add an agentic orchestrator to plan, run, and report Qwen3 metrics end-to-end without CI.
- Keep snapshots/baselines as historical artifacts; append QA logs.

Deliverables
- agents-toolchain/agentic/orchestrator.py (CLI) and README quickstart.
- reports/qwen3_phase4_<ts>/{per-metric *.json,current.json,diff.json,summary.md}.
- docs/summaries/* Phase 4 markdown exports.
- qa/qa_history.jsonl appended with Phase 4 run entries.

Work Items
1) Agentic Orchestrator
- [ ] CLI: plan → run → merge → diff → summarize.
- [ ] Plan: resolve models (Qwen3 variants) + metrics set.
- [ ] Run: reuse scripts/bench/lmarena_pull.py + scripts/run_indicator.py.
- [ ] Merge: scripts/report/merge_unified.py → current.json.
- [ ] Diff: scripts/bench/baseline_diff.py vs latest baseline.
- [ ] Summaries: scripts/report/unified_to_md.py to docs/summaries/.
- [ ] QA log: append run metadata to qa/qa_history.jsonl.

2) Qwen3 Agentic Run
- [ ] Models: Qwen3-4B, Qwen3-8B, Qwen3-30B-A3B, Qwen3-235B-A22B.
- [ ] Metrics: win_rate, elo_rating, latency_p99, throughput_rps, toxicity, accuracy_f1.
- [ ] Thresholds: default 0.05 (configurable via CLI).

3) Docs & Quickstart
- [ ] agents-toolchain/agentic/README.md quickstart.
- [ ] docs/PHASE4_QUICKSTART.md with commands.
- [ ] Link summaries index (docs/summaries) from README or PHASE docs.

4) Validation & Safety
- [ ] Run agents-toolchain/governance/validate_models_cli.py --report.
- [ ] Run tools/check_sensitive.py and confirm no secrets.

Notes
- No GitHub Actions. Runs are manual; artifacts committed for traceability.
