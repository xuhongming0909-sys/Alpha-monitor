# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据更新调度器，统一管理净值/ETF/汇率/持仓更新+清理
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF数据更新调度器"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from data_fetch.lof_db.schema import get_db, init_db, cleanup_old_data, drop_unused_tables
from data_fetch.lof_db.nav_updater import update_nav
from data_fetch.lof_db.etf_updater import update_etf
from data_fetch.lof_db.fx_updater import update_fx
from data_fetch.lof_db.holdings_updater import update_holdings


def update_all():
    """更新所有数据 + 清理过期数据"""
    init_db()
    drop_unused_tables()
    results = {}

    print("Updating fund NAV...")
    results['nav'] = update_nav()

    print("Updating ETF prices...")
    results['etf'] = update_etf()

    print("Updating FX rates...")
    results['fx'] = update_fx()

    print("Updating holdings...")
    results['holdings'] = update_holdings()

    print("Cleaning up old data (>90 days)...")
    results['cleanup'] = cleanup_old_data()

    return results


if __name__ == '__main__':
    results = update_all()
    print("\nUpdate summary:")
    for key, val in results.items():
        print(f"  {key}: {val}")