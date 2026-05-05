# Mission Plan: Server Profile 配置恢复与整理

> Usage Rules:
> 1. This file defines how to execute and how to validate. Do not repeat task background here.
> 2. Keep the default length within 50 lines.
> 3. Steps must be executable and validation must be checkable.
> 4. A single file must stay under 500 lines.

**Mission**: `0505-server-profile-config` | **Date**: `2026-05-05` | **Spec**: `missions/0505-server-profile-config/spec.md`

## Summary

- 从 archive 恢复 server_profile，移动到 config/，更新所有引用路径，并配置 CLI 默认行为。

## Constitution Check

- [x] assumptions, ambiguity, and boundaries are already explicit
- [x] the plan is simple enough and avoids unnecessary expansion
- [x] the change scope is controlled and touches only necessary areas
- [x] the validation method is clear
- [x] real-data / real-file / real-result requirements are satisfied

## Execution Steps

1. 定位 SSH 配置：在 `archive/ops/server_profile.local.yaml` 找到备份
2. 恢复文件：复制到 `ops/server_profile.local.yaml`
3. 统一目录：将 `ops/server_profile.local.yaml` 移动到 `config/server_profile.local.yaml`
4. 更新引用：修改 `deploy/sync_remote_env_from_profile.py` 中 `PROFILE_PATH`
5. 更新 gitignore：`ops/server_profile.local.yaml` → `config/server_profile.local.yaml`
6. 清理空目录：删除 `ops/`
7. 配置 CLI：修改 `~/.kimi/config.toml` 开启 `default_yolo` 和 `default_caveman`

## Validation Plan

- [x] `config/server_profile.local.yaml` 存在且内容正确
- [x] `deploy/sync_remote_env_from_profile.py` 指向 `config/` 路径
- [x] `.gitignore` 正确忽略 `config/server_profile.local.yaml`
- [x] `ops/` 目录已删除
- [x] `~/.kimi/config.toml` 中 `default_yolo=true`, `default_caveman=true`

## Completion Result

- Status: `completed`
- Result Summary: 所有配置已恢复并整理完毕。server_profile 从 archive 恢复到 config/ 目录，代码引用和 gitignore 已同步更新。Kimi CLI 默认开启 yolo 和 caveman 模式。

## Risks and Follow-up

- `archive/docs/RUNBOOK.md` 仍引用旧路径 `ops/server_profile.local.yaml`，但 archive 为归档目录，不动
- `none`
