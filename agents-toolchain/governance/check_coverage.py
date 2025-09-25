#!/usr/bin/env python3
"""
Check taxonomy coverage of the models directory.

Definition:
- Coverage = number of mapping entries in latest taxonomy snapshot / number of model JSON files.
- Pass if coverage >= threshold (default 0.95).

Usage:
  python agents-toolchain/governance/check_coverage.py --threshold 0.95
"""
from __future__ import annotations

import glob
import json
import os
from typing import Optional


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_latest_taxonomy(dir_path: str) -> Optional[dict]:
    files = sorted(glob.glob(os.path.join(dir_path, 'taxonomy_*.json')))
    if not files:
        return None
    latest = files[-1]
    with open(latest, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data['_path'] = latest
    return data


def count_valid_models(models_dir: str) -> int:
    total = 0
    for path in glob.glob(os.path.join(models_dir, '*.json')):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict) and (data.get('model_name') or data.get('name')):
                total += 1
        except Exception:
            continue
    return total


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--threshold', type=float, default=0.95)
    args = p.parse_args()

    tax = load_latest_taxonomy(os.path.join(ROOT, 'taxonomy_versions'))
    total_models = count_valid_models(os.path.join(ROOT, 'models'))
    if not tax or total_models == 0:
        print({'ok': False, 'reason': 'missing taxonomy or models', 'total_models': total_models})
        raise SystemExit(2)

    mappings = tax.get('mappings') or []
    coverage = len(mappings) / total_models
    ok = coverage >= args.threshold
    print({'ok': ok, 'coverage': round(coverage, 3), 'threshold': args.threshold, 'taxonomy': tax.get('_path')})
    if not ok:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
