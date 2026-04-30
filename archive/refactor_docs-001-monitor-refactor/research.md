# Research: Alpha Monitor Dashboard Refactor

## Decision 1: Reuse existing `/api/*` endpoints instead of creating dashboard-only APIs

**Rationale**:
- `SPEC.md` explicitly constrains the dashboard to consume existing interfaces.
- The constitution requires clean responsibility boundaries, so new display
  needs should first be solved in `presentation/routes/` and
  `presentation/view_models/`, not by inventing root-level shortcuts.
- This keeps fetch cadence, caching, and notification inputs aligned with the
  same upstream datasets already used elsewhere.

**Alternatives considered**:
- Add a dedicated dashboard aggregation API in `start_server.js`.
  Rejected because it would re-centralize presentation-specific composition in a
  top-level entry file.

## Decision 2: Keep a single dashboard page implementation and strengthen module helpers

**Rationale**:
- The current system already has `presentation/templates/dashboard_template.html`
  plus `presentation/dashboard/dashboard_page.js` and module helpers.
- The requirements call for one desktop/mobile experience, not two separate
  screens.
- If complexity grows, splitting helper logic inside `presentation/dashboard/`
  is cheaper than adding a second rendering surface.

**Alternatives considered**:
- Rebuild the dashboard as multiple standalone pages.
  Rejected because it would fight the current tab-based UX contract and add
  needless routing complexity.

## Decision 3: Treat push settings as notification-owned state with presentation-owned form behavior

**Rationale**:
- Persistence and normalization already belong to
  `notification/scheduler/push_config_store.js`.
- The dashboard only needs load, edit, validate, and submit behavior.
- This preserves the constitution rule that presentation must not absorb
  notification business rules.

**Alternatives considered**:
- Move push settings logic fully into `presentation/dashboard/dashboard_page.js`.
  Rejected because it would duplicate validation and blur ownership.

## Decision 4: Use shared table interaction rules for CB arbitrage, AH premium, and AB premium

**Rationale**:
- The spec calls for consistent sorting, pagination, sequence numbering, and
  responsive long-table behavior across these three modules.
- Shared client-side helpers reduce divergence while keeping each dataset's
  column mapping explicit.

**Alternatives considered**:
- Implement three unrelated table controllers.
  Rejected because it increases regression risk and violates the "change one
  class of requirement, touch one path" principle.

## Decision 5: Verification must combine server smoke, CLI checks, and manual browser checks

**Rationale**:
- `npm run check` only confirms server health.
- The constitution explicitly requires keeping existing CLI validation such as
  `python data_dispatch.py exchange-rate` and `python data_dispatch.py ah`.
- The dashboard contract also depends on visual behaviors like sorting,
  pagination, empty states, and responsive layout that are not covered by the
  current automated checks.

**Alternatives considered**:
- Rely only on the existing health endpoint smoke check.
  Rejected because it would miss the core UI contract regressions this feature
  is meant to control.
