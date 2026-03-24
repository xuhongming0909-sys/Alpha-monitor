# Dashboard API Contract

## Scope

This contract records the existing endpoints the dashboard is allowed to use for
the 001 monitor refactor feature. The feature should prefer shaping these
responses in `presentation/routes/` and `presentation/view_models/` rather than
creating new dashboard-only APIs.

## Endpoints

### `GET /api/market/exchange-rate`

- Purpose: Provide `HKD/CNY` and `USD/CNY` values for the status line.
- Required dashboard behavior:
  - Render currency values when present.
  - Keep a visible fallback when values are temporarily unavailable.

### `GET /api/market/convertible-bond-arbitrage`

- Purpose: Provide convertible bond arbitrage rows plus status-line treasury
  yield context.
- Required dashboard behavior:
  - Render long-table rows with sortable numeric columns.
  - Preserve fallback text when treasury yield is absent.

### `GET /api/market/ipo`

- Purpose: Provide IPO subscription items for the today agenda strip.

### `GET /api/market/convertible-bonds`

- Purpose: Provide convertible bond subscription items for the today agenda
  strip.

### `GET /api/market/ah`

- Purpose: Provide AH premium table data and summary candidates.

### `GET /api/market/ab`

- Purpose: Provide AB premium table data and summary candidates.

### `GET /api/monitors`

- Purpose: Provide custom monitor arbitrage rows.

### `GET /api/dividend?action=refresh`

- Purpose: Provide dividend reminder rows for today's highlights and full list.

### `GET /api/market/merger`

- Purpose: Provide merger/private announcement rows.

### `GET /api/push/config`

- Purpose: Load current push configuration into the dashboard form.
- Required response contract for the current push round:
  - `data.times`
  - `data.eventAlert.cooldownMinutes`
  - `data.eventAlert.convertibleBond.convertPremiumLt`
  - `data.deliveryStatus.lastMainPushSuccessAt`
  - `data.deliveryStatus.lastEventAlertSuccessAt`
  - `data.deliveryStatus.lastMainPushError`
  - `data.deliveryStatus.lastEventAlertError`
  - `data.deliveryStatus.webhookConfigured`
  - `data.deliveryStatus.pushHtmlUrlConfigured`
- The dashboard must not depend on merger-report push fields in this round.

### `GET /api/dashboard/ui-config`

- Purpose: Load shared dashboard table readability config for the static page.
- Required dashboard behavior:
  - Apply returned table typography and min-width settings through shared CSS variables.
  - Fall back to built-in defaults when the endpoint is temporarily unavailable.

### `POST /api/push/config`

- Purpose: Save push configuration changes from the dashboard form.
- Required dashboard behavior:
  - Submit normalized form data.
  - Render save success and failure feedback clearly.
- Current writable fields are limited to:
  - two fixed-time summary push values
  - event-alert cooldown minutes

## Contract rules

- The dashboard must not depend on hidden local mock data.
- New dashboard requirements should first try to reuse existing fields or
  presentation-layer mappings.
- If an endpoint payload must change, the change must preserve ownership:
  strategy/data-fetch produce business meaning, presentation only shapes display.

### `GET /api/market/convertible-bond-arbitrage` field additions (2026-03-25)

- The public row contract now additionally allows:
  - `stockAtr20`
  - `remainingSizeYi`
  - `stockAvgTurnoverAmount20Yi`
  - `stockAvgTurnoverAmount5Yi`
- Required dashboard behavior:
  - render these as visible main-table columns for the convertible-bond list
  - preserve `亿` as the turnover/remaining-size display unit
