---
name: lof-iopv
description: QDII LOF IOPV 双引擎估值策略规格
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

仅 QDII LOF 基金，两类估值引擎：

- **A类 指数跟踪法**：`IOPV = NAV * (1 + etf_ret) * fx_ratio`
- **B类 T10持仓法**：`IOPV = NAV * [1 + stock_ratio * Σ(w_i * ret_i * fx_i)]`

基金列表见 `data_fetch/lof_iopv/fetcher.py` → `QDII_FUNDS`。

## 2. 数据源

| 数据 | 来源 |
|---|---|
| 净值NAV | 东财 `api.fund.eastmoney.com/f10/lsjz` |
| 持仓Top10 | 东财 `fundf10.eastmoney.com/FundArchivesDatas.aspx` |
| LOF场内价 | 腾讯 `shared.market_service.get_quotes()` |
| 持仓股价 | 腾讯 K线 `web.ifzq.gtimg.cn` |
| 汇率 | 腾讯/akshare央行中间价 |
| 基金档案 | 东财 pingzhongdata（费用/公司/状态） |

无集思录依赖。

## 3. 估值公式

### 3.1 A类（指数跟踪法）

对应 `backtest_a.py`：
```
etf_ret = etf_price_d / etf_price_prev - 1
fx_ret = fx_d / fx_prev - 1
est_ret = etf_ret * fx_ratio
IOPV = NAV * (1 + est_ret)
```

### 3.2 B类（T10持仓加权法）

对应 `backtest_b.py`：
```
for each holding i:
    local_ret_i = price_d_i / price_prev_i - 1
    cny_ret_i = local_ret_i * (1 + fx_ret)  # US→*usd, HK→*hkd
    weighted_ret += cny_ret_i * (weight_i / total_weight)
est_ret = stock_ratio * weighted_ret
IOPV = NAV * (1 + est_ret)
```

### 3.3 真值边界

- NAV缺失 → IOPV为空，不伪造
- 持仓不足 → 允许保留但标注
- 汇率缺失 → fx_ratio=1

## 4. 主表18字段

| # | 字段 | key | 来源 |
|---|---|---|---|
| 1 | 代码 | code | fetcher |
| 2 | 名称 | name | fetcher |
| 3 | 币种 | currency | fetcher |
| 4 | 净值 | nav | 东财NAV API |
| 5 | 净值日期 | navDate | 东财NAV API |
| 6 | 现价 | price | 腾讯行情 |
| 7 | 实时估值 | iopv | 双引擎计算 |
| 8 | 溢价率 | premiumRate | (price/iopv-1)*100 |
| 9 | 申购费 | applyFee | 东财基金档案 |
| 10 | 申购状态 | applyStatus | 东财基金档案 |
| 11 | 赎回费 | redeemFee | 东财基金档案 |
| 12 | 赎回状态 | redeemStatus | 东财基金档案 |
| 13 | 托管费 | custodianFee | 东财基金档案 |
| 14 | 基金公司 | fundCompany | 东财基金档案 |
| 15 | 估值核心 | calcMode | A/B分类决定 |
| 16 | 估值状态 | calcStatus | 计算过程描述 |
| 17 | 动态仓位 | stockPosition | 持仓权重合计 |
| 18 | 持仓明细 | holdings | 东财Top10 |

## 5. 监控池规则

### 5.1 限购池
存在限购 + 溢价率>1% + 成交额>100万 + 非暂停

### 5.2 非限池
不限购 + |溢价率|>5% + 成交额>100万 + 非暂停

## 6. 推送规则

交易日 14:00 单次推送。
内容：limitedMonitorRows + unlimitedMonitorRows。
空池不推送。