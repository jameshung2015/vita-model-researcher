#!/usr/bin/env python3
import os
import subprocess
import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Minimal LangChain usage: Runnable chain for intent classification
try:
    from langchain_core.runnables import RunnableLambda
except Exception:  # fallback: allow running without langchain for basic echo
    class RunnableLambda:
        def __init__(self, fn):
            self.fn = fn
        def invoke(self, x):
            return self.fn(x)

# Optional chains and loaders
try:
    from agents_toolchain.orchestration.chains.taxonomy_assistant import chain as taxonomy_chain  # type: ignore
except Exception:
    # fallback to local relative import if package import fails
    try:
        from .chains.taxonomy_assistant import chain as taxonomy_chain  # type: ignore
    except Exception:
        taxonomy_chain = RunnableLambda(lambda x: {"intent": "chat", "hint": "taxonomy chain unavailable"})

try:
    # prefer module import style usable inside container
    from agents_toolchain.ingestion.langchain_loader import chain as loader_chain  # type: ignore
except Exception:
    try:
        from ..ingestion.langchain_loader import chain as loader_chain  # type: ignore
    except Exception:
        loader_chain = RunnableLambda(lambda x: {"error": "loader not available"})


N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'http://n8n:5678/webhook/chat_ingest')
MONGO_URI = os.getenv('MONGO_URI')

mongo_client = None
try:
    if MONGO_URI:
        from pymongo import MongoClient
        mongo_client = MongoClient(MONGO_URI)
except Exception:
    mongo_client = None

app = FastAPI(title="Agents Chatbot Router", version="0.1.0")


class ChatRequest(BaseModel):
    session_id: str
    user_query: str
    route: str  # "n8n" | "langchain"
    payload: dict | None = None


def classify_intent(text: str) -> dict:
    t = (text or '').lower()
    if any(k in t for k in ["taxonomy", "分类", "快照", "snapshot"]):
        return {"intent": "taxonomy_help", "action": "build_or_diff"}
    if any(k in t for k in ["ingest", "采集", "抓取", "fetch"]):
        return {"intent": "ingest_request", "action": "enqueue_sources"}
    return {"intent": "chat", "action": "echo"}


lc_chain = RunnableLambda(lambda x: {
    "intent": classify_intent(x.get("user_query", "")).get("intent"),
    "analysis": "runnable_result",
    "suggestion": (
        "Run build_taxonomy.py to create a snapshot and diff_taxonomy.py to compare"
        if "taxonomy" in x.get("user_query", "").lower() else
        "Use n8n route to enqueue sources for ingestion"
    )
})


@app.post("/chat")
def chat(req: ChatRequest):
    if req.route not in ("n8n", "langchain"):
        raise HTTPException(status_code=400, detail="route must be 'n8n' or 'langchain'")

    if req.route == "n8n":
        try:
            payload = req.payload or {"url": req.user_query}
            r = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=15)
            return {
                "route": "n8n",
                "status_code": r.status_code,
                "ok": r.ok,
                "n8n_response": safe_json(r)
            }
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"n8n error: {e}")

    # langchain route
    try:
        payload = req.payload or {}
        task = (payload.get("task") or "").lower()
        # 1) Normalize a URL via loader
        if task == "normalize_url":
            url = payload.get("url") or req.user_query
            if not url:
                raise HTTPException(status_code=400, detail="normalize_url requires 'url' in payload or user_query")
            res = loader_chain.invoke({"url": url})
            return {"route": "langchain", "task": task, "normalized": res}
        # 1b) List cached sources from Mongo
        if task == "list_sources":
            if not mongo_client:
                raise HTTPException(status_code=500, detail="Mongo client not available; set MONGO_URI")
            limit = int(payload.get("limit", 10))
            search = payload.get("search")
            q = {}
            if search:
                q = {"url": {"$regex": search, "$options": "i"}}
            cur = mongo_client[os.getenv('DB_NAME', 'agents_kb')]['sources_cache'].find(q).sort('fetched_at', -1).limit(limit)
            items = []
            for doc in cur:
                doc['_id'] = str(doc.get('_id'))
                # shrink snippet
                if 'content_snippet' in doc and isinstance(doc['content_snippet'], str):
                    doc['content_snippet'] = doc['content_snippet'][:256]
                items.append(doc)
            return {"route": "langchain", "task": task, "items": items}
        # 2) Build taxonomy snapshot
        if task == "build_taxonomy":
            out = run_script(["python", "agents-toolchain/governance/build_taxonomy.py"]) 
            return {"route": "langchain", "task": task, "result": out}
        # 3) Diff taxonomy snapshots
        if task == "diff_taxonomy":
            old = payload.get("old")
            new = payload.get("new")
            if not (old and new):
                raise HTTPException(status_code=400, detail="diff_taxonomy requires 'old' and 'new' paths in payload")
            out = run_script(["python", "agents-toolchain/governance/diff_taxonomy.py", old, new, "--out", "reports"]) 
            return {"route": "langchain", "task": task, "result": out}
        # 4) If user_query looks like a URL, auto-normalize
        if not task and (req.user_query.startswith('http://') or req.user_query.startswith('https://')):
            res = loader_chain.invoke({"url": req.user_query})
            return {"route": "langchain", "task": "normalize_url", "normalized": res}
        # Fallback assistant chain
        res = taxonomy_chain.invoke(req.dict())
        return {"route": "langchain", "result": res}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"langchain error: {e}")


def safe_json(r):
    try:
        return r.json()
    except Exception:
        return {"text": r.text[:1024]}


@app.get("/health")
def health():
    return JSONResponse({"ok": True})


@app.get("/")
def index():
    html = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Agents Chatbot Router</title>
    <style>
      body { font-family: ui-sans-serif, system-ui, Arial; margin: 24px; }
      textarea, input, select { width: 100%; padding: 8px; margin: 6px 0; }
      pre { background: #f6f8fa; padding: 12px; overflow: auto; }
      .row { display: flex; gap: 12px; }
      .row > * { flex: 1; }
      button { padding: 8px 12px; }
      small { color: #666; }
    </style>
  </head>
  <body>
    <h2>Agents Chatbot Router</h2>
    <div class="row">
      <div>
        <label>Session ID</label>
        <input id="session" value="s1" />
      </div>
      <div>
        <label>Route</label>
        <select id="route">
          <option value="langchain">langchain</option>
          <option value="n8n">n8n</option>
        </select>
      </div>
    </div>

    <label>User Query</label>
    <textarea id="query" rows="2" placeholder="For n8n, put a URL here (e.g., https://example.com)"></textarea>

    <details>
      <summary>Payload (JSON, optional for langchain tasks)</summary>
      <textarea id="payload" rows="6" placeholder='{"task":"list_sources","limit":5}'></textarea>
    </details>

    <button onclick="send()">Send</button>
    <small>Examples: langchain payload {"task":"list_sources","limit":5} or {"task":"normalize_url","url":"https://example.com"}</small>

    <h3>Response</h3>
    <pre id="out"></pre>

    <script>
      async function send(){
        const body = {
          session_id: document.getElementById('session').value || 's1',
          user_query: document.getElementById('query').value || '',
          route: document.getElementById('route').value,
        };
        const ptxt = document.getElementById('payload').value.trim();
        if (ptxt) {
          try { body.payload = JSON.parse(ptxt); } catch(e) { alert('Invalid JSON payload'); return; }
        }
        const res = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        const text = await res.text();
        try { document.getElementById('out').textContent = JSON.stringify(JSON.parse(text), null, 2); }
        catch { document.getElementById('out').textContent = text; }
      }
    </script>
  </body>
 </html>
    """
    return HTMLResponse(html)

def run_script(cmd: list[str]) -> dict:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {"returncode": p.returncode, "stdout": p.stdout[-2048:], "stderr": p.stderr[-2048:]}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("CHATBOT_PORT", "8080")))
