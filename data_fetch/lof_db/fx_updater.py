# -*- coding: utf-8 -*-
"""汇率增量更新，只拉取DB中缺失的日期范围。"""
from datetime import datetime, timedelta
from data_fetch.lof_db.schema import get_db


def _get_max_date(conn, currency):
    """获取某币种在DB中的最大日期。"""
    row = conn.execute(
        'SELECT MAX(date) FROM fx_rates WHERE currency = ?', (currency,)
    ).fetchone()
    return row[0] if row and row[0] else None


def fetch_fx_incremental(currency, start_date, end_date):
    """按日期范围获取汇率。"""
    import akshare as ak
    sym_map = {"USD": "美元", "HKD": "港币"}
    sym = sym_map.get(currency)
    if not sym:
        return {}
    try:
        df = ak.currency_boc_sina(symbol=sym, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {}
        fx = {}
        for _, row in df.iterrows():
            d = str(row.iloc[0])
            # 归一化日期格式为 YYYY-MM-DD
            d = d.replace("/", "-").strip()
            if len(d) == 8 and d.isdigit():
                d = f"{d[:4]}-{d[4:6]}-{d[6:]}"
            rate = float(row.iloc[4]) / 100
            if rate > 0:
                fx[d] = rate
        return fx
    except Exception as e:
        print(f'  FX {currency} ({start_date}~{end_date}): {e}')
        return {}


def update_fx():
    """增量更新汇率：只拉取DB中缺失的日期。"""
    conn = get_db()
    total = 0
    today = datetime.now()
    today_str = today.strftime('%Y%m%d')

    for currency in ['USD', 'HKD']:
        max_date = _get_max_date(conn, currency)
        if max_date:
            # 从 max_date+1 开始拉
            start = (datetime.strptime(max_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y%m%d')
        else:
            # 无数据，拉全年
            start = str(today.year) + '0101'

        if start > today_str:
            print(f'  {currency}: 已是最新 ({max_date})')
            continue

        fx = fetch_fx_incremental(currency, start, today_str)
        for date_str, rate in fx.items():
            conn.execute(
                'INSERT OR REPLACE INTO fx_rates (currency, date, rate) VALUES (?, ?, ?)',
                (currency, date_str, rate)
            )
        conn.commit()
        total += len(fx)
        print(f'  {currency}: +{len(fx)} 条 ({start}~{today_str})')

    conn.close()
    return total
