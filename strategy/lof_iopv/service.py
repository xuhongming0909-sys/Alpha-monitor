# -*- coding: utf-8 -*-
"""QDII LOF IOPV 双引擎估值。A类指数跟踪法 + B类T10持仓加权法。"""

from __future__ import annotations

import math
from typing import Any, Optional

import requests

from shared.market_service import get_fx_rates
from shared.models.service_result import build_success
from shared.time.shanghai_time import now_iso

from strategy.lof_iopv.classifier import get_calc_mode


def _to_float(v: Any) -> Optional[float]:
    try:
        r = float(v)
        return r if math.isfinite(r) else None
    except (TypeError, ValueError):
        return None


def _get_base_fx(currency: str, date_str: str) -> Optional[float]:
    if currency == "CNY":
        return 1.0
    if not date_str or len(date_str) < 10:
        return None
    try:
        import akshare as ak
        sym = {"USD": "美元", "HKD": "港币"}.get(currency)
        if not sym:
            return None
        from datetime import datetime, timedelta
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        start = (dt - timedelta(days=10)).strftime("%Y%m%d")
        end = dt.strftime("%Y%m%d")
        df = ak.currency_boc_sina(symbol=sym, start_date=start, end_date=end)
        if df is not None and not df.empty:
            return float(df.iloc[-1]["中间价"])
    except Exception:
        pass
    return None


def _calc_a(row: dict, fx_now: Optional[float]) -> tuple:
    """A类: IOPV = NAV * (1 + etf_ret) * fx_ratio。当前简化为 NAV * fx_ratio。"""
    nav = _to_float(row.get("nav"))
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    currency = row.get("currency", "CNY").upper()
    fx_ratio = 1.0
    if currency != "CNY" and fx_now and fx_now > 0:
        base = _get_base_fx(currency, row.get("navDate", "")[:10])
        if base and base > 0:
            fx_ratio = fx_now / base
    return round(nav * fx_ratio, 6), "A类-指数跟踪", {"fxRatio": fx_ratio}


def _calc_b(row: dict, fx_now: Optional[float]) -> tuple:
    """B类: T10持仓加权。est = stock_ratio * Σ(w_i * ret_i * fx_i)。"""
    nav = _to_float(row.get("nav"))
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    holdings = row.get("holdings") or []
    if not holdings:
        return None, "持仓缺失", {}
    currency = row.get("currency", "CNY").upper()
    fx_ratio = 1.0
    if currency != "CNY" and fx_now and fx_now > 0:
        base = _get_base_fx(currency, row.get("navDate", "")[:10])
        if base and base > 0:
            fx_ratio = fx_now / base
    stock_ratio = _to_float(row.get("stockPosition")) or 90.0
    total_w = sum(h.get("weight", 0) or 0 for h in holdings)
    if total_w <= 0:
        return nav * fx_ratio, "B类-T10(权重为零)", {"fxRatio": fx_ratio, "stockRatio": stock_ratio}
    # 当前简化: 返回 NAV * fx_ratio（需要K线历史价格才能算真实收益率）
    est = nav * fx_ratio
    return round(est, 6), f"B类-T10({len(holdings)}持仓,仓位{stock_ratio:.0f}%)", {"fxRatio": fx_ratio, "stockRatio": stock_ratio}


def _is_paused(status: Any) -> bool:
    return "暂停" in str(status or "")


def _monitor_pools(row: dict) -> tuple:
    premium = row.get("premiumRate")
    turnover = _to_float(row.get("turnoverWan"))
    paused = _is_paused(row.get("applyStatus"))
    lim = unlim = False
    if not paused and premium is not None and turnover is not None:
        if "限" in str(row.get("applyStatus") or "") and premium > 1.0 and turnover > 100:
            lim = True
        if ("不" in str(row.get("applyStatus") or "") or "正常" in str(row.get("applyStatus") or "")) and abs(premium) > 5.0 and turnover > 100:
            unlim = True
    return lim, unlim


def build_lof_iopv_response(fetch_payload: dict, records: list) -> dict:
    if not fetch_payload or fetch_payload.get("success") is False:
        return build_success({"groups": [], "rows": [], "sourceSummary": {}}, updateTime=now_iso(), source="lof_iopv", error=(fetch_payload or {}).get("error", "fetch_failed"))

    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}

    rows = fetch_payload.get("data") or []
    result = []

    for row in rows:
        est = row.get("estimation", "A")
        currency = row.get("currency", "CNY").upper()
        fx_now = fx_rates.get(currency)

        if est == "B":
            iopv, status, details = _calc_b(row, fx_now)
        else:
            iopv, status, details = _calc_a(row, fx_now)

        price = _to_float(row.get("price"))
        premium = round((price / iopv - 1) * 100, 2) if (iopv and price and price > 0 and iopv > 0) else None

        # 估值方法
        calc_method = "指数跟踪法" if est == "A" else "T10持仓法"
        # 仓位: A类反推, B类实际
        stock_pos = row.get("stockPosition")
        if est == "A" and iopv and row.get("nav") and row["nav"] > 0:
            # A类反推仓位: (IOPV/NAV - 1) / etf_ret
            stock_pos = round((iopv / row["nav"] - 1) * 100, 2) if iopv != row["nav"] else None
        # 溢价状态
        if premium is not None:
            premium_status = "溢价" if premium > 0.5 else ("折价" if premium < -0.5 else "平价")
        else:
            premium_status = None
        # 基准指数
        benchmark = row.get("etf") or f"Top10({len(row.get('holdings', []) or [])})"

        # 申购状态+限额
        apply_status = row.get("applyStatus") or ""
        min_amt = row.get("minAmt")
        if min_amt:
            apply_status = f"{apply_status}(限额{min_amt}万)"

        # 估值核心: A类=ETF标的, B类=前十大持仓摘要
        if est == "A":
            calc_core = row.get("etf") or "未知标的"
        else:
            holdings = row.get("holdings") or []
            if holdings:
                top3 = [f"{h.get('name','')}{h.get('weight',0)}%" for h in holdings[:3]]
                calc_core = "+".join(top3) + (f"...等{len(holdings)}只" if len(holdings) > 3 else "")
            else:
                calc_core = "无持仓数据"

        result.append({
            "code": row.get("code"),
            "name": row.get("name"),
            "nav": row.get("nav"),
            "navDate": row.get("navDate"),
            "price": price,
            "iopv": iopv,
            "premiumRate": premium,
            "applyStatus": apply_status,
            "shareIncrease": row.get("shareIncrease"),
            "shareTotal": row.get("shareTotal"),
            "applyFee": row.get("applyFee"),
            "redeemFee": row.get("redeemFee"),
            "custodianFee": row.get("custodianFee"),
            "fundCompany": row.get("fundCompany"),
            "calcCore": calc_core,
            "stockPosition": stock_pos,
            "r2": _BACKTEST_RESULTS.get(code, {}).get("r2"),
            "mae": _BACKTEST_RESULTS.get(code, {}).get("mae"),
            "maxErr": _BACKTEST_RESULTS.get(code, {}).get("maxErr"),
            "samplePeriod": _BACKTEST_RESULTS.get(code, {}).get("samplePeriod"),
        })

    for r in result:
        lim, unlim = _monitor_pools(r)
        r["limitedMonitorEligible"] = lim
        r["unlimitedMonitorEligible"] = unlim

    result.sort(key=lambda r: 9999.0 if r.get("premiumRate") is None else -abs(r["premiumRate"]))
    limited = [r for r in result if r.get("limitedMonitorEligible")]
    unlimited = [r for r in result if r.get("unlimitedMonitorEligible")]

    src = dict(fetch_payload.get("sourceSummary") or {})
    src["computedRows"] = sum(1 for r in result if r.get("iopv") is not None)
    src["totalRows"] = len(result)
    src["limitedMonitorCount"] = len(limited)
    src["unlimitedMonitorCount"] = len(unlimited)

    return build_success({
        "groups": [{"key": "qdii", "label": "QDII"}],
        "defaultGroup": "qdii",
        "rows": result,
        "limitedMonitorRows": limited,
        "unlimitedMonitorRows": unlimited,
        "sourceSummary": src,
    }, updateTime=fetch_payload.get("updateTime") or now_iso(), source="lof_iopv")