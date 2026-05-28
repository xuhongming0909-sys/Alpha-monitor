# -*- coding: utf-8 -*-
"""T10 IOPV回测引擎 - 从DB读取持仓和价格，计算T10估值精度。
不设默认值，没数据就报None。"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from data_fetch.lof_db.schema import get_db

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'backtest')
LOOKBACK_DAYS = 90
MIN_SAMPLES = 5


# ============================================================
# DB读取
# ============================================================
def _get_nav(code: str, start: str, end: str) -> Dict[str, float]:
    conn = get_db()
    rows = conn.execute(
        'SELECT date, nav FROM fund_nav WHERE code = ? AND date >= ? AND date <= ? ORDER BY date',
        (code, start, end)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _get_holdings(code: str) -> List[dict]:
    conn = get_db()
    rows = conn.execute(
        'SELECT ticker, name, weight, market FROM holdings WHERE code = ? ORDER BY weight DESC',
        (code,)
    ).fetchall()
    conn.close()
    return [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]


def _get_prices_batch(tickers: List[str], start: str, end: str) -> Dict[str, Dict[str, float]]:
    result = {}
    conn = get_db()
    for ticker in tickers:
        rows = conn.execute(
            'SELECT date, close FROM etf_prices WHERE ticker = ? AND date >= ? AND date <= ? ORDER BY date',
            (ticker, start, end)
        ).fetchall()
        if rows:
            result[ticker] = {r[0]: r[1] for r in rows}
            continue
        rows = conn.execute(
            'SELECT date, close FROM stock_prices WHERE ticker = ? AND date >= ? AND date <= ? ORDER BY date',
            (ticker, start, end)
        ).fetchall()
        if rows:
            result[ticker] = {r[0]: r[1] for r in rows}
    conn.close()
    return result


def _get_fx(start: str, end: str) -> Dict[str, float]:
    conn = get_db()
    rows = conn.execute(
        'SELECT date, rate FROM fx_rates WHERE currency = ? AND date >= ? AND date <= ? ORDER BY date',
        ('USD', start, end)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


# ============================================================
# T10计算
# ============================================================
def _calc_t10(prev_nav: float, holdings: List[dict],
              prices_prev: Dict[str, float], prices_curr: Dict[str, float],
              fx_prev: float, fx_curr: float) -> Optional[float]:
    """T10 IOPV: predicted = prev_nav * (1 + weighted_ret) * fx_ratio

    weights are in percentage (e.g., 20.85 for 20.85%)
    """
    weighted_ret = 0.0
    has_price = False
    total_weight = 0.0

    for h in holdings:
        ticker = h["ticker"]
        w_pct = h["weight"]  # percentage, e.g., 20.85
        pp = prices_prev.get(ticker)
        pc = prices_curr.get(ticker)
        if pp is None or pc is None or pp <= 0:
            continue
        ret = (pc - pp) / pp
        weighted_ret += (w_pct / 100.0) * ret  # convert % to decimal
        total_weight += w_pct
        has_price = True

    if not has_price or total_weight <= 0:
        return None

    # normalize: if total_weight < 100%, scale up
    norm_ret = weighted_ret / (total_weight / 100.0)

    if fx_prev is None or fx_curr is None or fx_prev <= 0:
        return None
    fx_ratio = fx_curr / fx_prev

    return prev_nav * (1 + norm_ret) * fx_ratio


# ============================================================
# 回测引擎
# ============================================================
def backtest_t10(code: str, end_date_str: str = None, lookback: int = LOOKBACK_DAYS) -> Optional[dict]:
    if end_date_str is None:
        end_date_str = datetime.now().strftime('%Y-%m-%d')

    start_date = (datetime.strptime(end_date_str, '%Y-%m-%d') - timedelta(days=lookback)).strftime('%Y-%m-%d')

    nav_dict = _get_nav(code, start_date, end_date_str)
    holdings = _get_holdings(code)
    if len(nav_dict) < MIN_SAMPLES or not holdings:
        return None

    tickers = list(set(h["ticker"] for h in holdings if h["ticker"]))
    if not tickers:
        return None

    price_data = _get_prices_batch(tickers, start_date, end_date_str)
    fx_rates = _get_fx(start_date, end_date_str)

    valid_tickers = set()
    for t in tickers:
        if t in price_data and len(price_data[t]) >= 2:
            valid_tickers.add(t)

    if not valid_tickers:
        return None

    valid_holdings = []
    excluded_tickers = []
    for h in holdings:
        if h["ticker"] in valid_tickers:
            valid_holdings.append(h)
        elif h["ticker"]:
            excluded_tickers.append(h["ticker"])

    if not valid_holdings:
        return None

    # 归一化权重
    total_w = sum(h["weight"] for h in valid_holdings)
    if total_w <= 0:
        return None
    norm_holdings = [{"ticker": h["ticker"], "weight": h["weight"] / total_w * 100} for h in valid_holdings]

    all_price_dates = set()
    for t in valid_tickers:
        all_price_dates.update(price_data[t].keys())
    all_price_dates = sorted(all_price_dates)

    nav_dates = sorted(nav_dict.keys())
    actual_series = []
    predicted_series = []
    error_ratios = []

    for i in range(1, len(nav_dates)):
        d_prev = nav_dates[i - 1]
        d_curr = nav_dates[i]
        nav_prev = nav_dict[d_prev]
        nav_curr = nav_dict[d_curr]

        if nav_prev <= 0 or nav_curr <= 0:
            continue

        etf_d_prev = None
        etf_d_curr = None
        for d in all_price_dates:
            if d <= d_prev:
                etf_d_prev = d
            if d <= d_curr:
                etf_d_curr = d

        if not etf_d_prev or not etf_d_curr or etf_d_prev == etf_d_curr:
            continue

        prices_prev = {}
        prices_curr = {}
        for t in valid_tickers:
            p = price_data.get(t, {})
            pp = p.get(etf_d_prev)
            pc = p.get(etf_d_curr)
            if pp is not None:
                prices_prev[t] = pp
            if pc is not None:
                prices_curr[t] = pc

        fx_prev = fx_rates.get(d_prev)
        fx_curr = fx_rates.get(d_curr)

        predicted = _calc_t10(nav_prev, norm_holdings, prices_prev, prices_curr, fx_prev, fx_curr)
        if predicted is None or predicted <= 0:
            continue

        error_ratio = abs(predicted - nav_curr) / nav_prev
        actual_series.append(nav_curr)
        predicted_series.append(predicted)
        error_ratios.append(error_ratio)

    if len(actual_series) < MIN_SAMPLES:
        return None

    return _calc_metrics(actual_series, predicted_series, error_ratios,
                         len(norm_holdings), excluded_tickers,
                         f"{nav_dates[1]}~{nav_dates[-1]}" if len(nav_dates) > 1 else "")


def _calc_metrics(actual: list, predicted: list, error_ratios: list,
                  holdings_count: int, excluded: list, period: str) -> dict:
    n = len(actual)
    errors_signed = [(p - a) / a * 100 for a, p in zip(actual, predicted)]
    errors_abs = [abs(e) for e in errors_signed]
    err_gt_05 = sum(1 for e in error_ratios if e > 0.005)

    return {
        "bias": round(np.mean(errors_signed), 4),
        "mae": round(np.mean(errors_abs), 4),
        "maxErr": round(max(errors_abs), 4),
        "errRate05": round(err_gt_05 / n * 100, 1),
        "errDays": err_gt_05,
        "totalDays": n,
        "holdings_count": holdings_count,
        "excluded_tickers": excluded,
        "samplePeriod": period,
    }


def run_all(end_date_str: str = None) -> dict:
    from shared.config.script_config import load_config
    cfg = load_config()
    plugins = cfg.get("data_fetch", {}).get("plugins", {})
    lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
    funds = lof_cfg.get("funds", [])

    results = {}
    for f in funds:
        code = f.get("code", "")
        name = f.get("name", "")
        r = backtest_t10(code, end_date_str)
        if r:
            r["code"] = code
            r["name"] = name
            results[code] = r
        else:
            results[code] = {"code": code, "name": name, "error": "无数据"}

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "results_t10.json")
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f"T10回测完成: {len(results)}只 -> {out_path}")
    return results


if __name__ == "__main__":
    results = run_all()
    for code, r in sorted(results.items()):
        if "error" in r:
            print(f"{code} ({r.get('name','')}): {r['error']}")
        else:
            bias = r.get("bias", 0)
            mae = r.get("mae", 0)
            maxe = r.get("maxErr", 0)
            err_rate = r.get("errRate05", 0)
            hc = r.get("holdings_count", 0)
            excl = r.get("excluded_tickers", [])
            print(f"{code} ({r.get('name','')}): bias={bias:+.3f}% MAE={mae:.3f}% maxErr={maxe:.3f}% err>0.5%={err_rate}% n={r.get('totalDays',0)} holdings={hc} excl={excl}")
