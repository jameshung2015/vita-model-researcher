from __future__ import annotations

try:
    from langchain_core.runnables import RunnableLambda
except Exception:
    class RunnableLambda:  # type: ignore
        def __init__(self, fn):
            self.fn = fn
        def invoke(self, x):
            return self.fn(x)


def _assist(payload: dict):
    text = (payload.get("user_query") or "").lower()
    if any(k in text for k in ["build taxonomy", "分类快照", "snapshot"]):
        return {
            "intent": "taxonomy_help",
            "next": [
                "python agents-toolchain/governance/build_taxonomy.py",
                "python agents-toolchain/governance/diff_taxonomy.py <old> <new> --out reports"
            ]
        }
    return {"intent": "chat", "hint": "Use route=n8n to enqueue ingestion."}


chain = RunnableLambda(_assist)

