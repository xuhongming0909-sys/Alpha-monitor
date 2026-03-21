# Data Model: Alpha Monitor Dashboard Refactor

## 1. DashboardStatusLine

- Purpose: Top-line market summary shown under the page title.
- Sources:
  - `/api/market/exchange-rate`
  - `/api/market/convertible-bond-arbitrage` for 10Y treasury-related display
- Fields:
  - `hkdCny`
  - `usdCny`
  - `treasuryYield10y`
  - `treasuryYieldStatusText`
  - `updateTime`
- Rules:
  - Missing treasury yield must render a clear fallback text.
  - Status line remains single-row text, not separate KPI cards.

## 2. SubscriptionAgendaItem

- Purpose: Unified "today only" row in the subscription long table.
- Sources:
  - `/api/market/ipo`
  - `/api/market/convertible-bonds`
- Fields:
  - `stage`
  - `kind`
  - `name`
  - `code`
  - `subscribeDate`
  - `lotteryDate`
  - `paymentDate`
  - `listingDate`
  - `limitAmount`
  - `issuePriceOrTransferPrice`
- Rules:
  - Only same-day subscribe/payment/listing records are included.
  - IPO and bond items share one table but keep a visible kind tag.

## 3. PushConfigViewState

- Purpose: Compact dashboard form state for push configuration.
- Source:
  - `GET/POST /api/push/config`
- Fields:
  - `enabled`
  - `times[]`
  - `modules`
  - `mergerSchedule.enabled`
  - `mergerSchedule.time`
  - `statusText`
- Rules:
  - Main schedule exposes exactly three time inputs in the dashboard contract.
  - Notification-owned normalization remains in `notification/scheduler/`.

## 4. PremiumTableState

- Purpose: Shared client-side state for CB arbitrage, AH, and AB long tables.
- Fields:
  - `sortKey`
  - `sortDir`
  - `page`
  - `pageSize`
  - `rows`
  - `total`
- Rules:
  - Default `pageSize` is 50.
  - Sequence number is derived from sorted rows plus page offset.
  - Each table has explicit sortable columns and default sorting behavior.

## 5. ConvertibleBondPremiumRow

- Purpose: One row in the convertible bond arbitrage table.
- Source:
  - `/api/market/convertible-bond-arbitrage`
- Core fields:
  - `bondCode`
  - `bondName`
  - `stockCode`
  - `stockName`
  - `bondPrice`
  - `bondChangePercent`
  - `stockPrice`
  - `stockChangePercent`
  - `conversionPrice`
  - `conversionValue`
  - `premiumRate`
  - `doubleLow`
  - `theoreticalPremiumRate`
  - `rating`
  - `remainingYears`
  - `remainingScale`
  - `turnoverAmount`
  - `maturityYield`
  - `listingDate`
  - `conversionStartDate`

## 6. AhAbPremiumRow

- Purpose: Shared view model shape for AH and AB premium tables.
- Sources:
  - `/api/market/ah`
  - `/api/market/ab`
- Core fields:
  - `aCode`
  - `aName`
  - `peerCode`
  - `peerName`
  - `aPrice`
  - `peerPrice`
  - `peerPriceCny`
  - `spread`
  - `premium`
  - `percentile`
  - `sampleRange`
  - `historyCount`
- Rules:
  - `spread = peerPriceCny - aPrice`
  - `sampleRange` renders as compact `YYMMDD-YYMMDD`
  - `historyCount` may remain in payload but should not become a visible main
    table column unless the spec changes

## 7. MonitorOpportunityRow

- Purpose: Arbitrage monitor table row derived from custom monitor runtime state.
- Source:
  - `/api/monitors`
- Fields:
  - `monitorName`
  - `acquirerName`
  - `acquirerPrice`
  - `targetName`
  - `targetPrice`
  - `exchangeRatio`
  - `safetyFactor`
  - `stockLegFairValue`
  - `stockLegSpread`
  - `stockLegYield`
  - `cashLegFairValue`
  - `cashLegSpread`
  - `cashLegYield`

## 8. DividendReminderSnapshot

- Purpose: Top highlight plus full observation list for dividend reminders.
- Source:
  - `/api/dividend?action=refresh`
- Fields:
  - `todayRecordRows[]`
  - `allRows[]`
  - `updateTime`

## 9. MergerAnnouncementRow

- Purpose: Full announcement row for merger/private pages.
- Source:
  - `/api/market/merger`
- Fields:
  - `announcementDate`
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
- Rules:
  - Default sort is newest announcement first.
  - Same-day announcements must receive a prominent visual highlight.
