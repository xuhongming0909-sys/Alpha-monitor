# -*- coding: utf-8 -*-
"""批量更新基金持仓 + 价格数据到DB。"""
from __future__ import annotations

import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from data_fetch.lof_db.schema import get_db, init_db
from data_fetch.lof_iopv.report_holdings import get_fund_holdings, store_holdings_to_db

_LOOKBACK_DAYS = 120
_PDF_CACHE = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'qreport')


# ============================================================
# 价格获取
# ============================================================
def _fetch_us_prices(ticker: str, start: str, end: str) -> List[Tuple[str, float]]:
    import akshare as ak
    try:
        df = ak.stock_us_daily(symbol=ticker, adjust="")
        if df is None or df.empty:
            return []
        return [(str(row["date"])[:10], float(row["close"]))
                for _, row in df.iterrows()
                if start <= str(row["date"])[:10] <= end]
    except Exception:
        return []


def _fetch_hk_prices(ticker: str, start: str, end: str) -> List[Tuple[str, float]]:
    import akshare as ak
    try:
        df = ak.stock_hk_daily(symbol=ticker, adjust="")
        if df is None or df.empty:
            return []
        return [(str(row["date"])[:10], float(row["close"]))
                for _, row in df.iterrows()
                if start <= str(row["date"])[:10] <= end]
    except Exception:
        return []


def _fetch_a_prices(ticker: str, start: str, end: str) -> List[Tuple[str, float]]:
    """A股价格 - 用stock_zh_a_daily(新浪源，不需要代理)"""
    import akshare as ak
    try:
        # 判断前缀: 6开头=sh, 其他=sz
        prefix = "sh" if ticker.startswith(("6", "5")) else "sz"
        symbol = f"{prefix}{ticker}"
        df = ak.stock_zh_a_daily(symbol=symbol, adjust="")
        if df is None or df.empty:
            return []
        return [(str(row["date"])[:10], float(row["close"]))
                for _, row in df.iterrows()
                if start <= str(row["date"])[:10] <= end]
    except Exception:
        return []


def _fetch_yf_prices(ticker: str, start: str, end: str) -> List[Tuple[str, float]]:
    """yfinance保底"""
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        df = tk.history(start=start, end=end)
        if df is None or df.empty:
            return []
        return [(str(idx.date()), float(row["Close"])) for idx, row in df.iterrows()]
    except Exception:
        return []


def _fetch_nav(code: str, start: str, end: str) -> List[Tuple[str, float]]:
    import akshare as ak
    try:
        df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
        if df is None or df.empty:
            return []
        return [(str(row["净值日期"])[:10], float(row["单位净值"]))
                for _, row in df.iterrows()
                if start <= str(row["净值日期"])[:10] <= end]
    except Exception:
        return []


def _fetch_fx(start: str, end: str) -> List[Tuple[str, float]]:
    import akshare as ak
    try:
        df = ak.currency_boc_sina(symbol="美元",
                                  start_date=start.replace("-", ""),
                                  end_date=end.replace("-", ""))
        if df is None or df.empty:
            return []
        return [(str(row["日期"])[:10], float(row["中行折算价"]) / 100)
                for _, row in df.iterrows()]
    except Exception:
        return []


# ============================================================
# DB写入
# ============================================================
def _store_prices(ticker: str, market: str, prices: List[Tuple[str, float]], db_path: str = None):
    if not prices:
        return
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'lof_db', 'lof.db')
    conn = sqlite3.connect(db_path)
    table = "etf_prices" if market == "US" else "stock_prices"
    for d, p in prices:
        conn.execute(f"INSERT OR REPLACE INTO {table} (ticker, date, close) VALUES (?, ?, ?)", (ticker, d, p))
    conn.commit()
    conn.close()


def _store_nav(code: str, nav_data: List[Tuple[str, float]], db_path: str = None):
    if not nav_data:
        return
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'lof_db', 'lof.db')
    conn = sqlite3.connect(db_path)
    for d, n in nav_data:
        conn.execute("INSERT OR REPLACE INTO fund_nav (code, date, nav) VALUES (?, ?, ?)", (code, d, n))
    conn.commit()
    conn.close()


def _store_fx(fx_data: List[Tuple[str, float]], db_path: str = None):
    if not fx_data:
        return
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'lof_db', 'lof.db')
    conn = sqlite3.connect(db_path)
    for d, r in fx_data:
        conn.execute("INSERT OR REPLACE INTO fx_rates (currency, date, rate) VALUES (?, ?, ?)", ("USD", d, r))
    conn.commit()
    conn.close()


# ============================================================
# 主入口
# ============================================================
def update_all(fund_codes: List[str] = None):
    if fund_codes is None:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        fund_codes = [f["code"] for f in lof_cfg.get("funds", [])]

    init_db()
    end = datetime.now().strftime('%Y-%m-%d')
    start = (datetime.now() - timedelta(days=_LOOKBACK_DAYS)).strftime('%Y-%m-%d')

    # 1. 持仓
    print("=== 1. 更新持仓 ===")
    all_tickers: Dict[str, str] = {}
    from data_fetch.lof_iopv.holdings_hardcoded import get_hardcoded_holdings
    for code in fund_codes:
        valid, excluded, err = get_fund_holdings(code, _PDF_CACHE)
        if err or not valid:
            hardcoded = get_hardcoded_holdings(code)
            if hardcoded:
                valid = hardcoded
                print(f"  {code}: fallback硬编码 ({len(valid)} holdings)")
            else:
                print(f"  {code}: 无数据")
                continue
        store_holdings_to_db(code, valid)
        print(f"  {code}: {len(valid)} holdings OK")
        for t, w, m in valid:
            all_tickers[t] = m
        time.sleep(0.3)

    # 2. 价格
    print(f"\n=== 2. 更新价格 ({len(all_tickers)} tickers) ===")
    ok, fail = 0, 0
    for ticker, market in sorted(all_tickers.items()):
        if market == "US":
            prices = _fetch_us_prices(ticker, start, end)
            if not prices:
                prices = _fetch_yf_prices(ticker, start, end)
        elif market == "HK":
            prices = _fetch_hk_prices(ticker, start, end)
        elif market == "A":
            prices = _fetch_a_prices(ticker, start, end)
        else:
            continue
        if prices:
            _store_prices(ticker, market, prices)
            ok += 1
            print(f"  {ticker:8s} {market:2s} OK {len(prices):4d} rows")
        else:
            fail += 1
            print(f"  {ticker:8s} {market:2s} FAIL")
        time.sleep(0.3)

    # 3. NAV
    print(f"\n=== 3. 更新NAV ({len(fund_codes)} funds) ===")
    for code in fund_codes:
        nav_data = _fetch_nav(code, start, end)
        if nav_data:
            _store_nav(code, nav_data)
            print(f"  {code} OK {len(nav_data)} rows")
        else:
            print(f"  {code} FAIL")

    # 4. 汇率
    print("\n=== 4. 更新汇率 ===")
    fx_data = _fetch_fx(start, end)
    if fx_data:
        _store_fx(fx_data)
        print(f"  USD/CNY OK {len(fx_data)} rows")

    print(f"\n=== 完成: 价格{ok}成功 {fail}失败 ===")


if __name__ == "__main__":
    update_all()
