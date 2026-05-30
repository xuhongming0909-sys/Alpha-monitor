# Alpha Monitor API 文档

**Last Updated**: 2026-05-30
**Base URL**: http://127.0.0.1:5001 (本地) / https://your-domain (生产)

---

## 目录

1. [系统健康](#系统健康)
2. [Dashboard 配置](#dashboard-配置)
3. [市场数据 API](#市场数据-api)
4. [LOF 套利 API](#lof-套利-api)
5. [合并套利 API](#合并套利-api)
6. [股票查询 API](#股票查询-api)
7. [自定义监控 API](#自定义监控-api)
8. [分红 API](#分红-api)
9. [推送配置 API](#推送配置-api)
10. [Python CLI 数据抓取](#python-cli-数据抓取)

---

## 通用响应格式

```json
{
  "success": true,
  "data": {},
  "updateTime": "2026-05-30T10:00:00+08:00",
  "source": "xxx"
}
```

错误响应：
```json
{
  "success": false,
  "error": "错误信息",
  "data": null
}
```

---

## 系统健康

### GET /api/health

系统运行状态检查。

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "1.0.0",
    "uptime": 12345
  }
}
```

---

## Dashboard 配置

### GET /api/dashboard/ui-config

UI 展示配置（字体、列宽、自动刷新等）。

### GET /api/dashboard/access-info

Dashboard 访问信息（IP、端口、认证状态）。

### GET /api/dashboard/resource-status

缓存状态元数据，支持按 key 轮询（避免全量刷新）。

**Query**: `keys=exchangeRate,ipo,bonds,cbArb,ah,ab,merger,cbRightsIssue`

---

## 市场数据 API

所有 `/api/market/*` 端点支持 `?force=1` 强制刷新缓存。

### GET /api/market/ah

AH 股溢价数据。

**响应**: AH 溢价排名列表。

### GET /api/market/ab

AB 股溢价数据。

### GET /api/market/exchange-rate

实时汇率（港币/美元 → 人民币）。

### GET /api/market/ipo

IPO/新股申购数据。

### GET /api/market/convertible-bonds

可转债数据列表。

### GET /api/market/convertible-bond-arbitrage

可转债套利数据（折价+双低+回售）。

### GET /api/market/cb-rights-issue

可转债抢权配售数据。

**响应字段**:
```json
{
  "monitorList": [],
  "sourceRows": [],
  "sourceSummary": {},
  "rebuildStatus": {}
}
```

### GET /api/market/lof-arbitrage

LOF 套利数据（核心端点）。

**响应字段**:
```json
{
  "groups": [{"key": "qdii", "label": "QDII"}],
  "defaultGroup": "qdii",
  "rows": [
    {
      "code": "161125",
      "name": "标普500",
      "price": 3.21,
      "nav": 3.15,
      "iopv": 3.16,
      "premiumRate": 1.58,
      "premiumAbs": 0.05,
      "iopvNote": "ETF(14/14持仓)",
      "currency": "USD",
      "fxRatio": 1.002,
      "stockRatio": 95.5,
      "dailyLimit": 0,
      "applyStatus": "限大额",
      "r2": 0.995,
      "maxErr": 0.8
    }
  ],
  "limitedMonitorRows": [],
  "unlimitedMonitorRows": [],
  "sourceSummary": {}
}
```

### GET /api/market/merger

并购套利数据。

### GET /api/market/event-arbitrage

事件套利数据（集思录来源）。

### GET /api/market/subscriptions

打新/申购汇总（IPO + 可转债）。

### GET /api/market/historical-premium

历史溢价率数据。

**Query**:
- `code` (必填): 基金/股票代码
- `days` (可选): 天数，默认 1825，最大 10000

---

## LOF 套利 API

### GET /api/market/lof-arbitrage

见上方市场数据 API 部分。

### GET /api/push/lof-arbitrage-config

LOF 独立推送配置状态。

**响应**:
```json
{
  "data": {
    "enabled": true,
    "times": ["14:00"],
    "tradingDaysOnly": true,
    "deliveryStatus": {
      "webhookConfigured": true,
      "schedulerEnabled": true,
      "lastSuccessAt": "2026-05-30T14:00:00+08:00",
      "lastError": null
    }
  }
}
```

### POST /api/push/lof-arbitrage-config

更新 LOF 推送配置（当前固定为 14:00 单时段）。

---

## 合并套利 API

### GET /api/merger/reports/today

今日并购报告列表。

### GET /api/merger/report?code=xxx

单只股票的并购详情。

### POST /api/merger/report/generate

触发生成并购报告。

---

## 股票查询 API

### GET /api/stock/search?keyword=xxx&limit=10

股票搜索（模糊匹配代码/名称）。

**Query**:
- `keyword` (必填): 搜索关键词
- `limit` (可选): 结果数，默认 10，最大 100

### GET /api/stock/price?code=xxx&market=a

单只股票实时价格。

**Query**:
- `code` (必填): 股票代码
- `market` (可选): `a`/`h`/`b`，默认 `a`
- `bMarket` (可选): B 股市场 `sh`/`sz`，默认 `sh`

---

## 自定义监控 API

### GET /api/monitors

获取自定义监控列表。

### POST /api/monitors

添加/更新自定义监控。

---

## 分红 API

### GET /api/dividend

分红提醒数据。

### POST /api/dividend

更新分红持仓。

---

## 推送配置 API

### GET /api/push/config

全局推送配置。

### POST /api/push/config

更新全局推送配置。

### GET /api/push/cb-arbitrage-config

转债套利推送配置。

### POST /api/push/cb-arbitrage-config

更新转债套利推送配置。

### GET /api/push/cb-rights-issue-config

抢权配售推送配置。

### POST /api/push/cb-rights-issue-config

更新抢权配售推送配置。

### GET /api/push/rules

推送规则查询。

### POST /api/push/wecom

企业微信推送。

### POST /api/push/wecom/event-alerts

企业微信事件告警推送。

---

## Python CLI 数据抓取

通过 `python data_dispatch.py <action>` 命令行触发数据抓取和计算。

### 使用方式

```bash
cd "C:\Users\93724\Desktop\Alpha monitor"
python data_dispatch.py <action>
```

### 可用 Action

| Action | 说明 | 输出 |
|--------|------|------|
| `ah` | AH 股溢价数据 | AH 溢价排名 JSON |
| `ab` | AB 股溢价数据 | AB 溢价排名 JSON |
| `exchange-rate` | 汇率数据 | 港币/美元汇率 JSON |
| `ipo` | IPO/新股申购 | 申购列表 JSON |
| `bonds` | 可转债数据 | 转债列表 JSON |
| `convertible-bond` | 可转债套利 | 折价/双低/回售 JSON |
| `cb-rights-issue` | 抢权配售 | 抢权列表 JSON |
| `lof-iopv` | LOF IOPV 估算 | LOF 快照 JSON |
| `lof-db-sync` | LOF 数据库同步 | NAV+ETF+FX+持仓更新 |
| `merger` | 并购套利 | 并购报告 JSON |
| `event-arbitrage` | 事件套利 | 事件列表 JSON |
| `dividend <code>` | 单只股票分红 | 分红详情 JSON |
| `dividend-upcoming <days>` | 即将分红 | N天内分红列表 |
| `sync-cb-stock-history` | 转债正股历史同步 | 历史数据更新 |
| `sync-cb-rights-issue-stock-history` | 抢权正股历史同步 | 历史数据更新 |

### 数据流架构

```
CLI(data_dispatch.py)  →  data_fetch/*  →  shared/bus  →  strategy/*  →  ui/routes  →  浏览器
       ↑                        ↓
    API 触发              runtime_data/lof_db/lof.db
```

### 常用运维命令

```bash
# 完整 LOF 数据库重建
python data_dispatch.py lof-db-sync

# 查看 LOF 套利机会
python data_dispatch.py lof-iopv

# 更新汇率
python data_dispatch.py exchange-rate

# 健康检查
curl http://127.0.0.1:5001/api/health

# 强制刷新某个模块
curl "http://127.0.0.1:5001/api/market/lof-arbitrage?force=1"
```

---

## 项目内部 Python 模块 API

以下为 Python 内部模块的函数级 API，供脚本和 Skill 调用。

### data_fetch.lof_iopv.fund_classifier

| 函数 | 签名 | 说明 |
|------|------|------|
| `is_index_fund(code)` | `str → bool` | 判断是否指数型基金 |
| `get_fund_class(code)` | `str → str` | 返回基金分类标签 |
| `get_index_etf_ticker(code)` | `str → list` | 返回指数型 ETF 映射列表 |
| `get_holdings_for_service(code)` | `str → list[dict]` | 实时服务用持仓获取 |
| `get_holdings_for_backtest(code)` | `str → list[dict]` | 回测用持仓获取 |

### data_fetch.lof_iopv.source

| 函数 | 签名 | 说明 |
|------|------|------|
| `build_lof_snapshot()` | `() → dict` | 构建全部 LOF 基金快照（NAV+行情+持仓） |

### data_fetch.lof_iopv.report_holdings

| 函数 | 签名 | 说明 |
|------|------|------|
| `update_all_holdings(codes)` | `list[str] → None` | 批量 PDF 持仓提取 |
| `update_fund_holdings(code)` | `str → None` | 单基金持仓更新 |
| `download_report_pdf(report_id)` | `str → str?` | 下载季报 PDF |

### data_fetch.lof_db.schema

| 函数 | 签名 | 说明 |
|------|------|------|
| `init_db()` | `() → None` | 初始化 5 张核心表 |
| `get_db()` | `() → Connection` | 获取 DB 连接 |
| `db_conn()` | context manager | 自动 commit/rollback |
| `cleanup_old_data()` | `() → dict` | 清理 90 天前数据 |

### data_fetch.lof_db 各 updater

| 模块 | 入口函数 | 说明 |
|------|----------|------|
| `nav_updater` | `update_nav(codes)` | 净值增量更新 |
| `etf_updater` | `update_etf_prices(tickers)` | ETF/个股价格更新 |
| `fx_updater` | `update_fx_rates()` | 汇率更新 |
| `holdings_updater` | `update_holdings(codes)` | 持仓更新(DB+API+PDF) |

### strategy.lof_iopv.calc

| 函数 | 签名 | 说明 |
|------|------|------|
| `calc_iopv(...)` | `(nav, holdings, current_prices, ...) → (float?, note, details)` | IOPV 核心计算 |
| `to_float(v)` | `any → float?` | 安全浮点转换 |

### strategy.lof_iopv.service

| 函数 | 签名 | 说明 |
|------|------|------|
| `build_lof_response(fetch_payload)` | `dict → dict` | 构建 LOF 套利完整响应 |

### shared.market_service

| 函数 | 签名 | 说明 |
|------|------|------|
| `get_fx_rates(currencies)` | `list → dict` | 实时汇率查询 |
| `get_quotes(tickers)` | `list → dict` | 实时行情查询 |

### shared.config.script_config

| 函数 | 签名 | 说明 |
|------|------|------|
| `load_config()` | `() → dict` | 加载 config.yaml |

### shared.time.shanghai_time

| 函数 | 签名 | 说明 |
|------|------|------|
| `now_iso()` | `() → str` | 当前上海时间 ISO 格式 |