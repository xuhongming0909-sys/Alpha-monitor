# Alpha Monitor 云服务器 GitHub 自动部署计划

**Date**: `2026-03-22`
**Feature**: `001-monitor-refactor`
**Related Docs**:
- [REQUIREMENTS.md](C:/Users/93724/Desktop/Alpha%20monitor/refactor_docs/001-monitor-refactor/REQUIREMENTS.md)
- [SPEC.md](C:/Users/93724/Desktop/Alpha%20monitor/refactor_docs/001-monitor-refactor/SPEC.md)

## 1. 本次目标

本次施工只解决一件事：把“云服务器已经连上 GitHub，但每次推送后还要手动更新”收口成正式自动部署链路。

完成后目标状态为：

1. 仓库内存在正式的 GitHub Actions 自动部署工作流。
2. 服务器端存在统一的拉取更新脚本。
3. 当 `main` 分支收到新提交时，GitHub 可以自动通过 SSH 登录服务器并执行更新。
4. 更新流程默认完成：
   - 拉取最新代码
   - 同步 Node 依赖
   - 检查 `alpha-monitor` 服务是否存在
   - 若服务存在则自动重启
   - 输出健康检查结果
5. 自动部署失败时，日志能明确定位是 SSH、代码同步、依赖安装、服务重启还是健康检查失败。

## 2. 本次不改的内容

本次不主动修改以下内容：

- 仪表盘 UI 布局
- AH / AB / 可转债 / 监控套利业务公式
- `/api/*` 对外路由
- 云服务器首次基础环境安装方式
- Nginx / Caddy 现有反向代理方案

如果实施中发现必须改这些内容，会先回到文档阶段重新确认。

## 3. 现状判断

当前已确认的事实：

1. 云服务器目录已连接 GitHub 仓库，主目录为 `/home/ubuntu/Alpha monitor`。
2. 仓库内已经有 Linux 启动、`systemd`、Nginx/Caddy 辅助脚本。
3. 仓库中已经存在 `.github/workflows/deploy.yml`，但当前实现仍包含部分服务器侧同步逻辑，和“工作流只负责触发、服务器脚本负责执行”的目标有偏差。
4. 服务器上是否已经安装 `alpha-monitor.service` 仍可能因机器状态不同而不一致，因此自动部署脚本必须兼容“服务已安装”和“服务未安装”两种情况。

## 4. 实施假设

本次计划采用以下默认假设：

1. 正式自动部署目标分支为 `main`。
2. GitHub Actions 使用 SSH 私钥登录服务器，不直接暴露服务器密码。
3. 服务器上的项目目录固定为 `/home/ubuntu/Alpha monitor`，但工作流允许通过变量覆盖。
4. 若服务器已经安装 `alpha-monitor` 服务，则自动部署后重启该服务；若未安装，则只同步代码并输出提醒，不在工作流里强行创建服务。
5. 自动部署优先使用 `npm ci`；若锁文件不可用再退回 `npm install`。

## 5. 施工步骤

### Phase A: 文档合同更新

目标：先把 GitHub 自动部署写进需求与技术合同。

计划修改：

- `refactor_docs/001-monitor-refactor/plan.md`
- `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
- `refactor_docs/001-monitor-refactor/SPEC.md`
- `RUNBOOK.md`

要补齐的内容：

1. 云服务器必须支持“推送到 GitHub 后自动更新”。
2. 自动部署只认 `main` 分支。
3. 自动部署链路固定为“GitHub Actions -> SSH -> 服务器更新脚本 -> 服务重启 -> 健康检查”。
4. 需要的 GitHub Secrets 名称、服务器目录和服务名要写清楚。

完成标准：

- 文档能独立说明自动部署要求、边界和验收。

### Phase B: 服务器更新脚本落地

目标：提供一个服务器侧统一入口，让 GitHub Actions 和人工排障都调用同一套逻辑。

计划新增：

- `tools/deploy/update_from_github.sh`

脚本职责：

1. 切到项目根目录。
2. 执行 `git fetch --all` 和 `git reset --hard origin/main`。
3. 根据锁文件决定运行 `npm ci` 或 `npm install`。
4. 如果存在 `alpha-monitor` 服务，则执行重启并输出状态。
5. 调用本地健康检查接口，失败时返回非零退出码。

完成标准：

- 在服务器本机手动执行该脚本，可以完成一次完整更新。

### Phase C: GitHub Actions 工作流落地

目标：让 `main` 分支提交自动触发远程部署。

计划新增：

- `.github/workflows/deploy.yml`

工作流职责：

1. 监听 `main` 分支 push。
2. 通过 GitHub Secrets 读取 SSH 连接参数。
3. 在 runner 上准备 SSH 环境。
4. 远程执行服务器更新脚本。
5. 在日志中清晰打印部署目标主机、目录、分支和完成状态。

完成标准：

- 工作流文件在仓库内完整可用。

### Phase D: 运行说明补齐

目标：把“怎么启用自动部署”和“出了问题看哪里”写成最小可执行说明。

计划修改：

- `RUNBOOK.md`

要补齐的内容：

1. GitHub Secrets 列表
2. 首次服务器准备步骤
3. 手动补救命令
4. 自动部署失败后的排障顺序

完成标准：

- 用户只看文档也能完成剩余少量手工配置。


### Phase E: 工作流职责收口与一致性修正

目标：把 GitHub Actions 职责收口为“准备 SSH + 触发服务器统一更新脚本”，避免与脚本逻辑重复。

计划修改：

- `.github/workflows/deploy.yml`

要修正的内容：

1. 去除工作流中的 `git fetch/reset`、服务重启等服务器业务逻辑。
2. 远程只执行 `tools/deploy/update_from_github.sh`，并通过环境变量传入目录、服务名和分支。
3. 日志中明确打印部署阶段，便于区分 SSH 连接失败与脚本内部失败。

完成标准：

- 工作流实现与 `REQUIREMENTS.md`、`SPEC.md` 的自动部署合同完全一致。

## 6. 风险与处理

### 风险 1：服务器没有安装正式服务

处理方式：

- 自动部署脚本不直接报死，而是明确提示“代码已更新，但未检测到 `alpha-monitor` 服务”。
- 继续保留已有 `install_systemd.sh` 作为首次安装入口。

### 风险 2：GitHub Secrets 没配好导致连接失败

处理方式：

- 工作流中统一使用固定变量名。
- 文档明确要求最少只配 4 项：`SERVER_HOST`、`SERVER_USER`、`SERVER_PORT`、`SERVER_SSH_KEY`。

### 风险 3：服务器目录带空格导致 SSH 命令失败

处理方式：

- 所有远程命令都对目录路径加双引号。
- 服务器脚本内部自行定位项目根目录，避免外部命令重复拼接复杂路径。

## 7. 交付结果

本次实施完成后，交付内容包括：

1. 更新后的自动部署文档合同
2. 服务器端统一更新脚本
3. GitHub Actions 自动部署工作流
4. 最小启用说明与排障说明

## 8. 当前状态

- 已读取：`CONSTITUTION.md`
- 本次是否需要先更新 `REQUIREMENTS.md` 和 `SPEC.md`：`是`
- 本次是否需要先输出或更新 `plan.md`：`是，已完成`
- 当前是否已经进入实施阶段：`是，文档更新后进入代码实施`


## 9. Phase F: One-shot Recovery Hardening (2026-03-22)

Goal: eliminate the recurring "service is running but homepage is old" deployment drift.

Planned script hardening in `tools/deploy/update_from_github.sh`:
1. Validate `config.yaml` syntax before install/restart.
2. Resolve `app.port` and force-release stale process owners on that port before service restart.
3. Keep systemd unit refresh as the single source of service startup path.
4. After health check, verify homepage markers:
   - expected marker exists: `dashboard_page.js`
   - forbidden legacy markers absent: `app.js|message-form`
5. Fail fast with clear deploy-stage logs when marker verification fails.

Acceptance:
- Deployment fails instead of silently serving stale homepage content.
- Successful deployment guarantees local homepage contract consistency with dashboard entry.
