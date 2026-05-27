# LOF 数据库维护规范

## 1. 数据库用途

为两类消费者提供数据：
- **实时 IOPV 计算**：source.py 从 DB 查 nav-date 价格（ETF/stock），NAV 和 FX 实时抓取
- **回测**：backtest_v2.py 从 DB 读 3 个月历史数据

## 2. 表结构（5 张表）

| 表 | 用途 | 数据来源 | 保留策略 |
|----|------|----------|----------|
| `etf_prices` | ETF 历史 K 线（nav-date 价格查找 + 回测） | akshare stock_us_daily | **90 天** |
| `stock_prices` | 个股历史 K 线（B 类 nav-date + 回测） | akshare stock_us_daily / stock_hk_daily | **90 天** |
| `fund_nav` | 基金净值历史（回测） | 东方财富 f10/lsjz | **90 天** |
| `fx_rates` | 汇率历史（回测） | akshare currency_boc_sina | **90 天** |
| `holdings` | B 类持仓（回测 + B 类 IOPV 备用） | 东方财富 fund_portfolio_hold_em | **保留全部**（季度报告，量小） |

## 3. 已删除的表

| 表 | 原因 |
|----|------|
| `funds` | 从未被读取，config.yaml 是唯一真相来源 |
| `iopv_results` | 从未写入，IOPV 实时计算不存储 |
| `update_log` | 从未被读取，调试日志无用 |

## 4. 维护规则

### 4.1 执行频率
- 每天 06:30 CST 通过 systemd timer 自动执行
- 手动执行：`python scripts/lof_maintenance.py`

### 4.2 执行顺序
1. init_db() — 确保表结构
2. update_nav() — 增量抓取基金净值
3. update_etf() — 增量抓取 ETF K 线
4. update_fx() — 增量抓取汇率
5. update_holdings() — 增量抓取 B 类持仓
6. cleanup_old_data() — 删除超过 90 天的历史数据

### 4.3 清理策略
- `fund_nav`：DELETE WHERE date < (today - 90d)
- `etf_prices`：DELETE WHERE date < (today - 90d)
- `stock_prices`：DELETE WHERE date < (today - 90d)
- `fx_rates`：DELETE WHERE date < (today - 90d)
- `holdings`：不清理（季度报告，总量 < 200 行）

### 4.4 数据量预估（90 天）
- `fund_nav`：24 基金 × ~65 交易日 ≈ 1560 行
- `etf_prices`：~15 ETF × ~65 交易日 ≈ 975 行
- `stock_prices`：~50 持仓股 × ~65 交易日 ≈ 3250 行
- `fx_rates`：~65 行
- `holdings`：~100 行
- **总计 ≈ 5950 行**（当前 23 万行 → 清理后 0.6 万行）

## 5. 实时数据流

实时 IOPV 不依赖 DB 中的 NAV/FX/holdings，这些全部实时抓取。
DB 仅作为 nav-date 价格的查找源（A 类查 ETF，B 类查个股）。