# Mission Spec: 部署最新版本

**Mission**: `0506-deploy-latest`
**Type**: `implement`
**Created**: `2026-05-06`
**Status**: `completed`
**Input Source**: `user request`

## Background

- 用户要求先部署，确保线上能看到最新 Alpha Monitor 页面。

## Goal

- 将当前 `main` 最新代码同步到服务器并完成前端构建、服务重启。
- 验证公网服务可访问。

## Deliverables

- 服务器部署完成。
- 记录部署命令、验证结果和剩余风险。

## In Scope

- 检查本地 git 状态。
- 必要时提交并推送本地待同步文件。
- 在服务器执行 `git pull`、`npm run build`、`systemctl restart alpha-monitor`。
- 验证 `/api/health`。

## Out of Scope

- 不修改业务功能。
- 不本地启动网页。
- 不卡片化剩余表格模块。

## Constraints

- 遵守服务器优先规则。
- 不修改 `AGENTS.md` 和已有模板。
- 不伪造部署结果。

## Impact on Formal Specs

- Changes formal requirements: `no`
- If no, explain why: 本任务只部署现有实现，不改变长期需求。

## Assumptions

- 当前远端 `origin/main` 是服务器可拉取的目标分支。
- 服务器路径为 `/home/ubuntu/Alpha monitor`，服务名为 `alpha-monitor`。
