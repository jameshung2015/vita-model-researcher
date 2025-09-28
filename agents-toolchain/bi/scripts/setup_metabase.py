#!/usr/bin/env python3
import json
import os
import time
import urllib.request as ur

MB_URL = os.environ.get('MB_URL', 'http://localhost:3000')
ADMIN_EMAIL = os.environ.get('MB_ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASS = os.environ.get('MB_ADMIN_PASS', 'P@ssw0rd123')

PG_DETAILS = {
    "engine": "postgres",
    "name": "Vita BI Warehouse",
    "details": {
        "host": os.environ.get('PG_HOST_MB', 'postgres'),
        "port": int(os.environ.get('PG_PORT', '5432')),
        "dbname": os.environ.get('PG_DB', 'vita_bi'),
        "user": os.environ.get('PG_USER', 'vita'),
        "password": os.environ.get('PG_PASSWORD', 'vita_pwd'),
        "ssl": False,
    },
}


def http_json(method, path, payload=None, session_id=None):
    url = f"{MB_URL}{path}"
    data = None if payload is None else json.dumps(payload).encode('utf-8')
    req = ur.Request(url, data=data, method=method)
    req.add_header('Content-Type', 'application/json')
    if session_id:
        req.add_header('X-Metabase-Session', session_id)
    try:
        with ur.urlopen(req, timeout=30) as resp:
            body = resp.read()
            if not body:
                return {}
            return json.loads(body.decode('utf-8'))
    except Exception as e:
        # attempt to read error body if available
        if hasattr(e, 'read'):
            try:
                err_body = e.read().decode('utf-8')
                print(f"HTTP error {getattr(e,'code',None)} {path}: {err_body}")
            except Exception:
                pass
        raise


def wait_ready():
    for _ in range(60):
        try:
            j = http_json('GET', '/api/health')
            if j.get('status') == 'ok' or j.get('ok') is True:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError('Metabase not ready')


def ensure_setup():
    props = http_json('GET', '/api/session/properties')
    token = props.get('setup-token') or props.get('setup_token')
    if token:
        try:
            http_json('POST', '/api/setup', {
                'token': token,
                'user': {
                    'first_name': 'Admin', 'last_name': 'User', 'email': ADMIN_EMAIL,
                    'password': ADMIN_PASS,
                },
                # site_name must be under prefs, not user
                'prefs': {'allow_tracking': False, 'site_name': 'Vita BI'},
                'database': PG_DETAILS,
            })
        except Exception as e:  # already set up (403) -> ignore
            if '403' not in str(e):
                raise


def login():
    j = http_json('POST', '/api/session', {'username': ADMIN_EMAIL, 'password': ADMIN_PASS})
    sid = j.get('id')
    if not sid:
        raise RuntimeError('Login failed')
    return sid


def get_db_id(session_id):
    j = http_json('GET', '/api/database', session_id=session_id)
    for db in j.get('data', []):
        if db.get('engine') == 'postgres' and db.get('name', '').startswith('Vita BI'):
            return db.get('id')
    # fallback: create
    j = http_json('POST', '/api/database', PG_DETAILS, session_id=session_id)
    return j.get('id')


def create_card(session_id, db_id, name, sql):
    payload = {
        'name': name,
        'dataset_query': {
            'type': 'native',
            'native': {'query': sql, 'template-tags': {}},
            'database': db_id,
        },
        'display': 'table',
        'visualization_settings': {},
    }
    j = http_json('POST', '/api/card', payload, session_id=session_id)
    return j.get('id')


def create_dashboard_with_cards(session_id, card_ids):
    d = http_json('POST', '/api/dashboard', {'name': 'Vita BI QA Demo'}, session_id=session_id)
    dash_id = d.get('id')
    if not dash_id:
        # attempt to find existing by name
        dashboards = http_json('GET', '/api/dashboard', session_id=session_id)
        if isinstance(dashboards, list):
            for entry in dashboards:
                if entry.get('name') == 'Vita BI QA Demo':
                    dash_id = entry.get('id')
                    print(f"Re-using existing dashboard id={dash_id}")
                    break
    if not dash_id:
        raise RuntimeError('Could not create or locate dashboard')
    # Try canonical endpoints first (may 404 in this version)
    failed = []
    for cid in card_ids:
        payload = {'cardId': cid, 'dashboard_id': dash_id, 'parameter_mappings': [], 'visualization_settings': {}}
        try:
            http_json('POST', f'/api/dashboard/{dash_id}/cards', payload, session_id=session_id)
            continue
        except Exception:
            try:
                http_json('POST', f'/api/dashboards/{dash_id}/cards', payload, session_id=session_id)
                continue
            except Exception:
                failed.append(cid)

    if failed:
        # Fallback: fetch dashboard JSON and PUT with ordered_cards array
        try:
            dash = http_json('GET', f'/api/dashboard/{dash_id}', session_id=session_id)
            existing_cards = []
            ordered = dash.get('ordered_cards') or []
            for oc in ordered:
                card_obj = oc.get('card') or {}
                cid_existing = card_obj.get('id') or oc.get('card_id') or oc.get('cardId')
                if cid_existing:
                    existing_cards.append(cid_existing)
            # build new ordered_cards list preserving existing
            new_ordered = []
            # keep originals
            for oc in ordered:
                # reduce size if missing expected layout fields
                if 'sizeX' not in oc:
                    oc['sizeX'] = oc.get('size_x', 8) or 8
                if 'sizeY' not in oc:
                    oc['sizeY'] = oc.get('size_y', 4) or 4
                if 'col' not in oc:
                    oc['col'] = 0
                if 'row' not in oc:
                    oc['row'] = 0
                new_ordered.append(oc)
            # append failed card ids with a grid layout
            base_index = len(new_ordered)
            for i, cid in enumerate(failed):
                pos = base_index + i
                new_ordered.append({
                    'card_id': cid,
                    'sizeX': 8,
                    'sizeY': 4,
                    'col': 0 if (pos % 2 == 0) else 8,
                    'row': (pos // 2) * 4,
                    'parameter_mappings': [],
                    'visualization_settings': {},
                })
            update_payload = {
                'name': dash.get('name', 'Vita BI QA Demo'),
                'description': dash.get('description'),
                'parameters': dash.get('parameters', []),
                'collection_id': dash.get('collection_id'),
                'ordered_cards': new_ordered,
            }
            http_json('PUT', f'/api/dashboard/{dash_id}', update_payload, session_id=session_id)
            print(f"Attached cards via PUT ordered_cards (added {len(failed)}).")
        except Exception as e:
            print(f"Fallback PUT dashboard update failed: {e}")
    return dash_id


def main():
    wait_ready()
    ensure_setup()
    sid = login()
    db_id = get_db_id(sid)
    sqls = [
        ("QA Events Count", "SELECT COUNT(*) AS qa_events FROM bi.qa_log;"),
        ("QA Tags Top10", "SELECT tag, COUNT(*) AS cnt FROM ( SELECT UNNEST(tags) AS tag FROM bi.qa_log WHERE tags IS NOT NULL ) t GROUP BY tag ORDER BY cnt DESC LIMIT 10;"),
        ("QA Timeline (Daily)", "SELECT to_timestamp(ts)::date AS day, COUNT(*) AS cnt FROM bi.qa_log GROUP BY 1 ORDER BY 1;"),
        ("Latest Indicators TopN", "WITH latest AS ( SELECT DISTINCT ON (model_id, indicator_id) model_id, indicator_id, value, started_at FROM bi.runs_flat ORDER BY model_id, indicator_id, started_at DESC ) SELECT m.id AS model, l.indicator_id, l.value, l.started_at FROM latest l JOIN bi.models m ON m.id = l.model_id ORDER BY l.value DESC LIMIT 50;")
    ]
    card_ids = [create_card(sid, db_id, n, s) for n, s in sqls]
    dash_id = create_dashboard_with_cards(sid, card_ids)
    print(f"Dashboard created: {MB_URL}/dashboard/{dash_id}")


if __name__ == '__main__':
    main()
