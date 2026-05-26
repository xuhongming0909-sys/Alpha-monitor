---
name: lof-iopv
description: QDII LOF IOPV 估值策略 - 18字段（用户定义）
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

仅 QDII LOF 基金，两类估值：

- **A类 指数跟踪法**：`IOPV = NAV * (1 + etf_ret) * fx_ratio`
- **B类 T10持仓法**：`IOPV = NAV * [1 + stock_ratio * Σ(w_i * ret_i * fx_i)]`

## 2. 数据源（已确定）

| 数据 | API |
|---|---|
| 净值NAV | 东财 `api.fund.eastmoney.com/f10/lsjz` |
| 持仓Top10 | 东财 `fundf10.eastmoney.com/FundArchivesDatas.aspx` |
| LOF场内价 | 腾讯 `shared.market_service.get_quotes()` |
| 持仓股价 | 腾讯 `shared.market_service.get_quotes()` |
| 汇率 | 腾讯/akshare央行中间价 |
| 基金档案 | 东财 `fundf10.eastmoney.com/jbgk_{code}.html` |
| 份额数据 | 东财 lsjz API (份额字段) |

## 3. 主表18字段

| # | 字段 | key | 来源 |
|---|---|---|---|
| 1 | 代码 | code | fetcher |
| 2 | 名称 | name | fetcher |
| 3 | T-2净值 | nav | 东财lsjz |
| 4 | T-2净值日期 | navDate | 东财lsjz |
| 5 | 现价 | price | 腾讯行情 |
| 6 | 实时估值 | iopv | 双引擎计算 |
| 7 | 实时溢价率 | premiumRate | (price/iopv-1)*100 核心数据 |
| 8 | 申购状态 | applyStatus | 东财jbgk |
| 9 | 新增份额 | shareIncrease | 东财lsjz |
| 10 | 原有份额 | shareTotal | 东财lsjz |
| 11 | 申购费 | applyFee | 东财jbgk |
| 12 | 赎回费 | redeemFee | 东财jbgk |
| 13 | 托管费 | custodianFee | 东财jbgk |
| 14 | 基金公司 | fundCompany | 东财jbgk |
| 15 | 估值核心 | calcCore | A类=ETF标的, B类=前十大持仓摘要 |
| 16 | 动态仓位 | stockPosition | A类=反推, B类=Top10合计 |
| 17 | R² | r2 | 回测结果 |
| 18 | 平均误差 | mae | 回测结果 |
| 19 | MAX误差 | maxErr | 回测结果 |
| 20 | 样本区间 | samplePeriod | 回测结果 |

## 4. 估值核心字段说明

- A类：列出对应ETF标的代码（如 SMH、QQQ、SPY）
- B类：写出前十大持仓摘要（如 腾讯9.5%+拼多多8.0%+...）

## 5. 监控池规则

### 5.1 限购池
存在限购 + 溢价率>1% + 成交额>100万 + 非暂停

### 5.2 非限池
不限购 + |溢价率|>5% + 成交额>100万 + 非暂停

## 6. 推送规则

交易日 14:00 单次推送。