#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""同步可转债抢权配售功能专用的正股历史库。"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

import akshare as ak
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.config.script_config import get_config
from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

import cb_rights_issue_stock_history_db as history_db
from data_fetch.cb_rights_issue.source import fetch_fixed_source_rows, normalize_stock_code

_CONFIG = get_config()
_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("cb_rights_issue") or {})

LOOKBACK_DAYS = max(120, int(_FETCH_CONFIG.get("history_lookback_days") or 420))
MAX_WORKERS = max(1, int(_FETCH_CONFIG.get("max_history_sync_workers") or 8))
VOL_WINDOW = max(1, int((((_CONFIG.get("strategy") or {}).get("cb_rights_issue") or {}).get("volatility_window") or 60)))
REQUIRED_CLOSE_ROWS = VOL_WINDOW + 1


def _to_tx_symbol(stock_code: str) -> str:
    code = str(stock_code or "").strip()
    if not code:
        return ""
    market = "sh" if code.startswith(("5", "6", "9")) else "sz"
    return f"{market}{code}"


def _extract_hist_rows(frame: pd.DataFrame) -> List[Dict[str, Any]]:
    if frame is None or frame.empty:
        return []

    date_col = next((name for name in ("日期", "date") if name in frame.columns), None)
    close_col = next((name for name in ("收盘", "close") if name in frame.columns), None)
    if not date_col or not close_col:
        return []

    rows: List[Dict[str, Any]] = []
    for _, record in frame.iterrows():
        trade_date = pd.to_datetime(record.get(date_col), errors="coerce")
        close = pd.to_numeric(pd.Series([record.get(close_col)]), errors="coerce").iloc[0]
        if pd.isna(trade_date) or pd.isna(close):
            continue
        close_value = float(close)
        if close_value <= 0:
            continue
        rows.append({
            "date": trade_date.date().isoformat(),
            "close": close_value,
        })
    return rows


def _fetch_hist_rows(stock_code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    try:
        frame = ak.stock_zh_a_daily(
            symbol=_to_tx_symbol(stock_code),
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        rows = _extract_hist_rows(frame)
        if rows:
            return rows
    except Exception:
        pass

    try:
        frame = ak.stock_zh_a_hist(
            symbol=str(stock_code),
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        return _extract_hist_rows(frame)
    except Exception:
        return []


def _extract_symbols_from_source_rows(rows: Iterable[Dict[str, Any]]) -> List[str]:
    symbols = []
    seen = set()
    for item in rows:
        code = normalize_stock_code(item.get("stock_id") or item.get("stockCode") or item.get("stock_code"))
        if not code or code in seen:
            continue
        seen.add(code)
        symbols.append(code)
    return sorted(symbols)


def _sync_symbol(symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
    try:
        rows = _fetch_hist_rows(symbol, start_date, end_date)
        if not rows:
            history_db.upsert_symbol_universe(symbol, status="failed", note="empty_history")
            return {"symbol": symbol, "success": False, "rows": 0, "error": "empty_history"}
        written = history_db.upsert_price_rows(symbol, rows, "akshare_hfq")
        history_db.upsert_symbol_universe(symbol, status="active", note="")
        return {"symbol": symbol, "success": True, "rows": int(written or 0)}
    except Exception as exc:
        history_db.upsert_symbol_universe(symbol, status="failed", note=str(exc))
        return {"symbol": symbol, "success": False, "rows": 0, "error": str(exc)}


def _build_task_args(symbol: str, *, force_full: bool) -> tuple[str, str, str]:
    end_date = datetime.now().strftime("%Y%m%d")
    if force_full:
        return symbol, "20200101", end_date

    closes = history_db.load_recent_closes(symbol, REQUIRED_CLOSE_ROWS)
    if len(closes) < REQUIRED_CLOSE_ROWS:
        start = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y%m%d")
        return symbol, start, end_date

    last_trade_date = history_db.get_last_trade_date(symbol)
    if not last_trade_date:
        start = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime("%Y%m%d")
        return symbol, start, end_date

    start = (datetime.fromisoformat(last_trade_date) - timedelta(days=5)).strftime("%Y%m%d")
    return symbol, start, end_date


def sync_cb_rights_issue_stock_history(*, force_full: bool = False, target_symbols: Sequence[str] | None = None) -> Dict[str, Any]:
    """同步当前固定来源对应正股的历史收盘价。"""

    history_db.init_db()
    symbols = sorted({normalize_stock_code(item) for item in (target_symbols or []) if normalize_stock_code(item)})
    cleanup = {
        "removedSymbols": 0,
        "removedPriceRows": 0,
    }
    if not symbols:
        source_rows = fetch_fixed_source_rows()
        symbols = _extract_symbols_from_source_rows(source_rows)
        cleanup = history_db.purge_symbols_not_in_universe(symbols)

    if not symbols:
        return {
            "success": False,
            "error": "no_source_symbols",
            "updateTime": datetime.now().isoformat(),
        }

    for symbol in symbols:
        history_db.upsert_symbol_universe(symbol, status="pending", note="")

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(symbols)))) as executor:
        future_map = {
            executor.submit(_sync_symbol, *_build_task_args(symbol, force_full=force_full)): symbol
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

    failed = [item for item in results if not item.get("success")]
    succeeded = [item for item in results if item.get("success")]
    return {
        "success": len(failed) == 0,
        "totalSymbols": len(symbols),
        "syncedSymbols": len(succeeded),
        "failedSymbols": len(failed),
        "writtenRows": sum(int(item.get("rows") or 0) for item in succeeded),
        "removedStaleSymbols": int(cleanup.get("removedSymbols") or 0),
        "removedStalePriceRows": int(cleanup.get("removedPriceRows") or 0),
        "failed": failed[:20],
        "updateTime": datetime.now().isoformat(),
        "source": "jisilu+akshare",
    }


if __name__ == "__main__":
    force_full = "--force-full" in sys.argv[1:]
    print(json.dumps(sync_cb_rights_issue_stock_history(force_full=force_full), ensure_ascii=False))
