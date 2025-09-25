#!/usr/bin/env python3
"""
Render unified_v1 metric items into a simple Markdown summary.

Input: JSON (list of items), each item has
  - metric_id, value, ci (opt), samples_used (opt), meta (dict with model, etc.)

Output: Markdown printed to stdout or written to --out
"""
import argparse
import json
from pathlib import Path


def render(items):
    lines = ["# Metrics Summary", ""]
    lines.append("metric_id | model | value | samples | snapshot_ts | rank | votes")
    lines.append("---|---|---:|---:|---:|---:|---:")
    for it in items:
        mid = it.get('metric_id')
        v = it.get('value')
        samples = it.get('samples_used')
        meta = it.get('meta') or {}
        model = meta.get('model')
        ts = meta.get('snapshot_ts')
        rank = meta.get('rank')
        votes = meta.get('votes')
        lines.append(f"{mid} | {model} | {v} | {samples} | {ts} | {rank} | {votes}")
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--in', dest='inp', required=True, type=Path)
    p.add_argument('--out', dest='out', type=Path)
    args = p.parse_args()

    items = json.load(open(args.inp, 'r', encoding='utf-8-sig'))
    if not isinstance(items, list):
        items = [items]
    md = render(items)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(md, encoding='utf-8')
        print(f"Wrote summary to {args.out}")
    else:
        print(md)


if __name__ == '__main__':
    main()

