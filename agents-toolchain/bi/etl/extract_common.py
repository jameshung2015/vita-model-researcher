"""Common ETL upsert helper functions.

Functions receive a psycopg cursor and operate idempotently. Each returns a
count of processed records (informational only).
"""
from __future__ import annotations
import json, re
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .settings import REPO_ROOT


def _load_json(path: Path):
    txt = path.read_text(encoding='utf-8-sig')
    return json.loads(txt)


def as_list(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def upsert_models(cur) -> int:
    c = 0
    for mp in (REPO_ROOT / 'models').glob('*.json'):
        try:
            m = _load_json(mp)
        except Exception:
            continue
        mid = m.get('model_name')
        if not mid:
            continue
        cur.execute(
            """
            INSERT INTO bi.models (id,name,family,vendor,params,tags,owner,created_at,updated_at)
            VALUES (%(id)s,%(name)s,%(family)s,%(vendor)s,%(params)s,%(tags)s,%(owner)s,%(created_at)s,%(updated_at)s)
            ON CONFLICT (id) DO UPDATE SET
              name=EXCLUDED.name, family=EXCLUDED.family, vendor=EXCLUDED.vendor,
              params=EXCLUDED.params, tags=EXCLUDED.tags, owner=EXCLUDED.owner, updated_at=EXCLUDED.updated_at
            """,
            {
                'id': mid,
                'name': m.get('short_description') or mid,
                'family': m.get('architecture_family'),
                'vendor': (m.get('provenance') or {}).get('provider'),
                'params': json.dumps({k: m.get(k) for k in ('variants','size_params','capabilities') if m.get(k) is not None}, ensure_ascii=False),
                'tags': as_list(m.get('tags')),
                'owner': None,
                'created_at': None,
                'updated_at': datetime.utcnow(),
            },
        )
        for var in as_list(m.get('variants')):
            vname = var.get('name') if isinstance(var, dict) else None
            if not vname:
                continue
            cur.execute(
                """
                INSERT INTO bi.models (id,name,family,vendor,params,tags,owner,created_at,updated_at)
                VALUES (%(id)s,%(name)s,%(family)s,%(vendor)s,%(params)s,%(tags)s,%(owner)s,%(created_at)s,%(updated_at)s)
                ON CONFLICT (id) DO UPDATE SET
                  name=EXCLUDED.name, family=EXCLUDED.family, vendor=EXCLUDED.vendor,
                  params=EXCLUDED.params, tags=EXCLUDED.tags, owner=EXCLUDED.owner, updated_at=EXCLUDED.updated_at
                """,
                {
                    'id': vname,
                    'name': vname,
                    'family': m.get('architecture_family'),
                    'vendor': (m.get('provenance') or {}).get('provider'),
                    'params': json.dumps(var, ensure_ascii=False),
                    'tags': as_list(m.get('tags')),
                    'owner': None,
                    'created_at': None,
                    'updated_at': datetime.utcnow(),
                },
            )
        c += 1
    return c


def upsert_scenarios(cur) -> int:
    c=0
    for sp in (REPO_ROOT / 'scenarios').rglob('scn_*.json'):
        try:
            s = _load_json(sp)
        except Exception:
            continue
        sid = s.get('scenario_id')
        if not sid:
            continue
        cur.execute(
            """
            INSERT INTO bi.scenarios (id,name,description,required_atomic_capabilities,recommended_agents,priority_indicators,minimal_test_cases,extra,created_at,updated_at)
            VALUES (%(id)s,%(name)s,%(description)s,%(rac)s,%(ra)s,%(pi)s,%(mtc)s,%(extra)s,%(created_at)s,%(updated_at)s)
            ON CONFLICT (id) DO UPDATE SET
              name=EXCLUDED.name, description=EXCLUDED.description,
              required_atomic_capabilities=EXCLUDED.required_atomic_capabilities,
              recommended_agents=EXCLUDED.recommended_agents,
              priority_indicators=EXCLUDED.priority_indicators,
              minimal_test_cases=EXCLUDED.minimal_test_cases,
              extra=EXCLUDED.extra,
              updated_at=EXCLUDED.updated_at
            """,
            {
                'id': sid,
                'name': s.get('name'),
                'description': s.get('description'),
                'rac': json.dumps(s.get('required_atomic_capabilities')),
                'ra': json.dumps(s.get('recommended_agents')),
                'pi': json.dumps(s.get('priority_indicators')),
                'mtc': json.dumps(s.get('minimal_test_cases')),
                'extra': None,
                'created_at': None,
                'updated_at': datetime.utcnow(),
            },
        )
        c+=1
    return c


def upsert_indicators(cur) -> int:
    c=0
    for ip in (REPO_ROOT / 'indicators').glob('*.json'):
        try:
            ind = _load_json(ip)
        except Exception:
            continue
        iid = ind.get('id')
        if not iid:
            continue
        cur.execute(
            """
            INSERT INTO bi.indicators (id,name,category,unit,higher_is_better,source,owner,aliases)
            VALUES (%(id)s,%(name)s,%(category)s,%(unit)s,%(hib)s,%(source)s,%(owner)s,%(aliases)s)
            ON CONFLICT (id) DO UPDATE SET
              name=EXCLUDED.name, category=EXCLUDED.category, unit=EXCLUDED.unit, higher_is_better=EXCLUDED.higher_is_better,
              source=EXCLUDED.source, owner=EXCLUDED.owner, aliases=EXCLUDED.aliases
            """,
            {
                'id': iid,
                'name': ind.get('name'),
                'category': ind.get('category'),
                'unit': ind.get('unit'),
                'hib': ind.get('higher_is_better'),
                'source': ind.get('source'),
                'owner': ind.get('owner'),
                'aliases': None,
            },
        )
        c+=1
    return c


def upsert_runs_flat(cur) -> int:
    reports = REPO_ROOT / 'reports'
    if not reports.exists(): return 0
    ts_dir_re = re.compile(r".*_(\d{10})$")
    c=0
    for dirpath in sorted(p for p in reports.glob('*') if p.is_dir()):
        run_id = dirpath.name
        m = ts_dir_re.match(run_id)
        from datetime import datetime as _dt
        started_at=None
        if m:
            try:
                started_at = _dt.utcfromtimestamp(int(m.group(1)))
            except Exception:
                started_at=None
        for fp in dirpath.rglob('*.json'):
            try:
                arr = _load_json(fp)
            except Exception:
                continue
            items = arr if isinstance(arr, list) else [arr]
            for it in items:
                if not isinstance(it, dict) or 'metric_id' not in it: continue
                metric_id = it.get('metric_id')
                if metric_id == 'toxicity_rate':
                    metric_id = 'toxicity'
                value = it.get('value')
                meta = it.get('meta') or {}
                model_id = meta.get('model')
                if not model_id:
                    px = fp.stem.split('_')
                    if len(px) >=2: model_id = px[-1]
                if not model_id: continue
                cur.execute("SELECT 1 FROM bi.models WHERE id=%s", (model_id,))
                if cur.fetchone() is None:
                    cur.execute(
                        """INSERT INTO bi.models (id,name,family,vendor,params,tags,owner,created_at,updated_at)
                        VALUES (%(id)s,%(name)s,%(family)s,%(vendor)s,%(params)s,%(tags)s,%(owner)s,%(created_at)s,%(updated_at)s)
                        ON CONFLICT (id) DO NOTHING""",
                        {
                            'id': model_id,
                            'name': model_id,
                            'family': None,
                            'vendor': None,
                            'params': json.dumps({}, ensure_ascii=False),
                            'tags': None,
                            'owner': None,
                            'created_at': None,
                            'updated_at': datetime.utcnow(),
                        },
                    )
                payload = {
                    'run_id': run_id,
                    'model_id': model_id,
                    'scenario_id': None,
                    'indicator_id': metric_id,
                    'value': float(value) if value is not None else None,
                    'ci': json.dumps(it.get('ci')) if it.get('ci') is not None else None,
                    'samples_used': it.get('samples_used'),
                    'started_at': started_at,
                    'env': json.dumps(meta, ensure_ascii=False),
                    'cost': None,
                }
                cur.execute(
                    """
                    INSERT INTO bi.runs_flat
                    (run_id,model_id,scenario_id,indicator_id,value,ci,samples_used,started_at,env,cost)
                    VALUES (%(run_id)s,%(model_id)s,%(scenario_id)s,%(indicator_id)s,%(value)s,%(ci)s,%(samples_used)s,%(started_at)s,%(env)s,%(cost)s)
                    ON CONFLICT (run_id, model_id, indicator_id) DO UPDATE SET
                      value=EXCLUDED.value, ci=EXCLUDED.ci, samples_used=EXCLUDED.samples_used, started_at=EXCLUDED.started_at,
                      env=EXCLUDED.env, cost=EXCLUDED.cost
                    """,
                    payload,
                )
                c+=1
    return c
