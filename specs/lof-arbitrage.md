---
name: lof-iopv
description: QDII LOF IOPV 双引擎估值策略规格 - 数据源已确定
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

仅 QDII LOF 基金，两类估值：

- **A类 指数跟踪法**：`IOPV = NAV * (1 + etf_ret) * fx_ratio`
- **B类 T10持仓法**：`IOPV = NAV * [1 + stock_ratio * Σ(w_i * ret_i * fx_i)]`

基金列表：`data_fetch/lof_iopv/fetcher.py` → `QDII_FUNDS`
回测参考：`strategy/lof_iopv/backtest_a.py` / `backtest_b.py`

## 2. 数据源（已确定，不再变更）

| 数据 | API | 地址 |
|---|---|---|
| 净值NAV | 东财基金净值API | `http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}` |
| 持仓Top10 | 东财F10持仓HTML | `https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}` |
| LOF场内价 | 腾讯行情 | `shared.market_service.get_quotes()` → `sz{code}/sh{code}` |
| 持仓股价 | 腾讯行情 | `shared.market_service.get_quotes()` → `hk{ticker}/us{ticker}` |
| 汇率实时 | 腾讯行情 | `shared.market_service.get_fx_rates()` |
| 汇率历史 | akshare央行中间价 | `akshare.currency_boc_sina()` |
| 基金档案 | 东财基金档案HTML | `https://fundf10.eastmoney.com/jbgk_{code}.html` |

**不使用**：集思录、Yahoo Finance、Open Exchange Rates

## 3. 估值公式（与回测代码一致）

### 3.1 A类（指数跟踪法）→ backtest_a.py

```
etf_ret = etf_price_d / etf_price_prev - 1
fx_ret = fx_d / fx_prev - 1
est_ret = etf_ret * fx_ratio
IOPV = NAV * (1 + est_ret)
```

### 3.2 B类（T10持仓加权法）→ backtest_b.py

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
- 持仓不足 → 保留但标注
- 汇率缺失 → fx_ratio=1

## 4. 主表18字段

| # | 字段 | key | 来源API |
|---|---|---|---|
| 1 | 代码 | code | fetcher配置 |
| 2 | 名称 | name | fetcher配置 |
| 3 | 币种 | currency | fetcher配置 |
| 4 | 净值 | nav | 东财lsjz API |
| 5 | 净值日期 | navDate | 东财lsjz API |
| 6 | 现价 | price | 腾讯行情 get_quotes |
| 7 | 实时估值 | iopv | 双引擎计算 |
| 8 | 溢价率 | premiumRate | (price/iopv-1)*100 |
| 9 | 申购费 | applyFee | 东财jbgk HTML |
| 10 | 申购状态 | applyStatus | 东财jbgk HTML |
| 11 | 赎回费 | redeemFee | 东财jbgk HTML |
| 12 | 赎回状态 | redeemStatus | 东财jbgk HTML |
| 13 | 托管费 | custodianFee | 东财jbgk HTML |
| 14 | 基金公司 | fundCompany | 东财jbgk HTML |
| 15 | 估值核心 | calcMode | A/B分类 |
| 16 | 估值状态 | calcStatus | 计算过程 |
| 17 | 动态仓位 | stockPosition | 持仓权重合计 |
| 18 | 持仓明细 | holdings | 东财F10 HTML |

## 5. 监控池规则

### 5.1 限购池
存在限购 + 溢价率>1% + 成交额>100万 + 非暂停

### 5.2 非限池
不限购 + |溢价率|>5% + 成交额>100万 + 非暂停

## 6. 推送规则

交易日 14:00 单次推送。
内容：limitedMonitorRows + unlimitedMonitorRows。
空池不推送。