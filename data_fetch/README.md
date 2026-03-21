# Data Fetch Domain

本目录只负责“上游数据获取 + normalizer映射”。

## 职责

- 对接 AkShare、腾讯、巨潮、集思录等上游来源。
- 把不同来源的字段差异转换成统一的 `The Bus` 记录。
- 输出 `ok / empty / error` 三类抓取状态，供策略层继续处理。

## 禁止事项

- 禁止在本目录实现排序、阈值判断、推送文案拼装。
- 禁止插件之间互相引用。
- 禁止把原始上游响应直接传给策略层而不做normalizer。

## 当前插件

- `ah_premium/`
- `ab_premium/`
- `exchange_rate/`
- `convertible_bond/`
- `merger/`
- `subscription/`
- `dividend/`
- `custom_monitor/`

