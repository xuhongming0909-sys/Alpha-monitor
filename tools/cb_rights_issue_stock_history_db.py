#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""可转债抢权配售功能专用的正股历史数据库。"""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db_paths import ensure_dir, shared_db_path

DB_PATH = shared_db_path("cb_rights_issue_stock_history.db")


def now_iso() -> str:
    return datetime.now().isoformat()


def connect() -> sqlite3.Connection:
    ensure_dir(DB_PATH.parent)
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 60000;")
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;

            CREATE TABLE IF NOT EXISTS stock_price_history (
                symbol TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                close_hfq REAL NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (symbol, trade_date)
            );

            CREATE INDEX IF NOT EXISTS idx_cb_rights_issue_hist_symbol_date
                ON stock_price_history(symbol, trade_date);

            CREATE TABLE IF NOT EXISTS stock_price_sync_state (
                symbol TEXT NOT NULL PRIMARY KEY,
                last_trade_date TEXT,
                source TEXT,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS stock_symbol_universe (
                symbol TEXT NOT NULL PRIMARY KEY,
                status TEXT NOT NULL,
                note TEXT,
                updated_at TEXT NOT NULL
            );
            """
        )


def upsert_price_rows(symbol: str, rows: Iterable[Dict], source: str) -> int:
    normalized_symbol = str(symbol or "").strip()
    if not normalized_symbol:
        return 0

    prepared: List[Dict[str, float | str]] = []
    for row in rows:
        trade_date = str(row.get("date") or "").strip()
        close_hfq = row.get("close")
        try:
            close_value = float(close_hfq)
        except (TypeError, ValueError):
            continue
        if not trade_date or close_value <= 0:
            continue
        prepared.append({"date": trade_date, "close": close_value})

    if not prepared:
        return 0

    timestamp = now_iso()
    with connect() as conn:
        for item in prepared:
            conn.execute(
                """
                INSERT INTO stock_price_history(symbol, trade_date, close_hfq, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(symbol, trade_date) DO UPDATE SET
                    close_hfq = excluded.close_hfq,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    normalized_symbol,
                    item["date"],
                    float(item["close"]),
                    source,
                    timestamp,
                    timestamp,
                ),
            )

        conn.execute(
            """
            INSERT INTO stock_price_sync_state(symbol, last_trade_date, source, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                last_trade_date = excluded.last_trade_date,
                source = excluded.source,
                updated_at = excluded.updated_at
            """,
            (normalized_symbol, prepared[-1]["date"], source, timestamp),
        )

    return len(prepared)


def load_recent_closes(symbol: str, min_rows: int = 61) -> List[float]:
    normalized_symbol = str(symbol or "").strip()
    if not normalized_symbol:
        return []

    with connect() as conn:
        rows = conn.execute(
            """
            SELECT close_hfq
            FROM stock_price_history
            WHERE symbol = ?
            ORDER BY trade_date DESC
            LIMIT ?
            """,
            (normalized_symbol, max(1, int(min_rows))),
        ).fetchall()

    values = [float(row["close_hfq"]) for row in rows]
    values.reverse()
    return values


def get_last_trade_date(symbol: str) -> Optional[str]:
    normalized_symbol = str(symbol or "").strip()
    if not normalized_symbol:
        return None

    with connect() as conn:
        row = conn.execute(
            "SELECT last_trade_date FROM stock_price_sync_state WHERE symbol = ?",
            (normalized_symbol,),
        ).fetchone()
    return str(row["last_trade_date"]) if row and row["last_trade_date"] else None


def upsert_symbol_universe(symbol: str, status: str = "active", note: str = "") -> None:
    normalized_symbol = str(symbol or "").strip()
    if not normalized_symbol:
        return

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO stock_symbol_universe(symbol, status, note, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(symbol) DO UPDATE SET
                status = excluded.status,
                note = excluded.note,
                updated_at = excluded.updated_at
            """,
            (normalized_symbol, str(status or "active"), str(note or ""), now_iso()),
        )


def purge_symbols_not_in_universe(active_symbols: Sequence[str]) -> Dict[str, int]:
    normalized = sorted({str(symbol or "").strip() for symbol in active_symbols if str(symbol or "").strip()})
    if not normalized:
        return {
            "removedSymbols": 0,
            "removedPriceRows": 0,
            "removedSyncRows": 0,
            "removedUniverseRows": 0,
        }

    placeholders = ",".join("?" for _ in normalized)
    with connect() as conn:
        removed_symbols = conn.execute(
            f"""
            SELECT COUNT(1) FROM (
                SELECT symbol
                FROM stock_price_history
                WHERE symbol NOT IN ({placeholders})
                GROUP BY symbol
            )
            """,
            tuple(normalized),
        ).fetchone()[0]

        removed_price_rows = conn.execute(
            f"DELETE FROM stock_price_history WHERE symbol NOT IN ({placeholders})",
            tuple(normalized),
        ).rowcount

        removed_sync_rows = conn.execute(
            f"DELETE FROM stock_price_sync_state WHERE symbol NOT IN ({placeholders})",
            tuple(normalized),
        ).rowcount

        removed_universe_rows = conn.execute(
            f"DELETE FROM stock_symbol_universe WHERE symbol NOT IN ({placeholders})",
            tuple(normalized),
        ).rowcount

    return {
        "removedSymbols": int(removed_symbols or 0),
        "removedPriceRows": int(removed_price_rows or 0),
        "removedSyncRows": int(removed_sync_rows or 0),
        "removedUniverseRows": int(removed_universe_rows or 0),
    }
