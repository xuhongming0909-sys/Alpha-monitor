# 执行计划：React 还原旧网页端表格风格

## 步骤

1. 同步规格：把 React 主内容从密集行表改为旧网页端风格表格。
   - 验证：规格不再强调卡片或行壳，而是模块表格。

2. 实现公共表格组件并替换模块视图。
   - 验证：各标签主列表使用统一简洁表格。

3. 调整概览和样式，减少复杂装饰。
   - 验证：页面结构更接近旧网页端，代码构建通过。

4. 测试、提交、推送、部署。
   - 验证：线上 smoke 通过。

## 当前结果

- 已完成规格同步。
- 已新增 `SimpleDataTable.jsx` 并将主要模块改为简洁表格。
- 已将概览改回轻量列表风格。
- 已通过 `npm run ui:build`、全部 `tests/ui_*.test.js`、`npm run check:boundaries`、`node tests/root_cleanliness.test.js`、`node tests/ai_summary_coverage.test.js`。
