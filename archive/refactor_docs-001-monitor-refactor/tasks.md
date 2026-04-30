# Tasks: Alpha Monitor Dashboard Refactor

**Input**: Design documents from `/refactor_docs/001-monitor-refactor/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required for scope), `research.md`, `data-model.md`, `contracts/`

**Tests**: 本轮不额外引入新的自动化测试框架，使用现有命令校验、公网健康检查、桌面端/手机端手工验收。  
**Organization**: 任务按用户故事分组，保证每个故事都能独立实现、独立验收、独立交付。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可并行执行（不同文件、无未完成前置依赖）
- **[Story]**: 用户故事标签（`[US1]`、`[US2]`、`[US3]`、`[US4]`）
- 每条任务都包含明确文件路径

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: 先把实施说明、接口合同、运行验收口径同步到最新计划，避免后续再次偏离公网部署目标。

- [ ] T001 同步公网部署与页面验收入口说明到 `refactor_docs/001-monitor-refactor/quickstart.md`
- [ ] T002 [P] 补充首页与公网健康检查合同到 `refactor_docs/001-monitor-refactor/contracts/dashboard-api-contract.md`
- [ ] T003 [P] 补充分层健康状态与部署配置模型到 `refactor_docs/001-monitor-refactor/data-model.md`
- [ ] T004 整理正式启动、停止、巡检说明到 `RUNBOOK.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 先完成所有故事都依赖的配置合同、健康分层、部署资产与运行边界。

**Critical**: 在本阶段完成前，不进入任何页面功能收口。

- [ ] T005 扩展部署与公网访问配置合同到 `config.yaml`
- [ ] T006 [P] 接入新增配置字段读取与默认值到 `shared/config/node_config.js` 和 `shared/config/script_config.py`
- [ ] T007 [P] 收紧公开地址、运行目录与路径策略到 `shared/paths/node_paths.js` 和 `shared/paths/script_paths.py`
- [ ] T008 重构分层健康状态基线与非致命任务隔离到 `start_server.js`
- [ ] T009 [P] 增强健康检查脚本输出与故障分类到 `tools/check_health.ps1`
- [ ] T010 [P] 创建 Linux 部署资产目录与服务模板到 `tools/deploy/alpha-monitor.service` 和 `tools/deploy/nginx-alpha-monitor.conf`
- [ ] T011 [P] 创建公网反向代理备选模板到 `tools/deploy/Caddyfile`
- [ ] T012 收敛正式启动脚本与开发辅助脚本边界到 `package.json`、`start_dashboard.bat`、`stop_dashboard.bat`

**Checkpoint**: 配置、健康检查、正式部署骨架和运维入口全部就位。

---

## Phase 3: User Story 1 - 云服务器公网长期在线访问 (Priority: P1) MVP

**Goal**: 任何拿到正式网址的用户都能稳定打开 Alpha Monitor，且关闭终端或断开会话后服务仍在线。

**Independent Test**: 在云服务器部署后，外部浏览器可访问首页与 `/api/health`；关闭 SSH 会话后仍可访问；重启服务器后服务自动恢复。

### Implementation for User Story 1

- [ ] T013 [US1] 实现正式首页与 `/api/health` 的服务存活校验到 `start_server.js` 和 `presentation/routes/dashboard_routes.js`
- [ ] T014 [P] [US1] 加强端口冲突、入口文件缺失、公开地址日志输出到 `start_server.js`
- [ ] T015 [P] [US1] 重写稳定启动与停止逻辑边界到 `tools/start_stable.ps1`、`tools/stop_stable.ps1`、`tools/keep_running.js`
- [ ] T016 [US1] 新增 Linux `systemd` 安装与卸载脚本到 `tools/deploy/install_systemd.sh` 和 `tools/deploy/uninstall_systemd.sh`
- [ ] T017 [P] [US1] 新增反向代理启用说明与公网 URL 诊断脚本到 `tools/show_access_info.ps1` 和 `RUNBOOK.md`
- [ ] T018 [US1] 补充公网烟雾验证与正式访问检查到 `smoke_check.js` 和 `refactor_docs/001-monitor-refactor/quickstart.md`

**Checkpoint**: 正式部署链路可独立交付，网页不再依赖手工终端常驻。

---

## Phase 4: User Story 2 - 首页壳层、顶部信息与推送设置收口 (Priority: P2)

**Goal**: 用户打开首页后能直接看到真实数据的状态行、股债打新长表、紧凑版推送设置和 6 个主功能页签。

**Independent Test**: 首页打开后不是空壳；状态行、股债打新、推送设置正常渲染；6 个页签可切换；推送时间可加载和保存。

### Implementation for User Story 2

- [ ] T019 [US2] 重构首页数据加载、页签切换和顶层状态管理到 `presentation/dashboard/dashboard_page.js`
- [ ] T020 [P] [US2] 重写首页 DOM 骨架与黑红科技风布局到 `presentation/templates/dashboard_template.html`
- [ ] T021 [P] [US2] 实现单行状态文字、全屏布局和桌面端/手机端响应式样式到 `presentation/templates/dashboard_template.html`
- [ ] T022 [US2] 实现股债打新今日事项长表渲染到 `presentation/dashboard/dashboard_page.js`
- [ ] T023 [US2] 收紧推送设置三时间框交互与保存反馈到 `presentation/dashboard/dashboard_page.js`
- [ ] T024 [US2] 对齐推送配置接口整形与三时间框约束到 `presentation/routes/push_routes.js`、`presentation/view_models/push_payload.js`、`notification/scheduler/push_config_store.js`
- [ ] T025 [US2] 确保首页正式入口与页面交付只由展示层承载到 `presentation/routes/dashboard_routes.js` 和 `start_server.js`

**Checkpoint**: 首页壳层、顶部模块和推送设置已经符合规格说明，可单独演示。

---

## Phase 5: User Story 3 - 转债套利、AH、AB 通用表格系统收口 (Priority: P3)

**Goal**: 用户可以在转债套利、AH、AB 页面使用统一的长表、排序、分页、序号和摘要排行能力。

**Independent Test**: 三个表格都支持点击表头排序、50 条分页、连续序号；AH/AB 同时显示前三和倒数前三；电脑端和手机端都能滚动查看。

### Implementation for User Story 3

- [ ] T026 [US3] 实现共享表格状态、排序状态与分页状态到 `presentation/dashboard/dashboard_page.js`
- [ ] T027 [P] [US3] 扩展转债套利字段映射与表格渲染到 `presentation/dashboard/market_dashboard.js`
- [ ] T028 [P] [US3] 实现 AH 页面前三、倒数前三、主表字段与排序行为到 `presentation/dashboard/market_dashboard.js`
- [ ] T029 [P] [US3] 实现 AB 页面前三、倒数前三、主表字段与排序行为到 `presentation/dashboard/market_dashboard.js`
- [ ] T030 [US3] 对齐转债套利、AH、AB 的展示字段整形到 `presentation/routes/market_routes.js` 和 `presentation/view_models/overview.js`
- [ ] T031 [US3] 补充序号列、分页栏、粘性表头、横向滚动容器和移动端可读性样式到 `presentation/templates/dashboard_template.html`
- [ ] T032 [US3] 审计并补齐 AH 历史库重建与样本覆盖分类到 `tools/rebuild_premium_db.py` 和 `tools/audit_ah_history_coverage.py`

**Checkpoint**: 转债套利、AH、AB 三块形成统一表格系统，可独立交付。

---

## Phase 6: User Story 4 - 监控套利、分红提醒、收购私有与数据可信度收口 (Priority: P4)

**Goal**: 用户能在剩余三块业务页看到可信的实时数据、清楚的公式解释、全量公告和高亮规则。

**Independent Test**: 监控套利显示实时股价与两腿收益率；分红提醒突出今日登记日；收购私有显示全量公告且今日公告高亮；数据不再明显陈旧或缺字段。

### Implementation for User Story 4

- [ ] T033 [US4] 修复监控套利默认股价刷新与动态重算链路到 `start_server.js` 和 `strategy/custom_monitor/service.js`
- [ ] T034 [P] [US4] 渲染监控套利公式说明与实时两腿结果到 `presentation/dashboard/monitor_dashboard.js` 和 `presentation/view_models/monitor_row.js`
- [ ] T035 [P] [US4] 收紧分红提醒页面为今日重点加全量列表模式到 `presentation/dashboard/dividend_dashboard.js`
- [ ] T036 [P] [US4] 渲染收购私有全量公告表与今日公告高亮到 `presentation/dashboard/merger_dashboard.js`
- [ ] T037 [US4] 补齐收购私有价格字段、日期标准化和最新排序口径到 `presentation/routes/market_routes.js` 和 `strategy/merger/service.js`
- [ ] T038 [US4] 收紧次级模块的加载态、空态、失败态和统一视觉反馈到 `presentation/dashboard/dashboard_page.js` 和 `presentation/templates/dashboard_template.html`

**Checkpoint**: 六个功能页全部可用，且监控套利、分红提醒、收购私有达到正式可读状态。

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 做最终一致性核对、命令回归、公网验收和文档收口。

- [ ] T039 [P] 同步最终行为变更到 `refactor_docs/001-monitor-refactor/REQUIREMENTS.md` 和 `refactor_docs/001-monitor-refactor/SPEC.md`
- [ ] T040 复核宪法同步状态到 `CONSTITUTION.md` 和 `.specify/memory/constitution.md`
- [ ] T041 运行 `npm run check`、`npm run check:boundaries` 并记录结果到 `refactor_docs/001-monitor-refactor/quickstart.md`
- [ ] T042 运行 `python data_dispatch.py exchange-rate`、`python data_dispatch.py ah`、`python data_dispatch.py ab` 并记录结果到 `refactor_docs/001-monitor-refactor/quickstart.md`
- [ ] T043 执行公网 URL、`/api/health`、桌面端、手机端手工验收并记录结果到 `refactor_docs/001-monitor-refactor/quickstart.md`
- [ ] T044 执行 `/speckit.analyze` 等价核对并记录 AH/AB 公式一致性结论到 `refactor_docs/001-monitor-refactor/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1**: 可立即开始。
- **Phase 2**: 依赖 Phase 1，且阻塞所有用户故事。
- **Phase 3 / US1**: 依赖 Phase 2，属于本轮最小可交付范围。
- **Phase 4 / US2**: 依赖 Phase 2，可在 US1 稳定后推进。
- **Phase 5 / US3**: 依赖 Phase 4 提供的首页壳层与通用展示规则。
- **Phase 6 / US4**: 依赖 Phase 4 的页面框架，但不依赖 US3 完成。
- **Phase 7**: 在需要交付的用户故事完成后执行。

### User Story Dependencies

- **US1 (P1)**: 无其他故事依赖，是当前 MVP。
- **US2 (P2)**: 依赖基础配置与健康链路，不依赖 US3、US4。
- **US3 (P3)**: 依赖 US2 的首页壳层与展示骨架。
- **US4 (P4)**: 依赖 US2 的页面框架，但可以与 US3 并行推进不同模块。

### Parallel Opportunities

- T002 与 T003 可并行，因为只改文档模型。
- T006、T007、T009、T010、T011 可在 Phase 2 内并行。
- US1 中 T014、T015、T017 可并行。
- US2 中 T020、T021 可并行；T023 与 T024 可并行。
- US3 中 T027、T028、T029 可并行。
- US4 中 T034、T035、T036 可并行。

## Parallel Example: User Story 3

```text
Task: "扩展转债套利字段映射与表格渲染到 presentation/dashboard/market_dashboard.js"
Task: "实现 AH 页面前三、倒数前三、主表字段与排序行为到 presentation/dashboard/market_dashboard.js"
Task: "实现 AB 页面前三、倒数前三、主表字段与排序行为到 presentation/dashboard/market_dashboard.js"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. 完成 Phase 1 和 Phase 2。
2. 完成 US1 公网长期在线访问。
3. 先验证云服务器正式入口、`/api/health`、重启恢复、断开终端后仍在线。
4. 只有 US1 验收通过后，才进入页面收口。

### Incremental Delivery

1. 先打通正式部署与健康链路。
2. 再交付首页壳层与顶部模块。
3. 再交付转债套利、AH、AB 通用表格。
4. 最后交付监控套利、分红提醒、收购私有和全量一致性核对。

### Suggested MVP Scope

- 推荐 MVP 范围：**Phase 1 + Phase 2 + US1**
- 理由：先根治“网页经常打不开”和“公网无法稳定访问”的问题，再继续页面和数据细化，风险最低。

## Notes

- 所有任务都保持“先改文档，再改代码，再核对”。
- AH 与 AB 的公式本轮不改方向，最终必须核对与 `SPEC.md` 第 `6.1`、`6.2` 条一致。
- 若某条任务暴露出接口字段缺口，优先在 `presentation/routes/` 和 `presentation/view_models/` 做最小整形，只有确有必要时再下沉到 `strategy/` 或 `data_fetch/`。
