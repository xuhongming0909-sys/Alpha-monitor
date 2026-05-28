# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF IOPV service layer - response building and monitor pool filtering
# INDEX section 9.3 file summary index
"""QDII LOF IOPV service. Uses shared calc.py for IOPV formulas."""

from __future__ import annotations

import os as _os
import json as _json

from shared.market_service import get_fx_rates
from shared.models.service_result import build_success
from shared.time.shanghai_time import now_iso
from strategy.lof_iopv.calc import to_float, get_base_fx, calc_a_iopv, calc_b_iopv


def _get_fx_base_from_db(currency, nav_date):
    """从 DB 获取 NAV 基准日汇率，fallback 到 get_base_fx"""
    if not nav_date or currency == "CNY":
        return 1.0 if currency == "CNY" else None
    try:
        from data_fetch.lof_db.schema import get_db
        conn = get_db()
        row = conn.execute(
            "SELECT rate FROM fx_rates WHERE currency=? AND date<=? AND rate IS NOT NULL ORDER BY date DESC LIMIT 1",
            (currency, nav_date[:10])
        ).fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return get_base_fx(currency, nav_date[:10])


def _get_fx_now_from_db(currency):
    """?DB?????"""
    if currency == "CNY":
        return 1.0
    try:
        from data_fetch.lof_db.schema import get_db
        conn = get_db()
        row = conn.execute(
            "SELECT rate FROM fx_rates WHERE currency=? AND rate IS NOT NULL ORDER BY date DESC LIMIT 1",
            (currency,)
        ).fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return None

# Load backtest results
_BACKTEST_DIR = _os.path.join(_os.path.dirname(__file__), "..", "..", "runtime_data", "backtest")
_BACKTEST_RESULTS = {}
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


def _is_paused(status):
    return "\u6682\u505c" in str(status or "")


def _monitor_pools(row):
    premium = row.get("premiumRate")
    turnover = to_float(row.get("turnoverWan"))
    paused = _is_paused(row.get("applyStatus"))
    lim = unlim = False
    if not paused and premium is not None and turnover is not None:
        if "\u9650" in str(row.get("applyStatus") or "") and premium > 1.0 and turnover > 100:
            lim = True
        if ("\u4e0d" in str(row.get("applyStatus") or "") or "\u6b63\u5e38" in str(row.get("applyStatus") or "")) and abs(premium) > 5.0 and turnover > 100:
            unlim = True
    return lim, unlim


def build_lof_iopv_response(fetch_payload, records):
    if not fetch_payload or fetch_payload.get("success") is False:
        return build_success({"groups": [], "rows": [], "sourceSummary": {}}, updateTime=now_iso(), source="lof_iopv", error=(fetch_payload or {}).get("error", "fetch_failed"))

    # DB???????????????fallback???API
    fx_rates = {}
    for cur in ["USD", "HKD"]:
        db_rate = _get_fx_now_from_db(cur)
        if db_rate:
            fx_rates[cur] = db_rate
    if not fx_rates:
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

        # Get FX base for the nav date (DB???fallback?akshare)
        fx_base = None
        if currency != "CNY":
            fx_base = _get_fx_base_from_db(currency, row.get("navDate", ""))

        if est == "B":
            iopv, status, details = calc_b_iopv(
                nav=row.get("nav"),
                holdings=row.get("holdings") or [],
                stock_ratio=to_float(row.get("stockPosition")),
                current_prices=row.get("currentPrices") or {},
                nav_date_prices=row.get("navDatePrices") or {},
                prev_closes=row.get("holdingsPrevClose") or {},
                fx_now=fx_now,
                fx_base=fx_base,
            )
        else:
            iopv, status, details = calc_a_iopv(
                nav=row.get("nav"),
                etf_change_pct=to_float(row.get("etfChange")),
                fx_now=fx_now,
                fx_base=fx_base,
                stock_position=to_float(row.get("stockPosition")),
                etf_nav_date_price=to_float(row.get("etfNavDatePrice")),
                etf_current_price=to_float(row.get("etfCurrentPrice")),
            )

        price = to_float(row.get("price"))
        premium = round((price / iopv - 1) * 100, 3) if (iopv and price and price > 0 and iopv > 0) else None

        calc_method = "\u6307\u6570\u8ddf\u8e2a\u6cd5" if est == "A" else "T10\u6301\u4ed3\u6cd5"
        stock_pos = row.get("stockPosition")

        if premium is not None:
            premium_status = "\u6ea2\u4ef7" if premium > 0.5 else ("\u6298\u4ef7" if premium < -0.5 else "\u5e73\u4ef7")
        else:
            premium_status = None

        benchmark = row.get("etf") or "Top10(%d)" % len(row.get("holdings", []) or [])

        apply_status = row.get("applyStatus") or ""
        daily_limit = row.get("dailyLimit")
        if apply_status == "\u9650\u5927\u989d" and daily_limit is not None and daily_limit < 1e10:
            apply_status = "\u9650\u989d%d" % int(daily_limit)
        elif not apply_status:
            apply_status = "--"

        if est == "A":
            calc_core = row.get("etf") or "\u672a\u77e5\u6807\u7684"
        else:
            calc_core = "\u524d\u5341\u5927"

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
            "dailyLimit": row.get("dailyLimit"),
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
