---
name: lof-iopv
description: QDII LOF IOPV 估值策略规格：范围、数据源、估值公式、监控池规则、推送规则
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 当前范围

仅保留 QDII LOF 基金，已移除指数LOF分组。

支持的基金列表见 `data_fetch/lof_iopv/fetcher.py` 中的 `QDII_FUNDS` 配置。

## 2. 数据来源

| 数据 | 来源 | 接口 |
|---|---|---|
| 基金净值 | 东财 | `api.fund.eastmoney.com/f10/lsjz` |
| 前十大持仓 | 东财 | `fundf10.eastmoney.com/FundArchivesDatas.aspx` |
| LOF场内价格 | 腾讯 | `shared.market_service.get_quotes()` |
| 持仓股价 | 腾讯 | `shared.market_service.get_quotes()` |
| 汇率 | 腾讯 | `shared.market_service.get_fx_rates()` |

不依赖集思录、Yahoo Finance 等外部数据源。

## 3. 估值公式

### 3.1 A类 - 指数跟踪法

`IOPV = NAV_base * (1 + index_change) * (1 + fx_change)`

当前版本简化为 `IOPV = NAV * fx_ratio`，后续接入指数行情。

### 3.2 B类 - T10持仓加权法

`IOPV = NAV_base * [1 + stock_position * sum(w_i * R_i)] * fx_ratio`

其中：
- `stock_position` = 股票仓位比例（默认90%）
- `w_i` = 第i只持仓股权重
- `R_i` = 第i只持仓股当期收益率
- `fx_ratio` = 当日汇率 / 基准汇率

### 3.3 C类 - FOF拟合法

当前返回 NAV 作为 IOPV。

## 4. 基金分类

- `T10`: 有持仓数据 → B类（T10持仓加权法）
- `ETF`: 单指数跟踪 → A类（指数跟踪法）
- `FOF`: 多ETF拟合 → C类（FOF拟合法）

分类依据：配置文件中的 `estimationMethod` 字段。

## 5. 主表字段

18个字段全部展示：

code, name, currency, nav, navDate, price, iopv, premiumRate,
applyFee, applyStatus, redeemFee, redeemStatus, custodianFee,
fundCompany, calcMode, calcStatus, stockPosition, backtest

## 6. 监控池规则

### 6.1 限购池

同时满足：
1. 存在限购（applyStatus含"限"）
2. 溢价率 > 1%
3. 成交额 > 100万
4. 不是暂停申购

### 6.2 非限池

同时满足：
1. 不限购（applyStatus含"不"或"正常"）
2. |溢价率| > 5%
3. 成交额 > 100万
4. 不是暂停申购

## 7. 推送规则

交易日 `14:00` 单次定时推送。

推送内容来自 `limitedMonitorRows` + `unlimitedMonitorRows`。

空监控池不推送。