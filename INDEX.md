# Alpha Monitor — 项目索引

**定位**：金融套利机会监控终端，从真实市场数据中发现套利机会，通过网页展示和企业微信推送完成闭环。
**阶段**：React 金融终端 UI 并行重做中，旧 HTML 看板保留 `/legacy` 回滚入口。
**技术栈**：Node.js 18+ + Express（API/服务层），Python 3（数据抓取/计算层），React + Vite（新前端），SQLite + JSON（运行时状态）。

---

## 1. 架构概览

```
浏览器/客户端
    │
    ▼
┌─────────────────────────────────────┐
│  presentation/        API 路由层    │
│  ├─ routes/           /api/market/* │
│  ├─ view_models/      数据整形      │
│  └─ templates/        HTML 模板     │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  strategy/            业务计算层    │
│  ├─ ah_premium/       AH 溢价排名   │
│  ├─ convertible_bond/ 转债套利      │
│  ├─ lof_arbitrage/    LOF 套利      │
│  └─ ... (共 10 个插件)              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  "The Bus" — 标准化记录格式         │
│  shared/bus/market_record.{py,js}   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  data_fetch/          数据抓取层    │
│  ├─ ah_premium/       腾讯行情      │
│  ├─ convertible_bond/ 集思录+东财   │
│  ├─ lof_arbitrage/    集思录        │
│  └─ ... (共 11 个插件)              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  上游数据源                         │
│  腾讯行情 / 集思录 / AkShare / 东财 │
└─────────────────────────────────────┘
```

**分层规则**：
- `data_fetch/` 只做抓取+标准化，不写业务逻辑
- `strategy/` 只做计算+规则判断，不直接调上游 API
- `presentation/` 只做 API 整形+展示，不做计算
- `notification/` 只做推送+调度，不碰数据抓取
- 跨层通信只能通过 The Bus 标准化记录
- 跨插件禁止直接 import（由 `tools/check_plugin_boundaries.py` 强制检查）

---

## 2. 目录索引

### 2.1 data_fetch/ — 数据抓取层（11 个插件）

每个插件标准结构：`fetcher.py`（调度）+ `source.py`（上游 API）+ `normalizer.py`（标准化为 Bus 记录）。部分插件有 `history_source.py`/`history_sync.py`（历史数据同步）。

| 插件 | 数据源 | 关键文件 | 输出 |
|------|--------|----------|------|
| `ah_premium/` | 腾讯行情 | `fetcher.py`, `normalizer.py` | AH 股溢价快照 |
| `ab_premium/` | 腾讯行情 | `fetcher.py`, `normalizer.py` | AB 股溢价快照 |
| `exchange_rate/` | 腾讯 | `fetcher.py`, `normalizer.py` | 港币/美元人民币汇率 |
| `convertible_bond/` | 集思录 + 东财 | `fetcher.py`, `source.py`, `normalizer.py`, `history_sync.py`, `history_source.py` | 转债套利数据（含理论定价） |
| `cb_rights_issue/` | 集思录 | `fetcher.py`, `source.py`, `normalizer.py`, `history_source.py` | 转债抢权配售数据 |
| `lof_arbitrage/` | 集思录 | `fetcher.py`, `source.py`, `normalizer.py` | LOF/QDII 套利数据 |
| `merger/` | 公告 API | `fetcher.py`, `source.py`, `normalizer.py` | 并购重组公告 |
| `event_arbitrage/` | 集思录 | `fetcher.py`, `normalizer.py` | 事件驱动套利 |
| `subscription/` | 多源 | `fetcher.py`, `ipo_source.py`, `bond_source.py`, `normalizer.py` | 新股/转债申购日历 |
| `dividend/` | AkShare / 巨潮 | `fetcher.py`, `source.py`, `normalizer.py` | 股息公告 |
| `custom_monitor/` | 运行态 | `input_reader.py` | 用户自定义监控组合 |

**统一入口**：`data_dispatch.py <action>` — 命令行调度器，根据 action 调用对应插件的 fetcher。

### 2.2 strategy/ — 业务计算层（10 个插件）

每个插件标准结构：`service.py`（Python 计算逻辑）+ `service.js`（Node.js 适配器）。部分有 `runtime_service.js`（运行时状态管理）或 `discount_runtime_store.js`（策略状态持久化）。

| 插件 | 关键文件 | 业务规则 |
|------|----------|----------|
| `ah_premium/` | `service.py`, `service.js` | 溢价率排名、历史百分位 |
| `ab_premium/` | `service.py`, `service.js` | AB 溢价排名 |
| `convertible_bond/` | `service.py`, `service.js`, `discount_runtime_store.js` | 双低策略、理论收益率、回售套利、折价策略（买入/卖出/监控） |
| `cb_rights_issue/` | `service.py` | 抢权配售预期收益计算、阶段判定、入池判断 |
| `lof_arbitrage/` | `service.py` | LOF/QDII 溢价率排名 |
| `merger/` | `service.py`, `service.js` | 并购重组 deal 分析、AI 报告生成（DeepSeek） |
| `event_arbitrage/` | `service.py` | 事件匹配与过滤 |
| `subscription/` | `service.py`, `service.js` | 申购事件跟踪 |
| `dividend/` | `service.py`, `service.js`, `runtime_service.js` | 股权登记日跟踪、收益率计算 |
| `custom_monitor/` | `service.py`, `service.js`, `runtime_service.js` | 自定义组合收益率计算 |

### 2.3 presentation/ — API 与展示层

| 文件 | 职责 | 服务端点 |
|------|------|----------|
| `routes/market_routes.js` | 市场行情路由 | `/api/market/ah`, `/api/market/ab`, `/api/market/convertible-bond-arbitrage`, `/api/market/lof-arbitrage`, `/api/market/merger`, `/api/market/event-arbitrage`, `/api/market/cb-rights-issue`, `/api/market/ipo`, `/api/market/convertible-bonds`, `/api/market/exchange-rate` |
| `routes/dashboard_routes.js` | 看板路由 | `/api/dashboard/ui-config`, `/api/dashboard/resource-status`, `/api/dashboard/overview`, `/api/monitors`, `/api/dividend?action=*` |
| `routes/push_routes.js` | 推送配置路由 | `/api/push/config`, `/api/push/cb-rights-issue-config`, `/api/push/lof-arbitrage-config`, `/api/push/wecom` |
| `view_models/overview.js` | 看板概览数据组装 | 被 dashboard_routes 调用 |
| `view_models/push_payload.js` | 推送配置响应格式 | 被 push_routes 调用 |
| `dashboard/dashboard_page.js` | 旧看板页面逻辑 | legacy 页面渲染 |
| `templates/dashboard_template.html` | 旧看板 HTML 模板 | 含内联 CSS/JS，暗色金融终端主题 |

### 2.4 notification/ — 推送与调度层

| 组件 | 关键文件 | 职责 |
|------|----------|------|
| **WeCom 客户端** | `wecom/client.js` | 发送 Markdown 到企业微信 Webhook |
| **调度器** | `scheduler/wecom_scheduler.js` | 定时推送调度（60s tick） |
| **推送配置** | `scheduler/push_config_store.js`, `push_runtime_store.js` | 运行时推送配置与状态 |
| **模块配置** | `scheduler/module_push_config_store.js`, `module_push_runtime_store.js` | 各模块（CB/LOF/抢权配售）独立推送配置 |
| **摘要服务** | `summary/main_summary.js` | 聚合所有模块生成每日摘要 Markdown |
| **折价策略提醒** | `alerts/event_alert_service.js` | 实时折价买入/卖出/监控名单推送 |
| **CB 套利推送** | `cb_arbitrage/service.js` | 可转债套利独立推送逻辑 |
| **抢权配售推送** | `cb_rights_issue/service.js` | 抢权配售独立推送逻辑 |
| **LOF 套利推送** | `lof_arbitrage/service.js` | LOF 套利独立推送逻辑（定时+即时） |
| **并购报告** | `merger_report/service.js` | 并购 deal 报告推送 |
| **Markdown 样式** | `styles/*.js` | 各推送类型的格式化模板 |

### 2.5 shared/ — 跨层通用能力

| 目录 | 关键文件 | 职责 |
|------|----------|------|
| `bus/` | `market_record.py`, `market_record.js`, `bus_contract.md` | **The Bus** — 标准化记录格式，定义跨层通信契约 |
| `config/` | `node_config.js`, `script_config.py` | 统一配置读取（YAML + 环境变量注入） |
| `paths/` | `node_paths.js`, `script_paths.py`, `tool_paths.py` | 路径解析（运行时文件、数据库、配置） |
| `runtime/` | `json_store.js`, `json_store.py`, `state_registry.js`, `state_registry.py` | JSON 文件持久化、运行时状态管理 |
| `time/` | `shanghai_time.js`, `shanghai_time.py` | 上海时区、交易时段检测、市场时间 |
| `logging/` | `logger.js`, `logger.py` | 统一日志 |
| `models/` | `service_result.js`, `service_result.py` | 标准成功/错误响应包装 |
| 根目录 | `market_service.py` | 跨市场工具（价格查询、配对匹配、搜索） |

### 2.6 tools/ — 部署与工具脚本

| 文件 | 职责 |
|------|------|
| `check_plugin_boundaries.py` | **架构 enforcement** — 检查跨插件非法依赖 |
| `check_constitution_sync.py` | 文档同步校验 |
| `rebuild_premium_db.py` | 溢价历史数据库维护 |
| `export_pair_pool.py` | 配对池导出 |
| `stock_price_history_db.py` | 股价历史数据库管理 |
| `premium_history_db.py` | 溢价历史数据库管理 |
| `fetch_convertible_bond.py` | 独立转债抓取脚本 |
| `fetch_dividend.py` | 独立股息抓取脚本 |
| `fetch_historical_premium.py` | 历史溢价抓取 |
| `fetch_merger_arbitrage.py` | 并购套利抓取 |
| `market_pairs.py` | 市场配对工具 |
| `sync_convertible_bond_stock_history.py` | 转债正股历史同步 |
| `cb_rights_issue_stock_history_db.py` | 抢权配售正股历史数据库 |
| `subscription_history_db.py` | 申购历史数据库 |
| `audit_ah_history_coverage.py` | AH 历史覆盖审计 |
| `render_mini_swe_task.py` | mini-SWE-agent 任务渲染 |
| `deploy/` | systemd 服务文件、nginx/Caddy 配置、自动部署脚本 |

### 2.7 docs/ — 项目文档

| 文件 | 职责 |
|------|------|
| `docs/UI_DESIGN.md` | UI 设计规范（Bloomberg 终端式金融界面） |
| `docs/RUNBOOK.md` | 运维手册（部署、验证、健康检查含义） |
| `docs/mini-swe-agent-guide.md` | mini-SWE-agent 使用教程 |

### 2.8 ui/ — React 前端（进行中）

| 文件 | 职责 |
|------|------|
| `src/App.jsx` | React 应用主组件 |
| `src/main.jsx` | 入口文件 |
| `src/styles.css` | 样式 |
| `index.html` | HTML 模板 |
| `package.json` | Vite + React 依赖 |

### 2.8 根目录关键文件

| 文件 | 职责 |
|------|------|
| `start_server.js` | **主入口**（3224 行）— Express 启动、服务注册、路由挂载、调度器启动 |
| `data_dispatch.py` | **数据调度 CLI** — 根据 action 调用对应 data_fetch + strategy 插件 |
| `start_server.js` | **主入口** — Express 启动、服务注册、路由挂载、调度器启动 |
| `config.yaml` | **唯一正式配置合同** — 所有业务参数、阈值、URL、开关 |
| `package.json` | Node 依赖与脚本 |
| `requirements.txt` | Python 依赖 |
| `tests/smoke_check.js` | 冒烟测试 |
| `shared/paths/db_paths.py` | 数据库路径配置 |

---

## 3. 文件速查表

按功能查询：

| 想找什么 | 文件位置 |
|----------|----------|
| 折价策略买入/卖出/监控推送逻辑 | `notification/alerts/event_alert_service.js` |
| 折价策略状态持久化 | `strategy/convertible_bond/discount_runtime_store.js` |
| 折价策略业务计算 | `strategy/convertible_bond/service.py` |
| 可转债数据抓取 | `data_fetch/convertible_bond/fetcher.py` |
| 可转债上游 API | `data_fetch/convertible_bond/source.py` |
| 抢权配售计算 | `strategy/cb_rights_issue/service.py` |
| 抢权配售数据抓取 | `data_fetch/cb_rights_issue/fetcher.py` |
| 抢权配售推送 | `notification/cb_rights_issue/service.js` |
| LOF 数据抓取 | `data_fetch/lof_arbitrage/fetcher.py` |
| LOF 推送 | `notification/lof_arbitrage/service.js` |
| AH 溢价计算 | `strategy/ah_premium/service.py` |
| AB 溢价计算 | `strategy/ab_premium/service.py` |
| 并购套利计算+AI 报告 | `strategy/merger/service.py` |
| 每日摘要推送组装 | `notification/summary/main_summary.js` |
| 推送调度器 | `notification/scheduler/wecom_scheduler.js` |
| 推送配置存储 | `notification/scheduler/push_config_store.js` |
| 模块推送配置 | `notification/scheduler/module_push_config_store.js` |
| WeCom 发送客户端 | `notification/wecom/client.js` |
| 市场行情路由 | `presentation/routes/market_routes.js` |
| 看板路由 | `presentation/routes/dashboard_routes.js` |
| 推送配置路由 | `presentation/routes/push_routes.js` |
| 看板概览数据 | `presentation/view_models/overview.js` |
| 统一配置读取 | `shared/config/node_config.js` / `script_config.py` |
| JSON 状态持久化 | `shared/runtime/json_store.js` / `json_store.py` |
| 上海时区/交易时段 | `shared/time/shanghai_time.js` / `shanghai_time.py` |
| The Bus 记录格式 | `shared/bus/market_record.js` / `market_record.py` |
| 架构边界检查 | `tools/check_plugin_boundaries.py` |
| 自动部署脚本 | `tools/deploy/update_from_github.sh` |
| 服务器启动 | `start_server.js` |
| 数据调度 CLI | `data_dispatch.py` |

---

## 4. 数据流速查

以 `/api/market/ah` 请求为例：

```
HTTP GET /api/market/ah
    │
    ▼
presentation/routes/market_routes.js
    │
    ├──► 检查内存缓存 → 有则直接返回
    │
    └──► 缓存过期 → 调用 data_dispatch.py ah
              │
              ▼
         data_fetch/ah_premium/fetcher.py
              │
              ├──► source.py 调腾讯行情 API
              │
              └──► normalizer.py 转为 Bus 记录
                        │
                        ▼
                   strategy/ah_premium/service.py
                        │
                        ├──► 计算溢价率
                        ├──► 查历史百分位（premium_history.db）
                        └──► 排序
                                  │
                                  ▼
                             返回 JSON
                                  │
                                  ▼
                         写入内存缓存 + JSON 文件
                                  │
                                  ▼
                         返回客户端
```

---

## 5. 运行态地图

`runtime_data/shared/` 下的关键文件：

| 文件 | 内容 | 谁读写 |
|------|------|--------|
| `market_cache_*.json` | 各模块市场数据缓存 | data_dispatch / start_server |
| `cb_arb_aux_cache.json` | 转债辅助缓存 | convertible_bond fetcher |
| `cb_discount_strategy_state.json` | 折价策略运行态（监控名单、买卖区状态） | notification/alerts |
| `cb_rights_issue_state.json` | 抢权配售状态 | strategy/cb_rights_issue |
| `lof_arbitrage_state.json` | LOF 套利状态 | strategy/lof_arbitrage |
| `custom_monitors.json` | 用户自定义监控组合 | data_fetch/custom_monitor |
| `dividend_portfolio.json` | 股息跟踪组合 | strategy/dividend |
| `merger_company_reports.json` | 并购公司报告 | strategy/merger |
| `push_config.json` | 主推送配置 | notification/scheduler |
| `push_runtime_state.json` | 推送运行态 | notification/scheduler |
| `cb_arbitrage_push_config.json` | CB 套利推送配置 | notification/cb_arbitrage |
| `*_push_runtime.json` | 各模块推送运行态 | notification/* |
| `market_refresh_state.json` | 市场刷新状态 | start_server |
| `*.db` | SQLite 数据库（股价历史、溢价历史、配对池） | tools/ 各脚本 |

**规则**：运行时 JSON 属于环境状态，不提交 Git，部署时保留不被覆盖。

---

## 6. 配置速查

`config.yaml` 关键段落：

| 段落 | 控制内容 |
|------|----------|
| `app.*` | 服务端口（5001）、host、超时、时区、Python 二进制路径 |
| `deployment.*` | 公网 URL、反向代理类型、systemd 服务名 |
| `storage.*` | 运行时数据目录、profile 路径、运行时 JSON 文件名 |
| `bus.*` | Bus 模式版本、必填字段、允许状态 |
| `plugins.*` | 各插件启用/禁用开关 |
| `data_fetch.plugins.*` | 各插件刷新间隔、超时、数据源 URL、API key、历史保留期 |
| `strategy.*` | 各插件排名指标、阈值、推送分类、AI prompt |
| `presentation.*` | API 前缀、看板主题、自动刷新间隔、表格尺寸、模块注释 |
| `notification.*` | Webhook URL、推送时间、启用模块、摘要 Top-N 数量 |

---

## 7. 验证命令

```bash
# 冒烟测试
npm run check

# 架构边界检查
python3 tools/check_plugin_boundaries.py

# 健康检查（需服务运行）
npm run check:health

# 测试数据管道
python data_dispatch.py exchange-rate
python data_dispatch.py ah
python data_dispatch.py ab
python data_dispatch.py cb-arb
python data_dispatch.py ipo
python data_dispatch.py dividend

# 构建 React UI
npm run ui:build
```

---

## 8. ELODIE 工作流文件

| 文件 | 职责 |
|------|------|
| `CLAUDE.md` | AI 规则入口（读取顺序、任务规则、宪法）— **用户所有，AI 不可修改** |
| `INDEX.md` | 本文件 — 项目架构+文件索引 — **AI 维护** |
| `README.md` | 项目简介 |
| `specs/spec.md` | 项目级规格索引（模块地图、全局规则） |
| `specs/*.md` | 模块级正式规格（业务规则、计算合同、接口合同） |
| `missions/MMDD-名称/` | 任务闭环（spec.md + plan.md） |
| `MEMORY.md` | 交接记忆（最近 50 条） |
| `config/config.yaml` | 工作流配置（mission_retention、memory_retention） |
| `templates/` | 任务/规格/子代理模板 |

**AI 读取顺序**：`CLAUDE.md` → `INDEX.md` → `README.md` → `specs/spec.md` → 相关 `specs/*.md` → `config/config.yaml` → `MEMORY.md`
