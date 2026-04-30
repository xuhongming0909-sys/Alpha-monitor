# Plan: React UI TDD 改进

## 验证方式
- 每个 slice 先写测试（RED），再写代码（GREEN），最后重构
- 使用现有 `tests/ui_shell_contract.test.js` 作为基线
- 每阶段完成后运行测试验证

## Slice 清单

### Phase 1: 基础上线准备
1.1 根 `package.json` 添加 `ui:build` / `ui:check`
1.2 `start_server.js` 添加 `/legacy` 路由（返回旧版 dashboard）
1.3 `start_server.js` 添加 `ui/dist` 静态服务
1.4 调整默认首页逻辑：优先 serve React，fallback 旧版
→ 验证：`node tests/ui_shell_contract.test.js` 通过

### Phase 2: 模块 Tab 导航
2.1 添加 `TabNav` 组件（转债套利、AH溢价、AB溢价、LOF套利、打新、分红、收购、合并、事件、自定义监控）
2.2 各 Tab 内容区展示对应 API 详细表格
→ 验证：切换 Tab 能看到对应数据，表格列完整

### Phase 3: 搜索与排序
3.1 全局搜索框（按代码/名称过滤当前 Tab 数据）
3.2 点击表头排序
→ 验证：搜索和排序行为正确

### Phase 4: 自定义监控列表
4.1 添加自定义监控详细表格（代码、名称、市场、价格、条件、当前值、安全垫）
→ 验证：列表展示完整字段

### Phase 5: 推送设置
5.1 添加推送设置入口（次级，不占首屏，如放在页面底部或设置面板）
→ 验证：能查看和修改推送配置

## 风险
- 旧版 Dashboard 被意外破坏 → 有 `/legacy` 路由作为安全网
- 构建失败 → Phase 1 先解决 build 问题
- 模块数据字段不一致 → 复用现有 `toArray`/`formatNumber`/`formatPercent` 工具
