# Qwen3 Dashboard Generator

This tool generates an interactive HTML dashboard for visualizing Qwen3 and OpenAI GPT/o1 model performance across multiple modalities, supporting rich cross-model comparisons.

## Features

- **Multi-Modal Support**: Displays benchmarks for LLM, VLM, ALM, and Omni models.
- **Cross-Model Comparison**: Toggle up to **three** models (e.g., Qwen3 LLM vs. OpenAI o1) side-by-side.
- **Variant-Aware Views**: Pick variants per model (Qwen3-8B, o1-mini, etc.); charts/tables update instantly.
- **Interactive Filtering**: Switch between model types, variants, and benchmark categories.
- **Visual Analytics**: 
  - Radar charts overlaying multiple model series
  - Stacked bar comparisons for top benchmarks
  - Detailed benchmark tables with per-model values
- **Auto-Update**: Reads latest data from JSON files on each generation.

## Usage

### Generate Dashboard

```bash
python agents-toolchain/dashboard/generate_dashboard.py
```

### Output

- **File**: `benchmarks/models/qwen3_dashboard.html`
- **Type**: Single-file standalone HTML (no dependencies required)

### View Dashboard

Simply open `benchmarks/models/qwen3_dashboard.html` in any modern web browser.

### (New) Generate Dashboard v2

The rewritten generator (`generate_dashboard_v2.py`) auto-parses consolidated benchmark JSON files (containing `benchmarks` arrays with `scores_by_variant`) and produces an updated interactive dashboard supporting dynamic model slot addition.

```bash
python agents-toolchain/dashboard/generate_dashboard_v2.py \
   --data-dir benchmarks/models \
   --out benchmarks/models/qwen3_dashboard_v2.html \
   --max-models 3 \
   --title "Model Performance Dashboard v2"
```

Open the output HTML file directly in a browser (no server required). You can add up to `--max-models` model slots; each slot lets you select a family/modality combination and then a variant. Benchmark rows are inferred from entries in each JSON file's `benchmarks` list using `benchmark_id` or `name` fields.

#### v1 vs v2 Differences
| Feature | v1 | v2 |
|---------|----|----|
| Data ingestion | Hard-coded specific JSON file names | Auto-discovers all `*.json` under data dir, parses `benchmarks` lists with `scores_by_variant` |
| Max selectable models | 3 (fixed) | Configurable via `--max-models` |
| Variants source | Pre-defined variant arrays | Inferred from `scores_by_variant` across all benchmarks |
| Categories | Keyword heuristic | Same heuristic (configurable inside script) |
| Resilience | Assumes structure | Skips non-conforming files, robust to percent string formats |
| Implementation | Single large template f-string | Incremental string assembly to avoid brace conflicts |

#### Benchmark JSON Format Parsed by v2
Minimal required fields per benchmark entry:
```json
{
   "benchmarks": [
      {
         "benchmark_id": "benchmark.mmlu",
         "scores_by_variant": {
            "Model-8B": "85%",
            "Model-30B": "88%"
         }
      }
   ],
   "model": "model_family_name"
}
```
Percent strings are converted to fractional numeric values (e.g. "85%" -> 0.85) for charting.

If a root object also contains `variants` (legacy style), those are still supported; otherwise `scores_by_variant` aggregation builds variant benchmark maps.

#### Customization (v2)
Edit category keywords inside `generate_dashboard_v2.py` (`CATEGORY_KEYWORDS`) to change grouping. Adjust palette or extend heuristics in `infer_family_modality_from_filename` for new modalities.

#### Troubleshooting
| Message | Meaning | Action |
|---------|---------|--------|
| `[skip] ... root is list` | File is not a model summary (likely raw benchmark set) | Ignore or convert to object form |
| `[warn] dropping model ... no variants` | Parsed model had no variant scores | Ensure `scores_by_variant` present |
| "No valid models discovered" | After parsing, no usable variants found | Verify directory and JSON schema |

#### Example Quick Run
```bash
python agents-toolchain/dashboard/generate_dashboard_v2.py --out benchmarks/models/dashboard_v2.html
```
Then open `benchmarks/models/dashboard_v2.html`.

---

## Data Sources

The dashboard aggregates data from:

1. **LLM (Text)**:
   - `benchmarks/models/qwen3_text.json`
   - `benchmarks/models/gpt_text.json` (已整合原 o1 推理系列数据; `gpt_reasoning.json` 已删除)
   - Variants: Qwen3-8B, Qwen3-30B-A3B, Qwen3-235B-A22B
   - GPT Variants (统一于 gpt_text.json): GPT-4o, GPT-4o-mini, GPT-4-Turbo, OpenAI o1, OpenAI o1-mini

2. **VLM (Vision)**: `benchmarks/models/qwen3_vl.json`
   - GPT Vision: `benchmarks/models/gpt_vl.json`
   - Variants: Qwen3-VL-8B, Qwen3-VL-30B-A3B, Qwen3-VL-235B-A22B

3. **ALM (Audio)**:
   - Qwen: `benchmarks/models/qwen3_audio.json`
   - GPT: `benchmarks/models/gpt_audio.json`

4. **Omni (Multimodal)**:
   - Qwen: `benchmarks/models/qwen3_omni.json`
   - GPT: `benchmarks/models/gpt_omni.json`

## Technology Stack

- **Frontend**: Vue.js 3 (CDN)
- **Charts**: ECharts 5
- **Backend**: Python 3.7+
- **Template**: Pure HTML/CSS/JS (no build required)

## Customization

### Add New Model Type

1. Add JSON file to `benchmarks/models/`
2. Update `generate_dashboard.py`:
   - Add an `aggregate_<model_family>_<modality>_data()` loader that calls `_store_model_entry`
   - Provide a friendly label via `_register_global_model`
   - (Optional) Extend `_categorize_benchmarks()` with new categories
   - HTML automatically surfaces model toggles based on registered models

### Modify Categories

Edit the `category_keywords` dictionary in `_categorize_benchmarks()` method.

### Change Styling

Modify the `<style>` section in `generate_html()` method.

### Extend Model Metadata

`generate_dashboard.py` keeps a global palette and model registry. To add colors/labels manually:

```python
self._register_global_model("my_model", "My Model Label")
```

If you need custom variant defaults, include `default_variant` in the stored entry.

## Development

### Project Structure

```
agents-toolchain/dashboard/
├── generate_dashboard.py    # Main generator script
├── templates/                # (Reserved for future Jinja2 templates)
├── static/                   # (Reserved for additional assets)
└── README.md                # This file
```

### Dependencies

```bash
# No external dependencies required for generation
# Python standard library only

# For viewing: Any modern browser
```

## References

- **LLM Technical Report**: https://arxiv.org/abs/2505.09388
- **OpenAI o1 Launch**: https://openai.com/index/introducing-openai-o1
- **VLM Collection**: https://huggingface.co/collections/Qwen/qwen3-vl-68d2a7c1b8a8afce4ebd2dbe
- **Audio Repository**: https://github.com/QwenLM/Qwen-Audio
- **Omni Technical Report**: https://arxiv.org/abs/2509.17765
- **Agent Reference**: https://github.com/THUDM/AgentBench

## License

Follows the main repository license (Apache 2.0).
