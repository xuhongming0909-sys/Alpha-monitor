# -*- coding: utf-8 -*-
# AI-SUMMARY: ETF和个股价格增量更新，统一使用新浪akshare替代东财secid反查
# 对应 INDEX.md §9.3 文件摘要索引
"""ETF/个股价格增量更新 - 新浪akshare stock_us_daily + stock_hk_daily"""

import os
import time

for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
    os.environ[k] = ''

from data_fetch.lof_db.schema import get_db


def _load_etf_list() -> list[str]:
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        etfs = {f["etf"] for f in funds if f.get("etf") and f.get("estimation") == "A"}
        if etfs:
            return sorted(etfs)
    except Exception:
        pass
    return ['QQQ', 'SPY', 'GLD', 'XLK']


def _load_stock_list() -> list[str]:
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT ticker FROM holdings').fetchall()
    conn.close()
    return sorted([r[0] for r in rows if r[0]])


def _is_hk(ticker: str) -> bool:
    """判断是否港股：5位数字开头或HK前缀"""
    return ticker.isdigit() and len(ticker) == 5


def _fetch_sina(ticker: str) -> dict[str, float]:
    """通过新浪akshare拉取美股/港股历史日线收盘价"""
    import akshare as ak
    try:
        if _is_hk(ticker):
            df = ak.stock_hk_daily(symbol=ticker, adjust='qfq')
        else:
            df = ak.stock_us_daily(symbol=ticker, adjust='qfq')
        prices = {}
        for _, row in df.iterrows():
            date_str = str(row['date'])[:10]
            close = float(row['close'])
            if close > 0:
                prices[date_str] = close
        return prices
    except Exception as e:
        print(f'  {ticker}: 新浪拉取失败 - {e}')
        return {}


def update_etf():
    conn = get_db()
    total_inserted = 0
    etf_list = _load_etf_list()
    print(f'ETF列表 ({len(etf_list)}): {", ".join(etf_list)}')
    for ticker in etf_list:
        prices = _fetch_sina(ticker)
        if not prices:
            continue
        for date_str, close in prices.items():
            conn.execute(
                'INSERT OR REPLACE INTO etf_prices (ticker, date, close) VALUES (?, ?, ?)',
                (ticker, date_str, close)
            )
        conn.commit()
        total_inserted += len(prices)
        print(f'  {ticker}: {len(prices)}天')
        time.sleep(0.3)
    conn.close()
    return total_inserted


def update_stocks(tickers: list[str] = None):
    if tickers is None:
        tickers = _load_stock_list()
    conn = get_db()
    total_inserted = 0
    print(f'股票列表 ({len(tickers)}): {", ".join(tickers[:10])}{"..." if len(tickers) > 10 else ""}')
    for ticker in tickers:
        prices = _fetch_sina(ticker)
        if not prices:
            continue
        for date_str, close in prices.items():
            conn.execute(
                'INSERT OR REPLACE INTO stock_prices (ticker, date, close) VALUES (?, ?, ?)',
                (ticker, date_str, close)
            )
        conn.commit()
        total_inserted += len(prices)
        print(f'  {ticker}: {len(prices)}天')
        time.sleep(0.3)
    conn.close()
    return total_inserted


def update_all():
    print('=== 更新ETF价格 ===')
    etf_count = update_etf()
    print(f'\n=== 更新持仓股票价格 ===')
    stock_count = update_stocks()
    print(f'\n完成: ETF {etf_count}条, 股票 {stock_count}条')
    return etf_count + stock_count


if __name__ == '__main__':
    update_all()