---
name: custom-monitor
description: 自定义监控模块规格：用户配置读取、套利收益率计算、监控列表管理
type: spec
---

# Module Spec: 自定义监控

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. Scope

- 读取用户自定义监控配置（来自运行态 JSON）
- 映射为总线记录，供策略层计算套利收益率
- 支持换股+现金对价、纯现金选择权两种模式
- 不覆盖：自动发现并购标的、历史回测

## 2. Requirements

- 监控配置持久化到 `custom_monitors.json`
- 支持 A 股、H 股、B 股跨市场监控
- 币种自动换算（CNY/HKD/USD）
- 安全系数约束在 [0, 1] 区间
- 至少填写换股比例、现金对价、现金选择权之一

## 3. Interface / API

**数据抓取（Python）**
- `read_custom_monitor_records() -> list[dict]` — 从运行态 JSON 读取并映射为总线记录

**策略层（Python）**
- `recalculate_monitor(monitor: dict, rates: dict) -> dict` — 重算换股腿、现金腿和收益率
- `to_cny(amount, currency, rates) -> float | None` — 币种换算

**策略层（JS）**
- `recalculateMonitor(monitor, rates) -> object` — JS 版重算（保留 3 位小数）
- `summarizeMonitor(monitor) -> object` — 提取 stockYieldRate / cashYieldRate / maxYieldRate
- `toCny(amount, currency, rates) -> number | null` — JS 版币种换算

**运行态服务（JS）**
- `getAllMonitors({ refreshPrices })` — 获取所有监控（可选刷新实时价格）
- `upsertMonitor(input)` — 新增/更新监控
- `deleteMonitor(id)` — 删除监控

**HTTP API**
- `GET /api/monitors?refreshPrices=0|1` — 获取所有监控
- `POST /api/monitors` — 新增/更新监控
- `DELETE /api/monitors/:id` — 删除监控

## 4. Rules

**数据来源**
- 配置：运行时状态文件 `custom_monitors.json`
- 价格：腾讯行情（通过 `getStockPrice`）
- 汇率：`exchange_rate` 模块（HKD/CNY、USD/CNY）

**监控输入字段**
- `targetCode`（目标代码，必填）
- `acquirerCode`（收购方代码，必填）
- `name`（监控名称）
- `stockRatio`（换股比例）
- `cashDistribution`（现金分配/对价）
- `cashDistributionCurrency`（现金对价币种，默认 CNY）
- `cashOptionPrice`（现金选择权价格）
- `cashOptionCurrency`（现金选择权币种，默认 CNY）
- `safetyFactor`（安全边际系数，默认 1，范围 [0, 1]）
- `acquirerPriceOriginal` / `targetPriceOriginal`（原始价格）
- `acquirerCurrency` / `targetCurrency`（原始价格币种，默认 CNY）
- `acquirerMarket` / `targetMarket`（市场：A/H/B，默认 A）

**计算规则（Python & JS 一致）**
```
target_price_cny = to_cny(target_price_original, target_currency, rates)
acquirer_price_cny = to_cny(acquirer_price_original, acquirer_currency, rates)
cash_distribution_cny = to_cny(cash_distribution, cash_distribution_currency, rates)
cash_option_price_cny = to_cny(cash_option_price, cash_option_currency, rates)

stock_payout = acquirer_price_cny * stock_ratio * safety_factor + cash_distribution_cny
stock_spread = stock_payout - target_price_cny
stock_yield_rate = (stock_spread / target_price_cny) * 100

cash_spread = cash_option_price_cny - target_price_cny
cash_yield_rate = (cash_spread / target_price_cny) * 100
```

**币种换算规则**
- CNY → 直接返回
- HKD → amount * rates.hkToCny
- USD → amount * rates.usdToCny
- 其他 → null

**安全系数规则**
- 输入 < 0 → 回退到默认值 1
- 输入 > 1 → 截断为 1
- 否则 → 原值

**校验规则**
- acquirerCode 和 targetCode 不能为空
- 至少填写 stockRatio、cashDistribution、cashOptionPrice 中的一项（非零有效值）

**推送规则**
- 监控结果纳入 overview 和定时摘要推送
- 推送时按 maxYieldRate 排序取前 5
- 展示格式：`{name} | 换股 {stockYieldRate}% | 现金 {cashYieldRate}% | 最大 {maxYieldRate}%`

## 5. Acceptance

- [ ] 创建监控时缺少 acquirerCode 或 targetCode，返回 400 错误
- [ ] 创建监控时未填写任何对价条款，返回 400 错误
- [ ] 刷新价格后，acquirerPrice 和 targetPrice 按汇率正确换算为 CNY
- [ ] 安全系数输入 1.5，实际存储为 1.0
- [ ] 港股监控（H 股）使用 hkToCny 汇率正确换算
