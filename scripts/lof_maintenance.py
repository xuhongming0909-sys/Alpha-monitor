# -*- coding: utf-8 -*-
"""LOF数据库每日维护脚本，独立入口供cron/systemd调用。"""
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

    results = {}
    errors = []

    # 逐步执行，记录失败但不中断
    steps = [
        ("nav", "data_fetch.lof_db.nav_updater", "update_nav"),
        ("etf", "data_fetch.lof_db.etf_updater", "update_etf"),
        ("fx", "data_fetch.lof_db.fx_updater", "update_fx"),
        ("holdings", "data_fetch.lof_db.holdings_updater", "update_holdings"),
    ]

    for key, module_name, func_name in steps:
        try:
            print(f"\nUpdating {key}...")
            import importlib
            mod = importlib.import_module(module_name)
            fn = getattr(mod, func_name)
            results[key] = fn()
        except Exception as e:
            errors.append(f"{key}: {e}")
            traceback.print_exc()

    # Cleanup
    try:
        print("\nCleaning up old data (>90 days)...")
        from data_fetch.lof_db.schema import cleanup_old_data
        results['cleanup'] = cleanup_old_data()
    except Exception as e:
        errors.append(f"cleanup: {e}")
        traceback.print_exc()

    # Summary
    print("\n=== Summary ===")
    for k, v in results.items():
        print(f"  {k}: {v}")
    if errors:
        print(f"\n=== Errors ({len(errors)}) ===")
        for e in errors:
            print(f"  FAIL: {e}")
        return False
    return True


if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    ok = run_maintenance(dry_run=dry)
    sys.exit(0 if ok else 1)