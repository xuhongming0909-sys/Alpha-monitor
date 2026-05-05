# Mission Spec: Server Profile 配置恢复与整理

> Usage Rules:
> 1. This file defines task boundaries only. Do not put detailed steps here.
> 2. Keep the default length within 60 lines.
> 3. Do not repeat content that belongs in `plan.md`.
> 4. A single file must stay under 500 lines.

**Mission**: `0505-server-profile-config`
**Type**: `implement`
**Created**: `2026-05-05`
**Status**: `completed`
**Input Source**: `user request`

## Background

- 用户询问 SSH 服务器密码信息存储位置
- 发现 `ops/server_profile.local.yaml` 在 `.gitignore` 中，但项目根目录不存在
- 备份存在于 `archive/ops/server_profile.local.yaml`

## Goal

- 恢复 server_profile.local.yaml 到可用位置
- 统一服务器配置入口到 `config/` 目录
- 配置 Kimi CLI 默认行为（yolo + caveman）

## Deliverables

- `config/server_profile.local.yaml`（从 archive 恢复并移动）
- 更新 `deploy/sync_remote_env_from_profile.py` 路径引用
- 更新 `.gitignore`
- 更新 `~/.kimi/config.toml`

## In Scope

- 恢复 server_profile 文件
- 移动 ops/ → config/
- 更新代码中的硬编码路径
- 更新 .gitignore
- 修改 Kimi CLI 全局配置

## Out of Scope

- 修改 server_profile 内容（密码、IP 等保持原样）
- 部署或同步远程 .env
- 修改正式 spec 文档

## Constraints

- `config/secrets.yaml` 已存在，server_profile 也放 config/ 下
- `CLAUDE.md` 禁止修改，不能动

## Impact on Formal Specs

- Changes formal requirements: `no`
- This is a config/tooling housekeeping task, no spec changes needed.

## Assumptions

- `archive/ops/server_profile.local.yaml` 是最新可用备份
