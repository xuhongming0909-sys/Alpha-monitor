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
6. Convert single-shot health probe into retry-based readiness check with explicit retry logs.

Acceptance:
- Deployment fails instead of silently serving stale homepage content.
- Successful deployment guarantees local homepage contract consistency with dashboard entry.

## 10. Phase G: Compact UX + Push Reliability + Monitor Recoverability (2026-03-22)

Goal: complete one-shot refactor for three production pain points:
1. Compact list presentation on desktop without module-internal horizontal/vertical scrolling.
2. Push config read/write reliability and effective scheduled delivery.
3. Monitor arbitrage recoverability in cloud deploy (Python runtime + dependencies).

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` contracts first.
2. Refactor dashboard tables to "key columns + inline detail expansion + strong pagination".
3. Remove module-internal max-height scrolling and tighten spacing.
4. Harden API client JSON parsing and add uniform `/api/*` JSON 404 fallback.
5. Make push scheduler calendar mode explicit and set to daily execution.
6. Add deploy-stage Python dependency install and import verification.

Acceptance:
- Desktop 1920x1080 can read key list information without module-internal scrolling.
- `GET/POST /api/push/config` is stable, parseable, and UI state remains consistent after save + reload.
- Scheduler can execute on all weekdays and weekends when times match.
- `GET /api/monitors` no longer fails with `python not found` / `No module named akshare`.
- GitHub Actions deploy remains the single sync path to cloud server and finishes with health + marker checks.

## 11. Phase H: Subscription Date Simplification + Monitor UI Recovery + Global 50-row Pagination (2026-03-23)

Goal: finish one-shot correction for three current production regressions:
1. In the subscription table, remove the standalone `抽签日` column and reuse `lotteryDate` as the displayed value for `中签缴款日`.
2. Restore `监控套利` to a stable, readable panel with the same table/pagination interaction as other modules.
3. Unify dashboard module tables to `50` rows per page instead of mixed `20` / unpaginated behavior.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first so page behavior and field semantics are explicit before coding.
2. Adjust the top subscription table contract:
   - keep today-stage judgment unchanged
   - remove the visible `抽签日` header
   - `中签缴款日` column displays `lotteryDate`
3. Refactor monitor rendering to use the shared paginated table path, not a special simple table path.
4. Extend the shared table state so `监控套利` / `分红提醒` / `收购私有` also paginate at `50` rows per page.
5. Keep existing formulas unchanged and verify monitor calculations still match `SPEC.md`.
6. After implementation, run local checks, then push to GitHub and trigger the cloud-server auto-deploy path.

Acceptance:
- The subscription table no longer shows a `抽签日` column.
- The visible `中签缴款日` column uses `lotteryDate` values consistently for IPO and bond rows.
- `监控套利` renders successfully when `/api/monitors` returns data and supports 50-row pagination.
- `转债套利` / `AH溢价` / `AB溢价` / `监控套利` / `分红提醒` / `收购私有` all use 50-row pagination.
- GitHub main branch and cloud deployment are updated to the latest implementation, and the latest webpage can be opened for verification.

## 11A. Phase H-2: Subscription Stage Alignment + Monitor Inline Editing (2026-03-23)

Goal: finish the remaining dashboard corrections from the latest user review:
1. `股债打新` must stop labeling bond rows as `今日中签缴款` on 2026-03-23 when the visible date column already shows 2026-03-20.
2. `监控套利` must support adding new monitor items and editing existing monitor parameters from the dashboard.
3. `监控套利` supplemental fields must render inline below each item, without a separate `详情` control column, and the wording must match real business terms.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first.
2. Align the subscription stage decision with the visible date contract:
   - the visible `中签缴款日` keeps using `lotteryDate`
   - the `今日中签缴款` stage judgment also switches to `lotteryDate`
3. Refactor the monitor panel into:
   - top editor area for create / edit
   - paginated monitor list
   - fixed inline parameter block under each item
4. Keep the existing `/api/monitors` contract and reuse `POST /api/monitors` for both create and update by carrying `id`.
5. Replace inaccurate monitor detail labels such as `股票腿公式` with wording that directly describes pricing inputs and calculation text.

Acceptance:
- On 2026-03-23, rows whose `lotteryDate` is not 2026-03-23 no longer appear as `今日中签缴款`.
- Dashboard users can create a new monitor item and edit an existing one without leaving the page.
- `监控套利` no longer shows a separate `详情` header/button path; supplemental fields are shown directly below each item.
- Monitor inline wording matches the actual fields returned by the custom monitor strategy.

## 12. Phase I: Fresh Quotes + Dense Core Tables + Push Delivery Truthfulness (2026-03-23)

Goal: finish the current production correction for four user-visible issues in one round:
1. Dashboard manual refresh and first-screen critical market modules must converge to the latest available quotes in the same session instead of staying on stale cache snapshots.
2. `杞€哄鍒? / AH婧环 / AB婧环` main tables must become denser and remove the visible `璇︽儏` header/button path as the primary reading mode.
3. Convertible bond main table must surface the key parameters behind `鐞嗚婧环鐜?` directly in the default row, including `杞€烘定璺屽箙` / `姝ｈ偂娑ㄨ穼骞?` / `60鏃ユ尝鍔ㄧ巼` / `绾€哄€?` / `鐞嗚浠?` / `鍒版湡绋庡墠鏀剁泭鐜?`.
4. Push delivery state must stop lying: failed sends cannot be recorded as sent, and the UI/API must expose webhook readiness, scheduler mode, selected modules, and last success/failure details.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new cache-refresh, dense-table, and push-delivery contracts.
2. Keep the existing cache layer for fast first paint, but:
   - `鎵嬪姩鍒锋柊` must call force refresh for market datasets
   - if first dashboard load receives `servedFromCache` for critical quote modules, trigger one background force revalidation in the same session
   - UI copy must tell the user when a module is still showing cached data
3. Refactor `杞€哄鍒?` main table to remove the explicit detail column and move key metrics into main-row composite cells.
4. Refactor `AH / AB` main tables to follow the same dense-table principle and inline sample metadata instead of using the current detail-expansion path.
5. Harden push runtime recording:
   - record attempt time, success time, and latest error separately
   - only mark a schedule slot as sent after the downstream WeCom send succeeds
   - keep failed slots retryable on later scheduler ticks
6. Extend `GET /api/push/config` response and dashboard push status text so the user can see:
   - selected push modules
   - scheduler mode
   - webhook configured or missing
   - last main push / merger push success time
   - latest push failure reason when present
7. After implementation, run local verification, push to GitHub `main`, let GitHub Actions trigger the cloud deploy path, and open the latest webpage for final visual confirmation.

Acceptance:
- Clicking dashboard `鍒锋柊` fetches fresh market data instead of only replaying stale cache.
- If the initial dashboard render used cache for `exchangeRate / cbArb / ah / ab`, the page performs one background real-time revalidation and updates the visible values in the same visit.
- `娴峰優杞€? 118008` on the refreshed page matches the latest backend snapshot instead of the previously stale `+3.61%` view.
- `杞€哄鍒?` main table shows key pricing / volatility / yield fields without a visible `璇︽儏` column.
- `AH / AB` main tables use the same dense default-row pattern and no longer depend on the old detail-label path.
- Push scheduler no longer records failed sends as completed.
- `GET /api/push/config` and the dashboard push strip clearly reveal whether push is blocked by missing webhook configuration or by the last runtime failure.
- GitHub `main`, cloud deployment, and the latest public webpage are all updated to the new implementation.

## 13. Phase J: Premium History Sync Tolerance For Provider Outliers (2026-03-23)

Goal: recover `data_jobs` health without taking down the live dashboard when a small number of upstream historical-price requests fail for individual symbols.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first with the operational tolerance rule for premium-history incremental sync.
2. Keep full rebuild mode strict, but change update mode so a single-symbol upstream provider anomaly does not fail the whole batch when the local cache can continue serving the dashboard.
3. Restrict this tolerance to known fetch-layer per-symbol provider failures, and keep the failures visible in script output as warnings.
4. Avoid restarting the Node web service for this fix; let the next scheduler tick pick up the new script automatically.

Acceptance:
- `python tools/rebuild_premium_db.py --mode update` can return success while exposing warning details for a small number of provider-outlier symbols.
- `/api/health` can recover from `data_jobs = warn` to healthy on the next scheduler cycle when only non-fatal provider-outlier errors remain.
- The homepage remains reachable throughout the repair and verification process.
## 14. Phase K: Cloud Runtime Preservation + First-Install Proxy Closure (2026-03-23)

Goal: make the cloud deploy path safe for long-term unattended operation by preserving runtime state and reducing first-install proxy drift.

Plan:
1. Remove runtime JSON state files from release-source expectations and document them as server-local state.
2. Keep deploy-script preservation in front of `git reset --hard` so automatic updates do not wipe monitor lists, push config, or runtime caches.
3. Strengthen the `systemd` service template with explicit working directory and `.env` loading.
4. Provide both nginx and Caddy installation scripts so first public rollout does not depend on manual copy-paste edits.

Acceptance:
- Automatic deployment no longer overwrites server-local `runtime_data/shared/*.json`.
- A fresh Ubuntu server can install either nginx or Caddy with a single repo script and expose the same homepage and `/api/health`.
- The managed service keeps loading from the project root after reboot and picks up `.env` overrides consistently.
