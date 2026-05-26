# -*- coding: utf-8 -*-
"""LOF IOPV 估值策略服务。

双引擎估值：A类指数法 + B类T10持仓法。
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

from strategy.lof_iopv.classifier import classify_fund, get_calc_mode, get_group_key

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


# ─── 历史汇率缓存 ────────────────────────────────────────

_FX_CACHE: Dict[str, float] = {}


def _get_base_fx(currency: str, date_str: str) -> Optional[float]:
    """获取指定日期央行中间价。"""
    if currency == "CNY":
        return 1.0
    if not date_str or len(date_str) < 10:
        return None
    cache_key = f"{currency}_{date_str}"
    if cache_key in _FX_CACHE:
        return _FX_CACHE[cache_key]
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
            rate = _to_float(df.iloc[-1].get("中行折算价") or df.iloc[-1].iloc[-1])
            if rate and rate > 0:
                _FX_CACHE[cache_key] = rate
                return rate
    except Exception:
        pass
    return None


# ─── 股票代码映射 ────────────────────────────────────────

def _tencent_code(ticker: str, market: str) -> str:
    ticker = str(ticker).strip()
    market = str(market).strip().lower()
    if market == "us":
        return f"us{ticker}" if "." in ticker else f"us{ticker}.OQ"
    elif market == "hk":
        return f"hk{ticker.zfill(5)}"
    elif market == "sz":
        return f"sz{ticker}"
    elif market == "sh":
        return f"sh{ticker}"
    return ""


# ─── 历史股价 ──────────────────────────────────────────

def _get_base_price(ticker: str, market: str, date_str: str) -> Optional[float]:
    """获取指定日期收盘价（腾讯K线）。"""
    tc = _tencent_code(ticker, market)
    if not tc or not date_str:
        return None
    try:
        import json
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        ds = dt.strftime("%Y-%m-%d")
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tc},day,{ds},{ds},1,qfq"
        resp = _SESSION.get(url, timeout=15)
        data = json.loads(resp.content.decode("utf-8", errors="ignore"))
        kline = (data.get("data") or {}).get(tc) or {}
        day = kline.get("day") or kline.get("qfqday") or []
        if day and len(day[-1]) >= 3:
            return _to_float(day[-1][2])
    except Exception:
        pass
    return None


# ─── 实时价格批量获取 ──────────────────────────────────

def _get_current_prices(holdings: List[dict]) -> Dict[str, float]:
    codes = [_tencent_code(h["ticker"], h["market"]) for h in holdings]
    codes = [c for c in codes if c]
    if not codes:
        return {}
    quotes = get_quotes(codes, timeout=15)
    result = {}
    for h in holdings:
        tc = _tencent_code(h.get("ticker", ""), h.get("market", ""))
        info = quotes.get(tc)
        if info and info.get("price"):
            result[h["ticker"]] = info["price"]
    return result


# ─── A类估值 ────────────────────────────────────────────

def _calc_a_type(row: dict, fx_now: Optional[float]) -> tuple:
    nav = _to_float(row.get("nav"))
    nav_date = str(row.get("navDate") or "")[:10]
    index_change = _to_float(row.get("indexIncreaseRate"))
    currency = str(row.get("currency") or "CNY").upper()

    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    if index_change is None:
        return None, "指数涨跌幅缺失", {}

    fx_ratio = 1.0
    fx_base = None
    if currency != "CNY" and fx_now and fx_now > 0:
        fx_base = _get_base_fx(currency, nav_date)
        if fx_base and fx_base > 0:
            fx_ratio = fx_now / fx_base

    iopv = round(nav * (1 + index_change / 100) * fx_ratio, 4)
    status = f"指数跟踪法 | ΔIndex={index_change:.2f}% | FX比={fx_ratio:.4f}"
    details = {"nav": nav, "navDate": nav_date, "indexChange": index_change, "fxRatio": round(fx_ratio, 6), "fxBase": fx_base, "fxNow": fx_now}
    return iopv, status, details


# ─── B类估值 ────────────────────────────────────────────

def _calc_b_type(row: dict, fx_now: Optional[float]) -> tuple:
    nav = _to_float(row.get("nav"))
    nav_date = str(row.get("navDate") or "")[:10]
    stock_ratio = _to_float(row.get("stockPosition")) or 90.0
    currency = str(row.get("currency") or "CNY").upper()
    holdings = row.get("holdings") or []

    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    if not holdings:
        return None, "持仓数据缺失", {}

    fx_ratio = 1.0
    fx_base = None
    if currency != "CNY" and fx_now and fx_now > 0:
        fx_base = _get_base_fx(currency, nav_date)
        if fx_base and fx_base > 0:
            fx_ratio = fx_now / fx_base

    current_prices = _get_current_prices(holdings)
    total_wr = 0.0
    total_w = 0.0
    valid = 0
    hd = []

    for h in holdings:
        ticker = str(h.get("ticker") or "").strip()
        name = str(h.get("name") or "").strip()
        weight = _to_float(h.get("weight"))
        market = str(h.get("market") or "").strip().lower()
        if not ticker or not weight or weight <= 0:
            continue
        p_base = _get_base_price(ticker, market, nav_date)
        p_now = current_prices.get(ticker)
        if p_base is None or p_base <= 0:
            hd.append({"ticker": ticker, "name": name, "weight": weight, "basePrice": None, "nowPrice": p_now, "returnCny": None, "status": "基价缺失"})
            continue
        if p_now is None:
            hd.append({"ticker": ticker, "name": name, "weight": weight, "basePrice": p_base, "nowPrice": None, "returnCny": None, "status": "现价缺失"})
            continue
        r_cny = (p_now / p_base) * fx_ratio - 1
        total_wr += weight * r_cny
        total_w += weight
        valid += 1
        hd.append({"ticker": ticker, "name": name, "weight": weight, "basePrice": round(p_base, 4), "nowPrice": round(p_now, 4), "returnCny": round(r_cny * 100, 4), "status": "ok"})

    if total_w <= 0 or valid == 0:
        return None, f"有效持仓为0(共{len(holdings)}只)", {"holdings": hd}

    wr = total_wr / total_w
    iopv = round(nav * (1 + (stock_ratio / 100) * wr), 4)
    status = f"T10持仓法 | 仓位={stock_ratio:.1f}% | 有效={valid}/{len(holdings)} | 加权收益={wr*100:.2f}% | FX比={fx_ratio:.4f}"
    details = {"nav": nav, "navDate": nav_date, "stockRatio": stock_ratio, "weightedReturn": wr, "fxRatio": round(fx_ratio, 6), "fxBase": fx_base, "fxNow": fx_now, "validHoldings": valid, "totalHoldings": len(holdings), "holdings": hd}
    return iopv, status, details


# ─── D类估值 ────────────────────────────────────────────

def _calc_d_type(row: dict) -> tuple:
    nav = _to_float(row.get("nav"))
    if nav is None or nav <= 0:
        return None, "NAV缺失", {}
    return nav, "直接NAV法", {"nav": nav}


# ─── 主入口 ────────────────────────────────────────────

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
        fund_type = classify_fund(row)
        currency = str(row.get("currency") or "CNY").upper()
        fx_now = fx_rates.get(currency)

        if fund_type == "A":
            iopv, calc_status, details = _calc_a_type(row, fx_now)
        elif fund_type == "B":
            iopv, calc_status, details = _calc_b_type(row, fx_now)
        elif fund_type == "D":
            iopv, calc_status, details = _calc_d_type(row)
        else:
            iopv, calc_status, details = _calc_d_type(row)
            fund_type = "C"
            calc_status = "多ETF拟合法(暂用NAV)"

        price = _to_float(row.get("price"))
        premium_rate = None
        if iopv is not None and price and price > 0 and iopv > 0:
            premium_rate = round((price / iopv - 1) * 100, 2)

        result_rows.append({
            "code": row.get("code"),
            "name": row.get("name"),
            "market": row.get("market"),
            "marketLabel": "深市" if row.get("market") == "sz" else "沪市",
            "currency": currency,
            "fundType": fund_type,
            "groupKey": get_group_key(fund_type),
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
            "marketGroup": row.get("marketGroup"),
        })

    result_rows.sort(key=lambda r: 9999.0 if r.get("premiumRate") is None else -abs(r["premiumRate"]))

    source_summary = dict(fetch_payload.get("sourceSummary") or {})
    source_summary["computedRows"] = sum(1 for r in result_rows if r.get("iopv") is not None)
    source_summary["totalRows"] = len(result_rows)

    return build_success({
        "groups": [{"key": "index", "label": "指数LOF"}, {"key": "qdii", "label": "QDII"}],
        "defaultGroup": "qdii",
        "rows": result_rows,
        "sourceSummary": source_summary,
    }, updateTime=fetch_payload.get("updateTime") or now_iso(), source=fetch_payload.get("source") or "lof_iopv")