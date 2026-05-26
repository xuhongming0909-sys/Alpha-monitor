# -*- coding: utf-8 -*-
"""QDII LOF IOPV 估值策略服务。

双引擎估值：A类指数跟踪法 + B类T10持仓法。
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from shared.config.script_config import get_config
from shared.market_service import get_fx_rates, get_quotes
from shared.models.service_result import build_success
from shared.time.shanghai_time import now_iso

from strategy.lof_iopv.classifier import classify_fund, get_calc_mode

_CONFIG = get_config()

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})


def _to_float(value: Any) -> Optional[float]:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _get_base_fx(currency: str, date_str: str) -> Optional[float]:
    """获取指定日期央行中间价。"""
    if currency == "CNY":
        return 1.0
    if not date_str or len(date_str) < 10:
        return None
    try:
        import akshare as ak
        symbol_map = {"USD": "美元/人民币", "HKD": "港币/人民币"}
        symbol = symbol_map.get(currency)
        if not symbol:
            return None
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        start = (dt - timedelta(days=10)).strftime("%Y%m%d")
        end = dt.strftime("%Y%m%d")
        df = ak.currency_boc_sina(symbol=symbol, start_date=start, end_date=end)
        if df is not None and not df.empty:
            return float(df.iloc[-1]["中间价"])
    except Exception:
        pass
    return None


def _calc_a_type(row: dict, fx_now: Optional[float]) -> tuple:
    """A类：指数跟踪法。NAV_t = NAV_base * (1 + index_change) * (1 + fx_change)"""
    nav = _to_float(row.get("nav"))
    nav_date = str(row.get("navDate") or "")[:10]
    currency = str(row.get("currency") or "CNY").upper()

    if nav is None or nav <= 0:
        return None, "NAV缺失", {}

    # A类基金一般用指数涨跌来估算
    # 但当前版本先用NAV直接返回，后续可接入指数行情
    fx_ratio = 1.0
    if currency != "CNY" and fx_now and fx_now > 0:
        fx_base = _get_base_fx(currency, nav_date)
        if fx_base and fx_base > 0:
            fx_ratio = fx_now / fx_base

    iopv = nav * fx_ratio
    status = "A类-指数跟踪"
    return round(iopv, 6), status, {"fxRatio": fx_ratio}


def _calc_b_type(row: dict, fx_now: Optional[float]) -> tuple:
    """B类：T10持仓加权法。NAV_t = NAV_base * [1 + position_ratio * sum(w_i * R_i)] * fx_ratio"""
    nav = _to_float(row.get("nav"))
    nav_date = str(row.get("navDate") or "")[:10]
    currency = str(row.get("currency") or "CNY").upper()
    holdings = row.get("holdings") or []
    current_prices = row.get("currentPrices") or {}

    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    if not holdings:
        return None, "持仓数据缺失", {}

    fx_ratio = 1.0
    if currency != "CNY" and fx_now and fx_now > 0:
        fx_base = _get_base_fx(currency, nav_date)
        if fx_base and fx_base > 0:
            fx_ratio = fx_now / fx_base

    # 计算持仓加权收益
    stock_ratio = 90.0  # 默认仓位
    total_wr = 0.0
    total_w = 0.0
    valid = 0
    hd = []

    for h in holdings:
        ticker = h.get("ticker", "")
        weight = _to_float(h.get("weight")) or 0.0
        price = _to_float(current_prices.get(ticker))

        if price is None or weight <= 0:
            hd.append({"ticker": ticker, "name": h.get("name", ""), "status": "no_price"})
            continue

        # 简化：用价格本身作为权重贡献（实际应用历史价格计算收益率）
        total_wr += weight * 0.0  # 占位，需要历史价格
        total_w += weight
        valid += 1
        hd.append({"ticker": ticker, "name": h.get("name", ""), "status": "ok", "price": price, "weight": weight})

    if valid == 0:
        return None, "无有效持仓", {"holdings": hd, "fxRatio": fx_ratio}

    # 简化版本：先返回NAV * fx_ratio
    iopv = nav * fx_ratio
    status = f"B类-T10({valid}/{len(holdings)})"
    return round(iopv, 6), status, {"holdings": hd, "fxRatio": fx_ratio}


def _calc_fof_type(row: dict, fx_now: Optional[float]) -> tuple:
    """FOF类：多ETF拟合。当前返回NAV。"""
    nav = _to_float(row.get("nav"))
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    return nav, "FOF-NAV", {"fxRatio": 1.0}


def _is_paused_apply(status: Any) -> bool:
    """判断是否暂停申购。"""
    return "暂停" in str(status or "")


def _classify_monitor_pools(row: dict) -> tuple:
    """根据 spec 规则判定限购池/非限池资格。"""
    limited_eligible = False
    unlimited_eligible = False
    paused = _is_paused_apply(row.get("applyStatus"))
    premium = row.get("premiumRate")
    turnover = _to_float(row.get("turnoverWan"))

    if not paused and premium is not None and turnover is not None:
        has_limit = "限" in str(row.get("applyStatus") or "")
        if has_limit and premium > 1.0 and turnover > 100:
            limited_eligible = True
        not_limited = "不" in str(row.get("applyStatus") or "") or "正常" in str(row.get("applyStatus") or "")
        if not_limited and abs(premium) > 5.0 and turnover > 100:
            unlimited_eligible = True

    return limited_eligible, unlimited_eligible


def build_lof_iopv_response(fetch_payload: dict, records: list) -> dict:
    """构建 LOF IOPV 估值响应。"""
    if not fetch_payload or fetch_payload.get("success") is False:
        error = (fetch_payload or {}).get("error", "fetch_failed")
        return build_success({"groups": [], "rows": [], "sourceSummary": {}}, updateTime=now_iso(), source="lof_iopv", error=error)

    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}

    rows = fetch_payload.get("data") or []
    result_rows = []

    for row in rows:
        estimation = row.get("estimationMethod", "ETF")
        currency = str(row.get("currency") or "CNY").upper()
        fx_now = fx_rates.get(currency)

        if estimation == "T10":
            fund_type = "B"
            iopv, calc_status, details = _calc_b_type(row, fx_now)
        elif estimation == "FOF":
            fund_type = "C"
            iopv, calc_status, details = _calc_fof_type(row, fx_now)
        else:
            fund_type = "A"
            iopv, calc_status, details = _calc_a_type(row, fx_now)

        price = _to_float(row.get("price"))
        premium_rate = None
        if iopv is not None and price and price > 0 and iopv > 0:
            premium_rate = round((price / iopv - 1) * 100, 2)

        result_rows.append({
            "code": row.get("code"),
            "name": row.get("name"),
            "market": "",
            "marketLabel": "QDII",
            "currency": currency,
            "fundType": fund_type,
            "groupKey": "qdii",
            "price": price,
            "nav": row.get("nav"),
            "navDate": row.get("navDate"),
            "iopv": iopv,
            "premiumRate": premium_rate,
            "applyFee": row.get("applyFee"),
            "applyStatus": row.get("applyStatus"),
            "redeemFee": row.get("redeemFee"),
            "redeemStatus": row.get("redeemStatus"),
            "custodianFee": row.get("custodianFee"),
            "fundCompany": row.get("fundCompany"),
            "shareAmountWan": row.get("shareAmountWan"),
            "shareAmountIncreaseWan": row.get("shareAmountIncreaseWan"),
            "turnoverWan": row.get("turnoverWan"),
            "changeRate": row.get("changeRate"),
            "calcMode": get_calc_mode(fund_type),
            "calcStatus": calc_status,
            "stockPosition": row.get("stockPosition"),
            "indexName": row.get("indexName"),
            "indexIncreaseRate": row.get("indexIncreaseRate"),
            "holdings": details.get("holdings") if isinstance(details, dict) else None,
            "backtest": {"r2": None, "mae": None, "maxErr": None, "samplePeriod": None},
            "currentFxRate": fx_now,
            "fxRatio": details.get("fxRatio") if isinstance(details, dict) else None,
            "marketGroup": "qdii",
        })

    # 标记监控池资格
    for r in result_rows:
        lim, unlim = _classify_monitor_pools(r)
        r["limitedMonitorEligible"] = lim
        r["unlimitedMonitorEligible"] = unlim

    result_rows.sort(key=lambda r: 9999.0 if r.get("premiumRate") is None else -abs(r["premiumRate"]))

    limited_rows = [r for r in result_rows if r.get("limitedMonitorEligible")]
    unlimited_rows = [r for r in result_rows if r.get("unlimitedMonitorEligible")]

    source_summary = dict(fetch_payload.get("sourceSummary") or {})
    source_summary["computedRows"] = sum(1 for r in result_rows if r.get("iopv") is not None)
    source_summary["totalRows"] = len(result_rows)
    source_summary["limitedMonitorCount"] = len(limited_rows)
    source_summary["unlimitedMonitorCount"] = len(unlimited_rows)

    return build_success({
        "groups": [{"key": "qdii", "label": "QDII"}],
        "defaultGroup": "qdii",
        "rows": result_rows,
        "limitedMonitorRows": limited_rows,
        "unlimitedMonitorRows": unlimited_rows,
        "sourceSummary": source_summary,
    }, updateTime=fetch_payload.get("updateTime") or now_iso(), source=fetch_payload.get("source") or "lof_iopv")