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
from strategy.lof_iopv.calc import to_float, get_base_fx, calc_iopv
from data_fetch.lof_iopv.fund_classifier import get_fund_class, get_index_etf_ticker, is_index_fund

_BACKTEST_PATH = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest', 'results_v2.json')
_BACKTEST_RESULTS = {}


def _load_backtest_results():
    """Load backtest results cache."""
    global _BACKTEST_RESULTS
    try:
        if _os.path.exists(_BACKTEST_PATH):
            with open(_BACKTEST_PATH, "r", encoding="utf-8") as f:
                _BACKTEST_RESULTS = _json.load(f)
    except Exception:
        _BACKTEST_RESULTS = {}


def _get_fx_base_from_db(currency, nav_date):
    """Get NAV base-date exchange rate from DB, fallback to get_base_fx."""
    if not nav_date or currency == "CNY":
        return 1.0 if currency == "CNY" else None
    try:
        from data_fetch.lof_db.schema import get_db
        conn = get_db()
        row = conn.execute(
            "SELECT rate FROM fx_rates WHERE currency=? AND date<=? AND date>=date(?, '-10 days') AND rate IS NOT NULL ORDER BY date DESC LIMIT 1",
            (currency, nav_date[:10], nav_date[:10])
        ).fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return get_base_fx(currency, nav_date)



def _get_holdings_from_db(code):
    """Get latest holdings data from DB bottom-up."""
    try:
        from data_fetch.lof_db.schema import get_db
        conn = get_db()
        rows = conn.execute(
            "SELECT ticker, name, weight, market FROM holdings WHERE code=? ORDER BY weight DESC",
            (code,)
        ).fetchall()
        conn.close()
        return [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]
    except Exception:
        return []

def _monitor_pools(row, limited_threshold=0.5, unlimited_threshold=1.0):
    """Decide monitor pool eligibility based on premium rate."""
    premium = row.get("premiumRate")
    if premium is None:
        return False, False
    limited = abs(premium) >= limited_threshold
    unlimited = abs(premium) >= unlimited_threshold
    return limited, unlimited



def _resolve_fx_rates(currencies):
    """Unified FX fetch: tencent API first, fallback to DB."""
    fx = {}
    try:
        api_rates = get_fx_rates(currencies)
        if api_rates:
            fx.update(api_rates)
    except Exception:
        pass
    missing = [c for c in currencies if c not in fx]
    if missing:
        try:
            from data_fetch.lof_db.schema import get_db
            conn = get_db()
            for cur in missing:
                row = conn.execute(
                    "SELECT rate FROM fx_rates WHERE currency=? AND rate IS NOT NULL ORDER BY date DESC LIMIT 1",
                    (cur,)
                ).fetchone()
                if row and row[0]:
                    fx[cur] = row[0]
            conn.close()
        except Exception:
            pass
    return fx

def build_lof_response(fetch_payload):
    """Build UI display data from source layer fetch results."""
    _load_backtest_results()

    fx_rates = _resolve_fx_rates(["USD", "HKD"])

    rows = fetch_payload.get("data") or []
    result = []

    for row in rows:
        currency = row.get("currency", "CNY").upper()
        fx_now = fx_rates.get(currency)

        fx_base = None
        if currency != "CNY":
            fx_base = _get_fx_base_from_db(currency, row.get("navDate", ""))

        iopv, status, details = calc_iopv(
            nav=row.get("nav"),
            holdings=row.get("holdings") or [],
            stock_ratio=to_float(row.get("stockPosition")),
            current_prices=row.get("currentPrices") or {},
            nav_date_prices=row.get("navDatePrices") or {},
            prev_closes=row.get("holdingsPrevClose") or {},
            fx_now=fx_now,
            fx_base=fx_base,
        )

        price = to_float(row.get("price"))
        premium = round((price / iopv - 1) * 100, 3) if (iopv and price and price > 0 and iopv > 0) else None

        stock_pos = row.get("stockPosition")

        if premium is not None:
            premium_status = "premium" if premium > 0.5 else ("discount" if premium < -0.5 else "flat")
        else:
            premium_status = None

        code = row.get("code", "")
        effective_holdings = row.get("holdings") or _get_holdings_from_db(code)
        cls = get_fund_class(code)
        if cls == "index":
            benchmark = "ETF:%s" % get_index_etf_ticker(code)
        else:
            benchmark = "active_holdings(%d)" % len(effective_holdings)

        apply_status = row.get("applyStatus") or ""
        daily_limit = row.get("dailyLimit")
        # 东方财富API返回: "开放申购"/"暂停申购"/"限大额"
        if apply_status == "限大额" and daily_limit is not None and daily_limit < 1e10:
            apply_status = "限额%d" % int(daily_limit)
        elif not apply_status:
            apply_status = "未知"

        # Exchange: 1xx=SZ (supports 1-to-6), 5xx=SH (no 1-to-6)
        fund_code = row.get("code", "")
        exchange = "SZ" if fund_code.startswith("1") else "SH"
        supports_1to6 = fund_code.startswith("1")
        result.append({
            "code": row.get("code"),
            "name": row.get("name"),
            "price": price,
            "nav": row.get("nav"),
            "iopv": iopv,
            "premiumRate": premium,
            "premiumStatus": premium_status,
            "iopvStatus": status,
            "iopvDetails": details,
            "currency": currency,
            "fxRate": fx_now,
            "fxBase": fx_base,
            "stockPosition": stock_pos,
            "calcTarget": benchmark,
            "holdingsCount": len(effective_holdings),
            "holdings": effective_holdings,
            "applyStatus": apply_status,
            "dailyLimit": daily_limit,
            "redeemFee": row.get("redeemFee"),
            "redeemStatus": row.get("redeemStatus"),
            "custodianFee": row.get("custodianFee"),
            "fundCompany": row.get("fundCompany"),
            "shareIncrease": row.get("shareIncrease"),
            "shareTotal": row.get("shareTotal"),
            "applyFee": row.get("applyFee"),
            "navDate": row.get("navDate"),
            "exchange": exchange,
            "supports1to6": supports_1to6,
            "fundClass": get_fund_class(row.get("code", "")),
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
