#!/usr/bin/env python3
"""
Export MongoDB collections to local JSON snapshots.

Usage (PowerShell):
  $env:MONGO_URI="mongodb://root:example@mongodb:27017/?authSource=admin"
  $env:DB_NAME="agents_kb"
  python scripts/ingest/snapshot_export.py --collections sources_cache taxonomy_versions --out snapshots
"""
import argparse
import json
import os
import sys
from datetime import datetime

try:
    from pymongo import MongoClient
except Exception as e:
    print("Missing dependency: pymongo. Install with 'pip install pymongo'.", file=sys.stderr)
    raise


def export_collections(uri: str, db_name: str, colls: list[str], out_dir: str) -> list[str]:
    client = MongoClient(uri)
    db = client[db_name]
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    written = []
    for c in colls:
        path = os.path.join(out_dir, f"{c}_{ts}.jsonl")
        with open(path, 'w', encoding='utf-8') as f:
            for doc in db[c].find({}):
                # convert ObjectId
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
        written.append(path)
    return written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uri', default=os.getenv('MONGO_URI'))
    parser.add_argument('--db', default=os.getenv('DB_NAME', 'agents_kb'))
    parser.add_argument('--collections', nargs='+', required=True)
    parser.add_argument('--out', default='snapshots')
    args = parser.parse_args()

    if not args.uri:
        print('MONGO_URI not provided (env or --uri).', file=sys.stderr)
        sys.exit(2)

    paths = export_collections(args.uri, args.db, args.collections, args.out)
    print("Written:")
    for p in paths:
        print(" -", p)


if __name__ == '__main__':
    main()

