#!/usr/bin/env python3
"""
Audit taxonomy changes between two snapshots and append entries to logs/entity_change.jsonl.

Rules:
- Added tags -> type: added_tag
- Removed tags -> type: removed_tag
- Optional rename/merge detection via alias map: JSON {category: {old: new|string[]}}

Outputs:
- Append JSONL to logs/entity_change.jsonl
- Write summary to reports/taxonomy_audit_<ts>.md
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime


def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_aliases(path: str | None) -> dict:
    if not path:
        return {}
    try:
        return load_json(path)
    except Exception:
        return {}


def diff_cats(old: dict, new: dict) -> dict:
    out = {}
    keys = set(old.keys()) | set(new.keys())
    for k in sorted(keys):
        a = set(old.get(k, []))
        b = set(new.get(k, []))
        out[k] = {
            'added': sorted(b - a),
            'removed': sorted(a - b),
            'unchanged': sorted(a & b),
        }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('old')
    p.add_argument('new')
    p.add_argument('--alias', help='optional alias map json')
    p.add_argument('--logs', default='logs/entity_change.jsonl')
    p.add_argument('--out', default='reports')
    args = p.parse_args()

    old = load_json(args.old)
    new = load_json(args.new)
    alias = load_aliases(args.alias)
    diff = diff_cats(old.get('categories', {}), new.get('categories', {}))

    os.makedirs(os.path.dirname(args.logs), exist_ok=True)
    os.makedirs(args.out, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    actions = []
    for cat, d in diff.items():
        # Renames/merges via aliases
        amap = alias.get(cat, {}) if isinstance(alias.get(cat, {}), dict) else {}
        for rem in d['removed']:
            if rem in amap:
                tgt = amap[rem]
                if isinstance(tgt, list):
                    actions.append({"ts": ts, "type": "merge_tag", "category": cat, "from": rem, "to": tgt})
                else:
                    actions.append({"ts": ts, "type": "rename_tag", "category": cat, "from": rem, "to": tgt})
            else:
                actions.append({"ts": ts, "type": "removed_tag", "category": cat, "value": rem})
        for add in d['added']:
            actions.append({"ts": ts, "type": "added_tag", "category": cat, "value": add})

    # Append logs
    with open(args.logs, 'a', encoding='utf-8') as f:
        for a in actions:
            f.write(json.dumps(a, ensure_ascii=False) + '\n')

    # Summary markdown
    mpath = os.path.join(args.out, f"taxonomy_audit_{ts}.md")
    lines = ["# Taxonomy Audit", f"Generated: {ts}"]
    added = [a for a in actions if a['type'] == 'added_tag']
    removed = [a for a in actions if a['type'] == 'removed_tag']
    renames = [a for a in actions if a['type'] == 'rename_tag']
    merges = [a for a in actions if a['type'] == 'merge_tag']
    lines += [
        f"- Added tags: {len(added)}",
        f"- Removed tags: {len(removed)}",
        f"- Renames: {len(renames)}",
        f"- Merges: {len(merges)}",
        "\n## Details"
    ]
    for a in actions:
        if a['type'] in ('rename_tag', 'merge_tag'):
            if a['type'] == 'rename_tag':
                lines.append(f"- [{a['category']}] rename: {a['from']} -> {a['to']}")
            else:
                lines.append(f"- [{a['category']}] merge: {a['from']} -> {', '.join(a['to'])}")
    with open(mpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"Appended {len(actions)} entries to {args.logs}\nWrote {mpath}")


if __name__ == '__main__':
    main()

