# Mission Plan: 部署最新版本

**Mission**: `0506-deploy-latest` | **Date**: `2026-05-06` | **Spec**: `missions/0506-deploy-latest/spec.md`

## Summary

- 先同步 git，再在服务器拉取、构建前端并重启服务，最后用真实公网接口验证。

## Constitution Check

- [x] assumptions, ambiguity, and boundaries are already explicit
- [x] the plan is simple enough and avoids unnecessary expansion
- [x] the change scope is controlled and touches only necessary areas
- [x] the validation method is clear
- [x] real-data / real-file / real-result requirements are satisfied, or the limitation is already stated

## Execution Steps

1. 检查本地 git 状态与远端配置。
2. 必要时提交并推送本地待同步文件。
3. SSH 到服务器执行 `git pull`、`cd ui && npm run build`、重启 `alpha-monitor`。
4. 验证公网 `/api/health` 和服务器服务状态。

## Validation Plan

- [ ] `git status --short --branch` 显示本地与远端同步。
- [ ] 服务器 `npm run build` 成功。
- [ ] `systemctl is-active alpha-monitor` 返回 `active`。
- [ ] 公网 `/api/health` 返回可用结果。

## Completion Result

- Status: `completed`
- Result Summary: 服务器已拉取最新代码，`ui` 已构建，`alpha-monitor` 已重启，公网 `/api/health` 正常。

## Risks and Follow-up

- 服务器工作树仍有未跟踪的 `tools/` 文件，导致不能直接切换分支。
- 现在 `workflow-elodie` 已设置跟踪 `origin/main`，后续 `git pull` 会对齐主线。
