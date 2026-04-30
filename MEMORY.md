# Memory

**Retention**: max 50 entries. Oldest auto-deleted when exceeded.

**Record only**: decisions, meaningful actions, verification results, memorable failures, next steps.
**Do not**: dump full conversations.

## Entries

### 2026-04-30 | 项目Review修复（TDD）

- **Review发现**：根目录垃圾文件、data_fetch→scripts跨层导入、47个核心文件缺AI-SUMMARY、缺presentation/README.md
- **Task 21**: 清理根目录垃圾文件 + 删除 strategy/aa_premium 空目录 → 新建 `tests/root_cleanliness.test.js`
- **Task 20**: 修复跨层导入 — 4个数据库模块从 scripts/ 下沉到 shared/db/，更新7个data_fetch文件+3个scripts文件导入路径，删除 scripts/ 旧文件，更新架构测试识别 `from shared.db` 合法导入
- **Task 19**: AI-SUMMARY覆盖率 — 批量给47个核心文件添加摘要（data_fetch/、strategy/、shared/、notification/、presentation/），新建 `tests/ai_summary_coverage.test.js`
- **Task 18**: 创建 `presentation/README.md`（职责、API路由、React UI说明），新建 `tests/presentation_readme.test.js`
- **Verification**: 全部13个测试通过 + `npm run ui:build` 通过 + `npm run check` 通过

### 2026-04-30 | 合并根目录 config.yaml → config/config.yaml

- **Decision**: 用户质问两个 config.yaml 未合并，过渡期应结束
- **Action**: 将根目录 `config.yaml`（564行业务配置）合并入 `config/config.yaml`（33行元数据）→ 598行统一配置
- **Action**: 更新 `shared/config/node_config.js` — `CONFIG_FILE` 指向 `config/config.yaml`
- **Action**: 更新 `shared/config/script_config.py` — `CONFIG_FILE` 指向 `config/config.yaml`
- **Action**: 删除根目录 `config.yaml`
- **Verification**: `npm run check` 通过，全部UI测试通过

### 2026-04-30 | 概览页面重构：打新置顶+策略混排+事件套利

- **Decision**: 概览页改造：打新/申购置顶展示，机会总览支持策略类型筛选
- **Action**: 新增 `SubscriptionTopSection` 组件（打新置顶区）— 放在概览页 MetricMatrix 之后
- **Action**: `SubscriptionTopSection` 对齐老UI面板 — 标题"新股打新"、当前阶段标签列（今日申购/今日中签缴款/今日上市高亮）、类型（新股/债券）、名称/代码合并、申购上限、发行价/转股价
- **Action**: `OpportunityCommandCenter` 增加策略筛选器 — 全部|转债|LOF|AH|AB|事件套利 过滤芯片
- **Action**: `buildOpportunityRows` 扩展事件套利数据来源（A股套利+港股私有），取前3条
- **Action**: `specs/react-terminal-ui.md` §4.1 更新概览页规格（打新置顶+机会筛选+转债表格三层结构）
- **TDD**: RED → GREEN → REFACTOR（7步测试），新建 `tests/ui_overview_subscription_pin.test.js`
- **Verification**: 全部6个UI测试通过，`npm run ui:build` 通过，`npm run check` 通过

- Decision: 服务器启动失败，view_models和routes使用CommonJS但被当作ES Module加载
- Fix: ui/routes/*.js → .cjs, ui/dashboard/*.js → .cjs, ui/view_models/*.js → .cjs
- Fix: update start_server.js require paths to .cjs
- Fix: config.yaml dashboard_entry路径从presentation改为ui/templates
- Fix: tool_paths.py tools→scripts目录名修复，config.yaml C++注释→YAML
- Verification: npm run check通过，npm run ui:build通过，health web:ok

### 2026-04-30 | 大文件拆分完成

- Decision: INDEX.md §9 规则要求代码文件不超过 1000 行，3 个文件超标
- Action: 拆分 dashboard_page.js → constants.js（提取 UI 常量 ~200 行）
- Action: 拆分 source.py → cb_metrics.py（提取计算密集型函数 ~570 行）
- Action: 新建 server_config_loader.js（配置读取逻辑 ~300 行）
- Verification: 所有文件语法检查通过，AI-SUMMARY 已添加
- Updated: INDEX.md §9.1、§9.2、§9.4 新增文件索引
- Next: start_server.js 尚未完全重构为使用 server_config_loader.js（依赖过多全局状态）

### 2026-04-30 | React UI 推送设置独立Tab + TDD工作流

- Decision: 用户批评未遵循TDD工作流（文档先行→RED→GREEN），要求推送设置从每页底部移至独立顶级Tab
- Fix Phase 1: `specs/react-terminal-ui.md` 更新Tab结构文档（10个顶级Tab含推送设置）
- Fix Phase 2: TabNav新增push tab：`{ key: 'push', label: '推送设置' }`
- Fix Phase 3: 移除页面底部PushSettings，改为条件渲染 `{activeTab === 'push' && <PushSettingsPage />}`
- Fix Phase 4: SearchBar排除push tab：`activeTab !== 'overview' && activeTab !== 'push'`
- Fix Phase 5: `toNumber(null/undefined)` 修复 → 返回null而非0（流通市值显示"--"而非"0"）
- Fix Phase 6: 表格+数据内容居中（`.num { text-align: center !important; }`）
- Fix Phase 7: PushSettingsPage完善（推送时间、模块开关、Webhook、调度器、上次推送、推送总开关）
- Tests: 新建 `ui_push_tab.test.js`（推送设为顶级Tab）和 `ui_rights_issue.test.js`（抢权配售子Tab）
- Verification: 全部6个UI测试通过 + `npm run ui:build` 通过
- 之前工作: Phase 1-6 信息补全（抢权配售/事件套利板块、ConvertibleTable 22列、小额刚兑子tab等）

### 2026-04-30 | 数据获取层结构审查与修复（Review + TDD）

- Decision: `shared/market_service.py` 越界引入 `tools/` 模块（`market_pairs`、`premium_history_db`），违反分层规则
- Action: 将 `build_ah_snapshot` + `build_ab_snapshot` 及依赖助手迁移至 `data_fetch/ah_premium/source.py` 和 `data_fetch/ab_premium/source.py`
- Action: 删除 `tools/fetch_convertible_bond.py`、`tools/fetch_dividend.py`（与 `data_fetch/` 完全重复）
- Action: 删除 `event_arbitrage/fetcher.py` 中 `verify=False` SSL 回退（安全隐患）
- Action: `shared/bus/market_record.py` 新增 `create_error_record()` 统一错误记录构造
- Verification: `python3 tests/test_data_fetch_structure.py` 6/6 通过，`python3 tools/check_plugin_boundaries.py` 通过
- Verification: `python3 data_dispatch.py ah`、`python3 data_dispatch.py ab` 数据正常获取
- Next: 可用 `create_error_record()` 逐步替换 8 个 normalizer 中的内联错误构造

### 2026-04-30 | ELODIE workflow migration completed

- Decision: adopt ELODIE workflow structure for AI collaboration
- Action: created `CLAUDE.md`, `specs/` (5 files), `missions/0430-migrate-to-elodie/`, `MEMORY.md`, `config/`, `templates/`
- Action: archived `refactor_docs/001-monitor-refactor/` → `archive/`
- Action: deprecated `AGENTS.md` and `CONSTITUTION.md`
- Verification: `python3 tools/check_plugin_boundaries.py` passes
- Next: use new workflow for subsequent tasks

### 2026-04-30 | 根目录简化

- Decision: 根目录文件过多，需要清理
- Action: 归档 `AGENTS.md` + `CONSTITUTION.md` → `archive/docs-deprecated/`
- Action: 移动 `db_paths.py` → `shared/paths/db_paths.py`，更新 6 个 tools/ 脚本引用
- Action: 移动 `smoke_check.js` → `tests/smoke_check.js`，更新 `package.json`
- Action: 移动 `RUNBOOK.md` → `docs/RUNBOOK.md`
- Action: 删除 `tools/check_constitution_sync.py`（引用已删除的 `.specify/`）
- Action: 更新 `tools/render_mini_swe_task.py` 工作流引用
- Action: 更新 `INDEX.md` 和 `package.json`
- Verification: `python3 tools/check_plugin_boundaries.py` passes, `node tests/smoke_check.js` passes

### 2026-04-30 | 补齐所有缺失 specs

- Decision: specs/ 目录严重不全，11 个模块 spec 缺失，2 个已有现成文档未迁移
- Action: 从 archive 迁移 5 份现成文档 → specs/（data-model, api-contract, lof-arbitrage, cb-rights-issue, push-system）
- Action: 从代码逆向提取 8 份模块 spec（ah-premium, ab-premium, merger-arbitrage, event-arbitrage, dividend, subscription, custom-monitor, exchange-rate）
- Action: 更新 `specs/spec.md` 模块地图，移除全部 "(待建)" 标记，新增 4 个 spec 引用
- Verification: `npm run check` passes, `python3 tools/check_plugin_boundaries.py` passes
- Next: 后续新模块开发时直接遵循 specs/ 格式创建 spec

### 2026-04-30 | 修复工作流文件缺失

- Decision: 审查发现根目录 README.md 缺失，各层 README 内容过时
- Action: 创建根目录 `README.md` — 项目总览、快速导航、技术栈、启动命令
- Action: 更新 `data_fetch/README.md` — 补充 cb_rights_issue、event_arbitrage、exchange_rate 插件，添加 specs/ 引用
- Action: 更新 `strategy/README.md` — 补充 cb_rights_issue、event_arbitrage 插件，添加 specs/ 引用
- Action: 更新 `presentation/README.md` — 补充 React UI 说明、/legacy 回滚、routes 细分，添加 specs/ 引用
- Action: 更新 `notification/README.md` — 补充 4 条推送链路总览、目录结构，添加 specs/ 引用
- Action: 更新 `shared/README.md` — 添加 specs/ 引用
- Action: 修复 `config.yaml` C++ 风格注释（// → #），修复 YAML 解析错误
- Verification: `npm run check` passes, `python3 tools/check_plugin_boundaries.py` passes

### 2026-04-30 | React UI 模块补全（TDD）

- Decision: 新版 React UI 功能覆盖不全，用 TDD 补全
- Action: Phase 1 — 基础上线：`ui:build`/`ui:check`、`/legacy` 路由、`ui/dist` 静态服务
- Action: Phase 2 — Tab 导航 + 8 模块详细表格（转债、AH、AB、LOF、打新、监控、分红）
- Action: Phase 3 — 全局搜索 + 点击表头排序（useSort hook + SortableTh）
- Action: 扩展 API fetch（subscriptions、dividend）
- Verification: `npm run ui:build` 通过，4 个测试全部通过
- Action: Phase 5 — 推送设置面板（推送时间、模块开关、Webhook/调度器/上次推送状态）
- Next: 如需完整推送编辑保存功能（POST /api/push/config），可继续扩展
