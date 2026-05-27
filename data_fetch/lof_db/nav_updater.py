# -*- coding: utf-8 -*-
# AI-SUMMARY: 基金净值增量更新，从东方财富API获取
# 对应 INDEX.md §9.3 文件摘要索引
"""基金净值增量更新"""

import requests
from datetime import datetime
from data_fetch.lof_db.schema import get_db

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://fundf10.eastmoney.com/',
})

# 所有A类基金代码
A_FUNDS = [
    '161128', '501225', '161130', '161125', '161126', '161127', '162415', '160140',
    '501300', '164824', '159202', '513660', '513690', '520600',
    '160416', '162719', '162411', '160723', '161129', '501018', '163208', '160216',
    '160719', '164701', '161116', '161815', '165513',
]

# 所有B类基金代码
B_FUNDS = ['160644', '164906', '160125', '501312']

ALL_FUNDS = A_FUNDS + B_FUNDS


def fetch_nav(code, pages=5):
    """获取基金净值历史"""
    nav = {}
    for p in range(1, pages + 1):
        url = f'http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={p}&pageSize=40&callback='
        try:
            r = SESSION.get(url, timeout=10)
            items = r.json()['Data']['LSJZList']
            if not items:
                break
            for i in items:
                nav[i['FSRQ']] = float(i['DWJZ'])
        except Exception as e:
            print(f'  {code} page {p}: {e}')
            break
    return nav


def update_nav():
    """增量更新所有基金净值"""
    conn = get_db()
    total_inserted = 0

    for code in ALL_FUNDS:
        nav = fetch_nav(code)
        if not nav:
            continue

        inserted = 0
        for date, nav_val in nav.items():
            try:
                conn.execute(
                    'INSERT OR IGNORE INTO fund_nav (code, date, nav) VALUES (?, ?, ?)',
                    (code, date, nav_val)
                )
                inserted += conn.total_changes
            except Exception:
                pass

        conn.commit()
        total_inserted += len(nav)
        print(f'  {code}: {len(nav)} days')

    conn.close()
    return total_inserted