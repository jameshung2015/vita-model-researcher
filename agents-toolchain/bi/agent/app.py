import os
import re
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy import text
from db import engine
from prompt import SYSTEM_PROMPT
from fewshots import FEW_SHOT_EXAMPLES

try:
    from openai import OpenAI
except ImportError:  # runtime safety if not installed
    OpenAI = None  # type: ignore

import json
import requests

load_dotenv()


LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")  # if /v1 not provided fallback to /api
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v3.1:671b-cloud")
SQL_LOG_ENABLED = os.getenv('SQL_LOG_ENABLED', '1') != '0'
SQL_LOG_RAW = os.getenv('SQL_LOG_RAW', '0') == '1'

def _ensure_sql_log_table():
    from sqlalchemy import text as _t
    with engine.begin() as conn:
        conn.execute(_t("""
        CREATE TABLE IF NOT EXISTS bi.sql_log (
          id BIGSERIAL PRIMARY KEY,
          ts TIMESTAMPTZ DEFAULT now(),
          question TEXT,
          sql TEXT,
          rows_returned INT,
          llm_model TEXT,
          raw_output TEXT,
          warning TEXT
        );
        """))
if SQL_LOG_ENABLED:
    try:
        _ensure_sql_log_table()
    except Exception as e:
        print(f"[warn] cannot ensure bi.sql_log: {e}")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama-placeholder-key")  # Ollama 只要非空
LLM_MODE = os.getenv("LLM_MODE", "auto")  # auto|openai|ollama


def _introspect_schema() -> str:
    """Fetch lightweight schema info to help model produce valid columns."""
    cols_sql = []
    with engine.connect() as conn:
        q = text("""
            SELECT table_schema, table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema='bi' AND table_name in ('models','scenarios','runs_flat','mv_latest_indicator')
            ORDER BY table_name, ordinal_position
        """)
        rows = conn.execute(q).fetchall()
    for r in rows:
        cols_sql.append(f"{r.table_name}.{r.column_name}:{r.data_type}")
    return "Schema Columns: " + ", ".join(cols_sql)


def _call_openai(messages: List[dict]) -> str:
    if OpenAI is None:
        raise RuntimeError("openai library not installed")
    client = OpenAI(base_url=LLM_BASE_URL.rstrip('/'), api_key=LLM_API_KEY)
    resp = client.chat.completions.create(model=LLM_MODEL, messages=messages, temperature=0.0, max_tokens=400)
    return resp.choices[0].message.content or ""


def _call_ollama(messages: List[dict]) -> str:
    # Convert to standard Ollama chat format
    base = LLM_BASE_URL.rstrip('/')
    # If user left default with /v1, strip it for native /api
    if base.endswith('/v1'):
        base = base[:-3]
    url = base + '/api/chat'
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.0}
    }
    r = requests.post(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"}, timeout=120)
    r.raise_for_status()
    j = r.json()
    # Ollama returns content under message.content
    msg = (j.get('message') or {}).get('content') or ''
    return msg


def _call_llm(messages: List[dict]) -> str:
    mode_order: List[str]
    if LLM_MODE == 'openai':
        mode_order = ['openai']
    elif LLM_MODE == 'ollama':
        mode_order = ['ollama']
    else:
        # auto: try openai-style first then native ollama
        mode_order = ['openai', 'ollama']
    errors = []
    for mode in mode_order:
        try:
            if mode == 'openai':
                return _call_openai(messages)
            else:
                return _call_ollama(messages)
        except Exception as e:
            errors.append(f"{mode}: {e}")
    raise RuntimeError("; ".join(errors))


SQL_BLOCK_RE = re.compile(r"```sql\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def llm_generate_sql(question: str) -> str:
    schema_hint = _introspect_schema()
    # Build messages: system + few-shot (user, assistant) pairs + real question
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n" + schema_hint}
    ]
    for q, sql in FEW_SHOT_EXAMPLES:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": sql})
    messages.append({"role": "user", "content": question})
    try:
        raw = _call_llm(messages)
    except Exception as e:
        # fallback to deterministic safe query if LLM fails
        print(f"[LLM Fallback] {e}")
        return (
            "SELECT model_id, indicator_id, AVG(value) AS avg_value "
            "FROM bi.runs_flat GROUP BY 1,2 ORDER BY 3 DESC LIMIT 50;"
        )
    m = SQL_BLOCK_RE.search(raw)
    sql = (m.group(1) if m else raw).strip()
    # Basic safety filters
    upper_sql = sql.upper().strip()
    if not upper_sql.startswith("SELECT"):
        raise HTTPException(status_code=400, detail="Generated SQL rejected: must start with SELECT")
    # enforce table whitelist: every FROM / JOIN target must start with bi.
    table_refs = re.findall(r"\bFROM\s+([a-zA-Z0-9_\.]+)|\bJOIN\s+([a-zA-Z0-9_\.]+)", sql, re.IGNORECASE)
    for a, b in table_refs:
        t = a or b
        if t and not t.startswith('bi.'):
            raise HTTPException(status_code=400, detail=f"Generated SQL rejected (table {t} not allowed)")
    if "LIMIT" not in upper_sql:
        sql += " LIMIT 200"
    return sql


class QARequest(BaseModel):
    question: str
    debug: bool | None = False


app = FastAPI()


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/qa")
def qa(req: QARequest):
    raw_output = None
    warning = None
    try:
        sql = llm_generate_sql(req.question)
    except Exception as e:
        warning = f"generation_error:{e}"
        sql = ("SELECT model_id, indicator_id, AVG(value) AS avg_value FROM bi.runs_flat "
               "GROUP BY 1,2 ORDER BY 3 DESC LIMIT 50;")
    with engine.connect() as conn:
        try:
            res = conn.execute(text(sql))
            rows = [dict(r._mapping) for r in res]
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"SQL execution error: {e}")
    if SQL_LOG_ENABLED:
        try:
            with engine.begin() as lg:
                lg.execute(text("""
                    INSERT INTO bi.sql_log(question, sql, rows_returned, llm_model, raw_output, warning)
                    VALUES (:q,:s,:n,:m,:r,:w)
                """), {
                    'q': req.question,
                    's': sql,
                    'n': len(rows),
                    'm': LLM_MODEL,
                    'r': raw_output if (SQL_LOG_RAW and raw_output) else None,
                    'w': warning,
                })
        except Exception as e:
            print(f"[warn] failed to log sql: {e}")
    return {"sql": sql, "rows": rows, "llm_model": LLM_MODEL, "debug": req.debug, "warning": warning}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("AGENT_PORT", 8088)))
