---
name: lof-iopv
description: QDII LOF IOPV 估值策略 - 23只基金
type: spec
---

# QDII LOF IOPV 估值策略

## 1. 范围

23只QDII LOF基金，两类估值（由 `fund_classifier.py` 的 `is_index_fund()` 决定）：
- **指数型（14只）**：ETF映射，硬编码在 `INDEX_ETF` 字典
- **主动型（9只）**：持仓加权法，持仓来源优先级：DB → akshare API → 硬编码兜底

已移除：160125南方香港（FOF持仓不透明）、161815抗通胀、160216国泰商品、165513中信保诚商品

## 2. 数据源

| 数据 | API | 存储 |
|------|-----|------|
| 净值NAV | 东方财富 lsjz API | 实时抓取 + DB(fund_nav) |
| LOF场内价 | 腾讯行情(qt.gtimg.cn) | 实时 |
| 美股/期货价格 | Yahoo Deno代理 5m | 美股+includePrePost(~16h)，期货不加(~23h) |
| 港股价格 | 腾讯行情优先 → Yahoo .HK 5m兜底 | 港股交易时段 |
| 伦敦上市 | Yahoo .L 5m | 伦敦交易时段(~8h) |
| 日股 | Yahoo .T 5m | 东京交易时段(~6h) |
| A股价格 | 腾讯API → Yahoo .SS/.SZ → DB兜底 | 非交易时段用DB/Yahoo最近价 |
| 国内期货 | Sina hq.sinajs.cn | 实时 |
| NAV日基准价 | DB(etf_prices/stock_prices) → Yahoo历史兜底 | 期货/海外标的不在DB时用Yahoo |
| 汇率 | akshare currency_boc_sina | DB(fx_rates) + 实时 |
| 持仓Top10 | 东方财富API / Vision LLM PDF | DB(holdings) |
| 申购限额 | 东方财富基金数据页 | 实时 |

## 3. IOPV公式

统一公式（`calc.py: calc_iopv()`）：

```
IOPV = NAV × (1 + stock_ratio/100 × weighted_ret) × fx_ratio
```

- `weighted_ret` = Σ(w_i × ret_i)，其中 ret_i = (current_price / nav_date_price - 1)
- `stock_ratio` = 股票仓位占比（来自东方财富API）
- `fx_ratio` = 当日汇率 / NAV日期汇率
- NAV日期：通常为T-1或T-2

指数型：holdings为ETF映射（100%权重），用ETF价格变化
主动型：holdings为实际持仓Top10，用个股价格加权

> **价格基准一致性**：current_prices 和 nav_date_prices 必须使用同一价格基准（Yahoo后复权价）。
> 美股持仓直接用Yahoo 5m复权价，期货不加includePrePost（会返回空数据）。
> A股用腾讯API，非交易时段用DB或Yahoo .SS/.SZ兜底。
> 指数(^NDX/^GSPC)通过IOPV_INDEX_FUTURES映射为期货(NQ=F/ES=F)获得24h报价。


## 4. 监控池规则

| 池 | 条件 |
|----|------|
| 限购监控池 | 有限额 AND 限额<5万 AND 溢价率>1% AND 成交额>100万 AND 未暂停申购 |
| 非限购监控池 | 不限购 AND 未暂停申购 AND \|溢价率\|>5% AND 成交额>100万 |

## 5. 推送

- 渠道：企业微信Webhook
- 时间：交易日 14:00
- 筛选：限额<5万 AND 溢价率>1%

## 6. 回测

- 窗口：最近90天
- 指标：bias（系统偏差）、MAE（平均绝对误差）、maxErr（最大误差）、R²（拟合度）
- 回测结果缓存在 `runtime_data/backtest/results_v2.json`，UI展示MAE/maxErr

## 7. 数据库维护

- 每天 06:30 CST 自动执行 `scripts/lof_maintenance.py`
- 5张表：fund_nav、etf_prices、stock_prices、fx_rates、holdings
- 保留策略：4张表保留90天，holdings永久保留

## 8. 文件结构

```
data_fetch/lof_iopv/           # 实时数据获取
  source.py                    #   主入口：NAV+行情+持仓+申购状态
  fetcher.py                   #   薄包装（调source.build_lof_snapshot）
  normalizer.py                #   快照→bus记录
  fund_classifier.py           #   基金分类(指数/主动)+持仓获取
  holdings_hardcoded.py        #   主动型硬编码持仓兜底（未使用）
  report_holdings.py           #   PDF季报解析+Vision LLM提取
  ticker_resolver.py           #   持仓名称→ticker解析
  yahoo_finance.py             #   Yahoo Finance ticker搜索+历史价格

data_fetch/lof_db/             # 数据库层
  schema.py                    #   5表Schema+初始化+清理
  updater.py                   #   更新调度器
  nav_updater.py               #   净值增量更新
  etf_updater.py               #   ETF/个股价格更新
  fx_updater.py                #   汇率增量更新
  holdings_updater.py          #   持仓更新(DB+API+PDF)

strategy/lof_iopv/             # 业务计算层
  calc.py                      #   共享IOPV公式
  service.py                   #   响应构建+监控池筛选
  backtest_v2.py               #   回测（90天窗口）

notification/lof_iopv/         # 推送层
  service.js                   #   推送逻辑+格式化
notification/styles/
  lof_iopv_markdown.js         #   推送Markdown格式化

ui/src/components/
  LofCardList.jsx              #   LOF IOPV表格组件

scripts/lof_maintenance.py     # 每日维护入口
config/config.yaml             # 基金列表(lof_iopv.funds)
```