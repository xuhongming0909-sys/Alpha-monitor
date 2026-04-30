# Strategy Domain

本目录只负责"消费normalizer总线记录，并输出业务判断结果"。

## 职责

- 根据 `config.yaml` 和 `The Bus` 记录执行业务规则。
- 输出溢价排行、事件筛选、并购分析范围、subscription提醒、dividend提醒、custom_monitor结果等。
- 保持策略对抓取实现无感知，只依赖统一字段语义。

## 禁止事项

- 禁止直接请求上游接口。
- 禁止直接读取兄弟抓取插件的内部实现。
- 禁止策略插件之间互相引用。
- 禁止在策略层拼接wecom文案或页面 DOM。

## 当前插件

- `ah_premium/` — AH 溢价排名、历史百分位
- `ab_premium/` — AB 溢价排名
- `convertible_bond/` — 双低策略、理论收益率、回售套利、折价策略（买入/卖出/监控）
- `cb_rights_issue/` — 抢权配售预期收益计算、阶段判定、入池判断
- `lof_arbitrage/` — LOF/QDII 溢价率排名
- `merger/` — 并购重组 deal 分析、AI 报告生成
- `event_arbitrage/` — 事件匹配与过滤
- `subscription/` — 申购事件跟踪
- `dividend/` — 股权登记日跟踪、收益率计算
- `custom_monitor/` — 自定义组合收益率计算

## 规格文档

各插件详细规格见 [`specs/`](../specs/spec.md)。
