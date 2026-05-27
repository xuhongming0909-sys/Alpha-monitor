# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据库每日维护统一入口
"""LOF数据库每日维护 - 净值/ETF/股票/汇率/持仓/回测"""

import os
import sys
import datetime

for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
    os.environ[k] = ''

def run_daily():
    """执行全部每日维护"""
    from data_fetch.lof_db.schema import init_db
    init_db()
    print("=== 1. 更新净值 ===")
    try:
        from data_fetch.lof_db.nav_updater import update_nav
        update_nav()
    except Exception as e:
        print(f"  净值更新失败: {e}")

    print("\n=== 2. 更新ETF价格 ===")
    try:
        from data_fetch.lof_db.etf_updater import update_etf
        update_etf()
    except Exception as e:
        print(f"  ETF更新失败: {e}")

    print("\n=== 3. 更新持仓股票价格 ===")
    try:
        from data_fetch.lof_db.etf_updater import update_stocks
        update_stocks()
    except Exception as e:
        print(f"  股票更新失败: {e}")

    print("\n=== 4. 更新汇率 ===")
    try:
        from data_fetch.lof_db.fx_updater import update_fx
        update_fx()
    except Exception as e:
        print(f"  汇率更新失败: {e}")

    print("\n=== 5. 更新持仓 ===")
    try:
        from data_fetch.lof_db.holdings_updater import update_holdings
        update_holdings()
    except Exception as e:
        print(f"  持仓更新失败: {e}")

    print("\n=== 6. 执行回测 ===")
    try:
        from strategy.lof_iopv.backtest import run_all
        run_all()
    except Exception as e:
        print(f"  回测失败: {e}")

    print("\n=== 维护完成 ===")


if __name__ == "__main__":
    run_daily()