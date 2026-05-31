# IOPV 24只基金完整映射方案（v3）

> 2026-05-31 最终版
> 原则：ETF 24h优先，期货保持已有，欧洲标的必须加正确后缀

## 欧洲市场 Yahoo 后缀

| 交易所 | 后缀 | 交易时间(UTC) | 示例 |
|--------|------|-------------|------|
| 伦敦 LSE | .L | 08:00-16:30 | CRUD.L, BRNT.L, PHAU.L |
| 法兰克福 Xetra | .DE | 07:00-15:30 | 4GLD.DE |
| 阿姆斯特丹 Euronext | .AS | 08:00-16:30 | （无可用标的） |
| 瑞士 SIX | .SW | 08:00-16:20 | （无可用标的） |
| 米兰 Borsa | .MI | 08:00-16:25 | CRUD.MI |
| 巴黎 Euronext | .PA | 08:00-16:30 | — |
| 马德里 Bolsa | .MC | 08:00-16:30 | — |
| 斯德哥尔摩 | .ST | 08:00-16:25 | — |
| 东京 TSE | .T | 00:00-06:00 | 1671.T |

**规则**：欧洲上市的标的必须加后缀，否则Yahoo返回空数据。

---

## 一、指数型基金（16只）

### 1. 161130 纳指LOF
- 当前：^NDX（仅盘中6.5h）
- 优化：**NQ=F**（期货24h）
- 类型：指数→期货

### 2. 161125 标普500LOF
- 当前：^GSPC（仅盘中6.5h）
- 优化：**ES=F**（期货24h）
- 类型：指数→期货

### 3. 161128 标普信息科技LOF
- 当前：^SP500-45（仅盘中）
- 优化：**XLK**（美股ETF，5m pre/post ~16h）
- 类型：ETF 24h

### 4. 160719 嘉实黄金LOF
- 当前：GC=F（期货）
- 优化：**GC=F**（升级为5m频率，~23h）
- 类型：仅升级频率

### 5. 164701 黄金LOF
- 当前：GLD（ETF，1d）
- 优化：**GLD**（ETF，5m pre/post ~16h）
- 类型：ETF 24h

### 6. 160140 美国REIT精选LOF
- 当前：IYR（ETF，1d）
- 优化：**IYR**（ETF，5m pre/post ~16h）

### 7. 161127 标普生物科技LOF
- 当前：XBI（ETF，1d）
- 优化：**XBI**（ETF，5m pre/post ~16h）

### 8. 162411 华宝油气LOF
- 当前：XOP（ETF，1d）
- 优化：**XOP**（ETF，5m pre/post ~16h）
- 类型：ETF 24h，不换期货

### 9. 162719 石油LOF
- 当前：IEO（ETF，1d）
- 优化：**IEO**（ETF，5m pre/post ~16h）
- 类型：ETF 24h，不换期货

### 10. 160416 石油基金LOF
- 当前：IXC（ETF，1d）
- 优化：**IXC**（ETF，5m pre/post ~16h）
- 类型：ETF 24h，不换期货

### 11. 162415 美国消费LOF
- 当前：XLY（ETF，1d）
- 优化：**XLY**（ETF，5m pre/post ~16h）

### 12. 161126 标普医疗保健LOF
- 当前：RYH（ETF，1d）
- 优化：**RYH**（保持日频，5m不可用）

### 13. 164824 印度基金LOF
- 当前：INDA（ETF，1d）
- 优化：**INDA**（ETF，5m pre/post ~16h）

### 14. 501300 美元债LOF
- 当前：AGG（ETF，1d）
- 优化：**AGG**（ETF，5m pre/post ~16h）

### 15. 164906 中概互联网LOF
- 当前：KWEB（ETF，1d）
- 优化：**KWEB**（ETF，5m pre/post ~16h）

### 16. 161226 白银LOF
- 当前：AG0（上海期货）
- **不优化**，保持现状

---

## 二、主动型基金（8只）

### 17. 501225 全球芯片LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 | 覆盖 |
|------|------|-----------|--------|------|
| PSI | 美股 | PSI | Yahoo 5m pre/post | ~16h |
| SOXX | 美股 | SOXX | Yahoo 5m pre/post | ~16h |
| SMH | 美股 | SMH | Yahoo 5m pre/post | ~16h |
| 159995 | A股(深) | — | **腾讯API** | A股时段 |
| 512800 | A股(沪) | — | **腾讯API** | A股时段 |
| 512760 | A股(沪) | — | **腾讯API** | A股时段 |

### 18. 501018 南方原油LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 | 覆盖 |
|------|------|-----------|--------|------|
| USL | 美股 | USL | Yahoo 5m pre/post | ~16h |
| BRNT | **伦敦** | **BRNT.L** | Yahoo 5m | ~8h |
| USO | 美股 | USO | Yahoo 5m pre/post | ~16h |
| BNO | 美股 | BNO | Yahoo 5m pre/post | ~16h |
| SimpleXWTI | — | 无数据 | **DB兜底** | — |

### 19. 161129 原油LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 | 覆盖 |
|------|------|-----------|--------|------|
| CRUD | **伦敦** | **CRUD.L** | Yahoo 5m | ~8h |
| BRNT | **伦敦** | **BRNT.L** | Yahoo 5m | ~8h |
| DBO | 美股 | DBO | Yahoo 5m pre/post | ~16h |
| BNO | 美股 | BNO | Yahoo 5m pre/post | ~16h |
| USO | 美股 | USO | Yahoo 5m pre/post | ~16h |
| GSCI | — | 无数据 | **DB兜底** | — |
| 210305 | A股 | — | **腾讯API** / DB | A股时段 |
| 250431 | A股 | — | **腾讯API** / DB | A股时段 |

### 20. 160723 嘉实原油LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 | 覆盖 |
|------|------|-----------|--------|------|
| CRUD | **伦敦** | **CRUD.L** | Yahoo 5m | ~8h |
| BRNT | **伦敦** | **BRNT.L** | Yahoo 5m | ~8h |
| OILK | 美股 | OILK | Yahoo 5m pre/post | ~16h |
| USO | 美股 | USO | Yahoo 5m pre/post | ~16h |
| BNO | 美股 | BNO | Yahoo 5m pre/post | ~16h |
| 1671 | **日股** | **1671.T** | Yahoo 5m | ~6h |
| 00883 | 港股 | 0883.HK | Yahoo 5m | 港股时段 |
| 00857 | 港股 | 0857.HK | Yahoo 5m | 港股时段 |
| XLE | 美股 | XLE | Yahoo 5m pre/post | ~16h |
| 03175 | 港股 | 3175.HK | Yahoo 5m | 港股时段 |

### 21. 160644 港美互联网LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 |
|------|------|-----------|--------|
| TSM | 美股 | TSM | Yahoo 5m pre/post |
| NVDA | 美股 | NVDA | Yahoo 5m pre/post |
| SNDK | 美股 | SNDK | Yahoo 5m pre/post |
| MU | 美股 | MU | Yahoo 5m pre/post |
| 00700 | 港股 | 0700.HK | Yahoo 5m |
| GOOGL | 美股 | GOOGL | Yahoo 5m pre/post |
| 09988 | 港股 | 9988.HK | Yahoo 5m |
| 00883 | 港股 | 0883.HK | Yahoo 5m |
| AVGO | 美股 | AVGO | Yahoo 5m pre/post |
| ASML | 美股 | ASML | Yahoo 5m pre/post |

### 22. 163208 全球油气能源LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 |
|------|------|-----------|--------|
| 00916等16只 | 港股 | *.HK | Yahoo 5m |

### 23. 501312 海外科技LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 |
|------|------|-----------|--------|
| ARKK等10只 | 美股 | 各自代码 | Yahoo 5m pre/post |

### 24. 161116 黄金主题LOF
| 持仓 | 市场 | Yahoo代码 | 数据源 | 覆盖 |
|------|------|-----------|--------|------|
| SGOL | 美股 | SGOL | Yahoo 5m pre/post | ~16h |
| GLDM | 美股 | GLDM | Yahoo 5m pre/post | ~16h |
| IAU | 美股 | IAU | Yahoo 5m pre/post | ~16h |
| GLD | 美股 | GLD | Yahoo 5m pre/post | ~16h |
| 250431 | A股 | — | **腾讯API** / DB | A股时段 |

---

## 三、数据源优先级

```
1. 期货（已有）：GC=F, NQ=F, ES=F → Yahoo 5m
2. 美股ETF/个股 → Yahoo 5m + includePrePost（~16h）
3. 港股 → Yahoo 5m .HK
4. 伦敦上市 → Yahoo 5m .L（~8h）
5. 日股 → Yahoo 5m .T（~6h）
6. A股 → 腾讯API（实时）
7. 全部失败 → DB 收盘价
```

## 四、Yahoo 代码后缀映射表

```python
# yahoo_finance.py 需要的后缀映射
YAHOO_SUFFIX = {
    "us": "",        # 美股无后缀
    "hk": ".HK",     # 港股
    "uk": ".L",      # 伦敦
    "de": ".DE",     # 德国Xetra
    "nl": ".AS",     # 阿姆斯特丹
    "ch": ".SW",     # 瑞士
    "it": ".MI",     # 意大利米兰
    "fr": ".PA",     # 法国巴黎
    "es": ".MC",     # 西班牙马德里
    "se": ".ST",     # 瑞典斯德哥尔摩
    "jp": ".T",      # 日本东京
}
```

## 五、需要修改的代码

### yahoo_finance.py
- `normalize_ticker_for_yahoo()`：确认欧洲后缀映射正确
- `fetch_history()`：支持 `include_pre_post` 参数

### source.py
- 美股：Yahoo 1d → Yahoo 5m + includePrePost
- 港股：腾讯 → Yahoo .HK 5m
- 伦敦：识别 market="uk" → 加 .L 后缀
- 日股：识别 market="jp" → 加 .T 后缀
- A股：保持腾讯API

### fund_classifier.py
- 新增 `IOPV_YAHOO替代`：仅 ^NDX→NQ=F, ^GSPC→ES=F