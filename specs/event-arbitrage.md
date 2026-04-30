---
name: event-arbitrage
description: 事件驱动套利监控模块规格
type: spec
---

# 事件套利模块规格

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 模块职责

- 监控港股私有化、中概股私有化、A 股事件套利机会
- 从集思录公开 API 获取实时数据
- 提供分类展示、套利空间计算、缓存回退

## 2. 数据来源

| 层级 | 来源 | 说明 |
|------|------|------|
| 港股私有化 | `jisilu.cn/data/taoligu/hk_arbitrage_list/` | 集思录港股私有化列表 |
| 中概私有化 | `jisilu.cn/data/taoligu/cn_arbitrage_list/` | 集思录中概股私有化列表 |
| A 股事件 | `jisilu.cn/data/taoligu/astock_arbitrage_list/` | 集思录 A 股套利列表 |
| 缓存回退 | `event_arbitrage_cache.json` | 运行时状态文件 |

## 3. 关键文件

| 路径 | 职责 |
|------|------|
| `data_fetch/event_arbitrage/fetcher.py` | 并发抓取 3 个源，带缓存回退 |
| `data_fetch/event_arbitrage/normalizer.py` | 标准化为统一行结构，再转 Bus 记录 |
| `strategy/event_arbitrage/service.py` | 分类聚合、概览统计 |
| `shared/bus/market_record.py` | Bus 记录契约 |

## 4. 数据字段

### 4.1 标准化行字段（`_build_standardized_row` 输出）

#### 港股私有化（`hk_private`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `symbol` | string | 股票代码 |
| `name` | string | 股票名称 |
| `currentPrice` | number | 当前价格 |
| `changeRate` | number | 涨跌幅（%） |
| `marketValue` | number | 市值 |
| `offerPrice` | number | 要约价格 |
| `spreadRate` | number | 套利空间（%） |
| `eventType` | string | `港股私有化` |
| `eventStage` | string | 进程阶段 |
| `offeror` | string | 要约方 |
| `offerorHolding` | number | 要约方持股比例 |
| `registryPlace` | string | 注册地 |
| `dealMethod` | string | 交易方式 |
| `canShort` | boolean | 可做空 |
| `canCounter` | boolean | 可反对 |
| `summary` | string | 描述 |
| `detailUrl` | string | 详情链接 |
| `releaseDate` | string | 发布日期 |

#### 中概私有化（`cn_private`）

字段与港股私有化基本相同，差异：
- `market`: `US`
- `eventType`: `中概股私有化`
- `registryPlace`: 空
- `canShort`: `None`
- `canCounter`: `None`

#### A 股事件（`a_event`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `symbol` | string | 股票代码 |
| `name` | string | 股票名称 |
| `currentPrice` | number | 当前价格 |
| `changeRate` | number | 涨跌幅（%） |
| `offerPrice` | number | 行权价格/现金选择权价格 |
| `spreadRate` | number | 折价率（%） |
| `eventType` | string | 事件类型（如要约收购、吸收合并） |
| `eventStage` | string | `进行中` 或空 |
| `currency` | string | 币种 |
| `safePrice` | number | 安全价格 |
| `safeDiscountRate` | number | 安全折价率（%） |
| `choosePrice` | number | 现金选择权价格 |
| `chooseDiscountRate` | number | 现金选择权折价率（%） |
| `announcementUrl` | string | 公告链接 |
| `forumUrl` | string | 集思录讨论链接 |

### 4.2 Bus Metrics

| 字段 | 来源 |
|------|------|
| `category` | `hk_private` / `cn_private` / `a_event` |
| `spread_rate` | `standardized.spreadRate` |
| `event_stage` | `standardized.eventStage` |
| `source_status` | 该分类的抓取状态 |

## 5. 计算规则

### 5.1 数据清洗

- 文本清洗：`-`, `--`, `None`, `null` 转为空字符串
- 百分比解析：去除 `%` 后转 float
- 数字解析：去除 `,` 后转 float
- URL 补全：无 scheme 时补 `https://`

### 5.2 分类统计

```python
overview = {
    "totalCount": len(hk + cn + a_event),
    "positiveCount": spreadRate > 0 的数量,
    "hkPrivateCount": len(hk),
    "cnPrivateCount": len(cn),
    "aEventCount": len(a_event),
}
```

### 5.3 缓存策略

- 每源独立缓存
- 抓取失败时回退到缓存，状态标记为 `stale_cache`
- 无缓存且失败时返回空数组，状态标记为 `error`
- `rights_issue` 源默认禁用

## 6. API 合同

### 6.1 对外端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/event-arbitrage` | 完整事件套利数据 |
| GET | `/api/market/overview` | 看板概览 |

### 6.2 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `force` | string | `"0"` | `1` 时强制刷新 |

### 6.3 响应结构

```json
{
  "success": true,
  "data": {
    "overview": {
      "totalCount": 45,
      "positiveCount": 12,
      "hkPrivateCount": 15,
      "cnPrivateCount": 8,
      "aEventCount": 22,
      "announcementPoolCount": 0
    },
    "categories": {
      "hk_private": [...],
      "cn_private": [...],
      "a_event": [...],
      "rights_issue": [],
      "announcement_pool": []
    },
    "sourceStatus": {
      "hk_private": { "status": "ok", "itemCount": 15, ... },
      ...
    }
  },
  "updateTime": "2026-04-30T14:30:00+08:00",
  "cacheTime": "2026-04-30T14:25:00+08:00"
}
```

## 7. 推送规则

- 事件套利数据不纳入主摘要 Markdown 推送（`enable_push: false`）
- 看板展示默认子标签：`a_event`
- 推送配置保留字段：`event_arbitrage_top_n: 6`（预留）

## 8. 配置参数

```yaml
data_fetch.plugins.event_arbitrage:
  intraday: true
  refresh_interval_ms: 300000
  daily_incremental_sync: false
  timeout_ms: 30000
  cache_ttl_ms: 300000
  sources:
    hk_private: { enabled: true }
    cn_private: { enabled: true }
    a_event: { enabled: true }
    rights_issue: { enabled: false }

strategy.event_arbitrage:
  primary_source: "jisilu"
  announcement_role: "auxiliary"
  match_by: "sec_code_only"
  match_lookback_days: 365
  enable_push: false
  treat_limited_apply_as_watch_only: true

presentation.event_arbitrage:
  default_subtab: "a_event"
  show_disabled_categories: true
  module_name: "事件套利"

notification.summary:
  event_arbitrage_top_n: 6
```

## 9. 验收标准

- **AC-001**: 3 个源并发抓取，单源失败不影响其他源
- **AC-002**: 抓取失败时自动回退到缓存，状态正确标记
- **AC-003**: `rights_issue` 源默认禁用，不报错
- **AC-004**: 所有百分比、数字字段正确解析，无效值显示 `--`
- **AC-005**: 概览统计准确，正套利空间计数正确
