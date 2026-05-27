# Plan: LOF 文档同步

## Steps

- [x] Step 1: 修复 specs/lof-arbitrage.md
  - [x] §8: daily_maintenance.py → scripts/lof_maintenance.py
  - [x] §5: 补充 stock_prices 表说明 + 清理策略
  - [x] §9: 补充 classifier.py, normalizer.py, backtest_v2.py
  - [x] §2: 拆分ETF/个股价格行，标注etf_updater来源
  - [x] §6: 补充backtest_v2.py
- [x] Step 2: 修复 INDEX.md
  - [x] §9.3 strategy: 补充 backtest_v2.py, classifier.py
  - [x] §9.3.1 lof_db: 更新 etf_updater.py 描述（含股票价格）
  - [x] §9.2 data_fetch: 补充 source.py, normalizer.py 条目
- [x] Step 3: 修复 calc.py docstring（iopv_calculator → backtest）
- [x] Step 4: 清理 MEMORY.md 重复条目（7→1）
- [x] Step 5: 验证通过，已提交 3726bb5
