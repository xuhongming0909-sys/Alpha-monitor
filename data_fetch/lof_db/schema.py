# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据库Schema定义和初始化（5表，90天保留）
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF数据库Schema定义和初始化"""

from datetime import datetime, timedelta
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'runtime_data', 'lof_db', 'lof.db')


def get_db():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库表（5张核心表）"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS fund_nav (
            code TEXT,
            date TEXT,
            nav REAL,
            PRIMARY KEY (code, date)
        );
        CREATE TABLE IF NOT EXISTS etf_prices (
            ticker TEXT,
            date TEXT,
            close REAL,
            PRIMARY KEY (ticker, date)
        );
        CREATE TABLE IF NOT EXISTS stock_prices (
            ticker TEXT,
            date TEXT,
            close REAL,
            PRIMARY KEY (ticker, date)
        );
        CREATE TABLE IF NOT EXISTS fx_rates (
            currency TEXT,
            date TEXT,
            rate REAL,
            PRIMARY KEY (currency, date)
        );
        CREATE TABLE IF NOT EXISTS holdings (
            code TEXT,
            report_date TEXT,
            ticker TEXT,
            name TEXT,
            weight REAL,
            market TEXT,
            PRIMARY KEY (code, report_date, ticker)
        );
    """)
    conn.commit()
    conn.close()


def drop_unused_tables(conn=None):
    """删除无用表（funds/iopv_results/update_log）"""
    own_conn = conn is None
    if own_conn:
        conn = get_db()
    for table in ('funds', 'iopv_results', 'update_log'):
        conn.execute(f'DROP TABLE IF EXISTS {table}')
    conn.commit()
    if own_conn:
        conn.close()


def cleanup_old_data(conn=None):
    """清理超过90天的历史数据（holdings不清理）"""
    own_conn = conn is None
    if own_conn:
        conn = get_db()
    today = datetime.now()
    stats = {}
    cutoff = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    for table in ('fund_nav', 'etf_prices', 'stock_prices', 'fx_rates'):
        cur = conn.execute(f'DELETE FROM {table} WHERE date < ?', (cutoff,))
        stats[table] = cur.rowcount
    conn.commit()
    if own_conn:
        conn.close()
    return stats


if __name__ == '__main__':
    init_db()
    drop_unused_tables()
    print(f"Database initialized at {DB_PATH}")