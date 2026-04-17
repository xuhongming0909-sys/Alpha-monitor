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
  - `250日波动率`
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
  - `volatility250`
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
- `250日波动率` is currently rendered from the annualized standard deviation of the latest `250` stock close-to-close log returns:
  - source close series = cached adjusted stock closes
  - current display semantics = historical estimate / reference
- `鏈熸潈鐞嗚浠峰€糮 is rendered as:
  - prefer `callOptionValue`
  - compatibility fallback to `callOptionValue - putOptionValue` only when legacy rows still carry the old pricing formula
  - fallback to `theoreticalPrice - 绾€哄熀鍑哷
- `鐞嗚浠峰€糮 is rendered from `theoreticalPrice`.
- `鐞嗚婧环鐜嘸 is rendered from `theoreticalPremiumRate`.
- The page must include a visible formula hint near the `杞€哄鍒ー main table, stating at least:
  - `鐞嗚浠峰€?= 绾€轰环鍊?+ 鏈熸潈鐞嗚浠峰€糮
  - `鏈熸潈鐞嗚浠峰€?= 鐪嬫定鏈熸潈(杞偂浠? - 鐪嬫定鏈熸潈(寮鸿祹浠?
- The page must also visibly mark the following fields as reference-only in this round:
  - `250日波动率`
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

## 25. Event-arbitrage Detail Text Responsive Spec (2026-03-24)

### 25.1 Scope
- This round changes only the event-arbitrage detail-text presentation.
- No event-arbitrage API field names or payload semantics change.

### 25.2 Rendering rule
- `A鑲″鍒ー detail `鎽樿` uses a dedicated single-column detail-grid variant.
- `娓偂濂楀埄` and `涓绉佹湁` detail `澶囨敞` use the same dedicated single-column variant.
- The single-column variant must span the available detail-row width on desktop instead of inheriting the default 4-column detail-grid compression.
- On narrow screens the same block continues wrapping naturally without horizontal overflow.
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
- `buildConvertibleColumns()` keeps `volatility250 ?? volatility60 ?? annualizedVolatility` as the visible read path for `250日波动率`.
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
- `volatility250` uses the latest `250` close-to-close log returns from real `后复权` daily history.
- Therefore the read path must load at least `251` closes for the active current window.

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
- `volatility250` and `annualizedVolatility` remain ratio-form numeric fields in the payload.
- Example: `0.3491101749` represents `34.91101749%`.

### 35.2 Front-end display rule
- The dashboard front end must multiply the ratio by `100` when rendering human-readable volatility percentages.
- The display helper used for this rule must not change the underlying numeric sort value.

### 35.3 Coverage rule
- This rule applies to:
  - the convertible-bond `250日波动率` table column
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
- independent state file: 
untime_data/shared/cb_discount_strategy_state.json
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

## 65. Convertible Discount Push Session Spec (2026-03-27)

### 65.1 Session gate
- `tradingDaysOnly = true` means the module only runs on Shanghai weekday `1..5`.
- `sessionWindows` defaults to:
  - `09:30-11:30`
  - `13:00-15:00`
- A discount push is eligible only when current Shanghai time falls inside one of the
  configured session windows.
- `15:00+` is outside the discount-push session and must suppress both timed-monitor and
  instant buy/sell sends.

### 65.2 Push-lane separation
- Timed monitor-list push:
  - keeps using `monitorSessionTimes`
  - due slots are filtered by the active session windows
  - each slot may send at most once per date
- Instant push:
  - buy signal is emitted only on buy-zone crossing during an active session window
  - sell signal is emitted only on sell-zone crossing during an active session window
- A shared scheduler tick may call both checks in one pass, but the implementation must
  preserve separate runtime timestamps and separate markdown titles for:
  - buy
  - sell
  - monitor

### 65.3 Config contract
- `strategy.convertible_bond.discount_strategy` additionally preserves:
  - `trading_days_only`
  - `session_windows`
  - `monitor_session_times`
- Invalid or empty `session_windows` must fall back to the default A-share windows above.

### 65.4 Dashboard status contract
- `GET /api/push/config` discount-strategy status must additionally expose:
  - `tradingDaysOnly`
  - `sessionWindows`
  - `monitorSessionTimes`
- Dashboard wording must distinguish:
  - “监控时点” for the timed monitor list
  - “即时时段” for buy/sell zone-crossing evaluation
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
  - `250日波动率` requires at least `251` closes from this dedicated DB
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
  - `volatility250`
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

## 36. Convertible Strike-price Simplification + Call-spread Pricing Spec (2026-03-25, amended 2026-03-30)

### 36.1 Scope
- This round changes the strike-price rule and the option-leg formula inside convertible theoretical pricing.
- This round does not change:
  - route shape
  - pure-bond source truth rule

### 36.2 Call-strike rule
- In `_build_theoretical_metrics(...)`, when `convertPrice > 0`:
  - `optionQty = 100 / convertPrice`
  - `callStrike = convertPrice`
- The old derived-strike rule is removed:
  - `max(bondValue / optionQty, convertPrice)` is no longer allowed
- This section is superseded by section 95 on 2026-03-30 and is no longer the live rule.

### 36.3 Call-spread pricing rule
- The old pricing branch is retired:
  - `bond + call`
  - `bond + call - put`
- In `_build_theoretical_metrics(...)`, the live option leg must use:
  - `longCallStrike = convertPrice`
  - `shortCallStrike = redeemTriggerPrice`
  - `longCallValue = americanCall(stockPrice, convertPrice, remainingYears, riskFreeRate, vol) * optionQty`
  - `shortCallValue = americanCall(stockPrice, redeemTriggerPrice, remainingYears, riskFreeRate, vol) * optionQty`
  - `callSpreadValue = max(longCallValue - shortCallValue, 0)`
  - `theoreticalPrice = bondValue + callSpreadValue`
- Missing any core real input, especially missing `redeemTriggerPrice`, must lead to truthful null `theoreticalPrice / theoreticalPremiumRate`.

### 36.4 Outward payload rule
- `callStrike20 / callStrike60 / callStrike120` must equal the same row's `convertPrice` when `convertPrice` is valid.
- `callOptionValue*` now means the net call-spread value.
- `putOptionValue*` remains compatibility-only and must be `null`.

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
  - `250日波动率` requiring `251` closes
  - `ATR20` requiring `21` rich bars
  - `20日/5日平均成交额`

### 36.5 Rights-issue underlying-history retention rule
- `data_fetch/cb_rights_issue/history_source.py` remains the official incremental sync path for `cb_rights_issue_stock_history.db`.
- After the sync batch finishes, the same path must call a rolling per-symbol prune.
- Rolling prune rule:
  - keep only the most recent configured row count for each symbol
  - delete older rows beyond that limit
  - delete orphaned sync-state rows when a symbol no longer has price rows
- The configured kept row count must stay safely above the live calculation floor for `250日波动率` requiring `251` closes.

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

## 46. Midnight Push Time Normalization Spec (2026-03-26)

### 46.1 Scope
- This round changes only timed-push Shanghai-time parsing and dedup alignment.
- This round does not change:
  - push content
  - push schedules
  - push module selection
  - non-push business modules

### 46.2 Shared Shanghai-time rule
- `shared/time/shanghai_time.js` remains the single authoritative Shanghai-time helper.
- If locale formatting returns midnight hour as `24`, the helper must normalize:
  - `24 -> 0`
- The outward `getShanghaiParts(date)` contract therefore guarantees:
  - `hour` is always in `0..23`

### 46.3 Runtime dedup rule
- `notification/scheduler/push_runtime_store.js` must not keep an independent,
  differently-behaving Shanghai-hour parser.
- Runtime-state Shanghai-date/hour extraction for ISO timestamps must reuse the
  same normalized Shanghai-time helper as the scheduler path.

### 46.4 Scheduler rule
- In `notification/scheduler/wecom_scheduler.js`:
  - `nowMinutes = sh.hour * 60 + sh.minute`
  - with the invariant that `sh.hour` can never be `24`
- Therefore during Shanghai `00:00-00:59`:
  - `nowMinutes` must stay in `0..59`
  - slots like `08:00` and `14:30` must remain `not_due_yet`

### 46.5 Affected push paths
- The fix must protect all timed push flows that rely on Shanghai clock comparison:
  - main summary push
  - cb-rights-issue timed push
  - LOF timed push

### 46.6 Verification samples
- The implementation must satisfy:
  - `2026-03-25T16:04:52.773Z -> { date: "2026-03-26", hour: 0, minute: 4 }`
  - `2026-03-25T16:59:24.168Z -> { date: "2026-03-26", hour: 0, minute: 59 }`
  - `2026-03-25T17:00:24.168Z -> { date: "2026-03-26", hour: 1, minute: 0 }`

### 46.7 Regression boundary
- Existing push runtime state shape remains compatible.
- Existing push-config API routes remain unchanged.
- Existing scheduler tick frequency remains `60s`.

## 47. Refresh Reliability And Status Truthfulness Spec (2026-03-26)

### 47.1 Scope
- This round changes only:
  - dataset refresh orchestration
  - dashboard resource-status truthfulness
  - cbArb intraday refresh critical path
  - daily-sync completion semantics
  - Shanghai midnight normalization reuse
- This round does not change:
  - market formulas
  - table schema
  - push message content

### 47.2 cbArb refresh-path rule
- `start_server.js > DATASETS.cbArb.fetch` must not require heavy stock-history maintenance during ordinary intraday reads.
- Ordinary `cbArb` refresh path is fixed to:
  - fetch latest convertible-bond dataset
  - reuse already-maintained history database for valuation inputs
  - persist last-good dataset cache on success
- Heavy maintenance path remains available only for:
  - explicit sync task
  - daily sync
- Therefore:
  - `GET /api/market/convertible-bond-arbitrage`
  - `GET /api/market/convertible-bond-arbitrage?force=1`
  must not implicitly run `sync-cb-stock-history` first.

### 47.3 Dataset cache-status rule
- `withCachedDatasetMeta()` may continue to mark a returned payload as cache-backed.
- But `GET /api/dashboard/resource-status` must no longer derive `servedFromCache` from “cache file exists”.
- `readCachedDatasetStatus(resourceKey)` must expose freshness truth using at least:
  - `updateTime`
  - `cacheTime`
  - `refreshing`
  - `servedFromCache`
- `servedFromCache` in resource-status must mean:
  - the current outward dataset is a fallback stale snapshot because refresh failed or no fresh in-memory success exists
- `servedFromCache = false` must remain valid when:
  - the latest successful dataset was built normally
  - and then persisted into the cache file as the standard storage mechanism

### 47.4 Dashboard header-copy rule
- `presentation/dashboard/dashboard_page.js` must treat the new resource-status semantics as the single source of truth for freshness text.
- For critical market modules, header copy must follow:
  - `refreshing = true` -> background revalidation text
  - `servedFromCache = true` -> stale fallback text
  - otherwise -> real-time connected text
- Fresh same-day datasets must no longer render stale-cache copy only because they were read from persisted cache.

### 47.5 Daily-sync success rule
- In `start_server.js > runDailySync()`:
  - `lastDailySyncDate` may be written only after all required daily-sync dataset refreshes succeeded
- `Promise.allSettled()` results must be inspected explicitly.
- If one or more required daily-sync datasets fail:
  - `lastDailySyncDate` must remain unchanged
  - failure details should remain visible in logs
- `lastPremiumHistorySyncDate` keeps its own success gate and must not be conflated with dataset daily-sync success.

### 47.6 Shanghai midnight reuse rule
- Cloud runtime must reuse the normalized midnight rule from `shared/time/shanghai_time.js`.
- The shared helper contract is:
  - outward `hour` is always `0..23`
  - `24:xx` locale output is normalized to `00:xx`
- Timed push paths must keep reading the shared helper so scheduler decisions and runtime dedup use the same hour semantics.

### 47.7 Verification rule
- Runtime verification for this round must cover:
  - `exchange-rate / ipo / bonds / ah / ab / lof-arbitrage / cb-rights-issue / event-arbitrage` force refresh success
  - `convertible-bond-arbitrage?force=1` same-day success
  - `resource-status` freshness semantics after a successful refresh
  - midnight time normalization samples around `00:xx`

### 47.8 Module-local push runtime self-healing
- `notification/scheduler/module_push_runtime_store.js` must reuse the same-day
  slot-sanitizing rule that `notification/scheduler/push_runtime_store.js` already
  applies to the main summary scheduler.
- The module-local runtime store must expose and internally use:
  - latest module success ISO
  - Shanghai same-day parts parsed from ISO timestamps
  - current-day scheduled-slot sanitation before scheduler decisions
- Sanitizing rule for the current Shanghai date:
  - keep only slots that still exist in the configured schedule
  - if there is no same-day module success, clear all persisted current-day slots
  - if there is a same-day module success, keep only slots whose configured minute
    is not later than the latest same-day success minute
- This hardened module-runtime contract must be consumed by:
  - `notification/cb_rights_issue/service.js`
  - `notification/lof_arbitrage/service.js`
- `notification/lof_arbitrage/service.js` must emit diagnosis logs for:
  - sanitized dirty records
  - `not_due_yet`
  - `already_sent`
  - send success / failure

## 48. Dashboard Dual-theme Presentation Spec (2026-03-27)

### 48.1 Scope
- This round changes only the dashboard presentation theme layer.
- This round does not change:
  - business data contracts
  - API paths
  - dataset refresh logic
  - push behavior
  - scheduler behavior
  - table schema
  - module/tab structure

### 48.2 Config contract
- `config.yaml` adds:
  - `presentation.dashboard_theme`
- Supported values are:
  - `classic`
  - `clean_data`
- Invalid or missing values must fall back to:
  - `classic`

### 48.3 UI-config contract
- `GET /api/dashboard/ui-config` keeps returning:
  - `tableUi`
  - `autoRefresh`
  - `moduleNotes`
- It may additionally return:
  - `dashboardTheme`
- Existing callers that ignore the new field must continue to work.

### 48.4 Server normalization rule
- `start_server.js` must normalize the configured dashboard theme once during startup.
- The normalized theme value must be the single source of truth exposed to the
  dashboard UI-config route.
- Theme normalization must not read runtime user state files; it is a static
  presentation config.

### 48.5 Frontend apply rule
- `presentation/dashboard/dashboard_page.js` must:
  - normalize the incoming theme value
  - apply it to the root document via one stable attribute
- Recommended outward contract:
  - `document.documentElement.dataset.dashboardTheme = <theme>`
- Missing / invalid payload must fall back to:
  - `classic`

### 48.6 CSS implementation rule
- `presentation/templates/dashboard_template.html` must keep the existing visual
  rules as the `classic` baseline.
- `clean_data` must be implemented as CSS-variable overrides plus a small number of
  selector-level visual overrides only.
- This round must not introduce:
  - a duplicate template
  - a second HTML entry page
  - duplicated module markup for theming

### 48.7 Visual behavior contract
- `clean_data` should shift the dashboard toward a simpler data-terminal look:
  - lighter neutral page background
  - flatter white/light panels
  - calmer steel/blue accent colors
  - clearer table separators and reduced glow
- The following must remain unchanged across themes:
  - root tabs and subtab order
  - module titles
  - table columns and values
  - sorting/search/pagination behavior
  - push-setting form semantics
  - auto-refresh behavior

### 48.8 Rollback rule
- Switching `presentation.dashboard_theme` from `clean_data` back to `classic`
  must be sufficient to restore the prior appearance.
- No code rollback is required for a visual rollback in this round.

## 49. Dashboard Footer-note And Compact-label Spec (2026-03-28)

### 49.1 Scope
- This round changes only dashboard presentation copy/layout density.
- This round does not change:
  - API paths
  - payload semantics
  - table schema
  - dataset refresh logic
  - push behavior
  - scheduler behavior

### 49.2 Shared footer-note rule
- `presentation/templates/dashboard_template.html` must provide one shared page-bottom
  note container outside the tab panels.
- `presentation/dashboard/dashboard_page.js` must render only the active tab's note
  into that shared footer container.
- Module panels must stop rendering inline `renderModuleFootnote(...)` cards.

### 49.3 Note content rule
- The footer-note content still reuses the existing module-note payload:
  - `dataSources`
  - `formulas`
  - `strategyNotes`
- The note card title may be shortened, but the three section meanings remain unchanged.

### 49.4 Root-tab compact rule
- Desktop root tabs must keep the same tab order and count.
- Visual compaction should use:
  - shorter labels
  - smaller height
  - smaller padding
  - smaller font size
- On desktop-width layouts, the preferred rendering remains a single row.
- Mobile responsive fallback may still wrap into multiple rows.

### 49.5 Visible label-shortening rule
- Dashboard visible labels may be shortened toward data-page wording, for example:
  - `转债套利 -> 转债`
  - `AH溢价 -> AH`
  - `AB溢价 -> AB`
  - `LOF套利 -> LOF`
  - `监控套利 -> 监控`
  - `分红提醒 -> 分红`
  - `事件套利 -> 事件`
  - `可转债抢权配售 -> 抢权`
- List-area labels may also be shortened, for example:
  - `主表 -> 列表`
  - `监控列表 -> 入池列表`
  - `固定来源结构化信息 -> 来源列表`
  - `今日登记日提醒 -> 今日登记`
  - `分红观察名单 -> 观察列表`
  - `前三 / 倒数前三 -> 前3 / 后3`
- These changes are display-copy-only and must not alter business meaning.

### 49.6 Dense summary rule
- Summary-card grids should prefer tighter multi-column layouts on desktop.
- CSS may switch from fixed `2/3` columns to auto-fit compact columns when doing so
  reduces vertical waste without hiding data.
- Summary cards should use reduced spacing and shorter titles, but still keep the same
  underlying summary data.

### 49.7 Regression boundary
- Search, sorting, pagination, subtab order, and push-setting interaction remain unchanged.
- The active module's data note remains available, only its placement changes to the page footer.

## 50. Table-header Compaction And Width-tightening Spec (2026-03-28)

### 50.1 Scope
- This round changes only dashboard table copy and width density.
- This round does not change:
  - root module names
  - module/tab order
  - API paths
  - payload semantics
  - sorting/searching/pagination behavior

### 50.2 Root-name preservation rule
- Root tab labels and module titles must keep the original business names:
  - `转债套利`
  - `AH溢价`
  - `AB溢价`
  - `LOF套利`
  - `监控套利`
  - `分红提醒`
  - `事件套利`
  - `可转债抢权配售`
- Any density optimization in this round must happen below the module title layer.

### 50.3 Column-label compaction rule
- `presentation/dashboard/dashboard_page.js` may shorten visible column labels so long
  as each label still clearly maps to the same field semantics.
- Typical compaction patterns include:
  - `代码 / 名称 / 现价 / 涨幅`
  - `正股码 / 正股 / 转股值 / 转股溢`
  - `分位 / 区间 / 收益率 / 公告`
- The implementation must not hide fields merely to simulate density.

### 50.4 Width-tightening rule
- `presentation/templates/dashboard_template.html` may reduce shared width constraints for:
  - code columns
  - numeric columns
  - percent columns
  - date columns
  - sticky columns in dense tables
- Dense table kinds such as `convertible / premium / merger / lof` may also reduce
  their minimum widths when doing so does not remove fields.

### 50.5 Regression boundary
- No table field is removed in this round.
- No field is moved into a hidden detail-only path in this round.
- Existing row data, sort keys, and search keys remain unchanged.

## 50. Convertible Premium-only Truthfulness Spec (2026-03-28)

### 50.1 Scope
- This round changes only the convertible-bond live source truthfulness, outward
  premium semantics, dashboard convertible presentation, and related push wording.
- This round does not change:
  - AH / AB / LOF / cb-rights-issue / merger formulas
  - non-convertible tables
  - non-convertible push schedules

### 50.2 Live field truth rule
- In `data_fetch/convertible_bond/source.py`, the following fields are live
  price-derived fields:
  - `stockPrice`
  - `convertPrice`
  - `convertValue`
  - `premiumRate`
- These fields must not fall back to `previous_row` cached values during ordinary
  realtime assembly.
- `convertValue` must not trust unreliable upstream bulk fields such as stale
  `TRANSFER_VALUE` when both `stockPrice` and `convertPrice` are available.

### 50.3 Convertible value formula rule
- Source-layer final formula is fixed to:
  - `convertValue = stockPrice * 100 / convertPrice`
- Recompute rule:
  - whenever `stockPrice > 0` and `convertPrice > 0`, the final outward
    `convertValue` must be recomputed from that formula
  - this recomputed value overrides any conflicting upstream realtime/bulk value

### 50.4 Premium formula rule
- Source-layer final premium formula is fixed to:
  - `premiumRate = (price / convertValue - 1) * 100`
- Recompute rule:
  - whenever `price > 0` and recomputed `convertValue > 0`, final outward
    `premiumRate` must be recomputed from the formula above

### 50.5 Slow-cache boundary rule
- The following may still reuse last-good or history-backed cache paths:
  - volatility fields
  - ATR-derived fields
  - turnover-average fields
  - pure-bond-value snapshots
  - static metadata supplements
- These slow-cache paths must not overwrite the final live values of:
  - `stockPrice`
  - `convertPrice`
  - `convertValue`
  - `premiumRate`

### 50.6 Premium-monitor strategy rule
- In `strategy/convertible_bond/service.js`, the outward monitor lane becomes
  premium-only:
  - buy zone active when `premiumRate < -2`
  - sell zone active when `premiumRate > -0.5`
- Runtime state may keep the existing storage shape if needed, but outward wording
  must reflect `低溢价监控` instead of `折价监控`.
- Outward summary/push payload no longer needs to include:
  - `discountRate`
  - `weightedDiscountRate`

### 50.7 Convertible page rule
- In `presentation/dashboard/dashboard_page.js`:
  - remove visible columns `折价率` and `加权折价率`
  - keep `转股溢价率` as the single outward premium field
  - top summary card replaces `折价监控` with a premium-based monitor card
- Sticky-column contract becomes:
  - sticky `序号`
  - sticky `转债名称`
  - `转债代码` remains non-sticky

### 50.8 Public API shaping rule
- In `start_server.js`, `CB_ARB_PUBLIC_ROW_KEYS` and shaped payloads must stop
  exposing obsolete outward fields that the page no longer uses:
  - `discountRate`
  - `weightedDiscountRate`
- The converted summary object returned with `cbArb` should use premium wording and
  remain stable for the dashboard consumer.

### 50.9 Verification rule
- Concrete verification sample:
  - code `118025`
  - if `stockPrice = 106.02`
  - and `convertPrice = 114.97`
  - then `convertValue` must be about `92.215`
- Post-deploy cloud verification must include:
  - `GET /api/market/convertible-bond-arbitrage?force=1`
  - dashboard convertible table sticky behavior
  - premium-based push status wording

### 50.10 Public force-refresh timeout rule
- `config.yaml > data_fetch.plugins.convertible_bond.force_request_soft_timeout_ms`
  defines the public-route soft timeout for `cbArb force` requests.
- When:
  - `key == cbArb`
  - `force == true`
  - a last-good cached payload exists
  - and the refresh task exceeds the configured soft-timeout window
- the public route may return:
  - the latest last-good cached payload
  - plus `servedFromCache = true`
  - plus `refreshing = true`
  - plus `forceAccepted = true`
  - plus `forceRefreshDeferred = true`
- The underlying refresh task must continue in background and update the cache on success.
- This rule exists only to avoid public-proxy `504` while preserving the same real
  refresh chain behind the scenes.

### 50.11 Frozen-column correction + weighted-discount restore rule
- `presentation/dashboard/dashboard_page.js`
  - convertible main-table columns must be reordered so the only frozen columns are:
    - `index`
    - `bondName`
  - `code` remains visible but must not be frozen and must not sit immediately after `bondName`
  - `weightedDiscountRate` returns as an auxiliary visible strategy field
  - `premiumRate` remains the primary outward truth field
- `presentation/templates/dashboard_template.html`
  - convertible sticky CSS must only reserve frozen offsets for:
    - `col-index-sticky`
    - `col-bond-sticky`
  - `col-code-sticky` must no longer be active in the live contract
- `strategy/convertible_bond/service.js`
  - internal `discountRate = -premiumRate`
  - `weightedDiscountRate = discountRate * atrCoefficient * sellPressureCoefficient * boardCoefficient`
  - `weightedDiscountRate` is restored to strategy-enriched rows and monitor-summary rows
  - raw `discountRate` may remain internal, but `premiumRate` stays the primary external pricing truth
- `start_server.js`
  - `CB_ARB_PUBLIC_ROW_KEYS` must include `weightedDiscountRate`
  - public `cbArb` payload keeps `premiumMonitorSummary`, and its items may include `weightedDiscountRate`
- Cloud verification must confirm:
  - only `序号 + 转债名称` remain frozen
  - `加权折价率` is visible again
  - returned `weightedDiscountRate` is consistent with `-premiumRate`

### 50.12 Convertible main-table compaction rule
- `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()` must shift
  from a “show every auxiliary field” pattern to a compact key-metrics pattern.
- The live visible convertible main table should prefer these compact cells:
  - `转债价`: bond price + bond change percent
  - `代码`: bond code only
  - `正股`: stock name + stock code
  - `正股价`: stock price + stock change percent
  - `正股成交`: `stockAvgTurnoverAmount20Yi` primary + `stockAvgTurnoverAmount5Yi` secondary
  - `转股价`
  - `转股值`
  - `转股溢`
  - `加权折`
  - `双低`
  - `纯债价` (optional but still allowed)
  - `理论溢`
  - `剩余期`
  - `规模`
- The following fields remain backend-visible but must leave the main table:
  - `listingDate`
  - `convertStartDate`
  - `maturityDate`
  - `optionTheoreticalValue`
  - `theoreticalPrice`
- `remainingYears` becomes the single visible term field and should render as a compact
  year-based value in the main table.
- `theoreticalPremiumRate` becomes the only visible theoretical-pricing field in the main table.
- The convertible search UI may stay active, but:
  - it should render as one compact input line
  - no standalone clear button
  - no extra helper-text line
- `renderPagination()` should stop emphasizing a separate `筛选后` phrase in the visible status text.

## 52. LOF Nav-date-aligned RMB Index-change Spec (2026-03-28)

### 52.1 Scope
- This round changes only the outward meaning of the LOF page field currently shown as
  `相关指数涨幅`.
- This round does not change:
  - the existing IOPV branch selection order
  - LOF source URLs
  - LOF monitor thresholds
  - LOF push schedule

### 52.2 Outward field rule
- In `strategy/lof_arbitrage/service.py`, each outward LOF row must add:
  - `navAlignedIndexChangeRate`
- The field is the single live page meaning of `相关指数涨幅`.

### 52.3 Formula rule
- When both `nav > 0` and `iopv > 0`:
  - `navAlignedIndexChangeRate = (iopv / nav - 1) * 100`
- This is the outward rate consistent with:
  - `iopv = nav * (1 + changeRate)`
- For `same_day_nav_direct` rows:
  - outward `navAlignedIndexChangeRate = 0`

### 52.4 Semantics rule
- `navAlignedIndexChangeRate` is always:
  - relative to the row `navDate`
  - RMB-priced after any required FX adjustment
  - based on the final outward `iopv`, not on a raw upstream source field
- Therefore:
  - `指数LOF / QDII亚洲` rows both expose the same outward semantics
  - the visible field reflects the combined result of index move and FX adjustment since `navDate`

### 52.5 Raw-source boundary
- Existing normalized `indexIncreaseRate` may remain in the backend row for diagnostics.
- `presentation/dashboard/dashboard_page.js` must stop using raw `indexIncreaseRate`
  as the visible `相关指数涨幅` field.
- If `navAlignedIndexChangeRate` is unavailable:
  - the page shows `--`
  - it must not silently fall back to raw `indexIncreaseRate`

### 52.6 Presentation rule
- In `presentation/dashboard/dashboard_page.js > buildLofArbColumns()`:
  - the `相关指数/涨幅` cell should sort and render by `navAlignedIndexChangeRate`
  - the visible label may remain `相关指数/涨幅` or become a clearer variant such as
    `相关指数/人民币涨幅`, but the semantics must follow this section

### 52.7 Verification rule
- For any row where `nav` and `iopv` are both present:
  - visible `相关指数涨幅` must match `(iopv / nav - 1) * 100`
- For same-day NAV rows:
  - visible `相关指数涨幅` must be `0%`
- Raw upstream `indexIncreaseRate` must no longer be the displayed value on the page.

## Effective Rollback Note (2026-03-28)

- The currently effective dashboard presentation spec is rolled back from the rejected
  visual experiment.
- Effective live spec:
  - classic dashboard presentation is the active style
  - module notes render inline with their modules, not in a shared page footer
  - list titles and table headers use the earlier baseline wording
  - shared table density, sticky-column layout, and width guidance use the pre-experiment baseline
- Any earlier dual-theme / footer-note / compact-header descriptions remain historical
  design records only and must not be treated as the live UI contract.

## 53. Convertible Frozen Identity + Dual-value Label Spec (2026-03-30)

### 53.1 Scope
- This round changes only the convertible dashboard table presentation.
- This round does not change:
  - source-layer pricing formulas
  - strategy fields
  - push behavior
  - public API payload shape

### 53.2 Frozen-column rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - remove the visible `index` column from the live convertible main table
  - remove the separate visible `code` column
  - keep one merged identity column keyed by `bondName`
  - render that cell as:
    - primary line: `bondName`
    - secondary line: `code`
- In `presentation/templates/dashboard_template.html`:
  - `table[data-table-kind="convertible"]` keeps only one active frozen-column style:
    - `col-bond-sticky`
  - legacy `col-index-sticky` frozen offsets must no longer be required for the live
    convertible contract

### 53.3 Pricing-cell dual-value rule
- The following visible columns must render as compact stacked cells instead of
  single-value percentage cells:
  - `转股溢价`
  - `加权折价`
  - `理论溢价`
- Amount formulas are presentation-only and fixed to:
  - `convertPremiumAmount = price - convertValue`
  - `weightedDiscountAmount = convertValue - price`
  - `theoreticalPremiumAmount = price - theoreticalPrice`
- Rate lines remain sourced from existing fields:
  - `premiumRate`
  - `weightedDiscountRate`
  - `theoreticalPremiumRate`
- The stacked display order is fixed to:
  - first line: amount
  - second line: rate label + formatted percentage

### 53.4 Visible copy rule
- The live convertible main-table labels must read:
  - `转债名称`
  - `转股溢价`
  - `加权折价`
  - `纯债价值`
  - `理论溢价`
  - `剩余规模`
  - `波动率`
  - `剩余期限`
- This round keeps the existing compact cells for:
  - `转债价`
  - `正股`
  - `正股价`
  - `正股成交`

### 53.5 Regression boundary
- The row sort keys remain attached to the same underlying fields:
  - `bondName`
  - `premiumRate`
  - `weightedDiscountRate`
  - `theoreticalPremiumRate`
  - `remainingSizeYi`
  - `volatility250`
  - `remainingYears`
- The table still uses the shared paginated table path and existing search behavior.
- No backend row field is deleted in this round.

## 52. Active 250D HFQ Volatility Implementation Contract (2026-03-30)

### 52.1 Scope
- The active volatility standard is switched to `250日年化后复权波动率` for:
  - convertible-bond theoretical pricing
  - cb-rights-issue option-value / expected-return pricing

### 52.2 Data source
- Both chains continue reading real underlying-stock daily `后复权` history from their existing dedicated/local history DB path.
- No front-end field, scraped static text, or non-history fallback may replace this truth source.

### 52.3 Calculation rule
- Read the latest `251` closes at minimum.
- Compute `250` close-to-close log returns.
- Compute annualized volatility from those returns.
- The row is volatility-ready only when the `251`-close minimum is satisfied.

### 52.4 Config rule
- `config.yaml > data_fetch.plugins.convertible_bond.primary_vol_window = 250`
- `config.yaml > data_fetch.plugins.convertible_bond.volatility_windows` must include `250` as the active pricing window.
- `config.yaml > strategy.cb_rights_issue.volatility_window = 250`
- Both history-retention parameters must remain above the `251`-close minimum with operational safety margin.

### 52.5 Compatibility rule
- During migration, payloads may still expose `volatility60` as a compatibility alias.
- If the alias exists, it must equal the active `250日年化后复权波动率`; it must not keep the old 60-day value.

### 52.6 Front-end rule
- User-facing labels and explanation copy for the affected modules must say `250日波动率`.
- Convertible-bond main-table sorting/rendering must prefer `volatility250`.
- cb-rights-issue table/detail rendering must prefer `volatility250`.

## 54. Convertible Premium-only Weighted-discount Spec (2026-03-30)

### 54.1 Scope
- This round changes only the convertible weighted-discount enrichment and the
  convertible main-table presentation.
- This round does not change:
  - convertible live `premiumRate` formula
  - non-convertible modules
  - push schedule timing

### 54.2 Base-value rule
- In `strategy/convertible_bond/service.js > enrichDiscountStrategyRow()`:
  - the weighted-discount base must use `-premiumRate` directly
  - the row object must stop exposing a standalone `discountRate` field for this round
- Signed base:
  - `premiumRateNegated = -premiumRate`

### 54.3 Coefficient-input rule
- Because anchor interpolation is defined on non-negative input space, the coefficient
  magnitude input is fixed to:
  - `premiumMagnitude = abs(-premiumRate)`
- Then:
  - `stockAtr20Pct = stockAtr20 / stockPrice * 100`
  - `atrRatio = premiumMagnitude / stockAtr20Pct`
  - `sellPressureRatio = remainingSizeYi / stockAvgTurnoverAmount20Yi`

### 54.4 Weighted-discount rule
- Final formula is fixed to:
  - `weightedDiscountRate = (-premiumRate) * atrCoefficient * sellPressureCoefficient * boardCoefficient`
- Therefore:
  - negative premium rows produce positive weighted-discount values
  - positive premium rows produce negative weighted-discount values
  - the field is no longer restricted to the old low-premium subset

### 54.5 Factor-column rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - insert these visible columns before `加权折价`:
    - `ATR系数/ATR%`
    - `抛压系数`
    - `市场`
- The recommended cell payload is:
  - `ATR系数/ATR%`
    - primary: `atrCoefficient`
    - secondary: `stockAtr20Pct`
  - `抛压系数`
    - primary: `sellPressureCoefficient`
    - secondary: `sellPressureRatio`
  - `市场`
    - primary: board label from stock-code prefix
    - secondary: `boardCoefficient`

### 54.6 Percentage-first cell rule
- `转股溢价 / 理论溢价 / 加权折价` must render percentage first and amount second.
- Presentation-only amount lines are fixed to:
  - `convertPremiumAmount = price - convertValue`
  - `weightedDiscountAmount = convertValue - price`
  - `theoreticalPremiumAmount = price - theoreticalPrice`
- Their main visible line must use:
  - `premiumRate`
  - `weightedDiscountRate`
  - `theoreticalPremiumRate`

### 54.7 Convertible-sort narrowing rule
- The live convertible main table must keep sort handles only for:
  - `premiumRate`
  - `weightedDiscountRate`
  - `theoreticalPremiumRate`
  - `doubleLow`
- Other convertible columns remain visible but must not render clickable sort buttons.

### 54.8 Convertible premium-rate sort restore rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - the `premiumRate` column must restore:
    - `sortable: true`
    - `sortType: 'number'`
    - `defaultDir: 'desc'`
    - `sortValue: (row) => toNumber(row.premiumRate)`
- The sort input must use the numeric source field, not the rendered dual-line cell text.
- This round does not change:
  - `premiumRate` formula
  - dual-line rendering of the cell
  - any API payload key

### 54.9 Convertible remaining-term year-unit rule
- In `presentation/dashboard/dashboard_page.js > formatRemainingTerm()`:
  - the input source remains `remainingYears`
  - the renderer must always output year units
  - month-based fallback display is retired for this module
- Recommended output:
  - `${formatNumber(remainingYears, 2)}年`

### 54.10 Convertible force-redeem highlight rule
- In `presentation/dashboard/dashboard_page.js`:
  - add a dedicated affirmative-status predicate for the convertible table
  - the row-class hook for `cbArb` must apply a yellow highlight class when:
    - `forceRedeemStatus` is non-empty
    - status text matches affirmative force-redeem semantics such as `强赎` or `强制赎回`
    - status text is not a negative semantic such as `不强赎 / 暂不强赎 / 不提前赎回`
    - status text is not already terminal such as `完成 / 摘牌 / 终止 / 退市`
- In `presentation/templates/dashboard_template.html`:
  - add the yellow row background style for the new convertible force-redeem class
  - include the sticky left bond-name cell so the fixed column stays visually consistent

### 54.11 Convertible force-redeem source rule
- The current live force-redeem status source remains unchanged in this round:
  - `data_fetch/convertible_bond/source.py > _build_cov_basic_map()`
  - Eastmoney datacenter report `RPT_BOND_CB_LIST`
  - source field `IS_REDEEM`
- The field is merged into public rows as:
  - `forceRedeemStatus`
- This round is presentation-only with respect to that field; no new upstream source is introduced.

### 54.12 LOF single-slot push rule
- In `config.yaml`:
  - `notification.lof_arbitrage.default_times` must be reduced to:
    - `14:00`
- In `start_server.js`:
  - `DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.times` must normalize to a single fixed slot
  - existing persisted LOF push config that still contains multiple times must be migrated to `['14:00']`
  - the LOF push config domain must accept only one time slot

### 54.13 LOF instant-push retirement rule
- In `notification/lof_arbitrage/service.js`:
  - remove the old new-entry instant-push path from the active service contract
  - the active outward service surface for this round is scheduled full-pool push only
- In `start_server.js > refreshDataset('lofArb')`:
  - refreshing the LOF dataset must no longer call an instant-push side path
- Existing stale state keys such as seen maps or instant timestamps may remain readable for compatibility,
  but they are no longer part of the active behavior contract.

### 54.14 LOF dashboard push-card rule
- In `presentation/dashboard/dashboard_page.js`:
  - `buildLofArbPushStateText()` must no longer surface instant success/error wording
  - `renderLofArbPushCard()` must describe one fixed `14:00` trading-day full push
  - the old three-input editable time form must be removed from the visible LOF push card
- In `presentation/templates/dashboard_template.html`:
  - refresh the dashboard bundle version so the cloud page does not stay on the cached old LOF push card

### 54.15 LOF push API contract rule
- `GET /api/push/lof-arbitrage-config` remains active, but its effective payload contract for this round is:
  - `enabled`
  - `times` with only one value: `14:00`
  - `tradingDaysOnly`
  - `deliveryStatus.lastSuccessAt`
  - `deliveryStatus.lastError`
  - `deliveryStatus.webhookConfigured`
  - `deliveryStatus.schedulerEnabled`
- `POST /api/push/lof-arbitrage-config` may remain for compatibility, but the saved effective schedule must still resolve to the single `14:00` slot.

### 54.16 Convertible force-redeem public-field rule
- In `start_server.js > CB_ARB_PUBLIC_ROW_KEYS`:
  - expose these additional real fields for convertible public rows:
    - `forceRedeemStatus`
    - `delistDate`
    - `ceaseDate`
- This round does not change the sanitize/remove rule:
  - completed or terminal force-redeem rows are still removed upstream by `strategy/convertible_bond/service.js`
- The page highlight rule remains presentation-only and must read the real exposed field rather than fabricate a state.

## 55. Cloud-only Web Entry + Local Residue Cleanup Spec (2026-03-30)

### 55.1 Scope
- This round changes only:
  - web-entry semantics
  - operator verification defaults
  - cleanup of local-only / duplicate web residues
- This round does not change:
  - live dashboard business rendering
  - public API paths
  - fetch/strategy/notification formulas

### 55.2 Live web-chain rule
- The only live operator-facing web chain is:
  - `start_server.js`
  - `presentation/templates/dashboard_template.html`
  - `presentation/dashboard/dashboard_page.js`
- `start_server.js` fallback behavior must not depend on a deleted root `index.html`;
  the dashboard template path remains the safe default entry.

### 55.3 Residue-removal rule
- The following files may be removed when they are unreferenced by the live chain:
  - root `index.html`
  - `remote_dashboard_template.html`
  - `remote_dashboard_page.js`
  - `tools/install_firewall_rule.ps1`
  - `tools/uninstall_firewall_rule.ps1`
- Removal is allowed only because they are no longer part of the effective cloud runtime contract.
- No deletion in this round may touch:
  - `presentation/templates/dashboard_template.html`
  - `presentation/dashboard/dashboard_page.js`
  - cloud deploy scripts under `tools/deploy/`

### 55.4 Cloud-first verification rule
- `smoke_check.js` must resolve its default target in this order:
  1. explicit env override
  2. configured public URL
  3. configured server base URL
  4. loopback fallback only when no cloud/public URL is available
- `tools/check_health.ps1` must follow the same cloud-first default target rule.
- Explicit user override by env var or command argument remains allowed.

### 55.5 Documentation rule
- `RUNBOOK.md` and `refactor_docs/001-monitor-refactor/quickstart.md` must consistently describe:
  - cloud server as the only formal runtime surface
  - cloud homepage/public health endpoint as the official verification path
  - local dev start as temporary debugging only

### 55.6 Regression boundary
- Root path `/` on the live server must still render the current dashboard.
- Public `/api/health` must remain unchanged.
- No dashboard tab/module behavior may regress because of this cleanup round.

## 56. Pure-bond Truthfulness + Sort Stability + 250D Readiness Spec (2026-03-30)

### 56.1 Scope
- This round changes only:
  - convertible theoretical-pricing pure-bond input rule
  - dashboard table sort-position stability
  - default history-sync readiness for 250-day HFQ volatility
- This round does not change:
  - convertible premium formula
  - non-convertible module behavior
  - public API path names

### 56.2 Pure-bond input rule
- In `data_fetch/convertible_bond/source.py > _build_theoretical_metrics()`:
  - `bondValue` may use only `pureBondValue`
  - `_bond_floor_value()` must no longer be used as a runtime fallback for outward theoretical pricing
- If `pureBondValue` is missing or non-positive:
  - outward `bondValue = null`
  - outward `theoreticalPrice = null`
  - outward `theoreticalPremiumRate = null`
  - call/put auxiliary values may stay null unless all required truthful inputs exist

### 56.3 Front-end pure-bond read rule
- In `presentation/dashboard/dashboard_page.js`:
  - `readPureBondBase()` must read the truthful upstream pure-bond field first-class
  - it must not resurrect a retired local discounted fallback through old `bondValue` semantics

### 56.4 Sort-stability rule
- Sort interaction must preserve the current table wrapper scroll offset.
- In `presentation/dashboard/dashboard_page.js`:
  - each sortable table wrapper should expose a stable `data-table-key`
  - sort/page rerender paths may capture and restore wrapper `scrollLeft` / `scrollTop`
  - clicking a sort header must not visually snap the user back to the first visible column

### 56.5 250-day default rule
- `data_fetch/convertible_bond/history_source.py` fallback defaults must no longer assume `20/60/120` when config is absent; the default active window is `250`.
- `data_fetch/cb_rights_issue/history_source.py` fallback default `volatility_window` must be `250`.
- `tools/cb_rights_issue_stock_history_db.py` default retention assumptions must remain compatible with the `251`-close minimum rather than the old `90`-row era.

### 56.6 Readiness verification rule
- DB verification must inspect at least:
  - symbol count
  - per-symbol row-count range
  - how many symbols satisfy `>= 251` closes
- This verification applies to:
  - `runtime_data/shared/stock_price_history.db`
  - `runtime_data/shared/cb_rights_issue_stock_history.db`
- If readiness is insufficient, the result must be reported truthfully and followed by the appropriate history sync run before cloud close-out.

### 56.7 Regression boundary
- Convertible visible labels and API keys remain unchanged in this round.
- Sort result order may change only because of the intended sort key, not because the viewport resets.
- `250日波动率` wording and `volatility250` preference remain the active live contract.

## 58. Pure-bond Daily-cache Wireback Spec (2026-03-30)

### 58.1 Scope
- This round changes only the convertible pure-bond read/cache wireback.
- This round does not change:
  - option-pricing formula shape
  - public API path name
  - non-convertible modules
  - push behavior

### 58.2 Source-of-truth rule
- `pureBondValue` remains sourced only from the existing Eastmoney pure-bond interface:
  - `type=RPTA_WEB_KZZ_LS`
  - field `PUREBONDVALUE`
- The system must not restore the retired local discounted-bond fallback.

### 58.3 Read-path rule
- In `data_fetch/convertible_bond/source.py > get_bond_cb_data()`:
  - `pureBondMap` must be loaded through the shared daily-cache helper, not read as an unwritten raw aux entry only
  - the helper must attempt same-day upstream fetch first
  - if fresh same-day fetch succeeds, the fetched map must be used for outward rows and later persisted through the aux-cache write path
  - if same-day fetch fails, the read path may reuse only previously cached real upstream values

### 58.4 Outward row rule
- For each outward convertible row:
  - when `pureBondMap[code]` exists, expose:
    - `pureBondValue`
    - `pureBondValueDate`
    - `pureBondValueSource`
  - when the map lacks the code, keep these fields null/absent-equivalent and let the page render `--`
- `bondValue`, `theoreticalPrice`, and `theoreticalPremiumRate` remain governed by the truthful pure-bond rule from Spec 56.

### 58.5 Runtime wording rule
- Any assumptions/source-note text in the outward payload must no longer say:
  - `or_discount_floor_fallback`
- Wording must reflect the live rule:
  - pure-bond value comes from upstream API only
  - missing source value leads to truthful null output

### 58.6 Regression boundary
- Successful same-day pure-bond fetch must improve visible coverage only; it must not alter non-pure-bond fields.
- If the upstream pure-bond source is temporarily unavailable, the module may still use older cached real values, but it must not fabricate new ones.

## 82. Convertible Strong-redeem Page Truthfulness + Theoretical-premium 250D Repair Spec (2026-03-30)

### 82.1 Scope
- This round changes only the convertible read/display chain:
  - force-redeem page expression
  - pure-bond/theoretical-premium outward visibility
  - 250D wording consistency for the affected table/help text
- This round does not change:
  - non-convertible modules
  - the active 250D volatility standard itself
  - push-rule semantics

### 82.2 Strong-redeem truth rule
- `presentation/dashboard/dashboard_page.js > isConvertibleForceRedeemHighlighted()` may highlight only rows that:
  - have affirmative strong-redeem wording
  - do not carry terminal wording such as `完成 / 摘牌 / 终止 / 退市`
- `strategy/convertible_bond/service.js > isCbArbRowDelistedOrExpired()` remains the terminal gate:
  - rows with truthful terminal delist/cease dates or terminal force-redeem wording must be removed from the live list
- Therefore terminal cases such as `海优转债` must resolve to “not listed in live table” when the source is already terminal.

### 82.3 Theoretical-premium truth rule
- In `data_fetch/convertible_bond/source.py`:
  - outward `theoreticalPrice` and `theoreticalPremiumRate` continue to use the current `PRIMARY_VOL_WINDOW`
  - the active live window remains `250`
  - truthful outward values require:
    - `pureBondValue > 0`
    - `stockPrice`
    - `convertPrice`
    - `remainingYears`
    - `volatility250`
- If any truthful prerequisite is absent:
  - outward `theoreticalPrice = null`
  - outward `theoreticalPremiumRate = null`
- No local discounted bond-floor fallback may be reintroduced.

### 82.4 Daily-cache read rule
- The normal `GET /api/market/convertible-bond-arbitrage` path must read the same-day real `pureBondMap` first.
- If same-day fetch is empty or partially empty:
  - previously cached real upstream `pureBondValue` snapshots may still fill missing codes
  - fallback must remain code-by-code and truthful
- Public row shaping in `start_server.js` must keep exposing:
  - `pureBondValue`
  - `theoreticalPrice`
  - `theoreticalPremiumRate`
  - `forceRedeemStatus`
  - `delistDate`
  - `ceaseDate`

### 82.5 Page wording rule
- Convertible table and helper wording for this chain must continue to say `250日波动率` / `250日后复权年化波动率`.
- The helper text may explain the formula only when the example row has truthful:
  - pure-bond value
  - theoretical price
  - option value
  - 250D volatility
- It must not imply that blank theoretical-premium rows are computation errors when truthful pure-bond input is absent.

### 82.6 Regression boundary
- Active non-terminal strong-redeem rows can still highlight yellow.
- Terminal strong-redeem rows stay filtered out.
- Rows with truthful pure-bond input recover visible theoretical-premium values.
- Rows missing truthful pure-bond input remain blank rather than fabricated.

## 84. Custom Monitor Three-decimal Precision Spec (2026-03-30)

### 84.1 Scope
- This round changes only the custom-monitor chain:
  - `strategy/custom_monitor/service.js`
  - `presentation/dashboard/dashboard_page.js`
  - `notification/styles/markdown_style.js`
- This round does not change:
  - custom-monitor formulas
  - config structure
  - non-monitor modules

### 84.2 Output precision rule
- In `strategy/custom_monitor/service.js > recalculateMonitor()`:
  - outward derived numeric fields must round to `3` decimals
  - this applies to:
    - `acquirerPrice`
    - `targetPrice`
    - `cashDistributionCny`
    - `cashPayout`
    - `stockPayout`
    - `stockSpread`
    - `safetyFactor`
    - `stockYieldRate`
    - `cashSpread`
    - `cashYieldRate`
- Internal formula order remains unchanged; only the outward rounded result changes.

### 84.3 Dashboard display rule
- In `presentation/dashboard/dashboard_page.js`:
  - monitor tab table values must render with `3` decimals
  - monitor detail items and formula text must render with `3` decimals
- The affected monitor display fields include:
  - target price
  - stock-leg yield
  - cash-leg yield
  - best yield
  - acquirer price
  - target price
  - cash consideration
  - stock-leg payout
  - stock-leg spread
  - cash option price
  - cash-leg spread
  - formula explanation factors

### 84.4 Summary markdown rule
- In `notification/styles/markdown_style.js > buildMonitorLines()`:
  - `股票腿收益率`
  - `现金腿收益率`
  - `最优收益率`
  must render with `3` decimals to match the dashboard.

### 84.5 Regression boundary
- Sorting behavior remains numeric and unchanged in semantics.
- Monitoring formulas remain unchanged.
- Non-monitor modules keep their existing display precision.

## 85. Convertible Force-redeem Status Column + Highlight Repair Spec (2026-03-30)

### 85.1 Scope
- This round changes only the convertible read/display chain:
  - outward force-redeem status derivation
  - convertible table trailing status column
  - convertible strong-redeem row highlight style/rule
- This round does not change:
  - convertible pricing formulas
  - push behavior
  - non-convertible modules

### 85.2 Source-truth rule
- In `data_fetch/convertible_bond/source.py`:
  - raw `isRedeem` must no longer be exposed semantically as outward `forceRedeemStatus`
  - outward `forceRedeemStatus` must be a derived status text based on stronger real clues, including:
    - redeem notice dates
    - terminal delist dates
    - terminal stop-trading dates when applicable
- Outward status text may be blank when the source does not provide enough truthful evidence.

### 85.3 Outward status display rule
- The outward payload may expose supporting fields needed by the page, including notice dates.
- In `presentation/dashboard/dashboard_page.js`:
  - the convertible table must add a final column `强赎状态`
  - the column renders derived status text first
  - when notice date exists, the second line may render the date

### 85.4 Highlight rule
- `isConvertibleForceRedeemHighlighted()` must return true only when outward derived status clearly means an active published strong-redeem state.
- It must return false for:
  - blank status
  - generic raw flags such as the retired all-`是` source
  - terminal states such as `已摘牌 / 已完成强赎 / 已终止上市`

### 85.5 Style rule
- `presentation/templates/dashboard_template.html` strong-redeem row styling must use a brighter yellow visual treatment.
- The sticky left identity cell must stay visually aligned with that brighter yellow tone.

### 85.6 Regression boundary
- Convertible row highlighting becomes narrower and more truthful than the previous false-positive state.
- The final-column addition must not disturb earlier convertible formulas or sorting semantics.

## 83. Convertible Full-column Sort + Compact-width Spec (2026-03-30)

### 83.1 Scope
- This round changes only the convertible dashboard table presentation.
- This round does not change:
  - fetch logic
  - pricing formula
  - public API keys
  - push/runtime behavior

### 83.2 Sort-surface rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - every visible convertible main-table column must set `sortable: true`
  - each column must expose an explicit `sortValue`
  - composite cells must sort by their primary displayed value rather than the rendered HTML text

### 83.3 Convertible sort mapping
- Required sort mapping for the live table:
  - `转债名称` -> `bondName`
  - `转债价` -> `price`
  - `正股` -> `stockName`
  - `正股价` -> `stockPrice`
  - `正股成交` -> `stockAvgTurnoverAmount20Yi`
  - `转股价` -> `convertPrice`
  - `转股价值` -> `convertValue`
  - `转股溢价` -> `premiumRate`
  - `ATR系数/ATR%` -> `atrCoefficient`
  - `抛压系数` -> `sellPressureCoefficient`
  - `市场` -> `boardType`
  - `加权折价` -> `weightedDiscountRate`
  - `双低` -> `doubleLow`
  - `纯债价值` -> `pureBondValue`
  - `理论溢价` -> `theoreticalPremiumRate`
  - `剩余规模` -> `remainingSizeYi`
  - `250日波动率` -> `volatility250`
  - `剩余期限` -> `remainingYears`

### 83.4 Sort-header affordance rule
- Sort headers must keep using the existing table-state mechanism, but the visual affordance changes to:
  - compact up/down indicator
  - indicator shown above the label
  - reduced horizontal footprint compared with the previous inline layout

### 83.5 Convertible width rule
- Convertible width tuning must stay isolated to `table[data-table-kind="convertible"]`.
- The implementation may add convertible-specific column classes such as:
  - identity
  - quote
  - factor
  - numeric
  - percent
- These classes must tighten width closer to visible content than the old generic shared widths.
- Generic shared width rules for other table kinds must not be unintentionally widened or broken.

### 83.6 Regression boundary
- Existing sticky left identity column remains sticky.
- Existing sort-state persistence and scroll-restoration behavior remain intact.
- No convertible backend field is added, removed, or renamed in this round.

## 84. CB-rights-issue 250D Enforcement + History-DB Spec (2026-03-30)

### 84.1 Scope
- This round changes only the cb-rights-issue fetch/strategy/readiness chain.
- This round does not change:
  - AH / AB / LOF / dividend modules
  - convertible-arbitrage pricing chain
  - push schedule semantics

### 84.2 Live volatility rule
- In the cb-rights-issue chain, the only real pricing volatility is:
  - HFQ daily closes
  - latest 250 close-to-close log returns
  - annualized by trading-day convention
- The source row should expose `volatility250`.
- If `volatility60` is still exposed for compatibility, it must mirror the active `volatility250` value rather than a distinct 60-day metric.

### 84.3 Strategy rule
- In `strategy/cb_rights_issue/service.py`:
  - Black-Scholes pricing must read `volatility250` as the live source-of-truth input
  - it must not use an old real `volatility60` fallback
  - if `volatility250` is missing, `optionUnitValue / expectedProfit / expectedReturnRate` must remain null

### 84.4 History-readiness rule
- `runtime_data/shared/cb_rights_issue_stock_history.db` must be verified with:
  - symbol count
  - per-symbol row-count range
  - number of symbols with `>=251` closes
- A full sync must be run when the DB is still in the old ~90-row state.
- Truthful exceptions are allowed only for symbols whose listing history itself is insufficient.

### 84.5 Fetch-layer rule
- In `data_fetch/cb_rights_issue/source.py`:
  - `historyCloseCount` must reflect the dedicated history DB close count
  - `volatility250` must be derived only from the dedicated history DB
  - same-day source rows must not surface a real old 60-day volatility as if it were still active

### 84.6 Regression boundary
- Existing response envelope remains unchanged.
- Existing fields may remain for compatibility, but their semantics must align with the 250D live rule.
- Rows lacking enough history remain visible as source rows, but their pricing metrics must degrade truthfully.

## 87. Convertible Net Call-spread Debug Fields Spec (2026-03-30)

### 87.1 Internal helper fields
- `data_fetch/convertible_bond/source.py > _build_theoretical_metrics(...)` may additionally preserve:
  - `longCallOptionValue*`
  - `shortCallOptionValue*`
  - `callSpreadOptionValue*`
  - `redeemCallStrike*`
- These fields are for verification and explanatory copy alignment.

### 87.2 Primary-window projection rule
- When the primary volatility window is projected back to row-level outward fields, the row may also carry:
  - `longCallOptionValue`
  - `shortCallOptionValue`
  - `callSpreadOptionValue`
  - `redeemCallStrike`
  - `pricingFormula = bond+callspread`

### 87.3 Dashboard wording rule
- Dashboard explanatory text must describe the live formula as:
  - `理论价 = 债底 + 净看涨价差价值`
  - `净看涨价差价值 = call(转股价) - call(强赎价)`
- If `longCallOptionValue / shortCallOptionValue` are available, the example text should prefer showing both legs explicitly.
- The above `call(转股价)` wording is superseded by section 95 and is no longer the live wording.

## 86. CB-rights-issue Web-visible 250D Sync + Cache-bust Spec (2026-03-30)

### 86.1 Scope
- This round changes only the public dashboard presentation layer for `cb_rights_issue`.
- This round does not change:
  - the cb-rights-issue pricing formula
  - public API path or payload shape
  - push logic
  - non-cb-rights-issue modules

### 86.2 Visible wording rule
- In `presentation/dashboard/dashboard_page.js`:
  - all operator-facing explanatory text for the `可转债抢权配售` panel must match the already-active live volatility rule
  - stale wording such as `60 日波动率` must be removed
  - the visible wording must say `250日波动率`

### 86.3 Explanation boundary
- The panel copy may summarize the rule as:
  - fixed Jisilu pre-plan source
  - dedicated HFQ stock-history DB
  - `250` latest log-return samples annualized
  - expected return as a reference metric
- The copy must not imply a separate old 60-day runtime path still exists.

### 86.4 Template cache-bust rule
- In `presentation/templates/dashboard_template.html`:
  - the dashboard script query token must be bumped
  - goal: force browsers to fetch the refreshed front-end bundle after deployment
- This cache-bust action must remain front-end only and must not create a new route.

### 86.5 Verification rule
- Public homepage HTML must reference the new dashboard bundle token.
- Public cb-rights-issue page text must reflect `250日波动率`.
- Public API `/api/market/cb-rights-issue` continues exposing the already-fixed `volatility250`.

## 87. Convertible Theoretical-option Columns Spec (2026-03-30)

### 87.1 Scope
- This round changes only the convertible dashboard table presentation.
- This round does not change:
  - fetch logic
  - pricing formula
  - public API keys
  - push/runtime behavior

### 87.2 Column placement rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - three new columns must appear immediately after `理论溢价`
  - the order is fixed as:
    - `理论期权价值`
    - `隐含期权价值`
    - `期权折价率`

### 87.3 Read rule
- `理论期权价值` must reuse the existing theoretical-pricing result:
  - if `pricingFormula == "bond+callspread"` and `callOptionValue` exists, read `callOptionValue`
  - otherwise keep the existing compatibility read path:
    - `(callOptionValue ?? 0) - (putOptionValue ?? 0)`
    - fallback `theoreticalPrice - pureBondValue`
- `隐含期权价值` is:
  - `price - pureBondValue`
- `期权折价率` is:
  - `隐含期权价值 / 理论期权价值 - 1`

### 87.4 Truth boundary
- If any required truthful input is missing, the derived cell must stay null/blank.
- No guessed fallback or new backend hydration is allowed in this round.

### 87.5 Sort rule
- The three new columns remain sortable as numeric columns.
- Sort mapping is:
  - `理论期权价值` -> computed theoretical option value
  - `隐含期权价值` -> `price - pureBondValue`
  - `期权折价率` -> computed option discount rate

### 87.6 Cache-bust rule
- `presentation/templates/dashboard_template.html` should bump the dashboard script token again in this round so browsers fetch the new table definition promptly.

## 88. Convertible Option-discount-rate Correction Spec (2026-03-30)

### 88.1 Scope
- This round changes only the convertible dashboard table presentation.
- This round does not change:
  - fetch logic
  - pricing formula
  - public API keys
  - push/runtime behavior

### 88.2 Read rule
- `理论期权价值` stays unchanged.
- `隐含期权价值` stays unchanged:
  - `price - pureBondValue`
- The old column label `期权比例` must be renamed to:
  - `期权折价率`
- `期权折价率` must be corrected to:
  - `隐含期权价值 / 理论期权价值 - 1`

### 88.3 Truth boundary
- If `理论期权价值` is missing or equals `0`, `期权折价率` stays null.
- If `隐含期权价值` is missing, `期权折价率` stays null.
- No guessed fallback is allowed.

### 88.4 Sort rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - `期权折价率` remains a numeric sortable column
  - its `sortValue` must read the corrected discount-rate result

### 88.5 Cache-bust rule
- `presentation/templates/dashboard_template.html` should bump the dashboard script token again in this round so browsers fetch the corrected ratio implementation.

## 90. Convertible Option-discount Cell Stacked-gap Spec (2026-03-30)

### 90.1 Scope
- This round changes only the convertible dashboard table presentation.
- This round does not change:
  - fetch logic
  - pricing formula
  - public API keys
  - push/runtime behavior

### 90.2 Derived display rule
- In `presentation/dashboard/dashboard_page.js` add one display-only helper:
  - `optionValueGap = theoreticalOptionValue - implicitOptionValue`
- `optionValueGap` must stay null when either source value is null.

### 90.3 Cell rendering rule
- In `buildConvertibleColumns()` the `期权折价率` column must render as a compact stacked cell:
  - first line: formatted `期权折价率`
  - second line: `价差 <formatted optionValueGap>`
- The cell semantic color may continue following the existing rate-based status class.

### 90.4 Sort rule
- The `期权折价率` column remains sorted by the computed rate only.
- The displayed `期权价差` text must not become the sort source.

### 90.5 Cache-bust rule
- `presentation/templates/dashboard_template.html` should bump the dashboard script token again in this round so browsers fetch the updated cell renderer promptly.

## 89. Convertible Summary / Push Force-redeem Exclusion Spec (2026-03-30)

### 89.1 Scope
- This round changes only convertible summary / push candidate selection.
- This round does not change:
  - main-table membership
  - pricing formulas
  - public API route paths
  - non-convertible modules

### 89.2 Active force-redeem rule
- The system needs one shared helper for active force-redeem exclusion.
- A row is treated as active force-redeem-excluded when:
  - `forceRedeemStatus` contains active published semantics such as:
    - `已公告强赎`
    - `强赎进行中`
    - `实施赎回`
    - `公告赎回`
- A row is not excluded by this rule when:
  - status is blank
  - status means negation such as `不强赎 / 暂不强赎 / 不提前赎回`
- Terminal rows such as `已完成强赎 / 已摘牌 / 已终止上市 / 停止交易` remain governed by the existing terminal-row filter rather than this active exclusion helper.

### 89.3 Summary rule
- In `presentation/dashboard/dashboard_page.js`, the convertible page top-summary candidates for:
  - `双低前3`
  - `理论溢价前3`
  must filter out active force-redeem-excluded rows before ranking.

### 89.4 Main-summary push rule
- `notification/styles/markdown_style.js > buildCbSummaryLines()` relies on `cbArbOpportunitySets(rows)`.
- Therefore `strategy/convertible_bond/service.js > cbArbOpportunitySets()` must exclude active force-redeem-excluded rows before building category picks.

### 89.5 Convertible independent push rule
- `strategy/convertible_bond/service.js > buildConvertibleBondDiscountSnapshot()` must exclude active force-redeem-excluded rows from:
  - buy/sell signal generation
  - monitor pool
  - `premiumMonitorSummary`
- The outward `rows` payload may still keep those rows for page display.

### 89.6 Regression boundary
- Active force-redeem rows may still appear in the main convertible table.
- Existing terminal-row filtering remains unchanged.
- Existing push formats remain unchanged except for the removed excluded rows.


### 90.1 Scope
- This round changes only the LOF chain:
  - fetch config
  - LOF source grouping
  - LOF strategy group shaping
  - LOF route fallback payload
  - LOF dashboard subtab/default selection
  - LOF active operator docs
- This round does not change:
  - LOF API path
  - LOF independent push endpoints
  - non-LOF modules

### 90.2 Active group rule
- The only live LOF groups are:
  - `index`
  - `asia`

### 90.3 Config rule
- In `config.yaml > data_fetch.plugins.lof_arbitrage`:
  - `default_group = index`
  - `source_page_urls` keeps only:
    - `index`
    - `asia`
  - `source_api_urls` keeps only:
    - `index`
    - `asia`
- In `config.yaml > strategy.lof_arbitrage`:
  - `default_group = index`
- Dashboard module notes must describe only the still-live `指数LOF / QDII亚洲`
  calculation path.

### 90.4 Fetch rule
- In `data_fetch/lof_arbitrage/source.py`:
  - `GROUP_META` keeps only `index` and `asia`
  - `SOURCE_GROUP_ORDER` keeps only `index` and `asia`
  - `build_group_summary()` keeps only `index` and `asia`
  - outward `sourceSummary.defaultGroup = index`
- The fetch layer must no longer emit any retired overseas group label.

### 90.5 Strategy rule
- In `strategy/lof_arbitrage/service.py`:
  - default group becomes `index`
  - outward groups list contains only `index` and `asia`
- The remaining IOPV branch is:
  - same-day NAV direct-read when `navDate == priceDate`
  - otherwise `index / asia` use the existing `T-1` aligned branch

### 90.6 Route and dashboard rule
- In `presentation/routes/market_routes.js`:
  - LOF empty fallback payload uses `defaultGroup = index`
- In `presentation/dashboard/dashboard_page.js`:
  - `state.lofSubview` initial value becomes `index`
  - LOF fallback groups become only `index` and `asia`
  - LOF dashboard rendering must no longer reserve a third historical subtab slot

### 90.7 Truth boundary
- This round is a removal round, not a source substitution round.
- The system must not fabricate a replacement third group.
- Historical overseas samples that no longer belong to a live group must disappear from the active LOF dataset rather than be silently relabeled.

### 90.8 Verification rule
- Repo search should no longer find live LOF code/config/doc contracts that expose:
  - any retired overseas group key
  - any retired overseas visible label

## 91. Convertible Pure-bond Premium Dual-value Column Spec (2026-03-30)

### 91.1 Scope
- This round changes only the convertible dashboard presentation path:
  - `presentation/dashboard/dashboard_page.js`
- This round does not change:
  - data-fetch logic
  - API payload keys
  - pricing formulas
  - non-convertible modules

### 91.2 Read rule
- `readPureBondBase(row)` remains the truthful source for `纯债价值`.
- `computePureBondPremiumRate(row)` must use the user-specified live rule:
  - `price / pureBondValue - 1`
  - then render it as a percentage-style ratio value in the table
- If `price` or `pureBondValue` is missing/non-positive, the column must render `--`.

### 91.3 Column rule
- In the convertible main table:
  - visible label becomes `纯债溢价`
  - primary display = computed pure-bond premium ratio
  - secondary display = `纯债值 {pureBondValue}`

### 91.4 Sort rule
- Column sort value must equal `computePureBondPremiumRate(row)`.
- Sorting must no longer use `readPureBondBase(row)`.

### 91.5 Regression boundary
- Outward payload still exposes `pureBondValue` unchanged.
- Other convertible columns and all non-convertible modules keep their current behavior.

## 92. Convertible Force-redeem Marker Simplification Spec (2026-03-30)

### 92.1 Scope
- This round is limited to:
  - `start_server.js`
  - `presentation/dashboard/dashboard_page.js`
  - `presentation/templates/dashboard_template.html`
- No fetch-source rule or upstream force-redeem derivation rule changes in this round.

### 92.2 Active force-redeem marker rule
- The existing active force-redeem semantic boundary remains:
  - affirmative statuses such as `已公告强赎 / 强赎进行中 / 实施赎回 / 公告赎回` count as active
  - negative statuses such as `不强赎 / 暂不强赎 / 不提前赎回 / 不赎回` do not count
  - terminal statuses such as `已完成强赎 / 已摘牌 / 已终止上市 / 退市` do not count
  - rows whose `ceaseDate / delistDate` are already not later than today do not count
- The main table must no longer express this state via full-row highlight.
- Instead, the bond-name cell must append a red `!` marker immediately after the visible bond name when the row matches the active force-redeem rule.

### 92.3 Bond-name reason text rule
- The convertible bond-name cell must support a truthful secondary reason line assembled only from exposed public fields.
- The strong-redeem segment must read from:
  - `forceRedeemStatus`
  - `forceRedeemNoticeDate`
- The maturity segment must read from:
  - `maturityDate`
  - `maturityRedeemPrice`
- Recommended rendering contract:
  - strong-redeem segment example: `强赎 2026-03-30`
  - maturity segment example: `到期 2028-11-22 / 到期价 108.00`
- If `maturityRedeemPrice` is missing, the maturity segment must degrade to date-only text and must not fabricate a price.
- If no truthful reason segment exists, the bond-name cell falls back to its current two-line compact layout.

### 92.4 Column and layout rule
- Remove the standalone `强赎状态` column from the convertible main table.
- Remove the convertible row class hook that previously applied yellow background styling.
- Add only the compact red marker and subtle reason text in the sticky bond-name cell.

### 92.5 Public payload rule
- `shapeCbArbPublicRows()` must additionally expose:
  - `maturityRedeemPrice`
- Existing outward fields remain unchanged.

### 92.6 Regression boundary
- `summaryRows` and any summary/push exclusion logic that already filters active force-redeem rows must keep their current behavior.
- Other convertible columns, sorting, and non-convertible modules keep their current behavior.

## 92. Subscription Footnote Removal Spec (2026-03-30)

### 92.1 Scope
- This round changes only the subscription top-section footnote visibility.
- This round does not change:
  - subscription fetch logic
  - subscription table rendering
  - dashboard shared footnote renderer
  - any non-subscription module

### 92.2 Config rule
- In `config.yaml > presentation.dashboard_module_notes`:
  - the active `subscription` note object is removed
  - or equivalently kept empty so the shared renderer receives no visible lines

### 92.3 Rendering rule
- `presentation/dashboard/dashboard_page.js` keeps the existing shared footnote render path:
  - `renderModuleFootnote('subscription')`
- Because the module has no configured note lines after this round:
  - the renderer must hide the entire footnote card for the subscription section

### 92.4 Regression boundary
- `cbArb / ah / ab / monitor / dividend / merger` footnotes remain driven by the same
  config contract and continue rendering normally.
- `GET /api/dashboard/ui-config` remains the same route; only its effective
  `moduleNotes.subscription` content becomes empty/absent.

## 93. Convertible Weighted-discount Factor Simplification Spec (2026-03-30)

### 93.1 Scope
- This round changes only the live convertible weighted-discount factor path:
  - `strategy/convertible_bond/service.js`
  - `presentation/dashboard/dashboard_page.js`
  - convertible strategy docs
- This round does not change:
  - public API path
  - board-coefficient mapping rule
  - non-convertible modules
  - push scheduling path

### 93.2 ATR rule
- In `enrichDiscountStrategyRow()`:
  - `stockAtr20Pct = stockAtr20 / stockPrice * 100`
  - `atrCoefficient = stockAtr20Pct`
- This rule is superseded by section 94 in the same day and is no longer the live rule.
- Anchor interpolation is retired from the active ATR-coefficient path.
- `atrRatio` may remain as a compatibility/debug field, but it must not participate in
  `weightedDiscountRate`.

### 93.3 Sell-pressure rule
- In `enrichDiscountStrategyRow()`:
  - `sellPressureRatio = stockAvgTurnoverAmount20Yi / remainingSizeYi`
  - `sellPressureCoefficient = sellPressureRatio`
- Guard rule:
  - if `remainingSizeYi` is missing or `<= 0`, both fields return `null`
  - if `stockAvgTurnoverAmount20Yi` is missing, both fields return `null`

### 93.4 Weighted-discount rule
- Final live formula is fixed to:
  - `weightedDiscountRate = (-premiumRate) * atrCoefficient * sellPressureCoefficient * boardCoefficient`
- Therefore:
  - negative-premium rows still yield positive weighted-discount values
  - positive-premium rows still yield negative weighted-discount values
  - only the coefficient definitions change in this round

### 93.5 Board rule
- `normalizeBoardType()` and `normalizeBoardCoefficients()` remain unchanged.
- `boardCoefficient` keeps the existing mapping:
  - `科创板`
  - `创业板`
  - `主板`

### 93.6 Dashboard factor-column rule
- In `presentation/dashboard/dashboard_page.js > buildConvertibleColumns()`:
  - keep the visible labels:
    - `ATR系数/ATR%`
    - `抛压系数`
    - `市场`
  - update the sell-pressure secondary text to match the live direction:
    - `成交/规模 {sellPressureRatio}`
- Existing sort keys remain bound to:
  - `atrCoefficient`
  - `sellPressureCoefficient`
  - `boardCoefficient`-related row data as already implemented

### 93.7 Regression boundary
- `GET /api/market/convertible-bond-arbitrage` keeps the same path and top-level shape.
- Existing visible fields remain available:
  - `stockAtr20Pct`
  - `atrCoefficient`
  - `sellPressureRatio`
  - `sellPressureCoefficient`
  - `boardCoefficient`
  - `weightedDiscountRate`
- The live page and push chain must continue reading the same payload keys after this round.

## 94. Convertible ATR-coefficient Definition Reset Spec (2026-03-30)

### 94.1 Scope
- This round changes only the live ATR-coefficient definition in the convertible
  weighted-discount path.
- This round does not change:
  - sell-pressure rule
  - board-coefficient mapping
  - API path
  - non-convertible modules

### 94.2 ATR rule
- In `strategy/convertible_bond/service.js > enrichDiscountStrategyRow()`:
  - `stockAtr20Pct = stockAtr20 / stockPrice * 100`
  - `premiumMagnitude = abs(-premiumRate)`
  - `atrCoefficient = premiumMagnitude / stockAtr20Pct`
- Guard rule:
  - if `premiumMagnitude` is missing, `atrCoefficient = null`
  - if `stockAtr20Pct` is missing or `<= 0`, `atrCoefficient = null`
- `atrRatio` may remain and should equal the same computed ratio for compatibility.

### 94.3 Sell-pressure and board rule
- Keep unchanged:
  - `sellPressureRatio = stockAvgTurnoverAmount20Yi / remainingSizeYi`
  - `sellPressureCoefficient = sellPressureRatio`
  - `boardCoefficient` from the existing board mapping

### 94.4 Weighted-discount rule
- The live formula remains:
  - `weightedDiscountRate = (-premiumRate) * atrCoefficient * sellPressureCoefficient * boardCoefficient`
- Only the ATR-coefficient definition changes in this round.

### 94.5 Presentation rule
- `presentation/dashboard/dashboard_page.js` may keep the visible ATR column label:
  - `ATR系数/ATR%`
- The primary number must read `atrCoefficient`.
- The secondary hint may continue showing `ATR% {stockAtr20Pct}`.

### 94.6 Regression boundary
- The outward payload keeps:
  - `stockAtr20Pct`
  - `atrRatio`
  - `atrCoefficient`
  - `sellPressureRatio`
  - `sellPressureCoefficient`
  - `weightedDiscountRate`
- The convertible page and push chain continue to consume the same keys.

## 95. Convertible Long-call Strike Max-rule Spec (2026-03-30)

### 95.1 Scope
- This round changes only the live long-call strike rule in the convertible
  theoretical-pricing path.
- This round does not change:
  - short-call strike source
  - option model
  - non-convertible modules

### 95.2 Strike rule
- In `data_fetch/convertible_bond/source.py > _build_theoretical_metrics(...)`:
  - `optionQty = 100 / convertPrice`
  - `bondFloorStrike = pureBondValue / optionQty`
  - `callStrike = max(convertPrice, bondFloorStrike)`
- Guard rule:
  - if `optionQty` is missing or `<= 0`, `callStrike = null`
  - if `pureBondValue` is missing, no theoretical value is produced

### 95.3 Call-spread rule
- The live option leg becomes:
  - `longCallValue = americanCall(stockPrice, callStrike, remainingYears, riskFreeRate, vol) * optionQty`
  - `shortCallValue = americanCall(stockPrice, redeemTriggerPrice, remainingYears, riskFreeRate, vol) * optionQty`
  - `callSpreadValue = max(longCallValue - shortCallValue, 0)`
  - `theoreticalPrice = pureBondValue + callSpreadValue`
- Therefore `callStrike*` is a truthful live strike field, not a direct alias of `convertPrice`.

### 95.4 Dashboard wording rule
- In `presentation/dashboard/dashboard_page.js`:
  - any formula hint that currently says `call(转股价) - call(强赎价)` must be updated
  - preferred truthful wording:
    - `净看涨价差价值 = call(max(转股价, 债底折算行权价)) - call(强赎价)`
  - the detail text should show the actual `多头行权价` from `callStrike`

### 95.5 Regression boundary
- The outward payload keeps the same key family:
  - `callStrike*`
  - `redeemCallStrike*`
  - `longCallOptionValue*`
  - `shortCallOptionValue*`
  - `callSpreadOptionValue*`
  - `theoreticalPrice*`
- Only the meaning of `callStrike*` changes to the live max-rule value.

## 94. Convertible Header Wrap + Width Compression Spec (2026-03-30)

### 94.1 Scope
- This round is limited to:
  - `presentation/dashboard/dashboard_page.js`
  - `presentation/templates/dashboard_template.html`
- No API field, data source, or strategy logic changes are allowed in this round.

### 94.2 Header rendering rule
- `renderTableHeader()` must support a column-level optional header HTML field so specific
  columns can render trusted manual line breaks.
- Fallback behavior remains unchanged:
  - if no header HTML is provided, render the escaped plain-text label
- Convertible long headers may therefore use explicit HTML such as:
  - `理论期<br>权价值`
  - `隐含期<br>权价值`
  - `期权<br>折价率`

### 94.3 Convertible-only wrap rule
- The wrap behavior must be limited to `table[data-table-kind="convertible"] th`.
- Convertible header labels may use:
  - `white-space: normal`
  - tighter line-height
  - character-level wrap for CJK text
- Convertible body cells must keep the current compact single-line reading rule unless
  they already use stacked value rendering.

### 94.4 Width compression rule
- Convertible table may reduce:
  - header/cell horizontal padding
  - `col-cb-quote` minimum width
  - `col-cb-volume` minimum width
  - `col-cb-num` minimum width
  - `col-cb-percent` minimum width
  - `col-cb-factor` minimum width
  - `col-cb-market` minimum width
- The sticky identity column should remain readable and must not be collapsed to the point
  that the bond name and marker become unusable.

### 94.5 Regression boundary
- Sort buttons, sort direction indicator, and sortable behavior remain unchanged.
- Existing stacked body cells such as premium/discount/theoretical columns keep their
  current numeric content and ordering semantics.

## 95. Convertible Timed-summary And Top-card Filter Tightening Spec (2026-03-30)

### 95.1 Scope
- This round changes only the convertible regular-summary candidate path:
  - `strategy/convertible_bond/service.js`
  - `start_server.js`
  - `notification/styles/markdown_style.js`
  - `presentation/dashboard/dashboard_page.js`
- This round does not change:
  - convertible main-table membership
  - theoretical-pricing formula
  - low-premium monitor thresholds or its independent push cadence
  - non-convertible modules

### 95.2 Shared summary-eligibility rule
- `strategy/convertible_bond/service.js` must expose one shared helper for regular
  summary candidates.
- A row is summary-eligible only when all conditions are true:
  - it survives the existing terminal/delist sanitation
  - it is not an active force-redeem row

### 95.3 Strategy reuse rule
- `cbArbOpportunitySets(rows)` must reuse the shared summary-eligible row set instead of
  rebuilding a looser filter locally.
- This keeps timed main-summary selection aligned with the page top-summary candidates.

### 95.4 Server summary-shaping rule
- In `start_server.js > normalizeDatasetPayload(key === 'cbArb')`:
  - `data` continues exposing the full shaped convertible rows
  - `premiumMonitorSummary` continues exposing the independent low-premium monitor pool
  - `summary.topDoubleLow` and `summary.topTheoreticalPremiumRate` must be built only
    from the shared summary-eligible rows
- Sorting remains:
  - `topDoubleLow`: ascending `doubleLow`
  - `topTheoreticalPremiumRate`: descending `theoreticalPremiumRate`

### 95.5 Timed main-summary markdown rule
- In `notification/styles/markdown_style.js`:
  - the convertible block in the main timed summary must narrow to exactly two groups:
    - `双低前三名`
    - `理论溢价率前三名`
  - no other convertible opportunity buckets may appear in this markdown block
- Each `理论溢价率前三名` line must additionally include:
  - computed `期权折价率`
- `期权折价率` must reuse existing truthful row fields only:
  - theoretical option value from current `callOptionValue / putOptionValue / theoreticalPrice`
  - implicit option value from `price - pureBondValue`
  - formula: `隐含期权价值 / 理论期权价值 - 1`

### 95.6 Dashboard top-card rule
- In `presentation/dashboard/dashboard_page.js > renderConvertiblePanel()`:
  - `双低前3`
  - `理论溢价前3`
  must render from `cbPayload.summary.topDoubleLow` and
  `cbPayload.summary.topTheoreticalPremiumRate`
- The `低溢价监控` card must continue reading `cbPayload.premiumMonitorSummary` and must
  not be replaced by the tightened regular-summary helper.

### 95.7 Regression boundary
- The main convertible table still shows all live rows allowed by the existing page/API
  path, including rows outside the tightened summary candidate set.
- `notification/styles/discount_strategy_markdown.js` remains untouched in this round.
- Existing low-premium monitor buy/sell thresholds and independent push cadence remain
  unchanged.
## 96. CB-rights-issue Single-table Rework + Market-cap Ratio Spec (2026-04-16)

### 96.1 Scope
- This round changes only the cb-rights-issue chain:
  - `data_fetch/cb_rights_issue/source.py`
  - `strategy/cb_rights_issue/service.py`
  - `presentation/dashboard/dashboard_page.js`
  - `notification/styles/cb_rights_issue_markdown.js`
  - `notification/cb_rights_issue/service.js`
- This round does not change:
  - AH / AB / LOF / dividend / merger / convertible-arbitrage paths
  - cb-rights-issue volatility source rule
  - cb-rights-issue route path

### 96.2 Fetch-layer market-value rule
- In `data_fetch/cb_rights_issue/source.py`:
  - stock spot enrichment must additionally load truthful `总市值`
  - preferred source is the real-time A-share spot API already available through AkShare
  - outward row field must expose `stockMarketValueYi`
- Guard rule:
  - if market value is missing/non-positive, `stockMarketValueYi = null`
  - `issueRatio` must then remain null
- `issueScaleYi` must mirror the live `cbAmountYi` row value for public-read clarity.

### 96.3 Main derived-field rule
- In `strategy/cb_rights_issue/service.py`, outward row fields must follow:
  - `issueScaleYi = cbAmountYi`
  - `issueRatio = issueScaleYi / stockMarketValueYi`
  - `placementShares = rawRequiredShares`
  - `marginRequiredShares = ceil((rawRequiredShares * 0.6) / 50) * 50`
  - `requiredFunds = placementShares * stockPrice`
  - `marginRequiredFunds = marginRequiredShares * stockPrice`
  - `expectedReturnRate = expectedProfit / requiredFunds * 100`
  - `marginReturnRate = expectedProfit / marginRequiredFunds * 100`
- Guard rule:
  - if any denominator is missing or `<= 0`, the corresponding ratio field must stay null

### 96.4 Peel-yield rule
- The live peel-yield rule is fixed to released-capital value only:
  - `rawFundsBase = rawRequiredShares * stockPrice`
  - `expectedPeelReturnRate = expectedReturnRate * (rawFundsBase - requiredFunds) / requiredFunds`
  - `marginPeelReturnRate = marginReturnRate * (rawFundsBase - marginRequiredFunds) / marginRequiredFunds`
- Guard rule:
  - if the base spread is not positive, the peel-yield field must remain null
  - no synthetic zero-fill is allowed

### 96.5 Annualized-return rule
- `annualizedReturnRate` base is fixed to `marginPeelReturnRate`.
- Annualization formula is fixed to compound annualization:
  - `(1 + marginPeelReturnRate / 100)^(252 / estimatedApplyTradingDays) - 1`
  - outward field remains percentage-style after conversion back to `* 100`
- `estimatedApplyTradingDays` rule:
  - if a row already has a future `applyDate`, use truthful trading days from today to `applyDate`
  - otherwise:
    - `上市委通过 -> 申购日` uses the median historical trading-day lag
    - `同意注册 / 注册生效 -> 申购日` uses the median historical trading-day lag
  - if no truthful sample exists, both `estimatedApplyTradingDays` and `annualizedReturnRate` stay null

### 96.6 Pinning and push-eligibility rule
- Page pinning is no longer expressed by summary cards.
- Each row must expose:
  - `inApplyStage`
  - `pinPriority`
  - `pushEligible`
- `pinPriority` is fixed to:
  - `0` for apply-stage rows
  - `1` for non-apply rows with `expectedReturnRate > min_expected_return_rate`
  - `2` for all other rows
- `pushEligible = true` only when:
  - `pinPriority` is `0` or `1`
- Apply-stage rows must sort ahead of all other rows regardless of annualized return.

### 96.7 Page rendering rule
- In `presentation/dashboard/dashboard_page.js`:
  - remove all top summary / source-status / reminder cards for `可转债抢权配售`
  - remove the second source table
  - remove detail rendering for this module
  - render one single paginated table only
- Visible columns are fixed to:
  - `正股代码`
  - `正股名称`
  - `方案进展`
  - `进展公告日`
  - `发行规模`
  - `总市值`
  - `发行比例`
  - `原始所需股数`
  - `配售股数`
  - `两融所需股数`
  - `转股价`
  - `波动率`
  - `单位期权价值`
  - `期权价值`
  - `所需资金`
  - `股权登记日`
  - `预期收益率`
  - `两融收益率`
  - `预期收益率去皮`
  - `两融收益率去皮`
  - `年化收益率`
- Visible `转债代码 / 转债名称` and module detail rows are retired in this round.
- Default table ordering must be:
  - `pinPriority asc`
  - then `annualizedReturnRate desc`
  - then `marginReturnRate desc`

### 96.8 Push markdown rule
- `notification/styles/cb_rights_issue_markdown.js` must render exactly two groups:
  - `申购阶段项目`
  - `预期收益率 > 6% 项目`
- The second group must exclude rows already included in the first group.
- Each pushed line must include:
  - `方案进展`
  - `进展公告日`
  - `发行规模`
  - `总市值`
  - `发行比例`
  - `两融所需股数`
  - `两融收益率`
  - `两融收益率去皮`
  - `年化收益率`

### 96.9 Response-shape rule
- `GET /api/market/cb-rights-issue` outward row fields must include:
  - `stockMarketValueYi`
  - `issueScaleYi`
  - `issueRatio`
  - `placementShares`
  - `marginRequiredShares`
  - `marginRequiredFunds`
  - `marginReturnRate`
  - `expectedPeelReturnRate`
  - `marginPeelReturnRate`
  - `annualizedReturnRate`
  - `estimatedApplyTradingDays`
  - `pinPriority`
  - `inApplyStage`
  - `pushEligible`
- Existing path and envelope remain unchanged.

### 96.10 Regression boundary
- `volatility250` remains the only live volatility input.
- Existing push schedule slots remain unchanged.
- Rows lacking truthful market value or trading-day samples must remain visible, but the related derived fields must degrade to null rather than guessed values.

## 97. Phase CK: CB-rights-issue Three-subtab Phase Split (2026-04-17)

- This round changes only the cb-rights-issue presentation contract:
  - `presentation/dashboard/dashboard_page.js`
  - `presentation/templates/dashboard_template.html`
  - related live docs only
- This round does not change:
  - `GET /api/market/cb-rights-issue` response envelope
  - cb-rights-issue pricing formulas
  - cb-rights-issue push grouping
  - non-cb-rights-issue modules

### 97.1 Subtab split rule
- The live cb-rights-issue page must render three subtabs:
  - `申购阶段`
  - `埋伏阶段`
  - `等待阶段`
- Row grouping is fixed to:
  - `申购阶段`: `inApplyStage = true`
  - `埋伏阶段`: `inApplyStage = false`, stage semantic is one of `上市委通过 / 同意注册 / 注册生效`, and `expectedReturnRate > 6`
  - `等待阶段`: all remaining rows

### 97.2 Name-cell simplification rule
- `正股名称` cells must render stock-name text only.
- The old second-line badges under the name cell are retired:
  - no apply-stage badge
  - no `收益率 > 6%` badge
  - no standalone `年化收益率` tag

### 97.3 Retired pin-expression rule
- The page must no longer visually express cb-rights-issue pinning through:
  - row highlight classes
  - name-cell badges
  - extra front-end `pinPriority` pre-sort
- Existing backend fields such as `pinPriority` may remain in the API for compatibility, but this round's page must not depend on them for visible grouping.

### 97.4 Phase-specific column rule
- All three subtabs continue using the same truthful source rows.
- Phase-specific visible columns must differ at least as follows:
  - `申购阶段` keeps `股权登记日`
  - `埋伏阶段` does not show `股权登记日`
  - `等待阶段` does not show `股权登记日`
- No additional `年化收益率` label/tag may be added in subtab header summaries.
- If `年化收益率` remains as a data column, its field meaning is unchanged.

### 97.5 Acceptance
- The public page visibly switches between the three subtabs.
- `正股名称` cells no longer contain a second line.
- The previous pinning highlight expression disappears.
- `股权登记日` appears only in `申购阶段`.

## 98. Phase CL: CB-rights-issue Issue-Scale Fix + Annualized Column Removal (2026-04-17)

- This round changes:
  - `data_fetch/cb_rights_issue/source.py`
  - `strategy/cb_rights_issue/service.py`
  - `presentation/dashboard/dashboard_page.js`
  - related live docs only
- This round does not change:
  - cb-rights-issue route path
  - cb-rights-issue response envelope
  - cb-rights-issue push grouping

### 98.1 Issue-scale semantic rule
- The truthful live issue-scale source is `amount / amountYi`.
- `issueScaleYi` must therefore mirror `amountYi`, not `cbAmountYi`.
- `cbAmountYi` may remain in the outward row for compatibility, but it is no longer the public `发行规模` field.
- Strategy fallback order is fixed to:
  - `issueScaleYi`
  - `amountYi`
  - `cbAmountYi`

### 98.2 Derived-ratio rule
- `issueRatio = issueScaleYi / stockMarketValueYi` remains unchanged as a formula.
- Only the numerator source changes to the truthful issue size above.

### 98.3 Page-visible annualized-column rule
- The three cb-rights-issue subtabs must not show a visible `年化收益率` column:
  - `申购阶段`
  - `埋伏阶段`
  - `等待阶段`
- `annualizedReturnRate` may remain present in the API for compatibility and non-page uses.
- Any default front-end sort for a tab must use a still-visible column after this removal.

### 98.4 Acceptance
- A live row such as `金杨精密 / 金杨转债` renders `issueScaleYi = 9.8`.
- The public page shows no `年化收益率` column anywhere inside cb-rights-issue subtabs.

## 99. Phase CM: CB-rights-issue Monitoring Retirement (2026-04-17)

- This round changes:
  - `strategy/cb_rights_issue/service.py`
  - `presentation/dashboard/dashboard_page.js`
  - `refactor_docs/001-monitor-refactor/contracts/dashboard-api-contract.md`
  - related live docs only
- This round does not change:
  - cb-rights-issue route path
  - cb-rights-issue source fetch inputs
  - cb-rights-issue phase grouping rule

### 99.1 Page-expression retirement rule
- The cb-rights-issue page must now express the feature only through the three phase groups:
  - `申购阶段`
  - `埋伏阶段`
  - `等待阶段`
- The page must not render:
  - `推送候选`
  - `独立推送`
  - any monitor-pool summary wording

### 99.2 Compatibility response rule
- `GET /api/market/cb-rights-issue` may keep the existing `monitorList` field for compatibility.
- Effective live semantic is now:
  - `monitorList = []`
  - `pushEligibleCount = 0`
- Existing compatibility fields such as `pushEligible`, `monitorEligible`, and `pinPriority` may remain in the row shape, but they no longer represent an active monitoring workflow for this module.

### 99.3 Push-dormant rule
- The independent push service stays wired for compatibility but must naturally skip delivery because `monitorList` is empty.
- No new page control for cb-rights-issue push settings should remain visible after this round.

### 99.4 Acceptance
- The public cb-rights-issue page shows only the three phase groups and their tables.
- The public page contains no `推送候选` or `独立推送`.
- `GET /api/market/cb-rights-issue` returns an empty `monitorList`.
