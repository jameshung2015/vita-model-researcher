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
- [x] CLI: plan → run → merge → diff → summarize.
- [x] Plan: resolve models (Qwen3 variants) + metrics set.
- [x] Run: reuse scripts/bench/lmarena_pull.py + scripts/run_indicator.py.
- [x] Merge: scripts/report/merge_unified.py → current.json.
- [x] Diff: scripts/bench/baseline_diff.py vs latest baseline.
- [x] Summaries: scripts/report/unified_to_md.py to docs/summaries/.
- [x] QA log: append run metadata to qa/qa_history.jsonl.

2) Qwen3 Agentic Run
- [x] Models: Qwen3-4B, Qwen3-8B, Qwen3-30B-A3B, Qwen3-235B-A22B.
- [x] Metrics: win_rate, elo_rating, latency_p99, throughput_rps, toxicity, accuracy_f1.
- [x] Thresholds: default 0.05 (configurable via CLI).

3) Docs & Quickstart
- [x] agents-toolchain/agentic/README.md quickstart.
- [x] docs/PHASE4_QUICKSTART.md with commands.
- [ ] Link summaries index (docs/summaries) from README or PHASE docs.

4) Validation & Safety
- [x] Run agents-toolchain/governance/validate_models_cli.py --report.
- [x] Run tools/check_sensitive.py and confirm no secrets.

Notes
- No GitHub Actions. Runs are manual; artifacts committed for traceability.
