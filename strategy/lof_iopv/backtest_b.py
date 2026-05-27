# -*- coding: utf-8 -*-
# AI-SUMMARY: B类T10持仓法回测，从DB读取，输出b_results.json
# 对应 INDEX.md §9.3 文件摘要索引
"""B类回测: 基金净值日收益率 vs 持仓加权收益率，计算R²/MAE/maxErr/samplePeriod"""

import json
import os
import numpy as np

from data_fetch.lof_db.schema import get_db

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest', 'b_results.json')
MIN_SAMPLES = 10


def _load_b_funds() -> list[dict]:
    """从 config.yaml 读取 B 类基金列表。"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        return [f for f in funds if f.get("estimation") == "B" and f.get("code")]
    except Exception:
        return []


def _get_nav_series(code: str) -> dict[str, float]:
    conn = get_db()
    rows = conn.execute('SELECT date, nav FROM fund_nav WHERE code = ? ORDER BY date', (code,)).fetchall()
    conn.close()
    return {r[1]: r[0] for r in rows if r[0] is not None}


def _get_holdings(code: str) -> list[dict]:
    """获取最新一期持仓。"""
    conn = get_db()
    rows = conn.execute(
        'SELECT ticker, name, weight, market FROM holdings WHERE code = ? ORDER BY report_date DESC LIMIT 10',
        (code,)
    ).fetchall()
    conn.close()
    return [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]


def _get_stock_series(ticker: str) -> dict[str, float]:
    """获取持仓股票价格序列（尝试港股/美股前缀）。"""
    conn = get_db()
    # 尝试不同前缀
    for prefix in [f"hk{ticker}", f"us{ticker}", ticker]:
        rows = conn.execute(
            'SELECT date, close FROM etf_prices WHERE ticker = ? ORDER BY date',
            (prefix,)
        ).fetchall()
        if rows:
            conn.close()
            return {r[1]: r[0] for r in rows if r[0] is not None}
    conn.close()
    return {}


def _daily_ret(prices: dict[str, float]) -> dict[str, tuple[float, str]]:
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


def backtest_fund(code: str) -> dict | None:
    """单只 B 类基金回测。"""
    nav = _get_nav_series(code)
    if len(nav) < MIN_SAMPLES:
        return None
    holdings = _get_holdings(code)
    if not holdings:
        return None

    total_w = sum(h["weight"] for h in holdings)
    if total_w <= 0:
        return None

    # 各持仓股的收益率序列
    stock_rets = {}
    for h in holdings:
        prices = _get_stock_series(h["ticker"])
        if len(prices) >= 2:
            stock_rets[h["ticker"]] = (daily_ret(prices), h["weight"] / total_w)

    if not stock_rets:
        return None

    fund_ret = _daily_ret(nav)
    # 对齐日期
    common = set(fund_ret.keys())
    for ret, _ in stock_rets.values():
        common &= set(ret.keys())
    aligned = sorted(common)
    if len(aligned) < MIN_SAMPLES:
        return None

    y = np.array([fund_ret[d][0] for d in aligned])
    # 加权持仓收益率
    x = np.array([sum(ret[d][0] * w for ret, w in stock_rets.values() if d in ret) for d in aligned])

    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    abs_err = np.abs(y - x)
    mae = float(np.mean(abs_err)) * 100
    max_err = float(np.max(abs_err)) * 100

    return {
        "code": code,
        "r2": round(r2, 4),
        "mae": round(mae, 4),
        "maxErr": round(max_err, 4),
        "samplePeriod": f"{aligned[0]}~{aligned[-1]}",
    }


def run() -> dict:
    funds = _load_b_funds()
    results = {}
    for f in funds:
        r = backtest_fund(f["code"])
        if r:
            results[f["code"]] = r
    return results


def save(results: dict) -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f"已保存 {len(results)} 只基金回测结果到 {OUTPUT_PATH}")


if __name__ == "__main__":
    results = run()
    save(results)
    for code, r in sorted(results.items(), key=lambda x: -x[1]["r2"]):
        print(f"{code}: R²={r['r2']:.4f} MAE={r['mae']:.4f}% maxErr={r['maxErr']:.4f}%")