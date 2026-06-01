"""
合并 etf_prices + stock_prices → prices 表
- etf_prices 数据优先（Yahoo复权价，source='yahoo'）
- stock_prices 补充（腾讯/Sina，source='tencent'）
- 冲突时保留 etf_prices 的数据
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'runtime_data', 'lof_db', 'lof.db')
if not os.path.exists(DB_PATH):
    # Try server path
    DB_PATH = '/home/ubuntu/Alpha monitor/runtime_data/lof_db/lof.db'

conn = sqlite3.connect(DB_PATH)

# 1. 创建 prices 表（如果不存在）
conn.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        ticker TEXT,
        date TEXT,
        close REAL,
        source TEXT,
        PRIMARY KEY (ticker, date)
    )
""")
conn.commit()

# 2. 从 etf_prices 插入（优先，标记 source='yahoo'）
etf_count = conn.execute("SELECT COUNT(*) FROM etf_prices").fetchone()[0]
print(f"etf_prices: {etf_count} 条")
conn.execute("""
    INSERT OR REPLACE INTO prices (ticker, date, close, source)
    SELECT ticker, date, close, 'yahoo' FROM etf_prices
""")
conn.commit()

# 3. 从 stock_prices 插入（不覆盖已有数据，标记 source='tencent'）
stock_count = conn.execute("SELECT COUNT(*) FROM stock_prices").fetchone()[0]
print(f"stock_prices: {stock_count} 条")
conn.execute("""
    INSERT OR IGNORE INTO prices (ticker, date, close, source)
    SELECT ticker, date, close, 'tencent' FROM stock_prices
""")
conn.commit()

# 4. 统计结果
prices_count = conn.execute("SELECT COUNT(*) FROM prices").fetchone()[0]
yahoo_count = conn.execute("SELECT COUNT(*) FROM prices WHERE source='yahoo'").fetchone()[0]
tencent_count = conn.execute("SELECT COUNT(*) FROM prices WHERE source='tencent'").fetchone()[0]
print(f"prices: {prices_count} 条 (yahoo={yahoo_count}, tencent={tencent_count})")

# 5. 验证 XLY 数据
rows = conn.execute("SELECT date, close, source FROM prices WHERE ticker='XLY' ORDER BY date DESC LIMIT 5").fetchall()
print("\nXLY 最新5条:")
for r in rows:
    print(f"  {r[0]}: {r[1]:.2f} ({r[2]})")

conn.close()
print("\n迁移完成！")