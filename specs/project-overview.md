# 项目总览

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 技术栈

- Node.js >= 18 + Python 3.x
- Express + CORS + yaml
- React + Vite (新 UI)
- Python: akshare, pandas, requests, beautifulsoup4, numpy, PyYAML

## 2. 项目结构

```
data_fetch/     → 上游数据抓取 + 标准化到 "The Bus"
strategy/       → 业务计算与规则判断
ui/   → API 整形、页面、HTML 模板、Dashboard
notification/   → 企业微信推送与调度
shared/         → 配置、路径、时间、运行态、通用能力
tools/          → 部署脚本、数据库维护
runtime_data/   → JSON 状态文件、缓存、配对导出
ui/             → React + Vite 新前端（进行中）
specs/          → 正式模块规格
missions/       → 任务闭环记录
config/         → 配置与密钥占位
```

## 3. 模块职责

- `data_fetch/`：只负责抓取与标准化
- `strategy/`：只负责业务计算与规则判断
- `ui/`：只负责页面、接口整形和展示逻辑
- `notification/`：只负责推送配置、推送格式和推送调度
- `shared/`：只负责配置、路径、时间、运行态和通用能力

跨域公共逻辑只能下沉到 `shared/`，禁止插件之间直接耦合。

## 4. 配置原则

- `config.yaml` 是唯一正式配置合同
- 新增参数时，必须先写入 `config.yaml`，再写代码
- 敏感值可以来自环境变量，但字段名、用途和回退规则仍必须写在 `config.yaml` 中

## 5. 核心数据实体

### 5.1 DashboardStatusLine

- 用途：页面顶部市场摘要
- 来源：`/api/market/exchange-rate`、`/api/market/convertible-bond-arbitrage`
- 字段：`hkdCny`, `usdCny`, `treasuryYield10y`, `updateTime`

### 5.2 PremiumTableState

- 用途：CB、AH、AB 长表格共享客户端状态
- 字段：`sortKey`, `sortDir`, `page`, `pageSize`, `rows`, `total`
- 规则：默认 `pageSize = 50`，序号由排序后行加页偏移派生

### 5.3 ConvertibleBondPremiumRow

- 用途：转债套利表格行
- 来源：`/api/market/convertible-bond-arbitrage`
- 核心字段：`bondCode`, `bondName`, `stockCode`, `stockName`, `bondPrice`, `premiumRate`, `remainingYears`, `remainingScale`

### 5.4 AhAbPremiumRow

- 用途：AH/AB 溢价表格共享行形状
- 来源：`/api/market/ah`、`/api/market/ab`
- 核心字段：`aCode`, `aName`, `peerCode`, `peerName`, `aPrice`, `peerPriceCny`, `spread`, `premium`
- 规则：`spread = peerPriceCny - aPrice`

### 5.5 PushConfigViewState

- 用途：推送配置表单状态
- 来源：`GET/POST /api/push/config`
- 字段：`enabled`, `times[]`, `modules`, `deliveryStatus`

## 6. API 合同索引

详见 `specs/` 各模块规格。全局端点清单：

- `GET /api/health`
- `GET /api/dashboard/ui-config`
- `GET /api/dashboard/resource-status`
- `GET /api/market/exchange-rate`
- `GET /api/market/ipo`
- `GET /api/market/convertible-bonds`
- `GET /api/market/convertible-bond-arbitrage`
- `GET /api/market/ah`
- `GET /api/market/ab`
- `GET /api/market/event-arbitrage`
- `GET /api/market/cb-rights-issue`
- `GET /api/market/lof-arbitrage`
- `GET /api/monitors`
- `GET /api/dividend?action=portfolio`
- `GET /api/dividend?action=refresh`
- `GET/POST /api/push/config`
- `GET/POST /api/push/lof-arbitrage-config`

## 7. 验证命令

- `npm run check`
- `npm run check:boundaries`
- `python data_dispatch.py exchange-rate`
- `python data_dispatch.py ah`
- `python data_dispatch.py ab`
