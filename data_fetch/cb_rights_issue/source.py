#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""抓取并标准化可转债抢权配售固定来源数据。"""

from __future__ import annotations

import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import akshare as ak
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.config.script_config import get_config
from shared.market_service import get_quotes
from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

import cb_rights_issue_stock_history_db as history_db
_CONFIG = get_config()
_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("cb_rights_issue") or {})
_STRATEGY_CONFIG = (((_CONFIG.get("strategy") or {}).get("cb_rights_issue") or {}))

SOURCE_PAGE_URL = str(_FETCH_CONFIG.get("source_page_url") or "https://www.jisilu.cn/web/data/cb/pre").strip()
SOURCE_API_URL = str(_FETCH_CONFIG.get("source_api_url") or "https://www.jisilu.cn/webapi/cb/pre/").strip()
SOURCE_REFERER = str(_FETCH_CONFIG.get("source_referer") or SOURCE_PAGE_URL).strip()
SOURCE_TITLE = str(_FETCH_CONFIG.get("source_title") or "集思录可转债预案").strip()
REQUEST_TIMEOUT_MS = max(5000, int(_FETCH_CONFIG.get("request_timeout_ms") or 20000))
INLINE_HISTORY_HYDRATE_LIMIT = max(1, int(_FETCH_CONFIG.get("inline_history_hydrate_limit") or 12))
VOL_WINDOW = max(1, int(_STRATEGY_CONFIG.get("volatility_window") or 60))
TRADING_DAYS_PER_YEAR = 252


def now_iso() -> str:
    return datetime.now().isoformat()


def to_float(value: Any) -> Optional[float]:
    text = str(value or "").strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def normalize_stock_code(value: Any) -> str:
    text = str(value or "").strip()
    return text if len(text) == 6 and text[0] in {"0", "3", "6"} else ""


def normalize_date(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) >= 10:
        return text[:10]
    return text


def infer_market_from_stock_code(stock_code: str) -> str:
    code = normalize_stock_code(stock_code)
    return "sh" if code.startswith(("6", "68")) else "sz"


def to_quote_code(stock_code: str) -> str:
    code = normalize_stock_code(stock_code)
    if not code:
        return ""
    return f"{infer_market_from_stock_code(code)}{code}"


def fetch_fixed_source_rows() -> List[Dict[str, Any]]:
    """直接读取集思录固定来源 JSON。"""

    response = requests.get(
        SOURCE_API_URL,
        params={"history": 0},
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": SOURCE_REFERER,
            "Accept": "application/json,text/plain,*/*",
        },
        timeout=REQUEST_TIMEOUT_MS / 1000.0,
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("data") or payload.get("rows") or []
    return rows if isinstance(rows, list) else []


def _load_latest_stock_price_map(stock_codes: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    query_codes = [to_quote_code(code) for code in stock_codes if to_quote_code(code)]
    quote_map = get_quotes(query_codes, timeout=max(8, int(REQUEST_TIMEOUT_MS / 1000)))
    result: Dict[str, Dict[str, Any]] = {}
    for code in stock_codes:
        query_code = to_quote_code(code)
        if not query_code:
            continue
        quote = quote_map.get(query_code) or {}
        result[str(code)] = {
            "price": to_float(quote.get("price")),
            "name": str(quote.get("name") or "").strip(),
        }
    return result


def _calc_volatility_from_closes(closes: List[float]) -> Optional[float]:
    if len(closes) < VOL_WINDOW + 1:
        return None
    returns: List[float] = []
    for left, right in zip(closes[:-1], closes[1:]):
        if left <= 0 or right <= 0:
            continue
        returns.append(math.log(right / left))
    if len(returns) < VOL_WINDOW:
        return None
    sample = returns[-VOL_WINDOW:]
    mean_value = sum(sample) / len(sample)
    variance = sum((item - mean_value) ** 2 for item in sample) / len(sample)
    return math.sqrt(variance) * math.sqrt(TRADING_DAYS_PER_YEAR)


def _load_history_metrics(stock_codes: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    metrics: Dict[str, Dict[str, Any]] = {}
    for stock_code in sorted({normalize_stock_code(code) for code in stock_codes if normalize_stock_code(code)}):
        closes = history_db.load_recent_closes(stock_code, VOL_WINDOW + 1)
        metrics[stock_code] = {
            "closeCount": len(closes),
            "volatility60": _calc_volatility_from_closes(closes),
        }
    return metrics


def _hydrate_missing_history(metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    missing = [
        code
        for code, item in metrics.items()
        if not isinstance(item, dict) or item.get("volatility60") is None
    ]
    if not missing:
        return {"requested": 0, "success": True}
    if len(missing) > INLINE_HISTORY_HYDRATE_LIMIT:
        return {"requested": len(missing), "success": False, "skipped": "over_inline_limit"}
    # 这里延迟导入，避免 source.py 与 history_source.py 之间形成循环依赖。
    from data_fetch.cb_rights_issue.history_source import sync_cb_rights_issue_stock_history

    return sync_cb_rights_issue_stock_history(target_symbols=missing)


def _get_risk_free_rate() -> Dict[str, Any]:
    df = ak.bond_gb_zh_sina()
    if df is None or df.empty:
        raise RuntimeError("bond_gb_zh_sina returned empty data")
    latest = df.iloc[-1]
    close_rate = to_float(latest.get("close"))
    if close_rate is None:
        raise RuntimeError("10Y treasury close rate missing")
    return {
        "rate": close_rate / 100.0,
        "percent": close_rate,
        "date": normalize_date(latest.get("date")),
        "source": "sina",
    }


def get_cb_rights_issue_source_snapshot() -> Dict[str, Any]:
    """抓取固定来源并补充实时价、国债收益率和专用历史库指标。"""

    try:
        raw_rows = fetch_fixed_source_rows()
    except Exception as exc:
        return {
            "success": False,
            "error": f"fixed_source_fetch_failed: {exc}",
            "updateTime": now_iso(),
            "source": "jisilu",
        }

    history_db.init_db()
    stock_codes = sorted({
        normalize_stock_code(item.get("stock_id"))
        for item in raw_rows
        if normalize_stock_code(item.get("stock_id"))
    })
    history_metrics = _load_history_metrics(stock_codes)
    hydrate_stats = _hydrate_missing_history(history_metrics)
    if hydrate_stats.get("success"):
        history_metrics = _load_history_metrics(stock_codes)

    latest_price_map = _load_latest_stock_price_map(stock_codes)
    try:
        risk_free = _get_risk_free_rate()
    except Exception as exc:
        return {
            "success": False,
            "error": f"treasury_yield_unavailable: {exc}",
            "updateTime": now_iso(),
            "source": "jisilu+sina",
        }

    rows: List[Dict[str, Any]] = []
    for item in raw_rows:
        stock_code = normalize_stock_code(item.get("stock_id"))
        if not stock_code:
            continue
        price_info = latest_price_map.get(stock_code) or {}
        history_info = history_metrics.get(stock_code) or {}
        source_price = to_float(item.get("price"))
        latest_price = price_info.get("price") if price_info.get("price") is not None else source_price
        raw_required_shares = to_float(item.get("apply10"))
        if raw_required_shares is None:
            ration_value = to_float(item.get("ration"))
            if ration_value and ration_value > 0:
                raw_required_shares = 1000.0 / ration_value

        rows.append({
            "bondCode": str(item.get("bond_id") or "").strip(),
            "bondName": str(item.get("bond_nm") or "").strip(),
            "stockCode": stock_code,
            "stockName": str(price_info.get("name") or item.get("stock_nm") or "").strip(),
            "market": infer_market_from_stock_code(stock_code),
            "stockPrice": latest_price,
            "stockPriceSource": "tencent" if price_info.get("price") is not None else "jisilu",
            "sourceStockPrice": source_price,
            "convertPrice": to_float(item.get("convert_price")),
            "volatility60": history_info.get("volatility60"),
            "historyCloseCount": int(history_info.get("closeCount") or 0),
            "rationPerShare": to_float(item.get("ration")),
            "apply10": to_float(item.get("apply10")),
            "rawRequiredShares": raw_required_shares,
            "recordPrice": to_float(item.get("record_price")),
            "amountYi": to_float(item.get("amount")),
            "cbAmountYi": to_float(item.get("cb_amount")),
            "progress": str(item.get("progress") or "").strip(),
            "progressName": str(item.get("progress_nm") or "").strip(),
            "progressDate": normalize_date(item.get("progress_dt")),
            "progressFull": str(item.get("progress_full") or "").strip(),
            "applyDate": normalize_date(item.get("apply_date")),
            "recordDate": normalize_date(item.get("record_dt")),
            "listDate": normalize_date(item.get("list_date")),
            "rating": str(item.get("rating_cd") or "").strip(),
            "jslAdviseText": str(item.get("jsl_advise_text") or "").strip(),
            "applyTips": str(item.get("apply_tips") or "").strip(),
            "sourceUrl": SOURCE_PAGE_URL,
            "raw": dict(item),
        })

    return {
        "success": True,
        "data": rows,
        "updateTime": now_iso(),
        "source": "jisilu+tencent+sina+akshare",
        "sourceUrl": SOURCE_PAGE_URL,
        "sourceApiUrl": SOURCE_API_URL,
        "sourceTitle": SOURCE_TITLE,
        "riskFreeRate": risk_free.get("rate"),
        "treasuryYield10y": risk_free.get("percent"),
        "treasuryYield10yDate": risk_free.get("date"),
        "treasuryYield10ySource": risk_free.get("source"),
        "hydrateStats": hydrate_stats,
    }
