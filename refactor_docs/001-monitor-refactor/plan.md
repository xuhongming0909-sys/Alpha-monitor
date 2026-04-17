# Alpha Monitor 浜戞湇鍔″櫒 GitHub 鑷姩閮ㄧ讲璁″垝

**Date**: `2026-03-22`
**Feature**: `001-monitor-refactor`
**Related Docs**:
- [REQUIREMENTS.md](./REQUIREMENTS.md)
- [SPEC.md](./SPEC.md)

## 1. 鏈鐩爣

鏈鏂藉伐鍙В鍐充竴浠朵簨锛氭妸鈥滀簯鏈嶅姟鍣ㄥ凡缁忚繛涓?GitHub锛屼絾姣忔鎺ㄩ€佸悗杩樿鎵嬪姩鏇存柊鈥濇敹鍙ｆ垚姝ｅ紡鑷姩閮ㄧ讲閾捐矾銆?
瀹屾垚鍚庣洰鏍囩姸鎬佷负锛?
1. 浠撳簱鍐呭瓨鍦ㄦ寮忕殑 GitHub Actions 鑷姩閮ㄧ讲宸ヤ綔娴併€?2. 鏈嶅姟鍣ㄧ瀛樺湪缁熶竴鐨勬媺鍙栨洿鏂拌剼鏈€?3. 褰?`main` 鍒嗘敮鏀跺埌鏂版彁浜ゆ椂锛孏itHub 鍙互鑷姩閫氳繃 SSH 鐧诲綍鏈嶅姟鍣ㄥ苟鎵ц鏇存柊銆?4. 鏇存柊娴佺▼榛樿瀹屾垚锛?   - 鎷夊彇鏈€鏂颁唬鐮?   - 鍚屾 Node 渚濊禆
   - 妫€鏌?`alpha-monitor` 鏈嶅姟鏄惁瀛樺湪
   - 鑻ユ湇鍔″瓨鍦ㄥ垯鑷姩閲嶅惎
   - 杈撳嚭鍋ュ悍妫€鏌ョ粨鏋?5. 鑷姩閮ㄧ讲澶辫触鏃讹紝鏃ュ織鑳芥槑纭畾浣嶆槸 SSH銆佷唬鐮佸悓姝ャ€佷緷璧栧畨瑁呫€佹湇鍔￠噸鍚繕鏄仴搴锋鏌ュけ璐ャ€?
## 2. 鏈涓嶆敼鐨勫唴瀹?
鏈涓嶄富鍔ㄤ慨鏀逛互涓嬪唴瀹癸細

- 浠〃鐩?UI 甯冨眬
- AH / AB / 鍙浆鍊?/ 鐩戞帶濂楀埄涓氬姟鍏紡
- `/api/*` 瀵瑰璺敱
- 浜戞湇鍔″櫒棣栨鍩虹鐜瀹夎鏂瑰紡
- Nginx / Caddy 鐜版湁鍙嶅悜浠ｇ悊鏂规

濡傛灉瀹炴柦涓彂鐜板繀椤绘敼杩欎簺鍐呭锛屼細鍏堝洖鍒版枃妗ｉ樁娈甸噸鏂扮‘璁ゃ€?
## 3. 鐜扮姸鍒ゆ柇

褰撳墠宸茬‘璁ょ殑浜嬪疄锛?
1. 浜戞湇鍔″櫒鐩綍宸茶繛鎺?GitHub 浠撳簱锛屼富鐩綍涓?`/home/ubuntu/Alpha monitor`銆?2. 浠撳簱鍐呭凡缁忔湁 Linux 鍚姩銆乣systemd`銆丯ginx/Caddy 杈呭姪鑴氭湰銆?3. 浠撳簱涓凡缁忓瓨鍦?`.github/workflows/deploy.yml`锛屼絾褰撳墠瀹炵幇浠嶅寘鍚儴鍒嗘湇鍔″櫒渚у悓姝ラ€昏緫锛屽拰鈥滃伐浣滄祦鍙礋璐ｈЕ鍙戙€佹湇鍔″櫒鑴氭湰璐熻矗鎵ц鈥濈殑鐩爣鏈夊亸宸€?4. 鏈嶅姟鍣ㄤ笂鏄惁宸茬粡瀹夎 `alpha-monitor.service` 浠嶅彲鑳藉洜鏈哄櫒鐘舵€佷笉鍚岃€屼笉涓€鑷达紝鍥犳鑷姩閮ㄧ讲鑴氭湰蹇呴』鍏煎鈥滄湇鍔″凡瀹夎鈥濆拰鈥滄湇鍔℃湭瀹夎鈥濅袱绉嶆儏鍐点€?
## 4. 瀹炴柦鍋囪

鏈璁″垝閲囩敤浠ヤ笅榛樿鍋囪锛?
1. 姝ｅ紡鑷姩閮ㄧ讲鐩爣鍒嗘敮涓?`main`銆?2. GitHub Actions 浣跨敤 SSH 绉侀挜鐧诲綍鏈嶅姟鍣紝涓嶇洿鎺ユ毚闇叉湇鍔″櫒瀵嗙爜銆?3. 鏈嶅姟鍣ㄤ笂鐨勯」鐩洰褰曞浐瀹氫负 `/home/ubuntu/Alpha monitor`锛屼絾宸ヤ綔娴佸厑璁搁€氳繃鍙橀噺瑕嗙洊銆?4. 鑻ユ湇鍔″櫒宸茬粡瀹夎 `alpha-monitor` 鏈嶅姟锛屽垯鑷姩閮ㄧ讲鍚庨噸鍚鏈嶅姟锛涜嫢鏈畨瑁咃紝鍒欏彧鍚屾浠ｇ爜骞惰緭鍑烘彁閱掞紝涓嶅湪宸ヤ綔娴侀噷寮鸿鍒涘缓鏈嶅姟銆?5. 鑷姩閮ㄧ讲浼樺厛浣跨敤 `npm ci`锛涜嫢閿佹枃浠朵笉鍙敤鍐嶉€€鍥?`npm install`銆?
## 5. 鏂藉伐姝ラ

### Phase A: 鏂囨。鍚堝悓鏇存柊

鐩爣锛氬厛鎶?GitHub 鑷姩閮ㄧ讲鍐欒繘闇€姹備笌鎶€鏈悎鍚屻€?
璁″垝淇敼锛?
- `refactor_docs/001-monitor-refactor/plan.md`
- `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
- `refactor_docs/001-monitor-refactor/SPEC.md`
- `RUNBOOK.md`

瑕佽ˉ榻愮殑鍐呭锛?
1. 浜戞湇鍔″櫒蹇呴』鏀寔鈥滄帹閫佸埌 GitHub 鍚庤嚜鍔ㄦ洿鏂扳€濄€?2. 鑷姩閮ㄧ讲鍙 `main` 鍒嗘敮銆?3. 鑷姩閮ㄧ讲閾捐矾鍥哄畾涓衡€淕itHub Actions -> SSH -> 鏈嶅姟鍣ㄦ洿鏂拌剼鏈?-> 鏈嶅姟閲嶅惎 -> 鍋ュ悍妫€鏌モ€濄€?4. 闇€瑕佺殑 GitHub Secrets 鍚嶇О銆佹湇鍔″櫒鐩綍鍜屾湇鍔″悕瑕佸啓娓呮銆?
瀹屾垚鏍囧噯锛?
- 鏂囨。鑳界嫭绔嬭鏄庤嚜鍔ㄩ儴缃茶姹傘€佽竟鐣屽拰楠屾敹銆?
### Phase B: 鏈嶅姟鍣ㄦ洿鏂拌剼鏈惤鍦?
鐩爣锛氭彁渚涗竴涓湇鍔″櫒渚х粺涓€鍏ュ彛锛岃 GitHub Actions 鍜屼汉宸ユ帓闅滈兘璋冪敤鍚屼竴濂楅€昏緫銆?
璁″垝鏂板锛?
- `tools/deploy/update_from_github.sh`

鑴氭湰鑱岃矗锛?
1. 鍒囧埌椤圭洰鏍圭洰褰曘€?2. 鎵ц `git fetch --all` 鍜?`git reset --hard origin/main`銆?3. 鏍规嵁閿佹枃浠跺喅瀹氳繍琛?`npm ci` 鎴?`npm install`銆?4. 濡傛灉瀛樺湪 `alpha-monitor` 鏈嶅姟锛屽垯鎵ц閲嶅惎骞惰緭鍑虹姸鎬併€?5. 璋冪敤鏈湴鍋ュ悍妫€鏌ユ帴鍙ｏ紝澶辫触鏃惰繑鍥為潪闆堕€€鍑虹爜銆?
瀹屾垚鏍囧噯锛?
- 鍦ㄦ湇鍔″櫒鏈満鎵嬪姩鎵ц璇ヨ剼鏈紝鍙互瀹屾垚涓€娆″畬鏁存洿鏂般€?
### Phase C: GitHub Actions 宸ヤ綔娴佽惤鍦?
鐩爣锛氳 `main` 鍒嗘敮鎻愪氦鑷姩瑙﹀彂杩滅▼閮ㄧ讲銆?
璁″垝鏂板锛?
- `.github/workflows/deploy.yml`

宸ヤ綔娴佽亴璐ｏ細

1. 鐩戝惉 `main` 鍒嗘敮 push銆?2. 閫氳繃 GitHub Secrets 璇诲彇 SSH 杩炴帴鍙傛暟銆?3. 鍦?runner 涓婂噯澶?SSH 鐜銆?4. 杩滅▼鎵ц鏈嶅姟鍣ㄦ洿鏂拌剼鏈€?5. 鍦ㄦ棩蹇椾腑娓呮櫚鎵撳嵃閮ㄧ讲鐩爣涓绘満銆佺洰褰曘€佸垎鏀拰瀹屾垚鐘舵€併€?
瀹屾垚鏍囧噯锛?
- 宸ヤ綔娴佹枃浠跺湪浠撳簱鍐呭畬鏁村彲鐢ㄣ€?
### Phase D: 杩愯璇存槑琛ラ綈

鐩爣锛氭妸鈥滄€庝箞鍚敤鑷姩閮ㄧ讲鈥濆拰鈥滃嚭浜嗛棶棰樼湅鍝噷鈥濆啓鎴愭渶灏忓彲鎵ц璇存槑銆?
璁″垝淇敼锛?
- `RUNBOOK.md`

瑕佽ˉ榻愮殑鍐呭锛?
1. GitHub Secrets 鍒楄〃
2. 棣栨鏈嶅姟鍣ㄥ噯澶囨楠?3. 鎵嬪姩琛ユ晳鍛戒护
4. 鑷姩閮ㄧ讲澶辫触鍚庣殑鎺掗殰椤哄簭

瀹屾垚鏍囧噯锛?
- 鐢ㄦ埛鍙湅鏂囨。涔熻兘瀹屾垚鍓╀綑灏戦噺鎵嬪伐閰嶇疆銆?

### Phase E: 宸ヤ綔娴佽亴璐ｆ敹鍙ｄ笌涓€鑷存€т慨姝?
鐩爣锛氭妸 GitHub Actions 鑱岃矗鏀跺彛涓衡€滃噯澶?SSH + 瑙﹀彂鏈嶅姟鍣ㄧ粺涓€鏇存柊鑴氭湰鈥濓紝閬垮厤涓庤剼鏈€昏緫閲嶅銆?
璁″垝淇敼锛?
- `.github/workflows/deploy.yml`

瑕佷慨姝ｇ殑鍐呭锛?
1. 鍘婚櫎宸ヤ綔娴佷腑鐨?`git fetch/reset`銆佹湇鍔￠噸鍚瓑鏈嶅姟鍣ㄤ笟鍔￠€昏緫銆?2. 杩滅▼鍙墽琛?`tools/deploy/update_from_github.sh`锛屽苟閫氳繃鐜鍙橀噺浼犲叆鐩綍銆佹湇鍔″悕鍜屽垎鏀€?3. 鏃ュ織涓槑纭墦鍗伴儴缃查樁娈碉紝渚夸簬鍖哄垎 SSH 杩炴帴澶辫触涓庤剼鏈唴閮ㄥけ璐ャ€?
瀹屾垚鏍囧噯锛?
- 宸ヤ綔娴佸疄鐜颁笌 `REQUIREMENTS.md`銆乣SPEC.md` 鐨勮嚜鍔ㄩ儴缃插悎鍚屽畬鍏ㄤ竴鑷淬€?
## 6. 椋庨櫓涓庡鐞?
### 椋庨櫓 1锛氭湇鍔″櫒娌℃湁瀹夎姝ｅ紡鏈嶅姟

澶勭悊鏂瑰紡锛?
- 鑷姩閮ㄧ讲鑴氭湰涓嶇洿鎺ユ姤姝伙紝鑰屾槸鏄庣‘鎻愮ず鈥滀唬鐮佸凡鏇存柊锛屼絾鏈娴嬪埌 `alpha-monitor` 鏈嶅姟鈥濄€?- 缁х画淇濈暀宸叉湁 `install_systemd.sh` 浣滀负棣栨瀹夎鍏ュ彛銆?
### 椋庨櫓 2锛欸itHub Secrets 娌￠厤濂藉鑷磋繛鎺ュけ璐?
澶勭悊鏂瑰紡锛?
- 宸ヤ綔娴佷腑缁熶竴浣跨敤鍥哄畾鍙橀噺鍚嶃€?- 鏂囨。鏄庣‘瑕佹眰鏈€灏戝彧閰?4 椤癸細`SERVER_HOST`銆乣SERVER_USER`銆乣SERVER_PORT`銆乣SERVER_SSH_KEY`銆?
### 椋庨櫓 3锛氭湇鍔″櫒鐩綍甯︾┖鏍煎鑷?SSH 鍛戒护澶辫触

澶勭悊鏂瑰紡锛?
- 鎵€鏈夎繙绋嬪懡浠ら兘瀵圭洰褰曡矾寰勫姞鍙屽紩鍙枫€?- 鏈嶅姟鍣ㄨ剼鏈唴閮ㄨ嚜琛屽畾浣嶉」鐩牴鐩綍锛岄伩鍏嶅閮ㄥ懡浠ら噸澶嶆嫾鎺ュ鏉傝矾寰勩€?
## 7. 浜や粯缁撴灉

鏈瀹炴柦瀹屾垚鍚庯紝浜や粯鍐呭鍖呮嫭锛?
1. 鏇存柊鍚庣殑鑷姩閮ㄧ讲鏂囨。鍚堝悓
2. 鏈嶅姟鍣ㄧ缁熶竴鏇存柊鑴氭湰
3. GitHub Actions 鑷姩閮ㄧ讲宸ヤ綔娴?4. 鏈€灏忓惎鐢ㄨ鏄庝笌鎺掗殰璇存槑

## 8. 褰撳墠鐘舵€?
- 宸茶鍙栵細`CONSTITUTION.md`
- 鏈鏄惁闇€瑕佸厛鏇存柊 `REQUIREMENTS.md` 鍜?`SPEC.md`锛歚鏄痐
- 鏈鏄惁闇€瑕佸厛杈撳嚭鎴栨洿鏂?`plan.md`锛歚鏄紝宸插畬鎴恅
- 褰撳墠鏄惁宸茬粡杩涘叆瀹炴柦闃舵锛歚鏄紝鏂囨。鏇存柊鍚庤繘鍏ヤ唬鐮佸疄鏂絗


## 9. Phase F: One-shot Recovery Hardening (2026-03-22)

Goal: eliminate the recurring "service is running but homepage is old" deployment drift.

Planned script hardening in `tools/deploy/update_from_github.sh`:
1. Validate `config.yaml` syntax before install/restart.
2. Resolve `app.port` and force-release stale process owners on that port before service restart.
3. Keep systemd unit refresh as the single source of service startup path.
4. After health check, verify homepage markers:
   - expected marker exists: `dashboard_page.js`
   - forbidden legacy markers absent: `app.js|message-form`
5. Fail fast with clear deploy-stage logs when marker verification fails.
6. Convert single-shot health probe into retry-based readiness check with explicit retry logs.

Acceptance:
- Deployment fails instead of silently serving stale homepage content.
- Successful deployment guarantees local homepage contract consistency with dashboard entry.

## 10. Phase G: Compact UX + Push Reliability + Monitor Recoverability (2026-03-22)

Goal: complete one-shot refactor for three production pain points:
1. Compact list presentation on desktop without module-internal horizontal/vertical scrolling.
2. Push config read/write reliability and effective scheduled delivery.
3. Monitor arbitrage recoverability in cloud deploy (Python runtime + dependencies).

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` contracts first.
2. Refactor dashboard tables to "key columns + inline detail expansion + strong pagination".
3. Remove module-internal max-height scrolling and tighten spacing.
4. Harden API client JSON parsing and add uniform `/api/*` JSON 404 fallback.
5. Make push scheduler calendar mode explicit and set to daily execution.
6. Add deploy-stage Python dependency install and import verification.

Acceptance:
- Desktop 1920x1080 can read key list information without module-internal scrolling.
- `GET/POST /api/push/config` is stable, parseable, and UI state remains consistent after save + reload.
- Scheduler can execute on all weekdays and weekends when times match.
- `GET /api/monitors` no longer fails with `python not found` / `No module named akshare`.
- GitHub Actions deploy remains the single sync path to cloud server and finishes with health + marker checks.

## 11. Phase H: Subscription Date Simplification + Monitor UI Recovery + Global 50-row Pagination (2026-03-23)

Goal: finish one-shot correction for three current production regressions:
1. In the subscription table, remove the standalone `鎶界鏃 column and reuse `lotteryDate` as the displayed value for `涓缂存鏃.
2. Restore `鐩戞帶濂楀埄` to a stable, readable panel with the same table/pagination interaction as other modules.
3. Unify dashboard module tables to `50` rows per page instead of mixed `20` / unpaginated behavior.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first so page behavior and field semantics are explicit before coding.
2. Adjust the top subscription table contract:
   - keep today-stage judgment unchanged
   - remove the visible `鎶界鏃 header
   - `涓缂存鏃 column displays `lotteryDate`
3. Refactor monitor rendering to use the shared paginated table path, not a special simple table path.
4. Extend the shared table state so `鐩戞帶濂楀埄` / `鍒嗙孩鎻愰啋` / `鏀惰喘绉佹湁` also paginate at `50` rows per page.
5. Keep existing formulas unchanged and verify monitor calculations still match `SPEC.md`.
6. After implementation, run local checks, then push to GitHub and trigger the cloud-server auto-deploy path.

Acceptance:
- The subscription table no longer shows a `鎶界鏃 column.
- The visible `涓缂存鏃 column uses `lotteryDate` values consistently for IPO and bond rows.
- `鐩戞帶濂楀埄` renders successfully when `/api/monitors` returns data and supports 50-row pagination.
- `杞€哄鍒ー / `AH婧环` / `AB婧环` / `鐩戞帶濂楀埄` / `鍒嗙孩鎻愰啋` / `鏀惰喘绉佹湁` all use 50-row pagination.
- GitHub main branch and cloud deployment are updated to the latest implementation, and the latest webpage can be opened for verification.

## 11A. Phase H-2: Subscription Stage Alignment + Monitor Inline Editing (2026-03-23)

Goal: finish the remaining dashboard corrections from the latest user review:
1. `鑲″€烘墦鏂癭 must stop labeling bond rows as `浠婃棩涓缂存` on 2026-03-23 when the visible date column already shows 2026-03-20.
2. `鐩戞帶濂楀埄` must support adding new monitor items and editing existing monitor parameters from the dashboard.
3. `鐩戞帶濂楀埄` supplemental fields must render inline below each item, without a separate `璇︽儏` control column, and the wording must match real business terms.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first.
2. Align the subscription stage decision with the visible date contract:
   - the visible `涓缂存鏃 keeps using `lotteryDate`
   - the `浠婃棩涓缂存` stage judgment also switches to `lotteryDate`
3. Refactor the monitor panel into:
   - top editor area for create / edit
   - paginated monitor list
   - fixed inline parameter block under each item
4. Keep the existing `/api/monitors` contract and reuse `POST /api/monitors` for both create and update by carrying `id`.
5. Replace inaccurate monitor detail labels such as `鑲＄エ鑵垮叕寮廯 with wording that directly describes pricing inputs and calculation text.

Acceptance:
- On 2026-03-23, rows whose `lotteryDate` is not 2026-03-23 no longer appear as `浠婃棩涓缂存`.
- Dashboard users can create a new monitor item and edit an existing one without leaving the page.
- `鐩戞帶濂楀埄` no longer shows a separate `璇︽儏` header/button path; supplemental fields are shown directly below each item.
- Monitor inline wording matches the actual fields returned by the custom monitor strategy.

## 12. Phase I: Fresh Quotes + Dense Core Tables + Push Delivery Truthfulness (2026-03-23)

Goal: finish the current production correction for four user-visible issues in one round:
1. Dashboard manual refresh and first-screen critical market modules must converge to the latest available quotes in the same session instead of staying on stale cache snapshots.
2. `鏉烆剙鈧搫顨滈崚? / AH濠ь澀鐜?/ AB濠ь澀鐜痐 main tables must become denser and remove the visible `鐠囷附鍎廯 header/button path as the primary reading mode.
3. Convertible bond main table must surface the key parameters behind `閻炲棜顔戝┃顫幆閻?` directly in the default row, including `鏉烆剙鈧儤瀹氱捄灞界畽` / `濮濓綀鍋傚☉銊ㄧ┘楠?` / `60閺冦儲灏濋崝銊у芳` / `缁绢垰鈧搫鈧?` / `閻炲棜顔戞禒?` / `閸掔増婀＄粙搴″閺€鍓佹抄閻?`.
4. Push delivery state must stop lying: failed sends cannot be recorded as sent, and the UI/API must expose webhook readiness, scheduler mode, selected modules, and last success/failure details.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new cache-refresh, dense-table, and push-delivery contracts.
2. Keep the existing cache layer for fast first paint, but:
   - `閹靛濮╅崚閿嬫煀` must call force refresh for market datasets
   - if first dashboard load receives `servedFromCache` for critical quote modules, trigger one background force revalidation in the same session
   - UI copy must tell the user when a module is still showing cached data
3. Refactor `鏉烆剙鈧搫顨滈崚?` main table to remove the explicit detail column and move key metrics into main-row composite cells.
4. Refactor `AH / AB` main tables to follow the same dense-table principle and inline sample metadata instead of using the current detail-expansion path.
5. Harden push runtime recording:
   - record attempt time, success time, and latest error separately
   - only mark a schedule slot as sent after the downstream WeCom send succeeds
   - keep failed slots retryable on later scheduler ticks
6. Extend `GET /api/push/config` response and dashboard push status text so the user can see:
   - selected push modules
   - scheduler mode
   - webhook configured or missing
   - last main push / merger push success time
   - latest push failure reason when present
7. After implementation, run local verification, push to GitHub `main`, let GitHub Actions trigger the cloud deploy path, and open the latest webpage for final visual confirmation.

Acceptance:
- Clicking dashboard `閸掗攱鏌奰 fetches fresh market data instead of only replaying stale cache.
- If the initial dashboard render used cache for `exchangeRate / cbArb / ah / ab`, the page performs one background real-time revalidation and updates the visible values in the same visit.
- `濞村嘲鍎潪顒€鈧? 118008` on the refreshed page matches the latest backend snapshot instead of the previously stale `+3.61%` view.
- `鏉烆剙鈧搫顨滈崚?` main table shows key pricing / volatility / yield fields without a visible `鐠囷附鍎廯 column.
- `AH / AB` main tables use the same dense default-row pattern and no longer depend on the old detail-label path.
- Push scheduler no longer records failed sends as completed.
- `GET /api/push/config` and the dashboard push strip clearly reveal whether push is blocked by missing webhook configuration or by the last runtime failure.
- GitHub `main`, cloud deployment, and the latest public webpage are all updated to the new implementation.

## 13. Phase J: Premium History Sync Tolerance For Provider Outliers (2026-03-23)

Goal: recover `data_jobs` health without taking down the live dashboard when a small number of upstream historical-price requests fail for individual symbols.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first with the operational tolerance rule for premium-history incremental sync.
2. Keep full rebuild mode strict, but change update mode so a single-symbol upstream provider anomaly does not fail the whole batch when the local cache can continue serving the dashboard.
3. Restrict this tolerance to known fetch-layer per-symbol provider failures, and keep the failures visible in script output as warnings.
4. Avoid restarting the Node web service for this fix; let the next scheduler tick pick up the new script automatically.

Acceptance:
- `python tools/rebuild_premium_db.py --mode update` can return success while exposing warning details for a small number of provider-outlier symbols.
- `/api/health` can recover from `data_jobs = warn` to healthy on the next scheduler cycle when only non-fatal provider-outlier errors remain.
- The homepage remains reachable throughout the repair and verification process.
## 14. Phase K: Cloud Runtime Preservation + First-Install Proxy Closure (2026-03-23)

## 87. Phase CB-Call-Spread: Convertible Theoretical Pricing Replace Put Leg With Call Spread (2026-03-30)

Goal: replace the current convertible theoretical-pricing option leg with the newly confirmed strong-redeem call-spread model, and keep docs / backend / dashboard wording aligned in one round.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first so the old `bond+call` / `bond+call-put` wording is explicitly retired.
2. In `data_fetch/convertible_bond/source.py`, replace the current branch pricing with:
   - long American call at `convertPrice`
   - short American call at real `redeemTriggerPrice`
   - net option value floored at `0`
   - `theoreticalPrice = bondValue + netCallSpread`
3. Keep the current real `redeemTriggerPrice` resolution rule:
   - direct upstream field first
   - fallback to `convertPrice * redeemTriggerRatio`
4. Require truthful null output when any core pricing input is missing, especially when `redeemTriggerPrice` is absent.
5. Keep outward main-table fields stable:
   - `callOptionValue` becomes the net call-spread value
   - `putOptionValue` stays exposed only for compatibility and becomes `null`
6. Preserve internal verification fields for debugging:
   - `longCallOptionValue`
   - `shortCallOptionValue`
   - `callSpreadOptionValue`
   - `callStrike`
   - `redeemCallStrike`
   - `pricingFormula`
7. Update dashboard formula hint text so it explains:
   - `理论价 = 债底 + 净看涨价差价值`
   - `净看涨价差价值 = call(转股价) - call(强赎价)`
   - this wording is later superseded by Phase CI on 2026-03-30
8. Run targeted verification on the pricing helper and a minimal project check after implementation.

Acceptance:
- Existing `bond+call` / `bond+call-put` branch logic is no longer active in the live pricing path.
- Rows with real `redeemTriggerPrice` produce `callOptionValue = max(longCall - shortCall, 0)`.
- Rows missing `redeemTriggerPrice` now return truthful null `theoreticalPrice / theoreticalPremiumRate`.
- Dashboard explanatory text matches the new pricing formula.
- Non-theoretical fields such as `convertValue / premiumRate / weightedDiscountRate / pureBondValue` remain unchanged.

## 15. Phase L: Convertible / Rights-Issue Volatility Standard Switch To 250D HFQ (2026-03-30)

Goal: unify all currently effective convertible-bond theoretical-pricing volatility and cb-rights-issue option-pricing volatility to one truth standard: `250日年化后复权波动率`.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first so the active contract stops referring to `60日波动率` as the effective live standard for these two modules.
2. Change `config.yaml` so:
   - convertible-bond theoretical pricing uses `primary_vol_window = 250`
   - convertible-bond volatility windows are centered on `250`
   - convertible-bond underlying history retention is increased above the `251`-close floor
   - cb-rights-issue `volatility_window = 250`
   - cb-rights-issue dedicated stock-history retention is increased above the `251`-close floor
3. Keep the underlying-stock history source unchanged:
   - still use real A-share daily `后复权` history
   - still annualize by trading-day convention
   - still require at least `window + 1` closes
4. Update payload shaping and front-end read paths so the visible column/notes switch to `250日波动率`, while compatibility aliases may remain temporarily for older cached rows.
5. Rebuild the two pricing chains:
   - convertible-bond theoretical price
   - cb-rights-issue option value / expected return
6. Synchronize user-facing strategy notes so other Codex sessions do not keep reading the old `60日波动率` contract.

Acceptance:
- Convertible-bond theoretical pricing uses `250日年化后复权波动率`.
- cb-rights-issue expected-return calculation uses `250日年化后复权波动率`.
- Dashboard visible wording changes from `60日波动率` to `250日波动率` for the affected modules.
- Local history retention is safely above the `251`-close minimum for both modules.
- Contracts, config, code, and strategy docs no longer disagree on the active volatility window.

## 27. Phase X: Dashboard Render Recovery For Template/Script Drift (2026-03-24)

Goal: recover the public dashboard from a full-page render crash caused by template/script tab mismatch.

Plan:
1. Keep the current dashboard information architecture unchanged; this round is a runtime recovery fix, not a product-contract change.
2. Align `presentation/dashboard/dashboard_page.js` with the currently served dashboard template tab set.
3. Add null-safe panel activation so missing optional panels cannot crash the whole page render path.
4. Verify the public homepage and key APIs render again after the hotfix is synced.

Acceptance:
- Opening the public homepage no longer results in a blank or data-less dashboard caused by frontend initialization failure.
- `杞€哄鍒?/ AH / AB / LOF濂楀埄 / 鐩戞帶濂楀埄 / 鍒嗙孩鎻愰啋 / 浜嬩欢濂楀埄` tabs can switch normally.
- A missing or temporarily removed panel node does not crash `renderTabs()`.

Goal: make the cloud deploy path safe for long-term unattended operation by preserving runtime state and reducing first-install proxy drift.

Plan:
1. Remove runtime JSON state files from release-source expectations and document them as server-local state.
2. Keep deploy-script preservation in front of `git reset --hard` so automatic updates do not wipe monitor lists, push config, or runtime caches.
3. Strengthen the `systemd` service template with explicit working directory and `.env` loading.
4. Provide both nginx and Caddy installation scripts so first public rollout does not depend on manual copy-paste edits.

Acceptance:
- Automatic deployment no longer overwrites server-local `runtime_data/shared/*.json`.
- A fresh Ubuntu server can install either nginx or Caddy with a single repo script and expose the same homepage and `/api/health`.
- The managed service keeps loading from the project root after reboot and picks up `.env` overrides consistently.

## 15. Phase L: Daily Delisted Convertible Bond Exclusion (2026-03-23)

Goal: ensure the convertible-bond arbitrage page automatically removes bonds that are already delisted, ceased, or expired as of the current trading day, even when the page is still reading a previous cache snapshot.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first so the daily exclusion rule is explicit before code changes.
2. Keep the existing fetch-layer exclusion flag, but do not rely on it as the only truth source for dashboard output.
3. Add a strategy-layer daily filter for `/api/market/convertible-bond-arbitrage` that re-evaluates each row against the current Shanghai date on every response.
4. Exclude a row from the outward-facing list when:
   - `delistDate <= today`
   - or `ceaseDate <= today`
   - or `maturityDate < today`
5. Keep the existing API route and page structure unchanged; this round only corrects the daily visibility rule.

Acceptance:
- On any given day, the dashboard `杞€哄鍒ー page no longer shows bonds whose `delistDate` or `ceaseDate` is already that day or earlier.
- Matured bonds whose `maturityDate` is earlier than today are also removed from the visible list.
- The exclusion still works when the API response originated from an older cache payload, because the Node/service layer re-checks dates at response time.
## 16. Phase M: Event Arbitrage Unified Integration (2026-03-23)

Goal: replace the narrow `閺€鎯板枠缁変焦婀乣 dashboard tab with a broader `娴滃娆㈡總妤€鍩刞 module that uses external event-arbitrage data as the primary reading path while preserving the existing merger-announcement routes as auxiliary evidence.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first so the renamed module, sub-tabs, API contract, and zero-login first-phase scope are explicit before implementation.
2. Keep the top-level dashboard tab count fixed at 6, but rename the old `閺€鎯板枠缁変焦婀乣 tab to `娴滃娆㈡總妤€鍩刞.
3. Introduce a new aggregated API `GET /api/market/event-arbitrage` that returns:
   - overview cards
   - normalized category groups for `hk_private`, `cn_private`, `a_event`, `rights_issue`, and `announcement_pool`
   - per-source status metadata
4. Implement the fetch layer with direct public JSON requests to Jisilu for:
   - `hk_arbitrage_list`
   - `cn_arbitrage_list`
   - `astock_arbitrage_list`
5. Do not make Firecrawl part of the production hot path in phase 1; only document it as a future fallback if the public JSON interfaces disappear.
6. Keep `rights_issue` inside the API/model contract, but return it as disabled with empty rows in phase 1 because the current zero-login constraint disallows using the login-gated source.
7. Keep existing routes compatible:
   - `/api/market/merger`
   - `/api/merger/report`
   - `/api/merger/reports/today`
8. In the strategy layer, enrich external event rows with a lightweight exact-code match against the existing merger announcement pool, exposing:
   - latest matched announcement title
   - announcement date
   - PDF link
   - whether an AI report is already available
9. In the presentation layer, render `娴滃娆㈡總妤€鍩刞 with internal sub-tabs:
   - `閹槒顫峘
   - `濞擃垵鍋傜粔浣规箒閸?`
   - `娑擃厽顩ч懖锛勵潌閺堝瀵瞏
   - `A閼测€愁殰閸?`
   - `閸忣剙鎲″Ч?`
   - `濞擃垵鍋傛笟娑滃亗閺?瀵板懏甯撮崗?`
10. Keep the new module webpage-only in phase 1:
   - no push integration
   - no new AI summary generation for Jisilu rows
   - no changes to the existing merger push chain

Acceptance:
- The dashboard top tab label changes from `閺€鎯板枠缁変焦婀乣 to `娴滃娆㈡總妤€鍩刞.
- `GET /api/market/event-arbitrage` returns normalized real data for `hk_private`, `cn_private`, and `a_event`, plus `announcement_pool`, while `rights_issue` is present but explicitly disabled.
- The `娴滃娆㈡總妤€鍩刞 page defaults to `閹槒顫峘, not `閸忣剙鎲″Ч?`.
- External event rows can show matched announcement/PDF/report metadata without breaking when no match exists.
- Legacy merger endpoints stay compatible for existing callers and AI-report flows.
- A source failure in one external category degrades only that category and does not blank the whole page or the rest of the dashboard.

## 17. Phase N: Minimal Monitor Editor + Popup Entry (2026-03-23)

Goal: simplify `鐩戞帶濂楀埄` editing so the user only fills the smallest necessary business inputs, while the system auto-resolves the rest and keeps the editor hidden until explicitly opened.

Plan:
1. Update `REQUIREMENTS.md` and `SPEC.md` first.
2. Keep existing monitor runtime data and calculation output unchanged unless the user edits a value.
3. Keep the editor closed by default; clicking `鏂板鐩戞帶` or `缂栬緫` opens the editor.
4. Reduce the visible input set to:
   - `鏀惰喘鏂筦
   - `鐩爣鏂筦
   - `鎹㈣偂姣斾緥`
   - `瀹夊叏绯绘暟`
   - `鐜伴噾瀵逛环` + `甯佺`
   - `鐜伴噾閫夋嫨鏉僠 + `甯佺`
5. Hide implementation-oriented fields from the user-facing form, including:
   - code
   - market
   - share currency
   - optional generated monitor name
6. Add lightweight stock search confirmation under `鏀惰喘鏂筦 and `鐩爣鏂筦 so the user can see which security has been identified before saving.

Acceptance:
- `鐩戞帶濂楀埄` editor is not expanded by default when the panel opens.
- Clicking `鏂板鐩戞帶` expands the editor inline within the current panel instead of opening popup-style overlay UI.
- Clicking `缂栬緫` on an existing row opens the same inline editor with the current values filled in.
- The visible form includes `鎹㈣偂姣斾緥`.
- `鏀惰喘鏂筦 / `鐩爣鏂筦 inputs show resolved security info and candidate matches when auto-search runs.
- Existing monitor items can still be edited and saved without losing their stored hidden metadata.
## 18. Phase O: Startup Responsiveness + Premium History Self-Healing (2026-03-23)

Goal: remove the current "page waits too long" perception by fixing the broken data paths behind it, and make AH / AB premium history recover automatically when the SQLite cache degrades to a one-day snapshot.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first so the degraded-history recovery rule and IPO empty-state fallback are explicit before code changes.
2. Keep the existing cache-first dashboard strategy because cached quote endpoints are already fast enough for first paint.
3. Treat the following as production regressions that must self-heal instead of being silently skipped in incremental sync:
   - `premium_summary.sampleCount3Y <= 1`
   - missing `startDate3Y` / `endDate3Y` while samples exist
   - obviously collapsed short-range summaries that indicate the DB only retained a recent snapshot
4. In premium-history update mode, when the summary is degraded, force a full backfill for that symbol instead of doing the normal short incremental update window.
5. Change IPO data loading so "no stored history yet" returns a successful empty payload rather than HTTP 500 / `success: false`, because the dashboard should degrade to an empty table instead of looking broken.
6. After implementation, run server-side premium-history repair and verify `AH / AB` rows recover real multi-day sample ranges and non-null percentile values.

Acceptance:
- Normal cached dashboard quote endpoints remain fast for first paint.
- AH / AB no longer stay stuck at `sample 1 / same-day range` after the next repair cycle.
- Incremental premium-history update can detect a degraded cache and trigger full backfill for only the affected symbols.
- `/api/market/ipo` returns a parseable success payload with empty arrays when no IPO history is available yet.
- The homepage no longer looks "stuck loading" just because one optional data source currently has no stored history.

## 19. Phase P: Public CB Payload Slimming (2026-03-23)

Goal: fix the remaining homepage slow-open issue by shrinking the public `convertible-bond-arbitrage` response to the fields the dashboard actually renders.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the existing convertible-bond calculations unchanged.
3. Keep the route path unchanged:
   - `/api/market/convertible-bond-arbitrage`
4. Add a response-shaping step in the Node/service layer after row sanitization:
   - preserve the fields the dashboard uses for summary cards and dense main-table rendering
   - drop unused per-row fields that are inflating the payload by multiple megabytes
   - stop emitting duplicated public aliases for the same row collection and keep `data` as the single outward row array
5. Do not move this slimming into the raw Python fetch layer for this round; keep the raw fetch result available internally and only slim the outward-facing HTTP payload.

Acceptance:
- Public homepage no longer waits on a 6+ MB convertible-bond JSON payload.
- Cached `convertible-bond-arbitrage` HTTP response size is materially smaller than the current payload.
- Dashboard `杞€哄鍒ー main table and summary cards still render the same user-visible values after slimming.

- Public `convertible-bond-arbitrage` response no longer repeats the same rows in top-level `list` / `rows` aliases.

## 19. Phase P: Event Arbitrage UI Simplification (2026-03-23)

Goal: simplify the `浜嬩欢濂楀埄` reading path so the user lands directly on real category data, and A-share rows display only the core scraped content without forum links or expandable detail toggles.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first so the simplified event-arbitrage UI contract is explicit before frontend changes.
2. Remove the `鎬昏` sub-tab from the phase-1 `浜嬩欢濂楀埄` page, but keep the backend `overview` field in the API contract for internal aggregation and future use.
3. Change the default `浜嬩欢濂楀埄` sub-tab from `overview` to `a_event`.
4. Keep the existing visible sub-tabs as:
   - `A鑲″鍒ー
   - `娓偂濂楀埄`
   - `涓绉佹湁`
   - `娓緵濂楀埄`
   - `鏈€鏂板叕鍛奰
5. Remove the forum-link presentation from the `A鑲″鍒ー page even if the raw payload still contains a forum URL.
6. Rename the A-share official announcement link label from `鍏憡閾炬帴` to `瀹樻柟鍏憡`.
7. Remove expandable detail toggles from the `浜嬩欢濂楀埄` tables in this round.
8. Render A-share `鎽樿` directly below each row as an always-visible secondary detail block instead of an expandable detail area or a dedicated summary column.

Acceptance:
- The `浜嬩欢濂楀埄` page no longer exposes a `鎬昏` sub-tab.
- Opening `浜嬩欢濂楀埄` lands directly on `A鑲″鍒ー.
- `A鑲″鍒ー no longer renders `璁哄潧閾炬帴`.
- The A-share announcement link label is `瀹樻柟鍏憡`.
- Event-arbitrage tables no longer show `灞曞紑 / 鏀惰捣` controls.
- A-share rows show `鎽樿` directly below the main row using the existing detail-row visual style.

## 20. Phase Q: Constitution Alignment Audit And Guardrail (2026-03-23)

Goal: align the repository with the newly amended constitution using the smallest effective change set, and prevent future constitution drift from silently reappearing.

Plan:
1. Sync `CONSTITUTION.md` and `.specify/memory/constitution.md`, and update amendment metadata so the constitution contract is self-consistent again.
2. Treat this round as a governance-alignment change, not a broad architecture rewrite:
   - prioritize direct fixes with the shortest path
   - avoid mixing unrelated module refactors into the same round
   - record larger follow-up refactors separately if they are discovered during audit
3. Add a dedicated repo check for constitution drift:
   - compare the two constitution files as normalized UTF-8 text
   - fail with a clear diff preview when they diverge
   - expose the check through a stable command entry
4. Keep product behavior unchanged in this round unless a constitution violation requires a direct fix.

Acceptance:
- `CONSTITUTION.md` and `.specify/memory/constitution.md` stay synchronized after the amendment.
- Constitution version and amendment metadata reflect the 2026-03-23 change.
- The repository provides a one-command constitution sync check with non-zero exit on drift.
- This alignment round does not bundle unrelated product logic changes.

## 21. Phase R: Same-day Subscription Truthfulness + Invalid CB Exclusion + Dense CB Core Fields (2026-03-23)

Goal: fix three current user-visible regressions in one direct round:
1. `鑲″€烘墦鏂癭 must show today's real subscribe / lottery / listing items again, including current Beijing exchange IPO rows.
2. `杞€哄鍒ー must stop showing obviously invalid rows such as zero-price or zero-turnover bonds that have already entered the delist / cease / force-redeem end state.
3. `杞€哄鍒ー main table must surface the requested dense core parameters directly in the default row set.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the existing `鑲″€烘墦鏂癭 page structure, but repair the data truth path:
   - recognize Beijing exchange IPO codes correctly
   - do not keep trusting a fresh-looking empty cache snapshot when IPO history is still empty
   - redeploy the fixed IPO source so the live server can repopulate same-day rows
3. Harden `杞€哄鍒ー visible-row filtering in the strategy/service layer:
   - continue honoring delist / cease / maturity dates
   - additionally exclude clearly invalid end-state rows such as `price <= 0`
   - exclude zero-turnover rows that have already entered the terminal delist / cease / maturity chain
4. Expand the outward-facing CB payload whitelist only to the fields needed by the dense table contract.
5. Refactor the frontend CB main table to display the requested core fields directly, without reintroducing the old detail-button reading path.

Acceptance:
- Opening the dashboard on the live server can show today's IPO subscribe row again when the upstream source has one, including Beijing exchange rows.
- `鎭掗€歌浆鍊篳 and the other obviously invalid zero-price / terminal zero-turnover rows no longer appear in the visible CB list.
- `鑽?3杞€篳 and similar rows already in the terminal cease / delist chain are excluded from the visible CB list.
- The CB main table directly shows:
  - bond / stock identity and price-change fields
  - stock 3Y ROE and debt ratio
  - convert metrics
  - premium and pure-bond premium metrics
  - redeem / putback / volatility / option / theoretical / maturity-yield fields
  - listing / convert-start / maturity / rating fields

## 23. Phase T: CB Truth-source Yield + Formula Hint + Column Split Polish (2026-03-23)

Goal: finish the current convertible-bond dense-table round so the visible fields and source truthfulness match the latest user contract.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the existing theoretical-pricing engine unchanged for this round:
   - continue using `鐞嗚浠峰€?= 绾€轰环鍊?+ 鏈熸潈鐞嗚浠峰€糮
   - continue using `鏈熸潈鐞嗚浠峰€?= 鐪嬫定鏈熸潈浠峰€?- 鐪嬭穼鏈熸潈浠峰€糮
3. Refine the `杞€哄鍒ー main table rendering contract:
   - add `绾€轰环鍊糮 before `绾€烘孩浠风巼`
   - split `鐞嗚浠峰€糮 and `鐞嗚婧环鐜嘸 into two separate visible columns
   - add a page-visible formula hint instead of hiding the pricing鍙ｅ緞 only in code
4. Replace local `鍒版湡绋庡墠鏀剁泭鐜嘸 backfill with a real upstream field:
   - prefer Jisilu `bond_cb_jsl()` `鍒版湡绋庡墠鏀剁泭`
   - do not continue using a local approximation formula as the outward field value
5. Keep `ROE` and `璧勪骇璐熷€虹巼` on real upstream financial fetches only, and make that source contract explicit in docs:
   - allow Eastmoney bulk financial tables as the stable server-side fallback when THS / Sina endpoints fail
6. Redeploy and verify both the API payload and the public page.

Acceptance:
- `杞€哄鍒ー main table shows `绾€轰环鍊糮 immediately before `绾€烘孩浠风巼`.
- `鐞嗚浠峰€糮 and `鐞嗚婧环鐜嘸 render as separate columns.
- The page visibly explains the current `鐞嗚浠峰€糮 formula.
- `yieldToMaturityPretax` comes from a real upstream field and is no longer populated by the local fallback formula in this round.
- `stockAvgRoe3Y` and `stockDebtRatio` remain sourced from real upstream financial interfaces.

## 24. Phase U: Homepage Root-Module Cleanup (2026-03-24)

Goal: restore the stable homepage module contract, keep `LOF濂楀埄` as the visible fourth root tab, and reduce the active premium family back to `AH / AB`.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the cleaned homepage and premium contracts.
2. Keep homepage root navigation fixed at `7` modules, with `LOF濂楀埄` restored as the visible fourth root tab.
3. Remove abandoned premium experiments from public runtime scope:
   - no extra homepage root tab
   - no extra public market route
   - no extra historical-premium type
   - no scheduler/cache/bootstrap loading for removed datasets
4. Keep premium-history active contracts limited to `AH / AB`.
5. Keep LOF and existing premium modules stable:
   - `AH / AB` behavior unchanged
   - `LOF濂楀埄` remains accessible from the homepage
   - unrelated modules do not regress

Acceptance:
- Homepage root tabs remain `7`, and one visible tab is `LOF濂楀埄`.
- Premium-history active contracts remain limited to `AH / AB`.
- Existing `AH / AB / LOF濂楀埄 / 杞€?/ 鐩戞帶 / 鍒嗙孩 / 浜嬩欢濂楀埄` behavior does not regress.

## 26. Phase W: Event-arbitrage Detail Text Responsive Width Fix (2026-03-24)

Goal: fix the `浜嬩欢濂楀埄` detail-text layout so A-share `鎽樿` and HK/CN `澶囨敞` adapt to available screen width instead of being squeezed into the left quarter of the detail grid.

Plan:
1. Keep the data contract unchanged and only adjust presentation behavior.
2. Update the page contract docs first for the event-arbitrage detail-text layout.
3. Change the event-arbitrage detail renderers to use a single-column full-width detail block for:
   - A-share `鎽樿`
   - HK/CN `澶囨敞`
4. Add minimal CSS for a responsive single-column detail-grid variant, without changing other modules' shared detail layout.

Acceptance:
- `浜嬩欢濂楀埄` A-share `鎽樿` occupies the usable detail-row width instead of staying compressed on the left.
- `娓偂濂楀埄` and `涓绉佹湁` `澶囨敞` follow the same full-width responsive behavior.
- Other detail-grid based modules keep their existing layout.

## 26. Phase W: CB Yield Removal + Volatility Trust Warning (2026-03-24)

Goal: reduce false precision in the convertible-bond main table by removing the now-unwanted maturity-yield display and explicitly downgrading volatility-driven theoretical metrics to reference-only status.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the current backend theoretical-pricing calculation unchanged in this round:
   - do not silently swap the volatility engine yet
   - do not change the API field schema just because the page is hiding one column
3. Refine the `杞€哄鍒ー visible table contract:
   - remove `鍒版湡绋庡墠鏀剁泭鐜嘸 from the default visible columns
   - remove the same field from the default detail block
4. Clarify the trust boundary of the volatility-driven fields on the page:
   - `60鏃ユ尝鍔ㄧ巼` is the current historical annualized volatility estimate derived from recent equity closes
   - `鏈熸潈鐞嗚浠峰€?/ 鐞嗚浠峰€?/ 鐞嗚婧环鐜嘸 are reference values rather than execution-grade truth
5. Record the current volatility鍙ｅ緞 explicitly in docs so the next volatility-refactor round can replace it cleanly.

Acceptance:
- `杞€哄鍒ー page no longer displays `鍒版湡绋庡墠鏀剁泭鐜嘸.
- `60鏃ユ尝鍔ㄧ巼` and the volatility-derived theoretical metrics are visibly marked as historical/reference values on the page.
- The current volatility formula and trust boundary are documented.
## 29. Phase AA: Shared Dashboard Table Readability Upgrade (2026-03-24)

Goal: improve the readability of all dashboard long tables by upgrading shared presentation density, while keeping business meaning, sorting rules, pagination, and data pipelines unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the shared table-readability contract.
2. Keep this round strictly inside the presentation contract:
   - no fetch changes
   - no strategy calculation changes
   - no business-field meaning changes
3. Add minimum presentation config under `config.yaml > presentation.dashboard_table_ui` for:
   - desktop table font size
   - desktop header font size
   - desktop line height
   - desktop cell padding
   - tablet table font size
   - table-kind min widths
4. Add a light read-only endpoint `GET /api/dashboard/ui-config` so the static dashboard page can consume presentation config instead of hardcoding table density.
5. Keep the shared table renderer as the only main entry:
   - continue using `renderPaginatedTable()`
   - continue using `renderSimpleTable()`
   - do not fork separate table frameworks by module
6. Refine shared table rendering and CSS:
   - increase table text size and line height on desktop
   - enlarge header/body padding
   - keep sticky headers, sorting, pagination, and expand details unchanged
   - use per-table-kind min-width rules instead of relying only on `table-layout: fixed`
   - add clearer row separation and tabular-number alignment
7. Keep mobile safe:
   - only limited font growth under narrow breakpoints
   - continue using existing horizontal scroll containers when needed
   - do not introduce a second mobile-only table layout in this round

Acceptance:
- Desktop table text is visibly larger than the current `12px` baseline.
- Shared table renderers remain the primary rendering path for dashboard tables.
- `GET /api/dashboard/ui-config` returns the active table UI contract from config.
- Sorting, pagination, detail expansion, and field semantics remain unchanged.
- Desktop may use light controlled horizontal scrolling, but the page does not collapse on tablet/mobile widths.

## 30. Phase AB: Repository-local mini-SWE-agent Integration (2026-03-24)

Goal: embed a production-safe `mini-SWE-agent` helper path into the repository so agent execution can follow the same constitution-first workflow as Codex, without introducing a second parallel process.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the repository-local agent-assist contract.
2. Keep this round lightweight and tooling-only:
   - no runtime dashboard/API behavior changes
   - no deployment behavior changes
   - no background scheduler changes
3. Add a repository-owned prompt/task generator under `tools/` so `mini-SWE-agent` receives:
   - constitution-first instructions
   - plan/requirements/spec gate reminders
   - module-boundary rules
   - validation command defaults
4. Expose the helper through a stable local command entry from `package.json`.
5. Add a project-local usage guide that explains:
   - install steps
   - recommended `confirm` mode
   - how Codex and `mini-SWE-agent` should split work
   - example commands for `presentation`, `data_fetch`, and `strategy` scoped tasks
6. Keep the integration human-in-the-loop:
   - the tool generates repository-safe task text
   - it does not auto-run `mini-SWE-agent`
   - document/code review remains external to this helper

Acceptance:
- The repository contains a reusable local command that can generate a `mini-SWE-agent` task prompt for this project.
- The generated prompt explicitly reminds the agent to read `CONSTITUTION.md` first and stop for doc updates when contracts change.
- The repository contains a concise usage tutorial for installing and using `mini-SWE-agent` with this project.
- The integration does not alter the live dashboard, API routes, scheduler, or deployment flow.

## 31. Phase AC: Push Refactor to Summary + Event Alerts (2026-03-24)

Goal: replace the old `涓绘帹閫?+ 鏀惰喘绉佹湁涓撴姤` structure with a cleaner `瀹氭椂鎽樿 + 寮傚姩鎻愰啋` model that is easier to read, easier to validate, and closer to real decision needs.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and `contracts/dashboard-api-contract.md` first.
2. Retire the old merger-report push path from active push settings and scheduler flow:
   - remove the third push-time input from the homepage
   - remove merger-report push status from `GET /api/push/config`
   - stop exposing merger-report push as an active push route
3. Keep two push entrances only:
   - fixed-time summary push
   - event-driven alert push
4. Update push settings UI and API contract:
   - keep two summary times
   - add one editable event-alert cooldown minutes field
   - show summary push status and event-alert status separately
5. Rebuild summary push content into a denser readable format:
   - keep `鍙浆鍊?/ AH / AB / 鎵撴柊 / 鍒嗙孩 / 鑷畾涔夌洃鎺?/ 浜嬩欢濂楀埄鏂板娆℃棩姹囨€籤
   - keep `鑷畾涔夌洃鎺 full-volume
   - compress each row into scanable single-line or two-line Markdown
6. Add first-phase event alert logic for convertible bonds only:
   - trigger when `杞偂婧环鐜?< -3%`
   - enforce per-bond cooldown with default `30` minutes
   - alert payload must include only triggered rows, not the full summary
7. Track event-arbitrage newly discovered rows in push runtime state so the next day's fixed-time summary can include a concise `鏄ㄦ棩鏂板浜嬩欢濂楀埄` section.
8. After implementation, run local checks, sync the cloud server, set the public push HTML URL if missing, and verify the webpage plus push-config API online.

Acceptance:
- Push settings no longer contain `鏀惰喘绉佹湁涓撴姤`.
- The dashboard shows `2` summary time inputs and `1` alert cooldown input.
- `GET /api/push/config` returns summary times, alert cooldown, and separate summary/alert delivery status.
- Scheduled push content becomes visibly more concise and readable.
- Event alerts send only convertible-bond trigger rows with `杞偂婧环鐜?< -3%`.
- The same bond is not re-alerted within `30` minutes.
- Event-arbitrage rows first discovered on day `D` can appear in the summary push on day `D+1`.

## 31. Phase AC: Dashboard UI Density + Hierarchy Coordination (2026-03-24)

Goal: improve dashboard aesthetics, information density, and reading hierarchy together, while keeping all current behavior, data contracts, and interaction semantics unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with a presentation-only contract.
2. Keep this round strictly inside the dashboard presentation layer:
   - no `/api/*` contract changes
   - no strategy / formula changes
   - no scheduler / push behavior changes
   - no route restructuring
3. Apply the smallest effective UI changes in:
   - `presentation/templates/dashboard_template.html`
   - `presentation/dashboard/dashboard_page.js`
4. Improve first-screen efficiency by tightening:
   - hero height
   - section spacing
   - tab strip height
   - push strip height
5. Improve module readability by tightening and reordering visible emphasis for:
   - title
   - key counts / update time / freshness state
   - summary cards
   - explanatory copy
6. Keep mobile and tablet safe:
   - preserve the current responsive structure
   - only compress spacing and hierarchy
   - do not create a second mobile-only interaction model
7. Keep all edits annotated with concise Chinese comments when changing core layout or key style behavior.

Acceptance:
- The page shows more effective information within the first screen on desktop.
- Key module metadata is easier to scan than before.
- Summary areas are more compact without reducing data truthfulness.
- Existing tabs, tables, sorting, pagination, push settings, and monitor editing behavior remain unchanged.

## 32. Phase AD: Release-path Visibility + Fast Deploy (2026-03-24)

Goal: shorten the real path from `local change -> GitHub -> server -> visible homepage`, and make every stage truthfully expose which version is actually online.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the release-visibility and fast-deploy contracts.
2. Extend `/api/health` so it exposes deployment/version metadata from the actual running checkout, instead of only generic process health.
3. Add homepage-visible version text so the user can directly confirm:
   - current git short SHA
   - current branch
   - current app version
   - current server start time
4. Keep the current full deploy path as the default safe path:
   - `push main -> GitHub Actions -> update_from_github.sh`
5. Add a separate fast deploy wrapper for dependency-unchanged releases:
   - still performs git sync
   - still performs service restart
   - still performs health check
   - still performs homepage marker verification
   - skips Node/Python dependency installation and Python import verification by default
6. Allow GitHub Actions manual dispatch to select `full` or `fast`, while normal `push main` keeps using `full`.
7. Keep this round minimal and deployment-focused:
   - no change to market-data formulas
   - no change to scheduler business rules
   - no change to module ordering or routing semantics

Acceptance:
- `/api/health` returns parseable version metadata from the running service.
- Homepage visibly shows the currently deployed version instead of forcing the user to infer from behavior.
- Repository contains a dedicated fast-deploy entry script for dependency-unchanged updates.
- GitHub manual deploy can choose `fast` mode, while `push main` remains the safe full deploy path.
- Fast deploy still fails loudly if health check or homepage marker verification fails.
- The implementation remains limited to minimal front-end presentation changes.

## 33. Phase AE: Governance Rollback + Config-driven Access Entry (2026-03-24)

Goal: cancel the newly introduced `PROJECT_*` root-doc requirement and repair the homepage access entry so it no longer hardcodes `127.0.0.1:5000`.

Plan:
1. Keep this round minimal and split into one governance rollback plus one access-entry truthfulness repair.
2. Governance rollback:
   - remove the new `PROJECT_PLAN.md / PROJECT_REQUIREMENTS.md / PROJECT_TECH_STACK.md` requirement from `CONSTITUTION.md`
   - keep the existing repository workflow gate centered on `refactor_docs/001-monitor-refactor/plan.md / REQUIREMENTS.md / SPEC.md`
   - delete the temporary root-level `PROJECT_*` entry files added only for the now-cancelled rule
3. Access-entry repair:
   - update contracts first in `REQUIREMENTS.md` and `SPEC.md`
   - stop hardcoding `http://127.0.0.1:5000` in the root `index.html`
   - expose a lightweight runtime access-info API from the Node server
   - let the root entry page render the real configured service/public URL at runtime when served by the app
   - when `index.html` is opened directly as a local file, do not provide local preview; instead clearly guide the user to the configured cloud public URL
4. Keep this round narrow:
   - no market-data formula changes
   - no scheduler behavior changes
   - no module layout refactor

Acceptance:
- `CONSTITUTION.md` and `.specify/memory/constitution.md` no longer require `PROJECT_PLAN.md / PROJECT_REQUIREMENTS.md / PROJECT_TECH_STACK.md`.
- The temporary root-level `PROJECT_*` files are removed from the active repository surface.
- The root `index.html` no longer displays or links to a hardcoded `http://127.0.0.1:5000`.
- The access entry page shows the real runtime service URL when opened through the running app.
- Direct local-file open no longer provides local preview and instead directs the user to the cloud runtime path.

## 34. Phase AF: Cloud-only Runtime Surface (2026-03-24)

Goal: align the repository with the new rule that Alpha Monitor is officially a cloud-only runtime and no longer provides a local operator-facing access path.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the cloud-only runtime contract.
2. Keep developer-only local validation capability (`npm run dev`) for coding and checks, but stop treating any Windows-local helper path as an official runtime surface.
3. Remove repository-level local stable-runtime entrypoints and task installers that were previously used to keep a Windows-local service alive.
4. Replace the root `index.html` access page so it points users to the configured cloud public URL and health endpoint instead of local preview/service guidance.
5. Remove local-preview and local-service wording from dashboard user-facing copy where it implies the product should be opened from a local machine.
6. Update `RUNBOOK.md` and `quickstart.md` so they distinguish:
   - cloud runtime = official/long-term
   - local run = development validation only

Acceptance:
- The repository no longer exposes Windows-local stable-runtime commands as official package scripts.
- Local watcher/task helper files are removed from the active runtime surface.
- The root access page no longer offers local preview or local service start guidance.
- User-facing dashboard copy no longer tells the operator to confirm a local service.
- Docs consistently state that official access is through the cloud public URL only.

## 35. Phase AG: Local Push-scheduler Suppression (2026-03-24)

Goal: prevent accidental local startup from triggering repeated push failures when the runtime is still a loopback-only development instance.

Plan:
1. Keep this round minimal and runtime-scoped:
   - no deploy-flow change
   - no push content change
   - no webhook contract change
2. Treat loopback-only access configuration as a local/development runtime for push purposes.
3. When the effective public base URL resolves to loopback/localhost, suppress the push scheduler instead of attempting timed sends.
4. Keep cloud/public runtimes unchanged so the server still performs scheduled pushes normally.
5. Reflect the suppression truthfully in health and push-delivery status instead of surfacing repeated missing-webhook errors.

Acceptance:
- Local startup with `127.0.0.1`/`localhost` public URL no longer logs repeated `鏈厤缃?WECOM_WEBHOOK_URL` scheduled-push failures.
- Cloud runtime with a real public URL keeps scheduled push behavior unchanged.
- `/api/health` and push delivery status clearly show that local push scheduling is intentionally disabled rather than degraded.

## 35. Phase AG: Core Cloud-env Sync From Server Profile (2026-03-24)

Goal: make cloud runtime core parameters syncable from the repository-local server profile, so later Codex sessions can directly push the latest webhook/public URL class parameters to the server without asking again.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the cloud-env-sync contract.
2. Keep this round limited to deployment/config sync only:
   - no market-data fetch changes
   - no dashboard behavior changes
   - no push rule changes
3. Add a repository-owned sync script that:
   - reads `ops/server_profile.local.yaml`
   - derives the authoritative remote env values for core parameters
   - writes them into the configured remote `.env`
   - optionally restarts the managed service and checks health
4. Expose a stable local command entry so future Codex sessions can call the same path directly.
5. Keep precedence explicit:
   - server profile public URL is the source of truth for `PUBLIC_BASE_URL` and push HTML URL class fields
   - server profile webhook is the source of truth for `WECOM_WEBHOOK_URL`
   - effective local config may continue supplying other env-backed secrets when present
6. After implementation, execute one real sync against the configured cloud server and verify health.

Acceptance:
- Repository contains a stable cloud-env sync command.
- The command reads `ops/server_profile.local.yaml` instead of requiring re-entry of host/password/webhook/public URL.
- The command can update the remote `.env` keys for webhook/public URL style core parameters.
- When the sync changes effective values, the managed service is restarted and the health check passes.
- A later Codex session can reuse the same stored parameters and command path directly.

## 36. Phase AH: Core-table Concentration + Dividend Watchlist Merge (2026-03-24)

Goal: finish the latest dashboard usability corrections without changing existing route semantics or business formulas.

Plan:
1. Keep this round minimal and presentation-first:
   - no new page
   - no unrelated refactor
   - keep existing sorting / pagination / route semantics
2. Clarify convertible-bond volatility wording and visibility:
   - `60鏃ユ尝鍔ㄧ巼` remains an existing real field
   - wording must reflect historical K-line based real-data calculation
   - the column stays in the default main-reading area
3. Improve wide-table readability so more core fields stay in the first screen:
   - prioritize core convertible fields in earlier columns
   - reduce unnecessary horizontal padding / min-width inflation
   - allow content-aware width squeezing when columns are many
   - keep tables auto-adapting to container width when columns are fewer
4. Fix premium top-summary behavior:
   - `AB婧环` top summary must stay anchored to `婧环鐜囧墠涓?/ 鍊掓暟鍓嶄笁`
   - it must not switch to `杩戜笁骞村垎浣峘 just because the table sort column changed
5. Repair dividend watchlist source coverage:
   - the dividend page must include the user鈥檚 existing selected stocks
   - current dividend portfolio and existing custom-monitor stock selections must be merged into one read path
   - duplicate codes must be de-duplicated

Acceptance:
 - `60鏃ユ尝鍔ㄧ巼` is visibly present in the convertible main table and the page copy states it comes from historical K-line real data.
 - Convertible core columns require less horizontal sliding than the previous version.
 - Wide tables squeeze column usage when fields are many, but still stretch naturally when fields are fewer.
 - `AB婧环` top summary always shows premium top/bottom leaders.
 - Dividend page shows the previously selected watchlist rows instead of only the standalone dividend portfolio file.

## 37. Phase AI: Subscription Payment-day Truth Fix (2026-03-24)

Goal: repair the top subscription table so `浠婃棩涓缂存` reflects the real payment day instead of incorrectly using the lottery-announcement day.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the corrected payment-day contract.
2. Keep this round minimal and scoped to the subscription display path:
   - no data-fetch source change
   - no API route shape change
   - no unrelated dashboard refactor
3. Correct the page rule:
   - `浠婃棩涓缂存` must be triggered by `paymentDate = today`
   - the visible `涓缂存鏃 column must display `paymentDate`
   - `lotteryDate` must no longer masquerade as `涓缂存鏃
4. Keep the existing 鈥滀笉鍗曠嫭鏄剧ず鎽囧彿/涓鍏憡鍒椻€?rule, but restore truthful wording and matching dates.
5. Verify against live 2026-03-24 subscription data that multiple IPO payment rows appear instead of the current single wrong hit.

Acceptance:
- On 2026-03-24, the top subscription table no longer labels `闅嗘簮鑲′唤` as `浠婃棩涓缂存`.
- The same table includes the real 2026-03-24 payment rows such as `鐩涢緳鑲′唤`銆乣鎱ц胺鏂版潗`銆乣娉伴噾鏂拌兘`.
- The visible `涓缂存鏃 column matches the same `paymentDate` field used by the stage judgment.

## 38. Phase AJ: Dashboard Module Footnotes (2026-03-24)

Goal: add a unified explanatory footnote block at the end of each feature page so users can directly see data sources, formulas, and strategy notes.

Plan:
1. Keep this round strictly inside the presentation/config contract:
   - no data-source switching
   - no formula-result changes
   - no new route family
2. Update `REQUIREMENTS.md` and `SPEC.md` first.
3. Add config-driven footnotes under `config.yaml > presentation.dashboard_module_notes` for:
   - `subscription`
   - `cbArb`
   - `ah`
   - `ab`
   - `monitor`
   - `dividend`
   - `merger`
4. Extend existing `GET /api/dashboard/ui-config` so it also returns normalized module-footnote config.
5. Add one shared dashboard renderer with fixed section order:
   - `数据来源`
   - `计算公式`
   - `策略说明`
6. Render the shared footnote block at the end of:
   - top `股债打新`
   - all six main tab modules

Acceptance:
- Each feature page ends with a readable note block.
- Note content is driven from `config.yaml` through `GET /api/dashboard/ui-config`.
- Empty note sections auto-hide.
- Existing tables, summary cards, sorting, pagination, and calculation results remain unchanged.

## 37. Phase AI: DB-authoritative Convertible Volatility Fix (2026-03-24)

Goal: correct the convertible-bond volatility calculation so the visible `60鏃ユ尝鍔ㄧ巼` is truly computed from the local historical K-line database with the right sample window, without letting the sync path silently trim away the needed price history.

Plan:
1. Keep this round narrow and calculation-focused:
   - no dashboard layout change
   - no route semantic change
   - no unrelated refactor
2. Fix the realized-volatility sample window:
   - `20/60/120鏃ユ尝鍔ㄧ巼` must use the most recent `20/60/120` close-to-close log-return observations
   - this requires at least `window + 1` closes from the local price-history database
   - the current off-by-one return window must be removed
3. Fix the historical-price sync trust boundary:
   - the local `stock_price_history.db` remains the authoritative source for volatility reads
   - sync may append or backfill missing rows, but must not prune each symbol back down to a tiny rolling slice that destroys the established history library
4. Align missing-data hydration with the corrected window:
   - inline fallback hydration only fills when the database lacks the minimum close count required for volatility calculation
   - once the database already has enough rows, volatility calculation reads directly from the database result
5. After implementation, verify one or more live symbols by:
   - reading the closes from `stock_price_history.db`
   - recomputing the latest `60鏃ユ尝鍔ㄧ巼`
   - confirming the API payload matches the database-derived result

Acceptance:
- `60鏃ユ尝鍔ㄧ巼` uses `60` recent log-return samples rather than `59`.
- The volatility read path requires `window + 1` closes from `stock_price_history.db`.
- Convertible-bond history sync no longer prunes the established stock K-line library down to `120` rows per symbol.
- Manual database recomputation for a sample symbol matches the API payload.

## 38. Phase AJ: Full CB History Sync + Real Example Note (2026-03-24)

Goal: after the full underlying-stock history sync is completed, refresh convertible-bond theoretical metrics together and show one real on-page example explaining how a theoretical price is formed.

Plan:
1. Keep this round narrow:
   - no route change
   - no unrelated UI refactor
2. Run full underlying-stock HFQ history sync for convertible-bond symbols so the local history database is complete enough for all current volatility windows.
3. Rebuild the convertible-bond dataset after history sync so option-theoretical metrics and theoretical-price fields are refreshed from the updated volatility inputs.
4. Replace the generic convertible note text with a real example row from the current dataset:
   - use one actual bond / stock pair from live data
   - show the actual formula branch and actual numbers used in the displayed theoretical-price reference field
5. Verify cloud output after deploy by checking one sample row through the public API.

Acceptance:
- Full HFQ stock-history sync is executed for convertible-bond underlyings.
- Convertible theoretical metrics are refreshed after the history sync.
- The page note shows one real current example instead of only abstract wording.

## 39. Phase AK: Convertible Volatility Percent Display Alignment (2026-03-24)

Goal: keep the newly added real-example note accurate by aligning the convertible-bond volatility display with the actual data unit used by the API payload.

Plan:
1. Keep this round presentation-only:
   - no route change
   - no data recalculation change
   - no unrelated layout refactor
2. Treat `volatility60` / `annualizedVolatility` as ratio values in the front end:
   - payload example `0.3491` must display as `34.91%`
   - do not keep the current direct-percent formatting that renders `0.35%`
3. Apply the same display rule consistently in:
   - the main `60鏃ユ尝鍔ㄧ巼` column
   - the real example note at the bottom of the convertible-bond page
4. Re-verify the public page payload after deploy with one real row example.

Acceptance:
- The convertible-bond table no longer shows ratio-form volatility as `0.xx%`.
- The bottom real example note uses the correct human-readable volatility percentage.
- Existing volatility sort order and theoretical-price calculation remain unchanged.

## 40. Phase AL: Scheduled Push Truth Recovery (2026-03-24)

Goal: repair the scheduled WeCom push chain so a dirty runtime-state record cannot suppress a due cloud push, and make future diagnosis possible through truthful runtime status and explicit scheduler logs.

Plan:
1. Keep this round narrow and push-only:
   - no summary module content change
   - no dashboard route shape change
   - no market-data formula change
2. Harden the scheduled-slot trust rule:
   - scheduled push must no longer trust raw `mainPushRecords` blindly
   - for the current Shanghai date, recorded scheduled slots are only trusted when they are part of the active schedule and are backed by the latest same-day success timestamp
   - stale or impossible future slots in runtime state must be pruned before due-slot judgment
3. Preserve the existing success boundary:
   - a slot is marked sent only after downstream WeCom delivery succeeds
   - failed sends remain retryable on later scheduler ticks
4. Add explicit scheduler observability:
   - log when a scheduled slot is evaluated, skipped because it is not due yet, skipped because it is already truthfully sent, attempted, succeeded, or failed
   - log enough slot/date context to diagnose future `08:00`-style misses from `journalctl`
5. Keep the repair cloud-safe:
   - runtime-state self-healing may rewrite only the push scheduler's own persisted state
   - no reset of unrelated event-alert or dataset caches
6. After implementation:
   - verify locally with a dirty-state example where `mainPushRecords` already contains `08:00` but the latest success time is before `08:00`
   - deploy to the cloud server
   - verify health and push config status from the live public API

Acceptance:
- A current-day stale `mainPushRecords` entry such as `08:00` no longer suppresses the real `08:00` scheduled push when the latest same-day success time is earlier than `08:00`.
- Future scheduled times accidentally present in runtime state are pruned instead of being trusted.
- Scheduler logs clearly show slot attempt / success / failure context in `journalctl -u alpha-monitor`.
- Manual push remains available and does not falsely mark scheduled slots as already delivered.

## 41. Phase AM: Convertible Underlying ATR + Liquidity Fields (2026-03-25)

Goal: add four real-data fields to the convertible-bond main list so the user can directly judge underlying volatility and liquidity without opening other pages: `姝ｈ偂ATR(杩?0鏃?`銆乣鍓╀綑瑙勬ā(浜?`銆乣姝ｈ偂杩?0鏃ュ钩鍧囨垚浜ら(浜?`銆乣姝ｈ偂杩?鏃ュ钩鍧囨垚浜ら(浜?`.

Plan:
1. Keep this round narrow and cb-arb-only:
   - no push behavior change
   - no AH / AB / subscription route change
   - no theoretical-price formula change
2. Extend the underlying-stock history authority so the local history store can hold the real fields needed for ATR and turnover averages:
   - HFQ close
   - HFQ high
   - HFQ low
   - daily鎴愪氦棰?3. Use the same underlying-stock history chain to calculate:
   - `stockAtr20`
   - `stockAvgTurnoverAmount20Yi`
   - `stockAvgTurnoverAmount5Yi`
4. Keep `remainingSizeYi` as the existing real-data field, but move it into the visible convertible main table instead of leaving it only in the secondary info area.
5. Extend the public cb-arb payload contract and dashboard columns together.
6. Verify with a live sample row that the new fields appear in `/api/market/convertible-bond-arbitrage` and on the page.

Acceptance:
- The convertible-bond main table visibly adds `姝ｈ偂ATR(杩?0鏃?`銆乣鍓╀綑瑙勬ā(浜?`銆乣姝ｈ偂杩?0鏃ュ钩鍧囨垚浜ら(浜?`銆乣姝ｈ偂杩?鏃ュ钩鍧囨垚浜ら(浜?`.
- New ATR / average-turnover fields come from real underlying-stock history data rather than placeholders.
- Existing volatility / premium / theoretical-price fields remain unchanged.

## 42. Phase AN: Convertible Discount Strategy Replacement + Monitor Card (2026-03-25)

Goal: replace the old convertible-bond premiumRate < -3% event-alert rule with the new discount strategy, and replace the current 转股套利候选 summary card with a live 折价监控 card that shows the full monitored list.

Plan:
1. Update plan.md, REQUIREMENTS.md, and SPEC.md first with the new discount-strategy contract.
2. Keep this round focused on the convertible-bond strategy / push / page chain:
   - no AH / AB formula change
   - no subscription rule change
   - no dividend / monitor / merger business change
3. Replace the old negative-premium event alert:
   - stop using convertPremiumLt = -3 plus cooldown as the production rule
   - switch to 买入提醒 + 卖出提醒 + 监控名单定时推送
   - use threshold crossing rather than cooldown-based repeat suppression
4. Implement the strategy fields on top of real cb-arb rows:
   - discountRate = -premiumRate
   - stockAtr20 keeps the real-data definition vg(TR[-20:])
   - stockAtr20Pct = stockAtr20 / stockPrice * 100
   - trCoefficient / sellPressureCoefficient / oardCoefficient
   - weightedDiscountRate
5. Add independent runtime state for the strategy:
   - monitored bonds
   - prior buy/sell-zone state
   - latest buy / sell / monitor-push success and error metadata
6. Extend the public cb-arb payload and dashboard together:
   - main rows expose the new discount fields
   - the old 转股套利候选 top card is replaced by 折价监控
   - the card shows the full current monitor list rather than only top 3
7. Simplify push settings UI:
   - remove the old 异动冷却(分钟) input
   - remove old -3% rule wording
   - show summary-push status plus discount-strategy push status instead

Acceptance:
- The old premiumRate < -3% convertible event-alert rule no longer drives production reminders.
- Discount strategy buy/sell alerts and monitor pushes run from the new threshold-crossing logic.
- 转债套利 top summary area no longer shows 转股套利候选; it shows 折价监控.
- The 折价监控 card renders the full monitored list, with each item showing at least bond name/code, discount rate, and weighted discount rate.
- Push settings no longer show the obsolete cooldown input.

## 43. Phase AO: Convertible Bond Rights-Issue Monitoring (2026-03-25)

Goal: add an independent `可转债抢权配售` feature page with its own fetch, strategy, page, stock-history DB, and timed push chain, while keeping all existing modules unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the fixed-source-only contract.
2. Keep this round isolated to the new module:
   - no AH / AB formula change
   - no existing 转债套利公式 change
   - no global push contract replacement
3. Add a new independent data chain `cb_rights_issue`:
   - source fixed to `https://www.jisilu.cn/webapi/cb/pre/?history=0`
   - no user URL input area
   - no reuse of `event_arbitrage.rights_issue`
4. Keep an independent stock-history database for this feature, but only for volatility:
   - `60日波动率` is calculated from local stock-history DB using real `后复权` closes
   - source `convertPrice` is treated as the source-provided `20日均值` proxy
   - local DB is not used to determine the strike reference
   - DB sync remains independent from the strategy layer
5. Implement strategy outputs:
   - stage eligibility
   - `配售10张实际所需股数`
   - Shanghai rule: raw required shares -> `×0.6` -> round up to `100股`
   - strike rule: `行权价 = max(当前价, source convertPrice)`
   - `配售所需资金`
   - `单位期权价值`
   - `配售预期收益`
   - `预计收益率`
   - same-day monitor-list inclusion result
6. Add public/runtime surfaces:
   - `GET /api/market/cb-rights-issue`
   - `GET /api/push/cb-rights-issue-config`
   - `POST /api/push/cb-rights-issue-config`
   - independent runtime JSON for source snapshot, monitor list, rebuild status, and push runtime
7. Extend dashboard with a 7th root tab `可转债抢权配售`:
   - monitor list
   - fixed-source structured information list
   - module-local timed push settings
   - module footnote
8. Add independent timed push:
   - trading-day default times `08:00` / `14:30`
   - content based only on the current same-day monitor list
   - not merged into existing summary push

Acceptance:
- Dashboard root tabs increase from 6 to 7, and the new `可转债抢权配售` page renders real data.
- The page has no standalone URL parse area; it reads only the fixed Jisilu pre-plan source.
- Only rows in `上市委通过 / 同意注册(注册生效) / 已明确申购日` and `预计收益率 > 6%` enter the monitor list.
- A dedicated stock-history DB still exists for this feature, but only `60日波动率` depends on it.
- The feature has independent push config/runtime and can expose truthful last success/error state.
- Existing `打新 / 转债套利 / AH / AB / 监控套利 / 分红提醒 / 事件套利` behavior does not regress.

## 44. Phase AP: Convertible / AH / AB Table Search (2026-03-25)

Goal: let the user quickly find a target convertible bond or stock directly inside the three dense main tables without adding new backend APIs.

Plan:
1. Keep this round presentation-only:
   - no fetch change
   - no strategy/formula change
   - no route change
2. Add a shared client-side search capability to:
   - `转债套利`
   - `AH溢价`
   - `AB溢价`
3. Search works on the already loaded real rows and filters before pagination.
4. Search continues to coexist with existing sort and 50-row pagination rules.
5. Search scope:
   - `转债套利`: 转债代码、转债名称、正股代码、正股名称
   - `AH溢价`: A股代码、A股名称、H股代码、H股名称
   - `AB溢价`: A股代码、A股名称、B股代码、B股名称

Acceptance:
- The three pages visibly expose a search box above the main table.
- Typing a code or name filters the current table immediately.
- Clearing the keyword restores the full table.
- Sorting and 50-row pagination still work on the filtered result set.

## 45. Phase AQ: Real Pure-bond Value Truth Fix + Search IME Stability (2026-03-25)

Goal: repair the convertible-bond page so pure-bond-related fields use a real upstream pure-bond value instead of silently falling back to the discount-floor estimate, and make the new table search stable for multi-character and Chinese IME input.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the corrected truthfulness contract.
2. Keep this round minimal and scoped:
   - no new page
   - no route shape change
   - no AH / AB business formula change
   - no monitor business change
3. In the convertible-bond fetch chain:
   - fetch the latest real pure-bond value from the Eastmoney value-analysis source for active bonds
   - write it into `pureBondValue`
   - let theoretical pricing prefer this real value
   - keep the discount-floor result only as a fallback when the real source is unavailable
4. In the dashboard search interaction:
   - preserve focus and caret after in-panel re-render
   - do not re-render during IME composition
   - commit the final filter only on normal input or `compositionend`
   - after clearing, automatically return focus to the same search box

Acceptance:
- `永22转债(113653)` no longer shows the fallback `99.x` pure-bond base when the real upstream pure-bond value is available.
- Convertible theoretical-price calculation uses the real `pureBondValue` when available.
- Search boxes in `转债套利 / AH溢价 / AB溢价` no longer lose focus after the first character.
- Chinese input methods can type continuously without requiring a second click.

## 46. Phase AR: Convertible Strike-price Simplification (2026-03-25)

Goal: simplify the convertible-bond theoretical-pricing rule so the option strike price is fixed to the bond's conversion price, without any extra comparison or derived-strike adjustment.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round strictly inside the convertible theoretical-pricing rule:
   - no route change
   - no data-source change
   - no AH / AB / monitor / rights-issue behavior change
3. Replace the current derived strike rule in the cb-arb model:
   - stop using `max(bondValue / optionQty, convertPrice)`
   - use `callStrike = convertPrice`
   - this rule is later superseded by Phase CI on 2026-03-30
4. Keep the rest of the pricing chain unchanged:
   - real `pureBondValue` still preferred
   - `bond+call` / `bond+call-put` branch rule unchanged
   - volatility / remaining years / treasury-yield inputs unchanged

Acceptance:
- Convertible theoretical pricing no longer performs extra strike-price judgment.
- For rows with valid `convertPrice`, the visible `callStrike*` fields equal `convertPrice`.
- `永22转债(113653)` recalculation reflects the new strike rule directly.

## 47. Phase AS: Convertible Sticky Bond-name Column (2026-03-25)

Goal: make the convertible-bond main table easier to track during horizontal scrolling by keeping the bond name fixed as the leftmost visible column.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round presentation-only and cb-arb-only:
   - no API field change
   - no pricing/formula change
   - no AH / AB / monitor page change
3. Restore the natural identifier order on the convertible main table:
   - `序号`
   - `转债代码`
   - `转债名称`
4. Add a left frozen identifier zone only for the convertible main table:
   - `序号 / 转债代码 / 转债名称` stay fixed on the left while horizontal scrolling
   - sticky styling must remain readable on desktop and not break mobile horizontal viewing

Acceptance:
- 转债套利主表横向滚动时，左侧始终保留 `序号 / 转债代码 / 转债名称`。
- 用户看到后续价格/指标列时，仍能直接知道当前是哪只转债。
- 现有转债字段、排序、分页和计算结果不变。

## 46. Phase AR: Database Auto-update Gap Fill + Rolling Retention (2026-03-25)

Goal: finish one focused database-maintenance round so every active history DB either already has automatic daily upkeep or gets the missing minimal update/prune path, while keeping only the rows actually needed by current features.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the database-maintenance contract.
2. Keep this round narrow and data-maintenance-only:
   - no dashboard layout change
   - no push wording change
   - no AH / AB / convertible pricing formula change
3. Classify the current shared databases into three groups:
   - already auto-updated and already self-pruned: `premium_history.db`
   - already auto-updated and not a growing time-series store: `market_pairs.db`
   - auto-updated but missing rolling retention or missing prune invocation:
     - `subscription_history.db`
     - `stock_price_history.db`
     - `cb_rights_issue_stock_history.db`
4. Implement the simplest retention model for the missing cases:
   - `subscription_history.db`
     - keep daily append/upsert as-is
     - after each IPO / bond sync, prune rows older than the configured retention window
   - `stock_price_history.db`
     - keep incremental append/update as-is
     - after each convertible-underlying history sync, prune each symbol to the configured rolling max row count
     - the kept row count must stay safely above the current max need for `120日波动率 + ATR20 + 20日/5日平均成交额`
   - `cb_rights_issue_stock_history.db`
     - keep incremental append/update as-is
     - after each rights-issue stock-history sync, prune each symbol to the configured rolling max row count
     - the kept row count must stay safely above the current max need for `60日波动率`
5. Put all new retention parameters into `config.yaml` instead of hardcoding them.
6. Make the sync results report truthful prune counts so later diagnosis can see whether retention actually ran.

Acceptance:
- `subscription_history.db` no longer grows forever; the active sync path prunes rows older than the configured retention days.
- `stock_price_history.db` no longer depends on an unused prune helper; the daily sync path really executes rolling per-symbol retention after successful sync.
- `cb_rights_issue_stock_history.db` gains the same rolling retention behavior after sync.
- `premium_history.db` and `market_pairs.db` remain unchanged because they already satisfy the current upkeep contract.
- Current feature calculations still have enough history after pruning:
  - convertible-bond `20/60/120日波动率`
  - convertible-bond `ATR20`
  - convertible-bond `5日/20日平均成交额`
  - rights-issue `60日波动率`

## 48. Phase AT: Server-authoritative Refresh + Status-first Dashboard Polling (2026-03-25)

Goal: keep all current features and push behavior unchanged while making the
dashboard faster, especially for the convertible page, by making the server the
only active refresher and turning the frontend minute loop into status-first polling.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, `contracts/dashboard-api-contract.md`, `RUNBOOK.md`, and `quickstart.md` first.
2. Keep this round behavior-preserving:
   - no business-formula change
   - no tab removal
   - no push-capability removal
   - no public route deletion
3. Clarify refresh ownership:
   - the server scheduler remains the only active refresh owner
   - the dashboard only reads cache/state and does not own heavy sync
   - the page still auto-refreshes every `60s`, but only for status and cache-change detection
4. Improve server/runtime paths:
   - keep the existing `60s` scheduler tick
   - keep dataset refresh intervals unchanged
   - prevent ordinary `cbArb` page reads from waiting on `sync-cb-stock-history`
   - expose a lightweight dashboard resource-status API for cache metadata polling
5. Improve frontend loading:
   - initial bootstrap loads header dependencies plus the current visible tab
   - hidden tabs load on first activation
   - minute polling reloads full data only after `updateTime/cacheTime` changed
   - non-dataset tabs may keep lightweight full reload behavior when active
6. Remove stale dashboard dead paths such as leftover LOF click handling if still present.

Acceptance:
- The dashboard opens with the current tab and header resources first instead of loading every module at startup.
- The page keeps a `60s` auto-refresh loop without forcing large-table reloads when cache metadata is unchanged.
- Ordinary `GET /api/market/convertible-bond-arbitrage` reads no longer wait for underlying-stock history sync.
- Server-side push scheduling and dataset refresh cadence remain unchanged.

## 61. Phase BA: Push Strategy Documentation Sync (2026-03-26)

Goal: add one current, repository-visible push-strategy document so later Codex
sessions can quickly understand which push chains exist today, which config
fields are authoritative, and what the current live timings/status are.

Plan:
1. Keep this round documentation-only:
   - no push behavior change
   - no scheduler code change
   - no API contract change
2. Read the real push sources first:
   - `config.yaml` notification defaults
   - `start_server.js` scheduler/runtime wiring
   - push route/view-model files
   - current live `/api/push/*` responses
3. Add a new root document `推送设置策略.md` that clearly separates:
   - code defaults
   - runtime override files
   - current live effective settings
   - main summary push vs 转债折价提醒 vs 抢权配售独立推送 vs LOF 独立推送
4. Explicitly note the truth hierarchy:
   - `config.yaml` defines defaults
   - runtime JSON stores per-environment overrides
   - live public API is the fastest read path for current cloud truth

Acceptance:
- The repository contains one standalone push-strategy document that can explain
  current push architecture without re-reading large code sections.
- The document reflects the current cloud responses and current config defaults
  separately, avoiding confusion between defaults and environment-local runtime state.

## 62. Phase BB: Midnight Push Resend Fix (2026-03-26)

Goal: stop the cloud runtime from repeatedly sending scheduled push slots between
`00:00` and `01:00` Shanghai time because midnight is inconsistently interpreted
as `24:xx` in one scheduler path and `00:xx` in another.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the midnight-time
   normalization rule before changing code.
2. Keep this round tightly scoped to scheduler time parsing:
   - no push content change
   - no push time configuration change
   - no non-push business change
3. Unify Shanghai-time parsing so all scheduler and runtime-dedup paths use the
   same normalized hour semantics.
4. Add an explicit normalization rule:
   - if a runtime locale returns midnight hour as `24`, the effective scheduler
     hour must be normalized to `0`
   - `00:xx` must never be treated as after `08:00` or `14:30`
5. Ensure this fix applies to all affected timed push paths:
   - main summary push
   - cb-rights-issue timed push
   - LOF timed push
6. Validate with concrete midnight samples around:
   - `2026-03-25T16:04:52.773Z`
   - `2026-03-25T16:59:24.168Z`
   - `2026-03-25T17:00:24.168Z`

Acceptance:
- Between Shanghai `00:00` and `00:59`, scheduler time is interpreted as `00:xx`,
  never `24:xx`.
- Scheduled slots such as `08:00` and `14:30` are not sent during `00:00-01:00`.
- Push runtime dedup no longer clears same-day sent slots because of mismatched
  midnight parsing between scheduler and runtime-state code.

## 63. Phase BC: Module Push Runtime Self-healing (2026-03-26)

Goal: close the remaining gap between main-summary scheduled push and module-local
scheduled push so `cb_rights_issue` and `lof_arbitrage` can self-heal dirty same-day
slot records instead of treating raw persisted slot text as absolute truth.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the module-runtime
   self-healing contract.
2. Keep this round narrow and push-only:
   - no push content change
   - no push time configuration change
   - no non-push business change
3. Align `notification/scheduler/module_push_runtime_store.js` with the main push
   runtime-store rule:
   - current-day scheduled slot records are valid only when the latest same-day
     success time proves that the recorded slot is not later than the real success
     point
   - otherwise the dirty future slot records must be dropped automatically
4. Apply the hardened runtime-store behavior to both module-local timed push chains:
   - `cb_rights_issue`
   - `lof_arbitrage`
5. Improve `lof_arbitrage` timed-push logs so cloud diagnosis can see:
   - runtime self-healing result
   - `not_due_yet`
   - `already_sent`
   - success / failure

Acceptance:
- `cb_rights_issue` and `lof_arbitrage` no longer trust same-day future slot text
  blindly after a dirty early success record.
- Module-local timed push diagnostics become readable from live server logs.
- Existing module push schedule, payload fields, and API routes remain unchanged.
- Rows still degrade truthfully to source-estimate / missing-input status when exact external index data is unavailable.

## 63. Phase BC: Data Refresh Reliability And Status Truthfulness (2026-03-26)

Goal: repair the current cloud-runtime freshness failures so the dashboard can again
be treated as a financial-grade, time-sensitive page instead of a stale-cache viewer.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new refresh-reliability contract.
2. Keep this round tightly scoped to refresh, cache-status, and scheduler truthfulness:
   - no strategy-formula change
   - no table-layout change
   - no push-content change
3. Repair `cbArb` refresh so the public `可转债套利` dataset no longer blocks on the heavy
   history-maintenance path during ordinary intraday reads:
   - page/API read path must keep returning the latest good cache quickly
   - heavy stock-history sync must stay in explicit maintenance or daily-sync path
   - forced real-time read must complete within the existing server timeout budget
4. Correct dashboard freshness semantics:
   - `servedFromCache` can no longer mean merely “this dataset has a cache file”
   - resource status must distinguish between “latest successful dataset snapshot”
     and “fallback cache because refresh failed”
   - dashboard copy must stop calling today-fresh data a stale snapshot
5. Harden daily-sync truthfulness:
   - `runDailySync()` must not mark the day as completed when one or more required
     datasets failed
   - failed datasets must remain visible in runtime state / logs
6. Normalize midnight scheduler time:
   - Shanghai midnight `24:xx` must be normalized to `00:xx`
   - `00:00-00:59` must never trigger `08:00 / 14:30` timed sends early
7. Verify both locally and on the cloud server:
   - non-`cbArb` force refresh still succeeds
   - `cbArb` force refresh returns same-day data again
   - resource-status freshness text matches real update state
   - midnight scheduler regression is covered by targeted tests

Acceptance:
- `GET /api/market/convertible-bond-arbitrage?force=1` no longer times out behind the cloud proxy under normal runtime conditions.
- `runtime_data/shared/market_cache_cbArb.json` updates on `2026-03-26` instead of staying frozen on `2026-03-25`.
- `GET /api/dashboard/resource-status` stops marking every cached dataset as a stale-cache dataset.
- The dashboard header no longer claims “当前显示缓存快照” for datasets that were freshly rebuilt and simply persisted to cache.
- `runDailySync()` only records same-day success after required dataset refreshes actually succeed.
- Shanghai `00:xx` no longer appears as `24:xx` in timed-push decision logs, and timed slots are not sent early after midnight.

## 64. Phase BE: Dashboard Low-risk Dual-theme Restyle (2026-03-27)

Goal: introduce a cleaner, data-first dashboard visual style without changing any
business logic, API path, table field, push behavior, or refresh contract, so the
site can move to a simpler data-terminal look while remaining instantly rollbackable.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the visual-only
   dual-theme contract before touching code.
2. Keep this round isolated to the dashboard presentation layer:
   - no route-path change
   - no response-shape change except adding one optional UI-config field
   - no data-fetch / strategy / notification / scheduler behavior change
3. Add one centralized theme switch in `config.yaml`:
   - `presentation.dashboard_theme`
   - supported values:
     - `classic`
     - `clean_data`
4. Extend `GET /api/dashboard/ui-config` to expose the current dashboard theme, so
   the frontend can switch style without duplicating configuration logic.
5. Keep the current style as the safe fallback `classic`, and add a new
   `clean_data` theme that emphasizes:
   - lighter neutral background
   - cleaner table-first panels
   - calmer blue/steel accents
   - reduced decorative glow
   - unchanged DOM structure and interaction behavior
6. Apply the theme on the frontend by attribute/class switching only; do not rewrite
   page layout or module render logic in this round.
7. Make rollback trivial:
   - switching `presentation.dashboard_theme` back to `classic` restores the old
     appearance without code rollback.

Acceptance:
- All existing dashboard tabs, subtabs, sorting, searching, pagination, auto-refresh,
  push settings, and module rendering continue to behave exactly as before.
- `GET /api/dashboard/ui-config` returns the current theme name in addition to the
  existing UI payload.
- `clean_data` visually changes the dashboard to a cleaner, data-first style without
  changing any visible business field or interaction semantics.
- Setting `presentation.dashboard_theme = classic` restores the prior theme without
  touching any business code.

## 65. Phase BE: Convertible Discount Push Session Separation (2026-03-27)

Goal: align `可转债折价推送` with the user-confirmed A-share trading rhythm so the
module no longer pushes on non-trading days, no longer pushes after 15:00, and no
longer presents timed monitor pushes and buy/sell instant signals as one blurred channel.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the revised push contract.
2. Keep this round isolated to the convertible-bond discount push chain:
   - no AH / AB / LOF push schedule change
   - no main summary module-selection change
   - no convertible pricing-formula change in this round
3. Refine the discount-push session contract:
   - only run on A-share trading weekdays
   - valid push windows are fixed to `09:30-11:30` and `13:00-15:00`
   - after `15:00` no timed monitor push and no buy/sell instant push may be emitted
4. Keep the two push lanes explicit:
   - timed monitor-list push remains driven by `monitor_session_times`
   - buy/sell instant push remains driven by zone-crossing signals
   - shared scheduler tick is allowed, but runtime status and wording must clearly distinguish the two lanes
5. Expose the truthful runtime contract to the dashboard:
   - show monitor schedule slots instead of an ambiguous “监控频率”
   - show A-share session windows used by instant buy/sell checks
   - keep recent buy / sell / monitor success and error timestamps separated

Acceptance:
- `可转债折价推送` does not run on weekends or other non-trading weekdays configured as outside-session runtime.
- No discount push is emitted after `15:00` Shanghai time.
- Timed monitor pushes still use configured monitor slots, while buy/sell signals remain independent instant events.
- Push status text no longer makes the two channels look like one periodic task.

## 66. Phase BF: Dashboard Footer-note + Compact Naming + Dense Top Sections (2026-03-28)

Goal: further compress the dashboard into a more Jisilu-like reading flow by moving
all page notes to the global page bottom, shrinking root tabs, tightening top summary
sections, and shortening visible list/module names without changing any data logic.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new compact
   presentation contract.
2. Keep this round isolated to the dashboard presentation layer:
   - no API path change
   - no response-field change
   - no strategy / fetch / push / scheduler behavior change
3. Move module notes from each panel body to one shared footer-note area at the very
   end of the page:
   - the active tab's note is rendered there
   - module panels no longer repeat inline note cards
4. Compress root tabs on desktop into a smaller single-row navigation strip:
   - shorter labels
   - smaller height and padding
   - keep mobile responsive fallback
5. Make top summary sections denser:
   - use tighter multi-column summary cards
   - reduce decorative spacing
   - avoid vertically stacked “wasted” top blocks where side-by-side grouping is enough
6. Shorten visible module/list wording toward a Jisilu-style data page tone:
   - prefer `转债 / AH / AB / LOF / 监控 / 分红 / 事件 / 抢权`
   - prefer `列表 / 入池 / 来源 / 今日登记 / 前3 / 后3`
   - do not change any business meaning behind the text

Acceptance:
- Module notes no longer appear inside each tab panel and instead render in the page footer area.
- On desktop, root tabs are visibly smaller and remain on one row.
- Top summary blocks become denser and occupy less vertical space.
- Visible titles and list labels become shorter without changing data semantics or interaction behavior.

## 68. Phase BH: Table-header Compaction Instead Of Module Renaming (2026-03-28)

Goal: correct the compact-label direction so the dashboard keeps the original module
names, while the real density optimization happens in table headers, list labels, and
column widths under each module.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the corrected copy contract.
2. Revert any unintended shortening of root module names and module titles.
3. Apply compact wording to list/table headers instead, for example:
   - `转债代码 -> 代码`
   - `正股代码 -> 正股码`
   - `转股价值 -> 转股值`
   - `近三年分位 -> 分位`
4. Reduce width pressure in the shared dashboard table CSS:
   - narrower numeric/date/code columns
   - tighter sticky-column widths
   - smaller minimum widths for dense data tables where safe
5. Keep all changes presentation-only:
   - no data-field change
   - no sorting/searching behavior change
   - no API change

Acceptance:
- Root module names remain the original business names.
- Dense tables use shorter column labels and occupy less width.
- Data density improves mainly through table-header wording and column-width tuning, not through renaming root modules.

## 67. Phase BG: Convertible Premium-only Truthfulness Repair (2026-03-28)

Goal: finish the still-open convertible-bond repair by removing the outward
`折价率` semantics, correcting live conversion metrics at the source, and aligning
page/push wording with the user-confirmed `转股溢价率` contract.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round tightly scoped to the convertible-bond chain:
   - `data_fetch/convertible_bond`
   - `strategy/convertible_bond`
   - `start_server.js`
   - dashboard convertible presentation
   - convertible discount push wording/runtime view
3. Repair live source truthfulness:
   - `convertValue` must always be recomputed from latest `stockPrice` and `convertPrice`
   - `premiumRate` must always be recomputed from latest `price` and computed `convertValue`
   - live price-derived fields must stop falling back to previous cached rows
   - slow caches remain allowed only for history-derived metrics such as volatility, ATR, turnover, and pure-bond-value snapshots
4. Replace outward `折价率` semantics with `转股溢价率` semantics:
   - buy zone becomes `premiumRate < -2%`
   - sell zone becomes `premiumRate > -0.5%`
   - page, summary card, API wording, and push wording must stop exposing `折价率 / 加权折价率`
5. Adjust the convertible main table readability contract:
   - sticky columns become `序号 + 转债名称`
   - `转债代码` remains visible but no longer sticky and no longer sits before the name in the frozen area
6. Verify the concrete bad sample after the fix:
   - `118025 奕瑞转债`
   - `stockPrice = 106.02`
   - `convertPrice = 114.97`
   - expected `convertValue ≈ 92.215`
7. After local verification, deploy to cloud and force-refresh the public API/page.
8. If public `cbArb force` still exceeds the proxy window, add one proxy-safe soft timeout:
   - return the latest last-good snapshot instead of `504`
   - keep the real refresh task running in background

Acceptance:
- `GET /api/market/convertible-bond-arbitrage?force=1` returns `118025.convertValue`
  close to `92.215` instead of the previous bad `499.89`.
- Convertible public rows no longer expose visible `折价率 / 加权折价率` fields or wording.
- Buy/sell push reasoning uses `转股溢价率` thresholds instead of `折价率`.
- Convertible table sticky columns are `序号 + 转债名称`.
- The cloud page and API both reflect the corrected same-day snapshot after deploy.

## 70. Phase BJ: Dashboard Visual Experiment Rollback (2026-03-28)

Goal: roll the dashboard back to the pre-restyle presentation baseline after the
compact-theme experiment was rejected, while keeping all business logic, data fields,
APIs, and push behavior unchanged.

Plan:
1. Revert dashboard presentation from the experimental visual path back to the
   original classic reading mode.
2. Remove the active use of:
   - `clean_data` theme presentation
   - shared page-bottom footnote rendering
   - compact list titles such as `主表 / 入池 / 来源 / 观察`
   - compressed table-header wording introduced only for the visual experiment
3. Restore the earlier visible behavior:
   - inline module notes remain inside each module
   - original table/list titles return
   - original table density, sticky-column layout, and width guidance return
4. Keep rollback strictly presentation-only:
   - no fetch / strategy / notification / scheduler changes
   - no API path or response-shape changes

Acceptance:
- The dashboard visually returns to the pre-restyle baseline.
- Business functions remain available and unchanged.
- Documentation no longer treats the rejected visual experiment as the effective contract.

## 71. Phase BK: Convertible Frozen-column Correction + Weighted Discount Restore (2026-03-28)

Goal: finish the still-open convertible-bond follow-up requested in the latest user review:
1. the frozen columns must be exactly `序号 + 转债名称`
2. `转债代码` must no longer stay frozen and no longer sit immediately behind the frozen name column
3. `加权折价率` must be restored, but its underlying discount basis must switch to `-转股溢价率`

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the corrected live contract.
2. Keep this round isolated to the convertible-bond chain:
   - `strategy/convertible_bond`
   - `start_server.js`
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
   - convertible push wording/output where needed
3. Restore the weighted-discount strategy metric on the shortest path:
   - internal `discountRate = -premiumRate`
   - `weightedDiscountRate = discountRate * atrCoefficient * sellPressureCoefficient * boardCoefficient`
   - keep `转股溢价率` as the main truth field
4. Keep raw `折价率` out of the main user-facing table, but allow `加权折价率` to return as a user-facing auxiliary strategy field.
5. Reorder the convertible main table so the only frozen columns are:
   - `序号`
   - `转债名称`
   and move `转债代码` out of the frozen area.
6. Re-verify locally, then deploy to cloud and confirm the public page/API reflect the corrected table structure and weighted metric.

Acceptance:
- Convertible frozen columns are exactly `序号 + 转债名称`.
- `转债代码` is still visible but no longer frozen and no longer placed directly after the frozen name column.
- `weightedDiscountRate` is restored in strategy output and public API.
- `weightedDiscountRate` is calculated from `discountRate = -premiumRate`, not from the retired old discount source.
- Public page and cloud API both reflect the corrected contract after deploy.

## 72. Phase BL: Convertible Main-table Compaction (2026-03-28)

Goal: reduce the width pressure of the convertible main table without changing the
backend truth fields, so the page keeps the key pricing view but no longer tries to
show every auxiliary field at once.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible presentation path:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Compact the main table by:
   - shortening visible labels to concise names, target `<= 4` Chinese characters where practical
   - merging naturally paired values into one cell where that improves width:
     - `转债价 = 现价 + 涨幅`
     - `正股 = 名称 + 代码`
     - `正股价 = 现价 + 涨幅`
     - `正股成交 = 20日均额 + 5日均额`
   - keeping search ability, but removing separate clear/hint clutter from the convertible search bar
4. Remove the following from the convertible main table while keeping them in the backend payload:
   - `listingDate`
   - `convertStartDate`
   - `maturityDate`
   - `optionTheoreticalValue`
   - `theoreticalPrice`
5. Add one compact visible term field:
   - `剩余期` from `remainingYears`
6. Keep only `理论溢` as the visible theoretical-pricing field in the main table.

Acceptance:
- Convertible main table is visibly narrower than before.
- Visible column labels are shortened and avoid long phrases such as `正股20日均额(亿)`.
- `上市日 / 转股起始日 / 到期日 / 期权理论价值 / 理论价值` no longer appear in the main table.
- `剩余期` becomes the single visible term field.
- `理论溢` remains visible; `期权理论价值 / 理论价值` remain backend-only.

## 73. Phase BM: LOF RMB-aligned Index-change Definition (2026-03-28)

Goal: correct the dashboard meaning of `相关指数涨幅` in `LOF套利` so the visible
change rate is no longer the raw upstream index field, but the real
RMB-priced change aligned to the row's `净值日期`.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the LOF strategy/output and LOF page presentation:
   - `strategy/lof_arbitrage/service.py`
   - `presentation/dashboard/dashboard_page.js`
3. Keep the current IOPV branches unchanged, but add one outward derived field:
   - `navAlignedIndexChangeRate = (iopv / nav - 1) * 100`
4. Use the new field as the page definition of `相关指数涨幅`:
   - it is always relative to the row `净值日期`
   - it is the RMB-priced change after index and FX adjustment
   - for same-day NAV direct rows, the outward change is `0%`
5. Do not repurpose the raw source-normalized `indexIncreaseRate` as the visible page
   field anymore; it may remain in the backend row for diagnostics only.

Acceptance:
- `LOF套利` page no longer shows the raw upstream `indexIncreaseRate` as the visible
  `相关指数涨幅`.
- The visible change rate is consistent with:
  - `IOPV = 净值日净值 × (1 + 涨跌幅)`
  - equivalently `涨跌幅 = iopv / nav - 1`
- `指数LOF / QDII亚洲` rows both use the RMB-adjusted, nav-date-aligned visible result, even though
  their internal IOPV branch still relies on the existing source increase path.

## 74. Phase BN: Convertible Main-table Label + Frozen-column Follow-up (2026-03-30)

Goal: finish the latest user-reviewed convertible-table follow-up without touching the
backend pricing chain, so the page becomes denser and easier to scan while keeping the
same truth fields.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible dashboard presentation path:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Replace the frozen-column contract:
   - remove the visible `序号` column
   - merge `转债名称 + 转债代码` into one frozen identity column
   - make that merged `转债名称` column the only frozen column
4. Upgrade three pricing cells from single-value to dual-value display:
   - `转股溢价 = 溢价金额 + 溢价率`
   - `加权折价 = 折价金额 + 加权折价率`
   - `理论溢价 = 理论溢价金额 + 理论溢价率`
5. Align the visible copy with the latest user wording:
   - `纯债价 -> 纯债价值`
   - `规模 -> 剩余规模`
   - `60波动 -> 波动率`
   - `剩余期 -> 剩余期限`
6. Re-verify locally, then sync the dashboard changes to cloud if the repo checks pass.

Acceptance:
- The convertible main table no longer shows a visible `序号` column.
- The left frozen area contains only one merged `转债名称` identity column with
  `名称 + 代码` stacked in the same cell.
- Horizontal scrolling no longer leaves a separate frozen index column behind.
- `转股溢价 / 加权折价 / 理论溢价` each render as a compact two-line cell with
  amount first and rate second.
- The visible labels read exactly:
  - `转股溢价`
  - `加权折价`
  - `纯债价值`
  - `理论溢价`
  - `剩余规模`
  - `波动率`
  - `剩余期限`

## 75. Phase BO: Premium-only Weighted Discount Cleanup + Convertible Sort Narrowing (2026-03-30)

Goal: finish the next convertible-bond cleanup requested in the latest review so the
page and strategy stop reintroducing a standalone `折价率` concept, every normal row
can show a weighted-discount result, and the table only keeps the few sort handles
the user actually wants.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to:
   - `strategy/convertible_bond/service.js`
   - `presentation/dashboard/dashboard_page.js`
3. Remove the outward `discountRate` concept from this round's live contract:
   - weighted-discount logic must directly use `-premiumRate`
   - row enrichment must stop returning a standalone `discountRate` field
4. Extend weighted-discount calculation from “only low-premium rows” to the full
   convertible table:
   - signed base stays `-premiumRate`
   - coefficient magnitude uses `abs(-premiumRate)` where a non-negative anchor ratio
     is required
5. Make the three dual-value pricing cells percentage-first:
   - `转股溢价`: main line = `premiumRate`
   - `理论溢价`: main line = `theoreticalPremiumRate`
   - `加权折价`: main line = `weightedDiscountRate`
   - secondary line keeps the amount text
6. Insert the factor columns before `加权折价`:
   - `ATR系数/ATR%`
   - `抛压系数`
   - `市场`
7. Narrow convertible sorting to:
   - `加权折价`
   - `理论溢价`
   - `双低`
   and remove the other sort handles.

Acceptance:
- The live convertible strategy no longer returns or documents a standalone `discountRate`
  user-facing concept for this round.
- `weightedDiscountRate` is computed for the full table whenever the needed factor inputs exist,
  not only for the old low-premium monitor subset.
- `转股溢价 / 理论溢价 / 加权折价` display percentage first and amount second.
- `ATR系数/ATR% / 抛压系数 / 市场` appear before `加权折价` in the main table.
- The convertible main table only exposes sorting for `加权折价 / 理论溢价 / 双低`.

## 76. Phase BP: Cloud-only Web Entry Cleanup + Server-first Workflow (2026-03-30)

Goal: stop treating this repository as a local-web delivery target and converge the
operator workflow to one official path: update cloud server only, keep the cloud
dashboard as the single formal access surface, and delete local-webpage residues that
are no longer part of the live runtime.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to cloud-entry semantics, operator tooling, and residue cleanup:
   - do not change the live dashboard template/render chain used by the cloud server
   - do not change public API paths
   - do not change strategy/fetch/push business logic
3. Treat the formal live web chain as only:
   - `start_server.js`
   - `presentation/templates/dashboard_template.html`
   - `presentation/dashboard/dashboard_page.js`
   - configured `deployment.public_base_url`
4. Remove local-only / duplicate web-entry residues that are not part of the live chain,
   such as:
   - root `index.html` local/cloud guidance page
   - unreferenced `remote_dashboard_template.html`
   - unreferenced `remote_dashboard_page.js`
   - Windows local firewall helper scripts that only existed for local port exposure
5. Change default verification semantics from loopback-first to cloud-first:
   - `npm run check`
   - `npm run check:health`
   should prefer configured public URL / cloud URL, while still allowing explicit override.
6. Update runbook/quickstart wording so future sessions no longer treat local webpage access
   as a parallel official path.
7. Sync the resulting change set to the cloud server and verify the public homepage and
   public `/api/health`.

Acceptance:
- The repository documents the cloud server as the only official operator-facing web entry.
- Local duplicate dashboard mirror files are removed when they are not part of the live chain.
- Default health/smoke checks no longer assume `127.0.0.1:5000` as the primary target.
- The cloud homepage and cloud `/api/health` remain reachable after deployment.

## 77. Phase BQ: Convertible Premium-Rate Sort Restore (2026-03-30)

Goal: restore the user-requested `转股溢价` sort handle in the convertible main table
without reopening the broader sortable-surface cleanup from the previous round.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible main-table sorting contract:
   - do not change fetch logic
   - do not change weighted-discount formula
   - do not change push, summary, or API payload semantics
3. Promote the live sortable-column contract from three columns to four columns:
   - `转股溢价`
   - `加权折价`
   - `理论溢价`
   - `双低`
4. Implement the change only in the convertible dashboard column definition by restoring:
   - `sortable: true`
   - numeric sort
   - `premiumRate` as the sort value
5. Re-run local checks and sync the updated page bundle to the cloud server.

Acceptance:
- The convertible main table header for `转股溢价` is clickable again.
- `转股溢价` sorts by `premiumRate` numeric value rather than display text.
- Existing sort handles for `加权折价 / 理论溢价 / 双低` remain unchanged.
- No other module or API contract changes in this round.

## 78. Phase BR: Convertible Remaining-Term Year Unit + Force-Redeem Highlight (2026-03-30)

Goal: align the convertible main table with the latest operator requirement so
`剩余期限` always renders in `年`, and bonds that have already published a force-redeem
status are visually highlighted in yellow on the page.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible presentation chain:
   - no formula changes
   - no push changes
   - no new fetch source introduction
3. Normalize the `剩余期限` display rule:
   - keep using the existing source field `remainingYears`
   - stop switching to month display for short remaining terms
   - render all values in `年`
4. Add a dedicated front-end row highlight rule for published force-redeem items:
   - use yellow as the visual cue
   - only highlight rows whose force-redeem status is affirmative and not terminal
5. Surface the source truth clearly in the implementation notes:
   - the current force-redeem status field continues to come from the existing
     Eastmoney convertible-bond bulk source field `IS_REDEEM`
6. Re-run local checks and sync the updated assets to the cloud server.

Acceptance:
- `剩余期限` in the convertible main table always shows year units such as `0.42年`.
- Convertible rows with an affirmative published force-redeem status are highlighted yellow.
- Completed/delisted terminal statuses are not re-highlighted by this new UI rule.
- The round does not alter formulas, APIs, or push behavior.

## 79. Phase BS: LOF Push Simplification To One 14:00 Full Push (2026-03-30)

Goal: simplify the LOF push chain to one fixed trading-day full push at `14:00`
and retire the old entry-based instant path plus the extra afternoon slots.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and the dashboard API contract first.
2. Keep this round isolated to the LOF notification chain and its dashboard settings card:
   - no LOF market-data formula change
   - no non-LOF push behavior change
3. Retire the old LOF instant-push behavior completely:
   - no more new-entry detection
   - no more instant success/error state in the outward dashboard wording
4. Reduce the LOF scheduled push contract to one fixed slot:
   - trading days only
   - `14:00`
   - full current monitor-pool payload only
5. Migrate existing runtime config/state away from the old `13:30 / 14:00 / 14:30`
   schedule so the cloud server does not continue using stale stored times.
6. Simplify the LOF dashboard push card to match the new fixed behavior and remove the
   old three-time editable form.
7. Re-run local checks and sync the change set to the cloud server.

Acceptance:
- LOF no longer sends new-entry instant pushes.
- LOF scheduled push runs only once on trading days at `14:00`.
- The LOF dashboard push card no longer describes or exposes the retired instant/triple-slot behavior.
- Existing AH / AB / 转债 / 抢权 / 分红 / 事件套利 push chains remain unchanged.

## 80. Phase BT: Convertible Force-Redeem Public Field Fix (2026-03-30)

Goal: fix the remaining gap in the convertible page so force-redeem highlighting can
actually work on the live page by exposing the needed real fields through the public
cb-arbitrage payload, while keeping completed force-redeem bonds filtered out.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and the dashboard API contract first.
2. Keep this round isolated to the convertible public payload and page read path:
   - no LOF change
   - no formula change
   - no push change
3. Clarify the live business rule:
   - `已公告强赎、但未终止上市` => yellow highlight
   - `已完成强赎 / 已终止上市 / 已摘牌` => remove from the live list
4. Expose the real source fields needed by the page:
   - `forceRedeemStatus`
   - `delistDate`
   - `ceaseDate`
5. Re-run checks and sync to the cloud server.

Acceptance:
- Convertible public rows expose the force-redeem status/date fields needed by the page.
- The page can highlight active force-redeem rows when the source provides that status.
- Completed force-redeem bonds remain removed from the live table instead of being highlighted.

## 79. Phase BS: Pure-bond Truthfulness + Sort Stability + 250D Volatility Readiness (2026-03-30)

Goal: finish three tightly related corrections in the convertible and cb-rights-issue
chains without changing outward business modules:
1. pure-bond value in theoretical pricing must use only the upstream API value and must
   stop falling back to local discounted self-calculation;
2. dashboard table sorting must stop causing visible horizontal jump-back to the first
   column;
3. the active volatility standard must be truly enforced as `250日后复权年化波动率`,
   and the history-sync/default-retention chain must no longer quietly retain old 60-day
   assumptions when config or database state is stale.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to:
   - `data_fetch/convertible_bond/source.py`
   - `data_fetch/convertible_bond/history_source.py`
   - `data_fetch/cb_rights_issue/source.py`
   - `data_fetch/cb_rights_issue/history_source.py`
   - `tools/cb_rights_issue_stock_history_db.py`
   - `presentation/dashboard/dashboard_page.js`
3. Pure-bond truthfulness:
   - theoretical pricing may only use `pureBondValue` returned by the upstream pure-bond API
   - if upstream pure-bond value is missing, `bondValue/theoreticalPrice/theoreticalPremiumRate`
     must degrade truthfully instead of using local discounted fallback
4. Sort stability:
   - preserve current table horizontal scroll position when clicking sortable headers
   - prevent sort interaction from visually jumping the user back to the first column
5. 250-day volatility readiness:
   - keep `250` as the only active volatility window default
   - remove remaining source/history defaults that still assume `60`
   - verify current DB row counts for both convertible and cb-rights-issue history stores
   - if current DB does not yet satisfy 250-day minimum, report it truthfully and trigger
     the necessary history sync on the live server
6. Re-run checks, sync to cloud, and verify the public page/API plus history-db readiness.

Acceptance:
- Theoretical pricing no longer self-computes bond floor when upstream pure-bond value is absent.
- Sorting a wide dashboard table no longer jumps horizontal view back to the left edge.
- Active code defaults and runtime wording consistently use 250-day HFQ annualized volatility.
- DB verification clearly states whether 251-close minimum is currently satisfied, and the
  cloud server is brought to the correct history-sync state.

## 81. Phase BU: Pure-bond Cache Wireback Fix (2026-03-30)

Goal: restore truthful `纯债价值` display on the live convertible page after the
previous round removed the local fallback but left the upstream pure-bond daily cache
unwired from the normal read path.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible pure-bond read chain:
   - no formula expansion
   - no push change
   - no non-convertible module change
3. Reconnect the existing upstream pure-bond loader to the daily aux-cache path:
   - normal read path must load `pureBondMap` via the existing Eastmoney pure-bond source
   - if same-day fetch succeeds, cache it and expose it to outward rows
   - if same-day fetch fails, truthfully fall back only to previously cached real upstream values
4. Remove stale wording that still mentions the retired local discounted fallback.
5. Re-run checks, deploy cloud-only, and verify that the public convertible payload/page
   shows restored `pureBondValue` where the upstream source provides it.

Acceptance:
- Live `/api/market/convertible-bond-arbitrage` rows recover truthful `pureBondValue` values.
- The page `纯债价值` column no longer stays blank for bonds whose upstream pure-bond value exists.
- No local discounted fallback is reintroduced.

## 83. Phase BW: Convertible Full-column Sort + Compact Widths (2026-03-30)

Goal: improve the convertible main-table scanning experience without changing the
backend truth fields, by restoring sort interaction across all visible convertible
columns and tightening column widths so the table follows content width more closely.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible dashboard presentation path:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Expand the convertible sort contract:
   - every visible convertible main-table column gets a sortable header
   - sort value should follow the column's primary displayed field
   - header affordance changes to a compact arrow-above-label style
4. Tighten convertible width rules:
   - use narrower convertible-specific column classes instead of broad shared widths
   - let identity / quote / factor / numeric columns shrink closer to their visible content
   - keep horizontal scrolling available, but remove unnecessary width padding
5. Re-run front-end syntax checks and summarize the result.

Acceptance:
- All visible convertible main-table headers are sortable.
- Sort headers show a compact arrow indicator above the label.
- Convertible columns are visibly narrower and closer to content width than before.
- No backend formula, API field, or push behavior changes in this round.

## 86. Phase BZ: CB-rights-issue 250D Volatility Enforcement + DB Repair (2026-03-30)

Goal: repair the cb-rights-issue chain so it truly uses `250日后复权年化波动率`
as the only live pricing input, and bring the dedicated stock-history database to a
real `>=251`-close ready state.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the cb-rights-issue chain:
   - `data_fetch/cb_rights_issue/source.py`
   - `data_fetch/cb_rights_issue/history_source.py`
   - `strategy/cb_rights_issue/service.py`
   - dedicated history DB/runtime state
3. Enforce the live 250D rule:
   - outward/source rows must compute and expose `volatility250`
   - old `volatility60` may remain only as a compatibility alias that mirrors the 250D value
   - strategy pricing must stop using a real old-60-day fallback
4. Repair the database:
   - inspect current dedicated history DB row-count coverage
   - run the required full sync so symbols with enough listing history reach `>=251` closes
   - keep truthful exceptions only for genuinely short-listed symbols
5. Re-verify local/cloud results and summarize the final coverage.

Acceptance:
- `cb_rights_issue` pricing uses `250日后复权年化波动率` as the only real live input.
- Rows no longer price from a real old 60-day volatility value.
- The dedicated history DB is brought to `>=251`-close readiness wherever listing history allows.
- Cloud API rows for eligible names recover truthful `volatility250` and aligned收益率.

## 82. Phase BV: Convertible Strong-redeem Page Truthfulness + Theoretical-premium 250D Repair (2026-03-30)

Goal: fix the last two visible convertible-page regressions without changing unrelated
modules:
1. active strong-redeem rows must highlight correctly, while terminal rows such as
   completed/delisted bonds still stay out of the live list;
2. `理论溢价率` must again display truthful values under the current `250日后复权波动率`
   standard instead of degrading broadly to blank because the pure-bond input/cache chain
   or public-row shaping is incomplete.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible read/display chain:
   - `data_fetch/convertible_bond/source.py`
   - `strategy/convertible_bond/service.js`
   - `presentation/dashboard/dashboard_page.js`
   - `start_server.js`
3. Clarify the strong-redeem truth rule:
   - `已公告强赎、但尚未停牌/摘牌/终止上市` => yellow highlight
   - `已停牌 / 已摘牌 / 已终止上市 / 已完成强赎` => remove from the live list, not highlight
   - if `海优转债` is already terminal in the real source, the correct live behavior remains
     “not present” rather than “yellow-highlighted”
4. Repair the theoretical-premium live chain under the active 250D standard:
   - outward `theoreticalPrice / theoreticalPremiumRate` continue to depend on real
     `pureBondValue + 250日后复权波动率`
   - same-day pure-bond daily cache must be reused correctly on the normal read path
   - rows with available truthful inputs must recover visible `理论溢价率`
   - rows lacking truthful pure-bond input must still show `--`
5. Keep the page wording aligned with the live rule:
   - `波动率` display for this chain remains `250日后复权年化波动率`
   - formula/explain text must not imply the retired 60-day standard
6. Re-run checks, sync to the cloud server, and verify the public API/page.

Acceptance:
- Live page/API do not keep terminal strong-redeem rows such as completed `海优转债` in the
  convertible table.
- Active non-terminal strong-redeem rows can still be highlighted yellow.
- Live rows with truthful pure-bond + 250D volatility inputs recover `theoreticalPremiumRate`.
- Rows missing truthful pure-bond input continue to show `--`, with no fake fallback.

## 84. Phase BX: Custom Monitor Precision To Three Decimals (2026-03-30)

Goal: make the `监控套利 / 自定义监控` module numerically consistent by unifying
its calculated outputs and user-facing display precision to `小数点后三位`, without
changing formulas or touching other arbitrage modules.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the custom-monitor chain:
   - `strategy/custom_monitor/service.js`
   - `presentation/dashboard/dashboard_page.js`
   - `notification/styles/markdown_style.js`
3. Unify calculation/output precision:
   - monitor derived numeric fields should round to `3` decimals
   - this applies to monitor-side price / payout / spread / yield outputs
4. Unify outward display precision:
   - monitor tab table values show `3` decimals
   - monitor detail panel and formula text show `3` decimals
   - timed summary markdown for `自定义监控（全量）` shows `3`-decimal yield rates
5. Keep the round narrow:
   - no formula change
   - no config change
   - no AH / AB / 转债 / LOF / 分红 / 事件套利 display change
6. Re-run the relevant syntax checks and summarize the result.

Acceptance:
- `监控套利` module derived outputs are rounded/displayed to `3` decimals.
- Table, detail panel, and summary markdown stay consistent with one another.
- No non-monitor module precision changes regress in this round.

## 85. Phase BY: Convertible Force-redeem Status Column + Bright Highlight Fix (2026-03-30)

Goal: fix the false-positive convertible strong-redeem highlighting and add a dedicated
`强赎状态` column at the far right of the convertible table, while keeping the change
isolated to the convertible read/display chain.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to:
   - `data_fetch/convertible_bond/source.py`
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
   - `start_server.js`
3. Retire the wrong highlight input:
   - stop using raw `IS_REDEEM`/`isRedeem` as if it were a published strong-redeem state
   - derive outward `forceRedeemStatus` from stronger real clues such as notice dates and terminal dates
4. Add a dedicated convertible trailing column:
   - `强赎状态`
   - place it at the far right / final visible column
   - show the derived status text and, when available, its notice date
5. Tighten the page highlight rule:
   - highlight only rows whose outward derived status clearly means active published strong redeem
   - terminal/delisted rows must not highlight
6. Refresh the row color to a brighter yellow, avoiding the previous dull yellow-brown tone.
7. Re-run syntax checks, sync the server, and verify the live page/API.

Acceptance:
- Convertible page no longer highlights nearly all rows.
- `强赎状态` appears as the final convertible table column.
- Active strong-redeem rows use a bright yellow highlight.
- The page reads the corrected derived status instead of the raw all-`是` flag.

## 86. Phase BZ: Convertible Put-option Strike Fixed To Force-redeem Price (2026-03-30)

Goal: update the convertible theoretical-pricing chain so the put-option leg is
actually priced using `强赎价 / redeemTriggerPrice` whenever that real input exists,
instead of silently dropping the put leg when the stock is below the trigger.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible theoretical-pricing path:
   - `data_fetch/convertible_bond/source.py`
   - `presentation/dashboard/dashboard_page.js`
3. Clarify the live pricing rule:
   - put-option strike remains `redeemTriggerPrice`
   - if a truthful `redeemTriggerPrice` exists, the put leg must be priced and deducted
   - do not zero out the put leg merely because current stock price is below the trigger
4. Update outward pricing-formula text to match the new live rule.
5. Re-run checks and verify with a concrete bond such as `福22转债`.

Acceptance:
- Convertible rows with a real `redeemTriggerPrice` can produce non-zero `putOptionValue`.
- `theoreticalPrice` and `theoreticalPremiumRate` reflect the deducted put leg.
- Page explanation text matches the implemented formula.

## 91. Phase CE: Convertible Pure-bond Premium Dual-value Column (2026-03-30)

Goal: adjust the convertible main table so the former `纯债价值` column becomes a
dual-value `纯债溢价` column that follows the user-defined ratio
`转债价格 / 纯债价值 - 1`, with sorting driven by that ratio while keeping the change
isolated to front-end presentation.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to `presentation/dashboard/dashboard_page.js`.
3. Replace the old single-value read rule:
   - rename the visible column from `纯债价值` to `纯债溢价`
   - first-line primary value = `转债价格 / 纯债价值 - 1`
   - second-line secondary value = `纯债价值`
4. Sort the column by the primary ratio value, not by pure-bond value.
5. Do not change:
   - fetch logic
   - API payload shape
   - pricing formulas
   - non-convertible modules
6. Re-run front-end syntax checks and sync to the cloud server.

Acceptance:
- Convertible main table shows `纯债溢价` instead of `纯债价值`.
- The cell displays both `纯债溢价率` and `纯债价值`.
- Clicking the header sorts by `转债价格 / 纯债价值 - 1`.

## 92. Phase CF: Convertible Force-redeem Marker Simplification (2026-03-30)

Goal: retire the current yellow full-row force-redeem highlight and simplify the
operator-facing expression into a red exclamation marker placed immediately after the
convertible bond name, with a truthful reason line such as strong-redeem date or
maturity redeem information.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to:
   - `start_server.js`
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Retire the current page expression:
   - remove the yellow row highlight
   - remove the dedicated trailing `强赎状态` column from the convertible table
4. Add a compact name-cell risk marker:
   - when the row is an active force-redeem item, append a red `!` marker after `转债名称`
   - the same name cell must show a truthful secondary reason line built only from real exposed fields
5. The reason line must reuse real fields only:
   - strong-redeem status + notice date from `forceRedeemStatus / forceRedeemNoticeDate`
   - maturity reminder from `maturityDate / maturityRedeemPrice`
   - if `maturityRedeemPrice` is missing, omit the price segment truthfully
6. Keep current business boundaries unchanged:
   - active force-redeem rows may still appear in the main table
   - top summaries / push exclusions keep their current active-force-redeem filter
   - no new data source is introduced
7. Expose `maturityRedeemPrice` through the existing public row shape so the page can render the truthful reason text.
8. Re-run front-end checks, sync the cloud server, and verify the public page.

Acceptance:
- Convertible rows no longer use yellow full-row highlighting.
- The dedicated `强赎状态` column is removed from the main convertible table.
- Active force-redeem rows show a red exclamation marker after the bond name.
- The bond-name secondary text truthfully shows strong-redeem and/or maturity information when real fields exist.

## 87. Phase CA: CB-rights-issue Web-visible 250D Sync + Cache Bust (2026-03-30)

Goal: close the last operator-visible gap after the cb-rights-issue backend switched to
true `250日后复权年化波动率`, so the public dashboard page no longer shows stale `60 日`
wording and the browser is forced to fetch the updated front-end bundle.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the dashboard presentation layer for `可转债抢权配售`:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Do not change:
   - pricing formula
   - API path
   - response payload shape
   - push schedule
   - any non-cb-rights-issue module behavior
4. Align the visible page wording with the already-active backend truth:
   - replace the remaining `60 日波动率` explanatory text with `250日波动率`
   - keep the copy consistent with the dedicated history-DB rule and `>=251` close requirement
5. Force the browser to pick up the refreshed dashboard bundle by bumping the dashboard script version query in the template.
6. Sync the changed front-end files to the cloud server and verify:
   - public homepage serves the new template
   - cb-rights-issue panel visible text reflects `250日波动率`
   - public API continues returning the already-fixed `volatility250`

Acceptance:
- The public cb-rights-issue page no longer shows stale `60 日波动率` wording.
- The dashboard template references a new front-end bundle version token so browser cache does not mask the change.
- No cb-rights-issue calculation or API contract regresses in this round.

## 88. Phase CB: Convertible Theoretical-option Columns Expansion (2026-03-30)

Goal: extend the convertible main table right after `理论溢价` with three operator-facing
derived columns so the page can directly compare:
- theoretical option value
- implied option value
- their difference

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible dashboard presentation layer:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Do not change:
   - fetch logic
   - theoretical-pricing formula
   - public API path
   - push behavior
4. Reuse existing truthful fields only:
   - `callOptionValue` / `putOptionValue` / `pricingFormula`
   - `price`
   - `pureBondValue`
5. Add three visible columns after `理论溢价`:
   - `理论期权价值`
   - `隐含期权价值`
   - `期权折价率`
6. Fix their live read rules:
   - `理论期权价值 =` existing theoretical option value already implied by the pricing chain
   - `隐含期权价值 = 转债价格 - 纯债价值`
   - `期权折价率 = 隐含期权价值 / 理论期权价值 - 1`
7. Keep the new columns sortable and bump the dashboard bundle token so browsers fetch the new page code after deployment.

Acceptance:
- The convertible main table shows the three new columns immediately after `理论溢价`.
- The three new columns are computed from existing truthful fields and do not require API expansion.
- Sorting and existing convertible fields continue working.

## 89. Phase CC: Convertible Option-discount-rate Definition Correction (2026-03-30)

Goal: correct the just-added convertible option comparison column again so it matches the
latest user definition:
`期权折价率 = 隐含期权价值 / 理论期权价值 - 1`

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the convertible dashboard presentation layer:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Do not change:
   - fetch logic
   - theoretical-pricing formula
   - API payload shape
   - push behavior
4. Replace the read rule only:
   - `理论期权价值` unchanged
   - `隐含期权价值` unchanged
   - rename `期权比例` to `期权折价率`
   - `期权折价率 = 隐含期权价值 / 理论期权价值 - 1`
5. When `理论期权价值` is `0` or missing, keep the cell empty truthfully.
6. Bump the dashboard bundle token again and sync to the cloud server.

Acceptance:
- The live page no longer shows the old `期权比例` label.
- The live page computes `期权折价率` as `隐含期权价值 / 理论期权价值 - 1`.
- Existing convertible columns and sorting remain usable.

## 90. Phase CD: Convertible Summary / Push Force-redeem Exclusion (2026-03-30)

Goal: exclude active force-redeem convertibles from the operator-facing convertible
top summaries and related push lists, while keeping those rows visible in the main
convertible table.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to summary / push selection only:
   - `strategy/convertible_bond/service.js`
   - `start_server.js`
   - `presentation/dashboard/dashboard_page.js`
3. Do not change:
   - main table membership
   - pricing formula
   - API route paths
   - non-convertible modules
4. Add one shared active-force-redeem exclusion rule:
   - rows with active published force-redeem semantics are excluded from:
     - convertible top summaries
     - main summary convertible markdown picks
     - convertible discount monitor / signal push lists
   - terminal/delisted rows remain governed by the existing terminal filter
5. Keep the main table unchanged:
   - active force-redeem rows may still remain visible in the live convertible table
   - they are only excluded from the summary/push candidate sets
6. Sync to cloud and verify with at least one known strong-redeem sample.

Acceptance:
- Convertible page top summary cards no longer include active force-redeem rows.
- Main summary push no longer picks active force-redeem rows for convertible highlights.
- Convertible independent push chains also skip active force-redeem rows.
- Main convertible table still shows those rows when they are otherwise live.

## 91. Phase CE: Convertible Option-discount Cell Adds Option Gap (2026-03-30)

Goal: keep the existing convertible option columns and pricing formula unchanged, but make the `期权折价率` cell more useful by also showing the option-value gap below the rate.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to dashboard presentation files:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Do not change:
   - fetch logic
   - theoretical-pricing formula
   - API payload shape
   - push behavior
4. Keep existing reads unchanged:
   - `理论期权价值`
   - `隐含期权价值`
   - `期权折价率`
5. Add one new derived display-only helper:
   - `期权价差 = 理论期权价值 - 隐含期权价值`
6. Render the `期权折价率` column as a compact stacked cell:
   - first line: `期权折价率`
   - second line: `期权价差`
7. Keep sorting on the column bound to `期权折价率`, not the rendered text.
8. Bump the dashboard bundle token and sync to the cloud server.

Acceptance:
- The live `期权折价率` column shows both the rate and the option gap.
- `期权价差` uses `理论期权价值 - 隐含期权价值`.
- Existing convertible columns, formulas, and sort behavior remain usable.

## 92. Phase CF: Convertible Summary Push And Top-card Filter Tightening (2026-03-30)

Goal: tighten the convertible regular-summary candidate set for both the top summary cards and the timed main push, while leaving the low-premium monitor and its own push chain unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Add one shared convertible summary helper in `strategy/convertible_bond/service.js` for:
   - exclude active force-redeem rows
   - exclude rows with `remainingYears > 1`
   - exclude non-live / terminal rows through the existing delist-expiry gate
3. Reuse that helper in:
   - `start_server.js` convertible summary shaping
   - `notification/styles/markdown_style.js` timed main summary section
4. Keep the low-premium monitor chain unchanged:
   - do not change buy/sell thresholds
   - do not change timed monitor push
   - do not change discount monitor summary
5. Narrow the timed main summary convertible content to two fixed groups:
   - `双低前3`
   - `理论溢价率前3`
6. Add `期权折价率` text to the timed main summary theoretical-premium rows.
7. Keep the dashboard top cards aligned with the same summary-eligible row set.

Acceptance:
- Top convertible summary cards exclude active force-redeem rows, rows with more than one year remaining, and terminal/non-live rows.
- Timed main summary push uses the same filter.
- Timed main summary push convertible section shows only `双低前3` and `理论溢价率前3`.
- Theoretical-premium push rows include `期权折价率`.
- Low-premium monitor list and low-premium monitor push remain unchanged.

## 95. Phase CG: Convertible Summary Time-filter Removal (2026-03-30)

Goal: remove the just-added `remainingYears` time gate from convertible top summaries and the timed main summary push, while keeping the active force-redeem and terminal-row exclusions unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this rollback isolated to the regular-summary candidate path:
   - `strategy/convertible_bond/service.js`
   - `start_server.js`
   - `notification/styles/markdown_style.js`
   - `presentation/dashboard/dashboard_page.js`
3. Retain only two shared summary exclusions:
   - active force-redeem rows
   - terminal / non-live rows through existing sanitation
4. Remove the `remainingYears <= 1` requirement from:
   - top summary cards
   - timed main summary push
5. Keep unchanged:
   - low-premium monitor and its push path
   - timed summary convertible content structure
   - theoretical row `期权折价率` text

Acceptance:
- Convertible top summary cards no longer exclude rows solely because `remainingYears > 1`.
- Timed main summary push uses the same no-time-gate candidate set.
- Active force-redeem and terminal rows still stay excluded from those regular summaries.
- Low-premium monitor list and low-premium monitor push remain unchanged.


Goal: remove all retired overseas LOF behavior from the live LOF module without taking
down the remaining LOF page or other modules.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and the dashboard API contract first.
2. Keep this round isolated to the LOF chain:
   - `config.yaml`
   - `data_fetch/lof_arbitrage/source.py`
   - `strategy/lof_arbitrage/service.py`
   - `presentation/routes/market_routes.js`
   - `presentation/dashboard/dashboard_page.js`
   - `LOF套利策略.md`
3. Remove all historical overseas group wiring:
   - LOF visible groups become only `index` and `asia`
   - LOF default group becomes `index`
4. Keep the remaining module behavior intact:
   - `GET /api/market/lof-arbitrage` path remains unchanged
   - limited/unlimited monitor pools continue working on the remaining rows
   - LOF independent push path remains available
5. Re-run repo searches and minimal checks, then sync to the cloud server and verify the
   public page/API.

Acceptance:
- The live LOF page exposes only `指数LOF` and `QDII亚洲`.
- Remaining `指数LOF / QDII亚洲` page, API, and push behavior keep working.

## 92. Phase CF: Subscription Footnote Removal (2026-03-30)

Goal: remove the explanatory footnote block from the top `股债打新` section while keeping
all main-tab module footnotes unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to the dashboard presentation-config path:
   - `config.yaml`
3. Remove the active `presentation.dashboard_module_notes.subscription` content so the
   shared footnote renderer naturally hides the entire card for the subscription section.
4. Do not change:
   - subscription data source
   - subscription table fields
   - same-day stage judgment
   - other module footnotes
5. Re-parse config, sync to the cloud server, and verify the homepage top section no
   longer shows the subscription note block.

Acceptance:
- `股债打新` no longer renders a `页面注释` block.
- Other modules still keep their current footnotes.
- No subscription table/API behavior regresses.

## 93. Phase CG: Convertible Weighted-discount Factor Simplification (2026-03-30)

Goal: simplify the live `可转债套利` weighted-discount factor chain so the ATR and sell-
pressure coefficients use the user-specified direct formulas, while keeping the market
coefficient, page structure, API path, and push chain unchanged.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first, and sync the strategy note
   document `可转债折价策略.md`.
2. Keep this round isolated to the convertible discount-strategy chain:
   - `strategy/convertible_bond/service.js`
   - `presentation/dashboard/dashboard_page.js`
   - related live docs only
3. Replace the active factor definitions with:
   - `atrCoefficient = stockAtr20Pct`
   - `sellPressureCoefficient = stockAvgTurnoverAmount20Yi / remainingSizeYi`
   - `boardCoefficient` stays on the current board-mapping rule
4. Recompute:
   - `weightedDiscountRate = (-premiumRate) * atrCoefficient * sellPressureCoefficient * boardCoefficient`
5. Keep public path and visible field names stable:
   - `GET /api/market/convertible-bond-arbitrage` stays unchanged
   - `ATR系数/ATR% / 抛压系数 / 市场 / 加权折价` columns stay visible
6. Update the factor-column helper text so the sell-pressure secondary line reflects the
   new `成交额 / 剩余规模` direction.
7. Run minimal checks, then sync to the cloud server and verify service/API health.

Acceptance:
- This phase's ATR direct-equals rule is later superseded by Phase CH in the same day.
- The live `抛压系数` equals `20日均成交额 / 剩余规模`.
- `市场系数` remains unchanged.
- `加权折价率` is recomputed with the new direct coefficients.
- Convertible page, API path, and push chain remain available after deployment.

## 94. Phase CH: Convertible ATR-coefficient Definition Reset (2026-03-30)

Goal: keep the simplified sell-pressure rule and the existing market coefficient, but
reset the live `ATR系数` definition to the user-specified ratio:
`转股溢价率绝对值 / ATR百分比`.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first, and sync
   `可转债折价策略.md`.
2. Keep this round isolated to the convertible weighted-discount path:
   - `strategy/convertible_bond/service.js`
   - convertible strategy docs
   - optional dashboard wording only if needed for accuracy
3. Replace the live ATR-coefficient rule with:
   - `stockAtr20Pct = stockAtr20 / stockPrice * 100`
   - `atrCoefficient = abs(-premiumRate) / stockAtr20Pct`
4. Keep unchanged:
   - `sellPressureCoefficient = stockAvgTurnoverAmount20Yi / remainingSizeYi`
   - current board coefficient mapping
   - `weightedDiscountRate = (-premiumRate) * atrCoefficient * sellPressureCoefficient * boardCoefficient`
5. Run minimal checks, then sync to the cloud server and verify the API.

Acceptance:
- The live `atrCoefficient` no longer equals `stockAtr20Pct`.
- The live `atrCoefficient` equals `abs(-premiumRate) / stockAtr20Pct`.
- `sellPressureCoefficient`, `boardCoefficient`, and API path remain unchanged.
- Convertible page and push chain remain usable after deployment.

## 95. Phase CI: Convertible Long-call Strike Reset To Max Rule (2026-03-30)

Goal: correct the live convertible theoretical-pricing rule so the long-call strike is no
longer fixed to `转股价`, but instead uses the higher value between `转股价` and
`纯债价值 / 对应股数`.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first, and sync
   `可转债折价策略.md`.
2. Keep this round isolated to the convertible theoretical-pricing path:
   - `data_fetch/convertible_bond/source.py`
   - `presentation/dashboard/dashboard_page.js`
   - related pricing docs only
3. Replace the live long-call strike rule with:
   - `optionQty = 100 / convertPrice`
   - `bondFloorStrike = pureBondValue / optionQty`
   - `longCallStrike = max(convertPrice, bondFloorStrike)`
4. Keep unchanged:
   - short-call strike still uses `redeemTriggerPrice`
   - option model stays `american_binomial`
   - `theoreticalPrice = bondValue + max(longCallValue - shortCallValue, 0)`
5. Update the dashboard formula hint so it no longer claims
   `call(转股价) - call(强赎价)` when the true long strike may be higher.
6. Re-run minimal checks, then sync to the cloud server and verify sample bonds such as
   `123049` reflect the new strike rule.

Acceptance:
- The live `callStrike*` fields no longer blindly equal `convertPrice`.
- The live long-call strike equals `max(convertPrice, pureBondValue / optionQty)`.
- The page formula hint and docs describe the new strike rule truthfully.
- Convertible page and API remain available after deployment.

## 94. Phase CH: Convertible Header Wrap + Width Compression (2026-03-30)

Goal: keep the convertible table fields unchanged, but stop long header labels from
expanding column widths by allowing controlled multi-line header text and slightly
compressing convertible column widths.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep this round isolated to dashboard presentation files:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
3. Do not change:
   - convertible data fields
   - sort semantics
   - API payload shape
   - non-convertible modules
4. Add a header rendering contract so convertible columns may provide explicit multi-line
   header HTML such as:
   - `隐含期<br>权价值`
   - `期权<br>折价率`
5. Apply the wrap behavior only to convertible table headers and keep body cells on the
   current compact single-line layout.
6. Reduce convertible header/cell horizontal padding and selected convertible min-widths
   so the page becomes denser without breaking readability.
7. Re-run front-end checks and sync to the cloud server.

Acceptance:
- Long convertible headers wrap to multiple lines instead of forcing wider columns.
- The convertible table becomes visibly narrower/denser than before.
- Sort buttons and sort behavior remain usable.

## 96. Phase CJ: CB-rights-issue Single-table Yield Rebase + In-list Pinning (2026-04-16)

Goal: rebuild the live `可转债抢权配售` page into one dense main table, switch
the issue-ratio and margin-share rules to the latest user definition, and narrow the
independent push to only the two list-priority groups.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and `可转债抢权配售策略.md` first.
2. Keep this round isolated to the cb-rights-issue chain:
   - `data_fetch/cb_rights_issue/source.py`
   - `strategy/cb_rights_issue/service.py`
   - `presentation/dashboard/dashboard_page.js`
   - `notification/styles/cb_rights_issue_markdown.js`
   - `notification/cb_rights_issue/service.js`
3. Replace the live issue-ratio rule:
   - `总市值` comes from real-time stock API
   - `发行比例 = 发行规模 / 总市值`
   - do not continue using required-share reverse inference as the public ratio rule
4. Replace the live share/fund rules:
   - `配售股数 = 原始所需股数`
   - `两融所需股数 = ceil((原始所需股数 * 0.6) / 50) * 50`
   - `所需资金 = 配售股数 * 正股现价`
   - `两融所需资金 = 两融所需股数 * 正股现价`
5. Replace the page structure:
   - remove all top summary / status / reminder cards
   - remove the second source table
   - render one dense main table only
   - remove the detail panel path
6. Add in-list pinning only:
   - first pin `进入申购阶段`
   - then pin `预期收益率 > 6%`
   - keep the rest below
7. Narrow the independent push to two non-overlapping groups:
   - apply-stage rows first
   - then non-apply rows with `预期收益率 > 6%`
   - push text must include `两融收益率` and `两融收益率去皮`
8. Run minimal checks after implementation.

Acceptance:
- The live cb-rights-issue page no longer shows summary cards or a second source table.
- `发行比例` reads as `发行规模 / 总市值` using real API market value.
- `两融所需股数` follows the new `原始股数 * 0.6 -> 50股向上取整` rule.
- The visible list is pinned by apply-stage first, then `预期收益率 > 6%`.
- Independent push only covers those two groups and includes margin yield metrics.

## 97. Phase CK: CB-rights-issue Three-subtab Phase Split (2026-04-17)

Goal: stop expressing抢权配售 priorities through one pinned table, and instead split the
live page into three operator-facing phase views: `申购阶段` / `埋伏阶段` / `等待阶段`.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and `可转债抢权配售策略.md` first.
2. Keep this round isolated to the cb-rights-issue presentation contract:
   - `presentation/dashboard/dashboard_page.js`
   - `presentation/templates/dashboard_template.html`
   - related live docs only
3. Replace the single visible table view with three subtabs:
   - `申购阶段`: rows where `inApplyStage = true`
   - `埋伏阶段`: non-apply rows whose stage is `上市委通过` or `同意注册/注册生效`, and `expectedReturnRate > 6%`
   - `等待阶段`: all remaining rows
4. Retire the old in-page pin expression:
   - no row pin badges under `正股名称`
   - no row highlight classes used to simulate pinning
   - no extra front-end pin-priority sort for cb-rights-issue tables
5. Simplify the `正股名称` cell:
   - render stock name text only
   - do not render a second line with phase or yield badges
   - do not add a standalone `年化收益率` label/tag in the name area or subtab feature tags
6. Let each subtab expose only the fields useful to that phase:
   - `股权登记日` remains visible in `申购阶段`
   - `埋伏阶段` and `等待阶段` do not keep `股权登记日` as a visible column
7. Keep data path and push path unchanged in this round:
   - `GET /api/market/cb-rights-issue`
   - `GET /api/push/cb-rights-issue-config`
   - `POST /api/push/cb-rights-issue-config`
8. Run minimal checks, sync to the cloud server, and verify the public page.

Acceptance:
- The live page shows three subtabs: `申购阶段` / `埋伏阶段` / `等待阶段`.
- `正股名称` cells contain only the stock name text.
- The old pin badges/highlight expression disappears from the page.
- `申购阶段` keeps `股权登记日`, while the other two subtabs do not show it.
- Public API and independent push remain available after deployment.
