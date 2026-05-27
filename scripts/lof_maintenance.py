# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据库每日维护脚本，独立入口供cron/systemd调用
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF数据库每日维护

用法：python scripts/lof_maintenance.py [--dry-run]
"""

import sys
import os
import traceback

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, ROOT)


def run_maintenance(dry_run=False):
    print(f"=== LOF Database Maintenance {'(DRY RUN)' if dry_run else ''} ===")

    if dry_run:
        print("[dry-run] Would update and cleanup. Exiting.")
        return True

    try:
        from data_fetch.lof_db.updater import update_all
        results = update_all()

        print("\n=== Summary ===")
        for k, v in results.items():
            print(f"  {k}: {v}")

        return True
    except Exception as e:
        traceback.print_exc()
        return False


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    ok = run_maintenance(dry_run=dry)
    sys.exit(0 if ok else 1)