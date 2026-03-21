#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SQLite store for convertible-bond underlying stock HFQ daily prices."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db_paths import ensure_dir, shared_db_path

DB_PATH = shared_db_path("stock_price_history.db")


def now_iso() -> str:
    return datetime.now().isoformat()


def cutoff_date(days: int = 800) -> str:
    return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")


def connect() -> sqlite3.Connection:
    ensure_dir(DB_PATH.parent)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

            CREATE INDEX IF NOT EXISTS idx_stock_price_symbol_date
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

    prepared: List[Dict] = []
    for row in rows:
        trade_date = str(row.get("date") or "").strip()
        close_hfq = row.get("close")
        if not trade_date or close_hfq is None:
            continue
        try:
            close_hfq = float(close_hfq)
        except (TypeError, ValueError):
            continue
        if close_hfq <= 0:
            continue
        prepared.append({"date": trade_date, "close": close_hfq})

    if not prepared:
        return 0

    ts = now_iso()
    last_trade_date = prepared[-1]["date"]
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
                (normalized_symbol, item["date"], float(item["close"]), source, ts, ts),
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
            (normalized_symbol, last_trade_date, source, ts),
        )
    return len(prepared)


def load_recent_closes(symbol: str, min_rows: int = 121) -> List[float]:
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
    ts = now_iso()
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
            (normalized_symbol, str(status or "active"), str(note or ""), ts),
        )


def prune_to_recent_rows(max_rows_per_symbol: int = 120) -> int:
    max_rows = max(1, int(max_rows_per_symbol))
    with connect() as conn:
        cursor = conn.execute(
            """
            DELETE FROM stock_price_history
            WHERE rowid IN (
                SELECT rowid FROM (
                    SELECT
                        rowid,
                        ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY trade_date DESC) AS rn
                    FROM stock_price_history
                ) t
                WHERE t.rn > ?
            )
            """,
            (max_rows,),
        )
        conn.execute(
            """
            DELETE FROM stock_price_sync_state
            WHERE NOT EXISTS (
                SELECT 1 FROM stock_price_history h WHERE h.symbol = stock_price_sync_state.symbol
            )
            """
        )
    return int(cursor.rowcount or 0)


def purge_symbols_not_in_universe(active_symbols: Sequence[str]) -> Dict[str, int]:
    normalized = sorted({str(symbol or "").strip() for symbol in active_symbols if str(symbol or "").strip()})
    if not normalized:
        return {"removedSymbols": 0, "removedPriceRows": 0, "removedSyncRows": 0, "removedUniverseRows": 0}

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

