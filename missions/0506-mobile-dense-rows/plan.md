# 执行计划：手机端密集行表

## 步骤

1. 同步规格：把“卡片流”改为“密集行表”。
   - 验证：规格不再要求大块卡片作为主展示。

2. 修改公共展示层：`DenseCard` / `DenseCardList` 改为一标的一行的横向字段流。
   - 验证：组件输出含 `dense-row` / `dense-row-fields`，不再依赖大卡片垂直堆叠。

3. 调整样式与测试。
   - 验证：UI 测试通过，构建通过。

4. 提交、推送、服务器部署。
   - 验证：线上健康检查与 smoke 通过。

## 当前结果

- 已完成规格同步。
- 已把公共展示层改为密集行表。
- 已通过 `npm run ui:build`、全部 `tests/ui_*.test.js`、`npm run check:boundaries`、`node tests/root_cleanliness.test.js`、`node tests/ai_summary_coverage.test.js`。

## 风险

- 手机窄屏无法同时容纳所有字段，采用横向滚动保留“一标的一行”和字段完整性。
