# Dashboard API Contract

## Scope

This contract records the active dashboard-facing endpoints for the
`001-monitor-refactor` feature. The dashboard should prefer reusing these
interfaces and lightweight presentation shaping instead of adding heavy
dashboard-only data paths.

## Endpoints

### `GET /api/health`

- Purpose: Provide layered runtime health for the header status area.

### `GET /api/dashboard/ui-config`

- Purpose: Provide shared dashboard presentation config.
- Required dashboard behavior:
  - apply table typography and min-width settings through CSS variables
  - read dashboard auto-refresh config from the same payload
  - fall back to built-in defaults when temporarily unavailable

### `GET /api/dashboard/resource-status`

- Purpose: Provide lightweight cache/status metadata for minute polling without
  forcing a full table reload.
- Query:
  - `keys=exchangeRate,ipo,bonds,cbArb,ah,ab,merger,cbRightsIssue`
- Required item fields:
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`
  - `refreshing`
- Required dashboard behavior:
  - poll this endpoint on the `60s` dashboard loop
  - reload full table data only when metadata changed
  - allow non-dataset tabs to keep normal active-tab-only reload behavior

### `GET /api/market/exchange-rate`

- Purpose: Provide `HKD/CNY` and `USD/CNY` values for the status line.

### `GET /api/market/ipo`

- Purpose: Provide IPO subscription items for the header agenda strip.

### `GET /api/market/convertible-bonds`

- Purpose: Provide convertible-bond subscription items for the header agenda strip.

### `GET /api/market/convertible-bond-arbitrage`

- Purpose: Provide convertible-bond arbitrage rows plus treasury-yield context.
- Required dashboard behavior:
  - render long-table rows with sortable numeric columns
  - preserve fallback text when treasury yield is absent
- The outward payload may additionally expose:
  - `updateTime`
  - `cacheTime`
  - `servedFromCache`
  - `refreshing`
- Convertible-specific field additions already used by the page include:
  - `stockAtr20`
  - `remainingSizeYi`
  - `stockAvgTurnoverAmount20Yi`
  - `stockAvgTurnoverAmount5Yi`
  - `forceRedeemStatus`
  - `delistDate`
  - `ceaseDate`
- Required dashboard behavior for this round:
  - open directly from the latest available cache payload when present
  - not wait for `sync-cb-stock-history` during ordinary page reads
  - use metadata changes to decide whether a full reload is necessary

### `GET /api/market/ah`

- Purpose: Provide AH premium table data and summary candidates.

### `GET /api/market/ab`

- Purpose: Provide AB premium table data and summary candidates.

### `GET /api/market/event-arbitrage`

- Purpose: Provide event-arbitrage grouped data for the event module.

### `GET /api/market/cb-rights-issue`

- Purpose: Provide the rights-issue module dataset and rebuild status.
- Compatibility note for the current live round:
  - `data.monitorList` may still exist, but it is a reserved compatibility field and should be treated as empty.
  - the live product expression is now `sourceRows` + the three phase groups rendered by the dashboard.

### `GET /api/market/lof-arbitrage`

- Purpose: Provide the LOF arbitrage dataset for the LOF module.
- Required response fields include at least:
  - `data.groups`
  - `data.defaultGroup`
  - `data.rows`
  - `data.limitedMonitorRows`
  - `data.unlimitedMonitorRows`
  - `data.sourceSummary`
  - `data.rebuildStatus`
- Effective live LOF group contract for this round:
  - `groups` contains only `index` and `asia`
  - `defaultGroup = index`

### `GET /api/monitors`

- Purpose: Provide custom monitor arbitrage rows.

### `GET /api/dividend?action=portfolio`

- Purpose: Provide the current dividend watchlist payload.

### `GET /api/dividend?action=refresh`

- Purpose: Provide refreshed dividend reminder rows for highlights and the full list.

### `GET /api/push/config`

- Purpose: Load current push configuration into the dashboard form.
- Required response fields include at least:
  - `data.times`
  - `data.eventAlert.cooldownMinutes`
  - `data.eventAlert.convertibleBond.convertPremiumLt`
  - `data.deliveryStatus.lastMainPushSuccessAt`
  - `data.deliveryStatus.lastEventAlertSuccessAt`
  - `data.deliveryStatus.lastMainPushError`
  - `data.deliveryStatus.lastEventAlertError`
  - `data.deliveryStatus.webhookConfigured`
  - `data.deliveryStatus.pushHtmlUrlConfigured`

### `POST /api/push/config`

- Purpose: Save push configuration changes from the dashboard form.

### `GET /api/push/lof-arbitrage-config`

- Purpose: Load current LOF independent push status into the LOF module card.
- Required response fields include at least:
  - `data.enabled`
  - `data.times`
  - `data.tradingDaysOnly`
  - `data.deliveryStatus.webhookConfigured`
  - `data.deliveryStatus.schedulerEnabled`
  - `data.deliveryStatus.lastSuccessAt`
  - `data.deliveryStatus.lastError`
- Required dashboard behavior for this round:
  - treat `data.times` as a single-slot contract
  - render the fixed LOF push time as `14:00`
  - not render retired instant-push status wording

### `POST /api/push/lof-arbitrage-config`

- Purpose: Keep a compatibility write path for LOF push config.
- Effective contract for this round:
  - the saved schedule must resolve to one trading-day slot at `14:00`
  - the dashboard must not expose the old three-time editable workflow

## Contract rules

- The dashboard must not depend on hidden local mock data.
- New dashboard behavior should first try to reuse existing routes and metadata.
- If an endpoint payload changes, ownership stays split:
  - strategy/data-fetch defines business meaning
  - presentation only shapes display
