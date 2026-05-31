# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF回测 - 指数型ETF + 主动型持仓，统一calc_iopv公式
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF回测: 指数型用ETF映射, 主动型用持仓, 统一calc_iopv公式。

日期对齐规则：每个NAV披露日d，用d日的持仓和d日股价作为基准，
用d+1日股价推算IOPV，与d+1日实际NAV对比。
"""

import json
import os
import sys
from datetime import datetime, timedelta

import numpy as np

from data_fetch.lof_db.schema import get_db
from strategy.lof_iopv.calc import calc_iopv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from data_fetch.lof_iopv.source import _fetch_stock_position
from data_fetch.lof_iopv.fund_classifier import (
    is_index_fund, get_holdings_for_backtest, get_index_etf_ticker,
)

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


def _get_stock_prices_batch(tickers, start_date, end_date):
    """批量获取股价 {ticker: {date: price}}"""
    result = {}
    conn = get_db()
    for ticker in tickers:
        rows = conn.execute(
            'SELECT date, close FROM stock_prices WHERE ticker = ? AND date >= ? AND date <= ? ORDER BY date',
            (ticker, start_date, end_date)
        ).fetchall()
        if not rows:
            rows = conn.execute(
                'SELECT date, close FROM etf_prices WHERE ticker = ? AND date >= ? AND date <= ? ORDER BY date',
                (ticker, start_date, end_date)
            ).fetchall()
        result[ticker] = {r[0]: r[1] for r in rows}
    conn.close()
    return result


def _get_fx_rates(start_date, end_date, currency='USD'):
    """获取指定币种汇率 {date: rate}，支持 USD/HKD"""
    conn = get_db()
    rows = conn.execute(
        'SELECT date, rate FROM fx_rates WHERE currency = ? AND date >= ? AND date <= ? ORDER BY date',
        (currency.upper(), start_date, end_date)
    ).fetchall()
    conn.close()
    return {r[0]: r[1] for r in rows}


def _get_holdings(code):
    """获取持仓: A类=ETF(weight=100), B类=hardcoded实际持仓"""
    return get_holdings_for_backtest(code)


def _calc_metrics(actual_series, predicted_series):
    """计算回测指标: Bias / MAE / MaxErr / ErrRate05"""
    y = np.array(actual_series)
    x = np.array(predicted_series)
    n = len(y)
    if n < MIN_SAMPLES:
        return None
    nav_prev = np.concatenate([[y[0]], y[:-1]])
    signed_err = np.where(nav_prev > 0, (x - y) / nav_prev, 0)
    abs_err = np.abs(signed_err)
    bias = float(np.mean(signed_err)) * 100
    mae = float(np.mean(abs_err)) * 100
    max_err = float(np.max(abs_err)) * 100
    err_count = int(np.sum(abs_err > 0.005))
    err_rate = round(err_count / n * 100, 1) if n > 0 else 0
    return {
        "bias": round(bias, 4),
        "mae": round(mae, 4),
        "maxErr": round(max_err, 4),
        "errRate05": err_rate,
        "errDays": err_count,
        "totalDays": n,
    }


def backtest_fund(code, end_date_str):
    """回测单只基金: A类ETF追踪或B类持仓加权, 统一calc_iopv。"""
    start_date = (datetime.strptime(end_date_str, '%Y-%m-%d') - timedelta(days=LOOKBACK_DAYS)).strftime('%Y-%m-%d')
    nav_dict = _get_nav_dates(code, start_date, end_date_str)
    # Determine fund currency for FX lookup
    fund_currency = 'USD'
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get('data_fetch', {}).get('plugins', {})
        lof_cfg = plugins.get('lof_arbitrage', plugins.get('lof_iopv', {}))
        for f in lof_cfg.get('funds', []):
            if f.get('code') == code:
                fund_currency = f.get('currency', 'USD')
                break
    except Exception:
        pass
    fx_rates = _get_fx_rates(start_date, end_date_str, fund_currency)
    holdings = _get_holdings(code)
    if not holdings:
        return None

    # 总仓位: 从API获取(1-现金比例)
    stock_ratio = _fetch_stock_position(code)
    if not stock_ratio or stock_ratio <= 0:
        stock_ratio = sum(h.get("weight", 0) for h in holdings)
    if stock_ratio <= 0:
        return None

    cls = "A" if is_index_fund(code) else "B"
    etf = get_index_etf_ticker(code) if cls == "A" else ""

    tickers = list(set(h["ticker"] for h in holdings))
    stock_prices = _get_stock_prices_batch(tickers, start_date, end_date_str)

    nav_dates = sorted(nav_dict.keys())
    if len(nav_dates) < MIN_SAMPLES + 1:
        return None

    actual_series, predicted_series = [], []
    for i in range(1, len(nav_dates)):
        d_prev, d_curr = nav_dates[i - 1], nav_dates[i]
        # CNY基金无汇率数据时默认1.0
        fx_prev = fx_rates.get(d_prev, 1.0)
        fx_curr = fx_rates.get(d_curr, 1.0)
        nav_prev = nav_dict[d_prev]
        nav_curr = nav_dict[d_curr]
        if nav_prev <= 0:
            continue

        # 构建价格字典
        nav_date_prices = {}
        current_prices = {}
        valid_weight_sum = 0.0
        for h in holdings:
            t = h["ticker"]
            p_prev = stock_prices.get(t, {}).get(d_prev)
            p_curr = stock_prices.get(t, {}).get(d_curr)
            if p_prev and p_prev > 0:
                nav_date_prices[t] = p_prev
            else:
                continue
            if p_curr and p_curr > 0:
                current_prices[t] = p_curr
            else:
                continue
            valid_weight_sum += h.get("weight", 0)
        if valid_weight_sum <= 0:
            continue

        adjusted_stock_ratio = stock_ratio * valid_weight_sum / 100.0
        predicted, _, _ = calc_iopv(
            nav=nav_prev,
            holdings=holdings,
            stock_ratio=stock_ratio,
            current_prices=current_prices,
            nav_date_prices=nav_date_prices,
            prev_closes={},
            fx_now=fx_curr,
            fx_base=fx_prev,
        )
        if predicted is None or predicted <= 0:
            continue
        actual_series.append(nav_curr)
        predicted_series.append(predicted)

    metrics = _calc_metrics(actual_series, predicted_series)
    if metrics is None:
        return None
    metrics["samplePeriod"] = f"{nav_dates[1]}~{nav_dates[-1]}" if len(nav_dates) > 1 else ""
    metrics["alignedDays"] = len(actual_series)
    metrics["class"] = cls
    if etf:
        metrics["etf"] = etf
    return metrics


def run_all():
    """回测所有配置的LOF基金"""
    end_date_str = datetime.now().strftime('%Y-%m-%d')
    funds = _load_funds()
    results = {}
    skipped = []
    for f in funds:
        code = f.get("code", "")
        cls = "A" if is_index_fund(code) else "B"
        r = backtest_fund(code, end_date_str)
        if r:
            r["code"] = code
            r["name"] = f.get("name", "")
            results[code] = r
        else:
            skipped.append(f"{code}({f.get('name','')})")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f"回测完成: {len(results)}只 -> {OUTPUT_PATH}")
    if skipped:
        print(f"跳过(无数据): {', '.join(skipped)}")
    return results


if __name__ == "__main__":
    results = run_all()
    for code, r in sorted(results.items()):
        bias = r.get('bias', 0)
        mae = r.get('mae', 0)
        maxe = r.get('maxErr', 0)
        err_rate = r.get('errRate05', 0)
        cls = r.get('class', '?')
        tag = f"[{cls}]" + (f"<{r.get('etf','')}>" if r.get('etf') else "")
        print(f"{code} {tag}: bias={bias:+.3f}% mae={mae:.3f}% maxErr={maxe:.3f}% err>0.5%={err_rate}% ({r.get('errDays',0)}/{r.get('totalDays',0)})")
