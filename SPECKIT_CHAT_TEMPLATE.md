# Alpha Monitor 简化工作流模板

按本项目的更简化流程继续，不要跳步骤。

## 每次任务开始前必须先读

- `CONSTITUTION.md`

## 固定流程

### 1. 先形成 plan

- 每次有项目变更需求，先输出或更新 `refactor_docs/001-monitor-refactor/plan.md`
- 我会直接调用 Codex 的 Plan mode 来看方案
- 在我确认 `plan.md` 前，不要直接改代码

### 2. 实施前再检查 REQUIREMENTS 和 SPEC

如果本轮 `plan.md` 会影响以下任一内容，就必须在改代码前先更新文档：

- 需求范围
- 页面行为
- 计算逻辑
- 接口含义
- 配置项
- 部署方式

更新顺序固定为：

1. `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
2. `refactor_docs/001-monitor-refactor/SPEC.md`

### 3. 我确认后再实施

- 我确认 `plan.md` 后，再开始代码修改
- 修改完成后，做最小验证并汇报结果

## 回复格式

每次先告诉我：

1. 你已读取 `CONSTITUTION.md`
2. 这次是否需要先输出或更新 `plan.md`
3. 这次是否需要在实施前更新 `REQUIREMENTS.md` 和 `SPEC.md`
4. 当前是否已经进入实施阶段
