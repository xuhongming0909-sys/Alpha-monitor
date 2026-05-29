# -*- coding: utf-8 -*-
"""ETF和个股价格增量更新，统一使用新浪akshare stock_us_daily + stock_hk_daily"""
import time
from data_fetch.lof_db.schema import get_db


def _load_etf_list() -> list[str]:
    """从 fund_classifier 动态提取所有需要跟踪的 ETF ticker。"""
    try:
        from data_fetch.lof_iopv.fund_classifier import INDEX_ETF
        etfs = set()
        for mappings in INDEX_ETF.values():
            for item in mappings:
                etfs.add(item[0])  # ticker is first element
        return sorted(etfs)
    except Exception:
        # Fallback to hardcoded if import fails
        return sorted({'SOXX', 'DBC', 'TIP', 'OIH', 'SPY', 'QQQ', 'XLK', 'RYH',
                        'XBI', 'XLY', 'IXC', 'IEO', 'XOP', 'GLD', 'INDA', 'IYR', 'USO', 'BNO'})


def _load_stock_list() -> list[str]:
    conn = get_db()
    rows = conn.execute('SELECT DISTINCT ticker FROM holdings').fetchall()
    conn.close()
    return sorted([r[0] for r in rows if r[0]])


def _is_hk(ticker: str) -> bool:
    """判断是否港股：5位数字开头"""
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


def _update_prices(conn, table, ticker, prices):
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
    conn = get_db()
    total_inserted = 0
    etf_list = _load_etf_list()
    print(f'ETF列表 ({len(etf_list)}): {", ".join(etf_list[:10])}{"..." if len(etf_list) > 10 else ""}')
    for ticker in etf_list:
        prices = _fetch_sina(ticker)
        if not prices:
            continue
        inserted = _update_prices(conn, 'etf_prices', ticker, prices)
        conn.commit()
        total_inserted += inserted
        print(f'  {ticker}: {inserted}条')
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
        inserted = _update_prices(conn, 'stock_prices', ticker, prices)
        conn.commit()
        total_inserted += inserted
        print(f'  {ticker}: {inserted}条')
        time.sleep(0.3)
    conn.close()
    return total_inserted


def update_all():
    print('=== 更新ETF价格 ===')
    etf_count = update_etf()
    print(f'\n=== 更新持仓股票价格 ===')
    stock_count = update_stocks()
    print(f'\n完成: ETF {etf_count}条 股票 {stock_count}条')
    return etf_count + stock_count


if __name__ == '__main__':
    update_all()