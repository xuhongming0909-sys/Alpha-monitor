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
def _load_all_fund_codes() -> list[str]:
    """从 config.yaml 读取全部基金代码。"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get('data_fetch', {}).get('plugins', {})
        lof_cfg = plugins.get('lof_arbitrage', plugins.get('lof_iopv', {}))
        funds = lof_cfg.get('funds', [])
        if funds:
            return [f['code'] for f in funds if f.get('code')]
    except Exception:
        pass
    print('WARNING: config load failed, using 3-fund fallback')
    return ['164701', '161128', '161130']

ALL_FUNDS = _load_all_fund_codes()
A_FUNDS = ALL_FUNDS
B_FUNDS = ALL_FUNDS


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

        actual = 0
        for date, nav_val in nav.items():
            try:
                cur = conn.execute(
                    'INSERT OR IGNORE INTO fund_nav (code, date, nav) VALUES (?, ?, ?)',
                    (code, date, nav_val)
                )
                actual += cur.rowcount if cur.rowcount > 0 else 0
            except Exception:
                pass

        conn.commit()
        total_inserted += actual
        print(f'  {code}: {actual}/{len(nav)} new days')

    conn.close()
    return total_inserted
