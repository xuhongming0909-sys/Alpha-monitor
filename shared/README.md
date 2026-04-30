# Shared Layer

本目录承载跨领域复用的基础能力，只允许放置"不会直接表达某个具体业务策略"的内容。

## 职责

- `config/` — 统一配置读取与解析
- `runtime/` — 运行态 JSON 状态读写与分类
- `paths/` — 路径、profile、历史库与运行态文件定位
- `time/` — 上海时区、交易时段、日期归一化等时间能力
- `logging/` — 统一日志输出
- `models/` — 通用返回模型与公共数据结构
- `bus/` — 抓取层到策略层之间的normalizer总线契约

## 边界

- 这里禁止落入某个具体业务插件的专用逻辑。
- `shared/` 可以被 `data_fetch/`、`strategy/`、`ui/`、`notification/` 依赖。
- 一旦某段代码开始感知"AH 溢价""convertible_bond""merger"等业务语义，它就不应继续留在 `shared/`。

## 规格文档

跨层契约见 [`specs/api-contract.md`](../specs/api-contract.md)，数据模型见 [`specs/data-model.md`](../specs/data-model.md)。
