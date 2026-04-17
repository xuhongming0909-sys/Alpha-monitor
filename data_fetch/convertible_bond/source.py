#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Jisilu convertible bond realtime data with theoretical pricing."""

from __future__ import annotations

import json
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
import stock_price_history_db as price_db
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
MAX_VOL_SYNC_WORKERS = max(1, int(_CB_FETCH_CONFIG.get("max_vol_sync_workers") or 8))
REQUIRED_CLOSE_ROWS = max(VOL_WINDOWS) + 1
REQUIRED_HISTORY_BAR_ROWS = max(REQUIRED_CLOSE_ROWS, ATR_WINDOW + 1, max(TURNOVER_AVG_WINDOWS))
MAX_FINANCIAL_WORKERS = max(1, int(_CB_FETCH_CONFIG.get("max_financial_workers") or 10))
INLINE_HISTORY_HYDRATE_LIMIT = max(1, int(_CB_FETCH_CONFIG.get("inline_history_hydrate_limit") or 24))
AUX_CACHE_SCHEMA_VERSION = 1
FORCE_REDEEM_NOTICE_LOOKBACK_DAYS = 120
FORCE_REDEEM_DELIST_FORWARD_DAYS = 120


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
        "historyMetricsByStock": {"date": "", "value": {}},
        "financialMetricsByStock": {"date": "", "value": {}},
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
    metric_fields = ["stockAvgRoe3Y", "stockDebtRatio"]
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


def _persist_runtime_metric_cache(
    aux_cache: Dict[str, Any],
    as_of_date: str,
    rows: list[Dict[str, Any]],
) -> None:
    history_metrics_by_stock: Dict[str, Dict[str, Optional[float]]] = {}
    financial_metrics_by_stock: Dict[str, Dict[str, Optional[float]]] = {}
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
        financial_metrics_by_stock[stock_code] = _pick_row_metrics(row, [
            "stockAvgRoe3Y",
            "stockDebtRatio",
        ])

    aux_cache["historyMetricsByStock"] = {
        "date": as_of_date,
        "value": history_metrics_by_stock,
    }
    aux_cache["financialMetricsByStock"] = {
        "date": as_of_date,
        "value": financial_metrics_by_stock,
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
    for _, record in frame.iterrows():
        trade_date = pd.to_datetime(record.get(date_col), errors="coerce")
        close = _to_float(record.get(close_col))
        if pd.isna(trade_date) or close is None or close <= 0:
            continue
        high = _to_positive_float(record.get(high_col)) if high_col else None
        low = _to_positive_float(record.get(low_col)) if low_col else None
        amount = _to_float(record.get(amount_col)) if amount_col and include_amount else None
        rows.append({
            "date": trade_date.date().isoformat(),
            "close": close,
            "high": high,
            "low": low,
            "amount": amount if amount is not None and amount >= 0 else None,
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
    payload = str(text or "")
    values: list[float] = []
    for hit in re.finditer(r"(\d+(?:\.\d+)?)\s*%", payload):
        try:
            value = float(hit.group(1))
        except Exception:
            continue
        if value > 0:
            values.append(value)
    return values


def _derive_resale_trigger_ratio(row: Dict[str, Any]) -> Optional[float]:
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

    percent_values = [value for value in _extract_percent_values(clause) if 20.0 <= value <= 95.0]
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

    values = [value for value in _extract_percent_values(text) if 80 <= value <= 200]
    if not values:
        return None
    return max(values)


def _should_exclude_by_delist_or_expiry(row: Dict[str, Any], as_of_date: date) -> bool:
    for key in ("delistDate", "ceaseDate"):
        dt = _to_date_str(row.get(key))
        if not dt:
            continue
        try:
            if datetime.fromisoformat(dt).date() <= as_of_date:
                return True
        except Exception:
            continue

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
            payload = requests.get(url, params=params, timeout=20).json()
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
    for _, series in df.iterrows():
        symbol = str(series.get("symbol") or "").strip().lower()
        if not symbol.startswith(("sh", "sz")):
            continue
        code = _to_code6(series.get("code"))
        if not code:
            continue
        amount = _to_float(series.get("amount"))
        volume = _to_float(series.get("volume"))
        result[code] = {
            "bondName": str(series.get("name") or "").strip() or None,
            "price": _to_float(series.get("trade")),
            "changePercent": _to_float(series.get("changepercent")),
            "priceChange": _to_float(series.get("pricechange")),
            "turnoverAmountYi": (amount / 1e8) if amount is not None else None,
            "volumeWanShou": (volume / 1e4) if volume is not None else None,
            "tickTime": str(series.get("ticktime") or "").strip() or None,
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
    for _, series in df.iterrows():
        code = _to_code6(series.get(code_col))
        if not code:
            continue
        result[code] = {
            "bondName": str(series.get(bond_name_col) or "").strip() or None if bond_name_col else None,
            "stockCode": _to_code6(series.get(stock_code_col)) if stock_code_col else None,
            "stockName": str(series.get(stock_name_col) or "").strip() or None if stock_name_col else None,
            "stockPrice": _to_float(series.get(stock_price_col)) if stock_price_col else None,
            "convertPrice": _to_float(series.get(convert_price_col)) if convert_price_col else None,
            "convertValue": _to_float(series.get(convert_value_col)) if convert_value_col else None,
            "premiumRate": _to_float(series.get(premium_rate_col)) if premium_rate_col else None,
            "rating": str(series.get(rating_col) or "").strip() or None if rating_col else None,
            "listingDate": _to_date_str(series.get(listing_date_col)) if listing_date_col else None,
            "issueScaleYi": _to_positive_float(series.get(issue_scale_col)) if issue_scale_col else None,
            "price": _to_float(series.get(price_col)) if price_col else None,
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
    for _, series in df.iterrows():
        code = _to_code6(series.get(code_col))
        if not code:
            continue
        result[code] = {
            "yieldToMaturityPretax": _to_float(series.get(ytm_col)) if ytm_col else None,
            "remainingYears": _to_float(series.get(remaining_years_col)) if remaining_years_col else None,
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
        timeout=20,
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
            timeout=20,
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
    for _, series in df.iterrows():
        code = str(series.get(code_col) or "").strip()
        if not code:
            continue
        result[code] = {
            "listingDate": _to_date_str(series.get(listing_col)) if listing_col in df.columns else None,
            "maturityDate": _to_date_str(series.get(maturity_col)) if maturity_col in df.columns else None,
            "stockCode": _to_code6(series.get(stock_code_col)) if stock_code_col in df.columns else None,
            "stockName": (str(series.get(stock_name_col) or "").strip() or None) if stock_name_col in df.columns else None,
            "convertPrice": _to_positive_float(series.get(convert_price_col)) if convert_price_col in df.columns else None,
        }
    return result


def _build_stock_spot_map_from_a_spot() -> Dict[str, Dict[str, Optional[float]]]:
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
        for _, series in df.iterrows():
            code = _to_code6(series.get(code_col))
            if not code:
                continue
            result[code] = {
                "price": _to_float(series.get(price_col)) if price_col else None,
                "changePercent": _to_float(series.get(change_col)) if change_col else None,
            }
        if result:
            return result

    return {}


def _build_stock_change_map_from_a_spot() -> Dict[str, float]:
    return {
        code: _to_float(snapshot.get("changePercent"))
        for code, snapshot in _build_stock_spot_map_from_a_spot().items()
        if _to_float(snapshot.get("changePercent")) is not None
    }

def _normalize_putback_price_int(value: Any) -> Optional[float]:
    num = _to_float(value)
    if num is None or num <= 0:
        return None
    return float(int(round(num)))


def _american_option_binomial(
    spot: float,
    strike: float,
    years: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    steps: int = 120,
) -> float:
    if spot <= 0 or strike <= 0 or years <= 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
    if volatility <= 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)

    dt = years / max(steps, 1)
    if dt <= 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)

    up = math.exp(volatility * math.sqrt(dt))
    down = 1.0 / up
    disc = math.exp(-risk_free_rate * dt)
    growth = math.exp(risk_free_rate * dt)
    prob = (growth - down) / (up - down)
    prob = min(max(prob, 0.0), 1.0)

    values = []
    for i in range(steps + 1):
        stock_t = spot * (up ** (steps - i)) * (down ** i)
        if option_type == "call":
            values.append(max(stock_t - strike, 0.0))
        else:
            values.append(max(strike - stock_t, 0.0))

    for step in range(steps - 1, -1, -1):
        next_values = []
        for i in range(step + 1):
            hold = disc * (prob * values[i] + (1.0 - prob) * values[i + 1])
            stock_t = spot * (up ** (step - i)) * (down ** i)
            if option_type == "call":
                exercise = max(stock_t - strike, 0.0)
            else:
                exercise = max(strike - stock_t, 0.0)
            next_values.append(max(hold, exercise))
        values = next_values

    return float(values[0]) if values else 0.0


def _bond_floor_value(risk_free_rate: float, years: Optional[float]) -> float:
    if years is None or years <= 0:
        return 100.0
    base = max(1.0 + risk_free_rate, 1e-6)
    return 100.0 / (base ** years)


def _calc_volatility_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    symbol = str(stock_code or "").strip()
    if not symbol:
        return _blank_volatility_metrics()

    # 波动率严格按历史库最近 N 个收益率样本计算，因此至少需要 N+1 个收盘价。
    close_series = pd.Series(price_db.load_recent_closes(symbol, REQUIRED_CLOSE_ROWS), dtype="float64")

    if len(close_series) < 2:
        return _blank_volatility_metrics()

    returns = np.log(close_series / close_series.shift(1)).dropna()
    metrics: Dict[str, Optional[float]] = {}
    for window in VOL_WINDOWS:
        key = f"volatility{window}"
        required_returns = max(2, window)
        if len(returns) < required_returns:
            metrics[key] = None
            continue
        sample = returns.tail(required_returns)
        std = float(sample.std(ddof=1)) if len(sample) > 1 else 0.0
        metrics[key] = std * math.sqrt(TRADING_DAYS_PER_YEAR)
    return _with_primary_volatility_aliases(metrics)


def _metrics_ready(metrics: Dict[str, Any]) -> bool:
    if not isinstance(metrics, dict):
        return False
    return _to_float(metrics.get(f"volatility{PRIMARY_VOL_WINDOW}")) is not None


def _calc_stock_history_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    # 统一从正股历史库读取波动率 / ATR / 均成交额，避免页面字段各走各的临时口径。
    symbol = str(stock_code or "").strip()
    metrics: Dict[str, Optional[float]] = {
        **_blank_volatility_metrics(),
        "stockAtr20": None,
        "stockAvgTurnoverAmount20Yi": None,
        "stockAvgTurnoverAmount5Yi": None,
    }

    if not symbol:
        return metrics

    bars = price_db.load_recent_bars(symbol, REQUIRED_HISTORY_BAR_ROWS)
    close_series = pd.Series(
        [item.get("close") for item in bars if _to_float(item.get("close")) is not None],
        dtype="float64",
    )

    if len(close_series) >= 2:
        returns = np.log(close_series / close_series.shift(1)).dropna()
        for window in VOL_WINDOWS:
            key = f"volatility{window}"
            required_returns = max(2, window)
            if len(returns) < required_returns:
                continue
            sample = returns.tail(required_returns)
            std = float(sample.std(ddof=1)) if len(sample) > 1 else 0.0
            metrics[key] = std * math.sqrt(TRADING_DAYS_PER_YEAR)

    rich_bars = [
        {
            "close": _to_float(item.get("close")),
            "high": _to_float(item.get("high")),
            "low": _to_float(item.get("low")),
            "amount": _to_float(item.get("amount")),
        }
        for item in bars
        if _to_float(item.get("close")) is not None
    ]

    true_ranges: list[float] = []
    prev_close: Optional[float] = None
    for item in rich_bars:
        close = item["close"]
        high = item["high"]
        low = item["low"]
        if high is not None and low is not None:
            if prev_close is None:
                true_ranges.append(high - low)
            else:
                true_ranges.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
        prev_close = close
    if len(true_ranges) >= ATR_WINDOW:
        metrics["stockAtr20"] = float(sum(true_ranges[-ATR_WINDOW:]) / ATR_WINDOW)

    valid_amounts = [item["amount"] for item in rich_bars if item["amount"] is not None]
    if len(valid_amounts) >= 20:
        metrics["stockAvgTurnoverAmount20Yi"] = float(sum(valid_amounts[-20:]) / 20 / 1e8)
    if len(valid_amounts) >= 5:
        metrics["stockAvgTurnoverAmount5Yi"] = float(sum(valid_amounts[-5:]) / 5 / 1e8)
    return _with_primary_volatility_aliases(metrics)


def _metrics_ready(metrics: Dict[str, Any]) -> bool:
    if not isinstance(metrics, dict):
        return False
    if _to_float(metrics.get(f"volatility{PRIMARY_VOL_WINDOW}")) is None:
        return False
    if _to_float(metrics.get("stockAtr20")) is None:
        return False
    if _to_float(metrics.get("stockAvgTurnoverAmount20Yi")) is None:
        return False
    if _to_float(metrics.get("stockAvgTurnoverAmount5Yi")) is None:
        return False
    return True


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
    spot = _to_float(row.get("stockPrice"))
    market_price = _to_float(row.get("price"))
    convert_price = _to_float(row.get("convertPrice"))
    remaining_years = _to_float(row.get("remainingYears"))

    # 纯债价值只允许使用真实上游接口返回值；缺失时必须 truthfully 降级，不能再本地折现兜底。
    market_pure_bond = _to_positive_float(row.get("pureBondValue"))
    bond_value = market_pure_bond
    option_qty = None
    if convert_price and convert_price > 0:
        option_qty = 100.0 / convert_price
    redeem_trigger_price = _to_float(row.get("redeemTriggerPrice"))
    is_below_redeem_trigger = (
        spot is not None
        and redeem_trigger_price is not None
        and redeem_trigger_price > 0
        and spot < redeem_trigger_price
    )
    pricing_bucket = (
        "below_redeem_trigger"
        if is_below_redeem_trigger
        else "at_or_above_redeem_trigger"
        if (
            spot is not None
            and redeem_trigger_price is not None
            and redeem_trigger_price > 0
        )
        else "unknown"
    )
    # 强赎后的上方收益按“双看涨价差”收口：
    # 多头看涨执行价取 max(转股价, 债底折算行权价)，空头看涨执行价取强赎价；
    # 缺少真实强赎价时，理论价值保持为空，不再退回旧的单看涨/看涨减看跌分支。
    pricing_formula = "bond+callspread"

    result: Dict[str, Optional[float]] = {
        "bondValue": round(bond_value, 4) if bond_value is not None else None,
        "optionQty": round(option_qty, 6) if option_qty else None,
        "isStockBelowRedeemTrigger": bool(is_below_redeem_trigger),
        "pricingBucket": pricing_bucket,
        "pricingFormula": pricing_formula,
    }

    for window in VOL_WINDOWS:
        vol = _to_float(row.get(f"volatility{window}"))
        call_strike = None
        redeem_call_strike = None
        theoretical = None
        call_value = None
        put_value = None
        long_call_value = None
        short_call_value = None
        call_spread_value = None
        gap = None
        premium_rate = None

        if option_qty and option_qty > 0 and convert_price and convert_price > 0:
            # 用户确认理论定价口径：
            # 1) 对应股数 = 100 / 转股价；
            # 2) 多头看涨执行价 = max(转股价, 债底折算行权价)；
            # 3) 空头看涨执行价固定等于真实强赎价；
            # 4) 净期权价值 = max(long_call - short_call, 0)。
            bond_floor_strike = (bond_value / option_qty) if bond_value is not None and option_qty > 0 else None
            strike_candidates = [value for value in [convert_price, bond_floor_strike] if value is not None and value > 0]
            call_strike = max(strike_candidates) if strike_candidates else None
            redeem_call_strike = redeem_trigger_price if redeem_trigger_price and redeem_trigger_price > 0 else None
            if (
                bond_value is not None
                and spot is not None
                and vol is not None
                and remaining_years is not None
                and call_strike is not None
                and redeem_call_strike is not None
            ):
                long_call_unit = _american_option_binomial(spot, call_strike, remaining_years, risk_free_rate, vol, "call")
                short_call_unit = _american_option_binomial(
                    spot, redeem_call_strike, remaining_years, risk_free_rate, vol, "call"
                )
                long_call_value = long_call_unit * option_qty
                short_call_value = short_call_unit * option_qty
                call_spread_value = max(long_call_value - short_call_value, 0.0)
                call_value = call_spread_value
                put_value = None

                theoretical = bond_value + call_spread_value
                if market_price is not None:
                    gap = theoretical - market_price
                    if market_price != 0:
                        premium_rate = (gap / market_price) * 100.0

        suffix = str(window)
        result[f"callStrike{suffix}"] = round(call_strike, 4) if call_strike is not None else None
        result[f"redeemCallStrike{suffix}"] = (
            round(redeem_call_strike, 4) if redeem_call_strike is not None else None
        )
        result[f"putStrike{suffix}"] = None
        result[f"longCallOptionValue{suffix}"] = round(long_call_value, 4) if long_call_value is not None else None
        result[f"shortCallOptionValue{suffix}"] = round(short_call_value, 4) if short_call_value is not None else None
        result[f"callSpreadOptionValue{suffix}"] = (
            round(call_spread_value, 4) if call_spread_value is not None else None
        )
        result[f"callOptionValue{suffix}"] = round(call_value, 4) if call_value is not None else None
        result[f"putOptionValue{suffix}"] = None
        result[f"theoreticalPrice{suffix}"] = round(theoretical, 4) if theoretical is not None else None
        result[f"theoreticalGap{suffix}"] = round(gap, 4) if gap is not None else None
        result[f"theoreticalPremiumRate{suffix}"] = round(premium_rate, 4) if premium_rate is not None else None

    return result


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


def get_bond_cb_data() -> Dict[str, Any]:
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
    stock_change_cache_items: Dict[str, Any] = {}
    cov_basic_items = _load_daily_cached_map(aux_cache, "covBasicMap", as_of_date_text, _build_cov_basic_map)
    cb_jsl_items = _build_cb_jsl_map(jisilu_cookie)
    ths_cov_info_items = _load_daily_cached_map(aux_cache, "thsCovInfoMap", as_of_date_text, _build_ths_cov_info_map)
    pure_bond_value_items = _load_daily_cached_map(aux_cache, "pureBondMap", as_of_date_text, _build_latest_pure_bond_map)
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
            "turnoverAmountYi": turnover_amount_yi,
            "turnoverRate": None,
            "stockAtr20": None,
            "stockAvgTurnoverAmount20Yi": None,
            "stockAvgTurnoverAmount5Yi": None,
            "yieldToMaturityPretax": None,
            "doubleLow": double_low,
            "stockAvgRoe3Y": None,
            "stockDebtRatio": None,
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
        ready_stock_metric_count = sum(
            1
            for metrics in vol_cache_items.values()
            if _metrics_ready(metrics)
        )
        hydrate_targets = unique_missing_stocks
        # 当 250 日历史就绪覆盖率异常偏低时，说明历史库仍停留在旧窗口阶段；
        # 这里直接做一次真实补数，避免普通读链路整批退化成理论价/波动率全空。
        if ready_stock_metric_count > 10 and len(unique_missing_stocks) > INLINE_HISTORY_HYDRATE_LIMIT:
            hydrate_targets = unique_missing_stocks[:INLINE_HISTORY_HYDRATE_LIMIT]
        if hydrate_targets:
            _hydrate_stock_history_for_symbols(hydrate_targets)
        # 普通读链路优先复用已有历史库；若 250 日样本明显缺失，则对缺口标的做最小真实补数。
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


