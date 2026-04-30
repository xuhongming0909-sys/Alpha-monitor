# Presentation Domain

本目录负责 API 输出整形、presentation模型和前端行为拆分。

## 职责

- 承接 `/api/*` 路由控制器与响应格式化。
- 承接 dashboard 脚本、视图模型和 HTML 模板。
- 清晰表达"页面该显示什么"，而不是"业务该如何计算"。

## 边界

- 可以消费策略结果与共享模型。
- 不直接发起抓取，不直接实现策略判断，不直接决定推送渠道细节。

## 目录结构

- `routes/` — API 路由控制器
  - `market_routes.js` — 市场行情路由（`/api/market/*`）
  - `dashboard_routes.js` — 看板路由（`/api/dashboard/*`、`/api/monitors`、`/api/dividend`）
  - `push_routes.js` — 推送配置路由（`/api/push/*`）
- `view_models/` — 数据整形与响应格式
  - `overview.js` — 看板概览数据组装
  - `push_payload.js` — 推送配置响应格式
- `dashboard/` — 旧看板页面逻辑
  - `dashboard_page.js` — legacy 页面渲染
- `templates/` — HTML 模板
  - `dashboard_template.html` — 旧看板模板（暗色金融终端主题）

## React 新 UI

React + Vite 前端在同级 `ui/` 目录：
- `ui/src/App.jsx` — React 应用主组件
- `ui/src/styles.css` — 样式
- 构建产物输出到 `ui/dist/`
- 旧看板保留 `/legacy` 回滚入口

## 规格文档

详细 API 合同见 [`specs/api-contract.md`](../specs/api-contract.md)，UI 规范见 [`specs/ui-design.md`](../specs/ui-design.md)。
