# -*- coding: utf-8 -*-
# AI-SUMMARY: ETF价格增量更新，从东方财富美股K线API获取
# 对应 INDEX.md §9.3 文件摘要索引
"""ETF价格增量更新"""

import requests
import time
from data_fetch.lof_db.schema import get_db

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': None, 'https': None}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0'})

# 所有需要的ETF/商品标的（东方财富secid=107）
ETF_LIST = [
    'XLE', 'XOP', 'GLD', 'USO', 'GDX', 'BNO', 'GSG', 'DJP',
    'XLK', 'SMH', 'QQQ', 'SPY', 'RSPH', 'XBI', 'XLY', 'VNQ', 'AGG', 'INDA',
]


def fetch_etf(ticker, start='20260101', end='20261231'):
    """获取ETF价格历史"""
    url = (f'https://push2his.eastmoney.com/api/qt/stock/kline/get'
           f'?secid=107.{ticker}'
           f'&fields1=f1,f2,f3,f4,f5,f6'
           f'&fields2=f51,f52,f53,f54,f55,f56,f57,f58'
           f'&klt=101&fqt=1&beg={start}&end={end}')
    try:
        r = SESSION.get(url, timeout=15)
        data = r.json()
        klines = (data.get('data') or {}).get('klines', [])
        prices = {}
        for k in klines:
            parts = k.split(',')
            prices[parts[0]] = float(parts[2])
        return prices
    except Exception as e:
        print(f'  {ticker}: {e}')
        return {}


def update_etf():
    """增量更新所有ETF价格"""
    conn = get_db()
    total_inserted = 0

    for ticker in ETF_LIST:
        prices = fetch_etf(ticker)
        if not prices:
            continue

        for date, close in prices.items():
            conn.execute(
                'INSERT OR REPLACE INTO etf_prices (ticker, date, close) VALUES (?, ?, ?)',
                (ticker, date, close)
            )
        conn.commit()
        total_inserted += len(prices)
        print(f'  {ticker}: {len(prices)} days')
        time.sleep(0.3)

    conn.close()
    return total_inserted