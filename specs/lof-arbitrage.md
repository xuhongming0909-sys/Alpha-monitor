---
name: lof-iopv
description: QDII LOF IOPV 浼板€肩瓥鐣?- 24鍙熀閲?type: spec
---

# QDII LOF IOPV 浼板€肩瓥鐣?
## 1. 鑼冨洿

24鍙猀DII LOF鍩洪噾锛屼袱绫讳及鍊硷紙鐢?`fund_classifier.py` 鐨?`is_index_fund()` 鍐冲畾锛夛細
- **鎸囨暟鍨嬶紙14鍙級**锛欵TF鏄犲皠锛岀‖缂栫爜鍦?`INDEX_ETF` 瀛楀吀锛孖OPV = NAV 脳 (1 + stock_position 脳 etf_period_ret) 脳 fx_ratio
- **涓诲姩鍨嬶紙10鍙級**锛氭寔浠撳姞鏉冩硶锛屾寔浠撴潵婧愪紭鍏堢骇锛欴B 鈫?akshare API 鈫?纭紪鐮佸厹搴?
宸茬Щ闄わ細161815鎶楅€氳儉銆?60216鍥芥嘲鍟嗗搧銆?65513涓俊鍟嗗搧锛團OF鎸佷粨涓嶉€忔槑锛屾棤娉曟嫙鍚堬級

## 2. 鏁版嵁婧?
| 鏁版嵁 | API | 瀛樺偍 |
|---|---|---|
| 鍑€鍊糔AV | 涓滆储 lsjz API | 瀹炴椂鎶撳彇 + DB(fund_nav) |
| LOF鍦哄唴浠?| 鑵捐琛屾儏(qt.gtimg.cn) | 瀹炴椂 |
| ETF浠锋牸 | akshare stock_us_daily | DB(etf_prices) |
| 涓偂浠锋牸 | akshare stock_us_daily / stock_hk_daily | DB(stock_prices) |
| 姹囩巼 | akshare currency_boc_sina | DB(fx_rates) + 瀹炴椂 |
| 鎸佷粨Top10 | 涓滄柟璐㈠瘜fund_portfolio_hold_em / DeepSeek PDF | DB(holdings) |
| 鐢宠喘闄愰 | 涓滆储 fund鏁版嵁椤?| 瀹炴椂 |

## 3. IOPV鍏紡

缁熶竴鍏紡锛坄calc.py: calc_iopv()`锛夛細

```
IOPV = NAV_T-2 脳 (1 + stock_ratio/100 脳 weighted_ret) 脳 fx_ratio
```

- `weighted_ret` = 危(w_i 脳 ret_i)锛屽叾涓?ret_i = (current_price / nav_date_price - 1)
- `stock_ratio` = 鎸佷粨鍚堣鍗犳瘮锛堢櫨鍒嗘瘮锛?- `fx_ratio` = fx_today / fx_nav_date
- 鎸囨暟鍨嬶細stock_ratio=100, weighted_ret = etf_period_ret
- 涓诲姩鍨嬶細stock_ratio = 鎸佷粨鍚堣鏉冮噸锛寃eighted_ret = 鎸佷粨鍔犳潈鏀剁泭

## 4. 鍩洪噾鍒嗙被

### 4.1 鎸囨暟鍨嬶紙14鍙級鈥?`INDEX_ETF` 纭紪鐮?
| 浠ｇ爜 | 鍚嶇О | ETF |
|------|------|-----|
| 161125 | 鏍囨櫘500LOF | SPY |
| 161130 | 绾虫寚LOF | QQQ |
| 161128 | 鏍囨櫘淇℃伅绉戞妧LOF | XLK |
| 161126 | 鏍囨櫘鍖荤枟淇濆仴LOF | XHE |
| 161127 | 鏍囨櫘鐢熺墿绉戞妧LOF | XBI |
| 162415 | 缇庡浗娑堣垂LOF | XLY |
| 160416 | 鐭虫补鍩洪噾LOF | IXC |
| 162719 | 鐭虫补LOF | IEO |
| 162411 | 鍗庡疂娌规皵LOF | XOP |
| 160719 | 鍢夊疄榛勯噾LOF | GLD |
| 164824 | 鍗板害鍩洪噾LOF | INDA |
| 160140 | 缇庡浗REIT绮鹃€塋OF | IYR |
| 164701 | 榛勯噾LOF | GLD |
| 501300 | 缇庡厓鍊篖OF | AGG |

### 4.2 涓诲姩鍨嬶紙10鍙級鈥?鎸佷粨鏉ユ簮锛欴B 鈫?API 鈫?纭紪鐮?
| 浠ｇ爜 | 鍚嶇О | 甯佺 | 纭紪鐮佹寔浠?|
|------|------|------|-----------|
| 160644 | 娓編浜掕仈缃慙OF | HKD | 鉁?_HARDCODED |
| 164906 | 涓浜掕仈缃慙OF | USD | 鉁?_HARDCODED |
| 163208 | 鍏ㄧ悆娌规皵鑳芥簮LOF | USD | 鉁?_HARDCODED |
| 501312 | 娴峰绉戞妧LOF | USD | 鉁?_HARDCODED |
| 501225 | 鍏ㄧ悆鑺墖LOF | USD | 鉁?_HARDCODED |
| 160723 | 鍢夊疄鍘熸补LOF | USD | 鉂?DB/API |
| 161129 | 鍘熸补LOF | USD | 鉂?DB/API |
| 501018 | 鍗楁柟鍘熸补LOF | USD | 鉂?DB/API |
| 161116 | 榛勯噾涓婚LOF | USD | 鉂?DB/API |

## 5. 鏁版嵁搴?
Schema瀹氫箟锛歚data_fetch/lof_db/schema.py`锛?寮犺〃锛?0澶╀繚鐣欙級

| 琛ㄥ悕 | 鐢ㄩ€?| 娓呯悊绛栫暐 |
|---|---|---|
| `fund_nav` | 鍩洪噾鍑€鍊煎巻鍙诧紙鍥炴祴鐢級 | 90澶?|
| `etf_prices` | ETF浠锋牸鍘嗗彶锛坣av-date鏌ユ壘 + 鍥炴祴锛?| 90澶?|
| `stock_prices` | 涓偂浠锋牸鍘嗗彶锛堜富鍔ㄥ瀷nav-date + 鍥炴祴锛?| 90澶?|
| `fx_rates` | 姹囩巼鍘嗗彶锛堝洖娴嬶級 | 90澶?|
| `holdings` | 鎸佷粨鏁版嵁锛堜富鍔ㄥ瀷IOPV + 鍥炴祴锛?| 淇濈暀鍏ㄩ儴 |

## 6. 鍥炴祴

鑴氭湰锛歚strategy/lof_iopv/backtest_v2.py`
- 澶嶇敤 `calc_iopv()` 鍏紡
- 3涓湀绐楀彛锛孨AV缁濆鍊煎姣?- 鏃ユ湡瀵归綈锛氭瘡涓狽AV鏃锛岀敤d鏃ユ寔浠?鑲′环鎺ㄧ畻d+1鏃OPV锛屼笌d+1鏃AV瀵规瘮
- 璇勭骇锛歊虏>=0.8涓擬axErr<1%=OK, R虏>=0.6=WARN, 鍚﹀垯BAD

## 7. 鎺ㄩ€佽鍒?
- 鏉′欢锛歞ailyLimit瀛樺湪(闈炵┖闈為浂) + 婧环鐜?> 2%
- 鍐呭锛氫唬鐮併€佸悕绉般€佹孩浠风巼銆侀檺璐噾棰?- 鏃堕棿锛氫氦鏄撴棩14:00
- 鏈嶅姟锛歚notification/lof_iopv/service.js`

## 8. 姣忔棩缁存姢

- 鍏ュ彛锛歚scripts/lof_maintenance.py`
- 璋冨害锛歚data_fetch/lof_db/updater.py`锛坲pdate_all锛?- 娴佺▼锛歩nit_db 鈫?nav 鈫?etf+stock 鈫?fx 鈫?holdings 鈫?cleanup(90澶?

## 9. 鏂囦欢缁撴瀯

```
data_fetch/lof_iopv/           # 瀹炴椂鏁版嵁鑾峰彇
  source.py                    #   涓诲叆鍙ｏ細NAV+琛屾儏+鎸佷粨+鐢宠喘鐘舵€?  fetcher.py                   #   钖勫寘瑁咃紙璋僺ource.build_lof_snapshot锛?  normalizer.py                #   蹇収鈫払us璁板綍
  fund_classifier.py           #   鍩洪噾鍒嗙被(鎸囨暟/涓诲姩)+鎸佷粨鑾峰彇
  holdings_hardcoded.py        #   涓诲姩鍨嬬‖缂栫爜鎸佷粨鍏滃簳
  report_holdings.py           #   PDF瀛ｆ姤瑙ｆ瀽+LLM鎻愬彇

data_fetch/lof_db/             # 鏁版嵁搴撳眰
  schema.py                    #   5琛⊿chema+鍒濆鍖?娓呯悊
  updater.py                   #   鏇存柊璋冨害鍣?  nav_updater.py               #   鍑€鍊煎閲忔洿鏂?  etf_updater.py               #   ETF/涓偂浠锋牸鏇存柊
  fx_updater.py                #   姹囩巼鏇存柊
  holdings_updater.py          #   鎸佷粨鏇存柊(DB+API+PDF)

strategy/lof_iopv/             # 涓氬姟璁＄畻灞?  calc.py                      #   鍏变韩IOPV鍏紡
  service.py                   #   鍝嶅簲鏋勫缓+鐩戞帶姹犵瓫閫?  backtest_v2.py               #   鍥炴祴锛?涓湀绐楀彛锛?
notification/lof_iopv/         # 鎺ㄩ€佸眰
  service.js                   #   鎺ㄩ€侀€昏緫+鏍煎紡鍖?
scripts/lof_maintenance.py     # 姣忔棩缁存姢鍏ュ彛
config/config.yaml             # 鍩洪噾鍒楄〃(lof_arbitrage.funds)
```
