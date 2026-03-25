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

## 22. Phase S: LOF Arbitrage Zero-login MVP (2026-03-23)

Goal: add a first production-safe `LOF濂楀埄` module without destabilizing the existing homepage, while continuing to investigate zero-login IOPV sources in parallel.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new LOF module contract, zero-login scope, and IOPV fallback rules.
2. Keep the current Node + Python layered architecture:
   - `data_fetch/lof_arbitrage` only fetches and normalizes Jisilu QDII rows
   - `strategy/lof_arbitrage` only computes signal basis, fees, and action status
   - `presentation` only exposes the new API and dashboard tab
3. Use direct public JSON endpoints as phase-1 primary source:
   - `/data/qdii/qdii_list/E`
   - `/data/qdii/qdii_list/A`
   - `/data/qdii/qdii_list/C`
4. Do not block phase 1 on official IOPV completeness:
   - if `iopv` / `iopv_discount_rt` is available, use it as high-confidence signal
   - else if intraday estimate fields are available, use them as medium-confidence signal
   - else degrade to NAV premium as low-confidence observation only
5. Keep Firecrawl out of the hot path in this round:
   - direct JSON first
   - Firecrawl only documented as future fallback if the public JSON disappears
6. Add a new public API `GET /api/market/lof-arbitrage`.
7. Add a new top-level dashboard tab `LOF濂楀埄` with one phase-1 table, summary cards, and always-visible risk/detail rows.
8. Keep the module webpage-only in phase 1:
   - no push integration
   - no auto-execution
   - no changes to existing modules beyond adding the new tab and refresh path
9. Record the ongoing IOPV search status explicitly in the outward payload so the UI can show whether the current zero-login chain has usable IOPV or only NAV fallback.

Acceptance:
- The homepage still opens normally after the new LOF module is added.
- `GET /api/market/lof-arbitrage` returns real rows from the zero-login Jisilu QDII endpoints.
- The `LOF濂楀埄` page shows:
  - current price
  - NAV premium
  - IOPV premium when publicly available
  - estimate premium when publicly available
  - signal basis
  - apply status
  - action status
- When IOPV is missing, the page clearly downgrades to observation mode instead of pretending the signal is execution-grade.
- A single-source failure in one LOF category degrades only that category and does not blank the homepage.

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

## 24. Phase U: LOF Authenticated Enrichment + Market Subtabs (2026-03-23)

Goal: upgrade the current `LOF濂楀埄` MVP into a fuller real-data page that is closer to the live Jisilu reading path, while still refusing to fabricate unavailable `IOPV` fields.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the current layered architecture:
   - `data_fetch/lof_arbitrage` only fetches source rows and cache fallback
   - `strategy/lof_arbitrage` only computes outward row semantics and overview
   - `presentation` only renders page structure and columns
3. Add optional authenticated enhancement on top of the current Jisilu QDII endpoints:
   - if `data_fetch.plugins.lof_arbitrage.jisilu_cookie` is configured, send it and use the larger logged-in result set
   - if cookie is missing or invalid, automatically fall back to the public result set
4. Keep truthfulness strict:
   - more rows are allowed after login enhancement
   - `IOPV` / `IOPV婧环鐜嘸 may still stay empty
   - outward payload and UI must state that clearly instead of inventing values
5. Expand standardized LOF fields so the page can render the practical long-table view, including:
   - code / name / issuer
   - current price / change rate / 鎴愪氦棰?   - 鍦哄唴浠介 / 鍦哄唴鏂板浠介
   - T-2 鍑€鍊?/ 鍑€鍊兼棩鏈?/ 鍑€鍊兼孩浠?   - IOPV / IOPV婧环
   - 浼板€?/ 浼板€兼孩浠?   - 鐩稿叧鎸囨暟 / 鎸囨暟娑ㄥ箙
   - 鐢宠喘璐?/ 鐢宠喘鐘舵€?/ 璧庡洖璐?/ 璧庡洖鐘舵€?/ 绠℃墭璐?   - 瀹樻柟鍩洪噾椤甸摼鎺?/ 闆嗘€濆綍璇︽儏閾炬帴
6. Refactor the LOF page into visible market subtabs:
   - `娆х編甯傚満`
   - `浜氭床甯傚満`
   - `鍟嗗搧`
7. Keep the module stable-first:
   - no push integration
   - no auto-trading semantics
   - a single-source failure only degrades the affected subtab

Acceptance:
- `LOF濂楀埄` can display the larger logged-in dataset when a valid cookie is present, while still working without it.
- The page exposes more of the real Jisilu fields instead of only the MVP summary view.
- `娆х編甯傚満 / 浜氭床甯傚満 / 鍟嗗搧` can be switched directly inside the LOF module.
- `IOPV` fields remain empty when the source truly does not return them, and the UI explains that they are currently unavailable.
- Homepage stability and other modules remain unaffected.

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

## 25. Phase V: LOF Estimated-value Completion From Source Change Rate (2026-03-23)

Goal: complete the currently missing actionable LOF estimate fields by deriving them only from real Jisilu source fields, while keeping `IOPV` empty unless the upstream truly returns it.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the derived-estimate contract.
2. Keep the LOF source truth contract strict:
   - `IOPV` is still direct-source only
   - `IOPV婧环鐜嘸 is still direct-source only
   - `浼板€糮 and `浼板€兼孩浠穈 may be derived only when Jisilu already provides `est_val_increase_rt`
3. Add a deterministic source-based derivation path:
   - `estimatedValue = navValue * (1 + est_val_increase_rt / 100)`
   - `estimatedPremiumRate = ((currentPrice / estimatedValue) - 1) * 100`
4. Persist derivation provenance in the outward payload so the page can explain where the value came from:
   - direct source
   - derived from `est_val_increase_rt`
5. Expand the LOF page so the strategy view is easier to use:
   - add visible `缁撹`
   - add visible `淇″彿婧环`
   - add estimate-source, estimate-time, estimate-change, reference-price, and calculation-tips detail fields
6. Keep deployment risk low:
   - no push integration changes
   - no homepage root-tab changes
   - no changes to unrelated modules

Acceptance:
- Rows with real `est_val_increase_rt` now expose `estimatedValue` and `estimatedPremiumRate` instead of leaving the estimate area blank.
- `IOPV` and `IOPV婧环鐜嘸 remain empty when upstream still does not provide them.
- LOF main table visibly shows `缁撹` and `淇″彿婧环`.
- LOF detail area clearly explains whether the estimate is direct-source or derived from Jisilu estimate-change fields.
- The page remains loadable even if one LOF source category fails.

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
## 27. Phase Y: LOF Summary-card Removal + Detail-first Reading Path (2026-03-24)

Goal: simplify the `LOF濂楀埄` page by removing the current top summary-card band and making the long-table detail rows the default supplementary reading path.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Keep the LOF fetch/strategy/API schema unchanged in this round:
   - `data.overview` may remain in the API for aggregation/debugging
   - no calculation or classification logic changes
3. Refine the LOF page structure contract:
   - remove the visible top summary cards `濂楀埄鍊欓€?/ 浠呰瀵?/ 鏁版嵁閾捐矾`
   - keep title/status text and market subtabs
   - keep the long table as the immediate primary reading path
4. Preserve the current always-visible secondary detail rows under each LOF item so explanatory fields remain directly readable without a separate summary-card strip.

Acceptance:
- `LOF濂楀埄` no longer renders the visible top summary-card area.
- The page still shows toolbar status, market subtabs, and the active-market long table.
- LOF secondary detail rows remain visible and continue to expose estimate/source/risk context.

## 28. Phase Z: LOF Module Cancellation From Homepage (2026-03-24)

Goal: remove `LOF濂楀埄` from the public homepage module set while keeping the rest of the dashboard stable.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Treat this round as a homepage/module-scope cancellation rather than a full backend feature purge:
   - remove the visible `LOF濂楀埄` root tab
   - remove homepage startup loading of LOF data
   - keep unrelated modules unchanged
3. Stop spending homepage/runtime preload cost on LOF:
   - dashboard bootstrap no longer requests `lofArb`
   - server preload no longer includes `lofArb`
4. Keep the existing LOF backend implementation archived in place for now, but disconnected from the public homepage reading path.

Acceptance:
- The homepage no longer shows `LOF濂楀埄`.
- Dashboard initial load no longer requests LOF data.
- Server preload no longer includes `lofArb`.
- `杞€哄鍒?/ AH / AB / 鐩戞帶濂楀埄 / 鍒嗙孩鎻愰啋 / 浜嬩欢濂楀埄` remain usable.

## 29. Phase AA: LOF Complete Removal (2026-03-24)

Goal: fully retire `LOF濂楀埄` from the repository and runtime surface instead of only hiding it from the homepage.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first.
2. Remove all active LOF runtime surfaces:
   - dashboard render/bind/bootstrap logic
   - public market route
   - server dataset registration and preload
   - `data_dispatch.py` action
3. Remove all active LOF config contracts from `config.yaml`.
4. Delete the retired implementation directories:
   - `data_fetch/lof_arbitrage`
   - `strategy/lof_arbitrage`
5. Verify the homepage still works and old LOF route access falls back to normal API 404 behavior.

Acceptance:
- No active homepage, server, route, or CLI path still references LOF.
- LOF implementation directories are removed.
- Homepage and remaining modules continue working.

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

## 55. Phase AU: LOF Arbitrage Restoration With Real Jisilu URLs (2026-03-25)

Goal: restore `LOF套利` as a new independent homepage module based on the real Jisilu LOF / QDII pages the user provided, keep the chain isolated from other modules, and land a first production version with page, API, and independent push.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the new LOF module contract.
2. Restore `LOF套利` as a new independent chain instead of reviving the older archived implementation:
   - `data_fetch/lof_arbitrage` only handles source access, normalization, source fallback, and upstream helper hydration
   - `strategy/lof_arbitrage` only handles IOPV, premium-rate, pool classification, and push payload semantics
   - `presentation` only handles route shaping, dashboard rendering, and module footnote
   - `notification/lof_arbitrage` only handles independent scheduled / instant push
3. Use the user-provided real Jisilu pages as the authoritative source entry:
   - `https://www.jisilu.cn/data/lof/#index`
   - `https://www.jisilu.cn/data/qdii/#qdiie`
   - `https://www.jisilu.cn/data/qdii/#qdiia`
4. Implement source access with the shortest truthful path:
   - Firecrawl first against the provided page URLs when configured
   - direct JSON fallback to the real page-backed list endpoints discovered from those pages
   - no fake data, no static sample rows
5. Restore the homepage root navigation from `7` to `8` tabs by adding `LOF套利`.
6. Keep the page structure fixed to:
   - top limited-monitor list
   - top non-limited-monitor list
   - one shared main table with internal filters `指数LOF / QDII欧美 / QDII亚洲`
   - module-local push settings
   - module footnote
7. Implement first-round calculation truthfulness:
   - `溢价率 = (IOPV / 现价) - 1`
   - `QDII欧美` uses `T-2` NAV with live index/fx correction when resolvable
   - `指数LOF / QDII亚洲` use `T-1` NAV with source-provided index increase and fx correction
   - rows missing enough real inputs stay visible but marked non-computable instead of being fabricated
8. Keep filter and monitoring rules fixed to the approved strategy:
   - only LOF rows
   - exclude name containing `ETF`
   - limited pool: limited apply + cap < `10万` + premium > `1%` + turnover > `100万`
   - non-limited pool: no limited apply + premium > `5%` or premium < `-5%` + turnover > `100万`
9. Add independent push:
   - instant push when a row newly enters either pool
   - scheduled full-pool push at `13:30`, `14:00`, `14:30`
   - not merged into existing summary push

Acceptance:
- Homepage root tabs increase from `7` to `8`, and one visible tab is `LOF套利`.
- `GET /api/market/lof-arbitrage` returns real data from the approved Jisilu URL chain.
- The page top area shows only `限购监控池 / 非限监控池` and their core rows.
- The main table shows the required source fields plus computed `IOPV / 溢价率`, keeps 50-row pagination, and supports internal view switching.
- Firecrawl may enhance the source path, but a missing Firecrawl key does not block direct truthful fallback.
- Existing `转债 / AH / AB / 监控 / 分红 / 事件套利 / 可转债抢权配售` behavior does not regress.

## 56. Phase AV: LOF Premium Formula + Dense Table Adjustment (2026-03-25)

Goal: align the live `LOF套利` page with the latest user rule by switching premium-rate semantics to `现价 / IOPV - 1`, removing per-row detail expansion, and making the LOF main table denser so the list fits the page better.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the revised LOF formula and table contract.
2. Keep this round isolated to the LOF module:
   - no source URL change
   - no new APIs
   - no push schedule change
3. Revise the strategy-layer premium output only:
   - `溢价率 = (现价 / IOPV - 1) × 100%`
   - keep the same truthful `IOPV` calculation paths
   - continue deriving monitor-pool eligibility from the outward `premiumRate` field after the formula switch
4. Simplify the LOF main table:
   - remove the per-row detail area entirely
   - keep business fields directly visible in the main table
   - merge naturally paired fields into compact multi-line cells where helpful
5. Preserve shared table mechanics:
   - 50-row pagination
   - sorting
   - search
   - horizontal overflow fallback

Acceptance:
- `LOF套利` rows now compute `premiumRate` with `现价 / IOPV - 1` instead of `IOPV / 现价 - 1`.
- The LOF main table no longer renders row-level detail expansion.
- The LOF table remains searchable, sortable, and paginated, while fitting common desktop widths better than before.
- Existing LOF fetch, API, and push routes remain unchanged.

## 57. Phase AW: LOF NAV-date Priority + Post-close Premium Fix (2026-03-25)

Goal: keep the live `LOF套利` chain truthful to the latest Jisilu snapshot by making
the strategy respect the actual `净值日期`, stop re-estimating rows that already have
same-day NAV, and exclude `暂停申购` samples from both monitor pools.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and `LOF套利策略.md` first with the revised LOF post-close and monitor contracts.
2. Correct the live LOF premium contract back to the currently deployed business meaning:
   - outward `premiumRate` uses the existing live reading path `溢价率 = (IOPV / 现价 - 1) × 100%`
   - the older `现价 / IOPV - 1` text is treated as superseded document drift, not as the true production contract
3. Add a same-day NAV priority rule for `指数LOF / QDII亚洲 / QDII欧美`:
   - when `navDate == priceDate` and Jisilu already returns `nav_discount_rt`
   - stop doing T-1 / T-2 extrapolation for that row
   - reuse the source-provided same-day NAV premium reading instead
   - outward `iopv` falls back to the same-day `nav` reference so the visible table remains internally consistent
4. Refine the `QDII欧美` extrapolation path so it follows the real NAV anchor date:
   - when extrapolation is still needed, choose the index / FX base values whose dates actually match `navDate`
   - do not blindly anchor every row to a hardcoded `T-2` base if the latest NAV has already advanced to `T-1`
   - if no exact NAV-date match is available, keep the existing truthful fallback order instead of fabricating a new anchor
5. Tighten monitor-pool eligibility:
   - rows with `申购状态 = 暂停申购` must stay visible in the main table
   - but they must not enter `limitedMonitorRows`
   - and must not enter `unlimitedMonitorRows`
   - therefore they also stop participating in LOF instant-push entry detection
6. Keep this round isolated to the LOF module:
   - no new source URL
   - no dashboard tab structure change
   - no non-LOF formula change
   - no push-schedule change

Acceptance:
- Same-day NAV rows no longer show stale extrapolated LOF premiums after the source has already published today’s NAV.
- `QDII欧美` rows extrapolate from the NAV-aligned base date when such a base is available, so the result tracks the latest NAV snapshot more closely.
- `暂停申购` rows remain visible in the LOF main table but disappear from both monitor pools and the related push-entry path.
- Existing `LOF` API shape, dashboard tab, and independent push runtime remain available.

## 59. Phase AX: LOF Europe/US External Market API Enrichment (2026-03-25)

Goal: add one minimal external market-data fallback for `LOF套利 > QDII欧美` so the
module no longer depends only on Jisilu `cal_tips` plus the small Tencent index map
when building IOPV inputs.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, and `LOF套利策略.md` first with the new external-helper contract.
2. Keep this round isolated to the LOF fetch chain:
   - no new dashboard tab
   - no LOF push schedule change
   - no AH / AB / convertible behavior change
3. Add one external helper provider for exact mapped `QDII欧美` indices and FX:
   - phase-1 provider is `Stooq`
   - it is used only as a fallback /补数链路, not as the main source list
4. The fetch layer must support two external补数场景:
   - fill missing `currentIndexValue`
   - fill missing nav-date-aligned `baseIndexValue / baseFxValue` when Jisilu did not provide them
5. Mapping must stay config-driven in `config.yaml`:
   - provider enable switch
   - provider URLs / timeout
   - exact index symbol map
   - exact FX symbol map
6. Truth boundary:
   - only exact configured symbols may enter the full external calculation path
   - unresolved custom indices keep the existing truthful fallback order
   - no proxy ETF / guessed symbol may be silently treated as an exact index
7. First-round target:
   - recover at least the `恒生指数` row that currently lacks enough helper inputs to compute IOPV
   - improve other exact-mapped欧美 rows without forcing fake coverage for all custom indices

Acceptance:
- `QDII欧美` rows may use external exact index / FX data when Jisilu helper fields are incomplete.
- `南方香港LOF` no longer remains stuck in `真实输入不足，未计算 IOPV` when the external HSI + HKD/CNY path is available.
- Existing rows that already have enough truthful helper inputs continue to work without regression.
- Rows whose exact external mapping still does not exist remain visible and truthfully fall back to source-estimate or missing-input status.

## 58. Phase AX: LOF T-1/T Formula Split + Europe Real-time Anchor Revision (2026-03-25)

Goal: align the live `LOF套利` implementation with the latest user rule by splitting
the formula strictly by `净值日期`, keeping `指数LOF / QDII亚洲` on a same-day direct-NAV
path, and making `QDII欧美` continue to estimate off the latest published NAV plus
real-time external index / FX inputs.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, `SPEC.md`, `LOF套利策略.md`, and the LOF module notes in `config.yaml` first.
2. Keep the outward premium meaning fixed to the current production contract:
   - `溢价率 = (IOPV / 现价 - 1) × 100%`
3. Revise `指数LOF / QDII亚洲` by NAV-date branch:
   - when `navDate` is `T-1` relative to the current trading day:
     - `IOPV = T-1日净值 × (1 + 指数涨幅) × (今日汇率 / 基准汇率)`
   - when `navDate` is the current trading day:
     - `IOPV = T日净值`
   - the index change input in both branches remains the source-side Jisilu index-change field
4. Revise `QDII欧美` so it always estimates off the latest published NAV plus real-time anchors:
   - when the published NAV is `T-2`, estimate from the `T-2` NAV anchor
   - when the published NAV has advanced to `T-1`, estimate from the `T-1` NAV anchor
   - in both cases the strategy must use real-time external market data for:
     - current index value
     - current FX value
   - if a current external quote is unavailable, degrade truthfully to the existing source-estimate fallback instead of fabricating an anchor
5. Preserve the current monitor constraint:
   - `暂停申购` rows remain visible in the main table
   - but remain excluded from both monitor pools and instant-push entry logic
6. Keep this round isolated to the LOF chain:
   - no dashboard structure change
   - no route path change
   - no non-LOF business change

Acceptance:
- `指数LOF / QDII亚洲` same-day NAV rows now output `IOPV = 当日净值` directly.
- `指数LOF / QDII亚洲` T-1 NAV rows still use the source Jisilu index-change field and FX adjustment path.
- `QDII欧美` rows with published `T-1` NAV no longer stay stuck on an older `T-2` reading path.
- `QDII欧美` rows keep using real-time external current index / FX inputs when available.
- `暂停申购` rows still stay outside both monitor pools.

## 59. Phase AY: LOF Commodity Source Recovery Into Europe/US View (2026-03-25)

Goal: restore the missing `商品LOF` rows on the live `LOF套利 > QDII欧美` page by
truthfully reading Jisilu's separate commodity source and merging it into the existing
Europe/US view without adding a new visible subtab.

Plan:
1. Update `plan.md`, `REQUIREMENTS.md`, and `SPEC.md` first with the source-recovery contract.
2. Keep this round isolated to the LOF fetch chain:
   - no dashboard tab change
   - no new visible LOF subview
   - no AH / AB / convertible / monitor behavior change
3. Extend `data_fetch.plugins.lof_arbitrage` source config with the real commodity source:
   - page `https://www.jisilu.cn/data/qdii/#qdiic`
   - api `https://www.jisilu.cn/data/qdii/qdii_list/C`
4. Fetch `commodity` as an internal source only, then merge its rows into the outward
   `europe_us` group:
   - outward page still shows only `指数LOF / QDII欧美 / QDII亚洲`
   - commodity rows remain tagged with their real source URL for traceability
5. Aggregate source summary counts truthfully so the `QDII欧美` view count reflects:
   - original Europe/US rows
   - plus commodity LOF rows
6. Keep the existing LOF sample filter unchanged:
   - still only `LOF`
   - still exclude `ETF`

Acceptance:
- Codes shown on Jisilu `商品(刷新)` such as `160216 / 162719 / 162411` appear in the dashboard `QDII欧美` view.
- No new public LOF subtab is added for commodity-only viewing.
- `QDII欧美` source-visible counts reflect the merged Europe/US + commodity source total.
- Existing `指数LOF / QDII亚洲` data and LOF push/runtime behavior do not regress.
