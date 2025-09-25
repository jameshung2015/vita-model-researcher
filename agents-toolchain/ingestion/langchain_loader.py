#!/usr/bin/env python3
"""
LangChain-backed loader/normalizer for HTML/JSON sources.

- If the URL returns JSON, parse and map common fields.
- If HTML, extract <title> and simple meta tags.
Returns a normalized dict: { provider, io_modalities, size_params, tags, raw }.
"""
from __future__ import annotations

import json
import re
import sys
from urllib.parse import urlparse

import requests

try:
    from langchain_core.runnables import RunnableLambda
except Exception:
    class RunnableLambda:  # minimal fallback
        def __init__(self, fn):
            self.fn = fn
        def invoke(self, x):
            return self.fn(x)


def _extract_html(text: str) -> dict:
    title = None
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if m:
        title = re.sub(r"\s+", " ", m.group(1)).strip()
    metas = {}
    for name in ["description", "keywords", "og:title", "og:description"]:
        pat = rf"<meta[^>]+(?:name|property)=[\"']{re.escape(name)}[\"'][^>]*content=[\"'](.*?)[\"'][^>]*>"
        mm = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if mm:
            metas[name] = re.sub(r"\s+", " ", mm.group(1)).strip()
    return {"title": title, "meta": metas}


def _guess_modalities(text: str) -> list[str]:
    t = text.lower()
    mods = []
    for key, mod in [("image", "image"), ("audio", "audio"), ("video", "video"), ("text", "text")]:
        if key in t:
            mods.append(mod)
    return sorted(set(mods)) or ["text"]


def normalize_document(url: str) -> dict:
    r = requests.get(url, timeout=20)
    content_type = r.headers.get('Content-Type', '')
    provider = urlparse(url).hostname or "unknown"
    result = {"provider": provider, "io_modalities": [], "size_params": None, "tags": []}

    if 'application/json' in content_type or (r.text.strip().startswith('{') or r.text.strip().startswith('[')):
        try:
            data = r.json()
        except Exception:
            data = None
        if isinstance(data, dict):
            # Heuristic mapping
            result["io_modalities"] = data.get('input_types') or data.get('modalities') or []
            size = data.get('size_params') or data.get('params')
            result["size_params"] = size
            result["tags"] = list({*(data.get('tags') or []), *([] if not isinstance(size, str) else [size])})
            result["raw"] = data
            return result
    # HTML fallback
    html = r.text
    extra = _extract_html(html)
    result["io_modalities"] = _guess_modalities(html)
    result["tags"] = [t for t in [extra.get('title'), extra['meta'].get('keywords')] if t]
    result["raw"] = {"title": extra.get('title'), "meta": extra.get('meta')}
    return result


chain = RunnableLambda(lambda x: normalize_document(x["url"]))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python agents-toolchain/ingestion/langchain_loader.py <url>")
        sys.exit(2)
    print(json.dumps(normalize_document(sys.argv[1]), ensure_ascii=False, indent=2))

