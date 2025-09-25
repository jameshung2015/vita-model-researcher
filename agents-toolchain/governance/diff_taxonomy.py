#!/usr/bin/env python3
"""
Diff two taxonomy snapshots and write JSON and Markdown summaries.

Usage:
  python agents-toolchain/governance/diff_taxonomy.py old.json new.json --out reports
"""
import argparse
import json
import os
from datetime import datetime


def load(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def diff_cats(old: dict, new: dict) -> dict:
    out = {}
    keys = set(old.keys()) | set(new.keys())
    for k in sorted(keys):
        a = set(old.get(k, []))
        b = set(new.get(k, []))
        out[k] = {
            'added': sorted(b - a),
            'removed': sorted(a - b),
            'unchanged_count': len(a & b)
        }
    return out


def write_reports(diff: dict, out_dir: str) -> tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    jpath = os.path.join(out_dir, f"taxonomy_diff_{ts}.json")
    mpath = os.path.join(out_dir, f"taxonomy_diff_{ts}.md")
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(diff, f, ensure_ascii=False, indent=2)
    lines = ["# Taxonomy Diff", "", f"Generated: {ts}"]
    for k, v in diff.items():
        lines.append(f"\n## {k}")
        if v['added']:
            lines.append(f"- Added ({len(v['added'])}): " + ", ".join(v['added']))
        if v['removed']:
            lines.append(f"- Removed ({len(v['removed'])}): " + ", ".join(v['removed']))
        lines.append(f"- Unchanged count: {v['unchanged_count']}")
    with open(mpath, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")
    return jpath, mpath


def main():
    p = argparse.ArgumentParser()
    p.add_argument('old')
    p.add_argument('new')
    p.add_argument('--out', default='reports')
    args = p.parse_args()
    old = load(args.old)
    new = load(args.new)
    diff = diff_cats(old.get('categories', {}), new.get('categories', {}))
    jpath, mpath = write_reports(diff, args.out)
    print(f"Wrote: {jpath}\nWrote: {mpath}")


if __name__ == '__main__':
    main()

