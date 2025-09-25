# scripts — Runbooks & Bench Stubs

This folder mirrors the previous `eval/` and `bench/` locations and centralizes runnable stubs used by the indicators KB.

Quick examples (PowerShell)

Run the F1 stub (unified output by default):

```powershell
python .\scripts\eval\f1.py
```

Unified output shape (unified_v1): `{ metric_id, value, ci, samples_used, meta }`.
Use `--legacy` to emit `{ precision, recall, f1 }`.

Latency profiler (deterministic):

```powershell
python .\scripts\bench\latency_profiler.py --seed 42
```

Throughput stub:

```powershell
python .\scripts\bench\load_test.py --concurrency 50
```

Robustness and toxicity checks:

```powershell
python .\scripts\eval\robustness_suite.py
python .\scripts\eval\toxicity_check.py
```

LM Arena snapshot puller (stub):

```powershell
python .\scripts\bench\lmarena_pull.py --out .\benchmarks\snapshots\lmarena\<ts>.json
```

Notes
- The scripts are lightweight and dependency-free; intended as smoke tests and integration examples.
- If you rely on these paths in automation, update any references from `eval/` or `bench/` to `scripts/eval/` or `scripts/bench/` respectively.
# scripts/ — Utilities for the research KB

This folder contains small utilities to help plan and validate deployments for models in the KB. The main utility today is `estimate_vram.py` — a lightweight, heuristic estimator for VRAM and deployment sizing for Qwen3 variants.

Quick overview
- `estimate_vram.py` — estimate VRAM per-GPU and total memory using simple heuristics (weights + activations + KV cache + overhead). Not a substitute for real benchmarks.

Requirements
- Python 3.8+ (tested with Python 3.12)
- No external packages required

Usage (PowerShell)

- Basic example: estimate for Qwen3-8B, 32k sequence, FP16, single GPU

```powershell
python "D:\project\research\大模型评价指标与工具\scripts\estimate_vram.py" --variant Qwen3-8B --seq_len 32768 --batch 1 --precision fp16
```

- Large model example: Qwen3-235B-A22B, 256k context, int8, split across 8 GPUs (naive division)

```powershell
python "D:\project\research\大模型评价指标与工具\scripts\estimate_vram.py" --variant Qwen3-235B-A22B --seq_len 256000 --batch 1 --precision int8 --num_gpus 8 --moe
```

Understanding the output
- `estimated_vram_gb_per_gpu` — per-GPU memory estimate after naive split (if `--num_gpus` > 1).
- `estimated_vram_gb_total` — total combined memory footprint across all GPUs.
- `breakdown`:
  - `weight_gb` — estimated resident weights memory (based on params and precision bytes)
  - `activations_gb` — runtime activations estimate (scales with sequence length and model size)
  - `kv_cache_gb` — key-value cache (relevant for generation/long-context caching)
  - `moe_overhead_gb` — additional overhead estimated for Mixture-of-Experts models
  - `overhead_gb` — conservative floor for workspace/CUDA/other overhead

Caveats & guidance
- Heuristic only: numbers are for planning and rough comparisons across variants. They are not production-accurate.
- MoE models: peak memory depends on active experts and routing; set `--moe` to include MoE overhead if auto-detection misses it.
- Distributed inference: this script does a naive division across GPUs. Real deployments use tensor/model parallelism, activation checkpointing, and offloading — which change the per-GPU peak considerably.
- Quantization: `int8` reduces some memory; the script applies a conservative multiplier. For production quantized runs, follow GPTQ/AWQ workflows and benchmark.

Recommended next steps
- Use this script to create a sizing baseline for pilot deployments.
- Run a small local pilot (small batch, short sequence) on the target hardware to measure actual peak memory and throughput.
- If you need more accurate estimates, I can extend the script to incorporate tensor/model parallelism factors, activation checkpointing, and offloading heuristics.

Where to find model metadata
- The script reads model metadata from `../models/qwen3.json`. Add more model files (one JSON per model) and update the script if you want it to discover models automatically.

Adding or tuning variants
- Edit `models/qwen3.json` to add fields like `hardware_recommendations` or per-variant defaults for `seq_len` and `num_gpus`.

Contact
- If you want, I can add a README for the whole project or integrate this script into a small CI check that validates model entries against the JSON schema.
