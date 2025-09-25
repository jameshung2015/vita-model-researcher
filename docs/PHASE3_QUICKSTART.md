# Phase 3 Quickstart (Qwen3-first)

Goals
- Run smoke metrics for all Qwen3 variants and keep snapshots for history.
- Use unified_v1 outputs across indicators to enable baseline diffs.

Supported Qwen3 variants
- Qwen3-4B
- Qwen3-8B
- Qwen3-30B-A3B
- Qwen3-235B-A22B

1) Create/activate env
```
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -U pip jsonschema
```

2) Validate models (schema)
```
python agents-toolchain/governance/validate_models_cli.py --report
```

3) Pull LM Arena snapshot (all Qwen3 variants)
```
$ts = [int][double]::Parse((Get-Date -UFormat %s))
python scripts/bench/lmarena_pull.py --models "Qwen3-4B,Qwen3-8B,Qwen3-30B-A3B,Qwen3-235B-A22B" --out benchmarks/snapshots/lmarena/$ts.json
```

4) Normalize to unified outputs
```
python scripts/run_indicator.py --id win_rate   --models "Qwen3-4B,Qwen3-8B,Qwen3-30B-A3B,Qwen3-235B-A22B" --snapshot benchmarks/snapshots/lmarena/$ts.json --out reports/qwen3_win_rate_$ts.json
python scripts/run_indicator.py --id elo_rating --models "Qwen3-4B,Qwen3-8B,Qwen3-30B-A3B,Qwen3-235B-A22B" --snapshot benchmarks/snapshots/lmarena/$ts.json --out reports/qwen3_elo_$ts.json
```

5) Efficiency smoke (stubs)
```
python scripts/run_indicator.py --id latency_p99    --seed 42  --out reports/qwen3_latency_$ts.json
python scripts/run_indicator.py --id throughput_rps --concurrency 50 --out reports/qwen3_throughput_$ts.json
```

6) Safety smoke (stub)
```
python scripts/run_indicator.py --id toxicity --out reports/qwen3_toxicity_$ts.json
```

7) Baseline diff (optional)
```
python scripts/bench/baseline_diff.py --prev reports/<dir>/baseline.json --curr reports/<dir>/current.json --threshold 0.05
```

Notes
- Snapshots are stored under benchmarks/snapshots/lmarena/ and should be kept for history.
- All report JSON files are unified_v1 arrays; use scripts/report/unified_to_md.py to render markdown summaries.

