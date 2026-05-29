# -*- coding: utf-8 -*-
# AI-SUMMARY: ETF和个股价格增量更新，走Yahoo Deno代理
"""ETF和个股价格增量更新。

所有Yahoo请求走Deno Deploy代理，服务器不再直连Yahoo。
"""
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

from data_fetch.lof_db.schema import get_db


def _load_etf_list() -> List[str]:
    """从 fund_classifier 动态提取所有需要跟踪的 ETF ticker。"""
    try:
        from data_fetch.lof_iopv.fund_classifier import INDEX_ETF
        etfs = set()
        for mappings in INDEX_ETF.values():
            for item in mappings:
                etfs.add(item[0])
        return sorted(etfs)
    except Exception:
        return sorted({'SOXX', 'DBC', 'TIP', 'OIH', 'SPY', 'QQQ', 'XLK', 'RYH',
                        'XBI', 'XLY', 'IXC', 'IEO', 'XOP', 'GLD', 'INDA', 'IYR', 'USO', 'BNO'})


def _load_stock_list() -> List[str]:
    """从holdings表提取所有需要更新的ticker。"""
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT ticker, market FROM holdings').fetchall()
    conn.close()
    return [(r[0], r[1]) for r in rows if r[0]]


def _fetch_yahoo_history(ticker: str, market: str = "", period: str = "3mo") -> Dict[str, float]:
    """通过Deno代理拉取Yahoo历史收盘价。"""
    from data_fetch.lof_iopv.yahoo_finance import fetch_history, normalize_ticker_for_yahoo
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
    """更新ETF价格（来自fund_classifier的硬编码列表）。"""
    from data_fetch.lof_iopv.yahoo_finance import determine_market_from_ticker
    conn = get_db()
    total_inserted = 0
    etf_list = _load_etf_list()
    print(f'ETF列表 ({len(etf_list)}): {", ".join(etf_list[:10])}{"..." if len(etf_list) > 10 else ""}')
    for ticker in etf_list:
        market = determine_market_from_ticker(ticker)
        prices = _fetch_yahoo_history(ticker, market)
        if not prices:
            print(f'  {ticker}: 无数据')
            continue
        inserted = _update_prices(conn, 'etf_prices', ticker, prices)
        conn.commit()
        total_inserted += inserted
        print(f'  {ticker}: {inserted}条 ({market})')
        time.sleep(0.3)
    conn.close()
    return total_inserted


def update_stocks(tickers: Optional[List[tuple]] = None):
    """更新持仓个股价格。

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
    print('=== 更新ETF价格 (Yahoo Deno代理) ===')
    etf_count = update_etf()
    print(f'\n=== 更新持仓股票价格 (Yahoo Deno代理) ===')
    stock_count = update_stocks()
    print(f'\n完成: ETF {etf_count}条 股票 {stock_count}条')
    return etf_count + stock_count


if __name__ == '__main__':
    update_all()