# Plan: React 金融终端 UI 并行重做

## 假设

- 本轮开始页面实现，遵守 `docs/UI_DESIGN.md`。
- 新 UI 使用 React + Vite 并行落地，旧 HTML 看板保留为 `/legacy` 回滚入口。
- 不修改业务计算、数据抓取、推送逻辑和现有 `/api/*` 含义。
- 首版新 UI 优先完成金融终端外壳、机会排序首屏和核心数据表，不一次性迁移全部旧页面设置能力。

## 成功标准

1. 新增 React + Vite 前端应用。
   - 验证：`ui/package.json`、`ui/src/App.jsx`、`ui/src/styles.css` 存在。
2. 根项目提供 UI 构建与检查命令。
   - 验证：`package.json` 包含 `ui:build` 与 `ui:check`。
3. Express 默认托管新 UI，旧页面保留 `/legacy`。
   - 验证：`start_server.js` 引用 `ui/dist` 且存在 `/legacy` 路由。
4. 新 UI 首屏符合金融终端规范。
   - 验证：包含状态栏、`Opportunity Command Center`、机会排序和高密度数据表。
5. 新 UI 只消费真实接口。
   - 验证：前端请求现有 `/api/dashboard/*` 与 `/api/market/*`，不写假数据。
6. 合同测试和构建通过。
   - 验证：`node tests/ui_shell_contract.test.js` 与 `npm run ui:build` 通过。

## 步骤

1. 更新需求与规格文档。
   - 验证：文档声明 React + Vite 并行重做和 `/legacy` 回滚入口。
2. 创建 React + Vite 应用骨架。
   - 验证：可执行 `npm run ui:build`。
3. 实现终端式首屏。
   - 验证：状态栏、机会榜、数据矩阵和主表格均使用真实接口数据。
4. 接入服务端静态托管。
   - 验证：`/` 指向新 UI，`/legacy` 指向旧页面。
5. 运行检查。
   - 验证：合同测试、UI 构建和项目 smoke 检查通过或记录外部阻塞。
