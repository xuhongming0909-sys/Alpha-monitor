---
name: lof-holdings
description: QDII LOF 基金标的清单 - 24只基金
type: spec
---

# QDII LOF 基金标的清单

共24只QDII LOF基金，两类估值（`fund_classifier.py`）。

## 指数型（14只）— INDEX_ETF 硬编码映射

| 代码 | 名称 | ETF | 币种 |
|------|------|-----|------|
| 161125 | 标普500LOF | SPY | USD |
| 161130 | 纳指LOF | QQQ | USD |
| 161128 | 标普信息科技LOF | XLK | USD |
| 161126 | 标普医疗保健LOF | XHE | USD |
| 161127 | 标普生物科技LOF | XBI | USD |
| 162415 | 美国消费LOF | XLY | USD |
| 160140 | 美国REIT精选LOF | IYR | USD |
| 501300 | 美元债LOF | AGG | USD |
| 164824 | 印度基金LOF | INDA | USD |
| 160416 | 石油基金LOF | IXC | USD |
| 162719 | 石油LOF | IEO | USD |
| 162411 | 华宝油气LOF | XOP | USD |
| 160719 | 嘉实黄金LOF | GLD | USD |
| 164701 | 黄金LOF | GLD | USD |

## 主动型（10只）— 持仓来源：DB → API → 硬编码兜底

| 代码 | 名称 | 币种 | 硬编码持仓 |
|------|------|------|-----------|
| 160644 | 港美互联网LOF | HKD | ✅ |
| 164906 | 中概互联网LOF | USD | ✅ |
| 163208 | 全球油气能源LOF | USD | ✅ |
| 160125 | 南方香港LOF | HKD | ✅ |
| 501312 | 海外科技LOF | USD | ✅ |
| 501225 | 全球芯片LOF | USD | ✅ |
| 160723 | 嘉实原油LOF | USD | ❌ |
| 161129 | 原油LOF | USD | ❌ |
| 501018 | 南方原油LOF | USD | ❌ |
| 161116 | 黄金主题LOF | USD | ❌ |

## 已移除

| 代码 | 名称 | 原因 |
|------|------|------|
| 161815 | 抗通胀LOF | FOF持仓不透明 |
| 160216 | 国泰商品LOF | FOF持仓不透明 |
| 165513 | 中信保诚商品LOF | FOF持仓不透明 |