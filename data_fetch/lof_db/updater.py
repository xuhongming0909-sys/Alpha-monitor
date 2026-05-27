# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据更新调度器，统一管理净值/ETF/汇率/持仓更新
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF数据更新调度器"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from data_fetch.lof_db.schema import get_db, init_db
from data_fetch.lof_db.nav_updater import update_nav
from data_fetch.lof_db.etf_updater import update_etf
from data_fetch.lof_db.fx_updater import update_fx
from data_fetch.lof_db.holdings_updater import update_holdings
from data_fetch.lof_db.schema import cleanup_old_data



def sync_funds():
    from shared.config.script_config import load_config
    conn = get_db()
    cfg = load_config()
    plugins = cfg.get('data_fetch', {}).get('plugins', {})
    lof_cfg = plugins.get('lof_arbitrage', plugins.get('lof_iopv', {}))
    funds = lof_cfg.get('funds', [])
    count = 0
    for f in funds:
        code = f.get('code')
        if not code:
            continue
        conn.execute('INSERT OR REPLACE INTO funds (code, name, currency, estimation, etf, updated_at) VALUES (?, ?, ?, ?, ?, datetime("now"))',
            (code, f.get('name', ''), f.get('currency', 'USD'), f.get('estimation', 'A'), f.get('etf', '')))
        count += 1
    conn.commit()
    conn.close()
    return count


def update_all():
    """更新所有数据"""
    init_db()
    results = {}

    print("Updating fund NAV...")
    results['nav'] = update_nav()

    print("Updating ETF prices...")
    results['etf'] = update_etf()

    print("Updating FX rates...")
    results['fx'] = update_fx()

    print("Updating holdings...")
    results['holdings'] = update_holdings()

    print("Syncing fund list...")
    results['funds'] = sync_funds()

    print("Cleaning up old data...")
    results['cleanup'] = cleanup_old_data()

    return results


if __name__ == '__main__':
    results = update_all()
    print("\nUpdate summary:")
    for key, val in results.items():
        print(f"  {key}: {val}")