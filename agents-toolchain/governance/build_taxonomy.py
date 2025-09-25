#!/usr/bin/env python3
"""
Build a taxonomy snapshot from existing model specs and cached sources.

Inputs:
  - models/*.json (required)
  - optional: MongoDB sources_cache (if MONGO_URI provided)

Output:
  - taxonomy_versions/taxonomy_YYYYMMDD.json
"""
import glob
import json
import os
from datetime import datetime, timezone
from collections import defaultdict


def load_models(root: str) -> list[dict]:
    models = []
    for path in glob.glob(os.path.join(root, 'models', '*.json')):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                models.append(json.load(f))
        except Exception:
            continue
    return models


def synthesize(models: list[dict]) -> dict:
    cats = defaultdict(set)
    mappings = []
    for m in models:
        model_id = m.get('model_id') or m.get('model_name') or m.get('name')
        io_in = m.get('input_types') or m.get('modalities') or []
        io_out = m.get('output_types') or []
        tags = m.get('tags') or []
        arch = m.get('architecture_family') or m.get('architecture_details') or ''
        size = m.get('size_params') or m.get('params') or ''

        for i in io_in:
            cats['inputs'].add(str(i).lower())
        for o in io_out:
            cats['outputs'].add(str(o).lower())
        if arch:
            cats['architecture'].add(str(arch).lower())
        if size:
            cats['size'].add(str(size).lower())
        for t in tags:
            cats['tags'].add(str(t).lower())

        mappings.append({
            'model_ref': model_id,
            'inputs': [str(i).lower() for i in io_in],
            'outputs': [str(o).lower() for o in io_out],
            'arch': str(arch).lower() if arch else None,
            'size': str(size).lower() if size else None,
            'tags': [str(t).lower() for t in tags],
        })

    return {
        'version': datetime.now(timezone.utc).strftime('%Y%m%d'),
        'categories': {k: sorted(v) for k, v in cats.items()},
        'mappings': mappings,
        'source': 'models_index',
    }


def write_snapshot(root: str, data: dict) -> str:
    out_dir = os.path.join(root, 'taxonomy_versions')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"taxonomy_{data['version']}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    models = load_models(root)
    data = synthesize(models)
    path = write_snapshot(root, data)
    print(f"Wrote taxonomy: {path}")


if __name__ == '__main__':
    main()
