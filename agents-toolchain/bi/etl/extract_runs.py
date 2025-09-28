#!/usr/bin/env python3
"""Refactored ETL entrypoint using shared helper modules.

Provides run_etl() for reuse in tests. Connection fallback retains
original behaviour (retry with localhost when host 'postgres' fails).
Legacy in-place upsert functions were moved to `extract_common.py` to keep
this file focused on orchestration.
"""
import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

from .settings import build_conninfo
from . import extract_common as ec

load_dotenv()

PG_CONN = build_conninfo()

def _index_registration_docs(cur):  # kept local (low churn)
    from datetime import datetime
    from pathlib import Path
    from .settings import REPO_ROOT
    rdir = REPO_ROOT / 'registration'
    if not rdir.exists(): return 0
    c=0
    for md in rdir.glob('*.md'):
        try:
            text = md.read_text(encoding='utf-8-sig')
        except Exception:
            text = md.read_text(encoding='utf-8')
        title=None
        for ln in text.splitlines():
            if ln.startswith('# '):
                title = ln[2:].strip(); break
        cur.execute(
            """INSERT INTO bi.registration_docs(path,title,category,updated_at)
            VALUES (%(path)s,%(title)s,%(cat)s,%(ut)s)
            ON CONFLICT (path) DO UPDATE SET
              title=EXCLUDED.title, category=EXCLUDED.category, updated_at=EXCLUDED.updated_at""",
            {
                'path': str(md),
                'title': title,
                'cat': 'registration',
                'ut': datetime.utcfromtimestamp(md.stat().st_mtime),
            },
        )
        c+=1
    return c

def run_etl(conn):
    with conn.cursor(row_factory=dict_row) as cur:
        ec.upsert_models(cur)
        ec.upsert_scenarios(cur)
        ec.upsert_indicators(cur)
        ec.upsert_runs_flat(cur)
        _index_registration_docs(cur)
    conn.commit()

def main():
    try:
        with psycopg.connect(PG_CONN) as conn:
            run_etl(conn)
            return
    except Exception as e:
        if 'getaddrinfo failed' in str(e) and ('postgres' in PG_CONN):
            print('[info] ETL primary host "postgres" unresolved, retrying with localhost...')
            with psycopg.connect(build_conninfo('localhost')) as conn:
                run_etl(conn)
        else:
            raise

if __name__ == '__main__':
    main()
