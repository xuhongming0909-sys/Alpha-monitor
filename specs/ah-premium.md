---
name: ah-premium
description: A/H 股溢价监控模块规格
type: spec
---

# AH 溢价模块规格

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 模块职责

- 监控 A 股与对应 H 股之间的溢价率，发现跨市场定价差异
- 提供实时溢价率排名、历史分位数、极值区间
- 为看板概览和定时推送提供 AH 溢价 TOP N 数据

## 2. 数据来源

| 层级 | 来源 | 说明 |
|------|------|------|
| 配对池 | `market_pairs.load_dynamic_pairs()` | 动态 A/H 配对表，支持强制刷新 |
| 实时行情 | 腾讯行情 `qt.gtimg.cn` | A 股前缀 `sh/sz`，H 股前缀 `hk` |
| 汇率 | 腾讯行情 `whHKDCNY` | HKD/CNY 实时汇率 |
| 历史数据 | `premium_history.db` | SQLite，3 年历史溢价样本 |

## 3. 关键文件

| 路径 | 职责 |
|------|------|
| `data_fetch/ah_premium/fetcher.py` | 调用 `build_ah_snapshot()` 抓取 |
| `data_fetch/ah_premium/normalizer.py` | 转为 Bus 标准记录 |
| `strategy/ah_premium/service.py` | 消费 Bus 记录，恢复旧 API 结构 |
| `shared/market_service.py` | 核心计算：行情、汇率、溢价率、历史分位 |
| `shared/bus/market_record.py` | Bus 记录契约 |

## 4. 数据字段

### 4.1 原始行情字段（`raw`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `aCode` | string | A 股代码（6 位） |
| `aName` | string | A 股名称 |
| `aPrice` | number | A 股现价（CNY） |
| `hCode` | string | H 股代码（5 位） |
| `hName` | string | H 股名称 |
| `hPrice` | number | H 股现价（HKD） |
| `hPriceCny` | number | H 股人民币价 |
| `exchangeRate` | number | HKD/CNY 汇率 |
| `premium` | number | 溢价率（%） |
| `percentile` | number | 近 3 年分位数（0-100） |
| `premiumMin` | number | 近 3 年最小溢价率 |
| `premiumMax` | number | 近 3 年最大溢价率 |
| `historyCount` | number | 历史样本数 |
| `historyStartDate` | string | 历史样本起始日 |
| `historyEndDate` | string | 历史样本结束日 |
| `aReturn5Y` | number | A 股 5 年收益 |
| `pairReturn5Y` | number | H 股 5 年收益 |

### 4.2 Bus Metrics

| 字段 | 来源 |
|------|------|
| `premium` | `item.premium` |
| `percentile` | `item.percentile` |
| `premium_min` | `item.premiumMin` |
| `premium_max` | `item.premiumMax` |
| `history_count` | `item.historyCount` |
| `a_price` | `item.aPrice` |
| `pair_price` | `item.hPrice` |
| `pair_price_cny` | `item.hPriceCny` |
| `exchange_rate` | `item.exchangeRate` |

## 5. 计算规则

### 5.1 溢价率

```
h_price_cny = h_price * hkd_exchange_rate
premium = (h_price_cny / a_price - 1) * 100
```

### 5.2 历史分位数

- 使用 `bisect_right` 计算经验分位
- 样本窗口：3 年（`days=365*3`）
- 分位公式：`position / len(values) * 100`

### 5.3 配对过滤

- A 股代码 6 位，H 股代码 5 位
- 名称一致性校验：`SequenceMatcher.ratio >= 0.62`
- 价格为正才入池

### 5.4 排序

- 默认按 `premium` 降序排列

## 6. API 合同

### 6.1 对外端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/ah` | 完整 AH 溢价列表 |
| GET | `/api/market/overview` | 看板概览（含 AH 最高/最低溢价 TOP 5） |

### 6.2 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `force` | string | `"0"` | `1` 时强制刷新配对池 |

### 6.3 响应结构

```json
{
  "success": true,
  "data": [...],
  "total": 145,
  "exchangeRate": 0.923456,
  "source": "tencent+akshare_pairs+sqlite_history",
  "tradeDate": "2026-04-30",
  "historySync": { "success": true, "updatedRows": 145 },
  "updateTime": "2026-04-30T14:30:00+08:00"
}
```

### 6.4 历史溢价端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/historical-premium?type=AH&code=000001&days=1825` | 单股历史溢价曲线 |

## 7. 推送规则

- 纳入主摘要推送（`summary.ah_top_n: 2`）
- 推送格式：`AH溢价 | 名称 代码 | 溢价 +X.XX% | 分位 X.XX% | A X.XX / 对侧 X.XX`
- 同时输出溢价最高 TOP N 和折价最低 TOP N

## 8. 配置参数

```yaml
data_fetch.plugins.ah_premium:
  intraday: true
  refresh_interval_ms: 300000
  daily_incremental_sync: true
  force_pair_sync_on_daily_job: true

strategy.ah_premium:
  ranking_metric: "premium_rate"
  push_top_n: 3

notification.summary:
  ah_top_n: 2
```

## 9. 验收标准

- **AC-001**: `build_ah_snapshot()` 返回所有配对股票的实时溢价率
- **AC-002**: 历史分位数基于真实 3 年样本，无样本时显示 `--`
- **AC-003**: 名称不一致的配对自动过滤
- **AC-004**: 每日收盘后自动同步历史数据到 `premium_history.db`
