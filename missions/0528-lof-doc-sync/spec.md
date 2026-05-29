# Mission: LOF 文档同步

**日期**: 2026-05-28
**类型**: 文档同步
**目标**: 对齐 specs/lof-arbitrage.md、INDEX.md、calc.py docstring 与实际代码

## 差距分析

| 文件 | 差距 | 严重度 |
|------|------|--------|
| specs/lof-arbitrage.md §8 | 引用不存在的 `daily_maintenance.py`，应为 `scripts/lof_maintenance.py` | 高 |
| specs/lof-arbitrage.md §9 | 文件结构缺 `classifier.py`、`normalizer.py`、`backtest_v2.py` | 中 |
| specs/lof-arbitrage.md §5 | `stock_prices` 表角色未说明 | 低 |
| INDEX.md §9.3 strategy | 缺 `backtest_v2.py`、`classifier.py` | 中 |
| INDEX.md §9.3.1 lof_db | `etf_updater.py` 同时处理股票价格，描述不完整 | 中 |
| INDEX.md | `fetcher.py` 重复出现两次 | 低 |
| calc.py docstring | 引用不存在的 `iopv_calculator.py` | 低 |
| MEMORY.md | "LOF数据库+回测架构" 条目重复 3 次 | 低 |

## 约束

- 只改文档，不改业务逻辑
- 文档语言：中文
- 文件上限 500 行
