---
name: exchange-rate
description: 汇率模块规格：港币/美元兑人民币实时汇率抓取
type: spec
---

# Module Spec: 汇率

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. Scope

- 抓取港币、美元兑人民币的实时汇率
- 为 AH 溢价、AB 溢价、自定义监控等模块提供汇率输入
- 不覆盖：其他币种（EUR、JPY 等）、历史汇率曲线

## 2. Requirements

- 汇率必须来自真实行情接口
- 价格必须大于 0，否则抛异常
- 作为依赖模块，不单独推送

## 3. Interface / API

**数据抓取（Python）**
- `fetch_exchange_rate_snapshot() -> dict` — 汇率快照

**策略层（Python）**
- `get_exchange_rates() -> dict` — 返回 hkdToCny、usdToCny
- `get_fx_rates(currencies) -> dict` — 底层通用汇率查询

**HTTP API**
- `GET /api/market/exchange-rate?force=0|1` — 返回汇率快照

## 4. Rules

**数据来源**
- 腾讯行情 `https://qt.gtimg.cn/q={query_code}`
- HKD 查询代码：`whHKDCNY`
- USD 查询代码：`whUSDCNY`

**输出字段**
- `hkdToCny`：港币兑人民币汇率
- `usdToCny`：美元兑人民币汇率
- `updateTime`：更新时间 ISO 格式
- `source`：固定为 `tencent`

**错误处理**
- 任一汇率价格 <= 0 时，抛 `RuntimeError("exchange_rate接口缺少 {currency}")`
- 返回结构统一使用 `build_success` / `build_error`

**配置**
- `data_fetch.exchange_rate.intraday: true`
- `data_fetch.exchange_rate.refresh_interval_ms: 300000`（5 分钟）
- `data_fetch.exchange_rate.source: "tencent"`

**总线记录**
- plugin: `exchange_rate`
- market: `FX`
- symbol: `CNY`
- metrics: `{ hkd_to_cny, usd_to_cny }`

## 5. Acceptance

- [ ] 正常网络下返回 hkdToCny 和 usdToCny 均为大于 0 的浮点数
- [ ] 腾讯行情接口异常时返回错误结构，不伪造汇率
- [ ] AH 溢价模块调用时，汇率数据在 5 分钟缓存期内复用
