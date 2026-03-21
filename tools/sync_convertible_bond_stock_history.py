#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sync HFQ K-line history for all convertible-bond underlying stocks."""

from __future__ import annotations

import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import akshare as ak
import pandas as pd
from data_fetch.convertible_bond.history_source import sync_cb_stock_history as plugin_sync_cb_stock_history

from 抓取convertible_bond import _build_cov_quote_map, _build_cov_realtime_map, _to_code6
import stock_price_history_db as db

MAX_WORKERS = 8
MAX_ROWS_PER_SYMBOL = 120
LOOKBACK_DAYS = 360


def _load_jisilu_cookie() -> str:
    cookie = os.getenv("JISILU_COOKIE", "").strip()
    if cookie:
        return cookie
    env_path = ROOT / ".env"
    if not env_path.exists():
        return ""
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("JISILU_COOKIE="):
                return line.split("=", 1)[1].strip()
    except Exception:
        return ""
    return ""


def _is_supported_stock_code(stock_code: str) -> bool:
    code = str(stock_code or "").strip()
    return len(code) == 6 and code[0] in {"0", "3", "6"}


def _to_tx_symbol(stock_code: str) -> str:
    code = str(stock_code or "").strip()
    if not code:
        return ""
    market = "sh" if code.startswith(("5", "6", "9")) else "sz"
    return f"{market}{code}"


def _extract_rows_from_frame(frame: pd.DataFrame) -> List[Dict[str, Any]]:
    if frame is None or frame.empty:
        return []

    date_col = next((name for name in ("\u65e5\u671f", "date") if name in frame.columns), None)
    close_col = next((name for name in ("\u6536\u76d8", "close") if name in frame.columns), None)
    if not date_col or not close_col:
        return []

    rows: List[Dict[str, Any]] = []
    for _, record in frame.iterrows():
        trade_date = pd.to_datetime(record.get(date_col), errors="coerce")
        close = pd.to_numeric(pd.Series([record.get(close_col)]), errors="coerce").iloc[0]
        if pd.isna(trade_date) or pd.isna(close):
            continue
        close_val = float(close)
        if close_val <= 0:
            continue
        rows.append({"date": trade_date.date().isoformat(), "close": close_val})
    return rows


def _extract_underlying_codes_from_live() -> List[str]:
    realtime_items = _build_cov_realtime_map()
    quote_items = _build_cov_quote_map()
    if not realtime_items or not quote_items:
        return []

    codes = []
    seen = set()
    for bond_code in realtime_items.keys():
        quote_row = quote_items.get(str(bond_code))
        if not isinstance(quote_row, dict):
            continue
        code = _to_code6(quote_row.get("stockCode"))
        if not _is_supported_stock_code(code) or code in seen:
            continue
        seen.add(code)
        codes.append(code)
    return sorted(codes)


def _extract_underlying_codes_from_jsl(cookie: str) -> List[str]:
    if not cookie:
        return []
    df = ak.bond_cb_jsl(cookie=cookie)
    if df is None or df.empty:
        return []
    code_col = "\u6b63\u80a1\u4ee3\u7801"
    if code_col not in df.columns:
        return []

    codes = []
    seen = set()
    for value in df[code_col].tolist():
        code = str(value or "").strip()
        if not _is_supported_stock_code(code) or code in seen:
            continue
        seen.add(code)
        codes.append(code)
    return sorted(codes)


def _extract_underlying_codes(cookie: str) -> List[str]:
    try:
        codes = _extract_underlying_codes_from_live()
        if codes:
            return codes
    except Exception:
        pass
    return _extract_underlying_codes_from_jsl(cookie)


def _sync_symbol(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    if not _is_supported_stock_code(symbol):
        db.upsert_symbol_universe(symbol, status="unsupported", note="non_standard_a_share_code")
        return {"symbol": symbol, "success": True, "rows": 0, "skipped": True}

    try:
        frame = ak.stock_zh_a_hist_tx(
            symbol=_to_tx_symbol(symbol),
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        rows = _extract_rows_from_frame(frame)
        if not rows:
            db.upsert_symbol_universe(symbol, status="failed", note="empty_history")
            return {"symbol": symbol, "success": False, "rows": 0, "error": "empty_history"}

        written = db.upsert_price_rows(symbol, rows, "tencent")
        db.upsert_symbol_universe(symbol, status="active", note="")
        return {"symbol": symbol, "success": True, "rows": written}
    except Exception as exc:
        db.upsert_symbol_universe(symbol, status="failed", note=str(exc))
        return {"symbol": symbol, "success": False, "rows": 0, "error": str(exc)}


def sync_cb_stock_history(force_full: bool = False) -> Dict[str, Any]:
    db.init_db()

    cookie = _load_jisilu_cookie()
    try:
        symbols = _extract_underlying_codes(cookie)
    except Exception as exc:
        return {
            "success": False,
            "error": f"load_underlying_failed: {exc}",
            "updateTime": datetime.now().isoformat(),
        }

    if not symbols:
        return {
            "success": False,
            "error": "no_underlying_symbols",
            "updateTime": datetime.now().isoformat(),
        }

    cleanup = db.purge_symbols_not_in_universe(symbols)

    for symbol in symbols:
        db.upsert_symbol_universe(symbol, status="pending", note="")

    end_date = datetime.now().strftime("%Y%m%d")
    default_start = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y%m%d")

    def task_args(symbol: str) -> tuple[str, str, str]:
        if force_full:
            return symbol, "20200101", end_date
        last_trade = db.get_last_trade_date(symbol)
        if not last_trade:
            return symbol, default_start, end_date
        start = (datetime.fromisoformat(last_trade) - timedelta(days=5)).strftime("%Y%m%d")
        return symbol, start, end_date

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(symbols)))) as executor:
        future_map = {
            executor.submit(_sync_symbol, *task_args(symbol)): symbol
            for symbol in symbols
        }
        for future in as_completed(future_map):
            try:
                results.append(future.result())
            except Exception as exc:
                results.append({
                    "symbol": future_map[future],
                    "success": False,
                    "rows": 0,
                    "error": str(exc),
                })

    pruned = db.prune_to_recent_rows(MAX_ROWS_PER_SYMBOL)

    ok = [item for item in results if item.get("success") and not item.get("skipped")]
    skipped = [item for item in results if item.get("skipped")]
    failed = [item for item in results if not item.get("success")]

    return {
        "success": len(failed) == 0,
        "totalSymbols": len(symbols),
        "syncedSymbols": len(ok),
        "skippedSymbols": len(skipped),
        "failedSymbols": len(failed),
        "writtenRows": sum(int(item.get("rows") or 0) for item in ok),
        "prunedRows": int(pruned),
        "removedStaleSymbols": int(cleanup.get("removedSymbols") or 0),
        "removedStalePriceRows": int(cleanup.get("removedPriceRows") or 0),
        "failed": failed[:30],
        "updateTime": datetime.now().isoformat(),
        "source": "tencent+akshare",
    }


if __name__ == "__main__":
    force_full = "--force-full" in sys.argv[1:]
    print(json.dumps(plugin_sync_cb_stock_history(force_full=force_full), ensure_ascii=False))


