# -*- coding: utf-8 -*-
# AI-SUMMARY: ETF/指数/期货价格增量更新，走Yahoo Deno代理
"""ETF、指数、期货价格增量更新。

所有Yahoo请求走Deno Deploy代理，服务器不再直连Yahoo。
支持三种ticker类型:
  - 指数: ^NDX, ^GSPC 等
  - 期货: CL=F, BZ=F, GC=F 等
  - ETF:  KWEB, AGG, GLD 等 (使用后复权价格)
"""
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

from data_fetch.lof_db.schema import get_db


def _load_etf_list() -> List[str]:
    """从 INDEX_ETF 动态提取所有需要跟踪的标的ticker。"""
    try:
        from data_fetch.lof_iopv.fund_classifier import INDEX_ETF
        etfs = set()
        for mappings in INDEX_ETF.values():
            for item in mappings:
                etfs.add(item[0])
        return sorted(etfs)
    except Exception:
        return sorted({'^GSPC', '^NDX', '^SP500-45', '^SP500EW-35', '^SPBIO',
                        '^SP500-30', '^DJUSRE', '^SPSIOP', '^HSI',
                        'CL=F', 'BZ=F', 'GC=F',
                        'IXC', 'INDA', 'GLD', 'KWEB', 'AGG'})


def _load_stock_list() -> List[str]:
    """从holdings表提取所有需要更新的ticker。"""
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT ticker, market FROM holdings').fetchall()
    conn.close()
    return [(r[0], r[1]) for r in rows if r[0]]


def _fetch_yahoo_history(ticker: str, market: str = "", period: str = "3mo") -> Dict[str, float]:
    """通过Deno代理拉取Yahoo历史收盘价(后复权)。"""
    from data_fetch.lof_iopv.yahoo_finance import fetch_history, normalize_ticker_for_yahoo
    # 指数和期货不需要后缀
    if ticker.startswith("^") or "=F" in ticker:
        yahoo_sym = ticker
    else:
        yahoo_sym = normalize_ticker_for_yahoo(ticker, market)
    return fetch_history(yahoo_sym, period=period)


def _update_prices(conn, table: str, ticker: str, prices: Dict[str, float]) -> int:
    """通用价格写入，返回新增条数。"""
    count = 0
    for date_str, close in prices.items():
        conn.execute(
            f'INSERT OR REPLACE INTO {table} (ticker, date, close) VALUES (?, ?, ?)',
            (ticker, date_str, close)
        )
        count += 1
    return count


def update_etf():
    """更新标的价格(指数/期货/ETF，来自INDEX_ETF映射)。"""
    conn = get_db()
    total_inserted = 0
    etf_list = _load_etf_list()
    print(f'标的列表 ({len(etf_list)}): {", ".join(etf_list[:15])}{"..." if len(etf_list) > 15 else ""}')
    for ticker in etf_list:
        # 指数和期货用ticker本身，ETF推断market
        if ticker.startswith("^") or "=F" in ticker:
            market = ""
        else:
            from data_fetch.lof_iopv.yahoo_finance import determine_market_from_ticker
            market = determine_market_from_ticker(ticker)
        prices = _fetch_yahoo_history(ticker, market)
        if not prices:
            print(f'  {ticker}: 无数据')
            continue
        inserted = _update_prices(conn, 'etf_prices', ticker, prices)
        conn.commit()
        total_inserted += inserted
        kind = "指数" if ticker.startswith("^") else ("期货" if "=F" in ticker else "ETF")
        print(f'  {ticker}: {inserted}条 ({kind})')
        time.sleep(0.3)
    conn.close()
    return total_inserted


def update_stocks(tickers: Optional[List[tuple]] = None):
    """更新持仓个股价格(后复权)。

    Args:
        tickers: [(ticker, market), ...] 列表。None则从DB读取。
    """
    if tickers is None:
        tickers = _load_stock_list()

    conn = get_db()
    total_inserted = 0
    print(f'股票列表 ({len(tickers)}): {", ".join(t[:10] for t,_ in tickers)}...')
    for ticker, market in tickers:
        if not ticker:
            continue
        prices = _fetch_yahoo_history(ticker, market)
        if not prices:
            print(f'  {ticker}: 无数据 ({market})')
            continue
        inserted = _update_prices(conn, 'stock_prices', ticker, prices)
        conn.commit()
        total_inserted += inserted
        print(f'  {ticker}: {inserted}条 ({market})')
        time.sleep(0.3)
    conn.close()
    return total_inserted


def update_all():
    print('=== 更新标的价格 (指数/期货/ETF, Yahoo Deno代理) ===')
    etf_count = update_etf()
    print(f'\n=== 更新持仓股票价格 (Yahoo Deno代理) ===')
    stock_count = update_stocks()
    print(f'\n完成: 标的 {etf_count}条 股票 {stock_count}条')
    return etf_count + stock_count


if __name__ == '__main__':
    update_all()