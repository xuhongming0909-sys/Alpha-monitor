---
name: lof-iopv
description: QDII LOF IOPV 双引擎估值策略（A类指数法 / B类T10持仓法）
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

31只QDII LOF基金，两类估值引擎：

- **A类（指数跟踪法）**：`IOPV = NAV * (1 + etf_ret) * fx_ratio`
- **B类（T10持仓加权法）**：`IOPV = NAV * [1 + stock_ratio * Σ(w_i * ret_i * fx_i)]`

基金列表见 `data_fetch/lof_iopv/fetcher.py` → `QDII_FUNDS`。

## 2. 基金分类

### A类：指数跟踪法（27只）

| 类型 | 基金 | ETF标的 | 回测R² |
|------|------|---------|--------|
| 美股指数 | 161128 标普信息科技 | XLK | - |
| 美股指数 | 501225 全球芯片 | SMH | - |
| 美股指数 | 161130 纳指 | QQQ | - |
| 美股指数 | 161125 标普500 | SPY | - |
| 美股指数 | 161126 标普医疗 | RSPH | - |
| 美股指数 | 161127 标普生物 | XBI | - |
| 美股指数 | 162415 标普可选消费 | XLY | - |
| 美股指数 | 160140 标普地产 | VNQ | - |
| 美股指数 | 501300 美国国债 | AGG | - |
| 美股指数 | 164824 工银印度 | INDA | - |
| 港股指数 | 159202 恒生科技联接 | HSTECH | - |
| 港股指数 | 513660 恒生科技ETF | HSTECH | - |
| 港股指数 | 513690 恒生高股息ETF | HSHKLI | - |
| 港股指数 | 520600 沪港深科技ETF | - | - |
| 石油商品 | 160416 华安石油 | XLE | 0.849 |
| 石油商品 | 162719 广发石油 | XOP | 0.916 |
| 石油商品 | 162411 华宝油气 | XOP | 0.991 |
| 石油商品 | 160723 嘉实原油 | USO | 0.065 |
| 石油商品 | 161129 易方达原油 | USO | 0.146 |
| 石油商品 | 501018 南方原油 | USO | 0.422 |
| 石油商品 | 163208 诺安油气 | XLE | 0.880 |
| 石油商品 | 160216 国泰商品 | GSG | 0.680 |
| 黄金商品 | 160719 嘉实黄金 | GLD | 0.930 |
| 黄金商品 | 164701 汇添富黄金 | GLD | 0.995 |
| 黄金商品 | 161116 易方达黄金 | GLD | 0.509 |
| 黄金商品 | 161815 银华抗通胀 | GLD | 0.295 |
| 黄金商品 | 165513 中信保诚商品 | GSG | 0.117 |

### B类：T10持仓加权法（4只）

| 基金 | 持仓市场 | 回测R² |
|------|----------|--------|
| 160644 港美互联 | HK+US | 0.926 |
| 164906 中美互联 | HK+US | 0.891 |
| 160125 南方香港 | HK | 0.721 |
| 501312 全球互联 | US | - |

## 3. 数据源

| 数据 | 来源 |
|---|---|
| 净值NAV | 东方财富 `api.fund.eastmoney.com/f10/lsjz` |
| 持仓Top10 | 东方财富 `fundf10.eastmoney.com/FundArchivesDatas.aspx` |
| LOF场内价 | 腾讯 `shared.market_service.get_quotes()` |
| 持仓股价 | 腾讯 K线 `web.ifzq.gtimg.cn` |
| 汇率 | 腾讯/akshare央行中间价 |
| 基金档案 | 东方财富 pingzhongdata（费用/公司/状态） |

无集思录依赖。

## 4. 估值公式

### 4.1 A类（指数跟踪法）

对应 `tools/backtest/lof13_backtest_A.py`：
```
etf_ret = etf_price_d / etf_price_prev - 1
fx_ret = fx_d / fx_prev - 1
est_ret = etf_ret * fx_ratio
IOPV = NAV * (1 + est_ret)
```

### 4.2 B类（T10持仓加权法）

对应 `tools/backtest/lof13_backtest_B.py`：
```
for each holding i:
    local_ret_i = price_d_i / price_prev_i - 1
    cny_ret_i = local_ret_i * (1 + fx_ret)  # US→usd, HK→hkd
    weighted_ret += cny_ret_i * (weight_i / total_weight)
est_ret = stock_ratio * weighted_ret
IOPV = NAV * (1 + est_ret)
```

### 4.3 真值边界
- NAV缺失 → IOPV为空，不伪造
- 持仓不足 → 允许保留但标注
- 汇率缺失 → fx_ratio=1

## 5. 主表18字段

| # | 字段 | key | 来源 |
|---|---|---|---|
| 1 | 代码 | code | fetcher |
| 2 | 名称 | name | fetcher |
| 3 | 币种 | currency | fetcher |
| 4 | 净值 | nav | 东方财富NAV API |
| 5 | 净值日期 | navDate | 东方财富NAV API |
| 6 | 现价 | price | 腾讯行情 |
| 7 | 实时估值 | iopv | 双引擎计算 |
| 8 | 溢价率 | premiumRate | (price/iopv-1)*100 |
| 9 | 申购费 | applyFee | 东方财富基金档案 |
| 10 | 申购状态 | applyStatus | 东方财富基金档案 |
| 11 | 赎回费 | redeemFee | 东方财富基金档案 |
| 12 | 赎回状态 | redeemStatus | 东方财富基金档案 |
| 13 | 托管费 | custodianFee | 东方财富基金档案 |
| 14 | 基金公司 | fundCompany | 东方财富基金档案 |
| 15 | 估值核心 | calcMode | A/B分类决定 |
| 16 | 估值状态 | calcStatus | 计算过程描述 |
| 17 | 动态仓位 | stockPosition | 持仓权重合计 |
| 18 | 持仓明细 | holdings | 东方财富Top10 |

## 6. 监控池规则
### 6.1 限购池: 存在限购 + 溢价率>1% + 成交额>100万 + 非暂停
### 6.2 非限池: 不限购 + |溢价率|>5% + 成交额>100万 + 非暂停

## 7. 推送规则
交易日 14:00 单次推送。内容：limitedMonitorRows + unlimitedMonitorRows。空池不推送。

## 8. 回测结论

详见 `tools/backtest/lof13_backtest_report.md`

- A类最佳：164701(黄金GLD, R²=0.995), 162411(油气XOP, R²=0.991)
- B类最佳：164906(中美互联, R²=0.891), 160644(港美互联, R²=0.926)
- 误差较大：原油类(USO)和FOF型基金拟合差，IOPV仅供参考