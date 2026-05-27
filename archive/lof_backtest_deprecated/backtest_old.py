# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF回测脚本，从数据库读取数据计算R²/MAE
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF回测脚本 - 从数据库读取"""

import numpy as np
from collections import defaultdict
from data_fetch.lof_db.schema import get_db


def get_nav_series(code):
    """获取基金净值时间序列"""
    conn = get_db()
    rows = conn.execute(
        'SELECT date, nav FROM fund_nav WHERE code = ? ORDER BY date',
        (code,)
    ).fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def get_etf_series(ticker):
    """获取ETF价格时间序列"""
    conn = get_db()
    rows = conn.execute(
        'SELECT date, close FROM etf_prices WHERE ticker = ? ORDER BY date',
        (ticker,)
    ).fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}


def daily_ret(prices):
    """计算日收益率"""
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


def backtest_a(code, weights):
    """A类回测"""
    nav = get_nav_series(code)
    fund_ret = daily_ret(nav)
    if not fund_ret:
        return None

    total_w = sum(weights.values())
    etf_rets = {}
    for ticker, w in weights.items():
        prices = get_etf_series(ticker)
        if not prices:
            return None
        etf_rets[ticker] = (daily_ret(prices), w / total_w)

    common = set(fund_ret.keys())
    for er, _ in etf_rets.values():
        common &= set(er.keys())

    aligned = [d for d in sorted(common) if all(er[d][1] == fund_ret[d][1] for er, _ in etf_rets.values())]
    if len(aligned) < 10:
        return None

    y = np.array([fund_ret[d][0] for d in aligned])
    x = np.array([sum(er[d][0] * w for er, w in etf_rets.values()) for d in aligned])

    n = len(y)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    beta = np.dot(x, y) / np.dot(x, x) if np.dot(x, x) > 0 else 0

    abs_err = np.abs(y - x)
    mae = np.mean(abs_err) * 100
    max_err = np.max(abs_err) * 100
    over05 = int(np.sum(abs_err > 0.005))
    over03 = int(np.sum(abs_err > 0.003))
    dir_ok = sum(1 for a, b in zip(y, x) if (a > 0 and b > 0) or (a < 0 and b < 0))
    dir_pct = dir_ok / n * 100
    tag = 'OK' if max_err < 0.5 and over05 == 0 else ('WARN' if over05 <= 3 else 'BAD')

    return {
        'code': code, 'n': n, 'r2': round(r2, 4), 'beta': round(beta, 4),
        'mae': round(mae, 4), 'max_err': round(max_err, 4),
        'over05': over05, 'over03': over03, 'dir': round(dir_pct, 1), 'tag': tag,
    }


def run_backtest():
    """运行所有基金回测"""
    conn = get_db()
    funds = conn.execute(
        "SELECT code, name, estimation, etf FROM funds WHERE estimation = 'A'"
    ).fetchall()
    conn.close()

    # ETF权重映射
    etf_weights = {
        'XLE': 1.0, 'XOP': 1.0, 'GLD': 1.0, 'USO': 1.0,
        'GDX': 0.5, 'BNO': 0.4, 'GSG': 0.5, 'DJP': 1.0,
        'XLK': 1.0, 'SMH': 1.0, 'QQQ': 1.0, 'SPY': 1.0,
        'RSPH': 1.0, 'XBI': 1.0, 'XLY': 1.0, 'VNQ': 1.0,
        'AGG': 1.0, 'INDA': 1.0,
    }

    results = []
    for code, name, estimation, etf in funds:
        if not etf:
            continue
        weights = {etf: etf_weights.get(etf, 1.0)}
        r = backtest_a(code, weights)
        if r:
            r['name'] = name
            r['etf'] = etf
            results.append(r)

    return results


if __name__ == '__main__':
    results = run_backtest()
    print(f"{'code':<8}{'name':<14}{'ETF':<8}{'N':>3}{'R2':>8}{'MAE%':>8}{'tag':>5}")
    print('-' * 60)
    for r in sorted(results, key=lambda x: -x['r2']):
        print(f"{r['code']:<8}{r['name']:<14}{r['etf']:<8}{r['n']:>3}{r['r2']:>8.4f}{r['mae']:>8.4f}{r['tag']:>5}")