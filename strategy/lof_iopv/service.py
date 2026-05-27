# -*- coding: utf-8 -*-
"""QDII LOF IOPV 双引擎估值。A类指数跟踪法 + B类T10持仓加权法。"""

from __future__ import annotations

import math
from typing import Any, Optional

import requests

from shared.market_service import get_fx_rates
from shared.models.service_result import build_success
from shared.time.shanghai_time import now_iso

import os as _os
import json as _json

from strategy.lof_iopv.classifier import get_calc_mode

# 加载回test结果
_BACKTEST_DIR = _os.path.join(_os.path.dirname(__file__), "..", "..", "runtime_data", "backtest")
_BACKTEST_RESULTS = {}
# 加载回测结果：优先加载合并文件，再加载各子文件
for _fname in ("results.json",):
    _fpath = _os.path.join(_BACKTEST_DIR, _fname)
    if _os.path.exists(_fpath):
        try:
            with open(_fpath, "r", encoding="utf-8") as _f:
                _data = _json.load(_f)
                if isinstance(_data, list):
                    for _r in _data:
                        if _r.get("code") and _r["code"] not in _BACKTEST_RESULTS:
                            _BACKTEST_RESULTS[_r["code"]] = _r
                elif isinstance(_data, dict):
                    for _k, _v in _data.items():
                        if _k not in _BACKTEST_RESULTS:
                            _BACKTEST_RESULTS[_k] = _v
        except Exception:
            pass


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
    """A类: IOPV = NAV * (1 + etf_ret/100) * fx_ratio。"""
    nav = _to_float(row.get("nav"))
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    currency = row.get("currency", "CNY").upper()
    fx_ratio = 1.0
    if currency != "CNY" and fx_now and fx_now > 0:
        base = _get_base_fx(currency, row.get("navDate", "")[:10])
        if base and base > 0:
            fx_ratio = fx_now / base
    # ETF涨跌幅（百分比 → 小数）
    etf_change_pct = _to_float(row.get("etfChange"))
    etf_ret = etf_change_pct / 100 if etf_change_pct is not None else 0.0
    iopv = nav * (1 + etf_ret) * fx_ratio
    status = "A类-指数跟踪" if etf_change_pct is not None else "A类-指数跟踪(无ETF数据)"
    return round(iopv, 6), status, {"fxRatio": fx_ratio, "etfRet": etf_ret}


def _calc_b(row: dict, fx_now: Optional[float]) -> tuple:
    """B类: T10持仓加权。IOPV = NAV * (1 + stock_ratio * Σ(w_i * ret_i)) * fx_ratio"""
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
    stock_ratio = _to_float(row.get("stockPosition"))
    if stock_ratio is None:
        return None, "仓位缺失", {}
    total_w = sum(h.get("weight", 0) or 0 for h in holdings)
    if total_w <= 0:
        return round(nav * fx_ratio, 6), "B类-T10(权重为零)", {"fxRatio": fx_ratio}
    # 持仓加权收益率
    current_prices = row.get("currentPrices") or {}
    prev_closes = row.get("holdingsPrevClose") or {}
    weighted_ret = 0.0
    has_price = False
    for h in holdings:
        ticker = h.get("ticker", "")
        w = (h.get("weight", 0) or 0) / total_w
        cur_p = _to_float(current_prices.get(ticker))
        prev_p = _to_float(prev_closes.get(ticker))
        if cur_p and prev_p and prev_p > 0:
            weighted_ret += w * (cur_p / prev_p - 1)
            has_price = True
    if not has_price:
        return round(nav * fx_ratio, 6), "B类-T10(无股价)", {"fxRatio": fx_ratio, "stockRatio": stock_ratio}
    est = nav * (1 + stock_ratio / 100 * weighted_ret) * fx_ratio
    return round(est, 6), f"B类-T10({len(holdings)}持仓,{stock_ratio:.0f}%)", {"fxRatio": fx_ratio, "stockRatio": stock_ratio, "weightedRet": weighted_ret}


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
        premium = round((price / iopv - 1) * 100, 3) if (iopv and price and price > 0 and iopv > 0) else None

        # 估值方法
        calc_method = "指数跟踪法" if est == "A" else "T10持仓法"
        # 仓位: A类反推, B类实际
        stock_pos = row.get("stockPosition")
        if est == "A" and iopv and row.get("nav") and row["nav"] > 0:
            # A类反推仓位: (IOPV/NAV - 1) / etf_ret
            stock_pos = round((iopv / row["nav"] - 1) * 100, 3) if iopv != row["nav"] else None
        # 溢价状态
        if premium is not None:
            premium_status = "溢价" if premium > 0.5 else ("折价" if premium < -0.5 else "平价")
        else:
            premium_status = None
        # 基准指数
        benchmark = row.get("etf") or f"Top10({len(row.get('holdings', []) or [])})"

        # 申购状态：暂停申购 / 开放申购 / 限额XXXX
        apply_status = row.get("applyStatus") or ""
        daily_limit = row.get("dailyLimit")
        if apply_status == "限大额" and daily_limit is not None and daily_limit < 1e10:
            apply_status = f"限额{int(daily_limit)}"
        elif apply_status == "暂停申购":
            apply_status = "暂停申购"
        elif apply_status == "开放申购":
            apply_status = "开放申购"
        elif not apply_status:
            apply_status = "--"

        # 估值标的: A类=ETF标的代码, B类="前十大"
        if est == "A":
            calc_core = row.get("etf") or "未知标的"
        else:
            calc_core = "前十大"

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
            "calcTarget": calc_core,
            "stockPosition": stock_pos,
            "r2": _BACKTEST_RESULTS.get(row.get("code"), {}).get("r2"),
            "mae": _BACKTEST_RESULTS.get(row.get("code"), {}).get("mae"),
            "maxErr": _BACKTEST_RESULTS.get(row.get("code"), {}).get("maxErr"),
            "samplePeriod": _BACKTEST_RESULTS.get(row.get("code"), {}).get("samplePeriod"),
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