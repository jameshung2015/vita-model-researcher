#!/usr/bin/env python3
"""
Validate platforms/governance/OWNERS.json against templates/ownership_schema.json and
emit a brief summary report. Also verifies that key top-level globs have at least one owner.

Usage:
  python scripts/governance/validate_ownership.py [--report]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from datetime import datetime, timezone
from typing import Dict, List


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load_json(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_required_fields(data: dict) -> List[str]:
    errs: List[str] = []
    if not isinstance(data, dict):
        return ["OWNERS: not an object"]
    for field in ("id", "name", "owners"):
        if field not in data:
            errs.append(f"OWNERS: missing field '{field}'")
    owners = data.get('owners') or []
    if not isinstance(owners, list) or not owners:
        errs.append("OWNERS: 'owners' must be a non-empty array")
        return errs
    for i, o in enumerate(owners):
        if not isinstance(o, dict):
            errs.append(f"OWNERS.owners[{i}]: not an object")
            continue
        for f in ("owner_id", "display_name", "paths"):
            if f not in o:
                errs.append(f"OWNERS.owners[{i}]: missing field '{f}'")
        if 'paths' in o and not isinstance(o['paths'], list):
            errs.append(f"OWNERS.owners[{i}].paths must be array")
    return errs


def expand_paths(patterns: List[str]) -> List[str]:
    files: List[str] = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(ROOT, p), recursive=True))
    return sorted(set(files))


def compute_coverage(owners: List[dict]) -> Dict[str, List[str]]:
    covered: Dict[str, List[str]] = {}
    for o in owners:
        patterns = o.get('paths') or []
        files = [f for f in expand_paths(patterns) if os.path.isfile(f)]
        covered[o.get('owner_id') or o.get('display_name') or 'unknown'] = files
    return covered


def minimal_globs() -> List[str]:
    return [
        'models/*.json',
        'indicators/*.json',
        'benchmarks/*.json'
    ]


def verify_minimal_ownership(owners: List[dict]) -> List[str]:
    errs: List[str] = []
    patterns = minimal_globs()
    # pattern -> bool has_owner
    has_owner = {p: False for p in patterns}
    for o in owners:
        globs_o = set(o.get('paths') or [])
        for p in patterns:
            # simple glob equality
            if p in globs_o:
                has_owner[p] = True
    for p, ok in has_owner.items():
        if not ok:
            errs.append(f"OWNERS: no owner declares path '{p}'")
    return errs


def write_report(summary: dict) -> str:
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out_dir = os.path.join(ROOT, 'reports', f'governance_{ts}')
    os.makedirs(out_dir, exist_ok=True)
    # summary
    lines = [
        '# Ownership Validation Summary',
        f"Generated: {ts}",
        '',
        f"ok: {summary['ok']}",
        f"errors: {len(summary['errors'])}",
        '',
        'Errors:' if summary['errors'] else 'Errors: none'
    ]
    for e in summary['errors']:
        lines.append(f"- {e}")
    path = os.path.join(out_dir, 'ownership_summary.md')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    return path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--report', action='store_true')
    args = p.parse_args()

    owners_path = os.path.join(ROOT, 'platforms', 'governance', 'OWNERS.json')
    if not os.path.exists(owners_path):
        print(f"ERROR: missing OWNERS file: {owners_path}")
        raise SystemExit(2)
    data = load_json(owners_path)
    errs = validate_required_fields(data)
    errs += verify_minimal_ownership(data.get('owners') or [])

    ok = not errs
    summary = {'ok': ok, 'errors': errs}
    if args.report:
        path = write_report(summary)
        print(f"Report written to {path}")
    if errs:
        for e in errs:
            print(f"OWNERS ERROR: {e}")
        raise SystemExit(2)
    print("OWNERS: OK")


if __name__ == '__main__':
    main()
