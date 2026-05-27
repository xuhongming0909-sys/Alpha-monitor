# -*- coding: utf-8 -*-
# AI-SUMMARY: 共享IOPV计算公式：A类指数跟踪法 + B类T10持仓加权法
# 对应 INDEX.md §9.3 文件摘要索引
"""Shared IOPV calculation formulas.

Used by strategy/lof_iopv/service.py (realtime) and data_fetch/lof_db/iopv_calculator.py (historical).
"""

from __future__ import annotations

import math
from typing import Any, Optional


def to_float(v):
    try:
        r = float(v)
        return r if math.isfinite(r) else None
    except (TypeError, ValueError):
        return None


def get_base_fx(currency, date_str):
    if currency == "CNY":
        return 1.0
    if not date_str or len(date_str) < 10:
        return None
    try:
        import akshare as ak
        sym = {"USD": "美元", "HKD": "美元"}.get(currency)
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


def calc_a_iopv(nav, etf_change_pct, fx_now, fx_base):
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    fx_ratio = 1.0
    if fx_now and fx_base and fx_base > 0:
        fx_ratio = fx_now / fx_base
    etf_ret = (etf_change_pct or 0) / 100
    iopv = nav * (1 + etf_ret) * fx_ratio
    status = "A类-指数跟踪" if etf_change_pct is not None else "A类-指数跟踪(无ETF数据)"
    return round(iopv, 6), status, {"fxRatio": fx_ratio, "etfRet": etf_ret}


def calc_b_iopv(nav, holdings, stock_ratio, current_prices, nav_date_prices, prev_closes, fx_now, fx_base):
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    if not holdings:
        return None, "持仓缺失", {}
    fx_ratio = 1.0
    if fx_now and fx_base and fx_base > 0:
        fx_ratio = fx_now / fx_base
    if stock_ratio is None:
        return None, "仓位缺失", {}
    total_w = sum(h.get("weight", 0) or 0 for h in holdings)
    if total_w <= 0:
        return round(nav * fx_ratio, 6), "B类-T10(权重为零)", {"fxRatio": fx_ratio}
    weighted_ret = 0.0
    has_price = False
    for h in holdings:
        ticker = h.get("ticker", "")
        w = (h.get("weight", 0) or 0) / total_w
        cur_p = to_float(current_prices.get(ticker))
        base_p = to_float(nav_date_prices.get(ticker))
        if cur_p and base_p and base_p > 0:
            weighted_ret += w * (cur_p / base_p - 1)
            has_price = True
        elif cur_p:
            prev_p = to_float(prev_closes.get(ticker))
            if prev_p and prev_p > 0:
                weighted_ret += w * (cur_p / prev_p - 1)
                has_price = True
    if not has_price:
        return round(nav * fx_ratio, 6), "B类-T10(无股价)", {"fxRatio": fx_ratio, "stockRatio": stock_ratio}
    est = nav * (1 + stock_ratio / 100 * weighted_ret) * fx_ratio
    return round(est, 6), "B类-T10(%d持仓,%.0f%%)" % (len(holdings), stock_ratio), {"fxRatio": fx_ratio, "stockRatio": stock_ratio, "weightedRet": weighted_ret}
