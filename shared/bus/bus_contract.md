# The Bus v1

`The Bus` 是 `data_fetch/` 与 `strategy/` 之间唯一允许的normalizer数据传输格式。

## 设计目标

- 让不同市场、不同source的抓取结果先做归一化，再进入策略层。
- 当未来更换source时，只需要修改对应抓取插件与normalizer映射，不需要修改策略插件。
- 让策略层只关心“业务字段”，不关心上游接口字段名、编码差异或网页结构差异。

## 标准记录字段

每一条标准记录都必须是一个对象，并至少包含以下字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `plugin` | `string` | 产生该记录的抓取插件标识，例如 `ah_premium` |
| `market` | `string` | 市场标识，例如 `A`、`B`、`H`、`CB`、`FX` |
| `symbol` | `string` | 标的代码 |
| `name` | `string` | 标的名称 |
| `event_type` | `string` | 记录类别，例如 `quote`、`dividend_record`、`subscription_event` |
| `quote_time` | `string` | ISO 8601 时间字符串，表示本条记录对应的时间 |
| `metrics` | `object` | 已归一化的核心指标集合 |
| `raw` | `object` | 原始快照，保留上游字段，便于审计与排错 |
| `status` | `string` | `ok`、`empty`、`error` 之一 |

## 推荐可选字段

- `currency`: 价格或金额所对应的货币
- `source`: 上游来源，例如 `akshare`、`tencent`、`cninfo`
- `date`: 业务日期，例如登记日、申购日、公告日
- `tags`: 业务标签数组，便于下游筛选
- `message`: 对空结果或错误结果的说明
- `extra`: 不适合放进 `metrics` 的扩展信息

## 状态语义

- `ok`: 正常抓取并成功完成normalizer。
- `empty`: 上游访问成功，但当天没有对应事件或没有有效数据。
- `error`: 抓取或normalizer失败，必须在 `message` 中给出可读说明。

## 统一约束

- 抓取插件必须先输出 `The Bus` 记录，策略插件禁止直接消费抓取插件的原始响应。
- 同一插件不同source抓下来的记录，也必须对齐成同一个 `metrics` 口径。
- `raw` 用于审计和排错，不能被策略层当作主业务字段依赖。
- `quote_time` 必须使用上海时区语义下可解释的时间值。

