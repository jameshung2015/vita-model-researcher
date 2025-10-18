# Variant-Specific Score Support - Release Notes

## Version 2.0 Update

### New Features

✅ **Dynamic Variant-Specific Scores**

Dashboard now supports displaying different benchmark scores for different model sizes:

- Qwen3-8B
- Qwen3-30B-A3B
- Qwen3-235B-A22B

### How It Works

#### Data Structure
Benchmarks can now include `scores_by_variant` field:

```json
{
  "name": "MMLU-Pro",
  "value": "83.8%",
  "scores_by_variant": {
    "Qwen3-8B": "74%",
    "Qwen3-30B-A3B": "78%",
    "Qwen3-235B-A22B": "83%"
  }
}
```

#### Dashboard Behavior

When you select a **Model Variant**:
- ✅ Benchmark table values update to variant-specific scores
- ✅ Radar chart recalculates with variant scores
- ✅ Bar chart displays variant-specific values
- ✅ All visualizations reflect the selected model size

### Updated Benchmarks

**LLM (22 benchmarks)** - All with variant-specific scores:
- MMLU-Pro: 74% (8B) → 78% (30B) → 83% (235B)
- GPQA Diamond: 59% (8B) → 62% (30B) → 70% (235B)
- LiveCodeBench: 47% (8B) → 52% (30B) → 62% (235B)
- MATH-500: 93% (8B) → 96% (30B) → 96% (235B)
- AIME 2024: 75% (8B) → 76% (30B) → 84% (235B)
- And 17 more...

**VLM, ALM, Omni** - Currently using representative scores
- Data will be updated as variant-specific benchmarks become available

### Data Sources

Variant-specific scores extracted from:
- Novita AI Blog: https://blogs.novita.ai/which-qwen3-model-is-right-for-you-a-practical-guide/
- Qwen3 Technical Report benchmarks
- Community benchmarking (dev.to, Reddit)

### Technical Implementation

**Changes in `generate_dashboard.py`**:
1. Enhanced `filteredBenchmarks` computed property to apply variant scores
2. Updated `renderRadarChart()` to use variant-specific values
3. Updated `renderBarChart()` to use variant-specific values
4. Added `currentVariant` watch to trigger re-rendering

**Backward Compatibility**:
- Benchmarks without `scores_by_variant` still work (use `value` field)
- Existing data files remain compatible

### Estimated Scores

Some variant scores are marked with `~` (tilde) indicating estimates based on:
- Interpolation from official benchmark trends
- Community benchmarking results
- Proportional scaling from confirmed scores

### Future Work

- [ ] Add variant-specific scores for VLM models (4B, 8B, 30B, 235B)
- [ ] Extract more precise scores from technical reports
- [ ] Add confidence indicators for estimated vs confirmed scores
- [ ] Support multiple metric types per benchmark (with/without reasoning)

---

Generated: 2025-10-16
Dashboard Version: 2.0

# Multi-Model Comparison & GPT Integration - Release Notes

## Version 3.0 Update

### What’s New

- ✅ **Multi-model comparison (up to 3 models)** across every modality (LLM, VLM, ALM, Omni).
- ✅ **Per-model variant selectors** – choose different variants (e.g., Qwen3-8B vs. o1-mini) simultaneously.
- ✅ **OpenAI GPT/o1 family support** with merged benchmark/inference metadata.
- ✅ **Charts upgraded** to multi-series radar and bar views for side-by-side insights.
- ✅ **Detailed table redesign** showing variant-specific values for each selected model.

### How It Works

- **Model toggle bar** lets you pick any combination of registered models (e.g., `Qwen3 LLM`, `OpenAI GPT/o1`).
- Each selected model stores its own variant choice; changing one does not affect the others.
- Vue/ECharts now render multiple series, colored via centralized palette metadata.
- Data registration pipeline now normalizes to:
  ```python
  self.data[type_key]["models"][model_key] = {
      "label": "...",
      "benchmarks": [...],
      "variants": [...],
      "default_variant": "...",
      ...
  }
  ```

### Data Updates

- Added merged GPT benchmark rollup (`gpt_reasoning.json`) and schema-compliant `models/openai-gpt.json`.
- Dashboard aggregates both Qwen and GPT data while keeping validation checks green.

### UX Improvements

- No more raw template tags – HTML now renders real values instead of `{{ ... }}` placeholders.
- Added stats tiles reflecting the current comparison context (benchmarks, categories, variants, model count).
- Model selection guards prevent deselecting the last active model and limit selections to three.

### Developer Notes

- `generate_dashboard.py` now tracks global model metadata (labels, colors) to keep UI consistent.
- Benchmark totals in `generate()` recalc via nested model structures for accuracy.
- Script verified with `python scripts/validate_models.py` plus direct dashboard generation.

---

Generated: 2025-10-16 (update)
Dashboard Version: 3.0
