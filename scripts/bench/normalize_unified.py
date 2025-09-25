#!/usr/bin/env python3
"""
Normalize leaderboard or raw metric rows into unified_v1 items.

Input:
  - JSON array of rows, e.g. from scripts/bench/lmarena_pull.py
  - Each row should have at least: model, snapshot_ts, and fields for the metric

Output unified_v1 items (JSON array):
  [{
     "metric_id": "...",
     "value": 0.0,
     "ci": null,
     "samples_used": 0,
     "meta": { "...": "..." }
  }]

Supported metrics:
  - win_rate        (expects field 'win_rate' and optional 'votes')
  - elo_rating      (expects field 'elo' and optional 'rank','votes')
"""
import argparse
import json
from pathlib import Path


def normalize_win_rate(rows):
    items = []
    for r in rows:
        if 'win_rate' not in r:
            continue
        value = r.get('win_rate')
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        samples = r.get('votes')
        try:
            samples = int(samples) if samples is not None else None
        except (TypeError, ValueError):
            samples = None
        items.append({
            "metric_id": "win_rate",
            "value": value,
            "ci": None,
            "samples_used": samples,
            "meta": {
                "model": r.get('model'),
                "rank": r.get('rank'),
                "snapshot_ts": r.get('snapshot_ts'),
                "votes": r.get('votes')
            }
        })
    return items


def normalize_elo(rows):
    items = []
    for r in rows:
        if 'elo' not in r:
            continue
        value = r.get('elo')
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        items.append({
            "metric_id": "elo_rating",
            "value": value,
            "ci": None,
            "samples_used": None,
            "meta": {
                "model": r.get('model'),
                "rank": r.get('rank'),
                "snapshot_ts": r.get('snapshot_ts'),
                "votes": r.get('votes')
            }
        })
    return items


def main():
    p = argparse.ArgumentParser(description='Normalize rows to unified_v1 items')
    p.add_argument('--in', dest='inp', required=True, type=Path, help='Input JSON (array of rows)')
    p.add_argument('--out', dest='out', required=True, type=Path, help='Output JSON path (array of unified_v1 items)')
    p.add_argument('--metric', required=True, choices=['win_rate','elo_rating'])
    p.add_argument('--models', type=str, default='', help='Optional comma-separated model names to include')
    args = p.parse_args()

    with open(args.inp, 'r', encoding='utf-8-sig') as f:
        rows = json.load(f)

    models = [m.strip() for m in args.models.split(',') if m.strip()] if args.models else []
    if models:
        rows = [r for r in rows if r.get('model') in models]

    if args.metric == 'win_rate':
        items = normalize_win_rate(rows)
    else:
        items = normalize_elo(rows)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f'Wrote {len(items)} unified items to {args.out}')


if __name__ == '__main__':
    main()

