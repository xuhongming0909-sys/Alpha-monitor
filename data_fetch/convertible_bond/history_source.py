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

import akshare as ak
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from data_fetch.convertible_bond.source import _build_cov_quote_map, _build_cov_realtime_map, _to_code6
from shared.config.script_config import get_config
import stock_price_history_db as db

_CONFIG = get_config()
_CB_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("convertible_bond") or {})

MAX_WORKERS = max(1, int(_CB_FETCH_CONFIG.get("max_vol_sync_workers") or 8))
LOOKBACK_DAYS = max(120, int(_CB_FETCH_CONFIG.get("history_lookback_days") or 420))
VOL_WINDOWS = tuple(
    sorted({max(1, int(item)) for item in (_CB_FETCH_CONFIG.get("volatility_windows") or [250])})
) or (250,)
ATR_WINDOW = max(1, int(_CB_FETCH_CONFIG.get("atr_window") or 20))
TURNOVER_AVG_WINDOWS = tuple(
    sorted({max(1, int(item)) for item in (_CB_FETCH_CONFIG.get("turnover_avg_windows") or [5, 20])})
) or (5, 20)
REQUIRED_CLOSE_ROWS = max(VOL_WINDOWS) + 1
REQUIRED_RICH_BAR_ROWS = max(ATR_WINDOW + 1, max(TURNOVER_AVG_WINDOWS))
STOCK_HISTORY_RETENTION_ROWS = max(
    max(REQUIRED_CLOSE_ROWS, REQUIRED_RICH_BAR_ROWS) + 30,
    int(_CB_FETCH_CONFIG.get("stock_history_retention_rows") or 320),
)


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


def _pick_col(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    return next((name for name in candidates if name in frame.columns), None)


def _extract_rows_from_frame(frame: pd.DataFrame, *, include_amount: bool) -> List[Dict[str, Any]]:
    if frame is None or frame.empty:
        return []

    date_col = _pick_col(frame, ("\u65e5\u671f", "date"))
    close_col = _pick_col(frame, ("\u6536\u76d8", "close"))
    high_col = _pick_col(frame, ("\u6700\u9ad8", "high"))
    low_col = _pick_col(frame, ("\u6700\u4f4e", "low"))
    amount_col = _pick_col(frame, ("\u6210\u4ea4\u989d", "amount"))
    if not date_col or not close_col:
        return []

    rows: List[Dict[str, Any]] = []
    dates = pd.to_datetime(frame[date_col], errors="coerce")
    closes = pd.to_numeric(frame[close_col], errors="coerce")
    highs = pd.to_numeric(frame[high_col], errors="coerce") if high_col else [None] * len(frame)
    lows = pd.to_numeric(frame[low_col], errors="coerce") if low_col else [None] * len(frame)
    amounts = pd.to_numeric(frame[amount_col], errors="coerce") if amount_col and include_amount else [None] * len(frame)
    for trade_date, close, high, low, amount in zip(
        dates.tolist(),
        closes.tolist(),
        highs.tolist() if hasattr(highs, "tolist") else highs,
        lows.tolist() if hasattr(lows, "tolist") else lows,
        amounts.tolist() if hasattr(amounts, "tolist") else amounts,
    ):
        if pd.isna(trade_date) or pd.isna(close):
            continue
        close_val = float(close)
        if close_val <= 0:
            continue
        rows.append({
            "date": trade_date.date().isoformat(),
            "close": close_val,
            "high": float(high) if high is not None and not pd.isna(high) and float(high) > 0 else None,
            "low": float(low) if low is not None and not pd.isna(low) and float(low) > 0 else None,
            "amount": float(amount) if amount is not None and not pd.isna(amount) and float(amount) >= 0 else None,
        })
    return rows


def _fetch_hist_rows(symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    try:
        frame = ak.stock_zh_a_daily(
            symbol=_to_tx_symbol(symbol),
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        rows = _extract_rows_from_frame(frame, include_amount=True)
        if rows:
            return rows
    except Exception:
        pass

    try:
        frame = ak.stock_zh_a_hist_tx(
            symbol=_to_tx_symbol(symbol),
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        return _extract_rows_from_frame(frame, include_amount=False)
    except Exception:
        return []


def _has_recent_rich_bars(symbol: str) -> bool:
    # 只有最近窗口同时具备 high / low / amount，后续 ATR 和均成交额字段才有真实计算基础。
    bars = db.load_recent_bars(symbol, REQUIRED_RICH_BAR_ROWS)
    if len(bars) < REQUIRED_RICH_BAR_ROWS:
        return False
    atr_ready = sum(
        1 for item in bars
        if item.get("close") is not None and item.get("high") is not None and item.get("low") is not None
    ) >= (ATR_WINDOW + 1)
    turnover_ready = sum(1 for item in bars if item.get("amount") is not None) >= max(TURNOVER_AVG_WINDOWS)
    return atr_ready and turnover_ready


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
        rows = _fetch_hist_rows(symbol, start_date, end_date)
        if not rows:
            db.upsert_symbol_universe(symbol, status="failed", note="empty_history")
            return {"symbol": symbol, "success": False, "rows": 0, "error": "empty_history"}

        written = db.upsert_price_rows(symbol, rows, "akshare_stock_zh_a_daily")
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
        if not _has_recent_rich_bars(symbol):
            start = (datetime.now() - timedelta(days=max(LOOKBACK_DAYS, 120))).strftime("%Y%m%d")
            return symbol, start, end_date
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

    ok = [item for item in results if item.get("success") and not item.get("skipped")]
    skipped = [item for item in results if item.get("skipped")]
    failed = [item for item in results if not item.get("success")]
    pruned_rows = db.prune_to_recent_rows(STOCK_HISTORY_RETENTION_ROWS)

    return {
        "success": len(failed) == 0,
        "totalSymbols": len(symbols),
        "syncedSymbols": len(ok),
        "skippedSymbols": len(skipped),
        "failedSymbols": len(failed),
        "writtenRows": sum(int(item.get("rows") or 0) for item in ok),
        # 历史 K 线库作为波动率权威来源，不再在同步后把每个股票裁成短滚动窗口。
        "prunedRows": int(pruned_rows or 0),
        "prunedRows": int(pruned_rows or 0),
        "removedStaleSymbols": int(cleanup.get("removedSymbols") or 0),
        "removedStalePriceRows": int(cleanup.get("removedPriceRows") or 0),
        "failed": failed[:30],
        "updateTime": datetime.now().isoformat(),
        "source": "tencent+akshare",
    }


if __name__ == "__main__":
    force_full = "--force-full" in sys.argv[1:]
    print(json.dumps(sync_cb_stock_history(force_full=force_full), ensure_ascii=False))


