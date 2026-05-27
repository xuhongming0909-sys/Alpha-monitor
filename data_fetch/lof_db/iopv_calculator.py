# -*- coding: utf-8 -*-
# AI-SUMMARY: IOPV计算引擎，从数据库读取数据计算估值
# 对应 INDEX.md §9.3 文件摘要索引
"""IOPV计算引擎"""

import math
from datetime import datetime, timedelta
from data_fetch.lof_db.schema import get_db


def get_latest_nav(code):
    """获取最新净值"""
    conn = get_db()
    row = conn.execute(
        'SELECT date, nav FROM fund_nav WHERE code = ? ORDER BY date DESC LIMIT 1',
        (code,)
    ).fetchone()
    conn.close()
    return row


def get_etf_price(ticker, date):
    """获取ETF价格"""
    conn = get_db()
    row = conn.execute(
        'SELECT close FROM etf_prices WHERE ticker = ? AND date <= ? ORDER BY date DESC LIMIT 1',
        (ticker, date)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_fx_rate(currency, date):
    """获取汇率"""
    if currency == 'CNY':
        return 1.0
    conn = get_db()
    row = conn.execute(
        'SELECT rate FROM fx_rates WHERE UPPER(currency) = UPPER(?) AND date <= ? ORDER BY date DESC LIMIT 1',
        (currency, date)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def calc_iopv_a(code, nav, nav_date, etf, fx_now):
    """A类估值: IOPV = NAV * (1 + etf_ret) * fx_ratio"""
    if not etf:
        return None, "无ETF标的"

    # 获取ETF当前价格和净值日价格
    etf_now = get_etf_price(etf, datetime.now().strftime('%Y-%m-%d'))
    etf_prev = get_etf_price(etf, nav_date)

    if not etf_now or not etf_prev or etf_prev == 0:
        return None, "ETF价格缺失"

    etf_ret = etf_now / etf_prev - 1

    # 获取汇率
    fx_base = get_fx_rate('USD', nav_date) if nav_date else None
    fx_ratio = None
    if fx_now and fx_base and fx_base > 0:
        fx_ratio = fx_now / fx_base
    if fx_ratio is None:
        return None, "汇率缺失"

    iopv = nav * (1 + etf_ret) * fx_ratio
    return round(iopv, 3), f"A类({etf},ret={etf_ret:.4f},fx={fx_ratio:.4f})"


def calc_iopv_b(code, nav, nav_date, holdings, stock_ratio, fx_now):
    """B类估值: IOPV = NAV * (1 + stock_ratio * weighted_ret)"""
    if not holdings:
        return None, "持仓缺失"

    total_w = sum(h.get('weight', 0) for h in holdings)
    if total_w <= 0:
        return None, "权重为零"

    weighted_ret = 0
    valid_count = 0
    for h in holdings:
        ticker = h['ticker']
        weight = h['weight']
        market = h['market']

        # 获取持仓股票当前价格和净值日价格
        price_now = get_etf_price(ticker, datetime.now().strftime('%Y-%m-%d'))
        price_prev = get_etf_price(ticker, nav_date)

        if not price_now or not price_prev or price_prev == 0:
            continue

        local_ret = price_now / price_prev - 1

        # 汇率调整
        fx_key = 'usd' if market == 'US' else 'hkd'
        fx_base = get_fx_rate(fx_key, nav_date) if nav_date else None
        fx_ratio = None
        if fx_now and fx_base and fx_base > 0:
            fx_ratio = fx_now / fx_base
        if fx_ratio is None:
            continue

        cny_ret = local_ret * fx_ratio
        weighted_ret += cny_ret * (weight / total_w)
        valid_count += 1

    if valid_count == 0:
        return None, "无有效持仓价格"

    est_ret = (stock_ratio / 100) * weighted_ret
    iopv = nav * (1 + est_ret)
    return round(iopv, 3), f"B类({valid_count}/{len(holdings)}持仓,仓位{stock_ratio:.0f}%)"


def calculate_all_iopv():
    """计算所有基金的IOPV"""
    conn = get_db()
    funds = conn.execute('SELECT * FROM funds').fetchall()
    columns = [desc[0] for desc in conn.execute('SELECT * FROM funds').description]

    today = datetime.now().strftime('%Y-%m-%d')
    fx_usd = get_fx_rate('USD', today)
    fx_hkd = get_fx_rate('HKD', today)

    results = []
    for fund_row in funds:
        fund = dict(zip(columns, fund_row))
        code = fund['code']
        estimation = fund['estimation']

        nav_row = get_latest_nav(code)
        if not nav_row:
            results.append({'code': code, 'iopv': None, 'status': 'NAV缺失'})
            continue

        nav_date, nav = nav_row
        fx_now = fx_usd if fund['currency'] == 'USD' else (fx_hkd if fund['currency'] == 'HKD' else None)

        if estimation == 'A':
            iopv, status = calc_iopv_a(code, nav, nav_date, fund['etf'], fx_now)
        elif estimation == 'B':
            holdings = conn.execute(
                'SELECT * FROM holdings WHERE code = ? ORDER BY report_date DESC LIMIT 10',
                (code,)
            ).fetchall()
            h_columns = [desc[0] for desc in conn.execute('SELECT * FROM holdings LIMIT 0').description]
            holdings = [dict(zip(h_columns, h)) for h in holdings]
            stock_ratio = sum(h['weight'] for h in holdings)
            iopv, status = calc_iopv_b(code, nav, nav_date, holdings, stock_ratio, fx_now)
        else:
            iopv, status = None, "未知估值类型"

        results.append({
            'code': code,
            'nav': nav,
            'nav_date': nav_date,
            'iopv': iopv,
            'status': status,
        })

    conn.close()
    return results


if __name__ == '__main__':
    results = calculate_all_iopv()
    for r in results:
        print(f"{r['code']}: iopv={r.get('iopv')} status={r.get('status')}")