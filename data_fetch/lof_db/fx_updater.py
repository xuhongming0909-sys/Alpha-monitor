# -*- coding: utf-8 -*-
# AI-SUMMARY: 汇率增量更新，从akshare央行中间价获取
# 对应 INDEX.md §9.3 文件摘要索引
"""汇率增量更新"""

from datetime import datetime
from data_fetch.lof_db.schema import get_db


def fetch_fx():
    """获取汇率历史"""
    import akshare as ak
    fx = {}
    year = str(datetime.now().year)
    start_date = year + "0101"
    end_date = year + "1231"
    for sym, key in [("美元", "USD"), ("港币", "HKD")]:
        try:
            df = ak.currency_boc_sina(symbol=sym, start_date=start_date, end_date=end_date)
            for _, row in df.iterrows():
                d = str(row.iloc[0])
                rate = float(row.iloc[4]) / 100
                fx[(key, d)] = rate
        except Exception as e:
            print(f'  FX {sym}: {e}')
    return fx


def update_fx():
    """增量更新汇率"""
    conn = get_db()
    fx = fetch_fx()
    total = 0

    for (currency, date), rate in fx.items():
        conn.execute(
            'INSERT OR REPLACE INTO fx_rates (currency, date, rate) VALUES (?, ?, ?)',
            (currency, date, rate)
        )
        total += 1

    conn.commit()
    conn.close()
    return total