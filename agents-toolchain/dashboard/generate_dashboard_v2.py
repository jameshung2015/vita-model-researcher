"""Dashboard Generator v2
=================================
Rewritten implementation (ignoring existing v1 script) to build a standalone
HTML dashboard comparing up to three models across modalities (LLM, VLM, ALM, Omni).

Key Features Implemented:
 - Auto-discovery of model benchmark JSON files under benchmarks/models/*.json
 - Unified internal data schema for variants and benchmark scores
 - Category inference via keyword mapping
 - Vue3 + ECharts inline single-file HTML output (no build tooling)
 - Cross-model & per-variant selection (max configurable)
 - Resilient to missing files / malformed entries (warn & skip)
 - CLI options: --data-dir, --out, --max-models, --title

Expected Input JSON (flexible):
 Each file may look like one of:
 1. {"model_family": "qwen3", "modality": "llm", "variants": {"Qwen3-8B": {"benchmarks": {"gsm8k": 0.82, ...}}, ...}}
 2. {"model_family": "gpt", "modality": "vlm", "variants": [ {"name": "GPT-4o", "benchmarks": {"mmbench_en_v1_1_dev": 0.71}} ]}
 3. Minimal: {"variants": {...}} (will infer family & modality from filename heuristics)

Internal Normalized Structure:
 models[model_id] = {
     'model_id': 'qwen3_llm',
     'family': 'qwen3',
     'modality': 'llm',
     'label': 'Qwen3 LLM',
     'variants': {
         'Qwen3-8B': {
             'benchmarks': {'gsm8k': 0.82, 'mmlu': 0.71, ...},
             'meta': {...}
         },
         ...
     }
 }

Benchmarks Categories Mapping (edit category_keywords below):
 category_keywords = {
   'reasoning': ['gsm8k', 'math', 'gpqa', 'arc', 'bbh'],
   'knowledge': ['mmlu', 'mmlu_pro', 'mmlu_redux'],
   'vision': ['mmbench', 'mmstar', 'mathvista', 'chart', 'ocr', 'object'],
   'audio': ['librispeech', 'aishell', 'nsynth', 'audio', 'speech'],
   'agent': ['agentbench', 'androidworld', 'osworld', 'odinw'],
   'robustness': ['hallusion', 'livebench', 'refcoco', 'refospatial'],
 }

Because of heuristic nature, unmapped benchmarks fall under 'other'.

Usage:
  python agents-toolchain/dashboard/generate_dashboard_v2.py \
      --out benchmarks/models/qwen3_dashboard_v2.html \
      --data-dir benchmarks/models \
      --max-models 3

"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


CATEGORY_KEYWORDS = {
    'reasoning': ['gsm8k', 'math', 'gpqa', 'arc', 'bbh', 'aime'],
    'knowledge': ['mmlu', 'mmlu_pro', 'mmlu_redux', 'mmlu_prox'],
    'vision': ['mmbench', 'mmstar', 'mathvista', 'mathverse', 'chart', 'ocr', 'docvqa', 'object', 'hypersim', 'refcoco', 'mmvet', 'mmmu'],
    'audio': ['librispeech', 'aishell', 'nsynth', 'audio', 'speech', 'clotho', 'cochl', 'musr'],
    'agent': ['agentbench', 'androidworld', 'osworld', 'odinw', 'arkweb', 'design2code', 'erqa'],
    'robustness': ['hallusion', 'livebench', 'refospatial', 'robospatialhome', 'countbench', 'mmlongbench'],
}

PALETTE = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
]


def infer_family_modality_from_filename(filename: str) -> Tuple[str, str]:
    base = Path(filename).stem.lower()
    # heuristic splits
    family = 'generic'
    modality = 'llm'
    if 'qwen' in base:
        family = 'qwen3'
    elif 'gpt' in base or 'o1' in base:
        family = 'gpt'
    # modalities by keyword
    if 'audio' in base:
        modality = 'alm'
    elif 'omni' in base:
        modality = 'omni'
    elif any(k in base for k in ['vl', 'vision']):
        modality = 'vlm'
    return family, modality


def categorize_benchmark(bench_id: str) -> str:
    bid = bench_id.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in bid:
                return cat
    return 'other'


def load_models(data_dir: Path) -> Dict[str, Dict[str, Any]]:
    models: Dict[str, Dict[str, Any]] = {}
    for path in sorted(data_dir.glob('*.json')):
        try:
            raw = json.loads(path.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"[warn] unable to parse {path.name}: {e}", file=sys.stderr)
            continue

        # If root is a list: treat as a modality-specific benchmark collection for one model family.
        if isinstance(raw, list):
            family, modality = infer_family_modality_from_filename(path.name)
            model_id = f"{family}_{modality}".lower()
            if model_id not in models:
                models[model_id] = {
                    'model_id': model_id,
                    'family': family,
                    'modality': modality,
                    'label': f"{family.capitalize()} {modality.upper()}",
                    'variants': {}
                }
            # Determine variant names from any scores_by_variant keys; aggregate all encountered variants.
            for bench in raw:
                if not isinstance(bench, dict):
                    continue
                b_id = bench.get('benchmark_id') or bench.get('id') or bench.get('name')
                scores_map = bench.get('scores_by_variant')
                if scores_map and isinstance(scores_map, dict):
                    for variant_name, vscore in scores_map.items():
                        try:
                            if isinstance(vscore, str) and vscore.strip().endswith('%'):
                                num = float(vscore.strip().replace('%', '').replace('~', '')) / 100.0
                            elif isinstance(vscore, (int, float)):
                                num = float(vscore)
                            else:
                                num = float(vscore) if re.match(r'^\d+(\.\d+)?$', str(vscore)) else None
                        except Exception:
                            num = None
                        variant_entry = models[model_id]['variants'].setdefault(variant_name, {'benchmarks': {}, 'meta': {}})
                        if num is not None and b_id:
                            variant_entry['benchmarks'][b_id] = num
                else:
                    # No per-variant scores; place under a synthetic 'default' variant
                    val = bench.get('value')
                    try:
                        if isinstance(val, str) and val.strip().endswith('%'):
                            num = float(val.strip().replace('%', '').replace('~', '')) / 100.0
                        elif isinstance(val, (int, float)):
                            num = float(val)
                        else:
                            num = float(val) if re.match(r'^\d+(\.\d+)?$', str(val)) else None
                    except Exception:
                        num = None
                    variant_entry = models[model_id]['variants'].setdefault('default', {'benchmarks': {}, 'meta': {}})
                    if num is not None and b_id:
                        variant_entry['benchmarks'][b_id] = num
            continue

        # Support benchmark-style model summary with benchmarks list + scores_by_variant
        if 'benchmarks' in raw and 'variants' not in raw:
            benchmarks_list = raw.get('benchmarks', [])
            if not isinstance(benchmarks_list, list):
                benchmarks_list = []
            # infer family/modality
            family = raw.get('model_family') or raw.get('model') or None
            modality = raw.get('modality')
            if not modality:
                # heuristics
                fname, fmod = infer_family_modality_from_filename(path.name)
                family = family or fname
                modality = fmod
            model_id = f"{family}_{modality}".lower()
            if model_id not in models:
                models[model_id] = {
                    'model_id': model_id,
                    'family': family,
                    'modality': modality,
                    'label': f"{family.capitalize()} {modality.upper()}",
                    'variants': {}
                }
            # aggregate per variant
            for bench in benchmarks_list:
                b_id = bench.get('benchmark_id') or bench.get('name')
                scores_by_variant = bench.get('scores_by_variant', {})
                for variant_name, vscore in scores_by_variant.items():
                    try:
                        # normalize numeric percent string
                        if isinstance(vscore, str) and vscore.strip().endswith('%'):
                            num = float(vscore.strip().replace('%', '').replace('~', '')) / 100.0
                        elif isinstance(vscore, (int, float)):
                            num = float(vscore)
                        else:
                            num = None
                    except Exception:
                        num = None
                    variant_entry = models[model_id]['variants'].setdefault(variant_name, {'benchmarks': {}, 'meta': {}})
                    if num is not None and b_id:
                        variant_entry['benchmarks'][b_id] = num
            # continue to next file
            continue

        # --- Added: support alternative schema with model_info + benchmark_results (e.g., qwen3_vl.json) ---
        if 'benchmark_results' in raw and 'model_info' in raw and 'benchmarks' not in raw and 'variants' not in raw:
            mi = raw.get('model_info', {})
            family = mi.get('model_family') or 'qwen3'
            # map model_type vision-language -> vlm
            mtype = mi.get('model_type', '')
            modality = 'vlm' if 'vision' in mtype or 'vl' in mtype else 'llm'
            model_id = f"{family}_{modality}".lower()
            if model_id not in models:
                models[model_id] = {
                    'model_id': model_id,
                    'family': family,
                    'modality': modality,
                    'label': f"{family.capitalize()} {modality.upper()}",
                    'variants': {}
                }
            # choose tested variant name
            notes = raw.get('notes', {})
            tested_variant = notes.get('model_tested')
            if not tested_variant:
                # fallback: largest params variant from model_info.variants
                vlist = mi.get('variants', [])
                def _params_num(p):
                    if not isinstance(p, str):
                        return 0
                    # extract leading number (handle B suffix, parentheses)
                    m = re.search(r'(\d+(?:\.\d+)?)', p)
                    return float(m.group(1)) if m else 0
                largest = None
                max_size = -1
                for v in vlist:
                    sz = _params_num(v.get('params', ''))
                    if sz > max_size:
                        max_size = sz
                        largest = v.get('name')
                tested_variant = largest or 'default'
            variant_entry = models[model_id]['variants'].setdefault(tested_variant, {'benchmarks': {}, 'meta': {'schema':'benchmark_results'}})
            for bench in raw.get('benchmark_results', []):
                if not isinstance(bench, dict):
                    continue
                b_id = bench.get('benchmark_id') or bench.get('name')
                val = bench.get('value')
                if not b_id or val is None:
                    continue
                # handle multi-value like "67.1% / 61.8%"
                if isinstance(val, str) and '/' in val:
                    parts = [p.strip() for p in val.split('/') if p.strip()]
                    # heuristic language mapping for ocrbench en/zh
                    suffixes = ['part1', 'part2']
                    if 'ocrbench' in b_id.lower():
                        suffixes = ['en', 'zh']
                    for i, pval in enumerate(parts):
                        try:
                            if pval.endswith('%'):
                                num = float(pval.replace('%', '').replace('~', '')) / 100.0
                            else:
                                num = float(pval)
                        except Exception:
                            num = None
                        if num is not None:
                            variant_entry['benchmarks'][f"{b_id}_{suffixes[i]}"] = num
                    continue
                # normal single value parsing
                try:
                    if isinstance(val, str) and val.strip().endswith('%'):
                        num = float(val.strip().replace('%', '').replace('~', '')) / 100.0
                    elif isinstance(val, (int, float)):
                        num = float(val)
                    else:
                        num = float(val) if re.match(r'^\d+(?:\.\d+)?$', str(val)) else None
                except Exception:
                    num = None
                if num is not None:
                    variant_entry['benchmarks'][b_id] = num
            # continue; skip remaining standard parsing for this file
            continue

        family = raw.get('model_family') or raw.get('family')
        modality = raw.get('modality')
        if not family or not modality:
            inf_family, inf_modality = infer_family_modality_from_filename(path.name)
            family = family or inf_family
            modality = modality or inf_modality

        model_id = f"{family}_{modality}".lower()
        label = f"{family.capitalize()} {modality.upper()}" if family != 'generic' else model_id

        # Initialize model entry if first time
        if model_id not in models:
            models[model_id] = {
                'model_id': model_id,
                'family': family,
                'modality': modality,
                'label': label,
                'variants': {}
            }

        variants = raw.get('variants', {})
        if isinstance(variants, list):
            for v in variants:
                name = v.get('name') or v.get('variant') or 'unknown'
                benchmarks = v.get('benchmarks') or v.get('scores') or {}
                models[model_id]['variants'][name] = {
                    'benchmarks': benchmarks,
                    'meta': {k: v[k] for k in v.keys() if k not in ('name', 'variant', 'benchmarks', 'scores')}
                }
        elif isinstance(variants, dict):
            for vname, vdata in variants.items():
                if not isinstance(vdata, dict):
                    continue
                benchmarks = vdata.get('benchmarks') or vdata.get('scores') or {
                    k: vdata[k] for k in vdata.keys() if isinstance(vdata[k], (int, float)) and k not in ('params', 'meta')
                }
                models[model_id]['variants'][vname] = {
                    'benchmarks': benchmarks,
                    'meta': {k: vdata.get(k) for k in vdata.keys() if k not in ('benchmarks', 'scores') and not isinstance(vdata.get(k), (int, float))}
                }
        else:
            print(f"[warn] variants format unrecognized in {path.name}", file=sys.stderr)

    # Filter out entries with no variants
    empty_ids = [mid for mid, m in models.items() if not m['variants']]
    for mid in empty_ids:
        print(f"[warn] dropping model {mid}: no variants", file=sys.stderr)
        models.pop(mid, None)
    return models


def build_html(models: Dict[str, Dict[str, Any]], title: str, max_models: int) -> str:
    """Compose final single-file HTML with improved bar chart readability."""
    data_json = json.dumps(models, ensure_ascii=False)
    category_json = json.dumps(CATEGORY_KEYWORDS, ensure_ascii=False)
    parts: List[str] = []
    parts.append("<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/><title>" + title + "</title>")
    parts.append("<style>body{font-family:system-ui,Arial,sans-serif;margin:0;background:#f7f9fb;color:#222}header{padding:16px 24px;background:#1f2937;color:#fff}header h1{margin:0;font-size:20px}#app{padding:16px 24px}.flex{display:flex;gap:16px;flex-wrap:wrap}.card{background:#fff;border-radius:8px;padding:12px 16px;box-shadow:0 2px 4px rgba(0,0,0,.08);flex:1 1 320px;min-width:300px}select,button{padding:4px 8px;margin:4px}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:12px}th,td{padding:4px 6px;border:1px solid #eee;text-align:left}th{background:#fafafa;position:sticky;top:0}.chart{width:100%;}.model-slot{background:#eef3f8;padding:8px;border-radius:6px;margin-bottom:8px}.model-slot h3{margin:0 0 4px;font-size:14px}.category-filters button{background:#fff;border:1px solid #ccc;border-radius:4px;cursor:pointer}.category-filters button.active{background:#1f77b4;color:#fff;border-color:#1f77b4}</style></head><body>")
    parts.append(f"<header><h1>{title}</h1></header><div id='app'><p style='font-size:12px;'>Dashboard v2 – up to {max_models} concurrent models. Data loaded from repository JSON files.</p>")
    parts.append("<div class='flex'>")
    parts.append("<div class='card' style='max-width:340px;'><h2 style='margin-top:0;'>Model Selection</h2>")
    parts.append("<div v-for='(slot,idx) in selectedSlots' class='model-slot'><h3>Slot {{idx + 1}}</h3><label>Model Family:&nbsp;<select v-model='slot.modelId'><option disabled value=''>-- choose --</option><option v-for='m in modelList' :value='m.model_id'>{{m.label}}</option></select></label><br/><label v-if='slot.modelId'>Variant:&nbsp;<select v-model='slot.variant'><option v-for='v in variantOptions(slot.modelId)' :value='v'>{{v}}</option></select></label><br/><button @click='clearSlot(idx)' v-if='slot.modelId'>Clear</button></div><button @click='addSlot' :disabled='selectedSlots.length >= maxModels'>Add Model Slot</button></div>")
    parts.append("<div class='card'><h2 style='margin-top:0;'>Radar Comparison</h2><div id='radar' class='chart' style='height:360px;'></div></div>")
    parts.append("<div class='card'><h2 style='margin-top:0;'>Top Benchmarks</h2><div id='bar' class='chart' style='height:420px;'></div></div></div>")
    parts.append("<div class='card' style='margin-top:16px;'><h2 style='margin-top:0;'>Benchmark Table</h2><div class='category-filters'><button :class='{active: activeCategory === c}' v-for='c in categories' @click='activeCategory = c'>{{c}}</button><button :class='{active: activeCategory === \"all\"}' @click='activeCategory = \"all\"'>all</button></div><div class='table-wrap'><table><thead><tr><th>Benchmark</th><th>Category</th><th v-for='slot in selectedSlots'>{{displayLabel(slot)}}</th></tr></thead><tbody><tr v-for='row in filteredRows'><td>{{row.id}}</td><td>{{row.category}}</td><td v-for='slot in selectedSlots'>{{formatScore(row.values[slotKey(slot)])}}</td></tr></tbody></table></div></div>")
    parts.append("<footer>Generated by dashboard v2. Vue & ECharts via CDN. Edit category keywords inside HTML file if needed.</footer></div>")
    parts.append("<script src='https://cdn.jsdelivr.net/npm/vue@3.4.21/dist/vue.global.prod.js'></script><script src='https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js'></script>")
    parts.append(f"<script>const RAW_MODELS={data_json};const CATEGORY_KEYWORDS={category_json};")
    parts.append("const app=Vue.createApp({data(){return{models:RAW_MODELS,maxModels:" + str(max_models) + ",selectedSlots:[{modelId:'',variant:''}],activeCategory:'all'};},computed:{modelList(){return Object.values(this.models);},categories(){return Object.keys(CATEGORY_KEYWORDS);},allBenchmarkIds(){const ids=new Set();for(const m of Object.values(this.models)){for(const v of Object.values(m.variants)){for(const b of Object.keys(v.benchmarks||{}))ids.add(b);}}return Array.from(ids).sort();},tableRows(){return this.allBenchmarkIds.map(id=>{const category=this.categorize(id);const values={};for(const slot of this.selectedSlots){values[this.slotKey(slot)]=this.getScore(slot,id);}return{id,category,values};});},filteredRows(){if(this.activeCategory==='all')return this.tableRows;return this.tableRows.filter(r=>r.category===this.activeCategory);}},methods:{addSlot(){if(this.selectedSlots.length<this.maxModels){this.selectedSlots.push({modelId:'',variant:''});this.$nextTick(this.refreshCharts);}},clearSlot(idx){this.selectedSlots.splice(idx,1);if(this.selectedSlots.length===0){this.selectedSlots.push({modelId:'',variant:''});}this.$nextTick(this.refreshCharts);},variantOptions(modelId){if(!modelId)return[];return Object.keys(this.models[modelId].variants);},slotKey(slot){return slot.modelId+'|'+slot.variant;},displayLabel(slot){if(!slot.modelId)return'(empty)';const model=this.models[slot.modelId];return model.label+(slot.variant?' / '+slot.variant:'');},getScore(slot,benchId){if(!slot.modelId||!slot.variant)return null;const model=this.models[slot.modelId];const variant=model.variants[slot.variant];if(!variant)return null;const val=variant.benchmarks[benchId];return typeof val==='number'?val:null;},formatScore(v){if(v==null)return'';if(v>0&&v<1)return(v*100).toFixed(1)+'%';return Number(v).toFixed(3);},categorize(id){const lid=id.toLowerCase();for(const [cat,kws] of Object.entries(CATEGORY_KEYWORDS)){if(kws.some(k=>lid.includes(k)))return cat;}return'other';},radarData(){const slotSeries=[];for(const slot of this.selectedSlots){if(!slot.modelId||!slot.variant)continue;const catAgg={};const counts={};for(const bench of this.allBenchmarkIds){const cat=this.categorize(bench);const s=this.getScore(slot,bench);if(s==null)continue;catAgg[cat]=(catAgg[cat]||0)+s;counts[cat]=(counts[cat]||0)+1;}slotSeries.push({name:this.displayLabel(slot),values:catAgg});}return slotSeries;},barData(){const benchScores=[];for(const bench of this.allBenchmarkIds){let acc=0;let n=0;for(const slot of this.selectedSlots){const v=this.getScore(slot,bench);if(v!=null){acc+=v;n++;}}if(n>0)benchScores.push({id:bench,avg:acc/n});}benchScores.sort((a,b)=>b.avg-a.avg);return benchScores.slice(0,15);},refreshCharts(){this.$nextTick(()=>{this.renderRadar();this.renderBar();});},renderRadar(){const el=document.getElementById('radar');if(!el)return;const chart=echarts.getInstanceByDom(el)||echarts.init(el);const seriesData=this.radarData();const categories=Array.from(new Set(seriesData.flatMap(s=>Object.keys(s.values))));const indicators=categories.map(c=>({name:c}));chart.setOption({tooltip:{formatter:p=>p.name},legend:{data:seriesData.map(s=>s.name)},radar:{indicator:indicators},series:[{type:'radar',data:seriesData.map(s=>({name:s.name,value:categories.map(c=>s.values[c]?s.values[c].toFixed(3):0)}))}]});},renderBar(){const el=document.getElementById('bar');if(!el)return;const chart=echarts.getInstanceByDom(el)||echarts.init(el);const data=this.barData();chart.setOption({tooltip:{formatter:(params)=>params.name},grid:{left:220,right:40,top:40,bottom:25},xAxis:{type:'value'},yAxis:{type:'category',data:data.map(d=>d.id).reverse(),axisLabel:{interval:0,width:200,overflow:'break',fontSize:12}},series:[{type:'bar',data:data.map(d=>({value:d.avg,name:d.id})).reverse(),label:{show:true,position:'right',fontSize:12,formatter:(p)=>{const v=p.value;return v>0&&v<1?(v*100).toFixed(1)+'%':Number(v).toFixed(3);}}}]});}},watch:{selectedSlots:{handler(){this.refreshCharts();},deep:true},activeCategory(){this.refreshCharts();}},mounted(){this.refreshCharts();}});app.mount('#app');</script></body></html>")
    return "".join(parts)
def main():
    parser = argparse.ArgumentParser(description="Generate multi-model dashboard HTML (v2)")
    parser.add_argument('--data-dir', default='benchmarks/models', help='Directory containing model JSON benchmark files')
    parser.add_argument('--out', default='benchmarks/models/qwen3_dashboard_v2.html', help='Output HTML file path')
    parser.add_argument('--max-models', type=int, default=3, help='Maximum concurrent model slots selectable')
    parser.add_argument('--title', default='Model Performance Dashboard v2', help='Dashboard title')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"[error] data directory not found: {data_dir}", file=sys.stderr)
        sys.exit(1)

    models = load_models(data_dir)
    if not models:
        print(f"[error] no valid models discovered in {data_dir}", file=sys.stderr)
        sys.exit(2)

    html = build_html(models, args.title, args.max_models)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')
    print(f"[info] dashboard written: {out_path}")
    print(f"[info] models included: {len(models)} | variants total: {sum(len(m['variants']) for m in models.values())}")


if __name__ == '__main__':
    main()
