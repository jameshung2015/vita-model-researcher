#!/usr/bin/env python3
"""
Bulk fetch sources (arXiv/HuggingFace/official pages) and cache to MongoDB.

Usage (PowerShell):
  $env:MONGO_URI="mongodb://root:example@localhost:27017/?authSource=admin"
  $env:DB_NAME="agents_kb"
  python agents-toolchain/ingestion/bulk_fetch.py --file agents-toolchain/ingestion/sources/samples.txt

Notes:
- Computes fingerprint = sha256(url + body). Upserts on fingerprint to avoid duplicates.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime

import requests

try:
    from pymongo import MongoClient, UpdateOne
except Exception:
    print("Missing dependency: pymongo. Install with 'pip install pymongo'.", file=sys.stderr)
    raise


def read_urls(path: str) -> list[str]:
    urls = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            urls.append(s)
    return urls


def fetch(url: str, timeout: int = 20) -> dict:
    r = requests.get(url, timeout=timeout)
    body = r.text or ''
    fp = hashlib.sha256((url + '\n' + body).encode('utf-8', errors='ignore')).hexdigest()
    return {
        'url': url,
        'status': r.status_code,
        'content_snippet': body[:5120],
        'source_len': len(body),
        'fetched_at': datetime.utcnow().isoformat() + 'Z',
        'fingerprint': fp
    }


def bulk_insert(uri: str, db_name: str, docs: list[dict], coll_name: str = 'sources_cache'):
    client = MongoClient(uri)
    db = client[db_name]
    ops = []
    for d in docs:
        ops.append(UpdateOne({'fingerprint': d['fingerprint']}, {'$setOnInsert': d}, upsert=True))
    if ops:
        res = db[coll_name].bulk_write(ops, ordered=False)
        return {'matched': res.matched_count, 'upserted': len(res.upserted_ids)}
    return {'matched': 0, 'upserted': 0}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--file', required=True, help='path to a file with URLs (one per line)')
    p.add_argument('--uri', default=os.getenv('MONGO_URI'))
    p.add_argument('--db', default=os.getenv('DB_NAME', 'agents_kb'))
    args = p.parse_args()

    if not args.uri:
        print('MONGO_URI not provided (env or --uri).', file=sys.stderr)
        sys.exit(2)

    urls = read_urls(args.file)
    docs = []
    for u in urls:
        try:
            docs.append(fetch(u))
        except Exception as e:
            print(f"Fetch error: {u}: {e}", file=sys.stderr)
    res = bulk_insert(args.uri, args.db, docs)
    print({'urls': len(urls), **res})


if __name__ == '__main__':
    main()

