# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据库每日维护脚本，独立入口供cron/systemd调用
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF数据库每日维护

功能：
1. 同步基金列表
2. 增量更新净值/ETF/汇率/持仓
3. 清理过期数据
4. 日志写入 update_log 表

用法：python scripts/lof_maintenance.py [--dry-run]
"""

import sys
import os
import traceback

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)

from data_fetch.lof_db.schema import get_db, init_db, cleanup_old_data


def log_to_db(table_name, update_type, rows, status, error_msg=None):
    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO update_log (table_name, update_type, rows_affected, status, error_msg) VALUES (?, ?, ?, ?, ?)',
            (table_name, update_type, rows, status, error_msg)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def run_maintenance(dry_run=False):
    print(f"=== LOF Database Maintenance {'(DRY RUN)' if dry_run else ''} ===")

    if dry_run:
        print("[dry-run] Would update and cleanup. Exiting.")
        return True

    try:
        init_db()
        from data_fetch.lof_db.updater import update_all

        results = update_all()

        for key, val in results.items():
            log_to_db('maintenance', key, val if isinstance(val, int) else 0, 'success')

        print("\n=== Summary ===")
        for k, v in results.items():
            print(f"  {k}: {v}")

        return True
    except Exception as e:
        traceback.print_exc()
        log_to_db('maintenance', 'full_update', 0, 'error', str(e))
        return False


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    ok = run_maintenance(dry_run=dry)
    sys.exit(0 if ok else 1)