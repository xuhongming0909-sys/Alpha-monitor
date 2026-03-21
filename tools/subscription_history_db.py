#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SQLite store for IPO and convertible-bond subscription history (single-table design)."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db_paths import ensure_dir, shared_db_path

DB_PATH = shared_db_path("subscription_history.db")
SUPPORTED_KINDS = {"ipo", "bond"}


def now_iso() -> str:
    return datetime.now().isoformat()


def connect() -> sqlite3.Connection:
    ensure_dir(DB_PATH.parent)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_kind(kind: str) -> str:
    normalized = str(kind or "").strip().lower()
    if normalized in {"bond", "bonds", "convertible_bond"}:
        return "bond"
    if normalized == "ipo":
        return "ipo"
    raise ValueError(f"unsupported kind: {kind}")


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ? LIMIT 1",
        (table_name,),
    ).fetchone()
    return bool(row)


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;

            CREATE TABLE IF NOT EXISTS subscription_history (
                kind TEXT NOT NULL,
                code TEXT NOT NULL,
                subscribe_date TEXT NOT NULL,
                name TEXT,
                payload_json TEXT NOT NULL,
                source TEXT,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (kind, code, subscribe_date)
            );

            CREATE INDEX IF NOT EXISTS idx_subscription_history_kind_date
                ON subscription_history(kind, subscribe_date DESC, updated_at DESC);

            CREATE TABLE IF NOT EXISTS subscription_sync_log (
                sync_date TEXT NOT NULL,
                kind TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                success INTEGER NOT NULL,
                source TEXT,
                error TEXT,
                sync_time TEXT NOT NULL,
                PRIMARY KEY (sync_date, kind)
            );
            """
        )
def upsert_rows(kind: str, rows: Iterable[Dict], source: str) -> int:
    normalized_kind = normalize_kind(kind)
    ts = now_iso()
    count = 0

    with connect() as conn:
        for row in rows:
            code = str(row.get("code") or "").strip()
            subscribe_date = str(row.get("subscribeDate") or "").strip()
            if not code or not subscribe_date:
                continue

            conn.execute(
                """
                INSERT INTO subscription_history(
                    kind, code, subscribe_date, name, payload_json, source,
                    first_seen, last_seen, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(kind, code, subscribe_date) DO UPDATE SET
                    name = excluded.name,
                    payload_json = excluded.payload_json,
                    source = excluded.source,
                    last_seen = excluded.last_seen,
                    updated_at = excluded.updated_at
                """,
                (
                    normalized_kind,
                    code,
                    subscribe_date,
                    str(row.get("name") or "").strip(),
                    json.dumps(row, ensure_ascii=False),
                    source,
                    ts,
                    ts,
                    ts,
                ),
            )
            count += 1

    return count


def load_rows(kind: str, limit: int | None = None) -> List[Dict]:
    normalized_kind = normalize_kind(kind)
    sql = """
        SELECT payload_json
        FROM subscription_history
        WHERE kind = ?
        ORDER BY subscribe_date DESC, updated_at DESC
    """
    params: list = [normalized_kind]
    if isinstance(limit, int) and limit > 0:
        sql += " LIMIT ?"
        params.append(limit)

    with connect() as conn:
        rows = conn.execute(sql, tuple(params)).fetchall()

    result: List[Dict] = []
    for row in rows:
        payload = row["payload_json"]
        try:
            item = json.loads(payload)
        except Exception:
            continue
        if isinstance(item, dict):
            result.append(item)
    return result


def record_sync(kind: str, total_rows: int, success: bool, source: str, error: str | None = None) -> None:
    normalized_kind = normalize_kind(kind)
    sync_date = datetime.now().strftime("%Y-%m-%d")
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO subscription_sync_log(sync_date, kind, total_rows, success, source, error, sync_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sync_date, kind) DO UPDATE SET
                total_rows = excluded.total_rows,
                success = excluded.success,
                source = excluded.source,
                error = excluded.error,
                sync_time = excluded.sync_time
            """,
            (
                sync_date,
                normalized_kind,
                int(total_rows or 0),
                1 if success else 0,
                source,
                str(error or "") or None,
                now_iso(),
            ),
        )

