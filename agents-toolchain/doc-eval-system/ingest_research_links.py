#!/usr/bin/env python3
"""
Inject research_doc and last_reviewed into corresponding benchmarks/*.json
based on files under agents-toolchain/doc-eval-system/*_research.md.

This keeps external research knowledge discoverable from benchmark entries.
"""
from pathlib import Path
import json
import datetime as dt


ROOT = Path(__file__).resolve().parents[2]
DOC_DIR = ROOT / 'agents-toolchain' / 'doc-eval-system'
BM_DIR = ROOT / 'benchmarks'


def main():
    # map research doc stems to benchmark json filenames
    docs = list(DOC_DIR.glob('*_research.md'))
    today = dt.date.today().isoformat()
    updated = []
    for doc in docs:
        stem = doc.name.replace('_research.md', '')
        bm_json = BM_DIR / f'{stem}.json'
        if not bm_json.exists():
            # try special case mapping
            if stem == 'modelscope':
                bm_json = BM_DIR / 'modelscope_leaderboard.json'
            if not bm_json.exists():
                continue
        try:
            data = json.load(open(bm_json, 'r', encoding='utf-8-sig'))
        except Exception:
            # fallback read
            data = json.load(open(bm_json, 'r', encoding='utf-8'))
        # inject/overwrite fields
        data['research_doc'] = str(doc.relative_to(ROOT)).replace('\\', '/')
        if 'last_reviewed' not in data:
            data['last_reviewed'] = today
        else:
            # keep existing if newer; else update
            try:
                old = dt.date.fromisoformat(str(data['last_reviewed']))
                if old < dt.date.today():
                    data['last_reviewed'] = today
            except Exception:
                data['last_reviewed'] = today
        with open(bm_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        updated.append(bm_json)

    # write a small report next to docs dir
    out_dir = ROOT / 'reports' / f'doc_eval_ingest_{int(dt.datetime.utcnow().timestamp())}'
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = ['# Doc Eval System Ingestion', '', f'Updated {len(updated)} benchmark files with research_doc links.', '']
    for p in updated:
        summary.append(f'- {p.relative_to(ROOT)}')
    (out_dir / 'summary.md').write_text('\n'.join(summary) + '\n', encoding='utf-8')
    print(f'Wrote report to {out_dir}')


if __name__ == '__main__':
    main()

