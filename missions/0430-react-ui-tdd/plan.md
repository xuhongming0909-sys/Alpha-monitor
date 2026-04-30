# Plan: React UI TDD 改进

## 验证方式
- 每个 slice 先写测试（RED），再写代码（GREEN），最后重构
- 使用现有 `tests/ui_shell_contract.test.js` 作为基线
- 每阶段完成后运行测试验证

## Slice 清单

### Phase 1: 基础上线准备 ✅
1.1 根 `package.json` 添加 `ui:build` / `ui:check` ✅
1.2 `start_server.js` 添加 `/legacy` 路由（返回旧版 dashboard）✅
1.3 `start_server.js` 添加 `ui/dist` 静态服务 ✅
1.4 调整默认首页逻辑：优先 serve React，fallback 旧版 ✅
→ 验证：`node tests/ui_shell_contract.test.js` 通过 ✅

### Phase 2: 模块 Tab 导航 + 详细表格 ✅
2.1 添加 `TabNav` 组件（转债、AH溢价、AB溢价、LOF套利、打新、监控、分红）✅
2.2 扩展 `API_ENDPOINTS` 添加 subscriptions、dividend ✅
2.3 扩展 `useDashboardData` fetch 新接口 ✅
2.4 各 Tab 内容区展示对应 API 详细表格：
    - ConvertibleTable（概览+转债tab）✅
    - AhTable ✅
    - AbTable ✅
    - LofTable ✅
    - SubscriptionTable ✅
    - MonitorTable（含股票腿/现金腿收益率+最优收益率）✅
    - DividendTable ✅
→ 验证：`node tests/ui_module_navigation.test.js` 通过 ✅

### Phase 3: 搜索与排序 ✅
3.1 全局搜索框（按代码/名称过滤当前 Tab 数据）✅
3.2 各表格组件内部实现搜索过滤 ✅
3.3 点击表头排序（升序/降序切换，SortableTh + useSort hook）✅
→ 验证：`node tests/ui_search_filter.test.js` 通过 ✅

### Phase 4: 自定义监控列表 ✅
已包含在 Phase 2 中完成。MonitorTable 展示：
- 监控名称、收购方→目标方、目标现价
- 股票腿收益率、现金腿收益率、最优收益率
- 备注

### Phase 5: 推送设置 ✅
5.1 添加推送设置入口（页面底部，所有 Tab 共用）✅
5.2 消费 `/api/push/config` 接口 ✅
5.3 展示推送时间、模块开关、Webhook 状态、调度器状态、上次推送时间 ✅
→ 验证：`node tests/ui_push_settings.test.js` 通过 ✅

## 最终状态
- Build：`npm run ui:build` 通过 ✅
- 全部测试：4/4 通过 ✅
- 旧版 Dashboard：通过 `/legacy` 完整保留 ✅
- `ui/dist` 已生成，默认首页优先 React，fallback 旧版 ✅
- 模块覆盖：8 个 Tab（概览、转债、AH、AB、LOF、打新、监控、分红）+ 推送设置 ✅
- 交互：全局搜索 + 点击表头排序 ✅

## 当前状态
- Build：`npm run ui:build` 通过 ✅
- 全部测试：3/3 通过 ✅
- 旧版 Dashboard：通过 `/legacy` 完整保留 ✅
- `ui/dist` 已生成，默认首页优先 React，fallback 旧版

## 风险
- 旧版 Dashboard 被意外破坏 → 有 `/legacy` 路由作为安全网 ✅
- 构建失败 → Phase 1 已解决 ✅
- 模块数据字段不一致 → 复用现有工具函数 + pickText 安全取值 ✅
