# Alpha Monitor 云服务器 GitHub 自动部署计划

**Date**: `2026-03-22`
**Feature**: `001-monitor-refactor`
**Related Docs**:
- [REQUIREMENTS.md](./REQUIREMENTS.md)
- [SPEC.md](./SPEC.md)

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

## 27. Phase X: Dashboard Render Recovery For Template/Script Drift (2026-03-24)

Goal: recover the public dashboard from a full-page render crash caused by template/script tab mismatch.

Plan:
1. Keep the current dashboard information architecture unchanged; this round is a runtime recovery fix, not a product-contract change.
2. Align `presentation/dashboard/dashboard_page.js` with the currently served dashboard template tab set.
3. Add null-safe panel activation so missing optional panels cannot crash the whole page render path.
4. Verify the public homepage and key APIs render again after the hotfix is synced.

Acceptance:
- Opening the public homepage no longer results in a blank or data-less dashboard caused by frontend initialization failure.
- `转债套利 / AH / AB / LOF套利 / 监控套利 / 分红提醒 / 事件套利` tabs can switch normally.
- A missing or temporarily removed panel node does not crash `renderTabs()`.

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

## 15. Phase L: Daily Delisted Convertible Bond Exclusion (2026-03-23)

Goal: ensure the convertible-bond arbitrage page automatically removes bonds that are already delisted, ceased, or expired as of the current trading day, even when the page is still reading a previous cache snapshot.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first so the daily exclusion rule is explicit before code changes.
2. Keep the existing fetch-layer exclusion flag, but do not rely on it as the only truth source for dashboard output.
3. Add a strategy-layer daily filter for `/api/market/convertible-bond-arbitrage` that re-evaluates each row against the current Shanghai date on every response.
4. Exclude a row from the outward-facing list when:
   - `delistDate <= today`
   - or `ceaseDate <= today`
   - or `maturityDate < today`
5. Keep the existing API route and page structure unchanged; this round only corrects the daily visibility rule.

Acceptance:
- On any given day, the dashboard `转债套利` page no longer shows bonds whose `delistDate` or `ceaseDate` is already that day or earlier.
- Matured bonds whose `maturityDate` is earlier than today are also removed from the visible list.
- The exclusion still works when the API response originated from an older cache payload, because the Node/service layer re-checks dates at response time.
## 16. Phase M: Event Arbitrage Unified Integration (2026-03-23)

Goal: replace the narrow `鏀惰喘绉佹湁` dashboard tab with a broader `浜嬩欢濂楀埄` module that uses external event-arbitrage data as the primary reading path while preserving the existing merger-announcement routes as auxiliary evidence.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first so the renamed module, sub-tabs, API contract, and zero-login first-phase scope are explicit before implementation.
2. Keep the top-level dashboard tab count fixed at 6, but rename the old `鏀惰喘绉佹湁` tab to `浜嬩欢濂楀埄`.
3. Introduce a new aggregated API `GET /api/market/event-arbitrage` that returns:
   - overview cards
   - normalized category groups for `hk_private`, `cn_private`, `a_event`, `rights_issue`, and `announcement_pool`
   - per-source status metadata
4. Implement the fetch layer with direct public JSON requests to Jisilu for:
   - `hk_arbitrage_list`
   - `cn_arbitrage_list`
   - `astock_arbitrage_list`
5. Do not make Firecrawl part of the production hot path in phase 1; only document it as a future fallback if the public JSON interfaces disappear.
6. Keep `rights_issue` inside the API/model contract, but return it as disabled with empty rows in phase 1 because the current zero-login constraint disallows using the login-gated source.
7. Keep existing routes compatible:
   - `/api/market/merger`
   - `/api/merger/report`
   - `/api/merger/reports/today`
8. In the strategy layer, enrich external event rows with a lightweight exact-code match against the existing merger announcement pool, exposing:
   - latest matched announcement title
   - announcement date
   - PDF link
   - whether an AI report is already available
9. In the presentation layer, render `浜嬩欢濂楀埄` with internal sub-tabs:
   - `鎬昏`
   - `娓偂绉佹湁鍖?`
   - `涓鑲＄鏈夊寲`
   - `A鑲″鍒?`
   - `鍏憡姹?`
   - `娓偂渚涜偂鏉?寰呮帴鍏?`
10. Keep the new module webpage-only in phase 1:
   - no push integration
   - no new AI summary generation for Jisilu rows
   - no changes to the existing merger push chain

Acceptance:
- The dashboard top tab label changes from `鏀惰喘绉佹湁` to `浜嬩欢濂楀埄`.
- `GET /api/market/event-arbitrage` returns normalized real data for `hk_private`, `cn_private`, and `a_event`, plus `announcement_pool`, while `rights_issue` is present but explicitly disabled.
- The `浜嬩欢濂楀埄` page defaults to `鎬昏`, not `鍏憡姹?`.
- External event rows can show matched announcement/PDF/report metadata without breaking when no match exists.
- Legacy merger endpoints stay compatible for existing callers and AI-report flows.
- A source failure in one external category degrades only that category and does not blank the whole page or the rest of the dashboard.

## 17. Phase N: Minimal Monitor Editor + Popup Entry (2026-03-23)

Goal: simplify `监控套利` editing so the user only fills the smallest necessary business inputs, while the system auto-resolves the rest and keeps the editor hidden until explicitly opened.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first.
2. Keep existing monitor runtime data and calculation output unchanged unless the user edits a value.
3. Keep the editor closed by default; clicking `新增监控` or `编辑` opens the editor.
4. Reduce the visible input set to:
   - `收购方`
   - `目标方`
   - `换股比例`
   - `安全系数`
   - `现金对价` + `币种`
   - `现金选择权` + `币种`
5. Hide implementation-oriented fields from the user-facing form, including:
   - code
   - market
   - share currency
   - optional generated monitor name
6. Add lightweight stock search confirmation under `收购方` and `目标方` so the user can see which security has been identified before saving.

Acceptance:
- `监控套利` editor is not expanded by default when the panel opens.
- Clicking `新增监控` expands the editor inline within the current panel instead of opening popup-style overlay UI.
- Clicking `编辑` on an existing row opens the same inline editor with the current values filled in.
- The visible form includes `换股比例`.
- `收购方` / `目标方` inputs show resolved security info and candidate matches when auto-search runs.
- Existing monitor items can still be edited and saved without losing their stored hidden metadata.
## 18. Phase O: Startup Responsiveness + Premium History Self-Healing (2026-03-23)

Goal: remove the current "page waits too long" perception by fixing the broken data paths behind it, and make AH / AB premium history recover automatically when the SQLite cache degrades to a one-day snapshot.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first so the degraded-history recovery rule and IPO empty-state fallback are explicit before code changes.
2. Keep the existing cache-first dashboard strategy because cached quote endpoints are already fast enough for first paint.
3. Treat the following as production regressions that must self-heal instead of being silently skipped in incremental sync:
   - `premium_summary.sampleCount3Y <= 1`
   - missing `startDate3Y` / `endDate3Y` while samples exist
   - obviously collapsed short-range summaries that indicate the DB only retained a recent snapshot
4. In premium-history update mode, when the summary is degraded, force a full backfill for that symbol instead of doing the normal short incremental update window.
5. Change IPO data loading so "no stored history yet" returns a successful empty payload rather than HTTP 500 / `success: false`, because the dashboard should degrade to an empty table instead of looking broken.
6. After implementation, run server-side premium-history repair and verify `AH / AB` rows recover real multi-day sample ranges and non-null percentile values.

Acceptance:
- Normal cached dashboard quote endpoints remain fast for first paint.
- AH / AB no longer stay stuck at `sample 1 / same-day range` after the next repair cycle.
- Incremental premium-history update can detect a degraded cache and trigger full backfill for only the affected symbols.
- `/api/market/ipo` returns a parseable success payload with empty arrays when no IPO history is available yet.
- The homepage no longer looks "stuck loading" just because one optional data source currently has no stored history.

## 19. Phase P: Public CB Payload Slimming (2026-03-23)

Goal: fix the remaining homepage slow-open issue by shrinking the public `convertible-bond-arbitrage` response to the fields the dashboard actually renders.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the existing convertible-bond calculations unchanged.
3. Keep the route path unchanged:
   - `/api/market/convertible-bond-arbitrage`
4. Add a response-shaping step in the Node/service layer after row sanitization:
   - preserve the fields the dashboard uses for summary cards and dense main-table rendering
   - drop unused per-row fields that are inflating the payload by multiple megabytes
   - stop emitting duplicated public aliases for the same row collection and keep `data` as the single outward row array
5. Do not move this slimming into the raw Python fetch layer for this round; keep the raw fetch result available internally and only slim the outward-facing HTTP payload.

Acceptance:
- Public homepage no longer waits on a 6+ MB convertible-bond JSON payload.
- Cached `convertible-bond-arbitrage` HTTP response size is materially smaller than the current payload.
- Dashboard `转债套利` main table and summary cards still render the same user-visible values after slimming.

- Public `convertible-bond-arbitrage` response no longer repeats the same rows in top-level `list` / `rows` aliases.

## 19. Phase P: Event Arbitrage UI Simplification (2026-03-23)

Goal: simplify the `事件套利` reading path so the user lands directly on real category data, and A-share rows display only the core scraped content without forum links or expandable detail toggles.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first so the simplified event-arbitrage UI contract is explicit before frontend changes.
2. Remove the `总览` sub-tab from the phase-1 `事件套利` page, but keep the backend `overview` field in the API contract for internal aggregation and future use.
3. Change the default `事件套利` sub-tab from `overview` to `a_event`.
4. Keep the existing visible sub-tabs as:
   - `A股套利`
   - `港股套利`
   - `中概私有`
   - `港供套利`
   - `最新公告`
5. Remove the forum-link presentation from the `A股套利` page even if the raw payload still contains a forum URL.
6. Rename the A-share official announcement link label from `公告链接` to `官方公告`.
7. Remove expandable detail toggles from the `事件套利` tables in this round.
8. Render A-share `摘要` directly below each row as an always-visible secondary detail block instead of an expandable detail area or a dedicated summary column.

Acceptance:
- The `事件套利` page no longer exposes a `总览` sub-tab.
- Opening `事件套利` lands directly on `A股套利`.
- `A股套利` no longer renders `论坛链接`.
- The A-share announcement link label is `官方公告`.
- Event-arbitrage tables no longer show `展开 / 收起` controls.
- A-share rows show `摘要` directly below the main row using the existing detail-row visual style.

## 20. Phase Q: Constitution Alignment Audit And Guardrail (2026-03-23)

Goal: align the repository with the newly amended constitution using the smallest effective change set, and prevent future constitution drift from silently reappearing.

Plan:
1. Sync `CONSTITUTION.md` and `.specify/memory/constitution.md`, and update amendment metadata so the constitution contract is self-consistent again.
2. Treat this round as a governance-alignment change, not a broad architecture rewrite:
   - prioritize direct fixes with the shortest path
   - avoid mixing unrelated module refactors into the same round
   - record larger follow-up refactors separately if they are discovered during audit
3. Add a dedicated repo check for constitution drift:
   - compare the two constitution files as normalized UTF-8 text
   - fail with a clear diff preview when they diverge
   - expose the check through a stable command entry
4. Keep product behavior unchanged in this round unless a constitution violation requires a direct fix.

Acceptance:
- `CONSTITUTION.md` and `.specify/memory/constitution.md` stay synchronized after the amendment.
- Constitution version and amendment metadata reflect the 2026-03-23 change.
- The repository provides a one-command constitution sync check with non-zero exit on drift.
- This alignment round does not bundle unrelated product logic changes.

## 21. Phase R: Same-day Subscription Truthfulness + Invalid CB Exclusion + Dense CB Core Fields (2026-03-23)

Goal: fix three current user-visible regressions in one direct round:
1. `股债打新` must show today's real subscribe / lottery / listing items again, including current Beijing exchange IPO rows.
2. `转债套利` must stop showing obviously invalid rows such as zero-price or zero-turnover bonds that have already entered the delist / cease / force-redeem end state.
3. `转债套利` main table must surface the requested dense core parameters directly in the default row set.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the existing `股债打新` page structure, but repair the data truth path:
   - recognize Beijing exchange IPO codes correctly
   - do not keep trusting a fresh-looking empty cache snapshot when IPO history is still empty
   - redeploy the fixed IPO source so the live server can repopulate same-day rows
3. Harden `转债套利` visible-row filtering in the strategy/service layer:
   - continue honoring delist / cease / maturity dates
   - additionally exclude clearly invalid end-state rows such as `price <= 0`
   - exclude zero-turnover rows that have already entered the terminal delist / cease / maturity chain
4. Expand the outward-facing CB payload whitelist only to the fields needed by the dense table contract.
5. Refactor the frontend CB main table to display the requested core fields directly, without reintroducing the old detail-button reading path.

Acceptance:
- Opening the dashboard on the live server can show today's IPO subscribe row again when the upstream source has one, including Beijing exchange rows.
- `恒逸转债` and the other obviously invalid zero-price / terminal zero-turnover rows no longer appear in the visible CB list.
- `荣23转债` and similar rows already in the terminal cease / delist chain are excluded from the visible CB list.
- The CB main table directly shows:
  - bond / stock identity and price-change fields
  - stock 3Y ROE and debt ratio
  - convert metrics
  - premium and pure-bond premium metrics
  - redeem / putback / volatility / option / theoretical / maturity-yield fields
  - listing / convert-start / maturity / rating fields

## 22. Phase S: LOF Arbitrage Zero-login MVP (2026-03-23)

Goal: add a first production-safe `LOF套利` module without destabilizing the existing homepage, while continuing to investigate zero-login IOPV sources in parallel.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new LOF module contract, zero-login scope, and IOPV fallback rules.
2. Keep the current Node + Python layered architecture:
   - `data_fetch/lof_arbitrage` only fetches and normalizes Jisilu QDII rows
   - `strategy/lof_arbitrage` only computes signal basis, fees, and action status
   - `presentation` only exposes the new API and dashboard tab
3. Use direct public JSON endpoints as phase-1 primary source:
   - `/data/qdii/qdii_list/E`
   - `/data/qdii/qdii_list/A`
   - `/data/qdii/qdii_list/C`
4. Do not block phase 1 on official IOPV completeness:
   - if `iopv` / `iopv_discount_rt` is available, use it as high-confidence signal
   - else if intraday estimate fields are available, use them as medium-confidence signal
   - else degrade to NAV premium as low-confidence observation only
5. Keep Firecrawl out of the hot path in this round:
   - direct JSON first
   - Firecrawl only documented as future fallback if the public JSON disappears
6. Add a new public API `GET /api/market/lof-arbitrage`.
7. Add a new top-level dashboard tab `LOF套利` with one phase-1 table, summary cards, and always-visible risk/detail rows.
8. Keep the module webpage-only in phase 1:
   - no push integration
   - no auto-execution
   - no changes to existing modules beyond adding the new tab and refresh path
9. Record the ongoing IOPV search status explicitly in the outward payload so the UI can show whether the current zero-login chain has usable IOPV or only NAV fallback.

Acceptance:
- The homepage still opens normally after the new LOF module is added.
- `GET /api/market/lof-arbitrage` returns real rows from the zero-login Jisilu QDII endpoints.
- The `LOF套利` page shows:
  - current price
  - NAV premium
  - IOPV premium when publicly available
  - estimate premium when publicly available
  - signal basis
  - apply status
  - action status
- When IOPV is missing, the page clearly downgrades to observation mode instead of pretending the signal is execution-grade.
- A single-source failure in one LOF category degrades only that category and does not blank the homepage.

## 23. Phase T: CB Truth-source Yield + Formula Hint + Column Split Polish (2026-03-23)

Goal: finish the current convertible-bond dense-table round so the visible fields and source truthfulness match the latest user contract.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the existing theoretical-pricing engine unchanged for this round:
   - continue using `理论价值 = 纯债价值 + 期权理论价值`
   - continue using `期权理论价值 = 看涨期权价值 - 看跌期权价值`
3. Refine the `转债套利` main table rendering contract:
   - add `纯债价值` before `纯债溢价率`
   - split `理论价值` and `理论溢价率` into two separate visible columns
   - add a page-visible formula hint instead of hiding the pricing口径 only in code
4. Replace local `到期税前收益率` backfill with a real upstream field:
   - prefer Jisilu `bond_cb_jsl()` `到期税前收益`
   - do not continue using a local approximation formula as the outward field value
5. Keep `ROE` and `资产负债率` on real upstream financial fetches only, and make that source contract explicit in docs:
   - allow Eastmoney bulk financial tables as the stable server-side fallback when THS / Sina endpoints fail
6. Redeploy and verify both the API payload and the public page.

Acceptance:
- `转债套利` main table shows `纯债价值` immediately before `纯债溢价率`.
- `理论价值` and `理论溢价率` render as separate columns.
- The page visibly explains the current `理论价值` formula.
- `yieldToMaturityPretax` comes from a real upstream field and is no longer populated by the local fallback formula in this round.
- `stockAvgRoe3Y` and `stockDebtRatio` remain sourced from real upstream financial interfaces.

## 24. Phase U: Homepage Root-Module Cleanup (2026-03-24)

Goal: restore the stable homepage module contract, keep `LOF套利` as the visible fourth root tab, and reduce the active premium family back to `AH / AB`.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the cleaned homepage and premium contracts.
2. Keep homepage root navigation fixed at `7` modules, with `LOF套利` restored as the visible fourth root tab.
3. Remove abandoned premium experiments from public runtime scope:
   - no extra homepage root tab
   - no extra public market route
   - no extra historical-premium type
   - no scheduler/cache/bootstrap loading for removed datasets
4. Keep premium-history active contracts limited to `AH / AB`.
5. Keep LOF and existing premium modules stable:
   - `AH / AB` behavior unchanged
   - `LOF套利` remains accessible from the homepage
   - unrelated modules do not regress

Acceptance:
- Homepage root tabs remain `7`, and one visible tab is `LOF套利`.
- Premium-history active contracts remain limited to `AH / AB`.
- Existing `AH / AB / LOF套利 / 转债 / 监控 / 分红 / 事件套利` behavior does not regress.

## 24. Phase U: LOF Authenticated Enrichment + Market Subtabs (2026-03-23)

Goal: upgrade the current `LOF套利` MVP into a fuller real-data page that is closer to the live Jisilu reading path, while still refusing to fabricate unavailable `IOPV` fields.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the current layered architecture:
   - `data_fetch/lof_arbitrage` only fetches source rows and cache fallback
   - `strategy/lof_arbitrage` only computes outward row semantics and overview
   - `presentation` only renders page structure and columns
3. Add optional authenticated enhancement on top of the current Jisilu QDII endpoints:
   - if `data_fetch.plugins.lof_arbitrage.jisilu_cookie` is configured, send it and use the larger logged-in result set
   - if cookie is missing or invalid, automatically fall back to the public result set
4. Keep truthfulness strict:
   - more rows are allowed after login enhancement
   - `IOPV` / `IOPV溢价率` may still stay empty
   - outward payload and UI must state that clearly instead of inventing values
5. Expand standardized LOF fields so the page can render the practical long-table view, including:
   - code / name / issuer
   - current price / change rate / 成交额
   - 场内份额 / 场内新增份额
   - T-2 净值 / 净值日期 / 净值溢价
   - IOPV / IOPV溢价
   - 估值 / 估值溢价
   - 相关指数 / 指数涨幅
   - 申购费 / 申购状态 / 赎回费 / 赎回状态 / 管托费
   - 官方基金页链接 / 集思录详情链接
6. Refactor the LOF page into visible market subtabs:
   - `欧美市场`
   - `亚洲市场`
   - `商品`
7. Keep the module stable-first:
   - no push integration
   - no auto-trading semantics
   - a single-source failure only degrades the affected subtab

Acceptance:
- `LOF套利` can display the larger logged-in dataset when a valid cookie is present, while still working without it.
- The page exposes more of the real Jisilu fields instead of only the MVP summary view.
- `欧美市场 / 亚洲市场 / 商品` can be switched directly inside the LOF module.
- `IOPV` fields remain empty when the source truly does not return them, and the UI explains that they are currently unavailable.
- Homepage stability and other modules remain unaffected.

## 26. Phase W: Event-arbitrage Detail Text Responsive Width Fix (2026-03-24)

Goal: fix the `事件套利` detail-text layout so A-share `摘要` and HK/CN `备注` adapt to available screen width instead of being squeezed into the left quarter of the detail grid.

Plan:
1. Keep the data contract unchanged and only adjust presentation behavior.
2. Update the page contract docs first for the event-arbitrage detail-text layout.
3. Change the event-arbitrage detail renderers to use a single-column full-width detail block for:
   - A-share `摘要`
   - HK/CN `备注`
4. Add minimal CSS for a responsive single-column detail-grid variant, without changing other modules' shared detail layout.

Acceptance:
- `事件套利` A-share `摘要` occupies the usable detail-row width instead of staying compressed on the left.
- `港股套利` and `中概私有` `备注` follow the same full-width responsive behavior.
- Other detail-grid based modules keep their existing layout.

## 25. Phase V: LOF Estimated-value Completion From Source Change Rate (2026-03-23)

Goal: complete the currently missing actionable LOF estimate fields by deriving them only from real Jisilu source fields, while keeping `IOPV` empty unless the upstream truly returns it.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the derived-estimate contract.
2. Keep the LOF source truth contract strict:
   - `IOPV` is still direct-source only
   - `IOPV溢价率` is still direct-source only
   - `估值` and `估值溢价` may be derived only when Jisilu already provides `est_val_increase_rt`
3. Add a deterministic source-based derivation path:
   - `estimatedValue = navValue * (1 + est_val_increase_rt / 100)`
   - `estimatedPremiumRate = ((currentPrice / estimatedValue) - 1) * 100`
4. Persist derivation provenance in the outward payload so the page can explain where the value came from:
   - direct source
   - derived from `est_val_increase_rt`
5. Expand the LOF page so the strategy view is easier to use:
   - add visible `结论`
   - add visible `信号溢价`
   - add estimate-source, estimate-time, estimate-change, reference-price, and calculation-tips detail fields
6. Keep deployment risk low:
   - no push integration changes
   - no homepage root-tab changes
   - no changes to unrelated modules

Acceptance:
- Rows with real `est_val_increase_rt` now expose `estimatedValue` and `estimatedPremiumRate` instead of leaving the estimate area blank.
- `IOPV` and `IOPV溢价率` remain empty when upstream still does not provide them.
- LOF main table visibly shows `结论` and `信号溢价`.
- LOF detail area clearly explains whether the estimate is direct-source or derived from Jisilu estimate-change fields.
- The page remains loadable even if one LOF source category fails.

## 26. Phase W: CB Yield Removal + Volatility Trust Warning (2026-03-24)

Goal: reduce false precision in the convertible-bond main table by removing the now-unwanted maturity-yield display and explicitly downgrading volatility-driven theoretical metrics to reference-only status.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the current backend theoretical-pricing calculation unchanged in this round:
   - do not silently swap the volatility engine yet
   - do not change the API field schema just because the page is hiding one column
3. Refine the `转债套利` visible table contract:
   - remove `到期税前收益率` from the default visible columns
   - remove the same field from the default detail block
4. Clarify the trust boundary of the volatility-driven fields on the page:
   - `60日波动率` is the current historical annualized volatility estimate derived from recent equity closes
   - `期权理论价值 / 理论价值 / 理论溢价率` are reference values rather than execution-grade truth
5. Record the current volatility口径 explicitly in docs so the next volatility-refactor round can replace it cleanly.

Acceptance:
- `转债套利` page no longer displays `到期税前收益率`.
- `60日波动率` and the volatility-derived theoretical metrics are visibly marked as historical/reference values on the page.
- The current volatility formula and trust boundary are documented.
## 27. Phase Y: LOF Summary-card Removal + Detail-first Reading Path (2026-03-24)

Goal: simplify the `LOF套利` page by removing the current top summary-card band and making the long-table detail rows the default supplementary reading path.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the LOF fetch/strategy/API schema unchanged in this round:
   - `data.overview` may remain in the API for aggregation/debugging
   - no calculation or classification logic changes
3. Refine the LOF page structure contract:
   - remove the visible top summary cards `套利候选 / 仅观察 / 数据链路`
   - keep title/status text and market subtabs
   - keep the long table as the immediate primary reading path
4. Preserve the current always-visible secondary detail rows under each LOF item so explanatory fields remain directly readable without a separate summary-card strip.

Acceptance:
- `LOF套利` no longer renders the visible top summary-card area.
- The page still shows toolbar status, market subtabs, and the active-market long table.
- LOF secondary detail rows remain visible and continue to expose estimate/source/risk context.

## 28. Phase Z: LOF Module Cancellation From Homepage (2026-03-24)

Goal: remove `LOF套利` from the public homepage module set while keeping the rest of the dashboard stable.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Treat this round as a homepage/module-scope cancellation rather than a full backend feature purge:
   - remove the visible `LOF套利` root tab
   - remove homepage startup loading of LOF data
   - keep unrelated modules unchanged
3. Stop spending homepage/runtime preload cost on LOF:
   - dashboard bootstrap no longer requests `lofArb`
   - server preload no longer includes `lofArb`
4. Keep the existing LOF backend implementation archived in place for now, but disconnected from the public homepage reading path.

Acceptance:
- The homepage no longer shows `LOF套利`.
- Dashboard initial load no longer requests LOF data.
- Server preload no longer includes `lofArb`.
- `转债套利 / AH / AB / 监控套利 / 分红提醒 / 事件套利` remain usable.

## 29. Phase AA: LOF Complete Removal (2026-03-24)

Goal: fully retire `LOF套利` from the repository and runtime surface instead of only hiding it from the homepage.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Remove all active LOF runtime surfaces:
   - dashboard render/bind/bootstrap logic
   - public market route
   - server dataset registration and preload
   - `data_dispatch.py` action
3. Remove all active LOF config contracts from `config.yaml`.
4. Delete the retired implementation directories:
   - `data_fetch/lof_arbitrage`
   - `strategy/lof_arbitrage`
5. Verify the homepage still works and old LOF route access falls back to normal API 404 behavior.

Acceptance:
- No active homepage, server, route, or CLI path still references LOF.
- LOF implementation directories are removed.
- Homepage and remaining modules continue working.

## 29. Phase AA: Shared Dashboard Table Readability Upgrade (2026-03-24)

Goal: improve the readability of all dashboard long tables by upgrading shared presentation density, while keeping business meaning, sorting rules, pagination, and data pipelines unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the shared table-readability contract.
2. Keep this round strictly inside the presentation contract:
   - no fetch changes
   - no strategy calculation changes
   - no business-field meaning changes
3. Add minimum presentation config under `config.yaml > presentation.dashboard_table_ui` for:
   - desktop table font size
   - desktop header font size
   - desktop line height
   - desktop cell padding
   - tablet table font size
   - table-kind min widths
4. Add a light read-only endpoint `GET /api/dashboard/ui-config` so the static dashboard page can consume presentation config instead of hardcoding table density.
5. Keep the shared table renderer as the only main entry:
   - continue using `renderPaginatedTable()`
   - continue using `renderSimpleTable()`
   - do not fork separate table frameworks by module
6. Refine shared table rendering and CSS:
   - increase table text size and line height on desktop
   - enlarge header/body padding
   - keep sticky headers, sorting, pagination, and expand details unchanged
   - use per-table-kind min-width rules instead of relying only on `table-layout: fixed`
   - add clearer row separation and tabular-number alignment
7. Keep mobile safe:
   - only limited font growth under narrow breakpoints
   - continue using existing horizontal scroll containers when needed
   - do not introduce a second mobile-only table layout in this round

Acceptance:
- Desktop table text is visibly larger than the current `12px` baseline.
- Shared table renderers remain the primary rendering path for dashboard tables.
- `GET /api/dashboard/ui-config` returns the active table UI contract from config.
- Sorting, pagination, detail expansion, and field semantics remain unchanged.
- Desktop may use light controlled horizontal scrolling, but the page does not collapse on tablet/mobile widths.

## 30. Phase AB: Repository-local mini-SWE-agent Integration (2026-03-24)

Goal: embed a production-safe `mini-SWE-agent` helper path into the repository so agent execution can follow the same constitution-first workflow as Codex, without introducing a second parallel process.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the repository-local agent-assist contract.
2. Keep this round lightweight and tooling-only:
   - no runtime dashboard/API behavior changes
   - no deployment behavior changes
   - no background scheduler changes
3. Add a repository-owned prompt/task generator under `tools/` so `mini-SWE-agent` receives:
   - constitution-first instructions
   - plan/requirements/spec gate reminders
   - module-boundary rules
   - validation command defaults
4. Expose the helper through a stable local command entry from `package.json`.
5. Add a project-local usage guide that explains:
   - install steps
   - recommended `confirm` mode
   - how Codex and `mini-SWE-agent` should split work
   - example commands for `presentation`, `data_fetch`, and `strategy` scoped tasks
6. Keep the integration human-in-the-loop:
   - the tool generates repository-safe task text
   - it does not auto-run `mini-SWE-agent`
   - document/code review remains external to this helper

Acceptance:
- The repository contains a reusable local command that can generate a `mini-SWE-agent` task prompt for this project.
- The generated prompt explicitly reminds the agent to read `CONSTITUTION.md` first and stop for doc updates when contracts change.
- The repository contains a concise usage tutorial for installing and using `mini-SWE-agent` with this project.
- The integration does not alter the live dashboard, API routes, scheduler, or deployment flow.

## 31. Phase AC: Push Refactor to Summary + Event Alerts (2026-03-24)

Goal: replace the old `主推送 + 收购私有专报` structure with a cleaner `定时摘要 + 异动提醒` model that is easier to read, easier to validate, and closer to real decision needs.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and `contracts/dashboard-api-contract.md` first.
2. Retire the old merger-report push path from active push settings and scheduler flow:
   - remove the third push-time input from the homepage
   - remove merger-report push status from `GET /api/push/config`
   - stop exposing merger-report push as an active push route
3. Keep two push entrances only:
   - fixed-time summary push
   - event-driven alert push
4. Update push settings UI and API contract:
   - keep two summary times
   - add one editable event-alert cooldown minutes field
   - show summary push status and event-alert status separately
5. Rebuild summary push content into a denser readable format:
   - keep `可转债 / AH / AB / 打新 / 分红 / 自定义监控 / 事件套利新增次日汇总`
   - keep `自定义监控` full-volume
   - compress each row into scanable single-line or two-line Markdown
6. Add first-phase event alert logic for convertible bonds only:
   - trigger when `转股溢价率 < -3%`
   - enforce per-bond cooldown with default `30` minutes
   - alert payload must include only triggered rows, not the full summary
7. Track event-arbitrage newly discovered rows in push runtime state so the next day's fixed-time summary can include a concise `昨日新增事件套利` section.
8. After implementation, run local checks, sync the cloud server, set the public push HTML URL if missing, and verify the webpage plus push-config API online.

Acceptance:
- Push settings no longer contain `收购私有专报`.
- The dashboard shows `2` summary time inputs and `1` alert cooldown input.
- `GET /api/push/config` returns summary times, alert cooldown, and separate summary/alert delivery status.
- Scheduled push content becomes visibly more concise and readable.
- Event alerts send only convertible-bond trigger rows with `转股溢价率 < -3%`.
- The same bond is not re-alerted within `30` minutes.
- Event-arbitrage rows first discovered on day `D` can appear in the summary push on day `D+1`.

## 31. Phase AC: Dashboard UI Density + Hierarchy Coordination (2026-03-24)

Goal: improve dashboard aesthetics, information density, and reading hierarchy together, while keeping all current behavior, data contracts, and interaction semantics unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with a presentation-only contract.
2. Keep this round strictly inside the dashboard presentation layer:
   - no `/api/*` contract changes
   - no strategy / formula changes
   - no scheduler / push behavior changes
   - no route restructuring
3. Apply the smallest effective UI changes in:
   - `presentation/templates/dashboard_template.html`
   - `presentation/dashboard/dashboard_page.js`
4. Improve first-screen efficiency by tightening:
   - hero height
   - section spacing
   - tab strip height
   - push strip height
5. Improve module readability by tightening and reordering visible emphasis for:
   - title
   - key counts / update time / freshness state
   - summary cards
   - explanatory copy
6. Keep mobile and tablet safe:
   - preserve the current responsive structure
   - only compress spacing and hierarchy
   - do not create a second mobile-only interaction model
7. Keep all edits annotated with concise Chinese comments when changing core layout or key style behavior.

Acceptance:
- The page shows more effective information within the first screen on desktop.
- Key module metadata is easier to scan than before.
- Summary areas are more compact without reducing data truthfulness.
- Existing tabs, tables, sorting, pagination, push settings, and monitor editing behavior remain unchanged.

## 32. Phase AD: Release-path Visibility + Fast Deploy (2026-03-24)

Goal: shorten the real path from `local change -> GitHub -> server -> visible homepage`, and make every stage truthfully expose which version is actually online.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the release-visibility and fast-deploy contracts.
2. Extend `/api/health` so it exposes deployment/version metadata from the actual running checkout, instead of only generic process health.
3. Add homepage-visible version text so the user can directly confirm:
   - current git short SHA
   - current branch
   - current app version
   - current server start time
4. Keep the current full deploy path as the default safe path:
   - `push main -> GitHub Actions -> update_from_github.sh`
5. Add a separate fast deploy wrapper for dependency-unchanged releases:
   - still performs git sync
   - still performs service restart
   - still performs health check
   - still performs homepage marker verification
   - skips Node/Python dependency installation and Python import verification by default
6. Allow GitHub Actions manual dispatch to select `full` or `fast`, while normal `push main` keeps using `full`.
7. Keep this round minimal and deployment-focused:
   - no change to market-data formulas
   - no change to scheduler business rules
   - no change to module ordering or routing semantics

Acceptance:
- `/api/health` returns parseable version metadata from the running service.
- Homepage visibly shows the currently deployed version instead of forcing the user to infer from behavior.
- Repository contains a dedicated fast-deploy entry script for dependency-unchanged updates.
- GitHub manual deploy can choose `fast` mode, while `push main` remains the safe full deploy path.
- Fast deploy still fails loudly if health check or homepage marker verification fails.
- The implementation remains limited to minimal front-end presentation changes.

## 33. Phase AE: Governance Rollback + Config-driven Access Entry (2026-03-24)

Goal: cancel the newly introduced `PROJECT_*` root-doc requirement and repair the homepage access entry so it no longer hardcodes `127.0.0.1:5000`.

Plan:
1. Keep this round minimal and split into one governance rollback plus one access-entry truthfulness repair.
2. Governance rollback:
   - remove the new `PROJECT_PLAN.md / PROJECT_REQUIREMENTS.md / PROJECT_TECH_STACK.md` requirement from `CONSTITUTION.md`
   - keep the existing repository workflow gate centered on `refactor_docs/001-monitor-refactor/plan.md / REQUIREMENTS.md / SPEC.md`
   - delete the temporary root-level `PROJECT_*` entry files added only for the now-cancelled rule
3. Access-entry repair:
   - update contracts first in `REQUIREMENTS.md` and `SPEC.md`
   - stop hardcoding `http://127.0.0.1:5000` in the root `index.html`
   - expose a lightweight runtime access-info API from the Node server
   - let the root entry page render the real configured service/public URL at runtime when served by the app
   - when `index.html` is opened directly as a local file, keep preview usable and degrade gracefully instead of pretending a fixed port is always correct
4. Keep this round narrow:
   - no market-data formula changes
   - no scheduler behavior changes
   - no module layout refactor

Acceptance:
- `CONSTITUTION.md` and `.specify/memory/constitution.md` no longer require `PROJECT_PLAN.md / PROJECT_REQUIREMENTS.md / PROJECT_TECH_STACK.md`.
- The temporary root-level `PROJECT_*` files are removed from the active repository surface.
- The root `index.html` no longer displays or links to a hardcoded `http://127.0.0.1:5000`.
- The access entry page shows the real runtime service URL when opened through the running app.
- Direct local-file preview still works and no longer claims a fixed service URL that may be false.
