"""
Generate baseline VRAM estimates for all variants in models/qwen3.json.
Saves per-variant JSON files under scripts/estimates/ and a combined summary.
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_FILE = ROOT / 'models' / 'qwen3.json'
EST_DIR = Path(__file__).resolve().parent / 'estimates'
EST_DIR.mkdir(parents=True, exist_ok=True)

with open(MODELS_FILE, 'r', encoding='utf-8') as f:
    qwen = json.load(f)

variants = qwen.get('variants', [])
summary = []

for v in variants:
    name = v['name']
    # run estimator for fp16 and int8 using defaults
    for precision in ['fp16', 'int8']:
        cmd = [
            'python',
            str(Path(__file__).resolve().parent / 'estimate_vram.py'),
            '--variant', name,
            '--precision', precision,
        ]
        # add --moe if variant is MoE-like
        if 'A' in name or 'MoE' in name or 'a' in name.lower():
            cmd.append('--moe')
        print('Running:', ' '.join(cmd))
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print('Error running estimator for', name, precision, proc.stderr)
            continue
        data = json.loads(proc.stdout)
        out_file = EST_DIR / f"{name.replace('/','_')}.{precision}.json"
        with open(out_file, 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        summary.append({'variant': name, 'precision': precision, 'file': str(out_file), 'estimated_per_gpu': data.get('estimated_vram_gb_per_gpu')})

# write combined summary
with open(EST_DIR / 'summary.json', 'w', encoding='utf-8') as s:
    json.dump(summary, s, ensure_ascii=False, indent=2)

print('Estimates generated in', EST_DIR)
