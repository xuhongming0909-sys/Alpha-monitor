# Dashboard UI Tuning Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rework the dashboard layout so push settings live at the page bottom, convertible-bond summaries are compact, and the whole page becomes more readable on desktop without changing business formulas or APIs.

**Architecture:** Keep the existing single-page dashboard and current `/api/*` contracts. Implement the change by updating the HTML template structure, tightening summary rendering in the dashboard script, and making push-setting hydration/save behavior always reflect the latest server response.

**Tech Stack:** Node.js, Express static page delivery, vanilla JavaScript dashboard, inline CSS in `presentation/templates/dashboard_template.html`

---

### Task 1: Update the feature contract docs

**Files:**
- Modify: `refactor_docs/001-monitor-refactor/plan.md`
- Modify: `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
- Modify: `refactor_docs/001-monitor-refactor/SPEC.md`

**Step 1: Write the target UI contract**

Document these behaviors:

- Push settings move to the page bottom and render as a simple strip without a bordered card.
- Push settings must read, save, and immediately rehydrate from the server response.
- Convertible-bond summaries become compact columns with fewer items.
- Global typography and desktop table readability increase.

**Step 2: Review the docs for conflicts**

Run: `rg -n "推送设置|转债套利|首页结构|响应式|字号" refactor_docs/001-monitor-refactor`
Expected: matching sections point to the new layout contract instead of the old top-right push card.

**Step 3: Save the doc updates**

Run: `git diff -- refactor_docs/001-monitor-refactor/plan.md refactor_docs/001-monitor-refactor/REQUIREMENTS.md refactor_docs/001-monitor-refactor/SPEC.md`
Expected: only contract/documentation changes are shown.

### Task 2: Reshape the dashboard template

**Files:**
- Modify: `presentation/templates/dashboard_template.html`

**Step 1: Move push settings to the page bottom**

Replace the top two-column shell with:

- top hero
- top subscription section
- tab nav
- tab panels
- footer push-settings strip

**Step 2: Increase typography and width**

Adjust:

- `app-shell` width
- title, tab, table, input, and button font sizes
- paddings and row heights
- summary/card density

**Step 3: Verify the template structure**

Run: `rg -n "push-panel|push-strip|top-grid|tab-nav|tab-panels" presentation/templates/dashboard_template.html`
Expected: the push strip appears at the bottom and the old top-right push card structure is gone.

### Task 3: Fix push-settings hydration and save feedback

**Files:**
- Modify: `presentation/dashboard/dashboard_page.js`

**Step 1: Always hydrate inputs from current server data**

Update `renderPushSettings()` so the three time inputs always reflect the latest `GET /api/push/config` or `POST /api/push/config` response instead of only filling empty inputs.

**Step 2: Preserve user-visible status feedback**

Keep these signals:

- loading text
- error text
- enabled/disabled text
- save toast

**Step 3: Verify the save payload and readback path**

Run: `rg -n "renderPushSettings|savePushConfig|pushTime1|pushTime2|pushTime3" presentation/dashboard/dashboard_page.js`
Expected: one clear load/render path and one clear save/readback path.

### Task 4: Compact the convertible-bond summary area

**Files:**
- Modify: `presentation/dashboard/dashboard_page.js`
- Modify: `presentation/templates/dashboard_template.html`

**Step 1: Reduce summary card height**

Change the convertible-bond panel so:

- summary items per column are reduced
- summary rows become denser
- the table appears earlier on the screen

**Step 2: Keep the existing data contract**

Do not change:

- `/api/market/convertible-bond-arbitrage`
- sorting/pagination logic
- conversion formulas

**Step 3: Verify summary rendering references**

Run: `rg -n "renderConvertibleBondPanel|summary-grid|renderSummaryCard|convertSpread" presentation/dashboard/dashboard_page.js`
Expected: the panel still renders the three summary groups, but with compact presentation.

### Task 5: Run project checks

**Files:**
- Test: `presentation/templates/dashboard_template.html`
- Test: `presentation/dashboard/dashboard_page.js`

**Step 1: Run the existing checks**

Run: `npm run check`
Expected: PASS

**Step 2: Run the boundary check**

Run: `npm run check:boundaries`
Expected: PASS

**Step 3: Review final diff**

Run: `git diff -- presentation/templates/dashboard_template.html presentation/dashboard/dashboard_page.js refactor_docs/001-monitor-refactor/plan.md refactor_docs/001-monitor-refactor/REQUIREMENTS.md refactor_docs/001-monitor-refactor/SPEC.md docs/plans/2026-03-21-dashboard-ui-tuning.md`
Expected: diff matches the documented UI contract and does not alter backend formulas.
