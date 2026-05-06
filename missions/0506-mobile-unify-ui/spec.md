# Mission Spec: 手机端统一化重构

**Mission**: `0506-mobile-unify-ui`
**Type**: `implement`
**Created**: `2026-05-06`
**Status**: `completed`
**Input Source**: `user request`

## Background

- 用户要求所有设备统一显示手机端界面，废弃桌面端大表格。
- 当前 React UI 同时存在上下两套导航，且多个模块仍使用宽表格或省略字段卡片。

## Goal

- 将 React 首页与各模块统一为手机端单列密集卡片界面。
- 移除分红提醒、事件套利、推送设置的 React 导航与概览入口。
- 重构概览页为用户指定的分块摘要流。

## Deliverables

- 更新后的正式规格文档。
- React UI 与样式实现。
- 相关测试更新与新增。

## In Scope

- `ui/src/App.jsx` 结构重构与概览重写。
- `ui/src/components/` 卡片组件改造与新增。
- `ui/src/styles.css` 手机端密度样式调整。
- `tests/ui_*.test.js` 更新。
- `specs/` 与 `INDEX.md` 同步。

## Out of Scope

- 不改后端接口合同。
- 不改数据抓取与业务计算口径。
- 不处理非本轮要求的模块新增。

## Constraints

- 必须使用真实接口与真实字段。
- 先更新正式规格，再实现代码。
- 不修改 `AGENTS.md` 和已有模板。

## Impact on Formal Specs

- Changes formal requirements: `yes`
- If yes, update these files first: `specs/spec.md`, `specs/react-terminal-ui.md`, `specs/custom-monitor.md`

## Assumptions

- “配售登记”按抢权配售模块 `recordDate` 理解。
- 理论折价套利页面显示正数套利空间。
