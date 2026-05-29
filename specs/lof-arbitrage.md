---
name: lof-iopv
description: QDII LOF IOPV 浼板€肩瓥鐣?- 24鍙熀閲?
type: spec
---

# QDII LOF IOPV 浼板€肩瓥鐣?

## 1. 鑼冨洿

24鍙猀DII LOF鍩洪噾锛屼笁绫讳及鍊硷細
- **鎸囨暟鍨嬶紙14鍙級**锛欵TF鏄犲皠杩借釜涓氱哗鍩哄噯锛屽洖娴婱AE<0.5%锛孖OPV = NAV * (1 + etf_ret) * fx_ratio
- **鎸佷粨鍨嬶紙4鍙級**锛氬ぉ澶╁熀閲慉PI瀹炴椂鎸佷粨锛堝悎璁?30%锛夛紝鑷姩閫傚簲瀛ｅ害鍙樻洿
- **鎶ヨ〃鍨嬶紙6鍙級**锛歅DF瀛ｆ姤瑙ｆ瀽鎸佷粨锛屾瘡瀛ｅ害鎵嬪姩鏇存柊

鍒嗙被瑙勫垯锛?
1. 鍥炴祴MAE<0.5% 鈫?鎸囨暟鍨嬶紙ETF鏄犲皠锛?
2. 涓嶉€氳繃鈫?API鎸佷粨鍚堣>30% 鈫?鎸佷粨鍨嬶紙澶╁ぉ鍩洪噾API锛?
3. 鍏朵粬 鈫?鎶ヨ〃鍨嬶紙PDF瀛ｆ姤锛?

宸茬Щ闄わ細161815鎶楅€氳儉銆?60216鍥芥嘲鍟嗗搧銆?65513涓俊鍟嗗搧锛團OF鎸佷粨涓嶉€忔槑锛屾棤娉曟嫙鍚堬級

## 2. 鏁版嵁婧?

| 鏁版嵁 | API | 鍒锋柊闂撮殧 |
|---|---|---|
| 鍑€鍊糔AV | 涓滆储 lsjz API | 姣忔棩 |
| 鎸佷粨Top10 | 澶╁ぉ鍩洪噾API锛堟寔浠撳瀷锛? PDF瀛ｆ姤锛堟姤琛ㄥ瀷锛? ETF鏄犲皠锛堟寚鏁板瀷锛?| 瀹炴椂/瀛ｅ害/闈欐€?|
| LOF鍦哄唴浠?| shared.market_service锛堣吘璁鎯咃級 | 瀹炴椂 |
| ETF浠锋牸 | 鏂版氮 stock_us_daily锛坋tf_updater锛?| 姣忔棩 |
| 涓偂浠锋牸 | 鏂版氮 stock_us_daily / stock_hk_daily锛坋tf_updater锛?| 姣忔棩 |
| 姹囩巼 | akshare currency_boc_sina | 姣忔棩 |
| 鐢宠喘闄愰 | 涓滆储 fund鏁版嵁椤?| 姣忔棩 |

## 3. 鎸囨暟鍨嬩及鍊煎叕寮?

```
IOPV = NAV_T-2 * (1 + ETF_ret) * (FX_today / FX_T-2)
```

## 4. 鎸佷粨鍨?鎶ヨ〃鍨嬩及鍊煎叕寮?

```
IOPV = NAV_T-2 * (1 + stock_ratio * sum(w_i * ret_i)) * fx_ratio
```

## 5. 鏁版嵁搴?

Schema瀹氫箟锛歚data_fetch/lof_db/schema.py`

| 琛ㄥ悕 | 鐢ㄩ€?| 娓呯悊绛栫暐 |
|---|---|---|
| `fund_nav` | 鍩洪噾鍑€鍊煎巻鍙?| 90澶╄繃鏈熸竻鐞?|
| `etf_prices` | ETF浠锋牸鍘嗗彶 | 90澶╄繃鏈熸竻鐞?|
| `stock_prices` | 鎸佷粨鑲＄エ浠锋牸鍘嗗彶锛堟寔浠撳瀷/鎶ヨ〃鍨嬪洖娴嬬敤锛?| 90澶╄繃鏈熸竻鐞?|
| `fx_rates` | 姹囩巼鍘嗗彶 | 90澶╄繃鏈熸竻鐞?|
| `holdings` | 鎸佷粨鏁版嵁锛堜笉娓呯悊锛?| 淇濈暀鍏ㄩ儴 |

## 6. 鍥炴祴鏂规硶

- 鑴氭湰v1锛歚strategy/lof_iopv/backtest.py`锛堟棩鏀剁泭鐜囧洖褰掞紝鍏卞悓鏃ユ湡瀵归綈锛?
- 鑴氭湰v2锛歚strategy/lof_iopv/backtest_v2.py`锛圢AV缁濆鍊煎姣旓紝3涓湀绐楀彛锛屽鐢╟alc鍏紡锛?
- 鎸囨暟鍨嬶細鍩洪噾鍑€鍊兼棩鏀剁泭 vs ETF鏃ユ敹鐩?姹囩巼鏃ユ敹鐩?
- 鎸佷粨鍨?鎶ヨ〃鍨嬶細鍩洪噾鍑€鍊兼棩鏀剁泭 vs T10鎸佷粨鍔犳潈鏃ユ敹鐩?姹囩巼鏃ユ敹鐩?
- 鏃ユ湡瀵归綈锛氬叡鍚屼环鏍兼棩鏈熼泦鍚?
- 璇勭骇锛歊虏>=0.8涓擬axErr<1%=OK, R虏>=0.6=WARN, 鍚﹀垯BAD

## 7. 鎺ㄩ€佽鍒?

- 鏉′欢锛歞ailyLimit瀛樺湪(闈炵┖闈為浂) + 婧环鐜?> 2%
- 鍐呭锛氫唬鐮併€佸悕绉般€佹孩浠风巼銆侀檺璐噾棰?
- 鏃堕棿锛氫氦鏄撴棩14:00
- 鏈嶅姟锛歯otification/lof_iopv/service.js锛堢敤dailyLimit瀛楁鍒ゆ柇闄愯喘锛?

## 8. 姣忔棩缁存姢

- 鑴氭湰锛歚scripts/lof_maintenance.py`
- 璋冨害锛歚data_fetch/lof_db/updater.py`锛坲pdate_all锛?
- 娴佺▼锛氬噣鍊?鈫?ETF+涓偂 鈫?姹囩巼 鈫?鎸佷粨 鈫?娓呯悊

## 9. 鏂囦欢缁撴瀯

```
data_fetch/lof_iopv/         # 瀹炴椂鏁版嵁鑾峰彇锛坰ource/fetcher/normalizer锛?
data_fetch/lof_db/           # 鏁版嵁搴揝chema+缁存姢锛坰chema/updater/nav/etf/fx/holdings锛?
strategy/lof_iopv/           # 浼板€艰绠?calc) + 鏈嶅姟(service) + 鍥炴祴(backtest/v2) + 鍒嗙被(classifier)
notification/lof_iopv/       # 鎺ㄩ€佹湇鍔?service.js) + 鏍峰紡(markdown.js)
ui/src/components/          # React缁勪欢(LofCardList.jsx)
notification/lof_iopv/       # 鎺ㄩ€佹湇鍔?
scripts/lof_maintenance.py   # 姣忔棩缁存姢鍏ュ彛
config/config.yaml           # 鍩洪噾鍒楄〃 + 鎺ㄩ€侀厤缃?
specs/lof-arbitrage.md       # 鏈枃浠?
```