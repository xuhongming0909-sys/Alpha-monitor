# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF回测v2 - 复用IOPV公式，NAV绝对值对比，3个月窗口
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF回测v2: 复用calc_a_iopv/calc_b_iopv，NAV绝对值对比，3个月窗口，日期严格对齐"""

import json
import os
import sys
from datetime import datetime, timedelta

import numpy as np

from data_fetch.lof_db.schema import get_db
from strategy.lof_iopv.calc import calc_a_iopv, calc_b_iopv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from data_fetch.lof_iopv.source import _fetch_stock_position

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest', 'results_v2.json')
MIN_SAMPLES = 5
LOOKBACK_DAYS = 90


def _load_funds():
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        return lof_cfg.get("funds", [])
    except Exception:
        return []


def _get_nav_dates(code, start_date, end_date):
    conn = get_db()
    rows = conn.execute(
        'SELECT date, nav FROM fund_nav WHERE code = ? AND date >= ? AND date <= ? ORDER BY date',
        (code, start_date, end_date)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _get_etf_prices(ticker, start_date, end_date):
    conn = get_db()
    rows = conn.execute(
        'SELECT date, close FROM etf_prices WHERE ticker = ? AND date >= ? AND date <= ? ORDER BY date',
        (ticker, start_date, end_date)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _get_stock_prices_batch(tickers, start_date, end_date):
    conn = get_db()
    result = {}
    for ticker in tickers:
        rows = conn.execute(
            'SELECT date, close FROM stock_prices WHERE ticker = ? AND date >= ? AND date <= ? ORDER BY date',
            (ticker, start_date, end_date)
        ).fetchall()
        result[ticker] = {r[0]: r[1] for r in rows}
    conn.close()
    return result


def _get_fx_rates(start_date, end_date):
    conn = get_db()
    rows = conn.execute(
        'SELECT date, rate FROM fx_rates WHERE currency = ? AND date >= ? AND date <= ? ORDER BY date',
        ('USD', start_date, end_date)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _get_holdings(code):
    conn = get_db()
    rows = conn.execute(
        'SELECT ticker, name, weight, market FROM holdings WHERE code = ? ORDER BY report_date DESC LIMIT 10',
        (code,)
    ).fetchall()
    conn.close()
    return [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]


def _calc_metrics(actual_series, predicted_series, error_ratios):
    y = np.array(actual_series)
    x = np.array(predicted_series)
    n = len(y)
    if n < MIN_SAMPLES:
        return None
    # R2 on daily returns (measures correlation, not trend)
    actual_ret = np.diff(y) / y[:-1]
    predicted_ret = np.diff(x) / y[:-1]
    r_mean = np.mean(actual_ret)
    ss_tot = float(np.sum((actual_ret - r_mean) ** 2))
    ss_res = float(np.sum((actual_ret - predicted_ret) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    mae = float(np.mean(error_ratios)) * 100
    max_err = float(np.max(error_ratios)) * 100
    return {
        "r2": round(r2, 4),
        "mae": round(mae, 4),
        "maxErr": round(max_err, 4),
        "n": n,
    }


def backtest_a(code, etf, end_date_str):
    start_date = (datetime.strptime(end_date_str, '%Y-%m-%d') - timedelta(days=LOOKBACK_DAYS)).strftime('%Y-%m-%d')
    nav_dict = _get_nav_dates(code, start_date, end_date_str)
    etf_prices = _get_etf_prices(etf, start_date, end_date_str)
    fx_rates = _get_fx_rates(start_date, end_date_str)
    stock_position = _fetch_stock_position(code)
    if stock_position is None:
        return None

    nav_dates = sorted(nav_dict.keys())
    if len(nav_dates) < MIN_SAMPLES + 1:
        return None

    actual_series, predicted_series, error_ratios = [], [], []
    for i in range(1, len(nav_dates)):
        d_prev, d_curr = nav_dates[i-1], nav_dates[i]
        if d_prev not in etf_prices or d_curr not in etf_prices:
            continue
        if d_prev not in fx_rates or d_curr not in fx_rates:
            continue
        nav_prev = nav_dict[d_prev]
        nav_curr = nav_dict[d_curr]
        if nav_prev <= 0:
            continue
        etf_change_pct = (etf_prices[d_curr] / etf_prices[d_prev] - 1) * 100
        predicted, _, _ = calc_a_iopv(
            nav=nav_prev, etf_change_pct=etf_change_pct,
            fx_now=fx_rates[d_curr], fx_base=fx_rates[d_prev],
            stock_position=stock_position, etf_nav_date_price=etf_prices[d_prev],
            etf_current_price=etf_prices[d_curr],
        )
        if predicted is None or predicted <= 0:
            continue
        error_ratio = abs(predicted - nav_curr) / nav_prev
        actual_series.append(nav_curr)
        predicted_series.append(predicted)
        error_ratios.append(error_ratio)

    metrics = _calc_metrics(actual_series, predicted_series, error_ratios)
    if metrics is None:
        return None
    metrics["samplePeriod"] = f"{nav_dates[1]}~{nav_dates[-1]}" if len(nav_dates) > 1 else ""
    metrics["alignedDays"] = len(actual_series)
    return metrics


def backtest_b(code, end_date_str):
    start_date = (datetime.strptime(end_date_str, '%Y-%m-%d') - timedelta(days=LOOKBACK_DAYS)).strftime('%Y-%m-%d')
    nav_dict = _get_nav_dates(code, start_date, end_date_str)
    fx_rates = _get_fx_rates(start_date, end_date_str)
    holdings = _get_holdings(code)
    if not holdings:
        return None
    # 用雪球实际股票仓位，fallback到T10权重总和
    stock_ratio = _fetch_stock_position(code) or sum(h["weight"] for h in holdings)
    if stock_ratio <= 0:
        return None

    tickers = list(set(h["ticker"] for h in holdings))
    stock_prices = _get_stock_prices_batch(tickers, start_date, end_date_str)

    nav_dates = sorted(nav_dict.keys())
    if len(nav_dates) < MIN_SAMPLES + 1:
        return None

    actual_series, predicted_series, error_ratios = [], [], []
    for i in range(1, len(nav_dates)):
        d_prev, d_curr = nav_dates[i-1], nav_dates[i]
        if d_prev not in fx_rates or d_curr not in fx_rates:
            continue
        nav_prev = nav_dict[d_prev]
        nav_curr = nav_dict[d_curr]
        if nav_prev <= 0:
            continue

        nav_date_prices = {}
        current_prices = {}
        for h in holdings:
            t = h["ticker"]
            if t in stock_prices:
                if d_prev in stock_prices[t]:
                    nav_date_prices[t] = stock_prices[t][d_prev]
                if d_curr in stock_prices[t]:
                    current_prices[t] = stock_prices[t][d_curr]

        if not nav_date_prices or not current_prices:
            continue

        predicted, _, details = calc_b_iopv(
            nav=nav_prev, holdings=holdings, stock_ratio=stock_ratio,
            current_prices=current_prices, nav_date_prices=nav_date_prices,
            prev_closes={}, fx_now=fx_rates[d_curr], fx_base=fx_rates[d_prev]
        )
        if predicted is None or predicted <= 0:
            continue
        error_ratio = abs(predicted - nav_curr) / nav_prev
        actual_series.append(nav_curr)
        predicted_series.append(predicted)
        error_ratios.append(error_ratio)

    metrics = _calc_metrics(actual_series, predicted_series, error_ratios)
    if metrics is None:
        return None
    metrics["samplePeriod"] = f"{nav_dates[1]}~{nav_dates[-1]}" if len(nav_dates) > 1 else ""
    metrics["alignedDays"] = len(actual_series)
    metrics["holdings_count"] = len(holdings)
    return metrics


def run_all(end_date_str=None):
    if end_date_str is None:
        end_date_str = datetime.now().strftime('%Y-%m-%d')
    funds = _load_funds()
    results = {}
    for f in funds:
        code = f["code"]
        est = f.get("estimation", "A")
        if est == "A" and f.get("etf"):
            r = backtest_a(code, f["etf"], end_date_str)
            if r:
                r["type"] = "A"
                r["etf"] = f["etf"]
                r["code"] = code
                results[code] = r
        elif est == "B":
            r = backtest_b(code, end_date_str)
            if r:
                r["type"] = "B"
                r["code"] = code
                results[code] = r
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f"回测v2完成: {len(results)}只 -> {OUTPUT_PATH}")
    return results


if __name__ == "__main__":
    results = run_all()
    for code, r in sorted(results.items()):
        print(f"{code} ({r['type']}): r2={r['r2']}, maxErr={r['maxErr']}, aligned={r['alignedDays']}")

