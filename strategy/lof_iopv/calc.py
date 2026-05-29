# -*- coding: utf-8 -*-
# AI-SUMMARY: 共享IOPV计算公式：指数型(ETF映射) + 主动型(T10持仓加权)
# 对应 INDEX.md §9.3 文件摘要索引
"""Shared IOPV calculation formulas.

Used by strategy/lof_iopv/service.py (realtime) and strategy/lof_iopv/backtest_v2.py (historical).
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


def calc_iopv(nav, holdings, stock_ratio, current_prices, nav_date_prices,
              prev_closes, fx_now, fx_base):
    """Unified IOPV estimation for both A-class (index ETF) and B-class (holdings).

    Formula:
      1. weighted_ret = sum(weight_i * ret_i) for each holding
      2. nav_change = weighted_ret * stock_ratio / t10_total / 100
      3. IOPV = NAV * (1 + nav_change) * fx_ratio

    Args:
        nav: Fund NAV from disclosure date
        holdings: List of {"ticker": str, "weight": float}
        stock_ratio: Stock position % (e.g. 90 means 90%)
        current_prices: Target date prices {ticker: price}
        nav_date_prices: NAV date prices {ticker: price}
        prev_closes: Previous closes for fallback {ticker: price}
        fx_now: Target date FX rate
        fx_base: NAV date FX rate

    Returns:
        (estimated_nav, status_str, details_dict)
    """
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}

    fx_ratio = 1.0
    if fx_now and fx_base and fx_base > 0:
        fx_ratio = fx_now / fx_base

    if not holdings:
        return round(nav * fx_ratio, 6), "无持仓", {}

    t10_total = sum(h.get("weight") or 0 for h in holdings)
    if t10_total <= 0:
        return round(nav * fx_ratio, 6), "权重为零", {"fxRatio": fx_ratio}

    # Step 1: weighted returns (only count holdings with valid prices)
    weighted_ret = 0.0
    weighted_w_sum = 0.0  # sum of weights for holdings with price data
    has_price = False
    for h in holdings:
        ticker = h.get("ticker", "")
        w = h.get("weight") or 0
        cur_p = to_float(current_prices.get(ticker))
        base_p = to_float(nav_date_prices.get(ticker))
        if cur_p and base_p and base_p > 0:
            weighted_ret += w * (cur_p / base_p - 1)
            weighted_w_sum += w
            has_price = True
        elif cur_p:
            prev_p = to_float(prev_closes.get(ticker))
            if prev_p and prev_p > 0:
                weighted_ret += w * (cur_p / prev_p - 1)
                weighted_w_sum += w
                has_price = True

    if not has_price:
        return None, "无股价", {"fxRatio": fx_ratio, "stockRatio": stock_ratio}

    # Step 2: normalize by weight sum of holdings with prices
    if weighted_w_sum <= 0:
        return None, "权重为零", {"fxRatio": fx_ratio}
    nav_change = weighted_ret * stock_ratio / weighted_w_sum / 100

    # Step 3: IOPV
    est = nav * (1 + nav_change) * fx_ratio
    return round(est, 6), "T10(%d/%d持仓,%.0f%%)" % (sum(1 for h in holdings if to_float(current_prices.get(h.get("ticker",""))) is not None), len(holdings), stock_ratio), {
        "fxRatio": fx_ratio,
        "stockRatio": stock_ratio,
        "weightedRet": weighted_ret,
        "weightedWSum": weighted_w_sum,
        "navChange": nav_change,
    }
