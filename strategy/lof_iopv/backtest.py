# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF统一回测 - A类指数法+B类T10持仓法，从DB读取，含汇率，共同日期对齐
"""LOF统一回测: A类=基金净值vs ETF+汇率, B类=基金净值vs T10持仓加权+汇率"""

import json
import os
import numpy as np

from data_fetch.lof_db.schema import get_db

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest', 'results.json')
MIN_SAMPLES = 10


def _load_funds():
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        return lof_cfg.get("funds", [])
    except Exception:
        return []


def _get_series(table, key_col, val_col, key_val):
    conn = get_db()
    rows = conn.execute(f'SELECT {val_col}, date FROM {table} WHERE {key_col} = ? ORDER BY date', (key_val,)).fetchall()
    conn.close()
    return {r[1]: r[0] for r in rows if r[0] is not None}


def _daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


def _calc(y, x):
    if len(y) < MIN_SAMPLES:
        return None
    n = len(y)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    abs_err = np.abs(y - x)
    mae = float(np.mean(abs_err)) * 100
    max_err = float(np.max(abs_err)) * 100
    over05 = int(np.sum(abs_err > 0.005))
    over03 = int(np.sum(abs_err > 0.003))
    dir_correct = sum(1 for i in range(n) if (y[i] > 0 and x[i] > 0) or (y[i] < 0 and x[i] < 0) or (abs(y[i]) < 0.0001 and abs(x[i]) < 0.0001))
    dir_acc = dir_correct / n * 100 if n > 0 else 0
    return {
        "r2": round(r2, 4), "mae": round(mae, 4), "maxErr": round(max_err, 4),
        "over05": over05, "over03": over03, "dirAcc": round(dir_acc, 1),
        "n": n, "samplePeriod": "",
    }


def backtest_a(code, etf):
    nav = _get_series("fund_nav", "code", "nav", code)
    etf_prices = _get_series("etf_prices", "ticker", "close", etf)
    fx_prices = _get_series("fx_rates", "currency", "rate", "USD")
    if len(nav) < MIN_SAMPLES or len(etf_prices) < MIN_SAMPLES:
        return None
    fund_ret = _daily_ret(nav)
    etf_ret = _daily_ret(etf_prices)
    fx_ret = _daily_ret(fx_prices) if fx_prices else {}
    common = sorted(set(fund_ret.keys()) & set(etf_ret.keys()))
    if fx_ret:
        common = sorted(set(common) & set(fx_ret.keys()))
    if len(common) > 40:
        common = common[-40:]
    yv, xv = [], []
    for i in range(1, len(common)):
        d, dp = common[i], common[i - 1]
        if d not in fund_ret or dp not in fund_ret: continue
        if d not in etf_ret or dp not in etf_ret: continue
        if fx_ret and (d not in fx_ret or dp not in fx_ret): continue
        yv.append(fund_ret[d][0])
        xv.append(etf_ret[d][0] + (fx_ret[d][0] if fx_ret else 0))
    r = _calc(np.array(yv), np.array(xv))
    if r: r["samplePeriod"] = f"{common[0]}~{common[-1]}"
    return r


def backtest_b(code):
    nav = _get_series("fund_nav", "code", "nav", code)
    if len(nav) < MIN_SAMPLES:
        return None
    conn = get_db()
    rows = conn.execute('SELECT ticker, name, weight, market FROM holdings WHERE code = ? ORDER BY report_date DESC LIMIT 10', (code,)).fetchall()
    conn.close()
    holdings = [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]
    if not holdings:
        return None
    total_w = sum(h["weight"] for h in holdings)
    if total_w <= 0:
        return None
    fx_prices = _get_series("fx_rates", "currency", "rate", "USD")
    fx_ret = _daily_ret(fx_prices) if fx_prices else {}
    stock_rets = {}
    for h in holdings:
        prices = _get_series("stock_prices", "ticker", "close", h["ticker"])
        if len(prices) >= 2:
            stock_rets[h["ticker"]] = (_daily_ret(prices), h["weight"] / total_w)
    if not stock_rets:
        return None
    fund_ret = _daily_ret(nav)
    nav_dates = sorted(nav.keys())
    r40 = nav_dates[-40:] if len(nav_dates) >= 40 else nav_dates
    yv, xv = [], []
    for i in range(1, len(r40)):
        d, dp = r40[i], r40[i - 1]
        if d not in fund_ret or dp not in fund_ret: continue
        if fund_ret[d][1] != dp: continue
        available = sum(1 for h in holdings if h["ticker"] in stock_rets and d in stock_rets[h["ticker"]][0] and dp in stock_rets[h["ticker"]][0])
        if available < len(holdings) * 0.5: continue
        wr = 0
        for h in holdings:
            if h["ticker"] in stock_rets:
                ret_dict, w = stock_rets[h["ticker"]]
                if d in ret_dict and dp in ret_dict:
                    wr += ret_dict[d][0] * w
        fx_v = fx_ret[d][0] if (fx_ret and d in fx_ret and dp in fx_ret) else 0
        yv.append(fund_ret[d][0])
        xv.append(wr + fx_v)
    r = _calc(np.array(yv), np.array(xv))
    if r:
        r["samplePeriod"] = f"{r40[0]}~{r40[-1]}"
        r["holdings_count"] = len(holdings)
    return r


def run_all():
    funds = _load_funds()
    results = {}
    for f in funds:
        code = f["code"]
        est = f.get("estimation", "A")
        if est == "A" and f.get("etf"):
            r = backtest_a(code, f["etf"])
            if r:
                r["type"] = "A"
                r["etf"] = f["etf"]
                r["code"] = code
                results[code] = r
        elif est == "B":
            r = backtest_b(code)
            if r:
                r["type"] = "B"
                r["code"] = code
                results[code] = r
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fp:
        json.dump(results, fp, ensure_ascii=False, indent=2)
    print(f"回测完成: {len(results)}只 -> {OUTPUT_PATH}")
    return results


if __name__ == "__main__":
    results = run_all()
    a_ok = sum(1 for r in results.values() if r.get("type") == "A" and r["r2"] >= 0.8 and r["maxErr"] < 1.0)
    a_warn = sum(1 for r in results.values() if r.get("type") == "A" and r["r2"] >= 0.6 and (r["r2"] < 0.8 or r["maxErr"] >= 1.0))
    a_bad = sum(1 for r in results.values() if r.get("type") == "A" and (r["r2"] < 0.6 or r["maxErr"] >= 2.0))
    b_ok = sum(1 for r in results.values() if r.get("type") == "B" and r["r2"] >= 0.8 and r["maxErr"] < 1.0)
    b_warn = sum(1 for r in results.values() if r.get("type") == "B" and r["r2"] >= 0.6)
    b_bad = sum(1 for r in results.values() if r.get("type") == "B" and r["r2"] < 0.6)
    print(f"A类: OK={a_ok} WARN={a_warn} BAD={a_bad}")
    print(f"B类: OK={b_ok} WARN={b_warn} BAD={b_bad}")