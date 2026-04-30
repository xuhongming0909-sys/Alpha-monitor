# presentation

## 职责

presentation 层负责 API 塑形、Dashboard 渲染和前端路由。它消费 strategy/ 层产出的标准化数据，不直接触碰数据抓取逻辑。

## 目录结构

```
presentation/
  dashboard/           # 旧版 HTML 看板（/legacy 路由）
  routes/              # Express API 路由
  templates/           # HTML 模板
  view_models/         # 视图模型（数据塑形）
```

## API 路由

- `GET /api/health` — 系统健康状态
- `GET /api/dashboard/ui-config` — UI 配置
- `GET /api/dashboard/resource-status` — 资源状态
- `GET /api/market/*` — 各策略市场数据
- `GET /api/monitors` — 自定义监控
- `GET /api/dividend` — 分红数据
- `GET /api/push/config` — 推送配置

## React UI

新版终端式 UI（`/` 路由）：
- 10 个顶级 Tab：概览、转债、AH溢价、AB溢价、LOF套利、打新/申购、自定义监控、分红提醒、事件套利、推送设置
- 概览页：打新置顶 + 策略混排 + 转债表格
- 数据来源：全部真实接口，无假数据

旧版看板（`/legacy` 路由）保留向后兼容。

## 技术栈

- React + Vite
- Express 静态服务
- 深色终端主题

## 相关 Spec

- `specs/react-terminal-ui.md` — React UI 规格
- `specs/api-contract.md` — API 契约
