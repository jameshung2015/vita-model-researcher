#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_json(path: Path):
    # Accept files with or without BOM
    with open(path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)


def index_by_metric(items):
    out = {}
    for it in items:
        mid = it.get('metric_id')
        if mid:
            out[mid] = it
    return out


def summarize(diff_rows, threshold: float) -> str:
    lines = [
        "# Baseline Diff Summary",
        "",
        "Columns: metric_id | prev | curr | delta | over_threshold",
        ""
    ]
    for r in diff_rows:
        lines.append(f"- {r['metric_id']} | {r['prev']} | {r['curr']} | {r['delta']} | {r['over_threshold']}")
    lines.append("")
    lines.append(f"Threshold: {threshold}")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description='Diff two baseline JSON files and emit diff.json + summary.md')
    p.add_argument('--prev', required=True, type=Path)
    p.add_argument('--curr', required=True, type=Path)
    p.add_argument('--threshold', type=float, default=0.05)
    p.add_argument('--out_dir', type=Path, default=None, help='Where to write diff.json and summary.md (default: curr parent)')
    args = p.parse_args()

    prev = load_json(args.prev)
    curr = load_json(args.curr)

    # Normalize to list of metric items
    prev_items = prev if isinstance(prev, list) else [prev]
    curr_items = curr if isinstance(curr, list) else [curr]

    prev_idx = index_by_metric(prev_items)
    curr_idx = index_by_metric(curr_items)

    diff_rows = []
    for mid, c in curr_idx.items():
        pv = (prev_idx.get(mid) or {}).get('value')
        cv = c.get('value')
        if pv is None or cv is None:
            continue
        delta = round(cv - pv, 6)
        over = abs(delta) >= args.threshold
        diff_rows.append({
            'metric_id': mid,
            'prev': pv,
            'curr': cv,
            'delta': delta,
            'over_threshold': over
        })

    out_dir = args.out_dir or args.curr.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / 'diff.json', 'w', encoding='utf-8') as f:
        json.dump(diff_rows, f, ensure_ascii=False, indent=2)
    with open(out_dir / 'summary.md', 'w', encoding='utf-8') as f:
        f.write(summarize(diff_rows, args.threshold))

    print(f"Wrote {len(diff_rows)} rows to {out_dir / 'diff.json'} and summary.md")


if __name__ == '__main__':
    main()
