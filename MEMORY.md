# Memory

**Retention**: max 50 entries. Oldest auto-deleted when exceeded.

**Record only**: decisions, meaningful actions, verification results, memorable failures, next steps.
**Do not**: dump full conversations.

## Entries
### 2026-05-28 | LOF文档同步

### 2026-05-28 | LOF A/B类统一清理

- **Decision**: 所有14只基金都是B类(T10持仓法)，A类代码全是死代码，统一清理
- **Action**: calc.py: calc_b_iopv→calc_iopv，删除calc_a_iopv
- **Action**: backtest_v2.py: backtest_b→backtest_fund，删除backtest_a
- **Action**: service.py: 删除A类分支，统一calc_iopv
- **Action**: source.py: 删除ETF相关函数和estimation字段
- **Action**: 删除backtest.py/backtest_t10.py/classifier.py
- **Action**: config.yaml: 删除全部estimation字段
- **Action**: holdings_updater.py: 修复estimation=="B"过滤bug
- **Formula**: IOPV = NAV * (1 + stock_ratio/100 * weighted_ret) * fx_ratio
- **Result**: 删除3文件，5文件重写，代码精简~200行


- **Decision**: 代码领先于文档，全面同步specs/INDEX/calc与实际代码
- **Action**: 修复specs/lof-arbitrage.md（维护脚本路径、文件结构、数据源表）
- **Action**: INDEX.md补充backtest_v2/classifier/source/normalizer条目，更新etf_updater描述
- **Action**: calc.py docstring从iopv_calculator改为实际backtest文件引用
- **Action**: MEMORY.md清理7处重复的LOF数据库条目为1处
- **Result**: 6文件修改，74行增95行删，提交3726bb5



### 2026-05-27 | 40交易日回测+汇率修正

- **Decision**: 更新回测规范：40交易日、必须含汇率、R²<0.8=不合格
- **Action**: 写入specs/lof-arbitrage.md section 9，回测脚本使用akshare stock_us_daily+currency_boc_safe
- **Result**: OK 12只(52.2%), WARN 4只, BAD 7只
- **Key Finding**: 汇率修正后效果显著，美国消费/华宝油气/纳指100达到OK标准
- **Remaining**: 原油USO/GSG商品/FOF仍不可拟合
- **File**: missions/0527-fund-backtest/report.md


### 2026-05-27 | LOF回测完成-新浪API

- **Decision**: 使用akshare stock_us_daily(新浪API)替代东方财富push2his，解决限流问题
- **Action**: 运行A类回测，23只基金，95个交易日(2025-12-22~2026-05-22)
- **Result**: OK 1只(501300美元债AGG)，WARN 4只，BAD 18只
- **Key Finding**: 误差主要来源：汇率偏差、原油USO不可拟合、FOF持仓不透明
- **Recommendation**: 1)禁用6只BAD原油/商品基金 2)IOPV计算加入汇率修正
- **File**: missions/0527-fund-backtest/report.md

### 2026-05-27 | LOF回测链+估值链清理

- **Decision**: A类IOPV加入ETF涨幅因子，B类加入持仓加权收益率
- **Fix**: fetcher.py 新增 _fetch_etf_changes() 东财+腾讯双源，输出 etfChange + holdingsPrevClose
- **Fix**: service.py _calc_b 从简化版(NAV*汇率)恢复为完整持仓加权公式
- **Fix**: service.py _calc_b stockPosition 兜底从 90.0 改为 None(仓位缺失)
- **Fix**: market_service.py get_quotes 增加 prev_close 字段(parts[4])
- **Fix**: 回测加载只读 a_results.json + b_results.json(字段名匹配: maxErr, samplePeriod)
- **Action**: 删除 backtest.py，新建 backtest_a.py + backtest_b.py，字段对齐 service.py
- **Action**: 清理 runtime_data/backtest/ 10个无用文件，只保留 a/b_results.json
- **Action**: nav_updater.py 从 config 读取基金列表
- **Risk**: 东财美股API(107)不稳定，腾讯fallback格式需服务器验证
- **Mission**: missions/0527-lof-backtest-cleanup/
### 2026-05-27 | LOF全链修复

- **Decision**: 统一LOF管道，config.yaml为基金列表唯一来源，修复A类估值缺少ETF涨幅因子
- **Action**: 9个文件修改，5个冗余脚本归档
- **Fix**: service.py回测加载路径错误→修正为lof_all_r2_results.json
- **Fix**: A类IOPV从简化版(NAV*汇率)恢复为完整公式(NAV*(1+etf_ret)*汇率)
- **Fix**: fetcher.py新增_fetch_etf_changes()东财+腾讯双源
- **Action**: config.yaml daily_incremental_sync=true，start_server.js dailySync接入lof-db-sync
- **Action**: 冗余回测脚本归档至archive/lof_backtest_deprecated/
- **Risk**: ETF腾讯行情格式需服务器验证
- **Mission**: missions/0527-lof-pipeline-fix/


### 2026-05-27 | LOF数据库+回测架构

- **Decision**: 建立SQLite数据库存储IOPV计算和回测数据，消除硬编码和默认值
- **Action**: 创建 data_fetch/lof_db/ 模块（schema/updater/nav/etf/fx/holdings）
- **Action**: 创建 strategy/lof_iopv/backtest.py 回测脚本，从数据库读取
- **Action**: 24只基金分为A类(19只指数法)/B类(5只T10法)
- **Action**: 更新 specs/lof-arbitrage.md 为完整规格文档
- **Verification**: 根目录清洁检查通过，AI-SUMMARY覆盖检查通过
- **Backtest**: 13只可回测，1只OK(164701)，2只WARN，10只BAD
- **Risk**: 东方财富美股API当前不可用，ETF数据只有8个标的
- **Mission**: missions/0527-lof-database/
### 2026-05-06 | React 手机端改回密集行表

- **Decision**: 用户不接受大卡片，React 主展示形态从卡片流改为密集行表；保留 7 标签和统一手机端导航
- **Action**: 更新 `specs/spec.md`、`specs/react-terminal-ui.md`、`specs/custom-monitor.md`，正式口径改为“一标的一行，横向字段流，窄屏可横向滚动”
- **Action**: 改造 `cardHelpers.jsx`、`cardListHelpers.jsx`、`styles.css`，把公共壳从 `dense-card` 调整为 `dense-row`
- **Action**: 同步更新 `INDEX.md` 与 UI 测试断言
- **Verification**: `npm run ui:build`、全部 `tests/ui_*.test.js`、`npm run check:boundaries`、`node tests/root_cleanliness.test.js`、`node tests/ai_summary_coverage.test.js` 通过
- **Next**: 推送 GitHub 并部署服务器，确认线上手机端已切到密集行表

### 2026-05-06 | React 改回旧网页端表格风格

- **Decision**: 用户认为密集行表仍然过于复杂，React 内容区改为尽量还原旧网页端的干净清爽表格风格
- **Action**: 新增 `ui/src/components/SimpleDataTable.jsx`，将转债、AH、AB、LOF、打新、抢权配售、自定义监控切换为简洁模块表格
- **Action**: 概览由卡片块改回轻量列表样式
- **Action**: 更新 `specs/spec.md`、`specs/react-terminal-ui.md`、`INDEX.md`、相关 UI 测试
- **Verification**: `npm run ui:build`、全部 `tests/ui_*.test.js`、`npm run check:boundaries`、`node tests/root_cleanliness.test.js`、`node tests/ai_summary_coverage.test.js` 通过
- **Next**: 推送 GitHub 并部署服务器，确认线上风格接近原网页端

### 2026-05-06 | React 手机端统一化重构

- **Decision**: 全设备只保留手机端单列密集 UI；移除 React 上方导航、分红提醒、事件套利、推送设置
- **Action**: `App.jsx` 从 2600+ 行收敛到 686 行，重写为真实接口加载、概览摘要流、7 标签接线
- **Action**: 底部导航改为两行 7 标签：概览/转债/AH/AB/LOF/打新/监控
- **Action**: 新增/改造密集卡片：AB、打新、自定义监控、抢权配售、转债、AH、LOF
- **Action**: 概览改为今日打新、配售登记、折价套利、小额刚兑、理论折价、AH/AB 机会、自定义监控
- **Action**: 更新 `specs/`、`INDEX.md`、UI 测试、根目录清洁测试白名单
- **Verification**: `npm run ui:build`、全部 `tests/ui_*.test.js`、`npm run check:boundaries`、AI-SUMMARY、root cleanliness、线上 smoke 通过
- **Risk**: `tests/convertible_discount.test.js` 仍有历史失败，未纳入本轮 UI 改造
- **Mission**: `missions/0506-mobile-unify-ui/`

### 2026-05-06 | 部署最新版本到服务器

- **Decision**: 先把服务器对齐当前最新提交，确保用户能立刻看到最新页面
- **Action**: 服务器执行 `git pull`、`cd ui && npm run build`、`sudo systemctl restart alpha-monitor`
- **Verification**: 公网 `/api/health` 正常，`ui/dist` 新资源 `index-DAsT1b9e.js` / `index-DfyVk25X.css` 仍在使用
- **Action**: 服务器当前分支 `workflow-elodie` 已改为跟踪 `origin/main`
- **Risk**: 服务器工作树有未跟踪 `tools/` 文件，暂不能直接切到 `main`
- **Mission**: `missions/0506-deploy-latest/`

### 2026-05-06 | 全局移动端化（手机优先，所有设备统一）

- **Decision**: 用户主要用手机看网页，要求所有设备（手机/电脑/平板）统一显示移动端界面，废弃桌面端大表格
- **Action**: `styles.css` 改为 Mobile-First — 默认无 1920px 锁死、无 1800px 表格、垂直堆叠布局
- **Action**: 底部导航 `BottomNav` 全局显示，不再依赖屏幕宽度
- **Action**: 新增 `ui/src/components/ConvertibleCardList.jsx` — 转债套利全局卡片视图
- **Action**: 新增 `ui/src/components/AhCardList.jsx` — AH溢价全局卡片视图
- **Action**: 新增 `ui/src/components/LofCardList.jsx` — LOF套利全局卡片视图
- **Fix**: `App.jsx` return 缺少 Fragment 包裹导致 vite build 失败，已修复 `<></>`
- **Deploy**: GitHub push 因网络超时失败（临时），后恢复；服务器通过 expect SSH + 密码部署成功
- **Server**: 43.139.35.190, ubuntu/DellG77588, app_dir: /home/ubuntu/Alpha monitor, systemd: alpha-monitor
- **Verification**: 服务已重启，新资源文件 `index-DAsT1b9e.js` + `index-DfyVk25X.css` 已上线
- **Remaining**: AB溢价、打新/申购、自定义监控、分红提醒、抢权配售、事件套利仍为表格（未卡片化）
- **Mission**: `missions/0506-mobile-adaptation/`

### 2026-05-05 | Server Profile 恢复与 CLI 配置

- **Decision**: 用户要求恢复 SSH 服务器配置文件，并统一放到 config/ 目录
- **Action**: 从 `archive/ops/server_profile.local.yaml` 恢复备份
- **Action**: 移动到 `config/server_profile.local.yaml`，删除 `ops/` 空目录
- **Action**: 更新 `deploy/sync_remote_env_from_profile.py` 中 `PROFILE_PATH` 指向 `config/`
- **Action**: 更新 `.gitignore` 忽略 `config/server_profile.local.yaml`
- **Action**: 修改 `~/.kimi/config.toml` — `default_yolo=true`, `default_caveman=true`
- **Verification**: 文件位置正确，代码引用已更新，gitignore 正确
- **Mission**: `missions/0505-server-profile-config/`

### 2026-04-30 | ES Module修复 + dashboard_page.js拆分

- **Decision**: 服务器启动失败，view_models和routes使用CommonJS但被当作ES Module加载
- **Fix**: ui/routes/*.js → .cjs, ui/dashboard/*.js → .cjs, ui/view_models/*.js → .cjs
- **Fix**: update start_server.js require paths to .cjs
- **Fix**: config.yaml dashboard_entry路径从presentation改为ui/templates
- **Fix**: tool_paths.py tools→scripts目录名修复，config.yaml C++注释→YAML
- **Action**: 拆分 dashboard_page.js → constants.js（提取 UI 常量 ~200 行）
- **Action**: 拆分 source.py → cb_metrics.py（提取计算密集型函数 ~570 行）
- **Action**: 新建 server_config_loader.js（配置读取逻辑 ~300 行）

### 2026-05-30 | 道琼斯美国石油开发与生产指数可交易标的检查

- **任务**: 检查道琼斯美国石油开发与生产指数对应的指数行情、LOF、期货等
- **结果**:
  - 指数: ^DJUSEN (Dow Jones U.S. Oil & Gas Index) 可访问，但非完全匹配的石油开发与生产指数
  - ETF: XOP (SPDR S&P Oil & Gas Exploration & Production ETF) 是最接近的可交易标的，流动性高
  - LOF: Yahoo Finance 无中国 LOF 数据，需使用国内数据源补充
  - 期货: 原油期货 CL=F, QM=F, MCL=F 可访问，但非指数期货
- **数据源**: Yahoo Finance (代理端口 7897)
- **任务类型**: 研究/分析
- **Mission**: missions/0530-oil-index-check/

### 2026-05-30 | 移除南方香港LOF (160125)

- **任务**: 从基金列表中彻底移除南方香港LOF，包括UI页面等
- **Action**: 从 config/config.yaml 的 lof_arbitrage.funds 中删除该基金条目
- **Action**: 从 data_fetch/lof_iopv/fund_classifier.py 的 INDEX_ETF 中删除映射
- **Action**: 从 data_fetch/lof_iopv/holdings_hardcoded.py 中删除条目
- **Action**: 从 specs/lof-arbitrage.md 和 specs/lof-holdings.md 中删除相关行
- **Action**: 从调试脚本 (tools/debug_scripts/) 中删除引用
- **Verification**: 在活动代码中搜索 "160125" 无结果
- **Note**: 运行时数据和存档文件中的引用已忽略

### 2026-05-30 | 修复回测持仓数据缺失逻辑

- **问题**: 回测中只要有一只持仓股票价格缺失，就跳过整个日期
- **修复**: 修改 strategy/lof_iopv/backtest_v2.py，允许部分持仓缺失数据
- **逻辑**: 
  - 构建价格字典时只包含有效价格
  - 计算有数据的持仓权重总和 (valid_weight_sum)
  - 调整 stock_ratio 为 stock_ratio * valid_weight_sum / 100
  - 使用调整后的 stock_ratio 调用 calc_iopv
- **效果**: 持仓总和60%，其中10%没数据时，按54%持仓比例计算
- **验证**: 代码逻辑正确，calc_iopv 函数已支持部分持仓缺失
