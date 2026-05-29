---
name: lof-iopv
description: QDII LOF IOPV 估值策略 - 24只基金
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

24只QDII LOF基金，两类估值（由 `fund_classifier.py` 的 `is_index_fund()` 决定）：
- **指数型（14只）**：ETF映射，硬编码在 `INDEX_ETF` 字典，IOPV = NAV × (1 + stock_position × etf_period_ret) × fx_ratio
- **主动型（10只）**：持仓加权法，持仓来源优先级：DB → akshare API → 硬编码兜底

已移除：161815抗通胀、160216国泰商品、165513中信商品（FOF持仓不透明，无法拟合）

## 2. 数据源

| 数据 | API | 存储 |
|---|---|---|
| 净值NAV | 东财 lsjz API | 实时抓取 + DB(fund_nav) |
| LOF场内价 | 腾讯行情(qt.gtimg.cn) | 实时 |
| ETF价格 | akshare stock_us_daily | DB(etf_prices) |
| 个股价格 | akshare stock_us_daily / stock_hk_daily | DB(stock_prices) |
| 汇率 | akshare currency_boc_sina | DB(fx_rates) + 实时 |
| 持仓Top10 | 东方财富fund_portfolio_hold_em / DeepSeek PDF | DB(holdings) |
| 申购限额 | 东财 fund数据页 | 实时 |

## 3. IOPV公式

统一公式（`calc.py: calc_iopv()`）：

```
IOPV = NAV_T-2 × (1 + stock_ratio/100 × weighted_ret) × fx_ratio
```

- `weighted_ret` = Σ(w_i × ret_i)，其中 ret_i = (current_price / nav_date_price - 1)
- `stock_ratio` = 持仓合计占比（百分比）
- `fx_ratio` = fx_today / fx_nav_date
- 指数型：stock_ratio=100, weighted_ret = etf_period_ret
- 主动型：stock_ratio = 持仓合计权重，weighted_ret = 持仓加权收益

## 4. 基金分类

### 4.1 指数型（14只）— `INDEX_ETF` 硬编码

| 代码 | 名称 | ETF |
|------|------|-----|
| 161125 | 标普500LOF | SPY |
| 161130 | 纳指LOF | QQQ |
| 161128 | 标普信息科技LOF | XLK |
| 161126 | 标普医疗保健LOF | XHE |
| 161127 | 标普生物科技LOF | XBI |
| 162415 | 美国消费LOF | XLY |
| 160416 | 石油基金LOF | IXC |
| 162719 | 石油LOF | IEO |
| 162411 | 华宝油气LOF | XOP |
| 160719 | 嘉实黄金LOF | GLD |
| 164824 | 印度基金LOF | INDA |
| 160140 | 美国REIT精选LOF | IYR |
| 164701 | 黄金LOF | GLD |
| 501300 | 美元债LOF | AGG |

### 4.2 主动型（10只）— 持仓来源：DB → API → 硬编码

| 代码 | 名称 | 币种 | 硬编码持仓 |
|------|------|------|-----------|
| 160644 | 港美互联网LOF | HKD | ✅ _HARDCODED |
| 164906 | 中概互联网LOF | USD | ✅ _HARDCODED |
| 163208 | 全球油气能源LOF | USD | ✅ _HARDCODED |
| 160125 | 南方香港LOF | HKD | ✅ _HARDCODED |
| 501312 | 海外科技LOF | USD | ✅ _HARDCODED |
| 501225 | 全球芯片LOF | USD | ✅ _HARDCODED |
| 160723 | 嘉实原油LOF | USD | ❌ DB/API |
| 161129 | 原油LOF | USD | ❌ DB/API |
| 501018 | 南方原油LOF | USD | ❌ DB/API |
| 161116 | 黄金主题LOF | USD | ❌ DB/API |

## 5. 数据库

Schema定义：`data_fetch/lof_db/schema.py`（5张表，90天保留）

| 表名 | 用途 | 清理策略 |
|---|---|---|
| `fund_nav` | 基金净值历史（回测用） | 90天 |
| `etf_prices` | ETF价格历史（nav-date查找 + 回测） | 90天 |
| `stock_prices` | 个股价格历史（主动型nav-date + 回测） | 90天 |
| `fx_rates` | 汇率历史（回测） | 90天 |
| `holdings` | 持仓数据（主动型IOPV + 回测） | 保留全部 |

## 6. 回测

脚本：`strategy/lof_iopv/backtest_v2.py`
- 复用 `calc_iopv()` 公式
- 3个月窗口，NAV绝对值对比
- 日期对齐：每个NAV日d，用d日持仓+股价推算d+1日IOPV，与d+1日NAV对比
- 评级：R²>=0.8且MaxErr<1%=OK, R²>=0.6=WARN, 否则BAD

## 7. 推送规则

- 条件：dailyLimit存在(非空非零) + 溢价率 > 2%
- 内容：代码、名称、溢价率、限购金额
- 时间：交易日14:00
- 服务：`notification/lof_iopv/service.js`

## 8. 每日维护

- 入口：`scripts/lof_maintenance.py`
- 调度：`data_fetch/lof_db/updater.py`（update_all）
- 流程：init_db → nav → etf+stock → fx → holdings → cleanup(90天)

## 9. 文件结构

```
data_fetch/lof_iopv/           # 实时数据获取
  source.py                    #   主入口：NAV+行情+持仓+申购状态
  fetcher.py                   #   薄包装（调source.build_lof_snapshot）
  normalizer.py                #   快照→Bus记录
  fund_classifier.py           #   基金分类(指数/主动)+持仓获取
  holdings_hardcoded.py        #   主动型硬编码持仓兜底
  report_holdings.py           #   PDF季报解析+LLM提取

data_fetch/lof_db/             # 数据库层
  schema.py                    #   5表Schema+初始化+清理
  updater.py                   #   更新调度器
  nav_updater.py               #   净值增量更新
  etf_updater.py               #   ETF/个股价格更新
  fx_updater.py                #   汇率更新
  holdings_updater.py          #   持仓更新(DB+API+PDF)

strategy/lof_iopv/             # 业务计算层
  calc.py                      #   共享IOPV公式
  service.py                   #   响应构建+监控池筛选
  backtest_v2.py               #   回测（3个月窗口）

notification/lof_iopv/         # 推送层
  service.js                   #   推送逻辑+格式化

scripts/lof_maintenance.py     # 每日维护入口
config/config.yaml             # 基金列表(lof_arbitrage.funds)
```