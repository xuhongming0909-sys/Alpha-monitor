# Mission Plan: 手机端统一化重构

**Mission**: `0506-mobile-unify-ui` | **Date**: `2026-05-06` | **Spec**: `missions/0506-mobile-unify-ui/spec.md`

## Summary

- 先同步规格，再拆分 React UI 为统一手机端导航、概览摘要流和全字段密集卡片，最后补测试并部署。

## Constitution Check

- [x] assumptions, ambiguity, and boundaries are already explicit
- [x] the plan is simple enough and avoids unnecessary expansion
- [x] the change scope is controlled and touches only necessary areas
- [x] the validation method is clear
- [x] real-data / real-file / real-result requirements are satisfied, or the limitation is already stated

## Execution Steps

1. 更新 `specs/` 和 `INDEX.md`，固定新的 React UI 边界与概览结构。
2. 重构 `App.jsx`、导航与概览数据组装，移除分红/事件/推送标签。
3. 改造与新增卡片组件，统一为单列密集全字段展示。
4. 调整样式与测试，验证构建和 UI 测试。
5. 更新 mission、MEMORY，提交并部署服务器。

## Validation Plan

- [x] `npm run ui:build` 通过。
- [x] 相关 `tests/ui_*.test.js` 通过。
- [x] 线上服务重启后 `/api/health` 正常。

## Completion Result

- Status: `completed`
- Result Summary: 已完成 React 手机端统一化、概览重构、全字段卡片化、规格/索引/测试同步，并部署到服务器。

## Risks and Follow-up

- `npm run check` 默认打本机服务；本项目不本地跑网页，改用 `ALPHA_MONITOR_BASE_URL=http://43.139.35.190 node tests/smoke_check.js` 验证线上。
- `tests/convertible_discount.test.js` 存在历史失败，和本轮 UI 改造无关。
