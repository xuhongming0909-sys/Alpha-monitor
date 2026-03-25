# Alpha Monitor 瑙勬牸璇存槑

## 1. 鏂囨。瑙勫垯
- `REQUIREMENTS.md` 鏄?PM 瑙嗚鐨勯渶姹傚悎鍚屻€?- 鏈枃浠舵槸椤甸潰缁撴瀯銆佹帴鍙ｇ粦瀹氥€佽〃鏍间氦浜掑拰涓氬姟閫昏緫瀛楀吀鐨勫疄鐜板悎鍚屻€?- 鏈疆鍥哄畾閬靛畧锛氬厛鏀规枃妗ｏ紝鍐嶆敼浠ｇ爜锛屾渶鍚庡仛涓€鑷存€ф牳瀵广€?
## 2. 椤甸潰涓庢帴鍙ｅ悎鍚?
### 2.1 鍥哄畾鎺ュ彛
椤甸潰灞傜户缁彧娑堣垂鐜版湁鎺ュ彛锛?- `姹囩巼`锛歚/api/market/exchange-rate`
- `鍗佸勾鏈熷浗鍊烘敹鐩婄巼`锛歚/api/market/convertible-bond-arbitrage`
- `鏂拌偂鎵撴柊`锛歚/api/market/ipo`
- `鍙浆鍊烘墦鏂癭锛歚/api/market/convertible-bonds`
- `杞€哄鍒ー锛歚/api/market/convertible-bond-arbitrage`
- `AH婧环`锛歚/api/market/ah`
- `AB婧环`锛歚/api/market/ab`
- `鐩戞帶濂楀埄`锛歚/api/monitors`
- `鍒嗙孩鎻愰啋`锛歚/api/dividend?action=refresh`
- `鏀惰喘绉佹湁`锛歚/api/market/merger`
- `灞曠ず閰嶇疆`锛歚GET /api/dashboard/ui-config`
- `鎺ㄩ€佽缃甡锛歚GET /api/push/config`銆乣POST /api/push/config`

### 2.2 棣栭〉缁撴瀯鍚堝悓
棣栭〉涓ユ牸閲囩敤浠ヤ笅椤哄簭锛?1. 鏍囬鍖猴細鍙繚鐣?`Alpha Monitor` 鏍囬銆?2. 椤堕儴鐘舵€佽锛氫竴琛屾樉绀?`HKD/CNY`銆乣USD/CNY`銆佸崄骞存湡鍥藉€烘敹鐩婄巼銆佹洿鏂版椂闂淬€?3. 椤堕儴鍔熻兘鍖猴細
   - 浠呬繚鐣?`鑲″€烘墦鏂癭 浠婃棩浜嬮」闀胯〃銆?4. 涓诲鑸?tab锛?   - `杞€哄鍒ー
   - `AH婧环`
   - `AB婧环`
   - `LOF濂楀埄`
   - `鐩戞帶濂楀埄`
   - `鍒嗙孩鎻愰啋`
   - `浜嬩欢濂楀埄`
5. 涓诲姛鑳介潰鏉匡細鏍规嵁褰撳墠 tab 灞曠ず瀵瑰簲鐪熷疄鏁版嵁銆?6. 椤甸潰鏈熬锛氭覆鏌撶畝娲佺増 `鎺ㄩ€佽缃甡 缂栬緫鍖恒€?
棣栭〉涓嶅厑璁稿啀鍑虹幇锛?- `甯傚満鍔ㄦ€乣
- `浠婃棩姒傚喌`
- `閲嶇偣鏈轰細鎽樿`
- 鏍囬涓嬫柟闀胯鏄?- 鎸夎祫浜х被鍨嬫媶寮€鐨勫弻鍒楁墦鏂板崱鐗?- 鎺ㄩ€佽缃腑鐨勯暱娈佃В閲婃枃妗?
### 2.3 椤堕儴鐘舵€佽鍚堝悓
鐘舵€佽蹇呴』灞曠ず锛?- `HKD/CNY`
- `USD/CNY`
- `鍗佸勾鏈熷浗鍊烘敹鐩婄巼`
- 鏈€鏂版洿鏂版椂闂?
瑙勫垯锛?- 涓嶆樉绀哄崄骞存湡鍥藉€烘棩鏈熴€?- `treasuryYield10y` 缂哄け鏃讹紝鏂囨蹇呴』鏄剧ず `鍗佸勾鏈熷浗鍊烘敹鐩婄巼 鏆傛湭杩斿洖`銆?- 鐘舵€佽鏄崟琛屾枃鏈俊鎭甫锛屼笉鍐嶆覆鏌撲负鐙珛澶ч潰鏉裤€?
### 2.4 鑲″€烘墦鏂伴暱琛ㄥ悎鍚?椤堕儴鎵撴柊鍖哄繀椤绘敼鎴愨€滀粎浠婃棩浜嬮」鈥濈殑妯悜闀胯〃銆?
鍥哄畾瑙勫垯锛?- 鍙敹鏁涗粖澶╃浉鍏崇殑鏉＄洰锛?  - `subscribeDate = today`
  - `paymentDate = today`
  - `listingDate = today`
- 琛ㄥご鑷冲皯灞曠ず锛?  - `褰撳墠闃舵`
  - `绫诲瀷`
  - `鍚嶇О/浠ｇ爜`
  - `鐢宠喘鏃
  - `涓缂存鏃
  - `涓婂競鏃
  - `鐢宠喘涓婇檺`
  - `鍙戣浠?杞偂浠穈
- 椤甸潰涓嶅啀鍗曠嫭灞曠ず `鎶界鏃 鍒椼€?- 椤甸潰灞曠ず鐨?`涓缂存鏃 鍒楁湰杞浐瀹氳鍙?`lotteryDate`銆?- `浠婃棩涓缂存` 闃舵鍒ゆ柇涔熷浐瀹氳鍙?`lotteryDate`锛屼笌灞曠ず鍙ｅ緞淇濇寔涓€鑷淬€?- 鍚屼竴寮犺〃鍐呮贩鎺掓柊鑲″拰杞€恒€?- `褰撳墠闃舵` 浣跨敤鍒嗚壊鏍囩鍖哄垎锛?  - `浠婃棩鐢宠喘`
  - `浠婃棩涓缂存`
  - `浠婃棩涓婂競`
- 鏃犳暟鎹椂锛岃〃鍐呮槑纭樉绀?`浠婃棩鏃犳暟鎹甡銆?
### 2.5 鎺ㄩ€佽缃悎鍚?- 闈㈡澘鏍囬鍥哄畾涓?`鎺ㄩ€佽缃甡銆?- 鍙繚鐣?3 涓椂闂存锛?  - 鏃堕棿妗?1锛氬父瑙勬ā鍧椾富鎺ㄩ€?  - 鏃堕棿妗?2锛氬父瑙勬ā鍧椾富鎺ㄩ€?  - 鏃堕棿妗?3锛氭敹璐鏈変笓鎶ユ帹閫?- 椤甸潰蹇呴』鏀寔璇诲彇褰撳墠閰嶇疆骞朵繚瀛樹慨鏀圭粨鏋溿€?- 鎺ㄩ€佽缃浐瀹氭斁鍦ㄦ暣椤?tab 闈㈡澘涔嬪悗鐨勯〉闈㈡湯灏撅紝涓嶅啀鍗犵敤椤堕儴鍙充晶鍖哄煙銆?- 甯冨眬涓烘棤澶ц竟妗嗙殑绠€娲佹潯甯︼紝鍙繚鐣欑姸鎬佹枃瀛椼€佹椂闂存銆佷繚瀛樻寜閽拰鍒锋柊鎸夐挳銆?- 姣忔璇诲彇鎴愬姛鍚庯紝3 涓椂闂存閮藉繀椤讳互鏈€鏂版帴鍙ｈ繑鍥炲€煎埛鏂帮紝涓嶈兘浠呭湪杈撳叆妗嗕负绌烘椂濉厖銆?- 淇濆瓨鎴愬姛鍚庯紝椤甸潰蹇呴』鐩存帴浣跨敤 `POST /api/push/config` 杩斿洖缁撴灉鍥炲啓鐘舵€佹枃妗堝拰 3 涓椂闂存銆?
## 3. 閫氱敤琛ㄦ牸绯荤粺鍚堝悓

### 3.1 鐢熸晥鑼冨洿
鏈疆缁熶竴鍗囩骇浠ヤ笅 3 寮犱富琛細
- `杞€哄鍒ー
- `AH婧环`
- `AB婧环`

### 3.2 鐘舵€佹ā鍨?姣忓紶琛ㄨ嚦灏戠淮鎶や互涓嬪墠绔姸鎬侊細
- 褰撳墠鎺掑簭瀛楁
- 褰撳墠鎺掑簭鏂瑰悜
- 褰撳墠椤电爜
- 姣忛〉鏉℃暟

榛樿鍊硷細
- 姣忛〉鏉℃暟鍥哄畾涓?`50`
- `杞€哄鍒ー 鍒濆淇濇寔鎺ュ彛鍘熷椤哄簭
- `AH婧环 / AB婧环` 鍒濆鎸?`婧环鐜嘸 闄嶅簭
- `鐩戞帶濂楀埄` 鍒濆鎸夆€滄渶浼樻敹鐩婄巼鈥濋檷搴?- `鍒嗙孩鎻愰啋` 鍒濆鎸夆€滆偂鎭巼鈥濋檷搴?- `鏀惰喘绉佹湁` 鍒濆鎸夆€滃叕鍛婃椂闂粹€濆€掑簭

### 3.3 琛ㄥご鎺掑簭瑙勫垯
- 鍙湁澹版槑涓哄彲鎺掑簭鐨勮〃澶存墠鍝嶅簲鐐瑰嚮銆?- 棣栨鐐瑰嚮鏌愬瓧娈垫椂锛屼娇鐢ㄨ瀛楁榛樿鎺掑簭鏂瑰悜銆?- 鍐嶆鐐瑰嚮鍚屼竴瀛楁鏃讹紝鍦ㄥ崌搴?/ 闄嶅簭涔嬮棿鍒囨崲銆?- 鍒囨崲鍒板叾浠栧瓧娈垫椂锛岄噸缃负璇ュ瓧娈甸粯璁ゆ柟鍚戙€?- 褰撳墠鎺掑簭瀛楁蹇呴』鏈夋槑纭縺娲绘€佸拰鏂瑰悜鎻愮ず銆?
### 3.4 鍒嗛〉瑙勫垯
- 姣忛〉鍥哄畾 `50` 鏉°€?- 鍒嗛〉鎺т欢鑷冲皯鍖呭惈锛?  - 棣栭〉
  - 涓婁竴椤?  - 褰撳墠椤?/ 鎬婚〉鏁?  - 涓嬩竴椤?  - 鏈〉
  - 鎬绘潯鏁?- 搴忓彿鍒楀繀椤绘寜鈥滃綋鍓嶆帓搴忕粨鏋?+ 褰撳墠鍒嗛〉浣嶇疆鈥濊繛缁绠楋紝涓嶅厑璁哥洿鎺ヤ娇鐢ㄥ師濮嬫暟缁勪笅鏍囥€?
### 3.5 鍝嶅簲寮忚鍒?- 鐢佃剳绔細椤甸潰涓讳綋浣跨敤鎺ヨ繎婊″睆甯冨眬锛岄暱琛ㄥ厑璁歌嚜鐢辨í鍚戝拰绾靛悜婊氬姩銆?- 鎵嬫満绔細涓嶆媶绗簩濂楅〉闈紝淇濈暀鍚屼竴濂楄〃鏍艰涔夛紝閫氳繃鍗曞垪鍫嗗彔鍜屾í鍚戞粴鍔ㄤ繚璇佸彲鐢ㄣ€?- 闀胯〃鍖哄煙蹇呴』淇濈暀娓呮櫚鐨勮〃澶淬€佹粴鍔ㄨ竟鐣屽拰鍒嗛〉鎺т欢銆?- 鍏ㄥ眬鍩虹瀛楀彿銆乼ab銆佹寜閽€佽緭鍏ユ銆佽〃澶村拰琛ㄦ牸姝ｆ枃蹇呴』缁熶竴涓婅皟锛屼繚璇佹闈㈢闀挎椂闂撮槄璇讳笉鍚冨姏銆?
## 4. 鍔熻兘椤靛悎鍚?
### 4.1 杞€哄鍒?杞€哄鍒╅〉闈㈢粨鏋勫浐瀹氫负锛?1. 鏍囬涓庢洿鏂版椂闂?2. 绱у噾鎽樿鍖?3. 涓昏〃
4. 鍒嗛〉鍖?
涓嶅啀淇濈暀鏃х増澶ф寚鏍囨潯甯︼紝涔熶笉鍏佽涓夊紶楂樺崰鐢ㄦ憳瑕佸崱鎶婇灞忓ぇ閲忔尋鎺夈€?
鎽樿鍖哄悎鍚岋細
- 淇濈暀 3 缁勬憳瑕侊細
  - `鍙屼綆闈犲墠`
  - `鐞嗚婧环鐜囬潬鍓峘
  - `杞偂濂楀埄鍊欓€塦
- 鎽樿甯冨眬鍙傝€?`AH / AB` 鐨勫垎鏍忕З搴忥紝浣嗗瘑搴︽洿楂橈紝鏉＄洰鏁版洿灏戙€?- 妗岄潰绔紭鍏堜娇鐢ㄧ揣鍑戝鏍忓竷灞€锛岀Щ鍔ㄧ鍥炶惤涓哄崟鍒楀爢鍙犮€?- 姣忕粍鎽樿榛樿鏈€澶氭樉绀?`3` 鏉★紝閬垮厤绾靛悜绌洪棿澶辨帶銆?
涓昏〃鍥哄畾瀛楁椤哄簭涓猴細
- `搴忓彿`
- `杞€轰唬鐮乣
- `杞€哄悕绉癭
- `姝ｈ偂浠ｇ爜`
- `姝ｈ偂鍚嶇О`
- `杞€虹幇浠穈
- `杞€烘定璺屽箙`
- `姝ｈ偂鐜颁环`
- `姝ｈ偂娑ㄨ穼骞卄
- `杞偂浠穈
- `杞偂浠峰€糮
- `杞偂婧环鐜嘸
- `鍙屼綆`
- `鐞嗚婧环鐜嘸
- `璇勭骇`
- `鍓╀綑骞撮檺`
- `鍓╀綑瑙勬ā(浜?`
- `鎴愪氦棰?浜?`
- `鍒版湡绋庡墠鏀剁泭鐜嘸
- `涓婂競鏃
- `杞偂璧峰鏃

鍙帓搴忓瓧娈佃嚦灏戝寘鎷細
- `杞€虹幇浠穈
- `杞偂浠峰€糮
- `杞偂婧环鐜嘸
- `鍙屼綆`
- `鐞嗚婧环鐜嘸
- `鍓╀綑骞撮檺`
- `鍓╀綑瑙勬ā(浜?`
- `鎴愪氦棰?浜?`
- `鍒版湡绋庡墠鏀剁泭鐜嘸
- `涓婂競鏃
- `杞偂璧峰鏃

### 4.2 AH / AB 鍏辩敤楠ㄦ灦
AH 鍜?AB 椤甸潰蹇呴』浣跨敤瀹屽叏鐩稿悓鐨勫竷灞€鍜屾牱寮忥紝鍙厑璁搁€氳繃瀛楁鏄犲皠鍖哄垎锛?- AH锛?  - `瀵规墜浠ｇ爜 = hCode`
  - `瀵规墜鍚嶇О = hName`
  - `瀵规墜甯傚満浠?= hPrice`
  - `瀵规墜浜烘皯甯佷环 = hPriceCny`
- AB锛?  - `瀵规墜浠ｇ爜 = bCode`
  - `瀵规墜鍚嶇О = bName`
  - `瀵规墜甯傚満浠?= bPrice`
  - `瀵规墜浜烘皯甯佷环 = bPriceCny`

椤甸潰缁撴瀯鍥哄畾涓猴細
1. 鏍囬涓庢洿鏂版椂闂?2. 鍙屾憳瑕佸尯
3. 涓昏〃
4. 鏍锋湰璇存槑鍖?5. 鍒嗛〉鍖?
### 4.3 AH / AB 鎽樿鍚堝悓
- 椤堕儴蹇呴』淇濈暀涓ゅ潡鎽樿锛?  - 宸︿晶锛氬墠涓?  - 鍙充晶锛氬€掓暟鍓嶄笁
- 褰撲富鎺掑簭瀛楁涓?`premium` 鏃讹細
  - 鎽樿鏍囬鏄剧ず `婧环鐜囧墠涓塦 / `婧环鐜囧€掓暟鍓嶄笁`
- 褰撲富鎺掑簭瀛楁涓?`percentile` 鏃讹細
  - 鎽樿鏍囬鏄剧ず `杩戜笁骞寸櫨鍒嗕綅鍓嶄笁` / `杩戜笁骞寸櫨鍒嗕綅鍊掓暟鍓嶄笁`
- 鎽樿鎺掑簭璺熼殢褰撳墠涓绘帓搴忓瓧娈碉紝涓嶅啀棰濆缁存姢绗簩濂楁憳瑕佹帓搴忕姸鎬併€?
### 4.4 AH / AB 涓昏〃鍚堝悓
涓昏〃鍥哄畾瀛楁椤哄簭涓猴細
- `搴忓彿`
- `A鑲′唬鐮乣
- `A鑲″悕绉癭
- `H鑲′唬鐮?/ B鑲′唬鐮乣
- `H鑲″悕绉?/ B鑲″悕绉癭
- `A鑲′环`
- `H鑲′环 / B鑲′环`
- `瀵规墜浜烘皯甯佷环`
- `浠峰樊`
- `婧环鐜嘸
- `杩戜笁骞寸櫨鍒嗕綅`
- `鏍锋湰鍖洪棿`

瑙勫垯锛?- `浠峰樊 = 瀵规墜浜烘皯甯佷环 - A鑲′环`
- `杩戜笁骞寸櫨鍒嗕綅` 鏄 `percentile` 鐨勭畝鍖栨樉绀哄悕绉?- 涓昏〃涓嶅崟鐙樉绀?`historyCount`
- `鏍锋湰鍖洪棿` 蹇呴』鍘嬬缉涓?`YYMMDD-YYMMDD`

鍙帓搴忓瓧娈佃嚦灏戝寘鎷細
- `A鑲′环`
- `瀵规墜浜烘皯甯佷环`
- `浠峰樊`
- `婧环鐜嘸
- `杩戜笁骞寸櫨鍒嗕綅`

### 4.5 鐩戞帶濂楀埄
鐩戞帶濂楀埄椤甸潰缁撴瀯鍥哄畾涓猴細
1. 鏍囬涓庢洿鏂版椂闂?2. 鏂板 / 缂栬緫琛ㄥ崟鍖?3. 瀹炴椂鐩戞帶涓昏〃
4. 鍒嗛〉鍖?
涓昏〃蹇呴』灞曠ず锛?- 鐩戞帶鍚嶇О
- 鏀惰喘鏂瑰悕绉颁笌鑲′环
- 鐩爣鏂瑰悕绉颁笌鑲′环
- 鎹㈣偂姣斾緥
- 瀹夊叏绯绘暟
- 鐞嗚瀵逛环璁＄畻璇存槑
- 鑲＄エ鑵跨悊璁哄浠?- 鑲＄エ鑵夸环宸?- 鑲＄エ鑵挎敹鐩婄巼
- 鐜伴噾鑵垮浠?- 鐜伴噾鑵夸环宸?- 鐜伴噾鑵挎敹鐩婄巼

瑙勫垯锛?- 椤堕儴琛ㄥ崟浣跨敤鍚屼竴涓繚瀛樺叆鍙ｅ悓鏃舵敮鎸佹柊澧炰笌缂栬緫銆?- 缂栬緫宸叉湁椤圭洰鏃讹紝`POST /api/monitors` 蹇呴』鎼哄甫鐜版湁 `id` 骞惰鐩栬鏉＄洃鎺у弬鏁般€?- 涓昏〃浣跨敤鍏变韩鍒嗛〉琛ㄦ牸娓叉煋璺緞锛屼笉鍏佽缁х画浣跨敤涓嶅彲鍒嗛〉鐨勫崟鐙畝琛ㄥ疄鐜般€?- 琛ュ厖鍙傛暟鍖哄浐瀹氱洿鎺ユ樉绀哄湪姣忎釜涓昏涓嬫柟锛屼笉鍐嶄繚鐣欏崟鐙殑 `璇︽儏` 鎺у埗鍒椼€?- 琛ュ厖鏂囨蹇呴』浣跨敤鐪熷疄涓氬姟鍚嶈瘝锛屼緥濡?`鐞嗚瀵逛环璁＄畻璇存槑`锛屼笉寰椾娇鐢ㄤ笉鍑嗙‘鐨勮嚜閫犳爣绛俱€?- 榛樿鎸夆€滄渶浼樻敹鐩婄巼鈥濋檷搴忋€?- 姣忛〉鍥哄畾 `50` 鏉°€?
### 4.6 鍒嗙孩鎻愰啋
鍒嗙孩鎻愰啋椤甸潰缁撴瀯鍥哄畾涓猴細
1. 浠婃棩鐧昏鏃ユ彁閱?2. 瀹屾暣瑙傚療琛?3. 鍒嗛〉鍖?
涓嶅啀淇濈暀椤堕儴缁熻鍗°€?
瑙勫垯锛?- 瀹屾暣瑙傚療琛ㄩ粯璁ゆ寜 `鑲℃伅鐜嘸 闄嶅簭銆?- 姣忛〉鍥哄畾 `50` 鏉°€?
### 4.7 鏀惰喘绉佹湁
鏀惰喘绉佹湁椤甸潰缁撴瀯鍥哄畾涓猴細
1. 鏍囬涓庢洿鏂版椂闂?2. 涓昏〃
3. 鍒嗛〉鍖?
瑙勫垯锛?- 椤甸潰鏄剧ず鍏ㄩ噺鍏憡锛屼笉鍐嶅彧鍙栧綋澶┿€?- 涓昏〃榛樿鎸夊叕鍛婃椂闂村€掑簭銆?- 褰?`announcementDate` 鎴?`announcementTime` 灞炰簬褰撳ぉ鏃讹紝璇ヨ蹇呴』楂樹寒銆?- 楂樹寒琛屽繀椤诲甫 `浠婃棩鍏憡` 瑙掓爣鎴栨爣绛俱€?- 姣忛〉鍥哄畾 `50` 鏉°€?
涓昏〃浼樺厛灞曠ず浠ヤ笅瀛楁涓殑鍙敤椤癸細
- `announcementTime`
- `secCode`
- `secName`
- `dealType`
- `searchKeyword`
- `title`
- `latestPrice`
- `offerPrice`
- `premiumRate`
- `announcementUrl`
- `pdfUrl`

## 5. 瑙嗚涓庝氦浜掑悎鍚?
### 5.1 瑙嗚鏂瑰悜
- 涓昏壊锛氶粦銆佹繁绾€侀噾灞炵伆
- 姘旇川锛氱鎶€鎰?+ 鑹烘湳鎰?- 閲嶇偣锛氳鏁淬€佸眰娆℃竻妤氥€侀暱琛ㄦ槗璇汇€佹闈㈢鍒╃敤鐜囬珮

### 5.2 浜や簰瑙勫垯
鎵€鏈夋ā鍧楀繀椤讳繚鐣欙細
- 鍔犺浇涓?- 鏆傛棤鏁版嵁
- 鍔犺浇澶辫触

鎵€鏈?tab銆佸彲鎺掑簭琛ㄥご銆佸垎椤垫寜閽€佷繚瀛樻寜閽繀椤绘彁渚涳細
- hover 鎬?- active 鎬?- disabled 鎬?
## 6. 涓氬姟閫昏緫涓庤绠楀瓧鍏?鏈珷鏄〉闈㈠睍绀洪€昏緫鐨勫敮涓€璁＄畻鍙ｅ緞鏉ユ簮銆備唬鐮侀€昏緫濡傞渶淇敼锛屽繀椤诲厛鏀规湰绔犮€?
### 6.1 AH婧环
- 鍏紡锛歚AH 婧环 = (H 鑲′汉姘戝竵浠?/ A 鑲′环 - 1) * 100`
- 鍏朵腑锛歚H 鑲′汉姘戝竵浠?= H 鑲′环鏍?* 娓竵鍏戜汉姘戝竵姹囩巼`

### 6.2 AB婧环
- 鍏紡锛歚AB 婧环 = (B 鑲′汉姘戝竵浠?/ A 鑲′环 - 1) * 100`
- 鍏朵腑锛歚B 鑲′汉姘戝竵浠?= B 鑲′环鏍?* 瀵瑰簲姹囩巼`

### 6.3 浠峰樊
- AH / AB 椤甸潰涓殑 `浠峰樊 = 瀵规墜浜烘皯甯佷环 - A鑲′环`

### 6.4 杞偂浠峰€?- 鍏紡锛歚杞偂浠峰€?= 姝ｈ偂浠锋牸 * 100 / 杞偂浠穈

### 6.5 杞€烘孩浠风巼
- 鍏紡锛歚杞€烘孩浠风巼 = (杞€虹幇浠?/ 杞偂浠峰€?- 1) * 100`
- 鑻ヤ笂娓稿凡杩斿洖 `premiumRate`锛岄〉闈紭鍏堝睍绀轰笂娓稿€笺€?
### 6.6 鍙屼綆鍊?- 鍏紡锛歚鍙屼綆鍊?= 杞€虹幇浠?+ 杞€烘孩浠风巼`

### 6.7 杞偂濂楀埄绌洪棿
- 鍏紡锛歚杞偂濂楀埄绌洪棿 = (杞偂浠峰€?- 杞€虹幇浠? / 杞€虹幇浠?* 100`
- 褰撳墠瑙勫垯锛氬彧鏈?`杞偂濂楀埄绌洪棿 > 2%` 鎵嶈繘鍏ュ€欓€夋満浼氶泦鍚堛€?
### 6.8 鐩戞帶濂楀埄鑲＄エ鑵跨悊璁哄浠?- 鍏紡锛歚鑲＄エ鑵跨悊璁哄浠?= 鏀惰喘鏂硅偂浠?* 鎹㈣偂姣斾緥 * 瀹夊叏绯绘暟 + 鐜伴噾鍒嗘淳`

### 6.9 鐩戞帶濂楀埄鑲＄エ鑵挎敹鐩婄巼
- 鍏紡锛歚鑲＄エ鑵挎敹鐩婄巼 = (鑲＄エ鑵跨悊璁哄浠?- 鐩爣鐜颁环) / 鐩爣鐜颁环 * 100`

### 6.10 鐩戞帶濂楀埄鐜伴噾鑵挎敹鐩婄巼
- 鍏紡锛歚鐜伴噾鑵挎敹鐩婄巼 = (鐜伴噾瀵逛环 - 鐩爣鐜颁环) / 鐩爣鐜颁环 * 100`

### 6.11 鑲℃伅鐜?- 鍏紡锛歚鑲℃伅鐜?= 姣忚偂鍒嗙孩 / 褰撳墠鑲′环 * 100`

### 6.12 鑲″€烘墦鏂颁粖鏃ヤ簨浠?- `鐢宠喘鏃?= 浠婂ぉ` 褰掑叆 `浠婃棩鐢宠喘`
- `lotteryDate = 浠婂ぉ` 褰掑叆 `浠婃棩涓缂存`
- `涓婂競鏃?= 浠婂ぉ` 褰掑叆 `浠婃棩涓婂競`

### 6.13 鑲″€烘墦鏂板睍绀烘棩鏈熸槧灏?- 椤堕儴闀胯〃浣跨敤缁熶竴鍙ｅ緞锛?  - `涓缂存鏃 鍒楀浐瀹氭樉绀?`lotteryDate`
  - `浠婃棩涓缂存` 闃舵涔熷浐瀹氭寜 `lotteryDate`
  - `鎶界鏃 涓嶅啀鍗曠嫭鏄剧ず

## 7. 楠屾敹涓庝竴鑷存€ф牳瀵?
### 7.1 椤甸潰楠屾敹
浠ヤ笅鏉′欢蹇呴』鍚屾椂婊¤冻锛?1. 鎵撳紑 `http://127.0.0.1:5000/` 鍚庤兘鐪嬪埌鐪熷疄鏁版嵁銆?2. 椤堕儴鐘舵€佷俊鎭负涓€琛屾枃瀛楋紝涓嶅啀鏄ぇ鍧楃姸鎬佺洅銆?3. `鑲″€烘墦鏂癭 鏄€滀粎浠婃棩浜嬮」鈥濈殑妯悜闀胯〃锛屽苟鏄剧ず鍏抽敭鏃ユ湡涓庣敵璐笂闄愮瓑瀛楁銆?4. `鎺ㄩ€佽缃甡 浣嶄簬椤甸潰鏈熬锛屽彧鏈?3 涓椂闂存锛屼笖鑳戒繚瀛樺苟绔嬪嵆鍥炴樉銆?5. 7 涓富 tab 鍙互鍒囨崲銆?6. `杞€哄鍒?/ AH / AB` 涓昏〃鍧囨柊澧炲簭鍙峰垪銆?7. `杞€哄鍒?/ AH / AB` 涓昏〃鍧囨敮鎸佺偣鍑昏〃澶存帓搴忋€?8. `杞€哄鍒?/ AH / AB` 涓昏〃鍧囨敮鎸佸垎椤碉紝姣忛〉 50 鏉°€?9. `鐩戞帶濂楀埄 / 鍒嗙孩鎻愰啋 / 鏀惰喘绉佹湁` 涓昏〃鍧囨敮鎸佸垎椤碉紝姣忛〉 50 鏉°€?10. `鐩戞帶濂楀埄` 鏀寔鏂板鍜岀紪杈戝凡鏈夌洃鎺э紝涓旇ˉ鍏呭弬鏁板浐瀹氭樉绀哄湪姣忎釜椤圭洰涓嬫柟銆?11. AH / AB 鍚屾椂鏄剧ず鍓嶄笁鍜屽€掓暟鍓嶄笁銆?12. `鏀惰喘绉佹湁` 鏄剧ず鍏ㄩ噺鍏憡锛屼粖鏃ュ叕鍛婇珮浜槑鏄俱€?13. `杞€哄鍒ー 鎽樿鍖烘槑鏄炬洿绱у噾锛屼富琛ㄦ洿鏃╄繘鍏ヨ閲庛€?14. 鐢佃剳绔帴杩戞弧灞忔樉绀猴紝鏁翠綋瀛楀彿鏄庢樉鎻愬崌锛屾墜鏈虹甯冨眬涓嶅帇鍧忋€?15. 棣栭〉淇濇寔 7 涓牴 tab锛屼笖鍖呭惈 `LOF濂楀埄`銆?16. `LOF濂楀埄` 浣滀负棣栭〉鏍规ā鍧楀彲鐩存帴鎵撳紑骞舵覆鏌撶湡瀹?QDII 鏁版嵁銆?17. `GET /api/market/lof-arbitrage` 鍙繑鍥炲彲瑙ｆ瀽鐨?LOF 鏁版嵁銆?18. `GET /api/market/historical-premium` 浠呮帴鍙?`type=AH|AB`銆?
### 7.2 涓€鑷存€ф牳瀵?姣忔淇敼鍚庨兘瑕佸仛涓€娆?`/speckit.analyze` 绛変环鏍稿锛岃嚦灏戞姤鍛婏細
- `AH` 浠ｇ爜涓殑璁＄畻閫昏緫鏄惁涓庢湰鏂囦欢绗?`6.1` 鏉′竴鑷?- `AB` 浠ｇ爜涓殑璁＄畻閫昏緫鏄惁涓庢湰鏂囦欢绗?`6.2` 鏉′竴鑷?
鏈疆榛樿缁撹搴斾负锛?- AH锛氫竴鑷?- AB锛氫竴鑷?
鍘熷洜锛?- 鏈疆涓嶄慨鏀瑰叕寮忥紝鍙慨鏀归〉闈㈠睍绀恒€佹帓搴忋€佸垎椤点€佸瓧娈电粍缁囧拰鍝嶅簲寮忓竷灞€銆?
## 8. 浜戞湇鍔″櫒鍏綉璁块棶鍚堝悓

### 8.1 閮ㄧ讲鐩爣
- 褰撳墠椤圭洰闄や簡鏈湴璋冭瘯澶栵紝蹇呴』鏀寔閮ㄧ讲鍒颁簯鏈嶅姟鍣ㄥ苟闀挎湡瀵瑰鎻愪緵璁块棶銆?- 姝ｅ紡璁块棶鐩爣浠庘€滄湰鏈烘垨灞€鍩熺綉鍙墦寮€鈥濆崌绾т负鈥滀换鎰忓叕缃戠敤鎴锋嬁鍒扮綉鍧€鍗冲彲璁块棶鈥濄€?- 鏈疆璧凤紝浜戞湇鍔″櫒閮ㄧ讲瑙嗕负姝ｅ紡杩愯鐜锛屼笉鍐嶆妸鈥淲indows 鏈満绋冲畾鍚姩鈥濊涓烘渶缁堜氦浠樺舰鎬併€?
### 8.2 瀵瑰璁块棶鍏ュ彛
- 姝ｅ紡瀵瑰鍏ュ彛浼樺厛閲囩敤锛?  - `HTTPS + 鍩熷悕 + 443`
  - 娆￠€変负 `HTTP + 80`
- `http://鍏綉IP:5000/` 鍙厑璁镐綔涓轰复鏃惰皟璇曟垨璇佷功鏈畬鎴愬墠鐨勮繃娓″叆鍙ｃ€?- 椤甸潰姝ｅ紡瀵瑰鍦板潃涓?`/api/health` 蹇呴』缁忚繃鍚屼竴濂楀弽鍚戜唬鐞嗗叆鍙ｆ毚闇诧紝涓嶅厑璁搁椤佃蛋鍩熷悕鑰屽仴搴锋鏌ュ彧鑳芥湰鏈鸿闂€?
### 8.3 鏈嶅姟鍣ㄨ繍琛岄摼璺?- 姝ｅ紡閾捐矾鍥哄畾涓猴細
  - `Node 搴旂敤鏈嶅姟`
  - `鏈嶅姟瀹堟姢灞傦紙systemd 鎴栫瓑浠锋満鍒讹級`
  - `Nginx / Caddy 绛夊弽鍚戜唬鐞哷
  - `鍏綉璁块棶鍏ュ彛`
- 鏈嶅姟瀹堟姢灞傚繀椤绘弧瓒筹細
  - 寮€鏈鸿嚜鍔ㄥ惎鍔?  - 寮傚父閫€鍑鸿嚜鍔ㄦ媺璧?  - 鏃ュ織鍙拷韪?- 鍙嶅悜浠ｇ悊蹇呴』璐熻矗锛?  - 灏嗗叕缃?`80/443` 璇锋眰杞彂鍒板簲鐢ㄥ疄闄呯洃鍚鍙?  - 淇濈暀棣栭〉鍜?`/api/*` 璺敱鍙敤
  - 鍦ㄥ惎鐢?HTTPS 鏃剁鐞嗚瘉涔︾粦瀹?
### 8.4 浜戠綉缁滀笌瀹夊叏瑙勫垯
- 蹇呴』鍚屾椂妫€鏌ュ苟鎵撻€氫互涓嬪眰绾э細
  - 浜戝巶鍟嗗畨鍏ㄧ粍
  - 绯荤粺闃茬伀澧?  - 鍙嶅悜浠ｇ悊鐩戝惉绔彛
  - 搴旂敤瀹為檯鐩戝惉鍦板潃涓庣鍙?- 浠讳綍涓€灞傛湭鏀鹃€氾紝閮借涓衡€滃叕缃戣闂悎鍚屾湭瀹屾垚鈥濄€?- 搴旂敤鐩戝惉鍦板潃缁х画浠?`config.yaml > app.host` 鍜?`config.yaml > app.port` 涓哄敮涓€閰嶇疆鏉ユ簮銆?
### 8.5 鍋ュ悍妫€鏌ュ悎鍚?- `/api/health` 缁х画浣滀负鍞竴姝ｅ紡鍋ュ悍妫€鏌ュ叆鍙ｃ€?- 瀵瑰鍋ュ悍妫€鏌ョ粨鏋滃繀椤昏嚦灏戝寘鍚細
  - `web`
  - `data_jobs`
  - `push_scheduler`
- 鍏綉楠屾敹鏃讹紝棣栭〉鏄惁鍙闂互 `web = ok` 涓虹涓€鍒ゆ柇鏍囧噯銆?- `data_jobs` 鎴?`push_scheduler` 鍑虹幇 `warn` 鏃讹紝涓嶅簲鐩存帴瀵艰嚧棣栭〉涓嶅彲璁块棶銆?
### 8.6 杩愮淮鎿嶄綔鍚堝悓
- 姝ｅ紡杩愯鐜蹇呴』鏈夊浐瀹氬惎鍔ㄣ€佸仠姝€佹鏌ユ柟寮忋€?- 鏈湴/Windows 杈呭姪鑴氭湰鍙互淇濈暀锛屼絾浜戞湇鍔″櫒姝ｅ紡鐜蹇呴』琛ラ綈 Linux 渚ф寮忚繍琛屾柟妗堛€?- 鍚庣画璁″垝鏂囦欢鍜屼换鍔℃枃浠跺繀椤昏鐩栬嚦灏戜互涓嬩簨椤癸細
  - Ubuntu 鏈嶅姟鍣ㄩ儴缃叉楠?  - 鍙嶅悜浠ｇ悊閰嶇疆
  - 鏈嶅姟瀹堟姢閰嶇疆
  - 鍏綉绔彛涓庡畨鍏ㄧ粍鏍稿
  - HTTPS 鎴栬繃娓″叕缃戣闂鏄?
### 8.7 鍏綉閮ㄧ讲楠屾敹
浠ヤ笅鏉′欢蹇呴』鍚屾椂婊¤冻锛屾墠绠楀畬鎴愨€滃叕缃戦暱鏈熷彲璁块棶鈥濓細
1. 鍦ㄥ閮ㄧ綉缁滅幆澧冧笅锛岄€氳繃姝ｅ紡缃戝潃鑳芥墦寮€棣栭〉銆?2. 鏈嶅姟鍣ㄩ噸鍚悗锛屾棤闇€鎵嬪伐杩涘叆缁堢鎵ц鍛戒护锛岀綉椤靛彲鑷姩鎭㈠銆?3. 鎵嬪姩鏉€鎺夌綉椤典富杩涚▼鍚庯紝瀹堟姢鏈哄埗鑳借嚜鍔ㄦ媺璧锋湇鍔°€?4. 姝ｅ紡缃戝潃涓嬬殑 `/api/health` 鍙闂紝涓?`web` 鐘舵€佷负 `ok`銆?5. 鑻ュ凡閰嶇疆鍩熷悕锛屽垯娴忚鍣ㄨ闂紭鍏堜娇鐢?HTTPS锛涜嫢鏆傛湭閰嶇疆鍩熷悕锛屽繀椤诲湪鏂囨。涓槑纭叕缃?IP 璁块棶鍙槸涓存椂杩囨浮鏂规銆?
### 8.8 GitHub 鑷姩閮ㄧ讲鍚堝悓

#### 8.8.1 鍥哄畾閾捐矾
GitHub 鑷姩閮ㄧ讲姝ｅ紡閾捐矾鍥哄畾涓猴細

1. GitHub `main` 鍒嗘敮鏀跺埌 push
2. GitHub Actions 宸ヤ綔娴佽Е鍙?3. Runner 閫氳繃 SSH 鐧诲綍鏈嶅姟鍣?4. 鏈嶅姟鍣ㄦ墽琛岀粺涓€鏇存柊鑴氭湰
5. 鏇存柊鑴氭湰瀹屾垚浠ｇ爜鍚屾銆佷緷璧栧悓姝ャ€佹湇鍔￠噸鍚€佸仴搴锋鏌?
#### 8.8.2 浠撳簱鏂囦欢鍚堝悓
浠撳簱蹇呴』鎻愪緵浠ヤ笅姝ｅ紡鏂囦欢锛?
- `.github/workflows/deploy.yml`
- `tools/deploy/update_from_github.sh`

鑱岃矗绾︽潫锛?
- `deploy.yml` 鍙礋璐ｈЕ鍙戣繙绋嬮儴缃诧紝涓嶅唴宓屽ぇ閲忔湇鍔″櫒涓氬姟閫昏緫
- `deploy.yml` 浠呭厑璁告墽琛屼互涓嬭亴璐ｏ細鏍￠獙 Secrets銆佸噯澶?SSH銆佽Е鍙戣繙绋嬭剼鏈€佽緭鍑洪樁娈垫棩蹇?- `deploy.yml` 绂佹鐩存帴鎵ц `git fetch/reset`銆乣npm ci/install`銆乣systemctl restart` 绛夋湇鍔″櫒涓氬姟姝ラ
- `update_from_github.sh` 浣滀负鏈嶅姟鍣ㄧ粺涓€鏇存柊鍏ュ彛锛屼緵 GitHub Actions 鍜屼汉宸ユ帓闅滃叡鐢?- 宸ヤ綔娴佷腑鐨勬湇鍔″櫒涓氬姟杈撳嚭搴旂敱璇ヨ剼鏈粺涓€浜х敓锛屼究浜庡畾浣嶁€滆剼鏈澶辫触鈥濅笌鈥滆剼鏈唴澶辫触鈥?
#### 8.8.3 鏈嶅姟鍣ㄦ洿鏂拌剼鏈悎鍚?`tools/deploy/update_from_github.sh` 鑷冲皯蹇呴』鎵ц浠ヤ笅姝ラ锛?
1. 瀹氫綅椤圭洰鏍圭洰褰?2. 鎵ц `git fetch --all`
3. 鎵ц `git reset --hard origin/main`
4. 鑻ュ瓨鍦?`package-lock.json`锛屾墽琛?`npm ci`锛涘惁鍒欐墽琛?`npm install`
5. 妫€鏌?`alpha-monitor` 鎴栭厤缃寚瀹氭湇鍔″悕鏄惁瀛樺湪
6. 鑻ユ湇鍔″瓨鍦紝鍒欐墽琛岄噸鍚苟杈撳嚭鐘舵€?7. 瀵规湰鍦?`http://127.0.0.1:app.port/api/health` 鍋氬仴搴锋鏌?
绾︽潫锛?
- 鏈嶅姟鏈畨瑁呮椂锛岃剼鏈繀椤荤粰鍑烘槑纭鍛?- 鍋ュ悍妫€鏌ュけ璐ユ椂锛岃剼鏈繀椤昏繑鍥為潪闆堕€€鍑虹爜
- 鑴氭湰涓嶅緱淇敼涓氬姟鍏紡銆侀〉闈㈠悎鍚屽拰鏁版嵁搴撳彛寰?
#### 8.8.4 GitHub Secrets 鍚堝悓
宸ヤ綔娴侀粯璁や娇鐢ㄤ互涓?Secrets锛?
- `SERVER_HOST`
- `SERVER_USER`
- `SERVER_PORT`
- `SERVER_SSH_KEY`

鍙€夎鐩栭」锛?
- `SERVER_APP_DIR`
- `SERVER_SERVICE_NAME`

榛樿鍊硷細

- `SERVER_APP_DIR = /home/ubuntu/Alpha monitor`
- `SERVER_SERVICE_NAME = alpha-monitor`

#### 8.8.5 琛屼负杈圭晫
- 鑷姩閮ㄧ讲鍙敹鍙ｂ€滀唬鐮佹洿鏂颁笌鏈嶅姟閲嶅惎鈥濓紝涓嶆浛浠ｉ娆℃湇鍔″櫒鍒濆鍖?- 棣栨鍒濆鍖栦粛鐢辩幇鏈?Linux 閮ㄧ讲鑴氭湰璐熻矗锛屼緥濡傦細
  - `tools/deploy/install_systemd.sh`
  - `tools/deploy/install_nginx_site.sh`
- 鑷姩閮ㄧ讲涓嶆柊澧炴柊鐨勫澶?API
- 鑷姩閮ㄧ讲涓嶆洿鏀逛笟鍔¤绠楅€昏緫

#### 8.8.6 鑷姩閮ㄧ讲楠屾敹
浠ヤ笅鏉′欢蹇呴』鍚屾椂婊¤冻锛?
1. 鍚?`main` 鎺ㄩ€佹彁浜ゅ悗锛孏itHub Actions 鑷姩瑙﹀彂
2. 宸ヤ綔娴佽兘閫氳繃 SSH 杩涘叆鐩爣鏈嶅姟鍣ㄥ苟鎵ц鏇存柊鑴氭湰
3. 宸ヤ綔娴?YAML 涓嶉噸澶嶅疄鐜版湇鍔″櫒涓氬姟閫昏緫锛堝 git 鍚屾銆佷緷璧栧畨瑁呫€佹湇鍔￠噸鍚級
4. 鏇存柊鑴氭湰瀹屾垚浠ｇ爜鍚屾涓庝緷璧栧悓姝?5. 鑻ユ湇鍔″凡瀹夎锛屽垯鏈嶅姟鑷姩閲嶅惎
6. `/api/health` 鍦ㄩ儴缃插悗杩斿洖鍙敤缁撴灉锛屼笖 `web = ok`


#### 8.8.7 Deploy Drift Guardrails (2026-03-22)

`tools/deploy/update_from_github.sh` must enforce:
1. `config.yaml` syntax validation before dependency install and service restart.
2. Resolve runtime app port from config, then release stale process owners on that port before restart.
3. Keep systemd unit refresh as the canonical service startup path.
4. After `/api/health` passes, run homepage marker verification on `http://127.0.0.1:${app.port}/`:
   - required marker: `dashboard_page.js`
   - forbidden legacy markers: `app.js|message-form`
5. Marker check failure must terminate deploy with non-zero exit code.
6. Health check must run with retry attempts and delay window to tolerate post-restart warm-up.

## 9. Compact List Rendering Spec (2026-03-22)

### 9.1 Rendering mode
- Desktop-first list rendering mode is fixed to:
  - key columns only in the default row
  - inline detail row expansion for non-key fields
  - strong pagination with default `pageSize = 50`
- Module-internal max-height scroll containers must be removed from primary list rendering.

### 9.2 Expansion interaction
- Each row provides a deterministic expand/collapse action.
- Expanded details render in-place directly below the row and must not navigate away.
- Expansion state is table-scoped and does not alter sorting or pagination behavior.

### 9.3 Error presentation
- Long backend traceback text must not be rendered directly in list panels.
- UI displays a concise error summary with actionable hint text.

## 10. Push API and Scheduler Spec (2026-03-22)

### 10.1 API parsing behavior
- Frontend API client must parse response from raw text and then JSON decode.
- On decode failure, client error message must include endpoint + HTTP status + short body preview.

### 10.2 Route fallback behavior
- Server must return JSON 404 for unmatched `/api/*` routes.
- Non-API paths continue to use dashboard HTML fallback.

### 10.3 Save consistency behavior
- Push save flow is:
  1. POST config
  2. apply POST response in-memory
  3. immediately GET config for calibration
  4. re-render inputs and state text from latest GET payload

### 10.4 Scheduler calendar behavior
- `notification.scheduler.calendar_mode` is introduced.
- Supported values:
  - `daily`
  - `workdays`
  - `trading_days`
- This round default is `daily`.

## 11. Deploy Python Readiness Spec (2026-03-22)
- Deploy script must resolve an available Python executable with fallback candidates.
- Deploy script must install `requirements.txt` dependencies before service restart.
- Deploy script must verify import readiness for `akshare`, `pandas`, `requests`.
- Import verification failure is fatal and must terminate deploy with non-zero exit code.

## 12. Fresh Quote Revalidation Spec (2026-03-23)

### 12.1 Frontend request modes
- Dashboard API client must support two request modes for market datasets:
  - normal mode: existing endpoint path
  - force mode: same endpoint with `force=1`
- Manual `鍒锋柊` uses force mode for:
  - `/api/market/exchange-rate`
  - `/api/market/convertible-bond-arbitrage`
  - `/api/market/ah`
  - `/api/market/ab`
  - `/api/market/ipo`
  - `/api/market/convertible-bonds`
  - `/api/market/merger`

### 12.2 First-load cache revalidation
- If the initial dashboard response for `exchangeRate / cbArb / ah / ab` carries `servedFromCache = true`, frontend must trigger one background force revalidation for that dataset in the same session.
- Background revalidation must:
  - keep the current cached value visible until the fresh payload returns
  - replace the module state with the fresh payload after success
  - surface concise status text while revalidation is in progress

### 12.3 User-visible freshness text
- Push strip status is unrelated to market freshness.
- Market freshness copy must come from dataset response metadata:
  - `servedFromCache = true` => show cached/revalidating wording
  - no cache marker after force success => show real-time wording

## 13. Dense Core Table Rendering Spec (2026-03-23)

### 13.1 Convertible bond main table
- `杞€哄鍒ー must render without a visible `璇︽儏` header column.
- Default-row columns are fixed to:
  - `搴忓彿`
  - `杞€篳
  - `姝ｈ偂`
  - `杞€虹幇浠?/ 杞€烘定璺屽箙`
  - `姝ｈ偂鐜颁环 / 姝ｈ偂娑ㄨ穼骞卄
  - `杞偂浠?/ 杞偂浠峰€糮
  - `杞偂婧环鐜嘸
  - `鍙屼綆`
  - `60鏃ユ尝鍔ㄧ巼`
  - `绾€轰环鍊?/ 鐞嗚浠锋牸`
  - `鐞嗚婧环鐜嘸
  - `鍒版湡绋庡墠鏀剁泭鐜嘸
- Composite cells may use two-line rendering inside one column, but the values above must be visible without row expansion.
- Optional remaining low-priority fields may stay in inline detail rows only if they are no longer needed for the primary reading path.

### 13.2 AH / AB main tables
- `AH` and `AB` must share one rendering skeleton and differ only by field mapping.
- Default-row columns are fixed to:
  - `搴忓彿`
  - `A鑲
  - `H鑲?/ B鑲
  - `A鑲′环`
  - `瀵规墜甯傚満浠穈
  - `瀵规墜浜烘皯甯佷环`
  - `浠峰樊`
  - `婧环鐜嘸
  - `杩戜笁骞村垎浣峘
  - `鏍锋湰淇℃伅`
- `鏍锋湰淇℃伅` uses a compact two-line cell:
  - line 1: `鏍锋湰鏁癭
  - line 2: compressed range `YYMMDD-YYMMDD`
- `AH / AB` default rendering must not require the old detail-label column.

### 13.3 Table renderer behavior
- Shared table renderer must support hiding the explicit detail header/button column when the module contract does not need it.
- If a module still uses inline details, the header cell for that control must be blank rather than showing `璇︽儏`.

## 14. Push Delivery Truthfulness Spec (2026-03-23)

### 14.1 Runtime state fields
- Push runtime state must separately retain:
  - `lastMainPushAttemptAt`
  - `lastMainPushSuccessAt`
  - `lastMainPushError`
  - `lastMergerPushAttemptAt`
  - `lastMergerPushSuccessAt`
  - `lastMergerPushError`

### 14.2 Scheduler success semantics
- Main push scheduler flow:
  1. record attempt time
  2. try downstream send
  3. on success:
     - clear latest error
     - set success time
     - record the schedule slot as sent
  4. on failure:
     - update latest error
     - do not record the slot as sent
- Merger report scheduler follows the same rule set.

### 14.3 Push config API payload
- `GET /api/push/config` response must include delivery-health metadata in addition to editable schedule fields:
  - `webhookConfigured`
  - `schedulerEnabled`
  - `calendarMode`
  - `selectedModules`
  - `lastMainPushAttemptAt`
  - `lastMainPushSuccessAt`
  - `lastMainPushError`
  - `lastMergerPushAttemptAt`
  - `lastMergerPushSuccessAt`
  - `lastMergerPushError`

### 14.4 Push strip rendering
- Dashboard push strip must render a concise status summary derived from the API payload.
- If `webhookConfigured = false`, UI must explicitly warn that push cannot be delivered.
- If latest runtime error exists, UI must surface the short reason instead of only showing historical dates.

## 15. Premium History Incremental Sync Tolerance Spec (2026-03-23)

### 15.1 Scope
- This rule applies only to `tools/rebuild_premium_db.py --mode update`.
- It does not relax failure behavior for `--mode rebuild`.

### 15.2 Update-mode tolerance
- During update mode, the script may downgrade a per-symbol upstream historical-price fetch failure from `failed` to `warning` when all of the following hold:
  - the failure is limited to a single symbol
  - the error originates from the upstream provider fetch step
  - the script can continue processing the rest of the batch
- Warning entries must still include:
  - `type`
  - `code`
  - `error`

### 15.3 Success semantics
- Update mode final payload may still return `success = true` when warning-only entries exist.
- Final payload must distinguish:
  - `failedCount`
  - `warningCount`
  - `failed`
  - `warnings`
- `failedCount > 0` remains fatal.
- `warningCount > 0` is informational and must not by itself fail the batch.

### 15.4 Non-tolerated failures
- The following remain fatal even in update mode:
  - config / import / environment failures
  - SQLite write failures
  - FX history failures
  - batch-wide provider failures that prevent useful progress
  - any failure path outside the per-symbol upstream price-fetch anomaly classification
## 16. Cloud Runtime Preservation And Proxy Install Spec (2026-03-23)

### 16.1 Runtime-state boundary
- `runtime_data/shared/*.json` is runtime state, not release-source truth.
- Repository sync may update code and static assets, but must not replace the server's current runtime JSON content with repository copies.

### 16.2 Deploy-script preservation behavior
- `tools/deploy/update_from_github.sh` must preserve tracked runtime JSON files before `git reset --hard` and restore them immediately after code sync completes.
- Preservation scope must cover at least:
  - monitor list
  - dividend portfolio
  - push config
  - push runtime state
  - merger company reports
  - market cache snapshots
  - market refresh state

### 16.3 Managed service template
- `tools/deploy/alpha-monitor.service` must declare:
  - project-root working directory
  - optional `.env` loading through `EnvironmentFile`
  - pre-start runtime directory creation
  - automatic restart on failure

### 16.4 Reverse-proxy install scripts
- Repo must provide one-command installer scripts for both bundled proxy options:
  - `tools/deploy/install_nginx_site.sh`
  - `tools/deploy/install_caddy_site.sh`
- Both scripts must template the public host and upstream app port, validate config, and reload the managed proxy service.

## 17. Convertible Bond Daily Delist Filter Spec (2026-03-23)

### 17.1 Scope
- This rule applies to the outward-facing row list used by:
  - `/api/market/convertible-bond-arbitrage`
  - dashboard `杞€哄鍒ー panel
- The existing Python fetch layer may continue computing `isDelistedOrExpired`, but the final visible list must be re-checked again in Node strategy/service shaping.

### 17.2 Daily date source
- 鈥淭oday鈥?is fixed to the Shanghai calendar date.
- Node-side date comparison must use `shared/time/shanghai_time.js` so cloud/runtime timezone drift does not change the business result.

### 17.3 Exclusion decision
- Each row must be excluded from the final list when any of the following hold after date normalization:
  - `delistDate <= today`
  - `ceaseDate <= today`
  - `maturityDate < today`
- `delistDate` / `ceaseDate` are inclusive same-day cutoffs.
- `maturityDate` remains exclusive for same-day removal, matching the existing fetch-layer rule.

### 17.4 Cache tolerance behavior
- The Node-side sanitizer must recompute the rule on every response instead of trusting a stale cached `isDelistedOrExpired = false`.
- If a row already carries `isDelistedOrExpired = true`, it may be excluded immediately without further contradiction handling.

### 17.5 Output behavior
- Excluded rows must be removed before duplicate-row resolution and before any opportunity-set summary calculation.
- No new API field or route is required for this round; the correction is purely on visible row inclusion.
## 18. Event Arbitrage Unified Spec (2026-03-23)

### 18.1 Top-level dashboard contract
- The old dashboard tab label `閺€鎯板枠缁変焦婀乣 is replaced by `娴滃娆㈡總妤€鍩刞.
- The root dashboard tab key count remains 6.
- The existing merger-related backend routes remain valid and unchanged for backward compatibility, but the main dashboard reading path switches to the new event-arbitrage aggregate payload.

### 18.2 Page structure
- `娴滃娆㈡總妤€鍩刞 page structure is fixed to:
  1. module title and update time
  2. internal sub-tab strip
  3. sub-view content area
- Internal sub-tabs are fixed to:
  - `閹槒顫峘
  - `濞擃垵鍋傜粔浣规箒閸?`
  - `娑擃厽顩ч懖锛勵潌閺堝瀵瞏
  - `A閼测€愁殰閸?`
  - `閸忣剙鎲″Ч?`
  - `濞擃垵鍋傛笟娑滃亗閺?瀵板懏甯撮崗?`
- Default internal sub-tab is `閹槒顫峘.

### 18.3 API contract
- New route: `GET /api/market/event-arbitrage`
- Response shape is fixed to:
  - `success`
  - `data.overview`
  - `data.categories`
  - `data.sourceStatus`
  - `error`
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`
- `data.categories` fixed keys:
  - `hk_private`
  - `cn_private`
  - `a_event`
  - `rights_issue`
  - `announcement_pool`
- `data.sourceStatus` fixed keys:
  - `hk_private`
  - `cn_private`
  - `a_event`
  - `rights_issue`
  - `announcement_pool`

### 18.4 Standardized row schema
- Every external event row must expose:
  - `id`
  - `source`
  - `category`
  - `market`
  - `symbol`
  - `name`
  - `currentPrice`
  - `changeRate`
  - `marketValue`
  - `offerPrice`
  - `spreadRate`
  - `eventType`
  - `eventStage`
  - `offeror`
  - `offerorHolding`
  - `registryPlace`
  - `dealMethod`
  - `canShort`
  - `canCounter`
  - `summary`
  - `detailUrl`
  - `officialMatch`
  - `raw`
- `officialMatch` is either `null` or:
  - `matched`
  - `announcementId`
  - `title`
  - `announcementDate`
  - `pdfUrl`
  - `reportAvailable`

### 18.5 Source and adapter rules
- Phase-1 primary source is direct public JSON fetching from Jisilu:
  - `/data/taoligu/hk_arbitrage_list/`
  - `/data/taoligu/cn_arbitrage_list/`
  - `/data/taoligu/astock_arbitrage_list/`
- `rights_issue` stays in the outward-facing model but is disabled in phase 1:
  - rows = `[]`
  - status = `disabled_no_public_source`
- Firecrawl is not part of the production hot path in this round.
- If one source fails, only that category status may degrade; the whole aggregate endpoint must still return the remaining healthy categories when possible.

### 18.6 Matching rules
- External rows may be enriched from the existing merger announcement pool.
- Phase-1 matching rule is fixed to exact code matching only:
  - Jisilu `symbol`
  - matches merger `secCode`
- No fuzzy company-name matching is allowed in this round.
- If multiple merger rows share the same code, the newest announcement row wins.

### 18.7 Sub-view rendering contract
- `閹槒顫峘 shows:
  - per-category row counts
  - positive-spread row counts
  - latest update time
  - matched announcement count
- `濞擃垵鍋傜粔浣规箒閸?` main table columns:
  - `娴狅絿鐖渀
  - `閸氬秶袨`
  - `閻滈鐜痐
  - `濞戙劏绌奸獮?`
  - `鐢倸鈧?`
  - `缁変焦婀侀崠鏍︾幆閺?`
  - `婵傛鍩勭粚娲？`
  - `缁変焦婀侀崠鏍箻缁?`
  - `鐟曚胶瀹抽弬?`
  - `鐟曚胶瀹抽弬瑙勫瘮閼?`
  - `閸忣剙寰冨▔銊ュ斀閸?`
  - `閺€鎯板枠閺傜懓绱
  - `閸欏秴顨渀
  - `閸欘垰宕犵粚?`
  - `婢跺洦鏁瀈
  - `鐠囷附鍎忛柧鐐复`
- `娑擃厽顩ч懖锛勵潌閺堝瀵瞏 main table columns:
  - `娴狅絿鐖渀
  - `閸氬秶袨`
  - `閻滈鐜痐
  - `濞戙劏绌奸獮?`
  - `鐢倸鈧?`
  - `缁変焦婀侀崠鏍︾幆閺?`
  - `婵傛鍩勭粚娲？`
  - `鏉╂稓鈻糮
  - `鐟曚胶瀹抽弬?`
  - `閺€鎯板枠閺傜懓绱
  - `鐠愬湱鏁ら幓鎰仛`
  - `鐠囷附鍎忛柧鐐复`
- `A閼测€愁殰閸?` main table columns:
  - `娴狅絿鐖渀
  - `閸氬秶袨`
  - `閻滈鐜痐
  - `濞戙劏绌奸獮?`
  - `鐎瑰鍙忔潏褰掓娴?`
  - `鐎瑰鍙忔潏褰掓閹舵ü鐜痐
  - `閻滀即鍣鹃柅澶嬪閺夊啩鐜弽?`
  - `閻滀即鍣鹃柅澶嬪閺夊啯濮屾禒?`
  - `鐢胶顫抈
  - `娴滃娆㈢猾璇茬€穈
  - `閹芥顩
  - `閸忣剙鎲￠柧鐐复`
  - `鐠佸搫娼ч柧鐐复`
- `閸忣剙鎲″Ч?` continues to show the existing merger-announcement table and AI-report affordances.
- `濞擃垵鍋傛笟娑滃亗閺?瀵板懏甯撮崗?` must render a real disabled-state panel with a reason message, not an empty fake table.

### 18.8 Runtime/cache rules
- New runtime cache file may be used for normalized aggregate payload:
  - `runtime_data/shared/event_arbitrage_cache.json`
- Cache payload must not replace the existing merger cache or merger APIs.
- Cached aggregate payload may be served for fast first paint, but source-level failure text must stay visible in `sourceStatus`.

## 19. Minimal Monitor Popup Editor Spec (2026-03-23)

### 19.1 Interaction mode
- `鐩戞帶濂楀埄` panel keeps the monitor list visible by default.
- The editor is closed by default and must open only when:
  - user clicks `鏂板鐩戞帶`
  - user clicks row-level `缂栬緫`
- Create and edit share one inline implementation rendered above the monitor list.

### 19.2 Visible form fields
- Visible fields are fixed to:
  - `鏀惰喘鏂筦
  - `鐩爣鏂筦
  - `鎹㈣偂姣斾緥`
  - `瀹夊叏绯绘暟`
  - `鐜伴噾瀵逛环`
  - `鐜伴噾瀵逛环甯佺`
  - `鐜伴噾閫夋嫨鏉僠
  - `鐜伴噾閫夋嫨鏉冨竵绉峘
- The old direct-input fields for code / market / share-currency / note / generated name must not render as normal visible inputs in this round.

### 19.3 Search confirmation behavior
- `鏀惰喘鏂筦 and `鐩爣鏂筦 inputs must support lightweight live lookup using the existing stock-search API.
- The editor must render a visible resolved-security hint when hidden metadata is already known, including at least:
  - resolved name
  - code
  - market type
  - currency
- When the search API returns multiple candidates, the editor may render a compact candidate list for explicit user confirmation.
- Selecting a candidate updates the hidden fields immediately.

### 19.4 Hidden-field preservation
- When editing an existing monitor row, hidden fields from stored runtime data must be carried forward unless the corresponding visible entity input changes.
- At minimum, preserved hidden fields include:
  - `id`
  - `name`
  - `acquirerCode`
  - `acquirerMarket`
  - `acquirerCurrency`
  - `targetCode`
  - `targetMarket`
  - `targetCurrency`
  - `note`
- `stockRatio` is no longer hidden in this round; it must follow the visible form value.
## 20. Startup Responsiveness And Premium History Recovery Spec (2026-03-23)

### 20.1 Dashboard latency model
- Cached dataset responses remain the default first-paint path.
- Force-refresh requests are still allowed to be slower than cached reads and must not redefine the normal latency baseline.
- Diagnosis for this round treats the following separately:
  - cached endpoint latency
  - force-refresh latency
  - broken-source fallback behavior

### 20.2 Degraded premium-summary detection
- A premium-history summary must be treated as degraded when any of the following hold:
  - `sampleCount <= 1`
  - `sampleCount3Y <= 1`
  - positive sample count exists but required date boundaries are missing
  - a very small 3Y sample count is paired with a same-day or near-same-day sample range, indicating the DB only kept a recent fragment
- Degraded summary means "not safe to skip sync", even if `endDate` already matches the latest market date.

### 20.3 Full-backfill escalation rule
- `tools/rebuild_premium_db.py --mode update` must escalate degraded symbols to a full backfill path instead of the normal short incremental fetch window.
- The same escalation rule must be available to the on-demand premium-history ensure path used by APIs/tools.
- Non-degraded symbols may continue using the existing incremental logic.

### 20.4 IPO empty-history fallback
- `data_fetch/subscription/ipo_source.py` must return a successful empty payload when:
  - latest upstream fetch failed or returned nothing
  - and SQLite currently has no stored IPO rows
- Required payload shape:
  - `success: true`
  - `data: []`
  - `upcoming: []`
  - `historyCount: 0`
  - `updateTime`
- Optional fields:
  - `source`
  - `warning`
- This fallback must not throw an API-level error or produce an HTTP 500 by itself.

### 20.5 Convertible-bond outward payload shaping
- `normalizeDatasetPayload('cbArb', ...)` may apply a final outward-facing field whitelist after row sanitization succeeds.
- The whitelist must preserve the fields used by the dashboard rendering path, including at least:
  - bond identity
  - stock identity
  - bond / stock current price and change
  - convert-price metrics
  - premium / double-low / volatility / theoretical-price / yield metrics
  - any remaining date fields still needed by sanitization before shaping
- Unused per-row internal fields may be removed from the HTTP payload even if they remain present in the raw Python result.
- This shaping step must not change:
  - row count
  - row order after sanitization
  - visible dashboard calculations
- Public output keeps `data` as the only row-array contract for this round.
- The same sanitized row collection must not be emitted again as top-level `list` or `rows` aliases.

## 21. Event Arbitrage UI Simplification Spec (2026-03-23)

### 21.1 Visible navigation
- The frontend event-arbitrage sub-tab sequence is fixed to:
  - `a_event`
  - `hk_private`
  - `cn_private`
  - `rights_issue`
  - `announcement_pool`
- `overview` remains an API field only; it is not part of the visible sub-tab sequence.
- Frontend default event-arbitrage sub-tab becomes `a_event`.

### 21.2 A-share rendering rule
- `A鑲″鍒ー uses the standardized `a_event` rows directly.
- Table-visible A-share fields remain limited to the scraped core fields, including:
  - code
  - name
  - current price
  - change rate
  - safety price
  - safety discount
  - choose price
  - choose discount
  - currency
  - event type
  - official announcement link
- `forumUrl` may stay in raw payload storage, but frontend must not render it in this round.

### 21.3 HK/CN rendering rule
- `娓偂濂楀埄` main table displays only fetched core fields and a direct raw-announcement link from the scraped source row.
- That announcement link must point to the source-side original/core announcement URL carried by the normalized row.
- `涓绉佹湁` keeps the same non-expand secondary-row presentation pattern for textual notes.

### 21.4 Summary placement
- A-share `summary` is removed from the main table columns.
- Instead, each A-share row renders a second always-visible detail row directly below the main row.
- That detail row must not depend on expand/collapse interaction.
- The rendered label is fixed to `鎽樿`.
- HK/CN text notes follow the same always-visible detail-row pattern, but the rendered label is fixed to `澶囨敞`.

### 21.5 Event-arbitrage detail interaction
- `浜嬩欢濂楀埄` tables no longer use row-level expand buttons in this round.
- `announcement_pool` renders without detail toggles.
- `hk_private`, `cn_private`, and `a_event` keep the secondary detail-row visual style, but it is always visible and not interactive.

## 22. Same-day Subscription Truthfulness And Dense CB Core Fields Spec (2026-03-23)

### 22.1 IPO same-day retry rule
- `ipo` dataset cache may not be treated as healthy-first-choice when all of the following hold:
  - `historyCount <= 0`
  - `data = []`
  - `upcoming = []`
- In that state, later normal requests must retry the live fetch path instead of serving the cached empty payload forever.
- This rule is limited to the subscription datasets whose current-user contract is same-day event visibility.

### 22.2 Beijing IPO market recognition
- Subscription source market inference must recognize Beijing exchange IPO code prefixes:
  - `4*`
  - `8*`
  - `9*`
- This rule only fixes market classification; it must not change row identity, subscribe dates, or dedup keys.

### 22.3 Invalid convertible-bond visible-row rule
- Node-side `sanitizeCbArbRows()` must exclude a row before outward rendering when either of the following holds:
  - `price <= 0`
  - `turnoverAmountYi <= 0` and the row already has terminal delist-chain evidence such as `ceaseDate` / `delistDate` / `maturityDate` crossing an imminent end-state cutoff
- Existing `delistDate <= today`, `ceaseDate <= today`, and `maturityDate < today` rules remain in force.
- This rule is meant to remove obviously dead rows from the visible list; it is not a new opportunity-ranking formula.

### 22.4 CB outward payload whitelist expansion
- Public `cbArb` rows must preserve at least the following fields for the dense table:
  - `code`
  - `bondName`
  - `price`
  - `changePercent`
  - `stockCode`
  - `stockName`
  - `stockPrice`
  - `stockChangePercent`
  - `stockAvgRoe3Y`
  - `stockDebtRatio`
  - `convertPrice`
  - `convertValue`
  - `premiumRate`
  - `pureBondValue`
  - `bondValue`
  - `doubleLow`
  - `redeemTriggerPrice`
  - `putbackPrice`
  - `volatility60`
  - `callOptionValue`
  - `putOptionValue`
  - `theoreticalPrice`
  - `theoreticalPremiumRate`
  - `listingDate`
  - `convertStartDate`
  - `maturityDate`
  - `rating`
  - `yieldToMaturityPretax`

### 22.5 Dense CB table rendering contract
- `杞€哄鍒ー default-row columns are fixed to:
  - `搴忓彿`
  - `杞€篳
  - `杞€虹幇浠?/ 娑ㄨ穼`
  - `姝ｈ偂`
  - `姝ｈ偂鐜颁环 / 娑ㄨ穼`
  - `3Y骞冲潎ROE`
  - `璧勪骇璐熷€虹巼`
  - `杞偂浠?/ 杞偂浠峰€糮
  - `杞偂婧环鐜嘸
  - `绾€轰环鍊糮
  - `绾€烘孩浠风巼`
  - `鍙屼綆`
  - `寮鸿祹浠穈
  - `鍥炲敭浠穈
  - `60鏃ユ尝鍔ㄧ巼`
  - `鏈熸潈鐞嗚浠峰€糮
  - `鐞嗚浠峰€糮
  - `鐞嗚婧环鐜嘸
  - `涓婂競鏃
  - `杞偂璧峰鏃
  - `鍒版湡鏃
  - `璇勭骇`
- `绾€轰环鍊糮 is rendered from:
  - prefer `pureBondValue`
  - fallback to `bondValue`
- `绾€烘孩浠风巼` is rendered as `(杞€虹幇浠?/ 绾€哄熀鍑?- 1) * 100`:
  - prefer `pureBondValue`
  - fallback to `bondValue`
- `60鏃ユ尝鍔ㄧ巼` is currently rendered from the annualized standard deviation of recent stock close-to-close log returns:
  - source close series = cached adjusted stock closes
  - current display semantics = historical estimate / reference
- `鏈熸潈鐞嗚浠峰€糮 is rendered as:
  - prefer `callOptionValue - putOptionValue`
  - fallback to `theoreticalPrice - 绾€哄熀鍑哷
- `鐞嗚浠峰€糮 is rendered from `theoreticalPrice`.
- `鐞嗚婧环鐜嘸 is rendered from `theoreticalPremiumRate`.
- The page must include a visible formula hint near the `杞€哄鍒ー main table, stating at least:
  - `鐞嗚浠峰€?= 绾€轰环鍊?+ 鏈熸潈鐞嗚浠峰€糮
  - `鏈熸潈鐞嗚浠峰€?= 鐪嬫定鏈熸潈浠峰€?- 鐪嬭穼鏈熸潈浠峰€糮
- The page must also visibly mark the following fields as reference-only in this round:
  - `60鏃ユ尝鍔ㄧ巼`
  - `鏈熸潈鐞嗚浠峰€糮
  - `鐞嗚浠峰€糮
  - `鐞嗚婧环鐜嘸
- `yieldToMaturityPretax` outward value must come from a real upstream field:
  - prefer Jisilu `bond_cb_jsl()` `鍒版湡绋庡墠鏀剁泭`
  - if the source row has no real value, keep `yieldToMaturityPretax = null`
  - do not populate this field from a local approximation formula in this round
- `stockAvgRoe3Y` and `stockDebtRatio` remain real-source financial metrics:
  - the stable bulk path may use Eastmoney report-summary tables:
    - `stock_yjbb_em(date=YYYY1231)` for annual `鍑€璧勪骇鏀剁泭鐜嘸
    - `stock_zcfz_em(date=YYYYMMDD)` for latest available `璧勪骇璐熷€虹巼`
  - if the bulk path still misses a code, fallback fetchers may still try:
    - `ak.stock_financial_abstract_ths(symbol=code, indicator="鎸夋姤鍛婃湡")`
    - `ak.stock_financial_abstract(symbol=code)`

## 22A. Constitution Sync Guardrail Spec (2026-03-23)

### 22.1 Scope
- This round adds only a governance guardrail and does not change business API behavior.
- Fixed files:
  - source: `CONSTITUTION.md`
  - mirror: `.specify/memory/constitution.md`
  - checker: `tools/check_constitution_sync.py`
  - command entry: `npm run check:constitution`

### 22.2 Comparison rule
- The checker reads both constitution files as UTF-8 text.
- To avoid false positives caused only by Windows/Linux line-ending differences, comparison normalizes:
  - `\r\n` -> `\n`
  - trailing final newline presence
- Other content differences are treated as real drift and must fail the check.

### 22.3 Failure behavior
- The checker exits non-zero when:
  - either constitution file is missing
  - normalized text differs
- On failure, output must clearly identify:
  - which file is missing, or
  - a short unified diff preview for the first mismatching section

### 22.4 Success behavior
- On success, the checker prints a concise confirmation that the two constitution files are synchronized.
- The checker performs no file mutation, network access, or side effects beyond stdout/stderr output and exit code.

### 22.5 Governance rollback note (2026-03-24)
- This guardrail continues to protect only:
  - `CONSTITUTION.md`
  - `.specify/memory/constitution.md`
- The previously added root-level `PROJECT_PLAN.md / PROJECT_REQUIREMENTS.md / PROJECT_TECH_STACK.md` requirement is cancelled in this round.
- No checker logic should be expanded to require those files.

## 22B. Access Entry Runtime Spec (2026-03-24)

### 23.1 Scope
- This round repairs only the root access-entry truthfulness problem.
- No dashboard business dataset, scheduler logic, or market calculation changes are included.

### 23.2 Runtime access-info API
- Node service must expose a lightweight read-only access-info endpoint.
- Response payload must include at least:
  - `serverBaseUrl`
  - `publicBaseUrl`
  - `publicHealthUrl`
  - `environment`
- Values come from the same runtime config already resolved by the server:
  - `config.yaml > app.server_base_url`
  - `config.yaml > deployment.public_base_url`
  - derived health URL

### 23.3 Root entry page behavior
- `index.html` must not hardcode `http://127.0.0.1:5000` in visible text, primary action links, or health probes.
- When the page is served by the running app:
  - it fetches the access-info endpoint from the same origin
  - it renders the returned URLs into the page
  - it uses the returned service URL for the primary open-service action
- When the page is opened as a local file:
  - it does not provide local template preview
  - it does not claim a fixed service URL
  - it clearly guides the user to the configured cloud public URL

### 23.4 Safety boundary
- This round must not change:
  - `presentation/templates/dashboard_template.html`
  - dashboard data-fetch behavior
  - scheduler config or push behavior
  - market API payload semantics

## 23. LOF Arbitrage Zero-login Spec (2026-03-23)

### 23.1 Scope
- This round adds a new top-level dashboard module `LOF濂楀埄`.
- Phase-1 source scope is fixed to direct public JSON requests against Jisilu QDII endpoints:
  - `/data/qdii/qdii_list/E`
  - `/data/qdii/qdii_list/A`
  - `/data/qdii/qdii_list/C`
- Firecrawl is not in the hot path for this round.

### 23.2 Layering
- `data_fetch/lof_arbitrage/fetcher.py` only handles:
  - source request
  - retry / timeout
  - per-category cache fallback
  - outward raw-category snapshot
- `data_fetch/lof_arbitrage/normalizer.py` only maps source fields into bus rows.
- `strategy/lof_arbitrage/service.py` only handles:
  - premium-basis selection
  - fee adjustment
  - action-status classification
  - overview aggregation
- `presentation` only handles:
  - route registration
  - dataset refresh
  - dashboard rendering

### 23.3 API contract
- New route: `GET /api/market/lof-arbitrage`
- Response shape is fixed to:
  - `success`
  - `data.overview`
  - `data.rows`
  - `data.groups`
  - `data.sourceStatus`
  - `data.iopvSearch`
  - `error`
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`

### 23.4 Source groups
- `data.groups` fixed keys:
  - `europe_us`
  - `asia`
  - `commodity`
- `data.sourceStatus` fixed keys mirror the same 3 groups.
- Any single-group source failure must only degrade that group and may not blank the whole LOF page or homepage.

### 23.5 Standardized row schema
- Each outward LOF row must expose at least:
  - `id`
  - `source`
  - `category`
  - `market`
  - `symbol`
  - `name`
  - `issuer`
  - `currentPrice`
  - `changeRate`
  - `volumeWan`
  - `navValue`
  - `navDate`
  - `navPremiumRate`
  - `iopv`
  - `iopvTime`
  - `iopvPremiumRate`
  - `estimatedValue`
  - `estimatedTime`
  - `estimatedPremiumRate`
  - `premiumBasis`
  - `premiumRate`
  - `confidence`
  - `estimatedCostRate`
  - `netPremiumRate`
  - `applyStatus`
  - `applyOpen`
  - `applyFeeRate`
  - `redeemStatus`
  - `redeemFeeRate`
  - `managementFeeRate`
  - `currency`
  - `t0`
  - `actionStatus`
  - `actionRank`
  - `riskFlags`
  - `detailUrl`
  - `raw`

### 23.6 Premium-basis rule
- Phase-1 signal basis priority is fixed to:
  1. `iopvPremiumRate`
  2. `estimatedPremiumRate`
  3. `navPremiumRate`
- The outward row field `premiumBasis` must be one of:
  - `iopv`
  - `estimate`
  - `nav`
- The outward row field `confidence` must be one of:
  - `high`
  - `medium`
  - `low`

### 23.7 Action-status rule
- `actionStatus = 涓嶅彲鍙備笌` when current apply status is paused/closed.
- `actionStatus = 鏃犳槑鏄炬孩浠穈 when outward signal premium is missing or non-positive.
- `actionStatus = 浠呰瀵焋 when:
  - only NAV premium is available and phase-1 rule forbids treating NAV-only rows as execution-grade
  - or apply is limited and the current strategy config keeps limited-apply rows as watch-only
- `actionStatus = 濂楀埄鍊欓€塦 only when all of the following hold:
  - signal premium exists
  - signal premium >= `strategy.lof_arbitrage.premium_threshold_pct`
  - net premium >= `strategy.lof_arbitrage.min_net_premium_pct`
  - apply is open
  - row is not downgraded by the phase-1 NAV-only rule

### 23.8 Fee and risk rules
- `estimatedCostRate` in phase 1 is the conservative visible fee sum of:
  - `applyFeeRate`
  - `managementFeeRate`
- `netPremiumRate = premiumRate - estimatedCostRate` when both are available.
- `riskFlags` must append warnings for at least:
  - NAV-only signal
  - limited apply
  - paused apply
  - low liquidity under `strategy.lof_arbitrage.low_liquidity_volume_wan`

### 23.9 Dashboard rendering
- The dashboard adds a new root tab key `lof-arb`.
- The LOF page structure is fixed to:
  1. module title and status text
  2. market subtab strip
  3. one paginated main table
- Visible top summary cards are removed from the LOF page in this round:
  - `濂楀埄鍊欓€塦
  - `浠呰瀵焋
  - `鏁版嵁閾捐矾`
- Main table columns are fixed to:
  - `搴忓彿`
  - `浠ｇ爜`
  - `鍩洪噾 / 鍒嗗尯`
  - `鐜颁环 / 娑ㄥ箙`
  - `鍑€鍊?/ 婧环`
  - `IOPV / 婧环`
  - `浼板€?/ 婧环`
  - `淇″彿婧环`
  - `鎵ｈ垂鍚庢孩浠穈
  - `鐢宠喘鐘舵€乣
  - `鎴愪氦棰?涓?`
  - `缁撹`
  - `璇︽儏`
- Each row must render an always-visible secondary detail block for:
  - dates
  - fees
  - currency / T+0
  - reference index
  - risk flags

### 23.10 Search-status exposure
- `data.iopvSearch` is phase-1 operational metadata for the continuing zero-login IOPV search.
- It must expose at least:
  - `publicSourceStatus`
  - `currentZeroLoginAvailability`
- This metadata is informational only and must not block the page render.

## 24. LOF Authenticated Enrichment Spec (2026-03-23)

### 24.1 Fetch-mode rule
- `data_fetch/lof_arbitrage/fetcher.py` keeps using:
  - `/data/qdii/qdii_list/E`
  - `/data/qdii/qdii_list/A`
  - `/data/qdii/qdii_list/C`
- New optional config:
  - `data_fetch.plugins.lof_arbitrage.jisilu_cookie`
- When this cookie is present, the fetch session must send it as a request header and mark the source status as authenticated-enhanced.
- When the authenticated request fails or yields no usable response, the fetch layer must retry or fall back to the public path without taking down the module.

### 24.2 Source-status additions
- `data.sourceStatus.{group}` must additionally allow:
  - `cookieConfigured`
  - `authMode`
  - `usedLoginEnhancedRows`
- `authMode` is fixed to one of:
  - `public`
  - `authenticated`
  - `authenticated_fallback_public`
- `usedLoginEnhancedRows = true` only when the returned row set came from the authenticated request path.

### 24.3 Standardized LOF row additions
- Each outward LOF row keeps the phase-1 schema and additionally exposes:
  - `amountWanShares`
  - `amountIncreaseWanShares`
  - `amountIncreaseRate`
  - `navValueText`
  - `navPremiumRateText`
  - `iopvText`
  - `iopvPremiumRateText`
  - `estimatedValueText`
  - `estimatedPremiumRateText`
  - `referenceIndex`
  - `referenceIndexChangeRate`
  - `applyFeeText`
  - `redeemFeeText`
  - `managementFeeText`
  - `officialUrl`
  - `sourceDetailUrl`
- `officialUrl` comes from the source row `urls` field when available.
- `sourceDetailUrl` is the Jisilu detail page for the row symbol.

### 24.4 LOF page navigation
- The LOF page adds visible internal subtabs:
  - `europe_us`
  - `asia`
  - `commodity`
- Visible labels are fixed to:
  - `娆х編甯傚満`
  - `浜氭床甯傚満`
  - `鍟嗗搧`
- Frontend default LOF subtab becomes `europe_us`.

### 24.5 LOF long-table rendering
- The LOF main view renders one long table for the active market subtab.
- Main table columns are fixed to:
  - `搴忓彿`
  - `浠ｇ爜`
  - `鍚嶇О`
  - `鐜颁环`
  - `娑ㄨ穼骞卄
  - `鎴愪氦棰?涓囧厓)`
  - `鍦哄唴浠介(涓囦唤)`
  - `鍦哄唴鏂板(涓囦唤)`
  - `IOPV`
  - `IOPV婧环鐜嘸
  - `T-2鍑€鍊糮
  - `鍑€鍊兼棩鏈焋
  - `T-2鍑€鍊兼孩浠穈
  - `T-1鎸囨暟娑ㄥ箙`
  - `鐩稿叧鎸囨暟`
  - `鐢宠喘璐筦
  - `鐢宠喘鐘舵€乣
  - `璧庡洖璐筦
  - `璧庡洖鐘舵€乣
  - `绠℃墭璐筦
  - `鍩洪噾鍏徃`
  - `瀹樻柟閾炬帴`
  - `闆嗘€濆綍璇︽儏`
- The long table becomes the immediate primary reading path, without a visible summary-card band above it.

### 24.6 Missing-value truthfulness
- `IOPV`-related fields must remain empty when the current source chain does not return them.
- Frontend display text for truly missing `IOPV` / estimate values must use an explicit unavailability label rather than a fabricated number.
- The page should continue exposing the operational search state for better `IOPV` coverage, but this status is informational only.

### 24.7 LOF derived-estimate completion
- `data_fetch/lof_arbitrage/normalizer.py` may derive estimate fields only from source-provided raw fields.
- Phase-1 allowed estimate derivation:
  - `estimatedValue = navValue * (1 + est_val_increase_rt / 100)`
  - only when direct `estimate_value` is empty
- Phase-1 allowed estimate-premium derivation:
  - `estimatedPremiumRate = ((currentPrice / estimatedValue) - 1) * 100`
  - only when direct `discount_rt` is empty and `estimatedValue` exists
- `estimatedSource` fixed values:
  - `direct_source`
  - `derived_from_est_val_increase_rt`
- `estimatedSourceLabel` fixed outward semantics:
  - `婧愮洿鎺ヨ繑鍥瀈
  - `Jisilu浼板€兼定骞呮帹瀵糮
- LOF outward row additions for this round include:
  - `estimatedSource`
  - `estimatedSourceLabel`
  - `estimatedIncreaseRate`
  - `estimatedIncreaseRateText`
  - `turnoverRate`
  - `priceDate`
  - `amountDate`
  - `calculationTips`
  - `fundType`
- `estimatedTime` fallback order is fixed to:
  1. `last_est_datetime`
  2. `last_est_dt + last_est_time`
  3. `est_val_dt`
  4. `last_time`
- The LOF main table additionally renders:
  - `缁撹`
  - `淇″彿婧环`
- `淇″彿婧环` sorts by `premiumRate` descending by default inside each LOF market subtab.
- LOF detail rows additionally render:
  - `浼板€兼潵婧恅
  - `浼板€兼定骞卄
  - `鍙傝€冧环`
  - `浼板€艰鏄巂
  - `鎶ヤ环鏃堕棿`
- LOF secondary detail rows remain always visible beneath each row and serve as the default supplementary reading path.
- `IOPV` remains independent from the derived estimate path:
  - derived estimate logic must not populate `IOPV`
  - derived estimate logic must not populate `IOPV婧环鐜嘸

## 25. Event-arbitrage Detail Text Responsive Spec (2026-03-24)

### 25.1 Scope
- This round changes only the event-arbitrage detail-text presentation.
- No event-arbitrage API field names or payload semantics change.

### 25.2 Rendering rule
- `A鑲″鍒ー detail `鎽樿` uses a dedicated single-column detail-grid variant.
- `娓偂濂楀埄` and `涓绉佹湁` detail `澶囨敞` use the same dedicated single-column variant.
- The single-column variant must span the available detail-row width on desktop instead of inheriting the default 4-column detail-grid compression.
- On narrow screens the same block continues wrapping naturally without horizontal overflow.
## 25. LOF Homepage Cancellation Spec (2026-03-24)

### 25.1 Scope rule
- `LOF濂楀埄` is removed from the public homepage module set in this round.
- This round is a homepage/runtime disconnect, not a full backend deletion.

### 25.2 Homepage navigation rule
- Visible homepage root tabs are fixed to:
  - `cb-arb`
  - `ah`
  - `ab`
  - `monitor`
  - `dividend`
  - `merger`
- The homepage template must not render:
  - `data-tab="lof-arb"`
  - `panel-lof-arb`

### 25.3 Dashboard bootstrap rule
- Frontend bootstrap must not request the LOF dataset.
- Frontend force-refresh key list must not include `lofArb`.
- The active-panel router must not route homepage tabs to `renderLofArbitragePanel()`.

### 25.4 Runtime preload rule
- Server preload dataset keys must not include `lofArb`.
- Existing backend route `GET /api/market/lof-arbitrage` may remain implemented, but it is outside the active homepage contract.

## 26. Shared Dashboard Table Readability Spec (2026-03-24)

### 26.1 Config contract
- `config.yaml` adds `presentation.dashboard_table_ui`.
- Required config fields:
  - `desktop_font_px`
  - `desktop_header_font_px`
  - `desktop_line_height`
  - `desktop_cell_padding_y`
  - `desktop_cell_padding_x`
  - `tablet_font_px`
  - `min_width_by_kind`
- `min_width_by_kind` must expose at least:
  - `subscription`
  - `convertible`
  - `premium`
  - `monitor`
  - `dividend`
  - `merger`
  - `lof`

### 26.2 UI-config API contract
- New route: `GET /api/dashboard/ui-config`
- Response shape:
  - `success`
  - `data.tableUi.desktopFontPx`
  - `data.tableUi.desktopHeaderFontPx`
  - `data.tableUi.desktopLineHeight`
  - `data.tableUi.desktopCellPaddingY`
  - `data.tableUi.desktopCellPaddingX`
  - `data.tableUi.tabletFontPx`
  - `data.tableUi.minWidthByKind`
- The route is read-only and reflects active presentation config only.

### 26.3 Shared rendering rule
- `renderPaginatedTable()` and `renderSimpleTable()` remain the only shared table rendering entry points in this round.
- Table readability upgrades must be implemented through shared CSS variables and shared renderer output, not module-specific table rewrites.
- Shared output structure must keep:
  - sticky headers
  - sort buttons
  - existing pagination bar
  - existing detail-row rendering behavior

### 26.4 Table density and width rule
- Desktop table body font target is larger than the previous `12px` contract.
- Desktop header font target is not smaller than body font.
- Shared table cells use relaxed line-height and larger padding than the old dense baseline.
- Tables may continue using horizontal wrappers, but width control shifts to per-kind `min-width` rules instead of relying only on a fully compressed fixed layout.
- `table[data-table-kind="subscription" | "convertible" | "premium" | "monitor" | "dividend" | "merger"]` must each consume the corresponding min-width config.
- If LOF table rendering is active later, `table[data-table-kind="lof"]` follows the same contract.

### 26.5 Typography and scanability rule
- Table cells use tabular-number rendering to stabilize:
  - price fields
  - percentage fields
  - code-like fields
  - pagination counters
- Shared table rows add clearer visual separation through:
  - a slightly stronger divider
  - or a weak zebra pattern
- Existing semantic row highlighting must remain visually dominant for:
  - today-highlight rows
  - subscription stage rows
  - error / status colors

### 26.6 Breakpoint rule
- `>= 1380px`: full desktop readability settings apply.
- `861px - 1379px`: use intermediate density with reduced font size relative to large desktop.
- `<= 860px`: keep the current compact/mobile-safe reading path:
  - limited font growth only
  - existing horizontal scroll containers remain valid
  - no separate mobile-only table rendering mode

## 26. LOF Complete Removal Spec (2026-03-24)

### 26.1 Scope rule
- `LOF濂楀埄` is fully removed from the active repository/runtime surface in this round.
- This round supersedes the earlier LOF homepage-cancellation-only approach.

### 26.2 Required removals
- Remove the LOF public route registration:
  - `GET /api/market/lof-arbitrage`
- Remove the LOF data-core action exposure:
  - `lof-arbitrage` in `data_dispatch.py`
- Remove active LOF dataset registration from server runtime.
- Remove active LOF bootstrap/render logic from the dashboard bundle.
- Remove active LOF config sections from `config.yaml`, including:
  - runtime file key
  - data-fetch plugin registration
  - strategy registration
  - LOF plugin tuning section
  - LOF strategy section
  - LOF presentation section
- Remove retired implementation directories:
  - `data_fetch/lof_arbitrage`
  - `strategy/lof_arbitrage`

### 26.3 Post-removal contract
- Homepage visible root tabs remain:
  - `cb-arb`
  - `ah`
  - `ab`
  - `monitor`
  - `dividend`
  - `merger`
- Unknown former LOF route access must fall back to the project's normal API 404 behavior.
- No active code path may still request, preload, or dispatch LOF data.

## 27. Repository-local mini-SWE-agent Integration Spec (2026-03-24)

### 27.1 Scope
- This round adds only a local development helper for `mini-SWE-agent`.
- No dashboard route, runtime preload, scheduler path, deployment path, or market-data contract changes in this round.

### 27.2 Local command contract
- `package.json` must expose a stable local command entry:
  - `npm run agent:mini:task`
- The command must execute a repository-owned script under `tools/`.
- The command is a text-generation helper only:
  - it may print a ready-to-use task prompt
  - it may optionally write that prompt to a local file
  - it must not directly launch `mini-SWE-agent`

### 27.3 Prompt-generation contract
- The helper output must always include:
  - read `CONSTITUTION.md` first
  - stop and update `plan.md` / `REQUIREMENTS.md` / `SPEC.md` before coding if behavior, config, API, deployment, or contract meaning changes
  - respect `data_fetch / strategy / presentation / notification / shared` boundaries
  - avoid fake data
  - prefer minimal changes
- The helper output must include a `Task:` section populated from caller input.
- The helper output must include a `Validation:` section.
- Default validation commands must include:
  - `npm run check`
  - `npm run check:boundaries`
- The helper may allow additional validation commands to be appended from CLI arguments.

### 27.4 Scope-hint contract
- The helper must support a caller-provided scope hint.
- Supported scope hints in this round must include at least:
  - `presentation`
  - `data_fetch`
  - `strategy`
  - `notification`
  - `shared`
  - `docs`
  - `full_repo`
- When a narrow scope is chosen, the generated prompt must explicitly say which directories should not be modified unless the agent first stops for approval/doc updates.

### 27.5 Documentation contract
- The repository must include a local usage guide for `mini-SWE-agent`.
- The guide must cover at least:
  - installation steps
  - how to generate a task prompt with `npm run agent:mini:task -- ...`
  - recommended `confirm` mode
  - example task-generation commands for common repository scopes
  - a recommended collaboration split where Codex handles planning/contracts/review and `mini-SWE-agent` handles narrow implementation tasks

### 27.6 Safety boundary
- The helper script must not read or mutate runtime data as part of prompt generation.
- The helper script must not require network access.
- The helper script must not auto-discover server secrets or deployment credentials.
- The helper script must stay deterministic for the same CLI inputs.

## 28. Push Summary + Event-alert Refactor Spec (2026-03-24)

### 28.1 Scope
- This round changes active push behavior, push settings UI, and push runtime state.
- This round does not remove the event-arbitrage page itself.
- This round removes merger-report push scheduling from the active push surface only.

### 28.2 Push settings contract
- Dashboard push settings keep only:
  - `push-time-1`
  - `push-time-2`
  - `push-alert-cooldown`
- The old third merger-report input is removed.
- Save payload contract:
  - `times`: exactly two normalized `HH:MM` values
  - `eventAlert.cooldownMinutes`: positive integer
- Response payload contract:
  - `times`
  - `eventAlert.enabled`
  - `eventAlert.cooldownMinutes`
  - `eventAlert.convertibleBond.convertPremiumLt`
  - `deliveryStatus.lastMainPushAttemptAt`
  - `deliveryStatus.lastMainPushSuccessAt`
  - `deliveryStatus.lastMainPushError`
  - `deliveryStatus.lastEventAlertAttemptAt`
  - `deliveryStatus.lastEventAlertSuccessAt`
  - `deliveryStatus.lastEventAlertError`
  - `deliveryStatus.pushHtmlUrlConfigured`
- The active response contract must not include merger-report schedule or merger-report delivery fields.

### 28.3 Summary push content rule
- Summary push remains Markdown for enterprise-wecom.
- The summary template and event-alert template must be separated.
- Summary modules for this round:
  - `AH / AB`
  - `鍙浆鍊篳
  - `鎵撴柊`
  - `鍒嗙孩`
  - `鑷畾涔夌洃鎺
  - `鏄ㄦ棩鏂板浜嬩欢濂楀埄`
- `鑷畾涔夌洃鎺 stays full-volume.
- Each summary item should prefer scanable compact output such as:
  - `浠ｇ爜 | 鍏抽敭浠锋牸 | 鏍稿績鎸囨爣 | 瑙﹀彂鍘熷洜`
- Summary must not degrade into a large dense free-text paragraph block.

### 28.4 Convertible-bond alert rule
- A new event-alert path is added for convertible bonds only in this round.
- Candidate rows come from sanitized public convertible-bond arbitrage rows.
- Trigger rule:
  - `premiumRate < convertPremiumLt`
- Default threshold:
  - `convertPremiumLt = -3`
- Alert payload row must include at least:
  - bond name / code
  - bond price
  - stock name / code
  - stock change percent
  - convert value
  - premium rate
  - trigger time
- Alert title is fixed to `鍙浆鍊哄紓鍔ㄦ彁閱抈.
- Alert content must include only the triggered rows and must not append the full summary content.

### 28.5 Cooldown and runtime-state rule
- Cooldown is tracked per bond + rule key.
- Default cooldown is `30` minutes and remains user-editable from the dashboard.
- Runtime state must track at least:
  - `lastEventAlertAttemptAt`
  - `lastEventAlertSuccessAt`
  - `lastEventAlertError`
  - per-item alert send timestamps for cooldown judgment
- Failed sends must not advance cooldown records.

### 28.6 Event-arbitrage next-day summary rule
- The system must track newly discovered event-arbitrage rows in push runtime state.
- On first initialization with no historical seen-map, the current live set is seeded silently and must not be treated as a new-item burst.
- Rows first discovered on day `D` may appear in the summary push on day `D+1`.
- This round does not send same-day event-arbitrage alert pushes.
- The concise event-arbitrage summary item should include:
  - name / symbol
  - event type
  - event stage or spread text when available

### 28.7 Config rule
- `config.yaml` active notification config must include:
  - `notification.summary`
  - `notification.event_alert`
- `notification.scheduler.merger_schedule` is removed from the active push config contract.
- `notification.enabled_modules.merger` is removed from the active summary-push module contract.
- `notification.wecom.push_html_url` remains part of the active config contract and should be backed by a real public URL in deployed runtime.

## 28. Dashboard UI Density And Hierarchy Spec (2026-03-24)

### 28.1 Scope
- This round changes only dashboard presentation behavior.
- No market-data schema, route path, sort rule, pagination size, push-config semantics, or monitor formula changes are allowed.
- Primary write scope is limited to:
  - `presentation/templates/dashboard_template.html`
  - `presentation/dashboard/dashboard_page.js`

### 28.2 Global layout rule
- Homepage structure remains:
  1. hero
  2. subscription section
  3. root tab navigation
  4. active module panel
  5. push strip
- The visual hierarchy must be tightened by reducing unnecessary vertical height in:
  - hero
  - section wrappers
  - cards
  - summary blocks
  - pagination / empty states
- The page keeps the existing dark-red design language and may refine contrast and spacing, but must not switch to a new visual system.

### 28.3 Toolbar and metadata rule
- Module toolbars must continue to expose current metadata, but with clearer scan order:
  - module title
  - key counts
  - update time
  - freshness/cache state
  - primary action when applicable
- Metadata emphasis may be changed through layout and typography only; wording and truthfulness must remain intact.

### 28.4 Summary-area rule
- Convertible-bond and premium summary areas remain visible, but become more compact.
- Summary rendering may tighten:
  - card padding
  - row spacing
  - title/subtitle spacing
  - value emphasis
- Summary content count stays aligned with current logic:
  - convertible-bond keeps three summary groups
  - AH / AB keep top-three and bottom-three groups
- Summary optimization must help the main tables enter the viewport earlier on desktop.

### 28.5 Shared component density rule
- Shared presentation elements may be compacted uniformly, including:
  - button height
  - input height
  - tab height
  - subtab height
  - table-wrapper padding perception
  - empty/loading-state minimum height
  - pagination spacing
- Shared density changes must preserve readability and clickability.

### 28.6 Responsive rule
- Existing breakpoints remain valid.
- Desktop prioritizes information density and hierarchy.
- Tablet/mobile keep the same responsive logic and may only receive proportional spacing compression.
- No new mobile-only card-table rewrite is allowed in this round.

### 28.7 Annotation rule
- Core layout changes and key style adjustments must keep concise Chinese comments in the implementation to explain intent and boundary.

## 29. Release-path Visibility And Fast Deploy Spec (2026-03-24)

### 29.1 `/api/health` version contract
- `GET /api/health` keeps the existing liveness payload and additionally returns:
  - `version.appVersion`
  - `version.gitSha`
  - `version.gitShortSha`
  - `version.gitBranch`
  - `version.gitCommitTime`
  - `version.startedAt`
  - `version.source`
- `version.source` is fixed to one of:
  - `git`
  - `env`
  - `package_only`
- `startedAt` is the current Node service process start time in ISO format.
- Version metadata resolution must be best-effort:
  - prefer explicit env override if present
  - otherwise read the current git checkout
  - otherwise fall back to package version only
- Health endpoint failure is forbidden just because git metadata lookup is unavailable.

### 29.2 Homepage version rendering rule
- The dashboard frontend may read version metadata from `GET /api/health`.
- Homepage hero must render a visible version text area that shows at least:
  - git short SHA when available
  - branch when available
  - app version
  - started-at time
- If version metadata is temporarily unavailable, the page must render an explicit fallback such as `鐗堟湰淇℃伅鏆傛湭杩斿洖`.
- This version area is informational only and must not block the rest of the dashboard render.

### 29.3 Fast deploy wrapper contract
- New server-side wrapper script:
  - `tools/deploy/update_fast.sh`
- `update_fast.sh` must delegate to `tools/deploy/update_from_github.sh` instead of duplicating deploy logic.
- `update_fast.sh` must set the existing deploy script into a dependency-skip mode by default:
  - `INSTALL_NODE_MODULES=0`
  - `INSTALL_PYTHON_REQUIREMENTS=0`
  - `VERIFY_PYTHON_IMPORTS=0`
- `update_fast.sh` must preserve the following checks from the full deploy path:
  - config syntax validation
  - git sync
  - service stop/restart
  - `/api/health` readiness check
  - homepage marker verification

### 29.4 Full deploy script extension
- `tools/deploy/update_from_github.sh` must support a new env flag:
  - `INSTALL_NODE_MODULES`
- `INSTALL_NODE_MODULES=1` keeps the current Node dependency install behavior.
- `INSTALL_NODE_MODULES=0` skips `npm ci` / `npm install` and logs that the step was intentionally skipped.
- Existing full deploy defaults remain unchanged.

### 29.5 GitHub Actions dispatch rule
- `.github/workflows/deploy.yml` keeps:
  - `push main` automatic deploy
  - `workflow_dispatch` manual deploy
- Manual dispatch adds `deploy_mode` with allowed values:
  - `full`
  - `fast`
- `push main` must continue using `full`.
- Manual `fast` deploy must execute `tools/deploy/update_fast.sh`.
- Manual `full` deploy and push-triggered deploy must execute `tools/deploy/update_from_github.sh`.

## 30. Cloud-only Runtime Surface Spec (2026-03-24)

### 30.1 Official runtime boundary
- Official runtime surface is fixed to:
  - cloud server process
  - cloud reverse proxy public entry
  - public homepage URL
  - public `/api/health`
- Windows-local stable-runtime helper flow is removed from the active repository runtime surface.
- Developer-only local execution remains allowed through:
  - `npm run dev`
  - `npm run start`
- These local commands are for development/verification only and must not be described as the formal operator entry.

### 30.2 Package-script rule
- `package.json` must not expose the following local-runtime management scripts:
  - `start:stable`
  - `stop:stable`
  - `show:access`
  - `install:stable-task`
  - `uninstall:stable-task`
- Any removed local-runtime scripts must not remain documented as official entrypoints in `RUNBOOK.md`.

### 30.3 Root access page rule
- Root `index.html` must become a cloud-access guidance page.
- It must not render:
  - local preview iframe
  - local template-open button
  - local service startup instructions
- It may fetch runtime access info when served over HTTP(S), and may show:
  - public homepage URL
  - public health URL
  - environment/access hint
- When opened directly as a file, it must state that the project is cloud-only and tell the user to use the deployed public URL or runbook instructions.

### 30.4 Dashboard wording rule
- Dashboard status/failure copy in `presentation/dashboard/dashboard_page.js` must not instruct the user to confirm a local service.
- Equivalent wording must be updated to neutral/cloud-safe phrasing such as:
  - confirm service is reachable
  - confirm cloud service is healthy

### 30.5 Repository file-surface rule
- The active repository must remove Windows-local stable-runtime helper files from the formal access surface, including:
  - `start_dashboard.bat`
  - `stop_dashboard.bat`
  - `tools/start_stable.ps1`
  - `tools/stop_stable.ps1`
  - `tools/keep_running.js`
  - `tools/install_stable_task.ps1`
  - `tools/uninstall_stable_task.ps1`
  - `tools/show_access_info.ps1`

## 31. Local Push-scheduler Suppression Spec (2026-03-24)

### 31.1 Runtime gate rule
- Timed push scheduling is additionally gated by effective runtime access shape.
- The scheduler must treat the runtime as local/development-only when `PUBLIC_BASE_URL` resolves to a loopback host:
  - `127.0.0.1`
  - `localhost`
  - `0.0.0.0`

### 31.2 Behavior rule
- When the runtime is loopback-only:
  - `runPushSchedulerCycle()` must not call timed push execution
  - scheduler health must report an intentional disabled state, not an operational failure
  - push delivery status must report scheduler disabled for runtime reasons
- Existing data-job scheduling remains unchanged.

### 31.3 Cloud-preservation rule
- When `PUBLIC_BASE_URL` is non-loopback, timed push scheduling remains unchanged:
  - same schedule parsing
  - same retry semantics
  - same runtime state updates

## 31. Core Cloud-env Sync Spec (2026-03-24)

### 31.1 Scope
- This round adds a deployment/config-sync helper only.
- No dashboard route, market-data formula, scheduler rule, or push-format change is allowed in this round.

### 31.2 Command contract
- `package.json` must expose a stable local command:
  - `npm run sync:server:env`
- The command must run a repository-owned script under `tools/deploy/`.

### 31.3 Authoritative input contract
- The sync script must read `ops/server_profile.local.yaml` first.
- Required profile fields for this round:
  - `connection.host`
  - `connection.port`
  - `connection.user`
  - one of `connection.password` or `connection.private_key`
  - `app.env_file`
  - `app.service_name`
- The sync script may also read effective local config to obtain already-known env-backed secrets, but must not ask the operator to re-enter values that are already stored in the profile.

### 31.4 Remote env mapping rule
- The sync script must upsert remote `.env` keys while preserving unrelated existing keys.
- The minimum key mapping contract is:
  - `WECOM_WEBHOOK_URL`
    - source priority: `ops/server_profile.local.yaml > notifications.wecom_webhook_url`
  - `PUBLIC_BASE_URL`
    - source priority: `ops/server_profile.local.yaml public_url > effective config deployment.public_base_url`
  - `PUSH_HTML_URL`
    - source priority: `ops/server_profile.local.yaml public_url with trailing slash > effective config notification.wecom.push_html_url`
  - `ALPHA_MONITOR_HTML_URL`
    - same normalized value as `PUSH_HTML_URL`
- Additional keys may be synced when the effective local config already resolves them to non-empty values, including:
  - `DEEPSEEK_API_KEY`
  - `DEEPSEEK_BASE_URL`
  - `JISILU_COOKIE`

### 31.5 Runtime-apply rule
- When the sync script changes any remote `.env` value, it must:
  - restart the configured managed service
  - check the configured local health endpoint on the server
- When no value changes, the script may skip restart and must report `already_in_sync`-style output.

### 31.6 Safety/output rule
- The sync script must support a dry-run mode.
- The script output must summarize:
  - target host
  - target remote env file
  - changed keys
  - whether service restart was performed
  - whether health check passed
- The script must never print full secret values back to stdout.

## 32. Core-table Concentration + Dividend Watchlist Merge Spec (2026-03-24)

### 32.1 Convertible volatility visibility rule
- `buildConvertibleColumns()` keeps `volatility60 ?? annualizedVolatility` as the visible read path for `60鏃ユ尝鍔ㄧ巼`.
- The field stays in the default main table instead of being pushed behind non-core trailing fields.
- User-facing copy must describe this field as historical K-line real-data volatility, not a fabricated placeholder metric.

### 32.2 Wide-table width rule
- Shared wide tables continue using one-field-per-column output.
- Shared table rendering may add column-level width hints so:
  - code / date / compact numeric columns consume narrower fixed guidance
  - core text columns keep readable minimum width
  - low-priority trailing columns absorb the remaining horizontal overflow
- Shared CSS may reduce horizontal padding and table-kind min widths when this improves first-screen field concentration without shrinking font size back down.

### 32.3 AB top-summary rule
- `renderPremiumPanel('ab')` must resolve its visible summary column independently from the current table sort state.
- `AB婧环` top cards always use the `premium` field for:
  - title text
  - top-three sorting
  - bottom-three sorting
  - value rendering / status color
- `AH婧环` may keep the current summary-column-follow-sort behavior unless a later approved round changes it.

### 32.4 Dividend watchlist merge rule
- Dividend runtime reading is split into:
  - manual dividend portfolio rows
  - auto-derived stock rows from existing custom monitors
- Merge rules:
  - prefer manual dividend row data when the same code exists in both sources
  - only add monitor-derived rows when their stock code is non-empty and not already present
  - keep de-duplication by normalized code
- Refresh rules:
  - manual dividend portfolio persistence remains the source of truth for explicit dividend adds/removes
  - auto-derived monitor rows are enrichable for display but must not silently break manual persistence semantics

## 32. Subscription Payment-day Truth Spec (2026-03-24)

### 32.1 Scope
- This round changes only the subscription top-table display judgment.
- No subscription fetch source, route shape, or historical row schema changes are allowed.

### 32.2 Stage rule
- `浠婃棩鐢宠喘` remains `subscribeDate = today`.
- `浠婃棩涓缂存` is corrected to `paymentDate = today`.
- `浠婃棩涓婂競` remains `listingDate = today`.

### 32.3 Visible date mapping rule
- In the dashboard top subscription table:
  - `鐢宠喘鏃 renders `subscribeDate`
  - `涓缂存鏃 renders `paymentDate`
  - `涓婂競鏃 renders `listingDate`
- `lotteryDate` must not be used as the rendered value of `涓缂存鏃.

### 32.4 Regression acceptance
- For live 2026-03-24 data, `闅嗘簮鑲′唤` must not be classified as `浠婃棩涓缂存` because its `paymentDate` is 2026-03-25.
- The same day view must include the real 2026-03-24 payment rows such as `鐩涢緳鑲′唤`銆乣鎱ц胺鏂版潗`銆乣娉伴噾鏂拌兘`.

## 33. Dashboard Module Footnote Spec (2026-03-24)

### 33.1 Scope
- This round adds only explanatory footer rendering for dashboard modules.
- No fetch plugin, strategy plugin, or business formula result changes are included.

### 33.2 Config contract
- `config.yaml` adds `presentation.dashboard_module_notes`.
- Supported module keys in this round:
  - `subscription`
  - `cbArb`
  - `ah`
  - `ab`
  - `monitor`
  - `dividend`
  - `merger`
- Each module note object supports:
  - `data_sources: string[]`
  - `formulas: string[]`
  - `strategy_notes: string[]`

### 33.3 API contract
- `GET /api/dashboard/ui-config` continues returning `tableUi`.
- The same response now also returns `moduleNotes`.
- `moduleNotes` shape mirrors the normalized config contract and is read-only.

### 33.4 Front-end rendering contract
- Dashboard uses one shared renderer for module footnotes.
- Standard section order:
  - `数据来源`
  - `计算公式`
  - `策略说明`
- The shared renderer:
  - hides empty sections
  - hides the whole footnote card when a module has no configured lines
  - renders after the main module content rather than inside table cells
- Covered placements:
  - `股债打新` top section
  - each of the six tab panels

### 33.5 Style boundary
- Footnote blocks use shared dashboard styles and must not create a separate page layout framework.
- The implementation may add minimal CSS for:
  - footnote card shell
  - section titles
  - line lists
- Existing summary cards, tables, detail rows, and pagination layout must remain intact.

## 33. DB-authoritative Convertible Volatility Spec (2026-03-24)

### 33.1 Volatility sample rule
- `volatility20` uses the latest `20` close-to-close log returns.
- `volatility60` uses the latest `60` close-to-close log returns.
- `volatility120` uses the latest `120` close-to-close log returns.
- Therefore the read path must load at least `121` closes for the largest current window.

### 33.2 Database authority rule
- The visible convertible-bond volatility fields are calculated from `runtime_data/shared/stock_price_history.db`.
- Backfill logic may append missing local rows, but the final volatility read still comes from the local database rows after hydration.

### 33.3 History sync preservation rule
- `data_fetch/convertible_bond/history_source.py` and its script mirror must not prune each symbol to `120` rows after sync.
- The historical K-line library is preserved as the authority for later volatility recomputation and verification.

## 34. Full CB History Sync + Real Example Note Spec (2026-03-24)

### 34.1 Refresh sequencing rule
- Full convertible-underlying HFQ history sync runs before the refreshed convertible-bond theoretical metrics are trusted.
- After the history sync, the convertible-bond dataset must be rebuilt so `callOptionValue*`, `putOptionValue*`, `theoreticalPrice*`, and `theoreticalPremiumRate*` reflect the latest volatility inputs.

### 34.2 On-page real example rule
- `renderConvertibleBondPanel()` must render a note that includes:
  - the database-based volatility explanation
  - one real current row example from the active dataset when such a row is available
- The example may use either:
  - `鍊哄簳 + 鐪嬫定鏈熸潈`
  - or `鍊哄簳 + 鐪嬫定鏈熸潈 - 鐪嬭穼鏈熸潈`
- The displayed numbers must come from the same row payload already shown in the table.

## 35. Convertible Volatility Percent Display Spec (2026-03-24)

### 35.1 Payload unit rule
- `volatility60` and `annualizedVolatility` remain ratio-form numeric fields in the payload.
- Example: `0.3491101749` represents `34.91101749%`.

### 35.2 Front-end display rule
- The dashboard front end must multiply the ratio by `100` when rendering human-readable volatility percentages.
- The display helper used for this rule must not change the underlying numeric sort value.

### 35.3 Coverage rule
- This rule applies to:
  - the convertible-bond `60鏃ユ尝鍔ㄧ巼` table column
  - the bottom real-example note built from the same row payload

## 36. Scheduled Push Truth Recovery Spec (2026-03-24)

### 36.1 Scope
- This round only changes push-scheduler runtime-state trust and scheduler observability.
- No summary module composition, route shape, or notification channel contract changes are included.

### 36.2 Current-day slot trust rule
- `mainPushRecords[date]` remains a persisted helper record, not the sole source of truth.
- During scheduled evaluation for the current Shanghai date:
  - the runtime layer must first intersect persisted slots with the active configured schedule
  - then prune any slot whose scheduled minute is later than the latest same-day scheduled-push success minute
- If no latest same-day success timestamp exists, current-day persisted scheduled slots are treated as untrusted and must not suppress due sends.

### 36.3 Self-healing persistence rule
- When the runtime layer prunes dirty scheduled slots for the current date, it must persist the cleaned record back into `push_runtime_state.json`.
- Self-healing only affects the scheduler's own scheduled-slot record storage.
- Event-alert cooldown records and event-arbitrage seen caches are not touched.

### 36.4 Success / retry rule
- `setPushAttempt('main', ...)` may run before downstream delivery.
- `setPushRecord('main', date, [slot...])` and `setPushSuccess('main', ...)` still run only after `pushByModulesToWeCom()` resolves successfully.
- On downstream failure:
  - `lastMainPushError` is updated
  - the scheduled slot stays absent from the sent-slot record
  - the next scheduler tick may retry the same slot

### 36.5 Scheduler logging rule
- The scheduler must log at least:
  - normalized schedule list for the current tick
  - each slot that is skipped because it is not due yet
  - each slot skipped because it is already truthfully sent
  - each slot attempt
  - each slot success
  - each slot failure with error message
- Log lines must include enough context to identify date and slot from `journalctl -u alpha-monitor`.

## 37. Convertible Underlying ATR + Liquidity Spec (2026-03-25)

### 37.1 Scope
- This round changes only the convertible-bond history-support fields, cb-arb payload shaping, and cb-arb table rendering.
- No push rule, AH/AB payload, or theoretical-pricing formula change is included.

### 37.2 History-store rule
- The local `stock_price_history.db` authority for convertible underlyings must support at least:
  - `close_hfq`
  - `high_hfq`
  - `low_hfq`
  - `amount_yuan`
- Existing rows without the new columns are allowed and must be forward-compatible through additive schema migration.

### 37.3 ATR rule
- `stockAtr20` uses the latest `20` true-range samples.
- True range for each day is:
  - `max(high-low, abs(high-prev_close), abs(low-prev_close))`
- Therefore ATR20 requires at least `21` sequential bars with valid close/high/low values.
- Output unit remains the underlying-stock price unit, not a percentage.

### 37.4 Turnover-average rule
- `stockAvgTurnoverAmount20Yi` uses the latest `20` valid daily鎴愪氦棰?samples.
- `stockAvgTurnoverAmount5Yi` uses the latest `5` valid daily鎴愪氦棰?samples.
- Stored source unit is yuan; outward payload unit is `浜縛.

### 37.5 Public payload rule
- Public `cbArb` rows must additionally preserve:
  - `stockAtr20`
  - `stockAvgTurnoverAmount20Yi`
  - `stockAvgTurnoverAmount5Yi`
  - `remainingSizeYi`
- Dashboard column rendering must expose the same fields in the main table.

## 32. Convertible Discount Strategy Spec (2026-03-25)

### 32.1 Core formula contract
- discountRate = -premiumRate
- stockAtr20 = avg(TR[-20:])
- stockAtr20Pct = stockAtr20 / stockPrice * 100
- trRatio = discountRate / stockAtr20Pct
- weightedDiscountRate = discountRate * atrCoefficient * sellPressureCoefficient * boardCoefficient

### 32.2 Board mapping rule
- stock code prefix 688 -> 科创板 / coefficient 1
- stock code prefix 300 or 301 -> 创业板 / coefficient .85
- all other A-share stock codes -> 主板 / coefficient .8

### 32.3 Signal-state rule
- buy alert is emitted only on zone crossing into discountRate > 2%
- sell alert is emitted only for monitored bonds and only on zone crossing into discountRate < 0.5%
- monitored bonds auto-enter on buy crossing and auto-exit on sell crossing
- bootstrap seeds the monitored list silently and must not emit historical buy alerts

### 32.4 Runtime-state contract
- independent state file: untime_data/shared/cb_discount_strategy_state.json
- minimum persisted fields:
  - monitored bond map/list
  - prior buy-zone state
  - prior sell-zone state
  - latest buy push success/error
  - latest sell push success/error
  - latest monitor push success/error
  - latest bootstrap date

### 32.5 Push-scheduler contract
- the old cooldown-based cb event-alert due check no longer defines the production behavior
- timed monitored-list push schedule is fixed to:
  - 9:30, 09:40, ... , 11:30
  - 13:00, 13:10, ... , 14:50
- the monitored-list push may skip when the monitored list is empty
- 14:50 remains a mandatory monitored-list push point when the list is non-empty

### 32.6 Public API contract
- GET /api/market/convertible-bond-arbitrage row payload must additionally preserve:
  - discountRate
  - weightedDiscountRate
  - stockAtr20Pct
  - trCoefficient
  - sellPressureRatio
  - sellPressureCoefficient
  - oardType
  - oardCoefficient
  - isDiscountMonitorActive
- the same response must additionally expose discountMonitorSummary with:
  - count
  - items
- discountMonitorSummary.items is the full monitored list and must not be truncated to top 3 by the backend contract

### 32.7 Dashboard contract
- in 转债套利 top summary cards, the old 转股套利候选 card is removed
- it is replaced by 折价监控
- the card renders the full monitored list using the current card layout
- each row must show at least:
  - 转债名称/代码
  - 折价率
  - 加权折价率
- the main convertible table adds visible sortable columns:
  - 折价率
  - 加权折价率

### 32.8 Push-settings contract
- push settings no longer render 异动冷却(分钟)
- push status wording no longer describes the obsolete 转股溢价率 < -3% rule
- GET /api/push/config must expose discount-strategy runtime status instead of old cooldown-based cb event-alert config

## 33. Convertible Rights-Issue Monitoring Spec (2026-03-25)

### 33.1 Scope
- This round adds a new independent module only:
  - `data_fetch/cb_rights_issue`
  - `strategy/cb_rights_issue`
  - dashboard `可转债抢权配售` page
  - module-local push config/runtime
- No existing `event_arbitrage.rights_issue` semantics are changed in this round.

### 33.2 Source rule
- Fixed source page:
  - `https://www.jisilu.cn/web/data/cb/pre`
- Fixed machine fetch endpoint:
  - `https://www.jisilu.cn/webapi/cb/pre/?history=0`
- Fetch requests must send a real browser-like header set at least including:
  - `User-Agent`
  - `Referer: https://www.jisilu.cn/web/data/cb/pre`
  - `Accept: application/json,text/plain,*/*`
- Phase-1 does not include user-entered URL parsing or arbitrary announcement-page parsing.

### 33.3 Python action / dataset rule
- `data_dispatch.py` adds:
  - `cb-rights-issue`
  - `sync-cb-rights-issue-stock-history`
- `start_server.js` adds dataset key:
  - `cbRightsIssue`
- `cbRightsIssue` dataset fetch path:
  - force / dailySync may run `sync-cb-rights-issue-stock-history` first
  - then run `cb-rights-issue`
- `cbRightsIssue` dataset participates in:
  - initial dashboard load
  - intraday refresh
  - daily sync

### 33.4 Dedicated stock-history DB rule
- A new dedicated SQLite DB is required for this module only.
- Recommended file:
  - `runtime_data/shared/cb_rights_issue_stock_history.db`
- Minimum schema contract:
  - `stock_price_history(symbol, trade_date, close_hfq, source, created_at, updated_at)`
  - `stock_price_sync_state(symbol, last_trade_date, source, updated_at)`
  - `stock_symbol_universe(symbol, status, note, updated_at)`
- Sync rule:
  - the DB stores real `后复权` closes for this module
  - incremental by default using `last_trade_date - 5 days`
  - force-full path is supported
  - latest trading-day row must be appended/updated daily
- Read rule:
  - `60日波动率` requires at least `61` closes from this dedicated DB
  - the DB is used for volatility only and not for strike-reference override
  - if rows are still insufficient after sync, the feature row remains non-eligible

### 33.5 Normalized row contract
- Each normalized row must preserve at least:
  - `bondCode`
  - `bondName`
  - `stockCode`
  - `stockName`
  - `stockPrice`
  - `convertPrice`
  - `progress`
  - `progressName`
  - `progressDate`
  - `progressFull`
  - `applyDate`
  - `recordDate`
  - `listDate`
  - `rationPerShare`
  - `apply10`
  - `sourceUrl`
- Raw-source fields may also be preserved in `raw`.

### 33.6 Strategy formula rule
- `行权价 = max(source convertPrice, 当前价)`
- source `convertPrice` is treated as the source-provided `20日均值` proxy
- `期权数量 = 1000 / 行权价`
- `配售所需资金 = 配售10张实际所需股数 × 当前股价`
- `配售预期收益 = 单位期权价值 × 期权数量`
- `预计收益率 = 配售预期收益 / 配售所需资金`
- `单位期权价值` uses:
  - current stock price
  - exercised reference price
  - real 10Y treasury yield
  - real 60-day historical volatility
  - fixed term `6年`
- Phase-1 implementation may use a self-contained option-pricing helper in `strategy/cb_rights_issue`, but it must stay inside the strategy layer and use only the approved real inputs above.

### 33.7 Required-shares rule
- For `配售10张实际所需股数`:
  - if the stock is Shenzhen-market:
    - compute raw required shares for 10 bonds
    - round up to the next `100`
  - if the stock is Shanghai-market:
    - compute raw required shares for 10 bonds
    - multiply by `0.6`
    - round up to the next `100`
- Output field must preserve:
  - raw required shares
  - adjusted required shares
  - final rounded required shares
  - market rule text

### 33.8 Stage eligibility rule
- A row is stage-eligible when either:
  - `progressName` contains `上市委通过`
  - `progressName` contains `同意注册` or `注册生效`
  - `applyDate` is a valid date
- Rows outside these conditions remain visible in `sourceRows` but cannot enter `monitorList`.

### 33.9 Response contract
- `GET /api/market/cb-rights-issue` success payload must include:
  - `monitorList: []`
  - `sourceRows: []`
  - `sourceSummary: {}`
  - `rebuildStatus: {}`
  - `updateTime`
  - `source`
- `monitorList` rows must additionally preserve:
  - `stageEligible`
  - `monitorEligible`
  - `requiredSharesRaw`
  - `requiredSharesAdjusted`
  - `requiredSharesFinal`
  - `requiredFunds`
  - `optionStrikePrice`
  - `optionQuantity`
  - `volatility60`
  - `treasuryYield10y`
  - `optionUnitValue`
  - `expectedProfit`
  - `expectedReturnRate`
- `sourceSummary` must include at least:
  - `totalRows`
  - `eligibleStageCount`
  - `monitorEligibleCount`
  - `highReturnCount`
  - `sourceUrl`
  - `sourceTitle`

### 33.10 Runtime-state contract
- New runtime files must be independent from existing push/runtime files, at least:
  - `cb_rights_issue_state.json`
  - `cb_rights_issue_push_config.json`
  - `cb_rights_issue_push_runtime.json`
- `cb_rights_issue_state.json` minimum fields:
  - `monitorList`
  - `sourceRows`
  - `sourceSummary`
  - `lastRebuildAt`
  - `lastRebuildDate`
  - `lastRebuildError`
- `cb_rights_issue_push_runtime.json` minimum fields:
  - `pushRecords`
  - `lastAttemptAt`
  - `lastSuccessAt`
  - `lastError`

### 33.11 Push-config contract
- `GET /api/push/cb-rights-issue-config` returns:
  - `enabled`
  - `times`
  - `deliveryStatus`
- `POST /api/push/cb-rights-issue-config` accepts:
  - `enabled`
  - `times`
- Default schedule:
  - `08:00`
  - `14:30`
- `deliveryStatus` must at least expose:
  - `webhookConfigured`
  - `schedulerEnabled`
  - `lastAttemptAt`
  - `lastSuccessAt`
  - `lastError`

### 33.12 Scheduler rule
- Main summary scheduler remains unchanged.
- A second independent scheduler branch must evaluate `cb_rights_issue` push slots.
- The scheduler must:
  - normalize the configured time list
  - send only when the current slot is due and not truthfully sent
  - mark success only after downstream WeCom delivery succeeds
  - keep failed slots retryable
- Push content must be generated only from the current `monitorList`.
- If `monitorList` is empty, the scheduler may skip delivery and should not fake a success.

### 33.13 Dashboard contract
- Root tab order becomes:
  - `转债套利`
  - `AH溢价`
  - `AB溢价`
  - `监控套利`
  - `分红提醒`
  - `事件套利`
  - `可转债抢权配售`
- The new page renders:
  - top summary/meta area
  - monitor list table
  - module-local push-settings card
  - fixed-source structured-info table
  - module footnote
- The page must not render a separate URL input card.
- The monitor list table uses the shared paginated table renderer and keeps `50` rows per page.
- The fixed-source structured-info table also uses the shared paginated table renderer and keeps `50` rows per page.

### 33.14 Footnote contract
- `config.yaml > presentation.dashboard_module_notes` adds key:
  - `cbRightsIssue`
- `GET /api/dashboard/ui-config` must return this note under `moduleNotes`.
- The page footnote uses the same shared renderer and standard section order:
  - `数据来源`
  - `计算公式`
  - `策略说明`

### 33.15 Failure / truthfulness rule
- If source fetch fails, DB sync fails, treasury yield is unavailable, or volatility remains unavailable:
  - the API must return the real failure state
  - the row must not enter `monitorList`
  - the page must not fabricate missing results

## 34. 转债套利 / AH / AB 主表搜索 Spec (2026-03-25)

### 34.1 Scope
- This round is presentation-only.
- No new API, route, fetch-plugin, or strategy-plugin behavior is added.

### 34.2 State rule
- Shared dashboard table state adds one search field for searchable tables:
  - `searchQuery`
- Covered tables:
  - `cbArb`
  - `ah`
  - `ab`

### 34.3 Match rule
- Search is case-insensitive.
- The query is trimmed before matching.
- When the query contains spaces, the effective tokens are split by whitespace and all tokens must match the aggregated searchable text.
- Searchable text mapping:
  - `cbArb`: `code`, `bondName`, `stockCode`, `stockName`
  - `ah`: `aCode`, `aName`, `hCode`, `hName`
  - `ab`: `aCode`, `aName`, `bCode`, `bName`

### 34.4 Table pipeline rule
- Shared table processing order becomes:
  1. search filter
  2. column sort
  3. 50-row pagination
- Pagination status continues to reflect the filtered result set.

### 34.5 UI rule
- Each covered module renders one search box directly above the main table.
- The search box must provide:
  - keyword input
  - clear action
  - short hint text indicating searchable fields
- Search input must preserve focus across in-panel re-render.
- IME composition text is not committed until `compositionend`; during composition the table must not force a re-render that breaks Chinese input.
- Clearing the keyword resets the current page to page 1 of the full result set.

## 35. Convertible Pure-bond Truth + Search Focus Spec (2026-03-25)

### 35.1 Scope
- This round changes:
  - convertible-bond pure-bond-value hydration
  - convertible theoretical-pricing base selection
  - shared search-input interaction stability for `cbArb / ah / ab`
- This round does not change:
  - route paths
  - AH / AB business formulas
  - table search field scope

### 35.2 Pure-bond source rule
- `pureBondValue` must prefer a real upstream value from the Eastmoney convertible value-analysis source for the same bond code.
- The fetch path may call the latest-row endpoint shape of:
  - `https://datacenter-web.eastmoney.com/api/data/get`
  - `type=RPTA_WEB_KZZ_LS`
  - filtered by `zcode="<bondCode>"`
- The implementation must read the latest available row and extract at least:
  - `PUREBONDVALUE`
  - `DATE`
- If the latest row is blank, the read path may walk backward to the latest valid `PUREBONDVALUE`.

### 35.3 Pricing base rule
- `_build_theoretical_metrics(...)` must use:
  - `pureBondValue` when available
  - otherwise fallback to the existing discount-floor `bondValue`
- Truth boundary:
  - `pureBondValue` stays `null` when the real source is unavailable
  - the fallback discount-floor value may still populate `bondValue`
  - the fallback value must not overwrite `pureBondValue`

### 35.4 Outward payload rule
- Public convertible rows continue exposing:
  - `pureBondValue`
  - `bondValue`
- The row may additionally preserve:
  - `pureBondValueDate`
  - `pureBondValueSource`
- Existing front-end rendering remains compatible through:
  - pure-bond-base display prefers `pureBondValue`
  - fallback remains `bondValue`

### 35.5 Search focus rule
- Shared search-state updates for `cbArb / ah / ab` must preserve:
  - active input focus
  - caret selection range when practical
- The re-render path must restore focus to the same search input after panel redraw.
- Clicking the search `清空` button must return focus to the corresponding input.

### 35.6 IME composition rule
- During `compositionstart -> compositionend`:
  - query text may update in state
  - table filtering must not trigger panel re-render
- On `compositionend`, the final committed text must trigger the normal filter render exactly once.

## 36. Convertible Strike-price Simplification Spec (2026-03-25)

### 36.1 Scope
- This round changes only the strike-price rule inside convertible theoretical pricing.
- This round does not change:
  - route shape
  - pure-bond source truth rule
  - branch rule for redeem-trigger handling

### 36.2 Call-strike rule
- In `_build_theoretical_metrics(...)`, when `convertPrice > 0`:
  - `optionQty = 100 / convertPrice`
  - `callStrike = convertPrice`
- The old derived-strike rule is removed:
  - `max(bondValue / optionQty, convertPrice)` is no longer allowed

### 36.3 Pricing branch rule
- Keep the existing branch:
  - if `stockPrice < redeemTriggerPrice`, theoretical price = `bondValue + call`
  - else theoretical price = `bondValue + call - put`
- Only the strike-price input to the call-option leg changes in this round.

### 36.4 Outward payload rule
- `callStrike20 / callStrike60 / callStrike120` must equal the same row's `convertPrice` when `convertPrice` is valid.

## 37. Convertible Sticky Bond-name Column Spec (2026-03-25)

### 37.1 Scope
- This round changes only the convertible main-table presentation.
- No payload, route, or strategy change is included.

### 37.2 Column-order rule
- In `buildConvertibleColumns()`, the leading identifier order for the convertible main table is:
  - `序号`
  - `转债代码`
  - `转债名称`
- Remaining field coverage stays unchanged.

### 37.3 Sticky-column rule
- Only the convertible main table receives a sticky left column in this round.
- The sticky target is the convertible identifier zone:
  - `序号`
  - `转债代码`
  - `转债名称`
- Required behavior:
  - keep the left identifier zone fixed while the table scrolls horizontally
  - preserve sticky header behavior at the top
  - keep text readable through an explicit background and stacking order

### 37.4 Style boundary
- Implementation may add a dedicated convertible-only column class such as:
  - `col-index-sticky`
  - `col-code-sticky`
  - `col-bond-sticky`
- Sticky styling must not accidentally affect:
  - premium tables
  - monitor tables
  - rights-issue tables

## 36. Shared DB Auto-update + Rolling Retention Spec (2026-03-25)

### 36.1 Scope
- This round changes only the database-maintenance path for shared SQLite stores.
- No dashboard route shape, pricing formula, or push template change is included.

### 36.2 DB classification rule
- `premium_history.db`
  - already keeps incremental historical writes plus old-row pruning
  - no new behavior is added in this round
- `market_pairs.db`
  - remains a pair-master database rather than a growing time-series store
  - no new retention behavior is required in this round
- The following databases must support auto-prune immediately after sync:
  - `subscription_history.db`
  - `stock_price_history.db`
  - `cb_rights_issue_stock_history.db`

### 36.3 Subscription-history retention rule
- `data_fetch/subscription/ipo_source.py` and `data_fetch/subscription/bond_source.py` continue to:
  - fetch live rows
  - upsert into `subscription_history.db`
- After each successful sync write, the same chain must prune rows older than the configured retention days.
- Retention cutoff is date-based and applies to `subscribe_date`.
- The retention parameter is read from `config.yaml` and must not be hardcoded in the fetch modules.

### 36.4 Convertible underlying-history retention rule
- `data_fetch/convertible_bond/history_source.py` remains the official incremental sync path for `stock_price_history.db`.
- Sync continues to append or backfill only the needed recent window based on:
  - missing rich-bar coverage
  - latest stored trade date
- After the sync batch finishes, the same path must call a rolling per-symbol prune.
- Rolling prune rule:
  - keep only the most recent configured row count for each symbol
  - delete older rows beyond that limit
  - delete orphaned sync-state rows when a symbol no longer has price rows
- The configured kept row count must stay safely above the live calculation floor for:
  - `120日波动率` requiring `121` closes
  - `ATR20` requiring `21` rich bars
  - `20日/5日平均成交额`

### 36.5 Rights-issue underlying-history retention rule
- `data_fetch/cb_rights_issue/history_source.py` remains the official incremental sync path for `cb_rights_issue_stock_history.db`.
- After the sync batch finishes, the same path must call a rolling per-symbol prune.
- Rolling prune rule:
  - keep only the most recent configured row count for each symbol
  - delete older rows beyond that limit
  - delete orphaned sync-state rows when a symbol no longer has price rows
- The configured kept row count must stay safely above the live calculation floor for `60日波动率` requiring `61` closes.

### 36.6 Config contract
- `config.yaml` adds the formal retention controls:
  - `data_fetch.plugins.subscription.history_retention_days`
  - `data_fetch.plugins.convertible_bond.stock_history_retention_rows`
  - `data_fetch.plugins.cb_rights_issue.stock_history_retention_rows`

## 38. Server-authoritative Refresh + Status-first Dashboard Polling Spec (2026-03-25)

### 38.1 Refresh ownership
- The active refresh model for this round is:
  - server scheduler = authoritative refresh owner
  - dashboard = cache/state reader
- The existing scheduler tick remains `60s`.
- The dashboard auto-refresh loop is also `60s`, but it is status-first and must
  not redefine source freshness.

### 38.2 Config contract
- `config.yaml` adds `presentation.dashboard_auto_refresh` with at least:
  - `enabled`
  - `interval_ms`
  - `mode=status`
  - `current_tab_only=true`
  - `reload_data_on_cache_change=true`
- `GET /api/dashboard/ui-config` returns these values under a presentation-safe
  `autoRefresh` object for the static page.

### 38.3 Resource-status API
- Add a lightweight dashboard endpoint:
  - `GET /api/dashboard/resource-status`
- Query parameter:
  - `keys` = comma-separated logical resource keys
- Supported keys for this round include at least:
  - `exchangeRate`
  - `ipo`
  - `bonds`
  - `cbArb`
  - `ah`
  - `ab`
  - `merger`
  - `cbRightsIssue`
- Each returned item exposes at least:
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`
  - `refreshing`
- `merger` may be implemented as a stable alias to the current event-arbitrage dataset owner.

### 38.4 Convertible read-path rule
- Ordinary `GET /api/market/convertible-bond-arbitrage` reads must not wait for
  `sync-cb-stock-history`.
- Allowed places for `sync-cb-stock-history` in this round:
  - daily sync path
  - explicit maintenance path
  - other background-maintenance orchestration when deliberately invoked
- The outward cb-arb payload remains backward compatible and may additionally
  carry:
  - `cacheTime`
  - `servedFromCache`
  - `refreshing`

### 38.5 Frontend bootstrap and polling rule
- Initial dashboard bootstrap loads:
  - `ui-config`
  - `health`
  - `push-config`
  - shared header datasets actually used by the visible header
  - the current active tab dataset(s)
- Hidden tabs must not be loaded during bootstrap unless they are header dependencies.
- The minute polling loop:
  - polls `GET /api/dashboard/resource-status`
  - updates local status/freshness text immediately
  - reloads full data only when metadata changed
  - for non-dataset tabs such as runtime-state pages, may keep active-tab-only lightweight full reload behavior

### 38.6 Dead-path cleanup rule
- Stale LOF dashboard interaction branches must not remain active in
  `dashboard_page.js`.
- Current dashboard code must not require undefined LOF constants or renderers
  during click handling.
- These values are consumed directly by the corresponding sync / DB modules.

### 36.7 Truthful sync-result rule
- Sync result payloads for the affected history jobs must expose the real prune count returned by the DB layer.
- A fixed placeholder such as `prunedRows: 0` is no longer allowed once prune logic has actually run.

### 36.8 Simplicity rule
- The implementation must keep the shortest path:
- daily incremental append/update
- immediate prune of excess history
- This round does not introduce:
  - cold archive tables
  - monthly partitions
  - multi-tier storage

## 39. LOF Arbitrage Restoration Spec (2026-03-25)

### 39.1 Scope
- This round restores `LOF套利` as an active homepage module.
- This round adds:
  - one new fetch plugin `data_fetch/lof_arbitrage`
  - one new strategy plugin `strategy/lof_arbitrage`
  - one new dashboard tab and page
  - one new market API
  - one new independent push module
- This round does not change:
  - `AH / AB` formula semantics
  - `转债套利` strategy semantics
  - `事件套利` route shape

### 39.2 Source-entry rule
- The authoritative user-facing source-entry URLs are:
  - `https://www.jisilu.cn/data/lof/#index`
  - `https://www.jisilu.cn/data/qdii/#qdiie`
  - `https://www.jisilu.cn/data/qdii/#qdiia`
- The fetch plugin may resolve the real page-backed JSON list endpoints exposed by those pages:
  - `GET /data/lof/index_lof_list/`
  - `GET /data/qdii/qdii_list/E`
  - `GET /data/qdii/qdii_list/A`
- The fetch plugin must keep both:
  - `sourcePageUrl`
  - `sourceApiUrl`
  in the outward source summary for diagnosis.

### 39.3 Source access rule
- Fetch priority is:
  1. Firecrawl page read when enabled and configured
  2. direct JSON / direct page fallback
- Firecrawl configuration is read only from `config.yaml` and env placeholders.
- Direct fallback remains production-safe and must work without Firecrawl.
- Any one source-group failure degrades only that group and may not blank the whole page.

### 39.4 Fetch normalization rule
- `data_fetch/lof_arbitrage/source.py` is responsible for:
  - reading the three source groups
  - normalizing source rows into one internal row shape
  - applying sample filtering
  - hydrating external index / fx helper inputs when needed
  - returning group-level source status
- `data_fetch/lof_arbitrage/normalizer.py` only maps the fetch snapshot into bus records and must not contain strategy formulas.
- Minimum normalized row fields include:
  - `code`
  - `name`
  - `marketGroup`
  - `price`
  - `changeRate`
  - `turnoverWan`
  - `shareAmountWan`
  - `shareAmountIncreaseWan`
  - `nav`
  - `navDate`
  - `indexIncreaseRate`
  - `indexName`
  - `applyFee`
  - `applyStatus`
  - `redeemFee`
  - `redeemStatus`
  - `custodianFee`
  - `sourcePageUrl`
  - `sourceApiUrl`
  - `raw`

### 39.5 Filter rule
- The fetch layer must keep only LOF rows:
  - `qdii_list` rows require `lof_type == 'QDII'` or row name contains `LOF`
  - `index_lof_list` rows are accepted as domestic index LOF candidates
- The fetch layer must exclude rows whose `名称` contains `ETF`.
- Rows filtered out by these rules must not enter the strategy layer.

### 39.6 Index / FX helper rule
- The implementation should prefer a small shared helper set instead of many fragmented APIs.
- Allowed helper pattern for this round:
  - Tencent real-time quote family for index points and major FX
  - source-provided index increase fields for `指数LOF / QDII亚洲`
- `QDII欧美`:
  - when an external index point + historical FX path is resolvable, compute the full approved formula
  - when not resolvable but the source exposes a real estimate-change field, the row may be marked as source-estimate based instead of being dropped
  - outward row must expose which basis was used via `calcStatus` / `calcMode`
- The row must never pretend an unresolved external mapping is a full direct-index calculation.

### 39.7 Strategy rule
- `strategy/lof_arbitrage/service.py` is responsible for:
  - IOPV calculation
  - premium-rate calculation
  - limited / unlimited pool classification
  - push-facing row shaping
- Premium formula is fixed:
  - `premiumRate = (iopv / price) - 1`
- `QDII欧美` direct calculation path:
  - `iopv = nav_t2 * (currentIndex / closeIndexT2) * (currentFx / closeFxT2)`
- `指数LOF / QDII亚洲` calculation path:
  - `iopv = nav_t1 * (1 + indexIncreaseRate) * (currentFx / closeFxT1)`
- `currentFx / closeFxT*` defaults to `1` only for RMB-denominated domestic index rows.
- Strategy must expose at least:
  - `iopv`
  - `premiumRate`
  - `calcStatus`
  - `calcMode`
  - `timeNote`
  - `limitedMonitorEligible`
  - `unlimitedMonitorEligible`

### 39.8 Pool rule
- `limitedMonitorEligible` requires:
  - limited apply status detected
  - limited amount < `100000`
  - `premiumRate > 0.01`
  - `turnoverWan > 100`
- `unlimitedMonitorEligible` requires:
  - no limited apply status
  - `premiumRate > 0.05` or `premiumRate < -0.05`
  - `turnoverWan > 100`
- Pool membership is derived each refresh and not manually edited.

### 39.9 Public API rule
- Add route:
  - `GET /api/market/lof-arbitrage`
- Response data shape includes at least:
  - `groups`
  - `defaultGroup`
  - `rows`
  - `limitedMonitorRows`
  - `unlimitedMonitorRows`
  - `sourceSummary`
  - `rebuildStatus`
- Add routes:
  - `GET /api/push/lof-arbitrage-config`
  - `POST /api/push/lof-arbitrage-config`

### 39.10 Runtime / dataset rule
- `data_dispatch.py` adds action:
  - `lof-arbitrage`
- `start_server.js` adds dataset key:
  - `lofArb`
- The dataset keeps its own runtime store for:
  - source rows
  - limited pool rows
  - unlimited pool rows
  - last rebuild metadata
  - source summary

## 40. LOF Premium Formula And Dense Table Spec (2026-03-25)

### 40.1 Strategy formula revision
- `strategy/lof_arbitrage/service.py` must revise the outward premium calculation to:
  - `premiumRate = (price / iopv - 1) * 100`
- The helper still returns `None` when:
  - `iopv` is missing
  - `price` is missing
  - `iopv <= 0`
- The strategy must continue to calculate `iopv` first and only then derive `premiumRate`.
- `limitedMonitorEligible` and `unlimitedMonitorEligible` keep evaluating the outward `premiumRate` field after the formula change.

### 40.2 Dashboard table revision
- `presentation/dashboard/dashboard_page.js` must stop attaching an LOF detail-row renderer to `renderPaginatedTable()`.
- The LOF main table remains the only primary row-reading surface.
- The LOF main table may merge paired fields into compact multi-line cells, but must still visibly expose:
  - `code`
  - `name`
  - `price`
  - `changeRate`
  - `turnoverWan`
  - `shareAmountWan`
  - `shareAmountIncreaseWan`
  - `nav`
  - `navDate`
  - `indexIncreaseRate`
  - `indexName`
  - `applyFee`
  - `applyStatus`
  - `redeemFee`
  - `redeemStatus`
  - `custodianFee`
  - `iopv`
  - `premiumRate`
- The compact table still uses shared:
  - search
  - sorting
  - pagination
  - horizontal overflow container

### 40.3 Presentation-density rule
- The LOF table may use a smaller module-specific minimum width than the generic premium tables if needed for page fit.
- Module-specific compact styling must stay local to the LOF table kind and must not globally shrink unrelated tables.

## 41. LOF NAV-date Priority And Post-close Fix Spec (2026-03-25)

### 41.1 Strategy truth correction
- `strategy/lof_arbitrage/service.py` must treat the currently deployed LOF premium meaning as:
  - `premiumRate = (iopv / price - 1) * 100`
- The previous `price / iopv - 1` document text is superseded in this round and must not drive any active code path.

### 41.2 Same-day NAV shortcut
- The strategy layer must add a same-day NAV branch before the old T-1 / T-2 extrapolation branches:
  - input condition:
    - `navDate == priceDate`
    - `nav > 0`
    - source `nav_discount_rt` is present
  - output rule:
    - outward `iopv` uses the same-day `nav`
    - outward `premiumRate` is derived from the source `nav_discount_rt` with the sign converted into the module’s outward premium meaning
    - outward `calcMode` identifies same-day NAV direct-read mode
    - outward `calcStatus` explains that same-day NAV already exists and no longer needs extrapolation
- This same-day NAV branch applies to:
  - `index`
  - `asia`
  - `europe_us`

### 41.3 Europe/US NAV-date aligned extrapolation
- When `marketGroup == europe_us` and the row still needs extrapolation:
  - the strategy must determine which stored index / FX anchor matches `navDate`
  - preferred order:
    - anchor whose date exactly equals `navDate`
    - otherwise keep the existing truthful fallback order
- The implementation may use:
  - `baseIndexDate / baseIndexValue`
  - `midIndexDate / midIndexValue`
  - `baseFxDate / baseFxValue`
  - `midFxDate / midFxValue`
  - any other already-fetched real field already present in the normalized row
- The implementation must not invent a missing `T-1` or `T-2` anchor.

### 41.4 Pool exclusion rule
- Add helper-level pool exclusion for paused subscription rows:
  - if `applyStatus` expresses `暂停申购`
  - then `limitedMonitorEligible = false`
  - and `unlimitedMonitorEligible = false`
- The row still remains in:
  - `rows`
  - active market subtab table rendering
- Because the row cannot enter either pool, the existing LOF push service will naturally stop treating it as a new pool-entry candidate.

### 41.5 Data contract additions
- The normalized LOF row should expose enough truthful source context for the new strategy branch, including at least:
  - `priceDate`
  - source `nav_discount_rt` normalized for strategy use
- These fields may stay internal helper fields and do not need to become required visible columns.

## 42A. LOF Europe/US External Market API Enrichment Spec (2026-03-25)

### 42.1 Scope
- This round changes only the LOF fetch/helper path for `QDII欧美`.
- This round does not change:
  - LOF source list URLs
  - LOF dashboard layout
  - LOF push schedule
  - AH / AB / convertible logic

### 42.2 Config contract
- `config.yaml > data_fetch.plugins.lof_arbitrage.external_market_api` adds:
  - `enabled`
  - `provider`
  - `request_timeout_ms`
  - `current_quote_url`
  - `history_quote_url`
  - `index_symbol_map.cal_index_id`
  - `index_symbol_map.index_name`
  - `fx_symbol_map`
- Phase-1 provider is `stooq`.

### 42.3 Fetch-helper responsibility
- `data_fetch/lof_arbitrage/source.py` remains the only place that may talk to the external helper API in this round.
- The helper layer may enrich only helper inputs, not strategy outputs:
  - `currentIndexValue`
  - `baseIndexValue`
  - `currentFxRate`
  - `baseFxValue`
  - matching `*Date / *Source / *Symbol` diagnosis fields when useful

### 42.4 Mapping rule
- Exact external symbol resolution priority is:
  1. `calIndexId`
  2. `indexName`
  3. existing live token field only when an explicit config mapping exists
- FX symbol resolution is currency-based.
- If no exact configured mapping exists, the row must skip the external exact path instead of guessing.

### 42.5 Provider rule
- For `stooq` current quote:
  - use `current_quote_url` with one symbol per request
  - parse the returned latest price
- For `stooq` nav-date-aligned history:
  - use `history_quote_url`
  - request `d1 = d2 = navDate`
  - use the returned `Close` as the aligned base value
- The helper must tolerate provider miss / timeout per row and degrade without taking down the whole LOF dataset.

### 42.6 Enrichment rule
- External enrichment is attempted only for `marketGroup == europe_us`.
- External index enrichment is triggered when either is missing:
  - `currentIndexValue`
  - `baseIndexValue`
- External FX enrichment is triggered when either is missing:
  - `currentFxRate`
  - `baseFxValue`
- When a missing field is filled from the provider:
  - keep the original field names used by the strategy
  - set aligned `baseIndexDate / baseFxDate` to the real provider date when the source field was empty
- Existing source/Tencent values remain preferred when already present; the external path fills only the gaps.

### 42.7 Truthful fallback rule
- Rows with an exact external symbol may enter the full `T-2 / navDate-aligned` IOPV path after enrichment.
- Rows without an exact external symbol keep the pre-existing truthful fallback order:
  - source same-day NAV direct-read when available
  - source estimate path when available
  - otherwise `missing_inputs`
- Proxy ETF / guessed symbol is not allowed to silently masquerade as an exact index series in this round.

### 42.8 Diagnosis rule
- `sourceSummary` may expose external-helper usage counts for diagnosis.
- The outward dataset `source` string must reflect the added provider when the external helper is enabled, for example `jisilu+tencent+stooq`.

## 42. LOF NAV-date Formula Split And Europe External-anchor Spec (2026-03-25)

### 42.1 Outward premium rule
- `strategy/lof_arbitrage/service.py` keeps:
  - `premiumRate = (iopv / price - 1) * 100`

### 42.2 Index / Asia branch rule
- For `marketGroup in {"index", "asia"}`:
  - if `navDate == priceDate`:
    - outward `iopv = nav`
    - no extra index / FX extrapolation is applied
    - outward `calcMode` must identify same-day direct NAV mode
  - otherwise:
    - outward `iopv = nav * (1 + indexIncreaseRate / 100) * fx_ratio`
- `indexIncreaseRate` in this branch continues to use the normalized Jisilu source field directly.

### 42.3 Europe branch rule
- For `marketGroup == "europe_us"`:
  - the strategy must estimate from the latest published NAV date rather than a hardcoded relative day label
  - if `navDate` maps to the stored `base*Date/base*Value` anchor:
    - use that anchor
  - if `navDate` maps to the stored `mid*Date/mid*Value` anchor:
    - use that anchor
  - current index / current FX values must come from live external quote fetching when available
  - if the current external quote is unavailable, the strategy may degrade to the existing truthful source-estimate branch
- The Europe branch must therefore support both:
  - `T-2 NAV + today / T-2 anchor`
  - `T-1 NAV + today / T-1 anchor`

### 42.4 Source hydration rule
- `data_fetch/lof_arbitrage/source.py` must keep exposing the helper fields required by the split formula, including at least:
  - `priceDate`
  - `navDate`
  - `baseIndexDate`
  - `baseIndexValue`
  - `midIndexDate`
  - `midIndexValue`
  - `baseFxDate`
  - `baseFxValue`
  - `midFxDate`
  - `midFxValue`
  - `currentIndexValue`
  - `currentFxRate`
- The source layer may additionally expose truthful fallback live values already present in Jisilu helper text, but must still prefer external live quotes first.

### 42.5 Monitor exclusion rule
- Pool eligibility stays false when:
  - `applyStatus` contains `暂停申购`
- This rule applies before:
  - limited-pool threshold checks
  - unlimited-pool threshold checks

## 43. LOF Commodity-source Merge Spec (2026-03-25)

### 43.1 Internal source contract
- `data_fetch/lof_arbitrage/source.py` must extend the current Jisilu source map with one additional internal fetch-only source:
  - `commodity`
- Its truthful source endpoints are:
  - page `https://www.jisilu.cn/data/qdii/#qdiic`
  - api `https://www.jisilu.cn/data/qdii/qdii_list/C`

### 43.2 Outward grouping rule
- `commodity` is not a new outward LOF market group.
- Normalized rows fetched from `commodity` must be emitted with:
  - outward `marketGroup = "europe_us"`
  - outward `groupLabel = "QDII欧美"`
- The row must still preserve its own source trace fields:
  - `sourcePageUrl`
  - `sourceApiUrl`

### 43.3 Summary aggregation rule
- The fetch layer's `sourceSummary.groups.europe_us` must aggregate:
  - Europe/US source counts
  - plus commodity-source counts
- The aggregation must apply to at least:
  - `visibleCount`
  - `allCount`
  - `guestLimited`
  - `warn`
- Existing outward groups remain exactly:
  - `index`
  - `europe_us`
  - `asia`

### 43.4 Regression boundary
- `presentation/dashboard/dashboard_page.js` does not need a new LOF subtab for this round.
- Existing `strategy/lof_arbitrage/service.py` logic continues to consume the normalized outward rows without any non-LOF side effects.

### 39.11 Push rule
- Add independent notification module:
  - `notification/lof_arbitrage/service.js`
  - `notification/styles/lof_arbitrage_markdown.js`
- Push config uses the same module-push-config/runtime infrastructure as `cb_rights_issue`.
- Default schedule is:
  - `13:30`
  - `14:00`
  - `14:30`
- Instant push is triggered when a row newly enters either pool compared with the stored seen-map.
- Scheduled push sends the full current two-pool list.

### 39.12 Dashboard rule
- `dashboard_template.html` adds one new root tab:
  - `data-tab="lof-arb"`
  - one new panel `panel-lof-arb`
- `dashboard_page.js` adds:
  - `lofArb` endpoint and resource state
  - root-tab loading and rendering
  - one internal LOF view switcher:
    - `index`
    - `europe_us`
    - `asia`
- The top page area renders only:
  - limited-monitor card
  - unlimited-monitor card
- The main table uses the shared paginated table renderer with `tableKind="lof"`.
- The main table keeps 50-row pagination and shared search behavior.
- The page footnote uses the shared module-note renderer with module key `lofArb`.

### 39.13 Config contract
- `config.yaml` adds:
  - plugin registration entries for `lof_arbitrage`
  - source page URLs
  - direct JSON fallback URLs
  - Firecrawl config
  - refresh interval
  - default group
  - thresholds for both pools
  - default push times
  - dashboard module notes for `lofArb`

### 39.14 Truth / failure rule
- Missing Firecrawl credentials is not an error if direct fallback succeeds.
- Missing direct source or missing essential source fields returns a truthful module error.
- Missing enough real inputs for one row:
  - the row stays visible when possible
  - `iopv` / `premiumRate` stay empty
  - `calcStatus` explains the real reason
- No fake placeholder result is allowed for missing IOPV rows.
