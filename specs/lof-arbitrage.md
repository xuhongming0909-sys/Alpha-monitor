---
name: lof-iopv
description: QDII LOF IOPV 估值策略 - 24只基金
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

24只QDII LOF基金，两类估值：
- **A类-指数跟踪法（19只）**：美股/商品/黄金/原油ETF映射，IOPV = NAV * (1 + etf_ret) * fx_ratio
- **B类-T10持仓加权法（5只）**：前十大持仓股票加权，IOPV = NAV * [1 + stock_ratio * sum(w_i * ret_i)] * fx_ratio

已移除：161815抗通胀、160216国泰商品、165513中信商品（FOF持仓不透明，无法拟合）

## 2. 数据源

| 数据 | API | 刷新间隔 |
|---|---|---|
| 净值NAV | 东财 lsjz API | 每日 |
| 持仓Top10 | akshare fund_portfolio_hold_em | 每日 |
| LOF场内价 | 腾讯行情 | 实时 |
| ETF/个股价格 | 新浪 stock_us_daily / stock_hk_daily | 每日 |
| 汇率 | akshare currency_boc_safe | 每日 |
| 申购限额 | 集思录 qdii_list | 每日 |

## 3. A类估值公式

```
IOPV = NAV_T-2 * (1 + ETF_ret) * (FX_today / FX_T-2)
```

## 4. B类估值公式

```
IOPV = NAV_T-2 * (1 + stock_ratio * sum(w_i * ret_i)) * fx_ratio
```

## 5. 数据库

- `fund_nav`: 基金净值历史
- `etf_prices`: ETF价格历史
- `stock_prices`: 持仓股票价格历史
- `fx_rates`: 汇率历史
- `holdings`: 持仓数据

## 6. 回测方法

- 统一脚本：`strategy/lof_iopv/backtest.py`
- A类：基金净值日收益 vs ETF日收益+汇率日收益
- B类：基金净值日收益 vs T10持仓加权日收益+汇率日收益
- 日期对齐：共同价格日期集合，取最近40天
- 评级：R²>=0.8且MaxErr<1%=OK, R²>=0.6=WARN, 否则BAD

## 7. 推送规则

- 条件：限购金额存在 + 溢价率 > 2%
- 内容：代码、名称、溢价率、限购金额
- 时间：交易日14:00
- 服务：notification/lof_iopv/service.js

## 8. 每日维护

- 脚本：data_fetch/lof_db/daily_maintenance.py
- 流程：净值 → ETF → 个股 → 汇率 → 持仓 → 回测

## 9. 文件结构

```
data_fetch/lof_iopv/    # 实时数据获取
data_fetch/lof_db/      # 数据库维护
strategy/lof_iopv/      # 估值计算 + 回测
notification/lof_iopv/  # 推送服务
config/config.yaml      # 基金列表 + 推送配置
specs/lof-arbitrage.md  # 本文件
```