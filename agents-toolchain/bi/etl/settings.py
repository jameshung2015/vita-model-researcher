"""Shared settings for BI ETL.

Centralised environment + path helpers so other ETL modules/tests do not
recompute logic. Very small to avoid import side‑effects.
"""
from __future__ import annotations
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

PG_HOST = os.getenv('PG_HOST', 'postgres')
PG_PORT = os.getenv('PG_PORT', '5432')
PG_DB = os.getenv('PG_DB', 'vita_bi')
PG_USER = os.getenv('PG_USER', 'vita')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'vita_pwd')


def build_conninfo(host_override: str | None = None) -> str:
    host = host_override or PG_HOST or 'localhost'
    return (
        f"host={host} "
        f"port={PG_PORT} "
        f"dbname={PG_DB} "
        f"user={PG_USER} "
        f"password={PG_PASSWORD}"
    )
