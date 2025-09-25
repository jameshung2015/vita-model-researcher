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
- [ ] Human preference: win_rate (LM Arena snapshot)
- [ ] Ranking: elo_rating (LM Arena snapshot)
- [ ] Safety: toxicity_rate (stub)
- [ ] Efficiency: latency_p99 (stub), throughput_rps (stub)
- [ ] Accuracy example: accuracy_f1 (existing unified evaluator)

3) Snapshots & Reports
- [ ] Generate new LM Arena snapshot for all Qwen3 variants
- [ ] Normalize to unified_v1 JSON under reports/
- [ ] Add summary.md via scripts/report/unified_to_md.py
- [ ] Establish/update baselines and run baseline_diff as needed

4) Docs
- [x] Add docs/PHASE3_QUICKSTART.md
- [ ] Add snapshots blurb (benchmarks/index.md or separate doc)
- [ ] Update README with Phase 3 quickstart link

5) Validation
- [ ] Run scripts/validate_models.py; fix any schema issues
- [ ] Run safety scan (tools/check_sensitive.py) before push

Notes
- Do not add GitHub Actions. Commit snapshots for history under benchmarks/snapshots/lmarena/.
