# React 金融终端 UI 规格

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 范围

本规格定义 React + Vite 金融终端 UI 的并行重做范围、接口消费清单和验收标准。

本轮不改变业务计算口径、数据抓取规则、推送规则和现有接口含义。

## 2. 路由与托管

- 默认首页 `/` 托管 React + Vite 构建产物，静态产物目录为 `ui/dist`
- 旧 HTML 看板通过 `/legacy` 保留，继续使用原 `presentation.dashboard_entry` 指向的模板文件
- 根项目必须提供 `npm run ui:build` 与 `npm run ui:check`

## 3. 接口消费清单

React UI 必须消费以下现有真实接口：

- `GET /api/health`
- `GET /api/dashboard/ui-config`
- `GET /api/dashboard/resource-status`
- `GET /api/market/convertible-bond-arbitrage`
- `GET /api/market/ah`
- `GET /api/market/ab`
- `GET /api/market/lof-arbitrage`
- `GET /api/monitors`

不允许使用假数据、演示数据或静态占位数据冒充接口结果。

## 4. 首屏要求

React UI 首屏必须包含：
- 顶部状态栏（系统状态）
- 机会排序区
- 高密度表格区

禁止：
- 大 hero 区域
- 营销式欢迎区
- 宽松卡片布局

## 5. 机会排序

- 机会排序只能基于接口返回的真实字段生成
- 不得创建伪造综合分

## 6. 验收标准

- `ui/package.json`、`ui/src/App.jsx`、`ui/src/styles.css` 存在
- `package.json` 包含 `ui:build` 与 `ui:check`
- `start_server.js` 引用 `ui/dist` 且存在 `/legacy` 路由
- 首屏包含状态栏、Opportunity Command Center、机会排序和高密度数据表
- 前端请求现有 `/api/dashboard/*` 与 `/api/market/*`，不写假数据
- `node tests/ui_shell_contract.test.js` 与 `npm run ui:build` 通过
