#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI-SUMMARY: 可转债上游 API：集思录实时行情 + 东方财富财务数据
# 对应 INDEX.md §9 文件摘要索引


"""Jisilu convertible bond realtime data with theoretical pricing."""

from __future__ import annotations

import json
import io
import math
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import akshare as ak
import numpy as np
import pandas as pd
import requests
from shared.db import stock_price_history_db as price_db
from data_fetch.convertible_bond import cb_metrics
from shared.config.script_config import get_config
from shared.runtime.state_registry import create_state_registry

ROOT = Path(__file__).resolve().parents[2]
_CONFIG = get_config()
_STATE_REGISTRY = create_state_registry(_CONFIG)
_CB_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("convertible_bond") or {})

DEFAULT_VOL_WINDOWS = (250,)
VOL_WINDOWS = tuple(
    sorted({max(1, int(item)) for item in (_CB_FETCH_CONFIG.get("volatility_windows") or DEFAULT_VOL_WINDOWS)})
) or DEFAULT_VOL_WINDOWS
TRADING_DAYS_PER_YEAR = max(1, int(_CB_FETCH_CONFIG.get("trading_days_per_year") or 252))
PRIMARY_VOL_WINDOW = max(1, int(_CB_FETCH_CONFIG.get("primary_vol_window") or 250))
if PRIMARY_VOL_WINDOW not in VOL_WINDOWS:
    VOL_WINDOWS = tuple(sorted({*VOL_WINDOWS, PRIMARY_VOL_WINDOW}))
PRIMARY_VOLATILITY_FIELD = f"volatility{PRIMARY_VOL_WINDOW}"
LEGACY_PRIMARY_VOL_FIELD = "volatility60"
VOLATILITY_METRIC_FIELDS = tuple(dict.fromkeys([*(f"volatility{window}" for window in VOL_WINDOWS), LEGACY_PRIMARY_VOL_FIELD]))
ATR_WINDOW = max(1, int(_CB_FETCH_CONFIG.get("atr_window") or 20))
TURNOVER_AVG_WINDOWS = tuple(
    sorted({max(1, int(item)) for item in (_CB_FETCH_CONFIG.get("turnover_avg_windows") or [5, 20])})
) or (5, 20)
HISTORY_LOOKBACK_DAYS = max(120, int(_CB_FETCH_CONFIG.get("history_lookback_days") or 420))
REQUEST_TIMEOUT = max(1, int(_CB_FETCH_CONFIG.get("request_timeout_seconds") or 20))
LONG_REQUEST_TIMEOUT = max(1, int(_CB_FETCH_CONFIG.get("long_request_timeout_seconds") or 30))
MAX_VOL_SYNC_WORKERS = max(1, int(_CB_FETCH_CONFIG.get("max_vol_sync_workers") or 8))
REQUIRED_CLOSE_ROWS = max(VOL_WINDOWS) + 1
REQUIRED_HISTORY_BAR_ROWS = max(REQUIRED_CLOSE_ROWS, ATR_WINDOW + 1, max(TURNOVER_AVG_WINDOWS))
MAX_FINANCIAL_WORKERS = max(1, int(_CB_FETCH_CONFIG.get("max_financial_workers") or 10))
INLINE_HISTORY_HYDRATE_LIMIT = max(1, int(_CB_FETCH_CONFIG.get("inline_history_hydrate_limit") or 24))
AUX_CACHE_SCHEMA_VERSION = 2
FORCE_REDEEM_NOTICE_LOOKBACK_DAYS = 120
FORCE_REDEEM_DELIST_FORWARD_DAYS = 120
EASTMONEY_QUOTE_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"
MARKET_VALUE_TIMEOUT_SECONDS = 20
STOCK_SPOT_CACHE_TTL_MS = max(60_000, int(_CB_FETCH_CONFIG.get("spot_cache_ttl_ms") or 180_000))
INLINE_HISTORY_HYDRATE_ENABLED = bool(_CB_FETCH_CONFIG.get("inline_history_hydrate_enabled", False))

# Initialize cb_metrics module with config
cb_metrics.init_metrics_config(VOL_WINDOWS, PRIMARY_VOL_WINDOW, TRADING_DAYS_PER_YEAR, ATR_WINDOW)


_STOCK_SPOT_CACHE: Dict[str, Any] = {
    "expiresAt": 0,
    "data": {},
}


def _now_ts_ms() -> int:
    return int(datetime.now().timestamp() * 1000)


def _blank_volatility_metrics() -> Dict[str, Optional[float]]:
    return {field: None for field in VOLATILITY_METRIC_FIELDS}


def _with_primary_volatility_aliases(metrics: Dict[str, Optional[float]] | None) -> Dict[str, Optional[float]]:
    normalized = _blank_volatility_metrics()
    if isinstance(metrics, dict):
        normalized.update(metrics)
    primary_value = _to_float(normalized.get(PRIMARY_VOLATILITY_FIELD))
    if LEGACY_PRIMARY_VOL_FIELD != PRIMARY_VOLATILITY_FIELD and LEGACY_PRIMARY_VOL_FIELD not in {
        f"volatility{window}" for window in VOL_WINDOWS
    }:
        normalized[LEGACY_PRIMARY_VOL_FIELD] = primary_value
    return normalized


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in {"", "nan", "NaN", "nat", "NaT", "None"}:
        return True
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def _to_float(value: Any) -> Optional[float]:
    if _is_null(value):
        return None
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def _to_positive_float(value: Any) -> Optional[float]:
    num = _to_float(value)
    if num is None or num <= 0:
        return None
    return num


def _to_percent_ratio(value: Any) -> Optional[float]:
    if _is_null(value):
        return None
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        val = float(text)
    except Exception:
        return None
    if val <= 0:
        return None
    return val / 100.0 if val > 1.0 else val


def _to_date_str(value: Any) -> Optional[str]:
    if _is_null(value):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    try:
        parsed = pd.to_datetime(str(value).strip(), errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date().isoformat()
    except Exception:
        return None


def _normalize_market_value_to_yi(value: Any) -> Optional[float]:
    market_value = _to_float(value)
    if market_value is None or market_value <= 0:
        return None
    if market_value >= 100000:
        return market_value / 100000000.0
    return market_value


def _to_eastmoney_secid(stock_code: str) -> str:
    code = _to_code6(stock_code)
    if not code:
        return ""
    return f"{1 if code.startswith(('5', '6', '9')) else 0}.{code}"


def _load_stock_market_value_map_from_eastmoney(stock_codes: list[str]) -> Dict[str, Optional[float]]:
    target_codes = sorted({_to_code6(code) for code in stock_codes if _to_code6(code)})
    if not target_codes:
        return {}

    result: Dict[str, Optional[float]] = {}
    for index in range(0, len(target_codes), 80):
        batch = target_codes[index:index + 80]
        secids = [secid for secid in (_to_eastmoney_secid(code) for code in batch) if secid]
        if not secids:
            continue
        try:
            response = requests.get(
                EASTMONEY_QUOTE_URL,
                params={
                    "fltt": "2",
                    "invt": "2",
                    "fields": "f12,f21",
                    "secids": ",".join(secids),
                },
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Referer": "https://quote.eastmoney.com/",
                    "Accept": "application/json,text/plain,*/*",
                },
                timeout=MARKET_VALUE_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            continue

        for item in (((payload or {}).get("data") or {}).get("diff") or []):
            code = _to_code6(item.get("f12"))
            if not code:
                continue
            market_value_yi = _normalize_market_value_to_yi(item.get("f21"))
            if market_value_yi is not None:
                result[code] = market_value_yi
    return result


def _load_stock_market_value_map(stock_codes: list[str]) -> Dict[str, Optional[float]]:
    target_codes = {_to_code6(code) for code in stock_codes if _to_code6(code)}
    if not target_codes:
        return {}

    result: Dict[str, Optional[float]] = {}
    for fetcher in (getattr(ak, "stock_zh_a_spot_em", None), getattr(ak, "stock_zh_a_spot", None)):
        if fetcher is None:
            continue
        try:
            df = fetcher()
        except Exception:
            continue
        if df is None or df.empty:
            continue

        code_col = next((name for name in ("代码", "code", "symbol") if name in df.columns), None)
        market_value_col = next(
            (
                name
                for name in ("流通市值", "流通市值(元)", "circulating_market_value", "circulatingMarketValue")
                if name in df.columns
            ),
            None,
        )
        if not code_col or not market_value_col:
            continue

        records = df[[code_col, market_value_col]].to_dict("records")
        for record in records:
            code = _to_code6(record.get(code_col))
            if not code or code not in target_codes:
                continue
            market_value_yi = _normalize_market_value_to_yi(record.get(market_value_col))
            if market_value_yi is not None:
                result[code] = market_value_yi
        if result:
            break

    missing_codes = sorted(code for code in target_codes if code not in result)
    if missing_codes:
        result.update(_load_stock_market_value_map_from_eastmoney(missing_codes))

    return result


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


def _cb_arb_aux_cache_fallback() -> Dict[str, Any]:
    return {
        "schemaVersion": AUX_CACHE_SCHEMA_VERSION,
        "covBasicMap": {"date": "", "value": {}},
        "thsCovInfoMap": {"date": "", "value": {}},
        "pureBondMap": {"date": "", "value": {}},
        "stockMarketValueByStock": {"date": "", "value": {}},
        "historyMetricsByStock": {"date": "", "value": {}},
        "financialMetricsByStock": {"date": "", "value": {}},
        "holderInfoByStock": {"date": "", "value": {}},
        "updatedAt": None,
    }


def _read_cb_arb_aux_cache() -> Dict[str, Any]:
    raw = _STATE_REGISTRY["read"]("cb_arb_aux_cache", "cb_arb_aux_cache.json", _cb_arb_aux_cache_fallback())
    if not isinstance(raw, dict):
        return _cb_arb_aux_cache_fallback()
    if int(raw.get("schemaVersion") or 0) != AUX_CACHE_SCHEMA_VERSION:
        return _cb_arb_aux_cache_fallback()
    return raw


def _write_cb_arb_aux_cache(payload: Dict[str, Any]) -> None:
    next_payload = payload if isinstance(payload, dict) else _cb_arb_aux_cache_fallback()
    next_payload["schemaVersion"] = AUX_CACHE_SCHEMA_VERSION
    next_payload["updatedAt"] = datetime.now().isoformat()
    _STATE_REGISTRY["write"]("cb_arb_aux_cache", "cb_arb_aux_cache.json", next_payload)


def _read_cached_cb_arb_row_map() -> Dict[str, Dict[str, Any]]:
    # 这里复用最近一次成功的公开快照，只补静态/慢字段，不覆盖实时价格字段。
    cached = _STATE_REGISTRY["read"]("market_cache_cbArb", "market_cache_cbArb.json", {})
    rows = cached.get("data") if isinstance(cached, dict) else []
    if not isinstance(rows, list):
        return {}
    result: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = _to_code6(row.get("code"))
        if not code:
            continue
        result[code] = row
    return result


def _read_aux_cache_entry(cache_payload: Dict[str, Any], key: str) -> tuple[str, Dict[str, Any]]:
    entry = cache_payload.get(key) if isinstance(cache_payload, dict) else None
    if not isinstance(entry, dict):
        return "", {}
    entry_date = str(entry.get("date") or "").strip()
    entry_value = entry.get("value")
    return entry_date, entry_value if isinstance(entry_value, dict) else {}


def _load_daily_cached_map(
    cache_payload: Dict[str, Any],
    key: str,
    as_of_date: str,
    loader,
) -> Dict[str, Any]:
    # 这些映射属于慢变化辅助数据，按日缓存可以显著降低云端强刷超时风险。
    cached_date, cached_value = _read_aux_cache_entry(cache_payload, key)
    if cached_date == as_of_date and cached_value:
        return cached_value

    fresh_value: Dict[str, Any] = {}
    try:
        loaded = loader()
        if isinstance(loaded, dict):
            fresh_value = loaded
    except Exception:
        fresh_value = {}

    if fresh_value:
        cache_payload[key] = {
            "date": as_of_date,
            "value": fresh_value,
        }
        return fresh_value

    if cached_value:
        return cached_value
    return {}


def _pick_row_metrics(row: Dict[str, Any], fields: list[str]) -> Dict[str, Optional[float]]:
    return {
        field: _to_float(row.get(field))
        for field in fields
    }


def _build_cached_history_metrics_map(previous_rows: Dict[str, Dict[str, Any]], aux_cache: Dict[str, Any]) -> Dict[str, Dict[str, Optional[float]]]:
    metric_fields = [
        *VOLATILITY_METRIC_FIELDS,
        "stockAtr20",
        "stockAvgTurnoverAmount20Yi",
        "stockAvgTurnoverAmount5Yi",
    ]
    result: Dict[str, Dict[str, Optional[float]]] = {}
    _, cached_value = _read_aux_cache_entry(aux_cache, "historyMetricsByStock")
    for stock_code, metrics in cached_value.items():
        if isinstance(metrics, dict):
            result[str(stock_code).strip()] = _with_primary_volatility_aliases(_pick_row_metrics(metrics, metric_fields))
    for row in previous_rows.values():
        stock_code = _to_code6(row.get("stockCode"))
        if not stock_code:
            continue
        result[stock_code] = _with_primary_volatility_aliases(_pick_row_metrics(row, metric_fields))
    return result


def _build_cached_financial_metrics_map(previous_rows: Dict[str, Dict[str, Any]], aux_cache: Dict[str, Any]) -> Dict[str, Dict[str, Optional[float]]]:
    metric_fields = [
        "stockAvgRoe3Y",
        "stockDebtRatio",
        "stockNetAssetsYi",
        "stockInterestBearingDebtYi",
        "stockBroadCashYi",
        "stockNetDebtExposureYi",
    ]
    result: Dict[str, Dict[str, Optional[float]]] = {}
    _, cached_value = _read_aux_cache_entry(aux_cache, "financialMetricsByStock")
    for stock_code, metrics in cached_value.items():
        if isinstance(metrics, dict):
            result[str(stock_code).strip()] = _pick_row_metrics(metrics, metric_fields)
    for row in previous_rows.values():
        stock_code = _to_code6(row.get("stockCode"))
        if not stock_code:
            continue
        result[stock_code] = _pick_row_metrics(row, metric_fields)
    return result


def _build_cached_holder_info_map(previous_rows: Dict[str, Dict[str, Any]], aux_cache: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    text_fields = ["holderCountReportPeriod", "holderCountReportSourceUrl", "holderCountLastCheckedAt"]
    number_fields = ["holderCount"]
    bool_fields = ["holderCountFallbackUsed"]
    result: Dict[str, Dict[str, Any]] = {}
    _, cached_value = _read_aux_cache_entry(aux_cache, "holderInfoByStock")
    for stock_code, metrics in cached_value.items():
        if not isinstance(metrics, dict):
            continue
        payload: Dict[str, Any] = {}
        for field in text_fields:
            text = str(metrics.get(field) or "").strip()
            payload[field] = text or None
        for field in number_fields:
            payload[field] = _to_float(metrics.get(field))
        for field in bool_fields:
            payload[field] = metrics.get(field) is True
        result[str(stock_code).strip()] = payload
    for row in previous_rows.values():
        stock_code = _to_code6(row.get("stockCode"))
        if not stock_code:
            continue
        payload = {
            "holderCount": _to_float(row.get("holderCount")),
            "holderCountReportPeriod": str(row.get("holderCountReportPeriod") or "").strip() or None,
            "holderCountReportSourceUrl": str(row.get("holderCountReportSourceUrl") or "").strip() or None,
            "holderCountFallbackUsed": row.get("holderCountFallbackUsed") is True,
            "holderCountLastCheckedAt": str(row.get("holderCountLastCheckedAt") or "").strip() or None,
        }
        result[stock_code] = payload
    return result


def _persist_runtime_metric_cache(
    aux_cache: Dict[str, Any],
    as_of_date: str,
    rows: list[Dict[str, Any]],
) -> None:
    history_metrics_by_stock: Dict[str, Dict[str, Optional[float]]] = {}
    _, cached_financial_value = _read_aux_cache_entry(aux_cache, "financialMetricsByStock")
    _, cached_holder_value = _read_aux_cache_entry(aux_cache, "holderInfoByStock")
    financial_metrics_by_stock: Dict[str, Dict[str, Optional[float]]] = {
        str(stock_code).strip(): _pick_row_metrics(metrics, [
            "stockAvgRoe3Y",
            "stockDebtRatio",
            "stockNetAssetsYi",
            "stockInterestBearingDebtYi",
            "stockBroadCashYi",
            "stockNetDebtExposureYi",
        ])
        for stock_code, metrics in (cached_financial_value or {}).items()
        if isinstance(metrics, dict)
    }
    holder_info_by_stock: Dict[str, Dict[str, Any]] = {
        str(stock_code).strip(): {
            "holderCount": _to_float(metrics.get("holderCount")),
            "holderCountReportPeriod": str(metrics.get("holderCountReportPeriod") or "").strip() or None,
            "holderCountReportSourceUrl": str(metrics.get("holderCountReportSourceUrl") or "").strip() or None,
            "holderCountFallbackUsed": metrics.get("holderCountFallbackUsed") is True,
            "holderCountLastCheckedAt": str(metrics.get("holderCountLastCheckedAt") or "").strip() or None,
        }
        for stock_code, metrics in (cached_holder_value or {}).items()
        if isinstance(metrics, dict)
    }
    for row in rows:
        stock_code = _to_code6(row.get("stockCode"))
        if not stock_code:
            continue
        history_metrics_by_stock[stock_code] = _pick_row_metrics(row, [
            *VOLATILITY_METRIC_FIELDS,
            "stockAtr20",
            "stockAvgTurnoverAmount20Yi",
            "stockAvgTurnoverAmount5Yi",
        ])
        current_financial = financial_metrics_by_stock.get(stock_code) if isinstance(financial_metrics_by_stock.get(stock_code), dict) else {}
        next_financial = {**current_financial}
        for field in [
            "stockAvgRoe3Y",
            "stockDebtRatio",
            "stockNetAssetsYi",
            "stockInterestBearingDebtYi",
            "stockBroadCashYi",
            "stockNetDebtExposureYi",
        ]:
            value = _to_float(row.get(field))
            if value is not None:
                next_financial[field] = value
        financial_metrics_by_stock[stock_code] = next_financial

        current_holder = holder_info_by_stock.get(stock_code) if isinstance(holder_info_by_stock.get(stock_code), dict) else {}
        next_holder = {**current_holder}
        holder_count = _to_positive_float(row.get("holderCount"))
        if holder_count is not None:
            next_holder["holderCount"] = int(round(holder_count))
        report_period = str(row.get("holderCountReportPeriod") or "").strip()
        if report_period:
            next_holder["holderCountReportPeriod"] = report_period
        report_source_url = str(row.get("holderCountReportSourceUrl") or "").strip()
        if report_source_url:
            next_holder["holderCountReportSourceUrl"] = report_source_url
        if any((holder_count is not None, report_period, report_source_url)):
            next_holder["holderCountFallbackUsed"] = row.get("holderCountFallbackUsed") is True
        checked_at = str(row.get("holderCountLastCheckedAt") or "").strip()
        if checked_at:
            next_holder["holderCountLastCheckedAt"] = checked_at
        holder_info_by_stock[stock_code] = next_holder

    aux_cache["historyMetricsByStock"] = {
        "date": as_of_date,
        "value": history_metrics_by_stock,
    }
    aux_cache["financialMetricsByStock"] = {
        "date": as_of_date,
        "value": financial_metrics_by_stock,
    }
    aux_cache["holderInfoByStock"] = {
        "date": as_of_date,
        "value": holder_info_by_stock,
    }
    _write_cb_arb_aux_cache(aux_cache)


def _derive_remaining_years(row: Dict[str, Any], as_of: date) -> Optional[float]:
    explicit_years = _to_float(row.get("remainingYears"))
    if explicit_years is not None and explicit_years >= 0:
        return explicit_years

    maturity = _to_date_str(row.get("maturityDate"))
    if not maturity:
        return None

    try:
        maturity_date = datetime.fromisoformat(maturity).date()
    except Exception:
        return None

    delta_days = (maturity_date - as_of).days
    return max(delta_days, 0) / 365.0


def _to_date_obj(value: Any) -> Optional[date]:
    text = _to_date_str(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).date()
    except Exception:
        return None


def _derive_force_redeem_status(row: Dict[str, Any], as_of: date) -> Dict[str, Optional[str]]:
    notice_dates = [
        dt for dt in (
            _to_date_obj(row.get("redeemNoticeDateSh")),
            _to_date_obj(row.get("redeemNoticeDateHs")),
        )
        if dt is not None
    ]
    latest_notice = max(notice_dates) if notice_dates else None
    delist_dt = _to_date_obj(row.get("delistDate"))

    if latest_notice and delist_dt and delist_dt <= as_of:
        return {
            "forceRedeemStatus": "已完成强赎",
            "forceRedeemNoticeDate": latest_notice.isoformat(),
        }

    if delist_dt:
        delist_gap = (delist_dt - as_of).days
        if 0 <= delist_gap <= FORCE_REDEEM_DELIST_FORWARD_DAYS:
            return {
                "forceRedeemStatus": "强赎进行中",
                "forceRedeemNoticeDate": latest_notice.isoformat() if latest_notice else None,
            }

    if latest_notice:
        notice_gap = (as_of - latest_notice).days
        if 0 <= notice_gap <= FORCE_REDEEM_NOTICE_LOOKBACK_DAYS:
            return {
                "forceRedeemStatus": "已公告强赎",
                "forceRedeemNoticeDate": latest_notice.isoformat(),
            }

    return {
        "forceRedeemStatus": None,
        "forceRedeemNoticeDate": None,
    }


def _recompute_live_convert_metrics(row: Dict[str, Any]) -> None:
    # 实时口径强制收敛到“正股现价 + 转股价”两项真值，避免上游错误字段或旧缓存污染转股价值。
    stock_price = _to_float(row.get("stockPrice"))
    convert_price = _to_positive_float(row.get("convertPrice"))
    price = _to_float(row.get("price"))

    if stock_price is not None and convert_price is not None:
        row["convertValue"] = (stock_price * 100.0) / convert_price
    else:
        row["convertValue"] = None

    convert_value = _to_positive_float(row.get("convertValue"))
    if price is not None and convert_value is not None:
        row["premiumRate"] = ((price / convert_value) - 1.0) * 100.0
    else:
        row["premiumRate"] = None

    premium_rate = _to_float(row.get("premiumRate"))
    row["doubleLow"] = (price + premium_rate) if (price is not None and premium_rate is not None) else None


def _should_exclude_bond_by_name(name: Any) -> bool:
    text = str(name or "").strip()
    if not text:
        return False
    return "\u9000" in text


def _to_tx_symbol(stock_code: str) -> str:
    code = str(stock_code or "").strip()
    if not code:
        return ""
    market = "sh" if code.startswith(("5", "6", "9")) else "sz"
    return f"{market}{code}"


def _to_em_stock_symbol(stock_code: str) -> str:
    code = _to_code6(stock_code)
    if not code:
        return ""
    if code.startswith(("4", "8")):
        return f"BJ{code}"
    if code.startswith(("5", "6", "9")):
        return f"SH{code}"
    return f"SZ{code}"


def _format_report_period(period: str) -> Optional[str]:
    text = str(period or "").strip()
    if not re.fullmatch(r"\d{8}", text):
        return None
    return f"{text[:4]}-{text[4:6]}-{text[6:]}"


def _recent_holder_report_periods(as_of: date, count: int = 8) -> list[str]:
    result: list[str] = []
    for year in range(as_of.year, as_of.year - 5, -1):
        for month, day in ((12, 31), (6, 30)):
            report_date = date(year, month, day)
            if report_date > as_of:
                continue
            result.append(report_date.strftime("%Y%m%d"))
            if len(result) >= count:
                return result
    return result


def _current_holder_update_window(as_of: date) -> tuple[Optional[str], Optional[date], Optional[date]]:
    if (as_of.month, as_of.day) >= (1, 1) and (as_of.month, as_of.day) <= (4, 30):
        return f"{as_of.year - 1}-12-31", date(as_of.year, 1, 1), date(as_of.year, 4, 30)
    if (as_of.month, as_of.day) >= (7, 1) and (as_of.month, as_of.day) <= (8, 31):
        return f"{as_of.year}-06-30", date(as_of.year, 7, 1), date(as_of.year, 8, 31)
    return None, None, None


def _should_refresh_holder_info(cached: Dict[str, Any], as_of: date) -> bool:
    cached_holder_count = _to_positive_float((cached or {}).get("holderCount"))
    cached_period = str((cached or {}).get("holderCountReportPeriod") or "").strip() or None
    last_checked_at_text = str((cached or {}).get("holderCountLastCheckedAt") or "").strip()
    if cached_holder_count is None or not cached_period:
        return True

    target_period, window_start, window_end = _current_holder_update_window(as_of)
    if not target_period or not window_start or not window_end:
        return False
    if cached_period == target_period:
        return False

    last_checked_date = _to_date_obj(last_checked_at_text)
    if last_checked_date is None:
        return True
    if last_checked_date < window_start:
        return True
    if last_checked_date > window_end:
        return True
    return (as_of - last_checked_date).days >= 7


@lru_cache(maxsize=1)
def _load_cninfo_stock_orgid_map() -> Dict[str, str]:
    try:
        payload = requests.get(
            "https://www.cninfo.com.cn/new/data/szse_stock.json",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.cninfo.com.cn/"},
            timeout=REQUEST_TIMEOUT,
        ).json()
    except Exception:
        return {}
    stock_list = (payload or {}).get("stockList") or []
    result: Dict[str, str] = {}
    for item in stock_list:
        code = _to_code6((item or {}).get("code"))
        org_id = str((item or {}).get("orgId") or "").strip()
        if code and org_id:
            result[code] = org_id
    return result


def _pick_cninfo_regular_report_announcement(announcements: list[Dict[str, Any]], period: str) -> Optional[Dict[str, Any]]:
    if not announcements:
        return None
    year = period[:4]
    suffix = period[4:]
    preferred_keywords = [f"{year}年年度报告"] if suffix == "1231" else [f"{year}年半年度报告"]
    preferred: list[Dict[str, Any]] = []
    fallback: list[Dict[str, Any]] = []
    for item in announcements:
        title = str((item or {}).get("announcementTitle") or "").strip()
        if not title:
            continue
        if "摘要" in title:
            fallback.append(item)
            continue
        if any(keyword in title for keyword in preferred_keywords):
            preferred.append(item)
        else:
            fallback.append(item)
    ordered = preferred or fallback
    return ordered[0] if ordered else None


@lru_cache(maxsize=256)
def _fetch_cninfo_regular_reports(stock_code: str, as_of_date_text: str) -> list[Dict[str, Any]]:
    code = _to_code6(stock_code)
    if not code:
        return []
    org_id = _load_cninfo_stock_orgid_map().get(code)
    if not org_id:
        return []
    try:
        response = requests.post(
            "https://www.cninfo.com.cn/new/hisAnnouncement/query",
            data={
                "pageNum": "1",
                "pageSize": "12",
                "column": "szse",
                "tabName": "fulltext",
                "plate": "",
                "stock": f"{code},{org_id}",
                "searchkey": "",
                "secid": "",
                "category": "category_ndbg_szsh;category_bndbg_szsh;",
                "trade": "",
                "seDate": f"{max(int(as_of_date_text[:4]) - 3, 2017)}-01-01~{as_of_date_text}",
                "sortName": "time",
                "sortType": "desc",
                "isHLtitle": "true",
            },
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
            },
            timeout=REQUEST_TIMEOUT,
        )
        announcements = (response.json() or {}).get("announcements") or []
    except Exception:
        return []

    rows: list[Dict[str, Any]] = []
    for item in announcements:
        title = str((item or {}).get("announcementTitle") or "").strip()
        if not title or "摘要" in title or "英文" in title or "取消" in title:
            continue
        period: Optional[str] = None
        annual_hit = re.search(r"(\d{4})年年度报告", title)
        semi_hit = re.search(r"(\d{4})年半年度报告", title)
        if annual_hit:
            period = f"{annual_hit.group(1)}-12-31"
        elif semi_hit:
            period = f"{semi_hit.group(1)}-06-30"
        if not period:
            continue
        adjunct_url = str((item or {}).get("adjunctUrl") or "").strip()
        rows.append({
            "title": title,
            "period": period,
            "announcementTime": int((item or {}).get("announcementTime") or 0),
            "reportSourceUrl": f"https://static.cninfo.com.cn/{adjunct_url.lstrip('/')}" if adjunct_url else None,
        })
    rows.sort(key=lambda item: (item.get("period") or "", int(item.get("announcementTime") or 0)), reverse=True)
    return rows


@lru_cache(maxsize=256)
def _fetch_cninfo_regular_report_url(stock_code: str, period: str) -> Optional[str]:
    code = _to_code6(stock_code)
    formatted_period = _format_report_period(period)
    if not code or not formatted_period:
        return None
    org_id = _load_cninfo_stock_orgid_map().get(code)
    if not org_id:
        return None

    category = "category_ndbg_szsh" if period.endswith("1231") else "category_bndbg_szsh"
    try:
        response = requests.post(
            "https://www.cninfo.com.cn/new/hisAnnouncement/query",
            data={
                "pageNum": "1",
                "pageSize": "30",
                "column": "szse",
                "tabName": "fulltext",
                "plate": "",
                "stock": f"{code},{org_id}",
                "searchkey": "",
                "secid": "",
                "category": category,
                "trade": "",
                "seDate": f"{formatted_period}~{datetime.now().date().isoformat()}",
                "sortName": "",
                "sortType": "",
                "isHLtitle": "true",
            },
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search",
            },
            timeout=REQUEST_TIMEOUT,
        )
        announcements = (response.json() or {}).get("announcements") or []
    except Exception:
        return None

    picked = _pick_cninfo_regular_report_announcement(announcements, period)
    if not picked:
        return None
    adjunct_url = str((picked or {}).get("adjunctUrl") or "").strip()
    if adjunct_url:
        return f"https://static.cninfo.com.cn/{adjunct_url.lstrip('/')}"
    announcement_id = str((picked or {}).get("announcementId") or "").strip()
    if not announcement_id:
        return None
    return f"https://www.cninfo.com.cn/new/disclosure/detail?stockCode={code}&announcementId={announcement_id}&orgId={org_id}"


def _normalize_report_text(text: str) -> str:
    return re.sub(r"\s+", "", str(text or ""))


def _extract_integer_from_text(text: str) -> Optional[int]:
    digits = re.sub(r"[^\d]", "", str(text or ""))
    if not digits:
        return None
    try:
        value = int(digits)
    except Exception:
        return None
    return value if value > 0 else None


def _extract_holder_count_from_report_text(text: str) -> Optional[int]:
    normalized = _normalize_report_text(text)
    if not normalized:
        return None
    primary_patterns = [
        r"报告期(?:可)?转债持有人及担保人情况.*?期末(?:可)?转债持有人数[^0-9]{0,80}([0-9,，]+)",
        r"可转换公司债券名称期末(?:可)?转债持有人数[^0-9]{0,80}([0-9,，]+)",
        r"期末可转债持有人数(?:（户）|\(户\)|户)?[:：]?(?:为)?([\d,，]+)",
        r"期末转债持有人数(?:（户）|\(户\)|户)?[:：]?(?:为)?([\d,，]+)",
        r"截至报告期末可转债持有人数(?:（户）|\(户\)|户)?[:：]?(?:为)?([\d,，]+)",
        r"截至报告期末转债持有人数(?:（户）|\(户\)|户)?[:：]?(?:为)?([\d,，]+)",
    ]
    for pattern in primary_patterns:
        hit = re.search(pattern, normalized)
        if not hit:
            continue
        value = _extract_integer_from_text(hit.group(1))
        if value is not None:
            return value

    for keyword in ("可转债持有人数", "转债持有人数", "可转换公司债券持有人数"):
        for hit in re.finditer(keyword, normalized):
            window = normalized[max(0, hit.start() - 20):hit.start() + 80]
            if "披露日前一个月末" in window:
                continue
            number_hit = re.search(r"(?:（户）|\(户\)|户)?[:：]?(?:为)?([\d,，]+)", window)
            if not number_hit:
                continue
            value = _extract_integer_from_text(number_hit.group(1))
            if value is not None:
                return value
    return None


def _extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        return ""
    try:
        import pdfplumber

        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception:
        pass
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def _extract_holder_count_from_pdf_bytes(pdf_bytes: bytes) -> Optional[int]:
    if not pdf_bytes:
        return None
    try:
        from pdfminer.high_level import extract_pages
        from pdfminer.layout import LTTextContainer

        rolling_text = ""
        for layout in extract_pages(io.BytesIO(pdf_bytes)):
            page_text_parts: list[str] = []
            for element in layout:
                if isinstance(element, LTTextContainer):
                    page_text_parts.append(element.get_text())
            page_text = "".join(page_text_parts)
            if not page_text:
                continue
            candidate_text = f"{rolling_text}\n{page_text}"
            if any(keyword in candidate_text for keyword in (
                "报告期转债持有人及担保人情况",
                "报告期可转债持有人及担保人情况",
                "期末转债持有人数",
                "期末可转债持有人数",
                "可转换公司债券",
                "闻泰转债",
            )):
                value = _extract_holder_count_from_report_text(candidate_text)
                if value is not None:
                    return value
            rolling_text = candidate_text[-6000:]
    except Exception:
        pass

    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(pdf_bytes))
        rolling_text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if not page_text:
                continue
            candidate_text = f"{rolling_text}\n{page_text}"
            if any(keyword in candidate_text for keyword in (
                "报告期转债持有人及担保人情况",
                "报告期可转债持有人及担保人情况",
                "期末转债持有人数",
                "期末可转债持有人数",
                "可转换公司债券",
            )):
                value = _extract_holder_count_from_report_text(candidate_text)
                if value is not None:
                    return value
            rolling_text = candidate_text[-6000:]
    except Exception:
        pass

    return _extract_holder_count_from_report_text(_extract_text_from_pdf_bytes(pdf_bytes))


@lru_cache(maxsize=256)
def _extract_holder_count_from_cninfo_pdf(report_url: str) -> Optional[int]:
    url = str(report_url or "").strip()
    if not url:
        return None
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.cninfo.com.cn/"},
            timeout=LONG_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except Exception:
        return None
    return _extract_holder_count_from_pdf_bytes(response.content)


def _fetch_holder_info_for_stock(stock_code: str, as_of: date) -> Dict[str, Any]:
    code = _to_code6(stock_code)
    if not code:
        return {
            "holderCount": None,
            "holderCountReportPeriod": None,
            "holderCountReportSourceUrl": None,
            "holderCountFallbackUsed": False,
        }
    report_rows = _fetch_cninfo_regular_reports(code, as_of.isoformat())
    if not report_rows:
        return {
            "holderCount": None,
            "holderCountReportPeriod": None,
            "holderCountReportSourceUrl": None,
            "holderCountFallbackUsed": False,
            "holderCountLastCheckedAt": as_of.isoformat(),
        }
    latest_period = str((report_rows[0] or {}).get("period") or "").strip() or None
    for report in report_rows:
        report_period = str(report.get("period") or "").strip() or None
        report_url = str(report.get("reportSourceUrl") or "").strip() or None
        if not report_period or not report_url:
            continue
        holder_count = _extract_holder_count_from_cninfo_pdf(report_url)
        if holder_count is None:
            continue
        return {
            "holderCount": holder_count,
            "holderCountReportPeriod": report_period,
            "holderCountReportSourceUrl": report_url,
            "holderCountFallbackUsed": latest_period is not None and report_period != latest_period,
            "holderCountLastCheckedAt": as_of.isoformat(),
        }
    return {
        "holderCount": None,
        "holderCountReportPeriod": None,
        "holderCountReportSourceUrl": None,
        "holderCountFallbackUsed": False,
        "holderCountLastCheckedAt": as_of.isoformat(),
    }


def _sum_positive_balance_fields(record: Dict[str, Any], fields: list[str]) -> Optional[float]:
    values: list[float] = []
    for field in fields:
        value = _to_positive_float(record.get(field))
        if value is not None:
            values.append(value)
    if not values:
        return None
    return float(sum(values))


def _sort_balance_sheet(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    frame = df.copy()
    for field in ("REPORT_DATE", "NOTICE_DATE"):
        if field in frame.columns:
            frame[field] = pd.to_datetime(frame[field], errors="coerce")
    sort_fields = [field for field in ("REPORT_DATE", "NOTICE_DATE") if field in frame.columns]
    if sort_fields:
        frame = frame.sort_values(by=sort_fields, ascending=False, na_position="last")
    return frame


def _extract_balance_sheet_financial_metrics(df: pd.DataFrame) -> Dict[str, Optional[float]]:
    if df is None or df.empty:
        return {
            "stockNetAssetsYi": None,
            "stockInterestBearingDebtYi": None,
            "stockBroadCashYi": None,
            "stockNetDebtExposureYi": None,
        }
    frame = _sort_balance_sheet(df)
    if frame.empty:
        return {
            "stockNetAssetsYi": None,
            "stockInterestBearingDebtYi": None,
            "stockBroadCashYi": None,
            "stockNetDebtExposureYi": None,
        }
    record = frame.iloc[0].to_dict()
    broad_cash_fields = [
        "MONETARYFUNDS",
        "TRADE_FINASSET",
        "TRADE_FINASSET_NOTFVTPL",
        "FVTPL_FINASSET",
        "APPOINT_FVTPL_FINASSET",
        "DERIVE_FINASSET",
        "CREDITOR_INVEST",
        "OTHER_CREDITOR_INVEST",
        "AMORTIZE_COST_FINASSET",
        "AMORTIZE_COST_NCFINASSET",
        "FVTOCI_FINASSET",
        "FVTOCI_NCFINASSET",
        "OTHER_NONCURRENT_FINASSET",
    ]
    interest_bearing_debt_fields = [
        "SHORT_LOAN",
        "BORROW_FUND",
        "SHORT_BOND_PAYABLE",
        "LONG_LOAN",
        "BOND_PAYABLE",
        "SUBBOND_PAYABLE",
        "LEASE_LIAB",
        "LONG_PAYABLE",
        "PREFERRED_SHARES_PAYBALE",
        "PERPETUAL_BOND_PAYBALE",
    ]
    net_assets = _to_positive_float(record.get("TOTAL_EQUITY")) or _to_positive_float(record.get("TOTAL_PARENT_EQUITY"))
    broad_cash = _sum_positive_balance_fields(record, broad_cash_fields)
    interest_bearing_debt = _sum_positive_balance_fields(record, interest_bearing_debt_fields)
    return {
        "stockNetAssetsYi": round(net_assets / 100000000.0, 4) if net_assets is not None else None,
        "stockInterestBearingDebtYi": round(interest_bearing_debt / 100000000.0, 4) if interest_bearing_debt is not None else None,
        "stockBroadCashYi": round(broad_cash / 100000000.0, 4) if broad_cash is not None else None,
        "stockNetDebtExposureYi": round((interest_bearing_debt - broad_cash) / 100000000.0, 4)
        if interest_bearing_debt is not None and broad_cash is not None
        else None,
    }


def _fetch_small_redemption_financial_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    symbol = _to_em_stock_symbol(stock_code)
    if not symbol:
        return {
            "stockNetAssetsYi": None,
            "stockInterestBearingDebtYi": None,
            "stockBroadCashYi": None,
            "stockNetDebtExposureYi": None,
        }
    fetchers = [
        getattr(ak, "stock_balance_sheet_by_report_em", None),
        getattr(ak, "stock_balance_sheet_by_report_delisted_em", None),
    ]
    for fetcher in fetchers:
        if fetcher is None:
            continue
        try:
            df = fetcher(symbol=symbol)
        except Exception:
            continue
        metrics = _extract_balance_sheet_financial_metrics(df)
        if any(value is not None for value in metrics.values()):
            return metrics
    return {
        "stockNetAssetsYi": None,
        "stockInterestBearingDebtYi": None,
        "stockBroadCashYi": None,
        "stockNetDebtExposureYi": None,
    }


def _extract_hfq_rows(frame: pd.DataFrame, *, include_amount: bool) -> list[Dict[str, Any]]:
    if frame is None or frame.empty:
        return []

    date_col = next((name for name in ("\u65e5\u671f", "date") if name in frame.columns), None)
    close_col = next((name for name in ("\u6536\u76d8", "close") if name in frame.columns), None)
    high_col = next((name for name in ("\u6700\u9ad8", "high") if name in frame.columns), None)
    low_col = next((name for name in ("\u6700\u4f4e", "low") if name in frame.columns), None)
    amount_col = next((name for name in ("\u6210\u4ea4\u989d", "amount") if name in frame.columns), None)
    if not date_col or not close_col:
        return []

    rows: list[Dict[str, Any]] = []
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
        close_value = float(close)
        if close_value <= 0:
            continue
        rows.append({
            "date": trade_date.date().isoformat(),
            "close": close_value,
            "high": float(high) if high is not None and not pd.isna(high) and float(high) > 0 else None,
            "low": float(low) if low is not None and not pd.isna(low) and float(low) > 0 else None,
            "amount": float(amount) if amount is not None and not pd.isna(amount) and float(amount) >= 0 else None,
        })
    return rows


def _fetch_stock_hfq_rows(symbol: str, start_date: str, end_date: str) -> list[Dict[str, Any]]:
    try:
        frame = ak.stock_zh_a_daily(
            symbol=_to_tx_symbol(symbol),
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        rows = _extract_hfq_rows(frame, include_amount=True)
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
        rows = _extract_hfq_rows(frame, include_amount=False)
        if rows:
            return rows
    except Exception:
        pass

    try:
        frame = ak.stock_zh_a_hist(
            symbol=str(symbol),
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="hfq",
        )
        return _extract_hfq_rows(frame, include_amount=True)
    except Exception:
        return []


def _sync_stock_history_if_needed(symbol: str) -> Dict[str, Any]:
    code = str(symbol or "").strip()
    if not code:
        return {"symbol": code, "synced": False, "rows": 0}

    existing_metrics = _calc_stock_history_metrics(code)
    if _metrics_ready(existing_metrics):
        return {"symbol": code, "synced": False, "rows": 0}

    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=HISTORY_LOOKBACK_DAYS)).strftime("%Y%m%d")
    rows = _fetch_stock_hfq_rows(code, start_date, end_date)
    if not rows:
        return {"symbol": code, "synced": False, "rows": 0}
    written = int(price_db.upsert_price_rows(code, rows, "akshare_hfq_fallback") or 0)
    return {"symbol": code, "synced": written > 0, "rows": written}


def _hydrate_stock_history_for_symbols(symbols: list[str]) -> Dict[str, int]:
    targets = sorted({str(symbol or "").strip() for symbol in symbols if str(symbol or "").strip()})
    if not targets:
        return {"requested": 0, "syncedSymbols": 0, "writtenRows": 0}

    synced_symbols = 0
    written_rows = 0
    with ThreadPoolExecutor(max_workers=min(MAX_VOL_SYNC_WORKERS, max(1, len(targets)))) as executor:
        future_map = {executor.submit(_sync_stock_history_if_needed, symbol): symbol for symbol in targets}
        for future in as_completed(future_map):
            try:
                payload = future.result()
            except Exception:
                payload = {"synced": False, "rows": 0}
            if payload.get("synced"):
                synced_symbols += 1
            written_rows += int(payload.get("rows") or 0)
    return {"requested": len(targets), "syncedSymbols": synced_symbols, "writtenRows": written_rows}


def _pick_col(columns: list[str], candidates: list[str]) -> Optional[str]:
    for name in candidates:
        if name in columns:
            return name
    return None


def _extract_stock_financial_metrics(df: pd.DataFrame) -> Dict[str, Optional[float]]:
    if df is None or df.empty:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}

    columns = [str(col) for col in df.columns]
    roe_col = _pick_col(columns, ["净资产收益率", "净资产收益率-摊薄", "ROE", "roe"])
    debt_col = _pick_col(columns, ["资产负债率", "debt_ratio", "debtRatio"])
    if not roe_col and not debt_col:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}

    records = df.to_dict("records")
    roe_values: list[float] = []
    debt_ratio: Optional[float] = None
    for record in reversed(records):
        if debt_ratio is None and debt_col:
            debt_ratio = _to_float(record.get(debt_col))
        if roe_col and len(roe_values) < 3:
            roe = _to_float(record.get(roe_col))
            if roe is not None:
                roe_values.append(roe)
        if debt_ratio is not None and len(roe_values) >= 3:
            break

    roe_avg = (sum(roe_values) / len(roe_values)) if len(roe_values) >= 3 else None
    return {
        "stockAvgRoe3Y": round(float(roe_avg), 4) if roe_avg is not None else None,
        "stockDebtRatio": round(float(debt_ratio), 4) if debt_ratio is not None else None,
    }


def _fetch_stock_financial_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    code = str(stock_code or "").strip()
    if not code:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}

    try:
        df = ak.stock_financial_abstract_ths(symbol=code, indicator="按报告期")
        metrics = _extract_stock_financial_metrics(df)
        if metrics.get("stockAvgRoe3Y") is not None or metrics.get("stockDebtRatio") is not None:
            return metrics
    except Exception:
        pass

    try:
        df = ak.stock_financial_abstract(symbol=code)
    except Exception:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}
    if df is None or df.empty:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}

    # 新浪接口是横向报表，取最新一期列做当前资产负债率，近三年列做ROE均值。
    time_cols = [col for col in df.columns if re.fullmatch(r"\d{8}", str(col))]
    if not time_cols:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}
    time_cols = sorted(time_cols)
    indicator_col = "指标" if "指标" in df.columns else None
    if indicator_col is None:
        return {"stockAvgRoe3Y": None, "stockDebtRatio": None}

    roe_row = df[df[indicator_col].astype(str).str.contains("净资产收益率", na=False)]
    debt_row = df[df[indicator_col].astype(str).str.contains("资产负债率", na=False)]

    roe_values: list[float] = []
    if not roe_row.empty:
        series = roe_row.iloc[0]
        for col in reversed(time_cols):
            value = _to_float(series.get(col))
            if value is None:
                continue
            roe_values.append(value)
            if len(roe_values) >= 3:
                break

    debt_ratio = None
    if not debt_row.empty:
        series = debt_row.iloc[0]
        for col in reversed(time_cols):
            debt_ratio = _to_float(series.get(col))
            if debt_ratio is not None:
                break

    roe_avg = (sum(roe_values) / len(roe_values)) if len(roe_values) >= 3 else None
    return {
        "stockAvgRoe3Y": round(float(roe_avg), 4) if roe_avg is not None else None,
        "stockDebtRatio": round(float(debt_ratio), 4) if debt_ratio is not None else None,
    }


@lru_cache(maxsize=8)
def _fetch_em_annual_roe_map(report_date: str) -> Dict[str, Optional[float]]:
    fetcher = getattr(ak, "stock_yjbb_em", None)
    if fetcher is None:
        return {}
    try:
        df = fetcher(date=report_date)
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    code_col = _pick_col(list(df.columns), ["股票代码", "证券代码"])
    roe_col = _pick_col(list(df.columns), ["净资产收益率"])
    if not code_col or not roe_col:
        return {}

    result: Dict[str, Optional[float]] = {}
    for _, record in df.iterrows():
        code = _to_code6(record.get(code_col))
        if not code:
            continue
        result[code] = _to_float(record.get(roe_col))
    return result


@lru_cache(maxsize=8)
def _fetch_em_debt_ratio_map(report_date: str) -> Dict[str, Optional[float]]:
    fetcher = getattr(ak, "stock_zcfz_em", None)
    if fetcher is None:
        return {}
    try:
        df = fetcher(date=report_date)
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    code_col = _pick_col(list(df.columns), ["股票代码", "证券代码"])
    debt_col = _pick_col(list(df.columns), ["资产负债率"])
    if not code_col or not debt_col:
        return {}

    result: Dict[str, Optional[float]] = {}
    for _, record in df.iterrows():
        code = _to_code6(record.get(code_col))
        if not code:
            continue
        result[code] = _to_float(record.get(debt_col))
    return result


def _recent_annual_report_dates(as_of: date, count: int = 6) -> list[str]:
    result: list[str] = []
    for year in range(as_of.year, as_of.year - 8, -1):
        report_date = date(year, 12, 31)
        if report_date <= as_of:
            result.append(report_date.strftime("%Y%m%d"))
        if len(result) >= count:
            break
    return result


def _recent_report_dates(as_of: date, count: int = 8) -> list[str]:
    quarter_ends = ((12, 31), (9, 30), (6, 30), (3, 31))
    result: list[str] = []
    for year in range(as_of.year, as_of.year - 3, -1):
        for month, day in quarter_ends:
            report_date = date(year, month, day)
            if report_date > as_of:
                continue
            result.append(report_date.strftime("%Y%m%d"))
            if len(result) >= count:
                return result
    return result


def _build_em_financial_metrics_map(stock_codes: list[str], as_of: date) -> Dict[str, Dict[str, Optional[float]]]:
    targets = sorted({_to_code6(code) for code in stock_codes if _to_code6(code)})
    if not targets:
        return {}

    result: Dict[str, Dict[str, Optional[float]]] = {
        code: {"stockAvgRoe3Y": None, "stockDebtRatio": None}
        for code in targets
    }

    annual_dates = _recent_annual_report_dates(as_of)
    debt_dates = _recent_report_dates(as_of)

    roe_history: Dict[str, list[float]] = {code: [] for code in targets}
    for report_date in annual_dates:
        roe_map = _fetch_em_annual_roe_map(report_date)
        if not roe_map:
            continue
        for code in targets:
            if len(roe_history[code]) >= 3:
                continue
            value = _to_float(roe_map.get(code))
            if value is not None:
                roe_history[code].append(value)
        if all(len(values) >= 3 for values in roe_history.values()):
            break

    for code, values in roe_history.items():
        if len(values) >= 3:
            result[code]["stockAvgRoe3Y"] = round(sum(values[:3]) / 3.0, 4)

    pending_debt_codes = {code for code in targets}
    for report_date in debt_dates:
        debt_map = _fetch_em_debt_ratio_map(report_date)
        if not debt_map:
            continue
        resolved_now = set()
        for code in pending_debt_codes:
            value = _to_float(debt_map.get(code))
            if value is None:
                continue
            result[code]["stockDebtRatio"] = round(value, 4)
            resolved_now.add(code)
        pending_debt_codes -= resolved_now
        if not pending_debt_codes:
            break

    return result


def _extract_percent_values(text: Any) -> list[float]:
    return cb_metrics._extract_percent_values(text)


def _derive_resale_trigger_ratio(row: Dict[str, Any]) -> Optional[float]:
    result = cb_metrics._derive_resale_trigger_ratio(row)
    if result is not None:
        return result

    ratio = _to_percent_ratio(row.get("putbackTriggerRatio"))
    if ratio is not None:
        return ratio

    clause = str(row.get("resaleClause") or "")
    if not clause:
        return None

    targeted_patterns = [
        r"低于[^。；\n]{0,50}?(\d+(?:\.\d+)?)\s*%",
        r"不足[^。；\n]{0,50}?(\d+(?:\.\d+)?)\s*%",
    ]
    for pattern in targeted_patterns:
        hit = re.search(pattern, clause)
        if not hit:
            continue
        value = _to_float(hit.group(1))
        if value is not None and 20.0 <= value <= 95.0:
            return value / 100.0

    percent_values = [value for value in cb_metrics._extract_percent_values(clause) if 20.0 <= value <= 95.0]
    if not percent_values:
        return None
    return min(percent_values) / 100.0


def _resolve_putback_trigger_price(row: Dict[str, Any]) -> tuple[Optional[float], str]:
    direct = _to_positive_float(row.get("putbackTriggerPrice"))
    if direct is not None:
        return direct, "direct_resale_trigger_price"

    ratio = _derive_resale_trigger_ratio(row)
    row["putbackTriggerRatio"] = (ratio * 100.0) if ratio is not None else None
    if ratio is None:
        return None, "missing"

    base_price = (
        _to_positive_float(row.get("currentTransferPrice"))
        or _to_positive_float(row.get("downFixPrice"))
        or _to_positive_float(row.get("convertPrice"))
        or _to_positive_float(row.get("initialTransferPrice"))
    )
    if base_price is None:
        return None, "missing_base_transfer_price"

    return base_price * ratio, "derived_from_resale_clause_ratio"


def _extract_maturity_redeem_price(redeem_clause: Any) -> Optional[float]:
    result = cb_metrics._extract_maturity_redeem_price(redeem_clause)
    if result is not None:
        return result

    text = str(redeem_clause or "")
    if not text:
        return None

    patterns = [
        r"到期[^。；\n]{0,100}?面值[^0-9]{0,15}(\d+(?:\.\d+)?)\s*%",
        r"期满[^。；\n]{0,100}?面值[^0-9]{0,15}(\d+(?:\.\d+)?)\s*%",
    ]
    for pattern in patterns:
        hit = re.search(pattern, text)
        if not hit:
            continue
        value = _to_float(hit.group(1))
        if value is not None and 80 <= value <= 200:
            return value

    values = [value for value in cb_metrics._extract_percent_values(text) if 80 <= value <= 200]
    if not values:
        return None
    return max(values)


def _should_exclude_by_delist_or_expiry(row: Dict[str, Any], as_of_date: date) -> bool:
    if cb_metrics._should_exclude_by_delist_or_expiry(row, as_of_date):
        return True

    maturity = _to_date_str(row.get("maturityDate"))
    if maturity:
        try:
            if datetime.fromisoformat(maturity).date() < as_of_date:
                return True
        except Exception:
            pass
    return False


def _build_cov_basic_map() -> Dict[str, Dict[str, Any]]:
    url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    result: Dict[str, Dict[str, Any]] = {}
    page_number = 1
    page_size = 500
    max_pages = 20

    while page_number <= max_pages:
        params = {
            "reportName": "RPT_BOND_CB_LIST",
            "columns": "ALL",
            "source": "WEB",
            "client": "WEB",
            "pageNumber": str(page_number),
            "pageSize": str(page_size),
        }
        try:
            payload = requests.get(url, params=params, timeout=REQUEST_TIMEOUT).json()
        except Exception:
            break
        data = (payload.get("result") or {}).get("data") or []
        if not data:
            break
        for row in data:
            code = str(row.get("SECURITY_CODE") or "").strip()
            if not code:
                continue
            result[code] = {
                "stockCode": str(row.get("CONVERT_STOCK_CODE") or "").strip() or None,
                "stockName": str(row.get("SECURITY_SHORT_NAME") or row.get("CORRECODE_NAME_ABBR") or "").strip() or None,
                "rating": str(row.get("RATING") or "").strip() or None,
                "issueScaleYi": _to_positive_float(row.get("ACTUAL_ISSUE_SCALE")),
                "executePriceHs": _to_positive_float(row.get("EXECUTE_PRICE_HS")),
                "executePriceSh": _to_positive_float(row.get("EXECUTE_PRICE_SH")),
                "issuePrice": _to_positive_float(row.get("ISSUE_PRICE")),
                "resaleTrigPrice": _to_positive_float(row.get("RESALE_TRIG_PRICE")),
                "redeemTrigPrice": _to_positive_float(row.get("REDEEM_TRIG_PRICE")),
                "listingDate": _to_date_str(row.get("LISTING_DATE")),
                "convertStartDate": _to_date_str(row.get("TRANSFER_START_DATE")),
                "maturityDate": _to_date_str(row.get("EXPIRE_DATE")),
                "delistDate": _to_date_str(row.get("DELIST_DATE")),
                "ceaseDate": _to_date_str(row.get("CEASE_DATE")),
                "bondExpireYears": _to_float(row.get("BOND_EXPIRE")),
                "initialTransferPrice": _to_positive_float(row.get("INITIAL_TRANSFER_PRICE")),
                "transferPrice": _to_positive_float(row.get("TRANSFER_PRICE")),
                "transferValue": _to_positive_float(row.get("TRANSFER_VALUE")),
                "convertStockPrice": _to_positive_float(row.get("CONVERT_STOCK_PRICE")),
                "couponRate": _to_float(row.get("COUPON_IR")),
                "resaleClause": str(row.get("RESALE_CLAUSE") or "").strip() or None,
                "redeemClause": str(row.get("REDEEM_CLAUSE") or "").strip() or None,
                "maturityRedeemPrice": _extract_maturity_redeem_price(row.get("REDEEM_CLAUSE")),
                "isRedeem": str(row.get("IS_REDEEM") or "").strip() or None,
                "isSellback": str(row.get("IS_SELLBACK") or "").strip() or None,
                "redeemNoticeDateSh": _to_date_str(row.get("NOTICE_DATE_SH")),
                "redeemNoticeDateHs": _to_date_str(row.get("NOTICE_DATE_HS")),
                "redeemExecuteReasonSh": str(row.get("EXECUTE_REASON_SH") or "").strip() or None,
                "redeemExecuteReasonHs": str(row.get("EXECUTE_REASON_HS") or "").strip() or None,
            }
        pages = int((payload.get("result") or {}).get("pages") or 0)
        if pages and page_number >= pages:
            break
        page_number += 1

    return result


def _to_code6(value: Any) -> Optional[str]:
    text = str(value or "").strip()
    if not text:
        return None
    digits = "".join(ch for ch in text if ch.isdigit())
    if not digits:
        return None
    return digits[-6:].zfill(6)


def _build_cov_realtime_map() -> Dict[str, Dict[str, Any]]:
    try:
        df = ak.bond_zh_hs_cov_spot()
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    result: Dict[str, Dict[str, Any]] = {}
    records = df.to_dict("records")
    for record in records:
        symbol = str(record.get("symbol") or "").strip().lower()
        if not symbol.startswith(("sh", "sz")):
            continue
        code = _to_code6(record.get("code"))
        if not code:
            continue
        amount = _to_float(record.get("amount"))
        volume = _to_float(record.get("volume"))
        result[code] = {
            "bondName": str(record.get("name") or "").strip() or None,
            "price": _to_float(record.get("trade")),
            "changePercent": _to_float(record.get("changepercent")),
            "priceChange": _to_float(record.get("pricechange")),
            "turnoverAmountYi": (amount / 1e8) if amount is not None else None,
            "volumeWanShou": (volume / 1e4) if volume is not None else None,
            "tickTime": str(record.get("ticktime") or "").strip() or None,
            "source": "sina_cov_spot",
        }
    return result


def _build_cov_quote_map() -> Dict[str, Dict[str, Any]]:
    try:
        df = ak.bond_zh_cov()
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    def pick_col(candidates: list[str]) -> Optional[str]:
        for name in candidates:
            if name in df.columns:
                return name
        return None

    code_col = pick_col(["\u503a\u5238\u4ee3\u7801", "\u4ee3\u7801", "bond_code", "bondCode"])
    if not code_col:
        return {}
    bond_name_col = pick_col(["\u503a\u5238\u7b80\u79f0", "\u503a\u5238\u540d\u79f0", "\u540d\u79f0", "bond_name", "bondName"])
    stock_code_col = pick_col(["\u6b63\u80a1\u4ee3\u7801", "\u80a1\u7968\u4ee3\u7801", "stock_code", "stockCode"])
    stock_name_col = pick_col(["\u6b63\u80a1\u7b80\u79f0", "\u80a1\u7968\u7b80\u79f0", "stock_name", "stockName"])
    stock_price_col = pick_col(["\u6b63\u80a1\u4ef7", "\u6b63\u80a1\u4ef7\u683c", "stock_price", "stockPrice"])
    convert_price_col = pick_col(["\u8f6c\u80a1\u4ef7", "\u8f6c\u80a1\u4ef7\u683c", "convert_price", "convertPrice"])
    convert_value_col = pick_col(["\u8f6c\u80a1\u4ef7\u503c", "convert_value", "convertValue"])
    premium_rate_col = pick_col(["\u8f6c\u80a1\u6ea2\u4ef7\u7387", "\u6ea2\u4ef7\u7387", "premium_rate", "premiumRate"])
    rating_col = pick_col(["\u4fe1\u7528\u8bc4\u7ea7", "rating", "\u4fe1\u7528\u7ea7\u522b"])
    listing_date_col = pick_col(["\u4e0a\u5e02\u65f6\u95f4", "\u4e0a\u5e02\u65e5\u671f", "listing_date", "listingDate"])
    issue_scale_col = pick_col(["\u53d1\u884c\u89c4\u6a21", "\u89c4\u6a21", "issue_scale", "issueScale"])
    price_col = pick_col(["\u503a\u73b0\u4ef7", "\u73b0\u4ef7", "\u6700\u65b0\u4ef7", "price", "bond_price"])

    result: Dict[str, Dict[str, Any]] = {}
    records = df.to_dict("records")
    for record in records:
        code = _to_code6(record.get(code_col))
        if not code:
            continue
        result[code] = {
            "bondName": str(record.get(bond_name_col) or "").strip() or None if bond_name_col else None,
            "stockCode": _to_code6(record.get(stock_code_col)) if stock_code_col else None,
            "stockName": str(record.get(stock_name_col) or "").strip() or None if stock_name_col else None,
            "stockPrice": _to_float(record.get(stock_price_col)) if stock_price_col else None,
            "convertPrice": _to_float(record.get(convert_price_col)) if convert_price_col else None,
            "convertValue": _to_float(record.get(convert_value_col)) if convert_value_col else None,
            "premiumRate": _to_float(record.get(premium_rate_col)) if premium_rate_col else None,
            "rating": str(record.get(rating_col) or "").strip() or None if rating_col else None,
            "listingDate": _to_date_str(record.get(listing_date_col)) if listing_date_col else None,
            "issueScaleYi": _to_positive_float(record.get(issue_scale_col)) if issue_scale_col else None,
            "price": _to_float(record.get(price_col)) if price_col else None,
        }
    return result


def _build_cb_jsl_map(cookie: str = "") -> Dict[str, Dict[str, Any]]:
    fetcher = getattr(ak, "bond_cb_jsl", None)
    if fetcher is None:
        return {}
    try:
        df = fetcher(cookie=cookie or "")
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    def pick_col(candidates: list[str]) -> Optional[str]:
        for name in candidates:
            if name in df.columns:
                return name
        return None

    code_col = pick_col(["代码", "债券代码", "bond_id"])
    if not code_col:
        return {}

    ytm_col = pick_col(["到期税前收益", "到期税前收益率", "ytm_rt"])
    remaining_years_col = pick_col(["剩余年限", "year_left"])

    result: Dict[str, Dict[str, Any]] = {}
    records = df.to_dict("records")
    for record in records:
        code = _to_code6(record.get(code_col))
        if not code:
            continue
        result[code] = {
            "yieldToMaturityPretax": _to_float(record.get(ytm_col)) if ytm_col else None,
            "remainingYears": _to_float(record.get(remaining_years_col)) if remaining_years_col else None,
        }
    return result


def _fetch_eastmoney_pure_bond_rows(
    filter_expr: str = "",
    page_size: int = 5000,
    fetch_all_pages: bool = True,
) -> list[Dict[str, Any]]:
    params = {
        "sty": "ALL",
        "token": "894050c76af8597a853f5b408b759f5d",
        "st": "DATE",
        "sr": "-1",
        "source": "WEB",
        "type": "RPTA_WEB_KZZ_LS",
        "p": "1",
        "ps": str(page_size),
    }
    if filter_expr:
        params["filter"] = filter_expr

    response = requests.get(
        "https://datacenter-web.eastmoney.com/api/data/get",
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    payload = response.json()
    result = (payload or {}).get("result") or {}
    rows = list(result.get("data") or [])
    if not fetch_all_pages:
        return rows

    pages = max(1, int(result.get("pages") or 1))
    if pages <= 1:
        return rows

    for page in range(2, pages + 1):
        params["p"] = str(page)
        response = requests.get(
            "https://datacenter-web.eastmoney.com/api/data/get",
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        payload = response.json()
        rows.extend((((payload or {}).get("result") or {}).get("data")) or [])
    return rows


@lru_cache(maxsize=4)
def _build_latest_pure_bond_map() -> Dict[str, Dict[str, Any]]:
    try:
        # 这里只需要最新一条日期锚点，不能误触发全量翻页。
        head_rows = _fetch_eastmoney_pure_bond_rows(page_size=1, fetch_all_pages=False)
    except Exception:
        return {}
    if not head_rows:
        return {}

    latest_date = _to_date_str(head_rows[0].get("DATE"))
    if not latest_date:
        return {}

    try:
        lookback_date = (datetime.fromisoformat(latest_date).date() - timedelta(days=7)).isoformat()
        rows = _fetch_eastmoney_pure_bond_rows(filter_expr=f"(DATE>='{lookback_date}')", page_size=8000)
    except Exception:
        return {}

    result: Dict[str, Dict[str, Any]] = {}
    for item in rows:
        code = _to_code6(item.get("ZCODE"))
        if not code or code in result:
            continue
        pure_bond_value = _to_positive_float(item.get("PUREBONDVALUE"))
        if pure_bond_value is None:
            continue
        result[code] = {
            "pureBondValue": round(pure_bond_value, 6),
            "pureBondValueDate": _to_date_str(item.get("DATE")),
            "pureBondValueSource": "eastmoney_value_analysis_latest",
        }
    return result


def _build_ths_cov_info_map() -> Dict[str, Dict[str, Any]]:
    try:
        df = ak.bond_zh_cov_info_ths()
    except Exception:
        return {}
    if df is None or df.empty:
        return {}

    code_col = "\u503a\u5238\u4ee3\u7801"
    listing_col = "\u4e0a\u5e02\u65e5\u671f"
    maturity_col = "\u5230\u671f\u65f6\u95f4"
    stock_code_col = "\u6b63\u80a1\u4ee3\u7801"
    stock_name_col = "\u6b63\u80a1\u7b80\u79f0"
    convert_price_col = "\u8f6c\u80a1\u4ef7\u683c"
    if code_col not in df.columns:
        return {}

    result: Dict[str, Dict[str, Any]] = {}
    records = df.to_dict("records")
    for record in records:
        code = str(record.get(code_col) or "").strip()
        if not code:
            continue
        result[code] = {
            "listingDate": _to_date_str(record.get(listing_col)) if listing_col in df.columns else None,
            "maturityDate": _to_date_str(record.get(maturity_col)) if maturity_col in df.columns else None,
            "stockCode": _to_code6(record.get(stock_code_col)) if stock_code_col in df.columns else None,
            "stockName": (str(record.get(stock_name_col) or "").strip() or None) if stock_name_col in df.columns else None,
            "convertPrice": _to_positive_float(record.get(convert_price_col)) if convert_price_col in df.columns else None,
        }
    return result


def _build_stock_spot_map_from_a_spot(force_refresh: bool = False) -> Dict[str, Dict[str, Optional[float]]]:
    now_ts = _now_ts_ms()
    cached = _STOCK_SPOT_CACHE.get("data")
    expires_at = int(_STOCK_SPOT_CACHE.get("expiresAt") or 0)
    if not force_refresh and isinstance(cached, dict) and cached and now_ts < expires_at:
        return cached
    for fetcher in (getattr(ak, "stock_zh_a_spot_em", None), getattr(ak, "stock_zh_a_spot", None)):
        if fetcher is None:
            continue
        try:
            df = fetcher()
        except Exception:
            continue
        if df is None or df.empty:
            continue

        code_col = None
        for candidate in ("\u4ee3\u7801", "code", "symbol"):
            if candidate in df.columns:
                code_col = candidate
                break

        price_col = None
        for candidate in ("\u6700\u65b0\u4ef7", "\u73b0\u4ef7", "\u6700\u65b0", "trade", "price"):
            if candidate in df.columns:
                price_col = candidate
                break

        change_col = None
        for candidate in ("\u6da8\u8dcc\u5e45", "\u6da8\u8dcc\u5e45(%)", "changepercent", "changePercent"):
            if candidate in df.columns:
                change_col = candidate
                break

        if code_col is None:
            continue

        result: Dict[str, Dict[str, Optional[float]]] = {}
        records = df.to_dict("records")
        for record in records:
            code = _to_code6(record.get(code_col))
            if not code:
                continue
            result[code] = {
                "price": _to_float(record.get(price_col)) if price_col else None,
                "changePercent": _to_float(record.get(change_col)) if change_col else None,
            }
        if result:
            _STOCK_SPOT_CACHE["data"] = result
            _STOCK_SPOT_CACHE["expiresAt"] = now_ts + STOCK_SPOT_CACHE_TTL_MS
            return result

    return {}


def _build_stock_change_map_from_a_spot() -> Dict[str, float]:
    return {
        code: _to_float(snapshot.get("changePercent"))
        for code, snapshot in _build_stock_spot_map_from_a_spot().items()
        if _to_float(snapshot.get("changePercent")) is not None
    }

def _normalize_putback_price_int(value: Any) -> Optional[float]:
    return cb_metrics._normalize_putback_price_int(value)


def _american_option_binomial(
    spot: float,
    strike: float,
    years: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    steps: int = 120,
) -> float:
    return cb_metrics._american_option_binomial(spot, strike, years, risk_free_rate, volatility, option_type, steps)


def _bond_floor_value(risk_free_rate: float, years: Optional[float]) -> float:
    return cb_metrics._bond_floor_value(risk_free_rate, years)


def _calc_volatility_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    return cb_metrics._calc_volatility_metrics(stock_code)


def _metrics_ready(metrics: Dict[str, Any]) -> bool:
    return cb_metrics._volatility_metrics_ready(metrics)


def _calc_stock_history_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    return cb_metrics._calc_stock_history_metrics(stock_code)


def _metrics_ready(metrics: Dict[str, Any]) -> bool:
    return cb_metrics._stock_history_metrics_ready(metrics)


def _get_risk_free_rate() -> Dict[str, Any]:
    df = ak.bond_gb_zh_sina()
    if df is None or df.empty:
        raise RuntimeError("bond_gb_zh_sina returned empty data")

    latest = df.iloc[-1]
    close_rate = _to_float(latest.get("close"))
    if close_rate is None:
        raise RuntimeError("10Y treasury close rate missing")

    return {
        "rate": close_rate / 100.0,
        "percent": close_rate,
        "date": _to_date_str(latest.get("date")),
        "source": "sina",
    }


def _build_theoretical_metrics(row: Dict[str, Any], risk_free_rate: float) -> Dict[str, Optional[float]]:
    return cb_metrics._build_theoretical_metrics(row, risk_free_rate)


def _build_small_redemption_option_metrics(
    row: Dict[str, Any], risk_free_rate: float
) -> Dict[str, Optional[float]]:
    return cb_metrics._build_small_redemption_option_metrics(row, risk_free_rate)


def _resolve_redeem_trigger_price(row: Dict[str, Any]) -> tuple[Optional[float], str]:
    # 1) Preferred: direct redeem trigger price from source payload.
    direct = _to_float(row.get("redeemTriggerPrice"))
    if direct is not None and direct > 0:
        return direct, "direct_redeem_trigger_price"

    # 2) Fallback: infer from convert price * redeem trigger ratio if ratio exists.
    convert_price = _to_float(row.get("convertPrice"))
    ratio = _to_percent_ratio(row.get("redeemTriggerRatio"))
    if convert_price and convert_price > 0 and ratio and ratio > 0:
        return convert_price * ratio, "derived_from_convert_price_and_ratio"

    # 3) Practical fallback: most terms use 130% of convert price.
    if convert_price and convert_price > 0:
        return convert_price * 1.30, "fallback_130pct_convert_price"

    return None, "missing"


def get_bond_cb_data(allow_inline_history_hydrate: bool = False) -> Dict[str, Any]:
    now = datetime.now()
    now_iso = now.isoformat()
    jisilu_cookie = _load_jisilu_cookie()
    cookie_configured = bool(jisilu_cookie)
    cov_quote_items: Dict[str, Dict[str, Any]] = {}
    try:
        price_db.init_db()
        realtime_items = _build_cov_realtime_map()
        # 正股现价优先复用转债源侧已给出的实时字段，只有缺字段时才补拉全市场现货，避免 force 刷新超时。
        stock_spot_items: Dict[str, Dict[str, Any]] = {}
    except Exception as exc:
        return {
            "success": False,
            "data": [],
            "updateTime": now_iso,
            "error": str(exc),
            "source": "sina_cov_spot+eastmoney_cov",
            "cookieConfigured": cookie_configured,
        }

    if not realtime_items:
        cov_quote_items = _build_cov_quote_map()
        if cov_quote_items:
            fallback_items: Dict[str, Dict[str, Any]] = {}
            for code, item in cov_quote_items.items():
                price = _to_float((item or {}).get("price"))
                if price is None:
                    continue
                fallback_items[code] = {
                    "bondName": item.get("bondName"),
                    "price": price,
                    "changePercent": None,
                    "turnoverAmountYi": None,
                    "source": "eastmoney_cov_quote",
                }
            realtime_items = fallback_items

    if not realtime_items:
        return {
            "success": False,
            "data": [],
            "updateTime": now_iso,
            "error": "bond_zh_hs_cov_spot and bond_zh_cov both returned empty data",
            "source": "sina_cov_spot+eastmoney_cov",
            "cookieConfigured": cookie_configured,
        }

    try:
        risk_free = _get_risk_free_rate()
    except Exception as exc:
        return {
            "success": False,
            "data": [],
            "updateTime": now_iso,
            "error": f"10Y treasury yield unavailable: {exc}",
            "source": "sina_cov_spot+eastmoney_cov",
            "cookieConfigured": cookie_configured,
        }
    as_of_date_text = now.date().isoformat()
    aux_cache = _read_cb_arb_aux_cache()
    previous_row_map = _read_cached_cb_arb_row_map()
    vol_cache_items: Dict[str, Dict[str, Any]] = _build_cached_history_metrics_map(previous_row_map, aux_cache)
    financial_cache_items: Dict[str, Dict[str, Optional[float]]] = _build_cached_financial_metrics_map(previous_row_map, aux_cache)
    holder_cache_items: Dict[str, Dict[str, Any]] = _build_cached_holder_info_map(previous_row_map, aux_cache)
    stock_change_cache_items: Dict[str, Any] = {}
    cov_basic_items = _load_daily_cached_map(aux_cache, "covBasicMap", as_of_date_text, _build_cov_basic_map)
    cb_jsl_items = _build_cb_jsl_map(jisilu_cookie)
    ths_cov_info_items = _load_daily_cached_map(aux_cache, "thsCovInfoMap", as_of_date_text, _build_ths_cov_info_map)
    pure_bond_value_items = _load_daily_cached_map(aux_cache, "pureBondMap", as_of_date_text, _build_latest_pure_bond_map)
    stock_codes = sorted({
        stock_code
        for bond_code in realtime_items.keys()
        for stock_code in [
            _to_code6((cov_quote_items.get(bond_code) or {}).get("stockCode"))
            or _to_code6((cov_basic_items.get(bond_code) or {}).get("stockCode"))
            or _to_code6((ths_cov_info_items.get(bond_code) or {}).get("stockCode"))
            or _to_code6((previous_row_map.get(bond_code) or {}).get("stockCode"))
        ]
        if stock_code
    })
    stock_market_value_items = _load_daily_cached_map(
        aux_cache,
        "stockMarketValueByStock",
        as_of_date_text,
        lambda: _load_stock_market_value_map(stock_codes),
    )
    if not pure_bond_value_items:
        pure_bond_value_items = {}
        for previous_code, previous_row in previous_row_map.items():
            pure_bond_value = _to_positive_float((previous_row or {}).get("pureBondValue"))
            if pure_bond_value is None:
                continue
            pure_bond_value_items[previous_code] = {
                "pureBondValue": pure_bond_value,
                "pureBondValueDate": _to_date_str((previous_row or {}).get("pureBondValueDate")),
                "pureBondValueSource": str((previous_row or {}).get("pureBondValueSource") or "previous_cb_arb_snapshot").strip() or "previous_cb_arb_snapshot",
            }

    rows = []
    excluded_by_name_count = 0
    missing_stock_codes = []
    missing_stock_spot_codes = []
    missing_stock_change_codes = []

    for code, realtime in realtime_items.items():
        quote_row = cov_quote_items.get(code) if isinstance(cov_quote_items, dict) else None
        previous_row = previous_row_map.get(code) if isinstance(previous_row_map, dict) else None
        bond_name_raw = str((realtime or {}).get("bondName") or (quote_row or {}).get("bondName") or (previous_row or {}).get("bondName") or "").strip()
        if _should_exclude_bond_by_name(bond_name_raw):
            excluded_by_name_count += 1
            continue

        price = _to_float((realtime or {}).get("price"))
        change_percent = _to_float((realtime or {}).get("changePercent"))
        turnover_amount_yi = _to_float((realtime or {}).get("turnoverAmountYi"))
        stock_code = _to_code6((quote_row or {}).get("stockCode")) or _to_code6((previous_row or {}).get("stockCode"))
        stock_name = str((quote_row or {}).get("stockName") or (previous_row or {}).get("stockName") or "").strip() or None
        stock_spot = stock_spot_items.get(stock_code or "") if isinstance(stock_spot_items, dict) else None
        stock_spot_price = _to_float((stock_spot or {}).get("price"))
        stock_spot_change = _to_float((stock_spot or {}).get("changePercent"))
        stock_price = stock_spot_price if stock_spot_price is not None else _to_float((quote_row or {}).get("stockPrice"))
        convert_price = _to_float((quote_row or {}).get("convertPrice"))
        convert_value = _to_float((quote_row or {}).get("convertValue"))
        premium_rate = _to_float((quote_row or {}).get("premiumRate"))
        rating = str((quote_row or {}).get("rating") or (previous_row or {}).get("rating") or "").strip() or None
        listing_date_from_quote = _to_date_str((quote_row or {}).get("listingDate")) or _to_date_str((previous_row or {}).get("listingDate"))
        remaining_size_from_quote = _to_positive_float((quote_row or {}).get("issueScaleYi")) or _to_positive_float((previous_row or {}).get("remainingSizeYi"))
        stock_change_percent = stock_spot_change if stock_spot_change is not None else _to_float(stock_change_cache_items.get(stock_code))
        stock_market_value_yi = stock_market_value_items.get(stock_code) if stock_code else None
        if stock_market_value_yi is None:
            stock_market_value_yi = _to_positive_float((previous_row or {}).get("stockMarketValueYi"))
        double_low = (price + premium_rate) if (price is not None and premium_rate is not None) else None

        row = {
            "code": code,
            "bondName": bond_name_raw or None,
            "price": price,
            "changePercent": change_percent,
            "stockCode": stock_code,
            "stockName": stock_name,
            "stockPrice": stock_price,
            "stockChangePercent": stock_change_percent,
            "stockPb": None,
            "convertPrice": convert_price,
            "convertValue": convert_value,
            "premiumRate": premium_rate,
            "rating": rating,
            "putbackTriggerPrice": None,
            "putbackTriggerPriceTaxIncluded": None,
            "putbackTriggerRatio": None,
            "redeemTriggerPrice": None,
            "redeemTriggerRatio": None,
            "bondStockRatio": None,
            "maturityDate": None,
            "delistDate": None,
            "ceaseDate": None,
            "remainingYears": None,
            "remainingSizeYi": remaining_size_from_quote,
            "stockMarketValueYi": stock_market_value_yi,
            "turnoverAmountYi": turnover_amount_yi,
            "turnoverRate": None,
            "stockAtr20": None,
            "stockAvgTurnoverAmount20Yi": None,
            "stockAvgTurnoverAmount5Yi": None,
            "yieldToMaturityPretax": None,
            "doubleLow": double_low,
            "stockAvgRoe3Y": None,
            "stockDebtRatio": None,
            "holderCount": None,
            "holderCountReportPeriod": None,
            "holderCountReportSourceUrl": None,
            "holderCountFallbackUsed": False,
            "holderCountLastCheckedAt": None,
            "smallRedemptionYield": None,
            "smallRedemptionExpectedYears": None,
            "smallRedemptionAnnualizedYield": None,
            "smallRedemptionAmount": None,
            "smallRedemptionTotalAmount": None,
            "smallRedemptionBondValue": None,
            "smallRedemptionCallStrike": None,
            "smallRedemptionLongCallOptionValue": None,
            "smallRedemptionShortCallOptionValue": None,
            "smallRedemptionOptionValue": None,
            "smallRedemptionOptionYield": None,
            "smallRedemptionOptionAnnualizedYield": None,
            "smallRedemptionTotalAnnualizedYield": None,
            "stockNetAssetsYi": None,
            "stockInterestBearingDebtYi": None,
            "stockBroadCashYi": None,
            "stockNetDebtExposureYi": None,
            "pureBondValue": None,
            "pureBondValueDate": None,
            "pureBondValueSource": None,
            "couponRate": None,
            "resaleClause": None,
            "redeemClause": None,
            "redeemNoticeDateSh": None,
            "redeemNoticeDateHs": None,
            "maturityRedeemPrice": None,
            "putbackPrice": None,
            "putbackPriceInt": None,
            "putbackPriceSource": None,
            "initialTransferPrice": None,
            "currentTransferPrice": None,
            "downFixPrice": None,
            "downFixBasePrice": None,
            "downFixDiff": None,
            "downFixSource": None,
            "isDownFixed": None,
            "listingDate": listing_date_from_quote,
            "listingDateSource": "previous_cb_arb_snapshot_listing" if listing_date_from_quote else None,
            "convertStartDate": None,
            "convertStartDateSource": None,
            "isUnlisted": None,
            "isBeforeConvertStart": None,
            "isMaturityWithinOneYear": None,
            "forceRedeemPrice": None,
            "forceRedeemStatus": None,
            "forceRedeemNoticeDate": None,
            "source": "sina_cov_spot+eastmoney_cov",
        }
        resolved_redeem_price, resolved_source = _resolve_redeem_trigger_price(row)
        row["redeemTriggerPrice"] = resolved_redeem_price
        row["redeemTriggerPriceSource"] = resolved_source

        cb_jsl_row = cb_jsl_items.get(code) if isinstance(cb_jsl_items, dict) else None
        if isinstance(cb_jsl_row, dict):
            cb_jsl_ytm = _to_float(cb_jsl_row.get("yieldToMaturityPretax"))
            cb_jsl_remaining_years = _to_float(cb_jsl_row.get("remainingYears"))
            if cb_jsl_ytm is not None:
                row["yieldToMaturityPretax"] = cb_jsl_ytm
            if cb_jsl_remaining_years is not None:
                row["remainingYears"] = cb_jsl_remaining_years

        cov_row = cov_basic_items.get(code) if isinstance(cov_basic_items, dict) else None
        if isinstance(cov_row, dict):
            cov_stock_code = _to_code6(cov_row.get("stockCode"))
            cov_stock_name = str(cov_row.get("stockName") or "").strip() or None
            cov_stock_price = _to_positive_float(cov_row.get("convertStockPrice"))
            cov_rating = str(cov_row.get("rating") or "").strip() or None
            cov_issue_scale = _to_positive_float(cov_row.get("issueScaleYi"))
            cov_listing = _to_date_str(cov_row.get("listingDate"))
            cov_convert_start = _to_date_str(cov_row.get("convertStartDate"))
            cov_maturity = _to_date_str(cov_row.get("maturityDate"))
            cov_delist = _to_date_str(cov_row.get("delistDate"))
            cov_cease = _to_date_str(cov_row.get("ceaseDate"))
            cov_resale_trig = _to_positive_float(cov_row.get("resaleTrigPrice"))
            cov_redeem_trig = _to_positive_float(cov_row.get("redeemTrigPrice"))
            cov_initial_transfer = _to_positive_float(cov_row.get("initialTransferPrice"))
            cov_transfer = _to_positive_float(cov_row.get("transferPrice"))
            cov_execute = _to_positive_float(cov_row.get("executePriceHs")) or _to_positive_float(cov_row.get("executePriceSh"))
            cov_issue = _to_positive_float(cov_row.get("issuePrice"))
            cov_coupon_rate = _to_float(cov_row.get("couponRate"))
            cov_resale_clause = str(cov_row.get("resaleClause") or "").strip() or None
            cov_redeem_clause = str(cov_row.get("redeemClause") or "").strip() or None
            cov_maturity_redeem = _to_positive_float(cov_row.get("maturityRedeemPrice"))
            cov_notice_sh = _to_date_str(cov_row.get("redeemNoticeDateSh"))
            cov_notice_hs = _to_date_str(cov_row.get("redeemNoticeDateHs"))

            if row.get("stockCode") is None and cov_stock_code:
                row["stockCode"] = cov_stock_code
            if row.get("stockName") is None and cov_stock_name:
                row["stockName"] = cov_stock_name
            if row.get("stockPrice") is None and cov_stock_price is not None:
                row["stockPrice"] = cov_stock_price
            if row.get("rating") is None and cov_rating:
                row["rating"] = cov_rating
            if row.get("remainingSizeYi") is None and cov_issue_scale is not None:
                row["remainingSizeYi"] = cov_issue_scale
            if row.get("listingDate") is None and cov_listing:
                row["listingDate"] = cov_listing
                row["listingDateSource"] = "eastmoney_cov_bulk_listing"
            if row.get("convertStartDate") is None and cov_convert_start:
                row["convertStartDate"] = cov_convert_start
                row["convertStartDateSource"] = "eastmoney_cov_bulk_convert_start"
            if row.get("maturityDate") is None and cov_maturity:
                row["maturityDate"] = cov_maturity
            if row.get("delistDate") is None and cov_delist:
                row["delistDate"] = cov_delist
            if row.get("ceaseDate") is None and cov_cease:
                row["ceaseDate"] = cov_cease
            if row.get("putbackTriggerPrice") is None and cov_resale_trig is not None:
                row["putbackTriggerPrice"] = cov_resale_trig
                row["putbackTriggerPriceTaxIncluded"] = cov_resale_trig
            if row.get("redeemTriggerPrice") is None and cov_redeem_trig is not None:
                row["redeemTriggerPrice"] = cov_redeem_trig
                row["redeemTriggerPriceSource"] = "eastmoney_cov_bulk_redeem_trigger"
            if row.get("couponRate") is None and cov_coupon_rate is not None:
                row["couponRate"] = cov_coupon_rate
            if row.get("resaleClause") is None and cov_resale_clause:
                row["resaleClause"] = cov_resale_clause
            if row.get("redeemClause") is None and cov_redeem_clause:
                row["redeemClause"] = cov_redeem_clause
            if row.get("maturityRedeemPrice") is None and cov_maturity_redeem is not None:
                row["maturityRedeemPrice"] = cov_maturity_redeem
            if row.get("redeemNoticeDateSh") is None and cov_notice_sh:
                row["redeemNoticeDateSh"] = cov_notice_sh
            if row.get("redeemNoticeDateHs") is None and cov_notice_hs:
                row["redeemNoticeDateHs"] = cov_notice_hs
            if cov_initial_transfer is not None:
                row["initialTransferPrice"] = cov_initial_transfer
                row["downFixBasePrice"] = cov_initial_transfer
            if cov_transfer is not None:
                row["currentTransferPrice"] = cov_transfer
                row["downFixPrice"] = cov_transfer
                row["downFixSource"] = "eastmoney_cov_bulk_transfer_price"
            if row.get("putbackPrice") is None:
                if cov_execute is not None:
                    row["putbackPrice"] = cov_execute
                    row["putbackPriceInt"] = _normalize_putback_price_int(cov_execute)
                    row["putbackPriceSource"] = "eastmoney_cov_bulk_execute"
                elif cov_issue is not None:
                    row["putbackPrice"] = cov_issue
                    row["putbackPriceInt"] = _normalize_putback_price_int(cov_issue)
                    row["putbackPriceSource"] = "eastmoney_cov_bulk_issue"
        ths_info = ths_cov_info_items.get(code) if isinstance(ths_cov_info_items, dict) else None
        if isinstance(ths_info, dict):
            ths_listing = _to_date_str(ths_info.get("listingDate"))
            if row.get("listingDate") is None and ths_listing:
                row["listingDate"] = ths_listing
                row["listingDateSource"] = "ths_cov_info_listing"
            ths_maturity = _to_date_str(ths_info.get("maturityDate"))
            if row.get("maturityDate") is None and ths_maturity:
                row["maturityDate"] = ths_maturity
            ths_stock_code = _to_code6(ths_info.get("stockCode"))
            if row.get("stockCode") is None and ths_stock_code:
                row["stockCode"] = ths_stock_code
            ths_stock_name = str(ths_info.get("stockName") or "").strip()
            if row.get("stockName") is None and ths_stock_name:
                row["stockName"] = ths_stock_name
            ths_convert_price = _to_positive_float(ths_info.get("convertPrice"))
            if row.get("convertPrice") is None and ths_convert_price is not None:
                row["convertPrice"] = ths_convert_price

        stock_code = _to_code6(row.get("stockCode"))
        stock_spot = stock_spot_items.get(stock_code or "") if isinstance(stock_spot_items, dict) else None
        if row.get("stockPrice") is None and stock_spot:
            row["stockPrice"] = _to_float((stock_spot or {}).get("price"))
        if row.get("stockChangePercent") is None and stock_spot:
            row["stockChangePercent"] = _to_float((stock_spot or {}).get("changePercent"))

        _recompute_live_convert_metrics(row)

        if row.get("downFixPrice") is None:
            fallback_convert_price = _to_positive_float(row.get("convertPrice"))
            if fallback_convert_price is not None:
                row["downFixPrice"] = fallback_convert_price
                row["currentTransferPrice"] = fallback_convert_price
                row["downFixSource"] = "convert_price_fallback"

        if row.get("redeemTriggerPrice") is None:
            redeem_price, redeem_source = _resolve_redeem_trigger_price(row)
            row["redeemTriggerPrice"] = redeem_price
            row["redeemTriggerPriceSource"] = redeem_source

        putback_trigger_price, putback_source = _resolve_putback_trigger_price(row)
        if putback_trigger_price is not None:
            row["putbackTriggerPrice"] = putback_trigger_price
            row["putbackTriggerPriceTaxIncluded"] = putback_trigger_price
            row["putbackTriggerPriceSource"] = putback_source

        stock_code = _to_code6(row.get("stockCode"))
        row["stockCode"] = stock_code
        if row.get("stockPrice") is None and stock_code:
            missing_stock_spot_codes.append(stock_code)
        if row.get("stockChangePercent") is None and stock_code:
            missing_stock_change_codes.append(stock_code)
        if stock_code:
            cached_vol = vol_cache_items.get(stock_code)
            if _metrics_ready(cached_vol):
                row.update(cached_vol)
            else:
                missing_stock_codes.append(stock_code)
            cached_financial = financial_cache_items.get(stock_code)
            if isinstance(cached_financial, dict):
                if row.get("stockAvgRoe3Y") is None:
                    row["stockAvgRoe3Y"] = cached_financial.get("stockAvgRoe3Y")
                if row.get("stockDebtRatio") is None:
                    row["stockDebtRatio"] = cached_financial.get("stockDebtRatio")
                if row.get("stockNetAssetsYi") is None:
                    row["stockNetAssetsYi"] = cached_financial.get("stockNetAssetsYi")
                if row.get("stockInterestBearingDebtYi") is None:
                    row["stockInterestBearingDebtYi"] = cached_financial.get("stockInterestBearingDebtYi")
                if row.get("stockBroadCashYi") is None:
                    row["stockBroadCashYi"] = cached_financial.get("stockBroadCashYi")
                if row.get("stockNetDebtExposureYi") is None:
                    row["stockNetDebtExposureYi"] = cached_financial.get("stockNetDebtExposureYi")
            cached_holder = holder_cache_items.get(stock_code)
            if isinstance(cached_holder, dict):
                if row.get("holderCount") is None:
                    row["holderCount"] = cached_holder.get("holderCount")
                if row.get("holderCountReportPeriod") is None:
                    row["holderCountReportPeriod"] = cached_holder.get("holderCountReportPeriod")
                if row.get("holderCountReportSourceUrl") is None:
                    row["holderCountReportSourceUrl"] = cached_holder.get("holderCountReportSourceUrl")
                row["holderCountFallbackUsed"] = cached_holder.get("holderCountFallbackUsed") is True
                if row.get("holderCountLastCheckedAt") is None:
                    row["holderCountLastCheckedAt"] = cached_holder.get("holderCountLastCheckedAt")

        rows.append(row)

    unique_missing_stock_spot_codes = sorted(set(code for code in missing_stock_spot_codes if code))
    unique_missing_stock_change_codes = sorted(set(code for code in missing_stock_change_codes if code))
    if (unique_missing_stock_spot_codes or unique_missing_stock_change_codes) and not stock_spot_items:
        stock_spot_items = _build_stock_spot_map_from_a_spot()
    if stock_spot_items:
        for row in rows:
            stock_code = row.get("stockCode")
            stock_spot = stock_spot_items.get(stock_code or "") if stock_code else None
            if row.get("stockPrice") is None and stock_spot:
                row["stockPrice"] = _to_float((stock_spot or {}).get("price"))
            if row.get("stockChangePercent") is None and stock_spot:
                row["stockChangePercent"] = _to_float((stock_spot or {}).get("changePercent"))
            if row.get("stockPrice") is not None:
                _recompute_live_convert_metrics(row)
    if unique_missing_stock_change_codes:
        latest_stock_change_map = {
            code: _to_float(snapshot.get("changePercent"))
            for code, snapshot in (stock_spot_items.items() if isinstance(stock_spot_items, dict) else [])
            if _to_float(snapshot.get("changePercent")) is not None
        }
        if not latest_stock_change_map:
            latest_stock_change_map = _build_stock_change_map_from_a_spot()
        if latest_stock_change_map:
            for code, change in latest_stock_change_map.items():
                stock_change_cache_items[code] = _to_float(change)
            for row in rows:
                stock_code = row.get("stockCode")
                if stock_code and row.get("stockChangePercent") is None:
                    row["stockChangePercent"] = _to_float(stock_change_cache_items.get(stock_code))

    unique_missing_stocks = sorted(set(code for code in missing_stock_codes if code))
    if unique_missing_stocks:
        if allow_inline_history_hydrate or INLINE_HISTORY_HYDRATE_ENABLED:
            ready_stock_metric_count = sum(
                1
                for metrics in vol_cache_items.values()
                if _metrics_ready(metrics)
            )
            hydrate_targets = unique_missing_stocks
            if ready_stock_metric_count > 10 and len(unique_missing_stocks) > INLINE_HISTORY_HYDRATE_LIMIT:
                hydrate_targets = unique_missing_stocks[:INLINE_HISTORY_HYDRATE_LIMIT]
            if hydrate_targets:
                _hydrate_stock_history_for_symbols(hydrate_targets)
        with ThreadPoolExecutor(max_workers=min(MAX_VOL_SYNC_WORKERS, max(1, len(unique_missing_stocks)))) as executor:
            future_map = {
                executor.submit(_calc_stock_history_metrics, code): code
                for code in unique_missing_stocks
            }
            for future in as_completed(future_map):
                code = future_map[future]
                try:
                    metrics = future.result()
                except Exception:
                    metrics = {
                        **_blank_volatility_metrics(),
                        "stockAtr20": None,
                        "stockAvgTurnoverAmount20Yi": None,
                        "stockAvgTurnoverAmount5Yi": None,
                    }
                vol_cache_items[code] = metrics

        for row in rows:
            stock_code = row.get("stockCode")
            if stock_code and stock_code in vol_cache_items:
                row.update(vol_cache_items[stock_code])
    as_of_date = now.date()
    # 纯债价值优先使用按日缓存的真实上游值，避免普通读链路重复跑重型补数。
    for row in rows:
        pure_bond_snapshot = pure_bond_value_items.get(_to_code6(row.get("code")) or "")
        if pure_bond_snapshot:
            row["pureBondValue"] = pure_bond_snapshot.get("pureBondValue")
            row["pureBondValueDate"] = pure_bond_snapshot.get("pureBondValueDate")
            row["pureBondValueSource"] = pure_bond_snapshot.get("pureBondValueSource")

        listing_date = _to_date_str(row.get("listingDate"))
        row["listingDate"] = listing_date
        if listing_date:
            try:
                row["isUnlisted"] = datetime.fromisoformat(listing_date).date() > as_of_date
            except Exception:
                row["isUnlisted"] = None
        else:
            row["isUnlisted"] = None

        convert_start_date = _to_date_str(row.get("convertStartDate"))
        row["convertStartDate"] = convert_start_date
        if convert_start_date:
            try:
                row["isBeforeConvertStart"] = datetime.fromisoformat(convert_start_date).date() > as_of_date
            except Exception:
                row["isBeforeConvertStart"] = None
        else:
            row["isBeforeConvertStart"] = None

        if row.get("isUnlisted") is None and row.get("isBeforeConvertStart") is True:
            row["isUnlisted"] = True
            if not row.get("listingDateSource"):
                row["listingDateSource"] = "inferred_from_future_convert_start"

        down_fix_price = _to_positive_float(row.get("downFixPrice"))
        down_fix_base_price = _to_positive_float(row.get("downFixBasePrice"))
        current_transfer_price = _to_positive_float(row.get("currentTransferPrice"))
        if current_transfer_price is None:
            current_transfer_price = _to_positive_float(row.get("convertPrice"))
        if down_fix_price is None:
            down_fix_price = current_transfer_price
        if down_fix_base_price is None:
            down_fix_base_price = _to_positive_float(row.get("initialTransferPrice"))

        row["currentTransferPrice"] = current_transfer_price
        row["downFixPrice"] = down_fix_price
        row["downFixBasePrice"] = down_fix_base_price
        if row.get("downFixSource") is None and down_fix_price is not None:
            row["downFixSource"] = "convert_price_fallback"

        stock_price = _to_float(row.get("stockPrice"))
        if stock_price is not None and down_fix_price is not None:
            row["downFixDiff"] = round(stock_price - down_fix_price, 4)
        else:
            row["downFixDiff"] = None

        if down_fix_price is not None and down_fix_base_price is not None:
            row["isDownFixed"] = down_fix_price < down_fix_base_price
        else:
            row["isDownFixed"] = None

        putback_trigger_price, putback_source = _resolve_putback_trigger_price(row)
        if putback_trigger_price is not None:
            row["putbackTriggerPrice"] = round(putback_trigger_price, 4)
            row["putbackTriggerPriceTaxIncluded"] = round(putback_trigger_price, 4)
            if row.get("putbackTriggerPriceSource") is None:
                row["putbackTriggerPriceSource"] = putback_source

        row["remainingYears"] = _derive_remaining_years(row, as_of_date)
        row["isMaturityWithinOneYear"] = (
            row["remainingYears"] is not None and float(row["remainingYears"]) < 1.0
        )
        row["isDelistedOrExpired"] = _should_exclude_by_delist_or_expiry(row, as_of_date)
        row.update(_derive_force_redeem_status(row, as_of_date))
        row.update(_with_primary_volatility_aliases(row))
        row.update(_build_theoretical_metrics(row, float(risk_free["rate"])))

        for window in VOL_WINDOWS:
            suffix = str(window)
            row[f"annualizedVolatility{suffix}"] = row.get(f"volatility{suffix}")
            row[f"bondEquityYield{suffix}"] = row.get(f"theoreticalPremiumRate{suffix}")
        row["annualizedVolatility"] = row.get(f"volatility{PRIMARY_VOL_WINDOW}")
        row["callStrike"] = row.get(f"callStrike{PRIMARY_VOL_WINDOW}")
        row["redeemCallStrike"] = row.get(f"redeemCallStrike{PRIMARY_VOL_WINDOW}")
        row["longCallOptionValue"] = row.get(f"longCallOptionValue{PRIMARY_VOL_WINDOW}")
        row["shortCallOptionValue"] = row.get(f"shortCallOptionValue{PRIMARY_VOL_WINDOW}")
        row["callSpreadOptionValue"] = row.get(f"callSpreadOptionValue{PRIMARY_VOL_WINDOW}")
        row["callOptionValue"] = row.get(f"callOptionValue{PRIMARY_VOL_WINDOW}")
        row["optionValue"] = row.get("callOptionValue")
        row["putOptionValue"] = None
        row["theoreticalPrice"] = row.get(f"theoreticalPrice{PRIMARY_VOL_WINDOW}")
        row["theoreticalPremiumRate"] = row.get(f"theoreticalPremiumRate{PRIMARY_VOL_WINDOW}")
        row["bondEquityYield"] = row.get(f"theoreticalPremiumRate{PRIMARY_VOL_WINDOW}")

    core_ready_rows = []
    excluded_missing_core_count = 0
    excluded_delisted_or_expired_count = 0
    for row in rows:
        has_core = (
            _to_code6(row.get("code")) is not None
            and _to_float(row.get("price")) is not None
            and _to_code6(row.get("stockCode")) is not None
            and _to_float(row.get("stockPrice")) is not None
            and _to_float(row.get("convertPrice")) is not None
        )
        if not has_core:
            excluded_missing_core_count += 1
            continue
        if row.get("isDelistedOrExpired") is True:
            excluded_delisted_or_expired_count += 1
            continue
        core_ready_rows.append(row)

    small_redemption_stock_codes = sorted({
        _to_code6(row.get("stockCode"))
        for row in core_ready_rows
        if _to_float(row.get("price")) is not None and _to_float(row.get("price")) < 100 and _to_code6(row.get("stockCode"))
    })

    missing_holder_stock_codes = sorted({
        code
        for code in small_redemption_stock_codes
        if _should_refresh_holder_info(holder_cache_items.get(code) if isinstance(holder_cache_items.get(code), dict) else {}, as_of_date)
    })
    if missing_holder_stock_codes:
        with ThreadPoolExecutor(max_workers=min(MAX_FINANCIAL_WORKERS, max(1, len(missing_holder_stock_codes)))) as executor:
            future_map = {
                executor.submit(_fetch_holder_info_for_stock, code, as_of_date): code
                for code in missing_holder_stock_codes
            }
            for future in as_completed(future_map):
                code = future_map[future]
                try:
                    holder_cache_items[code] = future.result()
                except Exception:
                    holder_cache_items[code] = {
                        "holderCount": None,
                        "holderCountReportPeriod": None,
                        "holderCountReportSourceUrl": None,
                        "holderCountFallbackUsed": False,
                        "holderCountLastCheckedAt": as_of_date.isoformat(),
                    }

    missing_small_redemption_financial_codes = sorted({
        code
        for code in small_redemption_stock_codes
        if not any(
            _to_float((financial_cache_items.get(code) or {}).get(field)) is not None
            for field in ("stockNetAssetsYi", "stockInterestBearingDebtYi", "stockBroadCashYi", "stockNetDebtExposureYi")
        )
    })
    if missing_small_redemption_financial_codes:
        with ThreadPoolExecutor(max_workers=min(MAX_FINANCIAL_WORKERS, max(1, len(missing_small_redemption_financial_codes)))) as executor:
            future_map = {
                executor.submit(_fetch_small_redemption_financial_metrics, code): code
                for code in missing_small_redemption_financial_codes
            }
            for future in as_completed(future_map):
                code = future_map[future]
                try:
                    metrics = future.result()
                except Exception:
                    metrics = {
                        "stockNetAssetsYi": None,
                        "stockInterestBearingDebtYi": None,
                        "stockBroadCashYi": None,
                        "stockNetDebtExposureYi": None,
                    }
                current_metrics = financial_cache_items.get(code) if isinstance(financial_cache_items.get(code), dict) else {}
                financial_cache_items[code] = {
                    **current_metrics,
                    **metrics,
                }

    for row in core_ready_rows:
        price = _to_float(row.get("price"))
        if price is None or price >= 100:
            continue
        stock_code = _to_code6(row.get("stockCode"))
        if not stock_code:
            continue

        holder_info = holder_cache_items.get(stock_code) if isinstance(holder_cache_items.get(stock_code), dict) else {}
        financial_metrics = financial_cache_items.get(stock_code) if isinstance(financial_cache_items.get(stock_code), dict) else {}

        row["holderCount"] = _to_positive_float(holder_info.get("holderCount"))
        if row["holderCount"] is not None:
            row["holderCount"] = int(round(float(row["holderCount"])))
        row["holderCountReportPeriod"] = str(holder_info.get("holderCountReportPeriod") or "").strip() or None
        row["holderCountReportSourceUrl"] = str(holder_info.get("holderCountReportSourceUrl") or "").strip() or None
        row["holderCountFallbackUsed"] = holder_info.get("holderCountFallbackUsed") is True
        row["holderCountLastCheckedAt"] = str(holder_info.get("holderCountLastCheckedAt") or "").strip() or None

        row["stockNetAssetsYi"] = _to_float(financial_metrics.get("stockNetAssetsYi"))
        row["stockInterestBearingDebtYi"] = _to_float(financial_metrics.get("stockInterestBearingDebtYi"))
        row["stockBroadCashYi"] = _to_float(financial_metrics.get("stockBroadCashYi"))
        row["stockNetDebtExposureYi"] = _to_float(financial_metrics.get("stockNetDebtExposureYi"))

        row["smallRedemptionYield"] = round(1.0 - (price / 100.0), 6)
        remaining_years = _to_positive_float(row.get("remainingYears"))
        if remaining_years is not None:
            expected_years = remaining_years + 0.5
            row["smallRedemptionExpectedYears"] = round(expected_years, 6)
            row["smallRedemptionAnnualizedYield"] = round((1.0 + row["smallRedemptionYield"]) ** (1.0 / expected_years) - 1.0, 6)
        else:
            row["smallRedemptionExpectedYears"] = None
            row["smallRedemptionAnnualizedYield"] = None

        remaining_size_yi = _to_positive_float(row.get("remainingSizeYi"))
        holder_count = _to_positive_float(row.get("holderCount"))
        if remaining_size_yi is not None and holder_count is not None:
            row["smallRedemptionAmount"] = round((remaining_size_yi * 100000000.0 / holder_count) * 0.825, 2)
            row["smallRedemptionTotalAmount"] = round(row["smallRedemptionAmount"] * holder_count, 2)
        else:
            row["smallRedemptionAmount"] = None
            row["smallRedemptionTotalAmount"] = None

        row.update(_build_small_redemption_option_metrics(row, float(risk_free["rate"])))

    _persist_runtime_metric_cache(aux_cache, as_of_date_text, core_ready_rows)

    return {
        "success": True,
        "data": core_ready_rows,
        "total": len(core_ready_rows),
        "excludedByNameCount": excluded_by_name_count,
        "excludedMissingCoreCount": excluded_missing_core_count,
        "excludedDelistedOrExpiredCount": excluded_delisted_or_expired_count,
        "exclusionRules": [
            "bondName_contains_delist_marker",
            "delist_or_cease_or_maturity_date_lte_today",
            "missing_core_fields(code,price,stockCode,stockPrice,convertPrice)",
        ],
        "updateTime": now_iso,
        "source": "sina_cov_spot+eastmoney_cov+ths",
        "cookieConfigured": cookie_configured,
        "treasuryYield10y": risk_free["percent"],
        "treasuryYield10yDate": risk_free["date"],
        "treasuryYield10ySource": risk_free["source"],
        "assumptions": {
            "bondValue": "pure_bond_value_from_eastmoney_value_analysis_latest_only",
            "issuePrice": 100,
            "volatilityWindows": list(VOL_WINDOWS),
            "primaryWindow": PRIMARY_VOL_WINDOW,
            "optionModel": "american_binomial",
            "formula": "theoretical=bondValue+max(americanCall(max(convertPrice,bondValue/optionQty))-americanCall(redeemTriggerStrike),0)",
            "bondValueSourceRule": "pure_bond_value_from_upstream_api_only",
        },
    }


if __name__ == "__main__":
    print(json.dumps(get_bond_cb_data(), ensure_ascii=False))
