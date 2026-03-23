#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""SQLite store for premium history and precomputed summaries."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db_paths import ensure_dir, shared_db_path

DB_PATH = shared_db_path("premium_history.db")


def now_iso() -> str:
    return datetime.now().isoformat()


def cutoff_date(days: int = 365 * 5) -> str:
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

            CREATE TABLE IF NOT EXISTS premium_history (
                type TEXT NOT NULL,
                a_code TEXT NOT NULL,
                pair_code TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                a_price REAL NOT NULL,
                pair_price REAL NOT NULL,
                pair_price_cny REAL NOT NULL,
                fx_rate REAL NOT NULL,
                premium REAL NOT NULL,
                currency TEXT NOT NULL,
                pair_market TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (type, a_code, trade_date)
            );

            CREATE INDEX IF NOT EXISTS idx_premium_type_code_date
                ON premium_history(type, a_code, trade_date);

            CREATE TABLE IF NOT EXISTS fx_history (
                currency TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                rate REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (currency, trade_date)
            );

            CREATE INDEX IF NOT EXISTS idx_fx_currency_date
                ON fx_history(currency, trade_date);

            CREATE TABLE IF NOT EXISTS premium_summary (
                type TEXT NOT NULL,
                a_code TEXT NOT NULL,
                pair_code TEXT NOT NULL,
                min_premium REAL NOT NULL,
                max_premium REAL NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                sample_count INTEGER NOT NULL,
                min_premium_3y REAL,
                max_premium_3y REAL,
                start_date_3y TEXT,
                end_date_3y TEXT,
                sample_count_3y INTEGER,
                a_return_5y REAL,
                pair_return_5y REAL,
                return_start_date TEXT,
                return_end_date TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (type, a_code)
            );

            CREATE INDEX IF NOT EXISTS idx_premium_summary_type
                ON premium_summary(type, a_code);
            """
        )
        # Backward-compatible migrations for old DB schema.
        migration_columns = {
            "min_premium_3y": "REAL",
            "max_premium_3y": "REAL",
            "start_date_3y": "TEXT",
            "end_date_3y": "TEXT",
            "sample_count_3y": "INTEGER",
            "a_return_5y": "REAL",
            "pair_return_5y": "REAL",
            "return_start_date": "TEXT",
            "return_end_date": "TEXT",
        }
        existing_columns = {
            str(row["name"])
            for row in conn.execute("PRAGMA table_info(premium_summary)").fetchall()
        }
        for column, column_type in migration_columns.items():
            if column in existing_columns:
                continue
            conn.execute(f"ALTER TABLE premium_summary ADD COLUMN {column} {column_type}")


def prune_old_rows(days: int = 365 * 5) -> None:
    threshold = cutoff_date(days)
    with connect() as conn:
        conn.execute("DELETE FROM premium_history WHERE trade_date < ?", (threshold,))
        conn.execute("DELETE FROM fx_history WHERE trade_date < ?", (threshold,))
        conn.execute(
            """
            DELETE FROM premium_summary
            WHERE NOT EXISTS (
                SELECT 1
                FROM premium_history h
                WHERE h.type = premium_summary.type AND h.a_code = premium_summary.a_code
            )
            """
        )


def upsert_fx_rows(currency: str, rows: List[Dict]) -> int:
    if not rows:
        return 0

    ts = now_iso()
    inserted = 0
    with connect() as conn:
        for row in rows:
            date = str(row.get("date") or "").strip()
            rate = row.get("rate")
            if not date or rate is None:
                continue
            conn.execute(
                """
                INSERT INTO fx_history(currency, trade_date, rate, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(currency, trade_date) DO UPDATE SET
                    rate = excluded.rate,
                    updated_at = excluded.updated_at
                """,
                (currency, date, float(rate), ts, ts),
            )
            inserted += 1
    return inserted


def load_fx_chain(currency: str, start_date: str) -> Dict[str, float]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT trade_date, rate
            FROM fx_history
            WHERE currency = ? AND trade_date >= ?
            ORDER BY trade_date ASC
            """,
            (currency, start_date),
        ).fetchall()
    return {str(row["trade_date"]): float(row["rate"]) for row in rows}


def get_last_trade_date(stock_type: str, a_code: str) -> str | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT MAX(trade_date) AS max_date
            FROM premium_history
            WHERE type = ? AND a_code = ?
            """,
            (stock_type, a_code),
        ).fetchone()
    if not row:
        return None
    return row["max_date"]


def delete_premium_history(stock_type: str, a_code: str) -> int:
    with connect() as conn:
        cursor = conn.execute(
            "DELETE FROM premium_history WHERE type = ? AND a_code = ?",
            (stock_type, a_code),
        )
        return int(cursor.rowcount or 0)


def upsert_premium_rows(rows: List[Dict]) -> int:
    if not rows:
        return 0

    ts = now_iso()
    count = 0
    touched_keys = set()
    with connect() as conn:
        for item in rows:
            conn.execute(
                """
                INSERT INTO premium_history(
                    type, a_code, pair_code, trade_date,
                    a_price, pair_price, pair_price_cny, fx_rate,
                    premium, currency, pair_market,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(type, a_code, trade_date) DO UPDATE SET
                    pair_code = excluded.pair_code,
                    a_price = excluded.a_price,
                    pair_price = excluded.pair_price,
                    pair_price_cny = excluded.pair_price_cny,
                    fx_rate = excluded.fx_rate,
                    premium = excluded.premium,
                    currency = excluded.currency,
                    pair_market = excluded.pair_market,
                    updated_at = excluded.updated_at
                """,
                (
                    item["type"],
                    item["aCode"],
                    item["pairCode"],
                    item["date"],
                    float(item["aPrice"]),
                    float(item["pairPrice"]),
                    float(item["pairPriceCny"]),
                    float(item["exchangeRate"]),
                    float(item["premium"]),
                    item["currency"],
                    item["pairMarket"],
                    ts,
                    ts,
                ),
            )
            count += 1
            touched_keys.add((str(item["type"]), str(item["aCode"])))
    if touched_keys:
        refresh_premium_summary(list(touched_keys))
    return count


def refresh_premium_summary(keys: List[tuple[str, str]]) -> int:
    if not keys:
        return 0

    ts = now_iso()
    updated = 0
    with connect() as conn:
        for stock_type, a_code in keys:
            cutoff_3y = cutoff_date(365 * 3)
            row = conn.execute(
                """
                SELECT
                    type,
                    a_code,
                    MIN(premium) AS min_premium,
                    MAX(premium) AS max_premium,
                    MIN(trade_date) AS start_date,
                    MAX(trade_date) AS end_date,
                    COUNT(1) AS sample_count
                FROM premium_history
                WHERE type = ? AND a_code = ?
                """,
                (stock_type, a_code),
            ).fetchone()
            if not row or not row["sample_count"]:
                conn.execute(
                    "DELETE FROM premium_summary WHERE type = ? AND a_code = ?",
                    (stock_type, a_code),
                )
                continue

            row_3y = conn.execute(
                """
                SELECT
                    MIN(premium) AS min_premium,
                    MAX(premium) AS max_premium,
                    MIN(trade_date) AS start_date,
                    MAX(trade_date) AS end_date,
                    COUNT(1) AS sample_count
                FROM premium_history
                WHERE type = ? AND a_code = ? AND trade_date >= ?
                """,
                (stock_type, a_code, cutoff_3y),
            ).fetchone()

            pair_row = conn.execute(
                """
                SELECT pair_code
                FROM premium_history
                WHERE type = ? AND a_code = ?
                ORDER BY trade_date DESC
                LIMIT 1
                """,
                (stock_type, a_code),
            ).fetchone()
            pair_code = str(pair_row["pair_code"]) if pair_row and pair_row["pair_code"] else ""

            return_rows = conn.execute(
                """
                SELECT trade_date, a_price, pair_price_cny
                FROM premium_history
                WHERE type = ? AND a_code = ?
                ORDER BY trade_date ASC
                """,
                (stock_type, a_code),
            ).fetchall()
            first_row = return_rows[0] if return_rows else None
            last_row = return_rows[-1] if return_rows else None

            a_return_5y = None
            pair_return_5y = None
            return_start_date = None
            return_end_date = None
            if first_row and last_row:
                first_a = float(first_row["a_price"]) if first_row["a_price"] is not None else None
                last_a = float(last_row["a_price"]) if last_row["a_price"] is not None else None
                first_pair = float(first_row["pair_price_cny"]) if first_row["pair_price_cny"] is not None else None
                last_pair = float(last_row["pair_price_cny"]) if last_row["pair_price_cny"] is not None else None
                if first_a and first_a > 0 and last_a is not None:
                    a_return_5y = ((last_a / first_a) - 1) * 100
                if first_pair and first_pair > 0 and last_pair is not None:
                    pair_return_5y = ((last_pair / first_pair) - 1) * 100
                return_start_date = str(first_row["trade_date"] or "")
                return_end_date = str(last_row["trade_date"] or "")

            conn.execute(
                """
                INSERT INTO premium_summary(
                    type, a_code, pair_code, min_premium, max_premium,
                    start_date, end_date, sample_count,
                    min_premium_3y, max_premium_3y, start_date_3y, end_date_3y, sample_count_3y,
                    a_return_5y, pair_return_5y, return_start_date, return_end_date,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(type, a_code) DO UPDATE SET
                    pair_code = excluded.pair_code,
                    min_premium = excluded.min_premium,
                    max_premium = excluded.max_premium,
                    start_date = excluded.start_date,
                    end_date = excluded.end_date,
                    sample_count = excluded.sample_count,
                    min_premium_3y = excluded.min_premium_3y,
                    max_premium_3y = excluded.max_premium_3y,
                    start_date_3y = excluded.start_date_3y,
                    end_date_3y = excluded.end_date_3y,
                    sample_count_3y = excluded.sample_count_3y,
                    a_return_5y = excluded.a_return_5y,
                    pair_return_5y = excluded.pair_return_5y,
                    return_start_date = excluded.return_start_date,
                    return_end_date = excluded.return_end_date,
                    updated_at = excluded.updated_at
                """,
                (
                    stock_type,
                    a_code,
                    pair_code,
                    float(row["min_premium"]),
                    float(row["max_premium"]),
                    str(row["start_date"]),
                    str(row["end_date"]),
                    int(row["sample_count"]),
                    float(row_3y["min_premium"]) if row_3y and row_3y["sample_count"] else None,
                    float(row_3y["max_premium"]) if row_3y and row_3y["sample_count"] else None,
                    str(row_3y["start_date"]) if row_3y and row_3y["sample_count"] else None,
                    str(row_3y["end_date"]) if row_3y and row_3y["sample_count"] else None,
                    int(row_3y["sample_count"]) if row_3y and row_3y["sample_count"] else 0,
                    a_return_5y,
                    pair_return_5y,
                    return_start_date,
                    return_end_date,
                    ts,
                ),
            )
            updated += 1
    return updated


def load_premium_summaries(stock_type: str, codes: List[str]) -> Dict[str, Dict]:
    normalized_codes = [str(code or "").strip() for code in codes if str(code or "").strip()]
    if not normalized_codes:
        return {}

    def _query() -> Dict[str, Dict]:
        placeholders = ",".join(["?"] * len(normalized_codes))
        with connect() as conn:
            rows = conn.execute(
                f"""
                SELECT
                    a_code,
                    pair_code,
                    min_premium,
                    max_premium,
                    start_date,
                    end_date,
                    sample_count,
                    min_premium_3y,
                    max_premium_3y,
                    start_date_3y,
                    end_date_3y,
                    sample_count_3y,
                    a_return_5y,
                    pair_return_5y,
                    return_start_date,
                    return_end_date,
                    updated_at
                FROM premium_summary
                WHERE type = ? AND a_code IN ({placeholders})
                """,
                [stock_type, *normalized_codes],
            ).fetchall()

        result: Dict[str, Dict] = {}
        for row in rows:
            result[str(row["a_code"])] = {
                "pairCode": str(row["pair_code"] or ""),
                "minPremium": float(row["min_premium"]),
                "maxPremium": float(row["max_premium"]),
                "startDate": str(row["start_date"] or ""),
                "endDate": str(row["end_date"] or ""),
                "sampleCount": int(row["sample_count"] or 0),
                "minPremium3Y": float(row["min_premium_3y"]) if row["min_premium_3y"] is not None else None,
                "maxPremium3Y": float(row["max_premium_3y"]) if row["max_premium_3y"] is not None else None,
                "startDate3Y": str(row["start_date_3y"] or ""),
                "endDate3Y": str(row["end_date_3y"] or ""),
                "sampleCount3Y": int(row["sample_count_3y"] or 0),
                "aReturn5Y": float(row["a_return_5y"]) if row["a_return_5y"] is not None else None,
                "pairReturn5Y": float(row["pair_return_5y"]) if row["pair_return_5y"] is not None else None,
                "returnStartDate": str(row["return_start_date"] or ""),
                "returnEndDate": str(row["return_end_date"] or ""),
                "updatedAt": str(row["updated_at"] or ""),
            }
        return result

    result = _query()
    missing = [code for code in normalized_codes if code not in result]
    if missing:
        refresh_premium_summary([(stock_type, code) for code in missing])
        result = _query()
    return result


def load_premium_distributions(stock_type: str, codes: List[str], days: int = 365 * 3) -> Dict[str, List[float]]:
    normalized_codes = [str(code or "").strip() for code in codes if str(code or "").strip()]
    if not normalized_codes:
        return {}

    placeholders = ",".join(["?"] * len(normalized_codes))
    start_date = cutoff_date(days)
    with connect() as conn:
        rows = conn.execute(
            f"""
            SELECT a_code, premium
            FROM premium_history
            WHERE type = ? AND a_code IN ({placeholders}) AND trade_date >= ?
            ORDER BY a_code ASC, trade_date ASC
            """,
            [stock_type, *normalized_codes, start_date],
        ).fetchall()

    result: Dict[str, List[float]] = {code: [] for code in normalized_codes}
    for row in rows:
        code = str(row["a_code"] or "").strip()
        premium = row["premium"]
        if not code or premium is None:
            continue
        result.setdefault(code, []).append(float(premium))
    return result


def load_premium_history(stock_type: str, a_code: str, days: int = 365 * 5) -> List[Dict]:
    start_date = cutoff_date(days)
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
                trade_date,
                a_code,
                pair_code,
                a_price,
                pair_price,
                pair_price_cny,
                fx_rate,
                premium,
                currency,
                pair_market
            FROM premium_history
            WHERE type = ? AND a_code = ? AND trade_date >= ?
            ORDER BY trade_date ASC
            """,
            (stock_type, a_code, start_date),
        ).fetchall()

    result: List[Dict] = []
    if stock_type == "AH":
        pair_field = "hPrice"
    else:
        pair_field = "bPrice"

    for row in rows:
        result.append(
            {
                "date": row["trade_date"],
                "aCode": row["a_code"],
                "pairCode": row["pair_code"],
                "aPrice": float(row["a_price"]),
                pair_field: float(row["pair_price"]),
                f"{pair_field}Cny": float(row["pair_price_cny"]),
                "exchangeRate": float(row["fx_rate"]),
                "premium": float(row["premium"]),
                "currency": row["currency"],
                "pairMarket": row["pair_market"],
            }
        )

    return result

