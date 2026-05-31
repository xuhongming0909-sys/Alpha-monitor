# IOPV 24只基金完整映射方案（v2）

> 2026-05-31 修订
> 原则：期货仅用于已有的（GC=F等），其余用ETF/股票24h数据

## 数据源能力实测

| 市场 | Yahoo代码后缀 | 5m可用 | 盘前盘后 | 实际覆盖 | 备注 |
|------|:---:|:---:|:---:|------|------|
| 美股ETF | 无后缀 | ✅ | ✅ | ~16h (08:00-23:59 UTC) | 最佳覆盖 |
| 美股个股 | 无后缀 | ✅ | ✅ | ~16h | 同上 |
| 美股期货(F) | =F | ✅ | 天然24h | ~23h | 已有的继续用 |
| 美股指数(^) | ^ | ✅(仅盘中) | ❌ | 6.5h | 用期货替代 |
| 港股 | .HK | ✅ | ❌ | 港股时段 | |
| A股ETF | .SS/.SZ | ✅ | ❌ | A股时段 | 用腾讯API |
| A股债券 | — | ❌ | — | — | DB兜底 |
| 伦敦上市 | .L | ✅ | ❌ | 伦敦时段(07-15 UTC) | 仅8h |
| 日股 | .T | ✅ | ❌ | 东京时段(00-06 UTC) | 仅6h |

**结论**：美股ETF/个股的24h数据（含盘前盘后）是最佳通用数据源。

---

## 一、指数型基金（16只）

### 1. 161130 纳指LOF
- **当前**：^NDX（指数，仅盘中6.5h）
- **优化**：`NQ=F`（E-mini纳指期货，24h）
- **原因**：^NDX无盘后，NQ=F天然24h

### 2. 161125 标普500LOF
- **当前**：^GSPC（指数，仅盘中6.5h）
- **优化**：`ES=F`（E-mini标普期货，24h）

### 3. 161128 标普信息科技LOF
- **当前**：^SP500-45（指数，仅盘中）
- **优化**：`XLK`（美股ETF，24h盘前盘后）
- **说明**：不换期货，用ETF 24h数据

### 4. 160719 嘉实黄金LOF
- **当前**：GC=F（期货）
- **优化**：`GC=F`（不变，升级为5m频率）

### 5. 164701 黄金LOF
- **当前**：GLD（ETF，1d）
- **优化**：`GLD`（ETF，5m + includePrePost，~16h）
- **说明**：不换期货，用ETF 24h

### 6. 160140 美国REIT精选LOF
- **当前**：IYR（ETF，1d）
- **优化**：`IYR`（ETF，5m + includePrePost，~16h）

### 7. 161127 标普生物科技LOF
- **当前**：XBI（ETF，1d）
- **优化**：`XBI`（ETF，5m + includePrePost，~16h）

### 8. 162411 华宝油气LOF
- **当前**：XOP（ETF，1d）
- **优化**：`XOP`（ETF，5m + includePrePost，~16h）
- **说明**：不换期货

### 9. 162719 石油LOF
- **当前**：IEO（ETF，1d）
- **优化**：`IEO`（ETF，5m + includePrePost，~16h）
- **说明**：不换期货

### 10. 160416 石油基金LOF
- **当前**：IXC（ETF，1d）
- **优化**：`IXC`（ETF，5m + includePrePost，~16h）
- **说明**：不换期货

### 11. 162415 美国消费LOF
- **当前**：XLY（ETF，1d）
- **优化**：`XLY`（ETF，5m + includePrePost，~16h）

### 12. 161126 标普医疗保健LOF
- **当前**：RYH（ETF，1d）
- **优化**：`RYH`（保持日频，5m数据不可用）

### 13. 164824 印度基金LOF
- **当前**：INDA（ETF，1d）
- **优化**：`INDA`（ETF，5m + includePrePost，~16h）

### 14. 501300 美元债LOF
- **当前**：AGG（ETF，1d）
- **优化**：`AGG`（ETF，5m + includePrePost，~16h）

### 15. 164906 中概互联网LOF
- **当前**：KWEB（ETF，1d）
- **优化**：`KWEB`（ETF，5m + includePrePost，~16h）

### 16. 161226 白银LOF
- **当前**：AG0（上海期货）
- **优化**：**不优化**，保持现状

---

## 二、主动型基金（8只）

### 17. 501225 全球芯片LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 说明 |
|------|------|-----------|------------|------|
| PSI | us | PSI | Yahoo 5m pre/post | |
| SOXX | us | SOXX | Yahoo 5m pre/post | |
| SMH | us | SMH | Yahoo 5m pre/post | |
| 159995 | a | 159995.SZ | **腾讯API** | A股无24h |
| 512800 | a | 512800.SS | **腾讯API** | |
| 512760 | a | 512760.SS | **腾讯API** | |

### 18. 501018 南方原油LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 覆盖 | 说明 |
|------|------|-----------|------------|------|------|
| USL | us | USL | Yahoo 5m pre/post | ~16h | 美股ETF |
| BRNT | uk | **BRNT.L** | Yahoo 5m | ~8h | 伦敦上市，加.L后缀 |
| USO | us | USO | Yahoo 5m pre/post | ~16h | |
| BNO | us | BNO | Yahoo 5m pre/post | ~16h | |
| SimpleXWTI | us | — | DB兜底 | — | 无Yahoo数据 |

### 19. 161129 原油LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 覆盖 | 说明 |
|------|------|-----------|------------|------|------|
| CRUD | uk | **CRUD.L** | Yahoo 5m | ~8h | 伦敦上市，加.L后缀 |
| BRNT | uk | **BRNT.L** | Yahoo 5m | ~8h | 伦敦上市 |
| DBO | us | DBO | Yahoo 5m pre/post | ~16h | |
| BNO | us | BNO | Yahoo 5m pre/post | ~16h | |
| USO | us | USO | Yahoo 5m pre/post | ~16h | |
| GSCI | us | — | DB兜底 | — | 无Yahoo数据 |
| 210305 | a | — | **腾讯API** / DB | A股时段 | A股债券 |
| 250431 | a | — | **腾讯API** / DB | A股时段 | A股债券 |

### 20. 160723 嘉实原油LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 覆盖 | 说明 |
|------|------|-----------|------------|------|------|
| CRUD | uk | **CRUD.L** | Yahoo 5m | ~8h | 伦敦上市 |
| BRNT | uk | **BRNT.L** | Yahoo 5m | ~8h | 伦敦上市 |
| OILK | us | OILK | Yahoo 5m pre/post | ~16h | |
| USO | us | USO | Yahoo 5m pre/post | ~16h | |
| BNO | us | BNO | Yahoo 5m pre/post | ~16h | |
| 1671 | jp | 1671.T | Yahoo 5m | ~6h | 日股 |
| 00883 | hk | 0883.HK | Yahoo 5m | 港股时段 | |
| 00857 | hk | 0857.HK | Yahoo 5m | 港股时段 | |
| XLE | us | XLE | Yahoo 5m pre/post | ~16h | |
| 03175 | hk | 3175.HK | Yahoo 5m | 港股时段 | |

### 21. 160644 港美互联网LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 说明 |
|------|------|-----------|------------|------|
| TSM | us | TSM | Yahoo 5m pre/post | |
| NVDA | us | NVDA | Yahoo 5m pre/post | |
| SNDK | us | SNDK | Yahoo 5m pre/post | |
| MU | us | MU | Yahoo 5m pre/post | |
| 00700 | hk | 0700.HK | Yahoo 5m | |
| GOOGL | us | GOOGL | Yahoo 5m pre/post | |
| 09988 | hk | 9988.HK | Yahoo 5m | |
| 00883 | hk | 0883.HK | Yahoo 5m | |
| AVGO | us | AVGO | Yahoo 5m pre/post | |
| ASML | us | ASML | Yahoo 5m pre/post | |

### 22. 163208 全球油气能源LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 说明 |
|------|------|-----------|------------|------|
| 00916等16只 | hk | *.HK | Yahoo 5m | 全部港股 |

### 23. 501312 海外科技LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 说明 |
|------|------|-----------|------------|------|
| ARKK等10只 | us | 各自代码 | Yahoo 5m pre/post | 全部美股ETF |

### 24. 161116 黄金主题LOF
| 持仓 | 市场 | Yahoo代码 | 优化后数据源 | 说明 |
|------|------|-----------|------------|------|
| SGOL | us | SGOL | Yahoo 5m pre/post | |
| GLDM | us | GLDM | Yahoo 5m pre/post | |
| IAU | us | IAU | Yahoo 5m pre/post | |
| GLD | us | GLD | Yahoo 5m pre/post | |
| 250431 | a | — | **腾讯API** / DB | A股债券 |

**说明**：不换期货，4个黄金ETF各自用24h数据。

---

## 三、数据源优先级

```
获取 current_price：
  1. 期货类（已有）：GC=F → Yahoo 5m
  2. 指数→期货替代：^NDX→NQ=F, ^GSPC→ES=F → Yahoo 5m
  3. 美股ETF/个股 → Yahoo 5m + includePrePost（~16h）
  4. 港股 → Yahoo 5m .HK
  5. 伦敦上市 → Yahoo 5m .L（~8h）
  6. 日股 → Yahoo 5m .T（~6h）
  7. A股 → 腾讯API（实时，无24h）
  8. 以上均失败 → DB 收盘价
```

## 四、Yahoo 代码后缀映射

| 市场 | 后缀 | 示例 |
|------|------|------|
| 美股/ETF | 无 | GLD, USO, NVDA |
| 美股期货 | =F | GC=F, CL=F, NQ=F |
| 美股指数 | ^ | ^NDX, ^GSPC |
| 港股 | .HK | 0700.HK, 9988.HK |
| 伦敦上市 | .L | CRUD.L, BRNT.L |
| 日股 | .T | 1671.T |
| A股(上海) | .SS | 512800.SS |
| A股(深圳) | .SZ | 159995.SZ |

## 五、需要修改的代码

### fund_classifier.py
- 新增 `IOPV_YAHOO替代` 映射表（仅指数→期货：^NDX→NQ=F, ^GSPC→ES=F）

### source.py
- 港股：腾讯 → Yahoo .HK（5m）
- 美股：Yahoo 1d → Yahoo 5m + includePrePost
- 伦敦：识别 `.L` 后缀，用 Yahoo 5m
- 日股：识别 `.T` 后缀，用 Yahoo 5m
- A股：保持腾讯API不变
- 期货：已有 GC=F，升级为 5m 频率

### yahoo_finance.py
- `normalize_ticker_for_yahoo()` 确保伦敦后缀 `.L`、日股 `.T` 正确映射
- `fetch_history()` 支持 `include_pre_post` 参数