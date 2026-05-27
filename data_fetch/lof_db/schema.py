# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF数据库Schema定义和初始化
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF数据库Schema定义和初始化"""

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
    """初始化数据库表"""
    conn = get_db()
    conn.executescript("""
        -- 基金基本信息
        CREATE TABLE IF NOT EXISTS funds (
            code TEXT PRIMARY KEY,
            name TEXT,
            currency TEXT,
            estimation TEXT,
            etf TEXT,
            fund_company TEXT,
            apply_fee REAL,
            redeem_fee REAL,
            custodian_fee REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 基金净值历史
        CREATE TABLE IF NOT EXISTS fund_nav (
            code TEXT,
            date TEXT,
            nav REAL,
            PRIMARY KEY (code, date)
        );

        -- ETF价格历史
        CREATE TABLE IF NOT EXISTS etf_prices (
            ticker TEXT,
            date TEXT,
            close REAL,
            PRIMARY KEY (ticker, date)
        );

        -- 汇率历史
        CREATE TABLE IF NOT EXISTS fx_rates (
            currency TEXT,
            date TEXT,
            rate REAL,
            PRIMARY KEY (currency, date)
        );

        -- 持仓数据
        CREATE TABLE IF NOT EXISTS holdings (
            code TEXT,
            report_date TEXT,
            ticker TEXT,
            name TEXT,
            weight REAL,
            market TEXT,
            PRIMARY KEY (code, report_date, ticker)
        );

        -- IOPV计算结果
        CREATE TABLE IF NOT EXISTS iopv_results (
            code TEXT,
            date TEXT,
            nav REAL,
            iopv REAL,
            premium_rate REAL,
            calc_mode TEXT,
            calc_status TEXT,
            PRIMARY KEY (code, date)
        );

        -- 数据更新日志
        CREATE TABLE IF NOT EXISTS update_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT,
            update_type TEXT,
            rows_affected INTEGER,
            status TEXT,
            error_msg TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    print(f"Database initialized at {DB_PATH}")