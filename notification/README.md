# Notification Domain

本目录负责统一推送与调度。

## 职责

- 统一封装wecom发送能力。
- 统一管理摘要拼装、merger_report推送、推送时间调度与推送样式模板。
- 保证以后只改推送样式时，修改路径尽量收敛在 `notification/` 内。

## 边界

- 可以消费策略输出和表现层稳定视图模型。
- 不直接发起抓取，不直接编写套利规则，不直接反向修改其他职责目录。

## 推送体系

当前共有 4 条推送链路：

1. **主摘要定时推送** — 聚合所有模块生成每日摘要 Markdown
2. **可转债折价策略提醒** — 实时折价买入/卖出/监控名单推送
3. **可转债抢权配售独立推送** — 抢权配售独立定时推送
4. **LOF 套利独立推送** — LOF 套利定时+即时推送

## 目录结构

- `wecom/` — WeCom 发送客户端
  - `client.js` — 发送 Markdown 到企业微信 Webhook
- `scheduler/` — 推送调度与配置
  - `wecom_scheduler.js` — 定时推送调度（60s tick）
  - `push_config_store.js` — 运行时推送配置
  - `push_runtime_store.js` — 运行时推送状态
  - `module_push_config_store.js` — 各模块独立推送配置
  - `module_push_runtime_store.js` — 各模块独立推送状态
- `summary/` — 摘要服务
  - `main_summary.js` — 聚合所有模块生成每日摘要
- `alerts/` — 折价策略提醒
  - `event_alert_service.js` — 实时折价买入/卖出/监控名单推送
- `cb_arbitrage/` — 可转债套利推送
- `cb_rights_issue/` — 抢权配售推送
- `lof_arbitrage/` — LOF 套利推送
- `merger_report/` — 并购 deal 报告推送
- `styles/` — Markdown 格式化模板

## 规格文档

推送体系总览见 [`specs/push-system.md`](../specs/push-system.md)。
