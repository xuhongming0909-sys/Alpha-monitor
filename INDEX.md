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
┌──────────────────────────────────────────────────────────┐
│  ui/              API 路由与页面渲染                      │
│  ├─ routes/       /api/market/* /api/dashboard/*        │
│  ├─ view_models/  数据整形                               │
│  └─ templates/    HTML 模板                             │
└──────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  strategy/          业务计算层                            │
│  ├─ ah_premium/     AH 溢价排名                          │
│  ├─ convertible_bond/ 转债套利（双低/折价/回售）        │
│  ├─ lof_arbitrage/  LOF/QDII 套利                       │
│  └─ ... (共 10 个插件)                                   │
└──────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  "The Bus" — 标准化记录格式                              │
│  shared/bus/market_record.{py,js}                       │
└──────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  data_fetch/          数据抓取层                          │
│  ├─ ah_premium/       腾讯行情（实时股价+汇率）           │
│  ├─ convertible_bond/ 集思录+东财（转债行情+财务）       │
│  ├─ lof_arbitrage/    集思录（LOF/QDII 溢价率）         │
│  └─ ... (共 11 个插件)                                   │
└──────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  上游数据源                                                │
│  腾讯行情 / 集思录 / AkShare / 巨潮资讯 / 东方财富       │
└──────────────────────────────────────────────────────────┘
```

**分层规则**：
- `data_fetch/` 只做抓取+标准化，不写业务逻辑
- `strategy/` 只做计算+规则判断，不直接调上游 API
- `ui/` 只做 API 整形+展示，不做计算
- `notification/` 只做推送+调度，不碰数据抓取
- 跨层通信只能通过 The Bus 标准化记录
- 跨插件禁止直接 import（由 `tools/check_plugin_boundaries.py` 强制检查）

---

## 2. 目录索引

### 2.1 data_fetch/ — 数据抓取层（11 个插件，从上游 API 拉数据并标准化为 Bus 记录）

每个插件标准结构：`fetcher.py`（调度）+ `source.py`（上游 API）+ `normalizer.py`（标准化为 Bus 记录）。部分插件有 `history_source.py`/`history_sync.py`（历史数据同步）。

| 插件 | 数据源 | 关键文件 | 输出 |
|------|--------|----------|------|
| `ah_premium/` | 腾讯行情 | `fetcher.py`, `source.py`, `normalizer.py` | AH 股溢价快照 |
| `ab_premium/` | 腾讯行情 | `fetcher.py`, `source.py`, `normalizer.py` | AB 股溢价快照 |
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

### 2.2 strategy/ — 业务计算层（10 个插件，执行计算规则、排名、筛选、策略判定）

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

### 2.3 ui/ — API 与展示层（Express 路由、视图模型、看板模板）

| 文件 | 职责 | 服务端点 |
|------|------|----------|
| `routes/market_routes.js` | 市场行情路由 | `/api/market/ah`, `/api/market/ab`, `/api/market/convertible-bond-arbitrage`, `/api/market/lof-arbitrage`, `/api/market/merger`, `/api/market/event-arbitrage`, `/api/market/cb-rights-issue`, `/api/market/ipo`, `/api/market/convertible-bonds`, `/api/market/exchange-rate` |
| `routes/dashboard_routes.js` | 看板路由 | `/api/dashboard/ui-config`, `/api/dashboard/resource-status`, `/api/dashboard/overview`, `/api/monitors`, `/api/dividend?action=*` |
| `routes/push_routes.js` | 推送配置路由 | `/api/push/config`, `/api/push/cb-rights-issue-config`, `/api/push/lof-arbitrage-config`, `/api/push/wecom` |
| `view_models/overview.js` | 看板概览数据组装 | 被 dashboard_routes 调用 |
| `view_models/push_payload.js` | 推送配置响应格式 | 被 push_routes 调用 |
| `dashboard/dashboard_page.js` | 旧看板页面逻辑 | legacy 页面渲染 |
| `templates/dashboard_template.html` | 旧看板 HTML 模板 | 含内联 CSS/JS，暗色金融终端主题 |

### 2.4 notification/ — 推送与调度层（企业微信、摘要组装、告警推送）

| 组件 | 关键文件 | 职责 |
|------|----------|------|
| **WeCom 客户端** | `wecom/client.js` | 发送 Markdown 到企业微信 Webhook |
| **调度器** | `scheduler/wecom_scheduler.js` | 定时推送调度（60s tick） |
| **推送配置** | `scheduler/push_config_store.js`, `push_runtime_store.js` | 运行时推送配置与状态 |
| **模块配置** | `scheduler/module_push_config_store.js`, `module_push_runtime_store.js` | 各模块（CB/LOF/抢权配售）独立推送配置 |
| **摘要服务** | `summary/main_summary.js` | 聚合所有模块生成每日摘要 Markdown |
| **折价策略提醒** | `alerts/event_alert_service.js` | 实时折价买入/卖出/监控名单推送 |
| **CB 套利推送** | `cb_arbitrage/service.js` | 转债套利独立推送逻辑 |
| **抢权配售推送** | `cb_rights_issue/service.js` | 抢权配售独立推送逻辑 |
| **LOF 套利推送** | `lof_arbitrage/service.js` | LOF 套利独立推送逻辑（定时+即时） |
| **并购报告** | `merger_report/service.js` | 并购 deal 报告推送 |
| **Markdown 样式** | `styles/*.js` | 各推送类型的格式化模板 |

### 2.5 shared/ — 跨层通用能力（配置、路径、时区、日志、Bus 记录格式、运行时状态）

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

### 2.6 scripts/ — 运维与数据管理脚本（历史库重建、配对导出、健康检查等）

| 文件 | 职责 |
|------|------|
| `add_ai_summary.py` | 批量添加 AI-SUMMARY 注释 |
| `audit_ah_history_coverage.py` | AH 历史覆盖审计 |
| `cb_rights_issue_stock_history_db.py` | 抢权配售正股历史数据库 |
| `check_plugin_boundaries.py` | **架构 enforcement** — 检查跨插件非法依赖 |
| `check_root_cleanliness.py` | 根目录清洁检查 |
| `check_health.ps1` | 健康检查（PowerShell） |
| `export_pair_pool.py` | 配对池导出 |
| `fetch_historical_premium.py` | 历史溢价抓取 |
| `fetch_merger_arbitrage.py` | 并购套利抓取 |
| `market_pairs.py` | 市场配对工具 |
| `premium_history_db.py` | 溢价历史数据库管理 |
| `rebuild_premium_db.py` | 溢价历史数据库重建 |
| `render_mini_swe_task.py` | mini-SWE-agent 任务渲染 |
| `stock_price_history_db.py` | 股价历史数据库管理 |
| `subscription_history_db.py` | 申购历史数据库管理 |
| `sync_convertible_bond_stock_history.py` | 转债正股历史同步 |

### 2.7 deploy/ — 部署配置

| 文件 | 职责 |
|------|------|
| `alpha-monitor.service` | systemd 服务文件 |
| `Caddyfile`, `nginx-*.conf` | Web 服务器配置 |
| `install_*.sh` | 安装脚本（Caddy/Nginx/systemd） |
| `update_*.sh` | 自动更新脚本 |
| `server_doctor.sh` | 服务器健康检查 |
| `sync_remote_env_from_profile.py` | 同步远程环境变量 |

### 2.7 docs/ — 项目文档（UI 设计规范、运维手册、mini-SWE-agent 使用指南）

### 2.8 ui/ — React 前端（进行中，Vite + React 重写 UI）

| 文件 | 职责 |
|------|------|
| `src/App.jsx` | React 应用主组件 |
| `src/main.jsx` | 入口文件 |
| `src/styles.css` | 样式 |
| `index.html` | HTML 模板 |
| `package.json` | Vite + React 依赖 |

### 2.9 根目录关键文件（入口脚本、配置合同、冒烟测试）

| 文件 | 职责 |
|------|------|
| `start_server.js` | **主入口**（3224 行）— Express 启动、服务注册、路由挂载、调度器启动 |
| `data_dispatch.py` | **数据调度 CLI** — 根据 action 调用对应 data_fetch + strategy 插件 |
| `config.yaml` | **唯一正式配置合同** — 所有业务参数、阈值、URL、开关 |
| `package.json` | Node 依赖与脚本 |
| `requirements.txt` | Python 依赖 |
| `tests/smoke_check.js` | 冒烟测试 |
| `shared/paths/db_paths.py` | 数据库路径配置 |

---

## 3. 文件速查表（按功能搜索源码位置）

按功能查询：

| 想找什么 | 文件位置 |
|----------|----------|
| 折价策略买入/卖出/监控推送逻辑 | `notification/alerts/event_alert_service.js` |
| 折价策略状态持久化 | `strategy/convertible_bond/discount_runtime_store.js` |
| 折价策略业务计算 | `strategy/convertible_bond/service.py` |
| 转债套利数据抓取 | `data_fetch/convertible_bond/fetcher.py` |
| 转债套利上游 API | `data_fetch/convertible_bond/source.py` |
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
| 市场行情路由 | `ui/routes/market_routes.js` |
| 看板路由 | `ui/routes/dashboard_routes.js` |
| 推送配置路由 | `ui/routes/push_routes.js` |
| 看板概览数据 | `ui/view_models/overview.js` |
| 统一配置读取 | `shared/config/node_config.js` / `script_config.py` |
| JSON 状态持久化 | `shared/runtime/json_store.js` / `json_store.py` |
| 上海时区/交易时段 | `shared/time/shanghai_time.js` / `shanghai_time.py` |
| The Bus 记录格式 | `shared/bus/market_record.js` / `market_record.py` |
| 架构边界检查 | `tools/check_plugin_boundaries.py` |
| 自动部署脚本 | `tools/deploy/update_from_github.sh` |
| 服务器启动 | `start_server.js` |
| 数据调度 CLI | `data_dispatch.py` |

---

## 4. 数据流速查（从 HTTP 请求到数据返回的完整链路）

以 `/api/market/ah` 请求为例：

```
HTTP GET /api/market/ah
    │
    ▼
ui/routes/market_routes.js
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

## 5. 运行态地图（runtime_data/ 下运行时状态文件一览）

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

## 6. 配置速查（config.yaml 各段落功能速查）

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

## 7. 验证命令（冒烟测试、架构检查、数据管道测试）

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

## 8. ELODIE 工作流文件（AI 工作流规范文件索引）

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

---

## 9. 代码文件规范（文件大小限制、AI-SUMMARY 注释规范）

### 9.1 文件大小限制

> **硬规则**：任何代码文件（`.py`、`.js`、`.jsx`）不得超过 **1000 行**。
>
> **为什么**：超过 1000 行的文件难以在 AI 上下文窗口中完整加载，导致检索困难、修改易出错、Review 成本指数级上升。
>
> **拆分原则**：
> - 按功能职责拆分（如 `source.py` → `source.py` + `parser.py` + `cache.py`）
> - 按 API 端点拆分（如 `market_routes.js` → `ah_routes.js` + `cb_routes.js` + `...`）
> - 按数据层拆分（如 `service.py` → `calculator.py` + `formatter.py` + `validator.py`）
> - 拆分后每份新文件必须有独立的 `AI-SUMMARY` 和 INDEX.md 登记
>
> **例外**：自动生成的模板/常量文件（如大型 HTML 模板、JSON 数据文件）可豁免，但应在文件名中标注（如 `.template.html`、`.data.json`）。

### 9.2 AI-SUMMARY 注释规范

> **硬规则**：每份核心代码文件顶部必须有 `AI-SUMMARY:` 注释。
>
> **格式**：
> ```python
> # AI-SUMMARY: [一句话职责描述]
> # 对应 INDEX.md §9.3 文件摘要索引
> ```
> ```javascript
> // AI-SUMMARY: [一句话职责描述]
> // 对应 INDEX.md §9.3 文件摘要索引
> ```
>
> **要求**：
> - 一句话，不超过 30 字
> - 说明"这个文件做什么"，不是"这个文件有什么函数"
> - 必须与 INDEX.md 表格中的描述完全一致
>
> **维护规则**：
> 1. 修改文件职责或结构后，必须同步更新文件顶部 `AI-SUMMARY` 和 INDEX.md 表格。
> 2. 新增核心文件时，必须写入 `AI-SUMMARY` 并在 INDEX.md 登记。
> 3. 删除核心文件时，必须同步删除 INDEX.md 对应行和文件中的注释。
> 4. 拆分文件时，旧文件的 `AI-SUMMARY` 和 INDEX.md 条目需更新或删除，新文件必须登记。

---

## 9.3 文件摘要索引

### 9.1 根目录与入口

| 文件 | 职责摘要 |
|------|----------|
| `server_config_loader.js` | 服务器配置加载：端口/路径/策略/超时等配置读取 |
| `start_server.js` | Express 主入口：启动服务、挂载路由、注册调度器、管理运行时状态 |
| `data_dispatch.py` | CLI 数据调度器：根据 action 调用对应 data_fetch 抓取和 strategy 计算 |
| `config.yaml` | 业务配置合同：所有参数、阈值、URL、开关的单一来源 |

### 9.2 data_fetch/ — 数据抓取层

| 文件 | 职责摘要 |
|------|----------|
| `data_fetch/ah_premium/fetcher.py` | AH 溢价抓取调度：调用腾讯行情 API 并标准化为 Bus 记录 |
| `data_fetch/ah_premium/source.py` | AH 溢价上游 API：腾讯行情 + 配对库 + 历史数据库 |
| `data_fetch/ah_premium/normalizer.py` | AH 溢价数据标准化：原始行情转为 Bus 标准化记录 |
| `data_fetch/ab_premium/fetcher.py` | AB 溢价抓取调度：调用腾讯行情 API 并标准化为 Bus 记录 |
| `data_fetch/ab_premium/source.py` | AB 溢价上游 API：腾讯行情 + 配对库 + 历史数据库 |
| `data_fetch/ab_premium/normalizer.py` | AB 溢价数据标准化：原始行情转为 Bus 标准化记录 |
| `data_fetch/convertible_bond/fetcher.py` | 转债套利抓取调度：调用集思录/东方财富 API |
| `data_fetch/convertible_bond/cb_metrics.py` | 转债套利指标计算：波动率/ATR/理论定价/纯债价值/期权价值 |
| `data_fetch/convertible_bond/source.py` | 转债套利上游 API：集思录实时行情 + 东方财富财务数据 |
| `data_fetch/convertible_bond/normalizer.py` | 转债套利数据标准化：含理论定价的 Bus 记录生成 |
| `data_fetch/lof_arbitrage/fetcher.py` | LOF 套利抓取调度：调用集思录 API |
| `data_fetch/lof_arbitrage/source.py` | LOF 套利上游 API：集思录 LOF/QDII 实时数据 |
| `data_fetch/merger/fetcher.py` | 并购数据抓取调度：调用巨潮公告 API |
| `data_fetch/merger/source.py` | 并购公告 API：巨潮资讯公告搜索与解析 |
| `data_fetch/dividend/fetcher.py` | 股息抓取调度：调用 AkShare/巨潮 API |
| `data_fetch/dividend/source.py` | 股息上游 API：AkShare CNINFO + 腾讯行情 |
| `data_fetch/subscription/fetcher.py` | 申购抓取调度：IPO + 转债申购日历 |
| `data_fetch/exchange_rate/fetcher.py` | 汇率抓取调度：调用腾讯汇率 API |
| `data_fetch/custom_monitor/input_reader.py` | 自定义监控输入读取：从运行态 JSON 读取用户组合 |
| `data_fetch/event_arbitrage/fetcher.py` | 事件套利抓取调度：调用集思录事件 API |
| `data_fetch/cb_rights_issue/fetcher.py` | 抢权配售抓取调度：调用集思录预案 API |

### 9.3 strategy/ — 业务计算层

| 文件 | 职责摘要 |
|------|----------|
| `strategy/ah_premium/service.py` | AH 溢价业务计算：溢价率排名、历史百分位 |
| `strategy/ah_premium/service.js` | AH 溢价 Node 适配器：Python 计算结果转为 API 响应 |
| `strategy/ab_premium/service.py` | AB 溢价业务计算：AB 股溢价率排名 |
| `strategy/ab_premium/service.js` | AB 溢价 Node 适配器：Python 计算结果转为 API 响应 |
| `strategy/convertible_bond/service.py` | 转债套利业务计算：双低策略、理论收益率、回售套利 |
| `strategy/convertible_bond/service.js` | 转债套利 Node 适配器：计算结果格式化、折价策略状态 |
| `strategy/merger/service.py` | 并购套利业务计算：Deal 分析、AI 报告生成 |
| `strategy/merger/service.js` | 并购套利 Node 适配器：报告生成调度 |
| `strategy/lof_arbitrage/service.py` | LOF 套利业务计算：溢价率排名与过滤 |
| `strategy/custom_monitor/service.py` | 自定义监控业务计算：组合收益率、对价计算 |
| `strategy/dividend/service.py` | 股息业务计算：登记日跟踪、股息率计算 |
| `strategy/subscription/service.py` | 申购业务计算：申购事件跟踪与状态管理 |
| `strategy/event_arbitrage/service.py` | 事件套利业务计算：事件匹配与过滤规则 |
| `strategy/cb_rights_issue/service.py` | 抢权配售业务计算：预期收益、阶段判定、入池判断 |

### 9.4 ui/ — API 与展示层

| 文件 | 职责摘要 |
|------|----------|
| `ui/routes/market_routes.js` | 市场行情 API 路由：/api/market/* 端点定义 |
| `ui/routes/dashboard_routes.js` | 看板 API 路由：/api/dashboard/* 端点定义 |
| `ui/routes/push_routes.js` | 推送配置 API 路由：/api/push/* 端点定义 |
| `ui/view_models/overview.js` | 看板概览数据组装：聚合各模块数据为统一视图 |
| `ui/view_models/push_payload.js` | 推送配置响应格式：推送配置数据结构整形 |
| `ui/dashboard/constants.js` | 看板 UI 常量：端点、Tab 序列、表格配置、样式默认值 |
| `ui/dashboard/dashboard_page.js` | 旧看板页面逻辑：HTML 看板渲染与交互 |
| `ui/templates/dashboard_template.html` | 旧看板 HTML 模板：含内联 CSS/JS |

### 9.5 notification/ — 推送与调度层

| 文件 | 职责摘要 |
|------|----------|
| `notification/wecom/client.js` | 企业微信客户端：发送 Markdown 到 Webhook |
| `notification/scheduler/wecom_scheduler.js` | 推送调度器：定时 tick 触发各模块推送 |
| `notification/scheduler/push_config_store.js` | 推送配置存储：主推送配置读写 |
| `notification/scheduler/push_runtime_store.js` | 推送运行时存储：推送状态与历史 |
| `notification/summary/main_summary.js` | 每日摘要组装：聚合所有模块生成推送 Markdown |
| `notification/alerts/event_alert_service.js` | 事件告警服务：折价策略买入/卖出/监控实时推送 |
| `notification/cb_arbitrage/service.js` | 转债套利推送：独立推送逻辑与格式化 |
| `notification/cb_rights_issue/service.js` | 抢权配售推送：独立推送逻辑与格式化 |
| `notification/lof_arbitrage/service.js` | LOF 套利推送：独立推送逻辑与格式化 |
| `notification/merger_report/service.js` | 并购报告推送：DeepSeek AI 报告生成与推送 |
| `notification/styles/markdown_style.js` | 推送 Markdown 样式：通用格式化模板 |

### 9.6 shared/ — 跨层通用能力

| 文件 | 职责摘要 |
|------|----------|
| `shared/config/node_config.js` | Node 配置读取器：YAML 解析 + 环境变量/Secrets 注入 |
| `shared/config/script_config.py` | Python 配置读取器：YAML 解析 + 环境变量/Secrets 注入 |
| `shared/bus/market_record.js` | Bus 标准化记录（JS）：跨层通信数据结构 |
| `shared/bus/market_record.py` | Bus 标准化记录（Python）：跨层通信数据结构 |
| `shared/runtime/json_store.js` | JSON 持久化（JS）：运行时状态读写 |
| `shared/runtime/json_store.py` | JSON 持久化（Python）：运行时状态读写 |
| `shared/runtime/state_registry.js` | 状态注册表（JS）：运行时文件统一管理 |
| `shared/runtime/state_registry.py` | 状态注册表（Python）：运行时文件统一管理 |
| `shared/time/shanghai_time.js` | 上海时区（JS）：交易时段检测、市场时间 |
| `shared/time/shanghai_time.py` | 上海时区（Python）：交易时段检测、市场时间 |
| `shared/paths/node_paths.js` | 路径解析（JS）：运行时目录、数据库路径 |
| `shared/paths/script_paths.py` | 路径解析（Python）：运行时目录、数据库路径 |
| `shared/models/service_result.js` | 标准响应包装（JS）：成功/错误响应格式 |
| `shared/models/service_result.py` | 标准响应包装（Python）：成功/错误响应格式 |
| `shared/market_service.py` | 跨市场工具：价格查询、配对匹配、股票搜索 |
| `shared/utils/ranking.js` | 通用排序工具：按字段升降序取 Top N |

### 9.7 scripts/ — 脚本

| 文件 | 职责摘要 |
|------|----------|
| `scripts/add_ai_summary.py` | 批量添加 AI-SUMMARY 注释 |
| `scripts/audit_ah_history_coverage.py` | AH 历史覆盖审计 |
| `scripts/check_plugin_boundaries.py` | 架构边界检查：验证插件间无非法依赖 |
| `scripts/check_root_cleanliness.py` | 根目录清洁检查 |
| `scripts/rebuild_premium_db.py` | 溢价历史数据库重建：AH/AB 溢价历史维护 |
| `scripts/stock_price_history_db.py` | 股价历史数据库：正股 K 线数据管理 |
| `scripts/premium_history_db.py` | 溢价历史数据库：溢价率历史数据管理 |
| `scripts/export_pair_pool.py` | 配对池导出：AH/AB 配对表生成 |

### 9.8 tests/ — 测试

| 文件 | 职责摘要 |
|------|----------|
| `tests/smoke_check.js` | 冒烟测试：验证服务首页和 health 端点可达 |
