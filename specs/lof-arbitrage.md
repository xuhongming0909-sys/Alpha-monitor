---
name: lof-iopv
description: QDII LOF IOPV 估值策略 - 20字段（27只基金）
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

27只 QDII LOF 基金，两类估值：
- **A类 指数跟踪法（23只）**：`IOPV = NAV * (1 + etf_ret) * fx_ratio`
- **B类 T10持仓法（4只）**：`IOPV = NAV * [1 + stock_ratio * sum(w_i * ret_i * fx_i)]`

完整基金标的清单见 `specs/lof-holdings.md`。

## 2. 数据源

| 数据 | API | 刷新间隔 |
|---|---|---|
| 净值NAV | 东财 `api.fund.eastmoney.com/f10/lsjz` | 每日 |
| 持仓Top10 | 东财 `fundf10.eastmoney.com/FundArchivesDatas` | 每日 |
| LOF场内价 | 腾讯 `shared.market_service.get_quotes()` | 60秒 |
| 持仓股价 | 腾讯 `shared.market_service.get_quotes()` | 60秒 |
| 汇率 | 腾讯/akshare央行中间价 | 60秒 |
| 基金档案 | 东财 `fundf10.eastmoney.com/jbgk_{code}.html` | 每日 |
| 份额数据 | 东财 lsjz API | 每日 |
| 申购限额 | 集思录 `jisilu.cn/data/qdii/qdii_list/A` | 每日 |
| 股票仓位 | 东财 `pingzhongdata/{code}.js` | 每日 |

## 3. 主表20字段

| # | 字段 | key | 来源 |
|---|---|---|---|
| 1 | 代码 | code | fetcher |
| 2 | 名称 | name | fetcher |
| 3 | T-2净值 | nav | 东财lsjz |
| 4 | T-2净值日期 | navDate | 东财lsjz |
| 5 | 现价 | price | 腾讯行情 |
| 6 | 实时估值 | iopv | 双引擎计算 |
| 7 | 实时溢价率 | premiumRate | (price/iopv-1)*100 |
| 8 | 申购状态 | applyStatus | 东财jbgk + 集思录限额 |
| 9 | 新增份额 | shareIncrease | 东财lsjz |
| 10 | 原有份额 | shareTotal | 东财lsjz |
| 11 | 申购费 | applyFee | 东财jbgk |
| 12 | 赎回费 | redeemFee | 东财jbgk |
| 13 | 托管费 | custodianFee | 东财jbgk |
| 14 | 基金公司 | fundCompany | 东财jbgk |
| 15 | 估值标的 | calcTarget | A类=ETF代码, B类="前十大" |
| 16 | 动态仓位 | stockPosition | A类=反推, B类=Top10合计 |
| 17 | R2 | r2 | 回测结果 |
| 18 | 平均误差 | mae | 回测结果 |
| 19 | MAX误差 | maxErr | 回测结果 |
| 20 | 样本区间 | samplePeriod | 回测结果 |

## 4. 估值标的字段说明

- A类：列出对应ETF标的代码（如 SMH、QQQ、SPY）
- B类：固定显示"前十大"

## 5. 监控池规则

### 5.1 限购池
存在限购 + 溢价率>1% + 成交额>100万 + 非暂停

### 5.2 非限池
不限购 + |溢价率|>5% + 成交额>100万 + 非暂停

## 6. 推送规则

交易日 14:00 单次推送。

## 7. 回测方法

### A类回测
- 脚本：`tools/backtest/qdii_backtest_A.py` / `tools/backtest/lof13_backtest_A.py`
- 方法：基金净值日收益率 vs ETF日收益率，对齐日期后计算R2/MAE/MaxErr
- 数据：NAV=东财lsjz, ETF=东财k.stock_us_hist（全部国内API）
- 结果：`runtime_data/backtest/a_results.json`

### B类回测
- 脚本：`tools/backtest/qdii_backtest_B.py`
- 方法：基金净值日收益率 vs T10持仓加权日收益率
- 数据：全部国内API（NAV=东财, 持仓=东财F10, 仓位=东财pingzhongdata, 股价=腾讯K线, 汇率=akshare）
- 结果：`runtime_data/backtest/b_results.json`

### A类回测结果（2026-03-03~2026-05-22，23只）

OK=13 WARN=3 BAD=7
详情见 specs/lof-holdings.md section 5

### B类回测结果（2026-03-11~2026-05-22，3只）

| 代码 | 名称 | R2 | MAE% | MaxErr% |
|------|------|-----|------|---------|
| 160125 | 南方香港 | 0.721 | 0.82 | 2.45 |
| 160644 | 港美互联网 | 0.926 | 0.38 | 0.97 |
| 164906 | 中概互联网 | 0.891 | 0.38 | 0.89 |

## 8. 缓存与刷新机制

- 场内价格/汇率：60秒缓存，交易时段刷新
- 基金净值/持仓/档案/限额：每日刷新（东财/集思录数据日更）
- 服务端整体刷新：60秒轮询（config.yaml `lof_arbitrage.refresh_interval_ms: 60000`）
- 回测结果：静态JSON文件，回测脚本运行后写入