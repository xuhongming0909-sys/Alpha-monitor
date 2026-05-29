# Alpha Monitor 鈥?椤圭洰绱㈠紩

**瀹氫綅**锛氶噾铻嶅鍒╂満浼氱洃鎺х粓绔紝浠庣湡瀹炲競鍦烘暟鎹腑鍙戠幇濂楀埄鏈轰細锛岄€氳繃缃戦〉灞曠ず鍜屼紒涓氬井淇℃帹閫佸畬鎴愰棴鐜€?
**闃舵**锛歊eact 閲戣瀺缁堢 UI 骞惰閲嶅仛涓紝鏃?HTML 鐪嬫澘淇濈暀 `/legacy` 鍥炴粴鍏ュ彛锛涘綋鍓?React 椤跺眰瀵艰埅鏀舵暃涓?7 涓爣绛俱€?
**鎶€鏈爤**锛歂ode.js 18+ + Express锛圓PI/鏈嶅姟灞傦級锛孭ython 3锛堟暟鎹姄鍙?璁＄畻灞傦級锛孯eact + Vite锛堟柊鍓嶇锛夛紝SQLite + JSON锛堣繍琛屾椂鐘舵€侊級銆?

---

## 1. 鏋舵瀯姒傝

```
娴忚鍣?瀹㈡埛绔?
    鈹?
    鈻?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? ui/              API 璺敱涓庨〉闈㈡覆鏌?                     鈹?
鈹? 鈹溾攢 routes/       /api/market/* /api/dashboard/*        鈹?
鈹? 鈹溾攢 view_models/  鏁版嵁鏁村舰                               鈹?
鈹? 鈹斺攢 templates/    HTML 妯℃澘                             鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
    鈹?
    鈻?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? strategy/          涓氬姟璁＄畻灞?                           鈹?
鈹? 鈹溾攢 ah_premium/     AH 婧环鎺掑悕                          鈹?
鈹? 鈹溾攢 convertible_bond/ 杞€哄鍒╋紙鍙屼綆/鎶樹环/鍥炲敭锛?       鈹?
鈹? 鈹溾攢 lof_iopv/  QDII LOF IOPV 浼板€硷紙T10鎸佷粨鍔犳潈娉曪級                       鈹?
鈹? 鈹斺攢 ... (鍏?10 涓彃浠?                                   鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
    鈹?
    鈻?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? "The Bus" 鈥?鏍囧噯鍖栬褰曟牸寮?                             鈹?
鈹? shared/bus/market_record.{py,js}                       鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
    鈹?
    鈻?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? data_fetch/          鏁版嵁鎶撳彇灞?                         鈹?
鈹? 鈹溾攢 ah_premium/       鑵捐琛屾儏锛堝疄鏃惰偂浠?姹囩巼锛?          鈹?
鈹? 鈹溾攢 convertible_bond/ 闆嗘€濆綍+涓滆储锛堣浆鍊鸿鎯?璐㈠姟锛?      鈹?
鈹? 鈹溾攢 lof_iopv/    闆嗘€濆綍锛圦DII LOF IOPV 婧环鐜囷級         鈹?
鈹? 鈹斺攢 ... (鍏?11 涓彃浠?                                   鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
    鈹?
    鈻?
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
鈹? 涓婃父鏁版嵁婧?                                               鈹?
鈹? 鑵捐琛屾儏 / 闆嗘€濆綍 / AkShare / 宸ㄦ疆璧勮 / 涓滄柟璐㈠瘜       鈹?
鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
```

**鍒嗗眰瑙勫垯**锛?
- `data_fetch/` 鍙仛鎶撳彇+鏍囧噯鍖栵紝涓嶅啓涓氬姟閫昏緫
- `strategy/` 鍙仛璁＄畻+瑙勫垯鍒ゆ柇锛屼笉鐩存帴璋冧笂娓?API
- `ui/` 鍙仛 API 鏁村舰+灞曠ず锛屼笉鍋氳绠?
- `notification/` 鍙仛鎺ㄩ€?璋冨害锛屼笉纰版暟鎹姄鍙?
- 璺ㄥ眰閫氫俊鍙兘閫氳繃 The Bus 鏍囧噯鍖栬褰?
- 璺ㄦ彃浠剁姝㈢洿鎺?import锛堢敱 `tools/check_plugin_boundaries.py` 寮哄埗妫€鏌ワ級

---

## 2. 鐩綍绱㈠紩

### 2.1 data_fetch/ 鈥?鏁版嵁鎶撳彇灞傦紙11 涓彃浠讹紝浠庝笂娓?API 鎷夋暟鎹苟鏍囧噯鍖栦负 Bus 璁板綍锛?

姣忎釜鎻掍欢鏍囧噯缁撴瀯锛歚fetcher.py`锛堣皟搴︼級+ `source.py`锛堜笂娓?API锛? `normalizer.py`锛堟爣鍑嗗寲涓?Bus 璁板綍锛夈€傞儴鍒嗘彃浠舵湁 `history_source.py`/`history_sync.py`锛堝巻鍙叉暟鎹悓姝ワ級銆?

| 鎻掍欢 | 鏁版嵁婧?| 鍏抽敭鏂囦欢 | 杈撳嚭 |
|------|--------|----------|------|
| `ah_premium/` | 鑵捐琛屾儏 | `fetcher.py`, `source.py`, `normalizer.py` | AH 鑲℃孩浠峰揩鐓?|
| `ab_premium/` | 鑵捐琛屾儏 | `fetcher.py`, `source.py`, `normalizer.py` | AB 鑲℃孩浠峰揩鐓?|
| `exchange_rate/` | 鑵捐 | `fetcher.py`, `normalizer.py` | 娓竵/缇庡厓浜烘皯甯佹眹鐜?|
| `convertible_bond/` | 闆嗘€濆綍 + 涓滆储 | `fetcher.py`, `source.py`, `normalizer.py`, `history_sync.py`, `history_source.py` | 杞€哄鍒╂暟鎹紙鍚悊璁哄畾浠凤級 |
| `cb_rights_issue/` | 闆嗘€濆綍 | `fetcher.py`, `source.py`, `normalizer.py`, `history_source.py` | 杞€烘姠鏉冮厤鍞暟鎹?|
| `lof_iopv/` | 涓滆储+鑵捐+闆悆 | `fetcher.py`, `source.py`, `fund_classifier.py`, `normalizer.py` | QDII LOF IOPV涓夊垎绫?鎸囨暟/鎸佷粨/鎶ヨ〃)鏁版嵁 |
| `merger/` | 鍏憡 API | `fetcher.py`, `source.py`, `normalizer.py` | 骞惰喘閲嶇粍鍏憡 |
| `event_arbitrage/` | 闆嗘€濆綍 | `fetcher.py`, `normalizer.py` | 浜嬩欢椹卞姩濂楀埄 |
| `subscription/` | 澶氭簮 | `fetcher.py`, `ipo_source.py`, `bond_source.py`, `normalizer.py` | 鏂拌偂/杞€虹敵璐棩鍘?|
| `dividend/` | AkShare / 宸ㄦ疆 | `fetcher.py`, `source.py`, `normalizer.py` | 鑲℃伅鍏憡 |
| `custom_monitor/` | 杩愯鎬?| `input_reader.py` | 鐢ㄦ埛鑷畾涔夌洃鎺х粍鍚?|

**缁熶竴鍏ュ彛**锛歚data_dispatch.py <action>` 鈥?鍛戒护琛岃皟搴﹀櫒锛屾牴鎹?action 璋冪敤瀵瑰簲鎻掍欢鐨?fetcher銆?

### 2.2 strategy/ 鈥?涓氬姟璁＄畻灞傦紙10 涓彃浠讹紝鎵ц璁＄畻瑙勫垯銆佹帓鍚嶃€佺瓫閫夈€佺瓥鐣ュ垽瀹氾級

姣忎釜鎻掍欢鏍囧噯缁撴瀯锛歚service.py`锛圥ython 璁＄畻閫昏緫锛? `service.js`锛圢ode.js 閫傞厤鍣級銆傞儴鍒嗘湁 `runtime_service.js`锛堣繍琛屾椂鐘舵€佺鐞嗭級鎴?`discount_runtime_store.js`锛堢瓥鐣ョ姸鎬佹寔涔呭寲锛夈€?

| 鎻掍欢 | 鍏抽敭鏂囦欢 | 涓氬姟瑙勫垯 |
|------|----------|----------|
| `ah_premium/` | `service.py`, `service.js` | 婧环鐜囨帓鍚嶃€佸巻鍙茬櫨鍒嗕綅 |
| `ab_premium/` | `service.py`, `service.js` | AB 婧环鎺掑悕 |
| `convertible_bond/` | `service.py`, `service.js`, `discount_runtime_store.js` | 鍙屼綆绛栫暐銆佺悊璁烘敹鐩婄巼銆佸洖鍞鍒┿€佹姌浠风瓥鐣ワ紙涔板叆/鍗栧嚭/鐩戞帶锛?|
| `cb_rights_issue/` | `service.py` | 鎶㈡潈閰嶅敭棰勬湡鏀剁泭璁＄畻銆侀樁娈靛垽瀹氥€佸叆姹犲垽鏂?|
| `lof_iopv/` | `service.py` | QDII LOF IOPV 婧环鐜囨帓鍚?|
| `merger/` | `service.py`, `service.js` | 骞惰喘閲嶇粍 deal 鍒嗘瀽銆丄I 鎶ュ憡鐢熸垚锛圖eepSeek锛?|
| `event_arbitrage/` | `service.py` | 浜嬩欢鍖归厤涓庤繃婊?|
| `subscription/` | `service.py`, `service.js` | 鐢宠喘浜嬩欢璺熻釜 |
| `dividend/` | `service.py`, `service.js`, `runtime_service.js` | 鑲℃潈鐧昏鏃ヨ窡韪€佹敹鐩婄巼璁＄畻 |
| `custom_monitor/` | `service.py`, `service.js`, `runtime_service.js` | 鑷畾涔夌粍鍚堟敹鐩婄巼璁＄畻 |

### 2.3 ui/ 鈥?API 涓庡睍绀哄眰锛圗xpress 璺敱銆佽鍥炬ā鍨嬨€佺湅鏉挎ā鏉匡級

| 鏂囦欢 | 鑱岃矗 | 鏈嶅姟绔偣 |
|------|------|----------|
| `routes/market_routes.js` | 甯傚満琛屾儏璺敱 | `/api/market/ah`, `/api/market/ab`, `/api/market/convertible-bond-arbitrage`, `/api/market/lof-arbitrage`, `/api/market/merger`, `/api/market/event-arbitrage`, `/api/market/cb-rights-issue`, `/api/market/ipo`, `/api/market/convertible-bonds`, `/api/market/exchange-rate` |
| `routes/dashboard_routes.js` | 鐪嬫澘璺敱 | `/api/dashboard/ui-config`, `/api/dashboard/resource-status`, `/api/dashboard/overview`, `/api/monitors`, `/api/dividend?action=*` |
| `routes/push_routes.js` | 鎺ㄩ€侀厤缃矾鐢?| `/api/push/config`, `/api/push/cb-rights-issue-config`, `/api/push/lof-arbitrage-config`, `/api/push/wecom` |
| `view_models/overview.js` | 鐪嬫澘姒傝鏁版嵁缁勮 | 琚?dashboard_routes 璋冪敤 |
| `view_models/push_payload.js` | 鎺ㄩ€侀厤缃搷搴旀牸寮?| 琚?push_routes 璋冪敤 |
| `dashboard/dashboard_page.js` | 鏃х湅鏉块〉闈㈤€昏緫 | legacy 椤甸潰娓叉煋 |
| `templates/dashboard_template.html` | 鏃х湅鏉?HTML 妯℃澘 | 鍚唴鑱?CSS/JS锛屾殫鑹查噾铻嶇粓绔富棰?|

### 2.4 notification/ 鈥?鎺ㄩ€佷笌璋冨害灞傦紙浼佷笟寰俊銆佹憳瑕佺粍瑁呫€佸憡璀︽帹閫侊級

| 缁勪欢 | 鍏抽敭鏂囦欢 | 鑱岃矗 |
|------|----------|------|
| **WeCom 瀹㈡埛绔?* | `wecom/client.js` | 鍙戦€?Markdown 鍒颁紒涓氬井淇?Webhook |
| **璋冨害鍣?* | `scheduler/wecom_scheduler.js` | 瀹氭椂鎺ㄩ€佽皟搴︼紙60s tick锛?|
| **鎺ㄩ€侀厤缃?* | `scheduler/push_config_store.js`, `push_runtime_store.js` | 杩愯鏃舵帹閫侀厤缃笌鐘舵€?|
| **妯″潡閰嶇疆** | `scheduler/module_push_config_store.js`, `module_push_runtime_store.js` | 鍚勬ā鍧楋紙CB/LOF/鎶㈡潈閰嶅敭锛夌嫭绔嬫帹閫侀厤缃?|
| **鎽樿鏈嶅姟** | `summary/main_summary.js` | 鑱氬悎鎵€鏈夋ā鍧楃敓鎴愭瘡鏃ユ憳瑕?Markdown |
| **鎶樹环绛栫暐鎻愰啋** | `alerts/event_alert_service.js` | 瀹炴椂鎶樹环涔板叆/鍗栧嚭/鐩戞帶鍚嶅崟鎺ㄩ€?|
| **CB 濂楀埄鎺ㄩ€?* | `cb_arbitrage/service.js` | 杞€哄鍒╃嫭绔嬫帹閫侀€昏緫 |
| **鎶㈡潈閰嶅敭鎺ㄩ€?* | `cb_rights_issue/service.js` | 鎶㈡潈閰嶅敭鐙珛鎺ㄩ€侀€昏緫 |
| **LOF 濂楀埄鎺ㄩ€?* | `lof_iopv/service.js` | QDII LOF IOPV 鎺ㄩ€侀€昏緫锛堝畾鏃?鍗虫椂锛?|
| **骞惰喘鎶ュ憡** | `merger_report/service.js` | 骞惰喘 deal 鎶ュ憡鎺ㄩ€?|
| **Markdown 鏍峰紡** | `styles/*.js` | 鍚勬帹閫佺被鍨嬬殑鏍煎紡鍖栨ā鏉?|

### 2.5 shared/ 鈥?璺ㄥ眰閫氱敤鑳藉姏锛堥厤缃€佽矾寰勩€佹椂鍖恒€佹棩蹇椼€丅us 璁板綍鏍煎紡銆佽繍琛屾椂鐘舵€侊級

| 鐩綍 | 鍏抽敭鏂囦欢 | 鑱岃矗 |
|------|----------|------|
| `bus/` | `market_record.py`, `market_record.js`, `bus_contract.md` | **The Bus** 鈥?鏍囧噯鍖栬褰曟牸寮忥紝瀹氫箟璺ㄥ眰閫氫俊濂戠害 |
| `config/` | `node_config.js`, `script_config.py` | 缁熶竴閰嶇疆璇诲彇锛圷AML + 鐜鍙橀噺娉ㄥ叆锛?|
| `paths/` | `node_paths.js`, `script_paths.py`, `tool_paths.py` | 璺緞瑙ｆ瀽锛堣繍琛屾椂鏂囦欢銆佹暟鎹簱銆侀厤缃級 |
| `runtime/` | `json_store.js`, `json_store.py`, `state_registry.js`, `state_registry.py` | JSON 鏂囦欢鎸佷箙鍖栥€佽繍琛屾椂鐘舵€佺鐞?|
| `time/` | `shanghai_time.js`, `shanghai_time.py` | 涓婃捣鏃跺尯銆佷氦鏄撴椂娈垫娴嬨€佸競鍦烘椂闂?|
| `logging/` | `logger.js`, `logger.py` | 缁熶竴鏃ュ織 |
| `models/` | `service_result.js`, `service_result.py` | 鏍囧噯鎴愬姛/閿欒鍝嶅簲鍖呰 |
| 鏍圭洰褰?| `market_service.py` | 璺ㄥ競鍦哄伐鍏凤紙浠锋牸鏌ヨ銆侀厤瀵瑰尮閰嶃€佹悳绱級 |

### 2.6 scripts/ 鈥?杩愮淮涓庢暟鎹鐞嗚剼鏈紙鍘嗗彶搴撻噸寤恒€侀厤瀵瑰鍑恒€佸仴搴锋鏌ョ瓑锛?

| 鏂囦欢 | 鑱岃矗 |
|------|------|
| `add_ai_summary.py` | 鎵归噺娣诲姞 AI-SUMMARY 娉ㄩ噴 |
| `audit_ah_history_coverage.py` | AH 鍘嗗彶瑕嗙洊瀹¤ |
| `cb_rights_issue_stock_history_db.py` | 鎶㈡潈閰嶅敭姝ｈ偂鍘嗗彶鏁版嵁搴?|
| `check_plugin_boundaries.py` | **鏋舵瀯 enforcement** 鈥?妫€鏌ヨ法鎻掍欢闈炴硶渚濊禆 |
| `check_root_cleanliness.py` | 鏍圭洰褰曟竻娲佹鏌?|
| `check_health.ps1` | 鍋ュ悍妫€鏌ワ紙PowerShell锛?|
| `export_pair_pool.py` | 閰嶅姹犲鍑?|
| `fetch_historical_premium.py` | 鍘嗗彶婧环鎶撳彇 |
| `fetch_merger_arbitrage.py` | 骞惰喘濂楀埄鎶撳彇 |
| `market_pairs.py` | 甯傚満閰嶅宸ュ叿 |
| `premium_history_db.py` | 婧环鍘嗗彶鏁版嵁搴撶鐞?|
| `rebuild_premium_db.py` | 婧环鍘嗗彶鏁版嵁搴撻噸寤?|
| `render_mini_swe_task.py` | mini-SWE-agent 浠诲姟娓叉煋 |
| `stock_price_history_db.py` | 鑲′环鍘嗗彶鏁版嵁搴撶鐞?|
| `subscription_history_db.py` | 鐢宠喘鍘嗗彶鏁版嵁搴撶鐞?|
| `sync_convertible_bond_stock_history.py` | 杞€烘鑲″巻鍙插悓姝?|

### 2.7 deploy/ 鈥?閮ㄧ讲閰嶇疆

| 鏂囦欢 | 鑱岃矗 |
|------|------|
| `alpha-monitor.service` | systemd 鏈嶅姟鏂囦欢 |
| `Caddyfile`, `nginx-*.conf` | Web 鏈嶅姟鍣ㄩ厤缃?|
| `install_*.sh` | 瀹夎鑴氭湰锛圕addy/Nginx/systemd锛?|
| `update_*.sh` | 鑷姩鏇存柊鑴氭湰 |
| server_doctor.sh | 鏈嶅姟鍣ㄥ仴搴锋鏌?|
| sync_server.sh | 鏈嶅姟鍣?git 鍚屾锛堝崗璁慨澶?stash/鍐茬獊/閲嶅惎锛?|
| `sync_remote_env_from_profile.py` | 鍚屾杩滅▼鐜鍙橀噺锛堣鍙?`config/server_profile.local.yaml`锛?|

### 2.6a config/ 鈥?閰嶇疆鏂囦欢

| 鏂囦欢 | 鑱岃矗 |
|------|------|
| `config/config.yaml` | 闈炴晱鎰熶笟鍔￠厤缃細鍙傛暟銆侀槇鍊笺€乁RL銆佸紑鍏?|
| `config/secrets.yaml` | 鏁忔劅閰嶇疆锛欰PI Key銆乄ebhook銆佸瘑鐮侊紙gitignored锛?|
| `config/server_profile.local.yaml` | 鏈嶅姟鍣ㄨ繛鎺ラ厤缃細SSH host/user/port/password锛坓itignored锛?|

### 2.7 docs/ 鈥?椤圭洰鏂囨。锛圲I 璁捐瑙勮寖銆佽繍缁存墜鍐屻€乵ini-SWE-agent 浣跨敤鎸囧崡锛?

### 2.8 ui/ 鈥?React 鍓嶇锛堣繘琛屼腑锛孷ite + React 閲嶅啓 UI锛?

褰撳墠 React 椤跺眰鏍囩鍥哄畾涓猴細姒傝銆佽浆鍊哄鍒┿€丄H 婧环銆丄B 婧环銆丩OF 濂楀埄銆佹墦鏂扮敵璐€佽嚜瀹氫箟銆?
React 瀵艰埅涓庢瑙堝凡鎺掗櫎锛氬垎绾㈡彁閱掋€佷簨浠跺鍒┿€佹帹閫佽缃€?

| 鏂囦欢 | 鑱岃矗 |
|------|------|
| `src/App.jsx` | React 搴旂敤涓荤粍浠?|
| `src/main.jsx` | 鍏ュ彛鏂囦欢 |
| `src/styles.css` | 鏍峰紡 |
| `src/components/BottomNav.jsx` | 鎵嬫満绔簳閮ㄥ鑸紝璐熻矗 7 涓《绾ф爣绛惧垏鎹?|
| `src/components/ConvertibleCardList.jsx` | 杞€哄鍒╃畝娲佹ā鍧楄〃鏍?|
| `src/components/AhCardList.jsx` | AH 婧环绠€娲佹ā鍧楄〃鏍?|
| `src/components/AbCardList.jsx` | AB 婧环绠€娲佹ā鍧楄〃鏍?|
| `src/components/LofCardList.jsx` | LOF IOPV浼板€艰〃鏍硷細涓夊垎绫诲睍绀?鎸囨暟鍨嬭摑/鎸佷粨鍨嬬豢/鎶ヨ〃鍨嬫)+MAE鍒?|
| `src/components/SubscriptionCardList.jsx` | 鎵撴柊鐢宠喘绠€娲佹ā鍧楄〃鏍?|
| `src/components/RightsIssueCardList.jsx` | 鎶㈡潈閰嶅敭绠€娲佹ā鍧楄〃鏍?|
| `src/components/MonitorCardList.jsx` | 鑷畾涔夌洃鎺х畝娲佹ā鍧楄〃鏍?|
| `src/components/cardHelpers.jsx` | React 鍏叡鏍煎紡鍖栦笌杞婚噺灞曠ず绉湪 |
| `src/components/cardListHelpers.jsx` | React 鍘嗗彶琛屽３甯姪鍑芥暟 |
| `src/components/SimpleDataTable.jsx` | React 绠€娲佹ā鍧楄〃鏍煎叕鍏辩粍浠?|
| `index.html` | HTML 妯℃澘 |
| `package.json` | Vite + React 渚濊禆 |

### 2.9 鏍圭洰褰曞叧閿枃浠讹紙鍏ュ彛鑴氭湰銆侀厤缃悎鍚屻€佸啋鐑熸祴璇曪級

| 鏂囦欢 | 鑱岃矗 |
|------|------|
| `start_server.js` | **涓诲叆鍙?*锛?224 琛岋級鈥?Express 鍚姩銆佹湇鍔℃敞鍐屻€佽矾鐢辨寕杞姐€佽皟搴﹀櫒鍚姩 |
| `data_dispatch.py` | **鏁版嵁璋冨害 CLI** 鈥?鏍规嵁 action 璋冪敤瀵瑰簲 data_fetch + strategy 鎻掍欢 |
| `config.yaml` | **鍞竴姝ｅ紡閰嶇疆鍚堝悓** 鈥?鎵€鏈変笟鍔″弬鏁般€侀槇鍊笺€乁RL銆佸紑鍏?|
| `package.json` | Node 渚濊禆涓庤剼鏈?|
| `requirements.txt` | Python 渚濊禆 |
| `tests/smoke_check.js` | 鍐掔儫娴嬭瘯 |
| `shared/paths/db_paths.py` | 鏁版嵁搴撹矾寰勯厤缃?|

---

## 3. 鏂囦欢閫熸煡琛紙鎸夊姛鑳芥悳绱㈡簮鐮佷綅缃級

鎸夊姛鑳芥煡璇細

| 鎯虫壘浠€涔?| 鏂囦欢浣嶇疆 |
|----------|----------|
| 鎶樹环绛栫暐涔板叆/鍗栧嚭/鐩戞帶鎺ㄩ€侀€昏緫 | `notification/alerts/event_alert_service.js` |
| 鎶樹环绛栫暐鐘舵€佹寔涔呭寲 | `strategy/convertible_bond/discount_runtime_store.js` |
| 鎶樹环绛栫暐涓氬姟璁＄畻 | `strategy/convertible_bond/service.py` |
| 杞€哄鍒╂暟鎹姄鍙?| `data_fetch/convertible_bond/fetcher.py` |
| 杞€哄鍒╀笂娓?API | `data_fetch/convertible_bond/source.py` |
| 鎶㈡潈閰嶅敭璁＄畻 | `strategy/cb_rights_issue/service.py` |
| 鎶㈡潈閰嶅敭鏁版嵁鎶撳彇 | `data_fetch/cb_rights_issue/fetcher.py` |
| 鎶㈡潈閰嶅敭鎺ㄩ€?| `notification/cb_rights_issue/service.js` |
| QDII LOF IOPV 鏁版嵁鎶撳彇 | `data_fetch/lof_iopv/fetcher.py` | LOF IOPV fetcher锛堣杽鍖呰锛岃皟鐢╯ource.py锛?|
| data_fetch/lof_iopv/source.py | LOF IOPV鏁版嵁鑾峰彇灞傦紙涓滆储鍑€鍊?鑵捐琛屾儏+闆悆浠撲綅锛?|
| QDII LOF IOPV 鎺ㄩ€?| `notification/lof_iopv/service.js` |
| AH 婧环璁＄畻 | `strategy/ah_premium/service.py` |
| AB 婧环璁＄畻 | `strategy/ab_premium/service.py` |
| 骞惰喘濂楀埄璁＄畻+AI 鎶ュ憡 | `strategy/merger/service.py` |
| 姣忔棩鎽樿鎺ㄩ€佺粍瑁?| `notification/summary/main_summary.js` |
| 鎺ㄩ€佽皟搴﹀櫒 | `notification/scheduler/wecom_scheduler.js` |
| 鎺ㄩ€侀厤缃瓨鍌?| `notification/scheduler/push_config_store.js` |
| 妯″潡鎺ㄩ€侀厤缃?| `notification/scheduler/module_push_config_store.js` |
| WeCom 鍙戦€佸鎴风 | `notification/wecom/client.js` |
| 甯傚満琛屾儏璺敱 | `ui/routes/market_routes.js` |
| 鐪嬫澘璺敱 | `ui/routes/dashboard_routes.js` |
| 鎺ㄩ€侀厤缃矾鐢?| `ui/routes/push_routes.js` |
| 鐪嬫澘姒傝鏁版嵁 | `ui/view_models/overview.js` |
| 缁熶竴閰嶇疆璇诲彇 | `shared/config/node_config.js` / `script_config.py` |
| JSON 鐘舵€佹寔涔呭寲 | `shared/runtime/json_store.js` / `json_store.py` |
| 涓婃捣鏃跺尯/浜ゆ槗鏃舵 | `shared/time/shanghai_time.js` / `shanghai_time.py` |
| The Bus 璁板綍鏍煎紡 | `shared/bus/market_record.js` / `market_record.py` |
| 鏋舵瀯杈圭晫妫€鏌?| `scripts/check_plugin_boundaries.py` |
| 鑷姩閮ㄧ讲鑴氭湰 | `deploy/update_from_github.sh` |
| 鏈嶅姟鍣ㄥ惎鍔?| `start_server.js` |
| 鏁版嵁璋冨害 CLI | `data_dispatch.py` |

---

## 4. 杩愯涓庨獙璇侀€熸煡

- 鏁版嵁娴侊細`ui/routes/*` 鈫?`data_dispatch.py` 鈫?`data_fetch/*` 鈫?Bus 鈫?`strategy/*` 鈫?API JSON銆?
- 杩愯鎬侊細鍏抽敭 JSON/DB 浣嶄簬 `runtime_data/shared/`锛岄儴缃叉椂淇濈暀锛屼笉鎻愪氦 Git銆?
- 涓昏楠岃瘉锛歚npm run ui:build`銆乣npm run check:boundaries`銆乣ALPHA_MONITOR_BASE_URL=http://43.139.35.190 node tests/smoke_check.js`銆乣node tests/ui_*.test.js`銆?
- 宸ヤ綔娴侊細鏂颁换鍔″啓鍏?`missions/MMDD-name/{spec.md,plan.md}`锛屼氦鎺ュ啓鍏?`MEMORY.md`锛屾寮忛渶姹傚啓鍏?`specs/`銆?

---

## 5. 浠ｇ爜鏂囦欢瑙勮寖锛堟枃浠跺ぇ灏忛檺鍒躲€丄I-SUMMARY 娉ㄩ噴瑙勮寖锛?

### 9.1 鏂囦欢澶у皬闄愬埗

> **纭鍒?*锛氫换浣曚唬鐮佹枃浠讹紙`.py`銆乣.js`銆乣.jsx`锛変笉寰楄秴杩?**1000 琛?*銆?
>
> **涓轰粈涔?*锛氳秴杩?1000 琛岀殑鏂囦欢闅句互鍦?AI 涓婁笅鏂囩獥鍙ｄ腑瀹屾暣鍔犺浇锛屽鑷存绱㈠洶闅俱€佷慨鏀规槗鍑洪敊銆丷eview 鎴愭湰鎸囨暟绾т笂鍗囥€?
>
> **鎷嗗垎鍘熷垯**锛?
> - 鎸夊姛鑳借亴璐ｆ媶鍒嗭紙濡?`source.py` 鈫?`source.py` + `parser.py` + `cache.py`锛?
> - 鎸?API 绔偣鎷嗗垎锛堝 `market_routes.js` 鈫?`ah_routes.js` + `cb_routes.js` + `...`锛?
> - 鎸夋暟鎹眰鎷嗗垎锛堝 `service.py` 鈫?`calculator.py` + `formatter.py` + `validator.py`锛?
> - 鎷嗗垎鍚庢瘡浠芥柊鏂囦欢蹇呴』鏈夌嫭绔嬬殑 `AI-SUMMARY` 鍜?INDEX.md 鐧昏
>
> **渚嬪**锛氳嚜鍔ㄧ敓鎴愮殑妯℃澘/甯搁噺鏂囦欢锛堝澶у瀷 HTML 妯℃澘銆丣SON 鏁版嵁鏂囦欢锛夊彲璞佸厤锛屼絾搴斿湪鏂囦欢鍚嶄腑鏍囨敞锛堝 `.template.html`銆乣.data.json`锛夈€?

### 9.2 AI-SUMMARY 娉ㄩ噴瑙勮寖

> **纭鍒?*锛氭瘡浠芥牳蹇冧唬鐮佹枃浠堕《閮ㄥ繀椤绘湁 `AI-SUMMARY:` 娉ㄩ噴銆?
>
> **鏍煎紡**锛?
> ```python
> # AI-SUMMARY: [涓€鍙ヨ瘽鑱岃矗鎻忚堪]
> # 瀵瑰簲 INDEX.md 搂9.3 鏂囦欢鎽樿绱㈠紩
> ```
> ```javascript
> // AI-SUMMARY: [涓€鍙ヨ瘽鑱岃矗鎻忚堪]
> // 瀵瑰簲 INDEX.md 搂9.3 鏂囦欢鎽樿绱㈠紩
> ```
>
> **瑕佹眰**锛?
> - 涓€鍙ヨ瘽锛屼笉瓒呰繃 30 瀛?
> - 璇存槑"杩欎釜鏂囦欢鍋氫粈涔?锛屼笉鏄?杩欎釜鏂囦欢鏈変粈涔堝嚱鏁?
> - 蹇呴』涓?INDEX.md 琛ㄦ牸涓殑鎻忚堪瀹屽叏涓€鑷?
>
> **缁存姢瑙勫垯**锛?
> 1. 淇敼鏂囦欢鑱岃矗鎴栫粨鏋勫悗锛屽繀椤诲悓姝ユ洿鏂版枃浠堕《閮?`AI-SUMMARY` 鍜?INDEX.md 琛ㄦ牸銆?
> 2. 鏂板鏍稿績鏂囦欢鏃讹紝蹇呴』鍐欏叆 `AI-SUMMARY` 骞跺湪 INDEX.md 鐧昏銆?
> 3. 鍒犻櫎鏍稿績鏂囦欢鏃讹紝蹇呴』鍚屾鍒犻櫎 INDEX.md 瀵瑰簲琛屽拰鏂囦欢涓殑娉ㄩ噴銆?
> 4. 鎷嗗垎鏂囦欢鏃讹紝鏃ф枃浠剁殑 `AI-SUMMARY` 鍜?INDEX.md 鏉＄洰闇€鏇存柊鎴栧垹闄わ紝鏂版枃浠跺繀椤荤櫥璁般€?

---

## 9.3 鏂囦欢鎽樿绱㈠紩

### 9.1 鏍圭洰褰曚笌鍏ュ彛

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `server_config_loader.js` | 鏈嶅姟鍣ㄩ厤缃姞杞斤細绔彛/璺緞/绛栫暐/瓒呮椂绛夐厤缃鍙?|
| `start_server.js` | Express 涓诲叆鍙ｏ細鍚姩鏈嶅姟銆佹寕杞借矾鐢便€佹敞鍐岃皟搴﹀櫒銆佺鐞嗚繍琛屾椂鐘舵€?|
| `data_dispatch.py` | CLI 鏁版嵁璋冨害鍣細鏍规嵁 action 璋冪敤瀵瑰簲 data_fetch 鎶撳彇鍜?strategy 璁＄畻 |
| `config.yaml` | 涓氬姟閰嶇疆鍚堝悓锛氭墍鏈夊弬鏁般€侀槇鍊笺€乁RL銆佸紑鍏崇殑鍗曚竴鏉ユ簮 |

### 9.2 data_fetch/ 鈥?鏁版嵁鎶撳彇灞?

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `data_fetch/ah_premium/fetcher.py` | AH 婧环鎶撳彇璋冨害锛氳皟鐢ㄨ吘璁鎯?API 骞舵爣鍑嗗寲涓?Bus 璁板綍 |
| `data_fetch/ah_premium/source.py` | AH 婧环涓婃父 API锛氳吘璁鎯?+ 閰嶅搴?+ 鍘嗗彶鏁版嵁搴?|
| `data_fetch/ah_premium/normalizer.py` | AH 婧环鏁版嵁鏍囧噯鍖栵細鍘熷琛屾儏杞负 Bus 鏍囧噯鍖栬褰?|
| `data_fetch/ab_premium/fetcher.py` | AB 婧环鎶撳彇璋冨害锛氳皟鐢ㄨ吘璁鎯?API 骞舵爣鍑嗗寲涓?Bus 璁板綍 |
| `data_fetch/ab_premium/source.py` | AB 婧环涓婃父 API锛氳吘璁鎯?+ 閰嶅搴?+ 鍘嗗彶鏁版嵁搴?|
| `data_fetch/ab_premium/normalizer.py` | AB 婧环鏁版嵁鏍囧噯鍖栵細鍘熷琛屾儏杞负 Bus 鏍囧噯鍖栬褰?|
| `data_fetch/convertible_bond/fetcher.py` | 杞€哄鍒╂姄鍙栬皟搴︼細璋冪敤闆嗘€濆綍/涓滄柟璐㈠瘜 API |
| `data_fetch/convertible_bond/cb_metrics.py` | 杞€哄鍒╂寚鏍囪绠楋細娉㈠姩鐜?ATR/鐞嗚瀹氫环/绾€轰环鍊?鏈熸潈浠峰€?|
| `data_fetch/convertible_bond/source.py` | 杞€哄鍒╀笂娓?API锛氶泦鎬濆綍瀹炴椂琛屾儏 + 涓滄柟璐㈠瘜璐㈠姟鏁版嵁 |
| `data_fetch/convertible_bond/normalizer.py` | 杞€哄鍒╂暟鎹爣鍑嗗寲锛氬惈鐞嗚瀹氫环鐨?Bus 璁板綍鐢熸垚 |
| `data_fetch/lof_iopv/fetcher.py` | LOF IOPV fetcher锛堣杽鍖呰锛岃皟鐢╯ource.py锛?|
| `data_fetch/lof_iopv/source.py` | LOF IOPV涓婃父API锛氫笢璐㈠噣鍊?鑵捐琛屾儏+闆悆浠撲綅+闆嗘€濆綍鐢宠喘鐘舵€?|
| `data_fetch/lof_iopv/normalizer.py` | LOF IOPV鏁版嵁鏍囧噯鍖栵細蹇収杞珺us璁板綍 |
| `data_fetch/merger/fetcher.py` | 骞惰喘鏁版嵁鎶撳彇璋冨害锛氳皟鐢ㄥ法娼叕鍛?API |
| `data_fetch/merger/source.py` | 骞惰喘鍏憡 API锛氬法娼祫璁叕鍛婃悳绱笌瑙ｆ瀽 |
| `data_fetch/dividend/fetcher.py` | 鑲℃伅鎶撳彇璋冨害锛氳皟鐢?AkShare/宸ㄦ疆 API |
| `data_fetch/dividend/source.py` | 鑲℃伅涓婃父 API锛欰kShare CNINFO + 鑵捐琛屾儏 |
| `data_fetch/subscription/fetcher.py` | 鐢宠喘鎶撳彇璋冨害锛欼PO + 杞€虹敵璐棩鍘?|
| `data_fetch/exchange_rate/fetcher.py` | 姹囩巼鎶撳彇璋冨害锛氳皟鐢ㄨ吘璁眹鐜?API |
| `data_fetch/custom_monitor/input_reader.py` | 鑷畾涔夌洃鎺ц緭鍏ヨ鍙栵細浠庤繍琛屾€?JSON 璇诲彇鐢ㄦ埛缁勫悎 |
| `data_fetch/event_arbitrage/fetcher.py` | 浜嬩欢濂楀埄鎶撳彇璋冨害锛氳皟鐢ㄩ泦鎬濆綍浜嬩欢 API |
| `data_fetch/cb_rights_issue/fetcher.py` | 鎶㈡潈閰嶅敭鎶撳彇璋冨害锛氳皟鐢ㄩ泦鎬濆綍棰勬 API |


### 9.3.1 data_fetch/lof_db/ -- LOF鏁版嵁搴撴ā鍧?

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `data_fetch/lof_db/schema.py` | SQLite鏁版嵁搴揝chema瀹氫箟鍜屽垵濮嬪寲 |锛堝惈cleanup_old_data杩囨湡娓呯悊锛墊
| `data_fetch/lof_db/updater.py` | 鏁版嵁鏇存柊璋冨害鍣?|
| `data_fetch/lof_db/nav_updater.py` | 鍩洪噾鍑€鍊煎閲忔洿鏂?|
| `data_fetch/lof_db/etf_updater.py` | ETF/涓偂浠锋牸澧為噺鏇存柊锛堟柊娴猘kshare stock_us_daily + stock_hk_daily锛?|
| `data_fetch/lof_db/fx_updater.py` | 姹囩巼澧為噺鏇存柊 |
| `data_fetch/lof_db/holdings_updater.py` | 鎸佷粨鏁版嵁澧為噺鏇存柊 |
| `data_fetch/lof_iopv/fund_classifier.py` | LOF涓夊垎绫?鎸囨暟鍨?鎸佷粨鍨?鎶ヨ〃鍨?鍩洪噾鍒嗙被鍣?鎸佷粨鑾峰彇 |
| `strategy/lof_iopv/backtest_v2.py` | LOF鍥炴祴锛堟寚鏁板瀷ETF+涓诲姩鍨嬫寔浠擄紝缁熶竴calc_iopv鍏紡锛?涓湀绐楀彛锛?|

### 9.3 strategy/ 鈥?涓氬姟璁＄畻灞?

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `strategy/ah_premium/service.py` | AH 婧环涓氬姟璁＄畻锛氭孩浠风巼鎺掑悕銆佸巻鍙茬櫨鍒嗕綅 |
| `strategy/ah_premium/service.js` | AH 婧环 Node 閫傞厤鍣細Python 璁＄畻缁撴灉杞负 API 鍝嶅簲 |
| `strategy/ab_premium/service.py` | AB 婧环涓氬姟璁＄畻锛欰B 鑲℃孩浠风巼鎺掑悕 |
| `strategy/ab_premium/service.js` | AB 婧环 Node 閫傞厤鍣細Python 璁＄畻缁撴灉杞负 API 鍝嶅簲 |
| `strategy/convertible_bond/service.py` | 杞€哄鍒╀笟鍔¤绠楋細鍙屼綆绛栫暐銆佺悊璁烘敹鐩婄巼銆佸洖鍞鍒?|
| `strategy/convertible_bond/service.js` | 杞€哄鍒?Node 閫傞厤鍣細璁＄畻缁撴灉鏍煎紡鍖栥€佹姌浠风瓥鐣ョ姸鎬?|
| `strategy/merger/service.py` | 骞惰喘濂楀埄涓氬姟璁＄畻锛欴eal 鍒嗘瀽銆丄I 鎶ュ憡鐢熸垚 |
| `strategy/merger/service.js` | 骞惰喘濂楀埄 Node 閫傞厤鍣細鎶ュ憡鐢熸垚璋冨害 |
| `strategy/lof_iopv/calc.py` | 鍏变韩IOPV璁＄畻鍏紡锛歍10鎸佷粨鍔犳潈娉曪紙浠庡噣鍊兼姭闇叉棩鎸夋寔浠撴帹绠楋級 |
| `strategy/lof_iopv/service.py` | QDII LOF IOPV涓氬姟璁＄畻锛氫笁鍒嗙被鎸佷粨鏉ユ簮+鍝嶅簲鏋勫缓+鐩戞帶姹犵瓫閫?|
| `strategy/custom_monitor/service.py` | 鑷畾涔夌洃鎺т笟鍔¤绠楋細缁勫悎鏀剁泭鐜囥€佸浠疯绠?|
| `strategy/dividend/service.py` | 鑲℃伅涓氬姟璁＄畻锛氱櫥璁版棩璺熻釜銆佽偂鎭巼璁＄畻 |
| `strategy/subscription/service.py` | 鐢宠喘涓氬姟璁＄畻锛氱敵璐簨浠惰窡韪笌鐘舵€佺鐞?|
| `strategy/event_arbitrage/service.py` | 浜嬩欢濂楀埄涓氬姟璁＄畻锛氫簨浠跺尮閰嶄笌杩囨护瑙勫垯 |
| `strategy/cb_rights_issue/service.py` | 鎶㈡潈閰嶅敭涓氬姟璁＄畻锛氶鏈熸敹鐩娿€侀樁娈靛垽瀹氥€佸叆姹犲垽鏂?|

### 9.4 ui/ 鈥?API 涓庡睍绀哄眰

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `ui/routes/market_routes.js` | 甯傚満琛屾儏 API 璺敱锛?api/market/* 绔偣瀹氫箟 |
| `ui/routes/dashboard_routes.js` | 鐪嬫澘 API 璺敱锛?api/dashboard/* 绔偣瀹氫箟 |
| `ui/routes/push_routes.js` | 鎺ㄩ€侀厤缃?API 璺敱锛?api/push/* 绔偣瀹氫箟 |
| `ui/view_models/overview.js` | 鐪嬫澘姒傝鏁版嵁缁勮锛氳仛鍚堝悇妯″潡鏁版嵁涓虹粺涓€瑙嗗浘 |
| `ui/view_models/push_payload.js` | 鎺ㄩ€侀厤缃搷搴旀牸寮忥細鎺ㄩ€侀厤缃暟鎹粨鏋勬暣褰?|
| `ui/dashboard/constants.js` | 鐪嬫澘 UI 甯搁噺锛氱鐐广€乀ab 搴忓垪銆佽〃鏍奸厤缃€佹牱寮忛粯璁ゅ€?|
| `ui/dashboard/dashboard_page.js` | 鏃х湅鏉块〉闈㈤€昏緫锛欻TML 鐪嬫澘娓叉煋涓庝氦浜?|
| `ui/templates/dashboard_template.html` | 鏃х湅鏉?HTML 妯℃澘锛氬惈鍐呰仈 CSS/JS |
| `ui/src/components/ConvertibleCardList.jsx` | 杞€哄鍒╃畝娲佹ā鍧楄〃鏍硷細灏介噺杩樺師鏃х綉椤电琛ㄦ牸椋庢牸 |
| `ui/src/components/AhCardList.jsx` | AH 婧环绠€娲佹ā鍧楄〃鏍硷細灏介噺杩樺師鏃х綉椤电琛ㄦ牸椋庢牸 |
| `ui/src/components/AbCardList.jsx` | AB 婧环绠€娲佹ā鍧楄〃鏍硷細灏介噺杩樺師鏃х綉椤电琛ㄦ牸椋庢牸 |
| `ui/src/components/LofCardList.jsx` | LOF 濂楀埄绠€娲佹ā鍧楄〃鏍硷細灏介噺杩樺師鏃х綉椤电琛ㄦ牸椋庢牸 |
| `ui/src/components/SubscriptionCardList.jsx` | 鎵撴柊鐢宠喘绠€娲佹ā鍧楄〃鏍硷細灏介噺杩樺師鏃х綉椤电琛ㄦ牸椋庢牸 |
| `ui/src/components/RightsIssueCardList.jsx` | 鎶㈡潈閰嶅敭绠€娲佹ā鍧楄〃鏍硷細娌繁甯傚満涓庝笁闃舵鍒囨崲 |
| `ui/src/components/MonitorCardList.jsx` | 鑷畾涔夌洃鎺х畝娲佹ā鍧楄〃鏍硷細淇濈暀缂栬緫鍒犻櫎鎿嶄綔 |
| `ui/src/components/cardHelpers.jsx` | React 鍏叡鏍煎紡鍖栦笌杞婚噺灞曠ず绉湪 |
| `ui/src/components/cardListHelpers.jsx` | React 鍘嗗彶瀵嗛泦琛屽３甯姪鍑芥暟 |
| `ui/src/components/SimpleDataTable.jsx` | React 绠€娲佹ā鍧楄〃鏍煎叕鍏辩粍浠?|
| `ui/src/components/BottomNav.jsx` | 鎵嬫満绔簳閮ㄥ鑸爮锛氬浐瀹氬簳閮ㄥ垏鎹?7 涓?React 椤剁骇鏍囩 |

### 9.5 notification/ 鈥?鎺ㄩ€佷笌璋冨害灞?

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `notification/wecom/client.js` | 浼佷笟寰俊瀹㈡埛绔細鍙戦€?Markdown 鍒?Webhook |
| `notification/scheduler/wecom_scheduler.js` | 鎺ㄩ€佽皟搴﹀櫒锛氬畾鏃?tick 瑙﹀彂鍚勬ā鍧楁帹閫?|
| `notification/scheduler/push_config_store.js` | 鎺ㄩ€侀厤缃瓨鍌細涓绘帹閫侀厤缃鍐?|
| `notification/scheduler/push_runtime_store.js` | 鎺ㄩ€佽繍琛屾椂瀛樺偍锛氭帹閫佺姸鎬佷笌鍘嗗彶 |
| `notification/summary/main_summary.js` | 姣忔棩鎽樿缁勮锛氳仛鍚堟墍鏈夋ā鍧楃敓鎴愭帹閫?Markdown |
| `notification/alerts/event_alert_service.js` | 浜嬩欢鍛婅鏈嶅姟锛氭姌浠风瓥鐣ヤ拱鍏?鍗栧嚭/鐩戞帶瀹炴椂鎺ㄩ€?|
| `notification/cb_arbitrage/service.js` | 杞€哄鍒╂帹閫侊細鐙珛鎺ㄩ€侀€昏緫涓庢牸寮忓寲 |
| `notification/cb_rights_issue/service.js` | 鎶㈡潈閰嶅敭鎺ㄩ€侊細鐙珛鎺ㄩ€侀€昏緫涓庢牸寮忓寲 |
| `notification/lof_iopv/service.js` | QDII LOF IOPV 鎺ㄩ€侊細鐙珛鎺ㄩ€侀€昏緫涓庢牸寮忓寲 |
| `notification/merger_report/service.js` | 骞惰喘鎶ュ憡鎺ㄩ€侊細DeepSeek AI 鎶ュ憡鐢熸垚涓庢帹閫?|
| `notification/styles/markdown_style.js` | 鎺ㄩ€?Markdown 鏍峰紡锛氶€氱敤鏍煎紡鍖栨ā鏉?|

### 9.6 shared/ 鈥?璺ㄥ眰閫氱敤鑳藉姏

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `shared/config/node_config.js` | Node 閰嶇疆璇诲彇鍣細YAML 瑙ｆ瀽 + 鐜鍙橀噺/Secrets 娉ㄥ叆 |
| `shared/config/script_config.py` | Python 閰嶇疆璇诲彇鍣細YAML 瑙ｆ瀽 + 鐜鍙橀噺/Secrets 娉ㄥ叆 |
| `shared/bus/market_record.js` | Bus 鏍囧噯鍖栬褰曪紙JS锛夛細璺ㄥ眰閫氫俊鏁版嵁缁撴瀯 |
| `shared/bus/market_record.py` | Bus 鏍囧噯鍖栬褰曪紙Python锛夛細璺ㄥ眰閫氫俊鏁版嵁缁撴瀯 |
| `shared/runtime/json_store.js` | JSON 鎸佷箙鍖栵紙JS锛夛細杩愯鏃剁姸鎬佽鍐?|
| `shared/runtime/json_store.py` | JSON 鎸佷箙鍖栵紙Python锛夛細杩愯鏃剁姸鎬佽鍐?|
| `shared/runtime/state_registry.js` | 鐘舵€佹敞鍐岃〃锛圝S锛夛細杩愯鏃舵枃浠剁粺涓€绠＄悊 |
| `shared/runtime/state_registry.py` | 鐘舵€佹敞鍐岃〃锛圥ython锛夛細杩愯鏃舵枃浠剁粺涓€绠＄悊 |
| `shared/time/shanghai_time.js` | 涓婃捣鏃跺尯锛圝S锛夛細浜ゆ槗鏃舵妫€娴嬨€佸競鍦烘椂闂?|
| `shared/time/shanghai_time.py` | 涓婃捣鏃跺尯锛圥ython锛夛細浜ゆ槗鏃舵妫€娴嬨€佸競鍦烘椂闂?|
| `shared/paths/node_paths.js` | 璺緞瑙ｆ瀽锛圝S锛夛細杩愯鏃剁洰褰曘€佹暟鎹簱璺緞 |
| `shared/paths/script_paths.py` | 璺緞瑙ｆ瀽锛圥ython锛夛細杩愯鏃剁洰褰曘€佹暟鎹簱璺緞 |
| `shared/models/service_result.js` | 鏍囧噯鍝嶅簲鍖呰锛圝S锛夛細鎴愬姛/閿欒鍝嶅簲鏍煎紡 |
| `shared/models/service_result.py` | 鏍囧噯鍝嶅簲鍖呰锛圥ython锛夛細鎴愬姛/閿欒鍝嶅簲鏍煎紡 |
| `shared/market_service.py` | 璺ㄥ競鍦哄伐鍏凤細浠锋牸鏌ヨ銆侀厤瀵瑰尮閰嶃€佽偂绁ㄦ悳绱?|
| `shared/utils/ranking.js` | 閫氱敤鎺掑簭宸ュ叿锛氭寜瀛楁鍗囬檷搴忓彇 Top N |


### 9.7.1 tools/backtest/ -- LOF/QDII 鍥炴祴鑴氭湰

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `ools/backtest/lof13_backtest_A.py` | ~~宸插簾寮冿細A绫绘寚鏁版硶鍥炴祴~~ |
| `ools/backtest/lof13_backtest_B.py` | LOF T10鎸佷粨娉曞洖娴嬶細鍓嶅崄澶ф寔浠撳姞鏉冧及鍊?|
| 	ools/backtest/lof13_backtest_report.md | 13鍙狶OF浼板€兼柟娉曞洖娴嬫姤鍛?|
| `ools/backtest/qdii_backtest_A.py` | ~~宸插簾寮冿細A绫绘寚鏁版硶鍥炴祴~~ |
| `ools/backtest/qdii_backtest_B.py` | QDII T10鎸佷粨娉曞洖娴嬶紙娓偂/缇庤偂娣峰悎鍩洪噾锛?|
| 	ools/backtest/qdii_v6_backtest.py | QDII v6鍥炴祴鑴氭湰锛堟棩鏈熷榻愮増锛?|
### 9.7 scripts/ 鈥?鑴氭湰

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `scripts/add_ai_summary.py` | 鎵归噺娣诲姞 AI-SUMMARY 娉ㄩ噴 |
| `scripts/audit_ah_history_coverage.py` | AH 鍘嗗彶瑕嗙洊瀹¤ |
| `scripts/check_plugin_boundaries.py` | 鏋舵瀯杈圭晫妫€鏌ワ細楠岃瘉鎻掍欢闂存棤闈炴硶渚濊禆 |
| `scripts/check_root_cleanliness.py` | 鏍圭洰褰曟竻娲佹鏌?|
| `scripts/rebuild_premium_db.py` | 婧环鍘嗗彶鏁版嵁搴撻噸寤猴細AH/AB 婧环鍘嗗彶缁存姢 |
| `scripts/stock_price_history_db.py` | 鑲′环鍘嗗彶鏁版嵁搴擄細姝ｈ偂 K 绾挎暟鎹鐞?|
| `scripts/premium_history_db.py` | 婧环鍘嗗彶鏁版嵁搴擄細婧环鐜囧巻鍙叉暟鎹鐞?|
| `scripts/lof_maintenance.py` | LOF鏁版嵁搴撴瘡鏃ョ淮鎶わ細鏇存柊+娓呯悊+鏃ュ織 |
| `scripts/export_pair_pool.py` | 閰嶅姹犲鍑猴細AH/AB 閰嶅琛ㄧ敓鎴?|

### 9.8 tests/ 鈥?娴嬭瘯

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `tests/smoke_check.js` | 鍐掔儫娴嬭瘯锛氶獙璇佹湇鍔￠椤靛拰 health 绔偣鍙揪 |

### 9.9 config/ 鈥?閰嶇疆鏂囦欢

| 鏂囦欢 | 鑱岃矗鎽樿 |
|------|----------|
| `config/config.yaml` | 涓氬姟閰嶇疆鍚堝悓锛氭墍鏈夊弬鏁般€侀槇鍊笺€乁RL銆佸紑鍏崇殑鍗曚竴鏉ユ簮 |
| `config/secrets.yaml` | 鏁忔劅閰嶇疆锛欰PI Key銆乄ebhook銆佸瘑鐮侊紙gitignored锛?|
| `config/server_profile.local.yaml` | 鏈嶅姟鍣ㄨ繛鎺ラ厤缃細SSH host/user/port/password锛坓itignored锛?|

