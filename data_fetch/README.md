# Data Fetch Domain

本目录只负责"上游数据获取 + normalizer映射"。

## 职责

- 对接 AkShare、腾讯、巨潮、集思录等上游来源。
- 把不同来源的字段差异转换成统一的 `The Bus` 记录。
- 输出 `ok / empty / error` 三类抓取状态，供策略层继续处理。

## 禁止事项

- 禁止在本目录实现排序、阈值判断、推送文案拼装。
- 禁止插件之间互相引用。
- 禁止把原始上游响应直接传给策略层而不做normalizer。

## 当前插件

- `ah_premium/` — AH 股溢价数据
- `ab_premium/` — AB 股溢价数据
- `exchange_rate/` — 港币/美元人民币汇率
- `convertible_bond/` — 转债套利数据（含理论定价、小额刚兑）
- `cb_rights_issue/` — 转债抢权配售数据
- `lof_arbitrage/` — LOF/QDII 套利数据
- `merger/` — 并购重组公告
- `event_arbitrage/` — 事件驱动套利
- `subscription/` — 新股/转债申购日历
- `dividend/` — 股息公告
- `custom_monitor/` — 用户自定义监控组合

## 规格文档

各插件详细规格见 [`specs/`](../specs/spec.md)。
