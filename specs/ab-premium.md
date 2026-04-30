---
name: ab-premium
description: A/B 股溢价监控模块规格
type: spec
---

# AB 溢价模块规格

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 模块职责

- 监控 A 股与对应 B 股之间的溢价率，发现跨市场定价差异
- 支持上海 B 股（USD）和深圳 B 股（HKD）双汇率
- 提供实时溢价率排名、历史分位数、极值区间

## 2. 数据来源

| 层级 | 来源 | 说明 |
|------|------|------|
| 配对池 | `market_pairs.load_dynamic_pairs()` | 动态 A/B 配对表，含 `bMarket` 和 `currency` |
| 实时行情 | 腾讯行情 `qt.gtimg.cn` | A 股前缀 `sh/sz`，B 股前缀 `sh/sz` |
| 汇率 | 腾讯行情 `whUSDCNY` / `whHKDCNY` | USD/CNY 和 HKD/CNY 实时汇率 |
| 历史数据 | `premium_history.db` | SQLite，3 年历史溢价样本 |

## 3. 关键文件

| 路径 | 职责 |
|------|------|
| `data_fetch/ab_premium/fetcher.py` | 调用 `build_ab_snapshot()` 抓取 |
| `data_fetch/ab_premium/normalizer.py` | 转为 Bus 标准记录 |
| `strategy/ab_premium/service.py` | 消费 Bus 记录，恢复旧 API 结构 |
| `shared/market_service.py` | 核心计算：行情、双汇率、溢价率、历史分位 |
| `shared/bus/market_record.py` | Bus 记录契约 |

## 4. 数据字段

### 4.1 原始行情字段（`raw`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `aCode` | string | A 股代码（6 位） |
| `aName` | string | A 股名称 |
| `aPrice` | number | A 股现价（CNY） |
| `bCode` | string | B 股代码（6 位） |
| `bName` | string | B 股名称 |
| `bPrice` | number | B 股现价（USD/HKD） |
| `bPriceCny` | number | B 股人民币价 |
| `market` | string | `SH-B` 或 `SZ-B` |
| `currency` | string | `USD` 或 `HKD` |
| `exchangeRate` | number | 对应汇率 |
| `premium` | number | 溢价率（%） |
| `percentile` | number | 近 3 年分位数（0-100） |
| `premiumMin` | number | 近 3 年最小溢价率 |
| `premiumMax` | number | 近 3 年最大溢价率 |
| `historyCount` | number | 历史样本数 |
| `historyStartDate` | string | 历史样本起始日 |
| `historyEndDate` | string | 历史样本结束日 |

### 4.2 Bus Metrics

| 字段 | 来源 |
|------|------|
| `premium` | `item.premium` |
| `percentile` | `item.percentile` |
| `premium_min` | `item.premiumMin` |
| `premium_max` | `item.premiumMax` |
| `history_count` | `item.historyCount` |
| `a_price` | `item.aPrice` |
| `pair_price` | `item.bPrice` |
| `pair_price_cny` | `item.bPriceCny` |
| `exchange_rate` | `item.exchangeRate` |

## 5. 计算规则

### 5.1 溢价率

```
b_price_cny = b_price * fx_rate   # fx_rate = USD/CNY 或 HKD/CNY
premium = (b_price_cny / a_price - 1) * 100
```

### 5.2 B 股市场识别

| `bMarket` | 前缀 | 币种 |
|-----------|------|------|
| `sh` | `900xxx` | USD |
| `sz` | `200xxx` | HKD |

### 5.3 历史分位数

- 同 AH 模块：3 年样本，`bisect_right` 经验分位

### 5.4 排序

- 默认按 `premium` 降序排列

## 6. API 合同

### 6.1 对外端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/market/ab` | 完整 AB 溢价列表 |
| GET | `/api/market/overview` | 看板概览（含 AB 最低溢价 TOP 5） |

### 6.2 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `force` | string | `"0"` | `1` 时强制刷新配对池 |

### 6.3 响应结构

```json
{
  "success": true,
  "data": [...],
  "total": 42,
  "hkdExchangeRate": 0.923456,
  "usdExchangeRate": 7.234567,
  "source": "tencent+akshare_pairs+sqlite_history",
  "tradeDate": "2026-04-30",
  "historySync": { "success": true, "updatedRows": 42 },
  "updateTime": "2026-04-30T14:30:00+08:00"
}
```

## 7. 推送规则

- 纳入主摘要推送（`summary.ab_top_n: 2`）
- 推送格式：`AB折价 | 名称 代码 | 溢价 X.XX% | 分位 X.XX% | A X.XX / 对侧 X.XX`
- 同时输出溢价最高 TOP N 和折价最低 TOP N

## 8. 配置参数

```yaml
data_fetch.plugins.ab_premium:
  intraday: true
  refresh_interval_ms: 300000
  daily_incremental_sync: true
  force_pair_sync_on_daily_job: true

strategy.ab_premium:
  ranking_metric: "premium_rate"
  push_top_n: 3

notification.summary:
  ab_top_n: 2
```

## 9. 验收标准

- **AC-001**: `build_ab_snapshot()` 正确区分 SH-B（USD）和 SZ-B（HKD）
- **AC-002**: 双汇率同时返回，无汇率缺失时整条记录丢弃
- **AC-003**: 历史分位数基于真实 3 年样本
- **AC-004**: 每日收盘后自动同步历史数据到 `premium_history.db`
