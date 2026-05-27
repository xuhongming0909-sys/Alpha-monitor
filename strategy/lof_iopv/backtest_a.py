# -*- coding: utf-8 -*-
# AI-SUMMARY: A类指数跟踪法回测，从DB读取，输出a_results.json
# 对应 INDEX.md §9.3 文件摘要索引
"""A类回测: 基金净值日收益率 vs ETF日收益率，计算R²/MAE/maxErr/samplePeriod"""

import json
import os
import numpy as np

from data_fetch.lof_db.schema import get_db

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest', 'a_results.json')
MIN_SAMPLES = 10


def _load_a_funds() -> list[dict]:
    """从 config.yaml 读取 A 类基金列表。"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        return [f for f in funds if f.get("estimation") == "A" and f.get("etf")]
    except Exception:
        return []


def _get_series(table: str, key_col: str, val_col: str, key_val: str) -> dict[str, float]:
    """从 DB 读取时间序列 {date: value}。"""
    conn = get_db()
    rows = conn.execute(
        f'SELECT {val_col}, date FROM {table} WHERE {key_col} = ? ORDER BY date',
        (key_val,)
    ).fetchall()
    conn.close()
    return {r[1]: r[0] for r in rows if r[0] is not None}


def _daily_ret(prices: dict[str, float]) -> dict[str, tuple[float, str]]:
    """日收益率 {date: (ret, prev_date)}。"""
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


def backtest_fund(code: str, etf: str) -> dict | None:
    """单只 A 类基金回测。"""
    nav = _get_series("fund_nav", "code", "nav", code)
    etf_prices = _get_series("etf_prices", "ticker", "close", etf)
    if len(nav) < MIN_SAMPLES or len(etf_prices) < MIN_SAMPLES:
        return None

    fund_ret = _daily_ret(nav)
    etf_ret = _daily_ret(etf_prices)
    # 对齐：同一天的前一天也必须对齐
    common = sorted(set(fund_ret.keys()) & set(etf_ret.keys()))
    aligned = [d for d in common if fund_ret[d][1] == etf_ret[d][1]]
    if len(aligned) < MIN_SAMPLES:
        return None

    y = np.array([fund_ret[d][0] for d in aligned])
    x = np.array([etf_ret[d][0] for d in aligned])

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
    """运行所有 A 类基金回测，返回 {code: result}。"""
    funds = _load_a_funds()
    results = {}
    for f in funds:
        r = backtest_fund(f["code"], f["etf"])
        if r:
            results[f["code"]] = r
    return results


def save(results: dict) -> None:
    """保存到 a_results.json。"""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f"已保存 {len(results)} 只基金回测结果到 {OUTPUT_PATH}")


if __name__ == "__main__":
    results = run()
    save(results)
    for code, r in sorted(results.items(), key=lambda x: -x[1]["r2"]):
        print(f"{code}: R²={r['r2']:.4f} MAE={r['mae']:.4f}% maxErr={r['maxErr']:.4f}%")