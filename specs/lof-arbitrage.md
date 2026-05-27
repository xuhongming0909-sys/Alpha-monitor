---
name: lof-iopv
description: QDII LOF IOPV 浼板€肩瓥鐣?- 20瀛楁锛?7鍙熀閲戯級
type: spec
---

# QDII LOF IOPV 浼板€肩瓥鐣?
## 1. 鑼冨洿

27鍙?QDII LOF 鍩洪噾锛屼袱绫讳及鍊硷細
- **A绫?鎸囨暟璺熻釜娉曪紙23鍙級**锛歚IOPV = NAV * (1 + etf_ret) * fx_ratio`
- **B绫?T10鎸佷粨娉曪紙4鍙級**锛歚IOPV = NAV * [1 + stock_ratio * sum(w_i * ret_i * fx_i)]`

瀹屾暣鍩洪噾鏍囩殑娓呭崟瑙?`specs/lof-holdings.md`銆?
## 2. 鏁版嵁婧?
| 鏁版嵁 | API | 鍒锋柊闂撮殧 |
|---|---|---|
| 鍑€鍊糔AV | 涓滆储 `api.fund.eastmoney.com/f10/lsjz` | 姣忔棩 |
| 鎸佷粨Top10 | 涓滆储 `fundf10.eastmoney.com/FundArchivesDatas` | 姣忔棩 |
| LOF鍦哄唴浠?| 鑵捐 `shared.market_service.get_quotes()` | 60绉?|
| 鎸佷粨鑲′环 | 鑵捐 `shared.market_service.get_quotes()` | 60绉?|
| 姹囩巼 | 鑵捐/akshare澶涓棿浠?| 60绉?|
| 鍩洪噾妗ｆ | 涓滆储 `fundf10.eastmoney.com/jbgk_{code}.html` | 姣忔棩 |
| 浠介鏁版嵁 | 涓滆储 lsjz API | 姣忔棩 |
| 鐢宠喘闄愰 | 闆嗘€濆綍 `jisilu.cn/data/qdii/qdii_list/A` | 姣忔棩 |
| 鑲＄エ浠撲綅 | 涓滆储 `pingzhongdata/{code}.js` | 姣忔棩 |

## 3. 涓昏〃20瀛楁

| # | 瀛楁 | key | 鏉ユ簮 |
|---|---|---|---|
| 1 | 浠ｇ爜 | code | fetcher |
| 2 | 鍚嶇О | name | fetcher |
| 3 | T-2鍑€鍊?| nav | 涓滆储lsjz |
| 4 | T-2鍑€鍊兼棩鏈?| navDate | 涓滆储lsjz |
| 5 | 鐜颁环 | price | 鑵捐琛屾儏 |
| 6 | 瀹炴椂浼板€?| iopv | 鍙屽紩鎿庤绠?|
| 7 | 瀹炴椂婧环鐜?| premiumRate | (price/iopv-1)*100 |
| 8 | 鐢宠喘鐘舵€?| applyStatus | 涓滆储jbgk + 闆嗘€濆綍闄愰 |
| 9 | 鏂板浠介 | shareIncrease | 涓滆储lsjz |
| 10 | 鍘熸湁浠介 | shareTotal | 涓滆储lsjz |
| 11 | 鐢宠喘璐?| applyFee | 涓滆储jbgk |
| 12 | 璧庡洖璐?| redeemFee | 涓滆储jbgk |
| 13 | 鎵樼璐?| custodianFee | 涓滆储jbgk |
| 14 | 鍩洪噾鍏徃 | fundCompany | 涓滆储jbgk |
| 15 | 浼板€兼爣鐨?| calcTarget | A绫?ETF浠ｇ爜, B绫?"鍓嶅崄澶? |
| 16 | 鍔ㄦ€佷粨浣?| stockPosition | A绫?鍙嶆帹, B绫?Top10鍚堣 |
| 17 | R2 | r2 | 鍥炴祴缁撴灉 |
| 18 | 骞冲潎璇樊 | mae | 鍥炴祴缁撴灉 |
| 19 | MAX璇樊 | maxErr | 鍥炴祴缁撴灉 |
| 20 | 鏍锋湰鍖洪棿 | samplePeriod | 鍥炴祴缁撴灉 |

## 4. 浼板€兼爣鐨勫瓧娈佃鏄?
- A绫伙細鍒楀嚭瀵瑰簲ETF鏍囩殑浠ｇ爜锛堝 SMH銆丵QQ銆丼PY锛?- B绫伙細鍥哄畾鏄剧ず"鍓嶅崄澶?

## 5. 鐩戞帶姹犺鍒?
### 5.1 闄愯喘姹?瀛樺湪闄愯喘 + 婧环鐜?1% + 鎴愪氦棰?100涓?+ 闈炴殏鍋?
### 5.2 闈為檺姹?涓嶉檺璐?+ |婧环鐜噟>5% + 鎴愪氦棰?100涓?+ 闈炴殏鍋?
## 6. 鎺ㄩ€佽鍒?
浜ゆ槗鏃?14:00 鍗曟鎺ㄩ€併€?
## 7. 鍥炴祴鏂规硶

### A绫诲洖娴?- 鑴氭湰锛歚tools/backtest/qdii_backtest_A.py` / `tools/backtest/lof13_backtest_A.py`
- 鏂规硶锛氬熀閲戝噣鍊兼棩鏀剁泭鐜?vs ETF鏃ユ敹鐩婄巼锛屽榻愭棩鏈熷悗璁＄畻R2/MAE/MaxErr
- 鏁版嵁锛歂AV=涓滆储lsjz, ETF=涓滆储k.stock_us_hist锛堝叏閮ㄥ浗鍐匒PI锛?- 缁撴灉锛歚runtime_data/backtest/a_results.json`

### B绫诲洖娴?- 鑴氭湰锛歚tools/backtest/qdii_backtest_B.py`
- 鏂规硶锛氬熀閲戝噣鍊兼棩鏀剁泭鐜?vs T10鎸佷粨鍔犳潈鏃ユ敹鐩婄巼
- 鏁版嵁锛氬叏閮ㄥ浗鍐匒PI锛圢AV=涓滆储, 鎸佷粨=涓滆储F10, 浠撲綅=涓滆储pingzhongdata, 鑲′环=鑵捐K绾? 姹囩巼=akshare锛?- 缁撴灉锛歚runtime_data/backtest/b_results.json`

### A绫诲洖娴嬬粨鏋滐紙2026-03-03~2026-05-22锛?3鍙級

OK=13 WARN=3 BAD=7
璇︽儏瑙?specs/lof-holdings.md section 5

### B绫诲洖娴嬬粨鏋滐紙2026-03-11~2026-05-22锛?鍙級

| 浠ｇ爜 | 鍚嶇О | R2 | MAE% | MaxErr% |
|------|------|-----|------|---------|
| 160125 | 鍗楁柟棣欐腐 | 0.721 | 0.82 | 2.45 |
| 160644 | 娓編浜掕仈缃?| 0.926 | 0.38 | 0.97 |
| 164906 | 涓浜掕仈缃?| 0.891 | 0.38 | 0.89 |

## 8. 缂撳瓨涓庡埛鏂版満鍒?
- 鍦哄唴浠锋牸/姹囩巼锛?0绉掔紦瀛橈紝浜ゆ槗鏃舵鍒锋柊
- 鍩洪噾鍑€鍊?鎸佷粨/妗ｆ/闄愰锛氭瘡鏃ュ埛鏂帮紙涓滆储/闆嗘€濆綍鏁版嵁鏃ユ洿锛?- 鏈嶅姟绔暣浣撳埛鏂帮細60绉掕疆璇紙config.yaml `lof_arbitrage.refresh_interval_ms: 60000`锛?- 鍥炴祴缁撴灉锛氶潤鎬丣SON鏂囦欢锛屽洖娴嬭剼鏈繍琛屽悗鍐欏叆

## 9. 回测规范

### 9.1 回测区间
- 默认回测区间：最近40个交易日（约2个月）
- 回测脚本必须动态计算最近40个交易日，不硬编码日期

### 9.2 汇率因素
- A类回测必须纳入汇率因子：基金日收益率 = ETF日收益率 + 汇率日变动
- 汇率数据源：东方财富USDCNY（133.USDCNY）
- 汇率对齐规则：使用基金净值日期对应的汇率

### 9.3 评级标准
| 评级 | 条件 | 含义 |
|------|------|------|
| **OK** | R² ≥ 0.8 且 MaxErr < 1.0% | 可直接用于套利决策 |
| **WARN** | R² ≥ 0.6 且 MaxErr < 2.0% | 可用但需注意误差 |
| **BAD** | R² < 0.8 或 MaxErr ≥ 2.0% | 误差过大，不建议依赖 |

### 9.4 评级应用
- **OK**: 正常显示IOPV和溢价率
- **WARN**: 显示IOPV但标注"误差较大"
- **BAD**: 不显示IOPV，只显示净值和价格

### 9.5 回测频率
- 每月至少运行一次回测
- 基金持仓变动时触发回测验证