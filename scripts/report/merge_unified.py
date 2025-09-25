#!/usr/bin/env python3
"""
Merge multiple unified_v1 JSON files (arrays or single item) into a single array.
Usage:
  python scripts/report/merge_unified.py --out merged.json file1.json file2.json ...
"""
import argparse
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('inputs', nargs='+')
    args = p.parse_args()

    merged = []
    for ip in args.inputs:
        with open(ip, 'r', encoding='utf-8-sig') as f:
            obj = json.load(f)
        if isinstance(obj, list):
            merged.extend(obj)
        else:
            merged.append(obj)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f'Merged {len(args.inputs)} files into {args.out} with {len(merged)} items')


if __name__ == '__main__':
    main()

