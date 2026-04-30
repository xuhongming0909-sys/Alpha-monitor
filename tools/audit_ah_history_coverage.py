#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Audit AH premium history coverage and classify short-history causes."""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import akshare as ak

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.paths.db_paths import shared_db_path

DB_PATH = shared_db_path("premium_history.db")
CUTOFF_3Y = (datetime.now() - timedelta(days=365 * 3)).strftime("%Y-%m-%d")
DEFAULT_SAMPLE_THRESHOLD = 550
DEFAULT_START_GRACE_DAYS = 30


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def parse_args(argv: list[str]) -> dict[str, Any]:
    options: dict[str, Any] = {
        "code": None,
        "limit": 20,
        "threshold": DEFAULT_SAMPLE_THRESHOLD,
        "grace_days": DEFAULT_START_GRACE_DAYS,
    }

    args = list(argv)
    while args:
        token = args.pop(0)
        if token == "--code" and args:
            options["code"] = args.pop(0).strip()
        elif token == "--limit" and args:
            options["limit"] = max(1, int(args.pop(0)))
        elif token == "--threshold" and args:
            options["threshold"] = max(1, int(args.pop(0)))
        elif token == "--grace-days" and args:
            options["grace_days"] = max(0, int(args.pop(0)))
    return options


def load_candidates(code: str | None, limit: int, threshold: int, grace_days: int) -> list[sqlite3.Row]:
    grace_date = (datetime.now() - timedelta(days=365 * 3 - grace_days)).strftime("%Y-%m-%d")
    with connect() as conn:
        if code:
            rows = conn.execute(
                """
                SELECT a_code, pair_code, sample_count_3y, start_date_3y, end_date_3y
                FROM premium_summary
                WHERE type = 'AH' AND a_code = ?
                ORDER BY sample_count_3y ASC
                """,
                (code,),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT a_code, pair_code, sample_count_3y, start_date_3y, end_date_3y
                FROM premium_summary
                WHERE type = 'AH'
                  AND (
                    COALESCE(sample_count_3y, 0) < ?
                    OR COALESCE(start_date_3y, '') > ?
                  )
                ORDER BY sample_count_3y ASC, a_code ASC
                LIMIT ?
                """,
                (threshold, grace_date, limit),
            ).fetchall()
    return list(rows)


def fetch_first_date(market: str, code: str) -> str | None:
    try:
        if market in {"sh", "sz"}:
            frame = ak.stock_zh_a_hist_tx(symbol=f"{market}{code}")
        elif market == "hk":
            frame = ak.stock_hk_daily(symbol=str(code).zfill(5))
        else:
            return None
    except Exception:
        return None

    if frame is None or getattr(frame, "empty", True):
        return None
    try:
        return str(frame["date"].iloc[0])[:10]
    except Exception:
        return None


def classify_row(row: sqlite3.Row) -> dict[str, Any]:
    a_code = str(row["a_code"])
    pair_code = str(row["pair_code"])
    a_market = "sh" if a_code.startswith("6") else "sz"

    a_first = fetch_first_date(a_market, a_code)
    h_first = fetch_first_date("hk", pair_code)
    source_start = max(date for date in [a_first, h_first] if date) if (a_first or h_first) else None

    if source_start and source_start > CUTOFF_3Y:
        category = "source_late_start"
        reason = "A股或H股可用历史本来就晚于三年窗口起点"
    else:
        category = "possible_backfill_gap"
        reason = "理论上应有更长历史，但数据库当前覆盖偏短，建议检查回填链路"

    return {
        "aCode": a_code,
        "pairCode": pair_code,
        "sampleCount3Y": int(row["sample_count_3y"] or 0),
        "startDate3Y": str(row["start_date_3y"] or ""),
        "endDate3Y": str(row["end_date_3y"] or ""),
        "sourceWindowStart": source_start,
        "aFirstDate": a_first,
        "hFirstDate": h_first,
        "category": category,
        "reason": reason,
    }


def main(argv: list[str]) -> int:
    if not Path(DB_PATH).exists():
        print(json.dumps({"success": False, "error": f"missing database: {DB_PATH}"}, ensure_ascii=False))
        return 1

    options = parse_args(argv)
    rows = load_candidates(options["code"], options["limit"], options["threshold"], options["grace_days"])
    result = [classify_row(row) for row in rows]

    payload = {
      "success": True,
      "cutoff3Y": CUTOFF_3Y,
      "database": str(DB_PATH),
      "count": len(result),
      "items": result,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
