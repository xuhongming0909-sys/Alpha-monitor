# Strategy Domain

本目录只负责“消费normalizer总线记录，并输出业务判断结果”。

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

- `ah_premium/`
- `ab_premium/`
- `convertible_bond/`
- `merger/`
- `subscription/`
- `dividend/`
- `custom_monitor/`

