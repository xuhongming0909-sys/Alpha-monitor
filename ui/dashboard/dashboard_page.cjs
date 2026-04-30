// AI-SUMMARY: 旧看板页面逻辑：HTML 看板渲染与交互
// 对应 INDEX.md §9 文件摘要索引

'use strict';

const {
  API_BASE,
  PAGE_SIZE,
  CRITICAL_CACHE_REVALIDATION_KEYS,
  DEFAULT_AUTO_REFRESH_CONFIG,
  DEFAULT_TABLE_UI_CONFIG,
  ENDPOINTS,
  TAB_SEQUENCE,
  CB_ARB_SUBTAB_SEQUENCE,
  CB_RIGHTS_ISSUE_SUBTAB_SEQUENCE,
  CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE,
  CB_RIGHTS_ISSUE_TABLE_KEYS,
  EVENT_ARB_SUBTAB_SEQUENCE,
  TAB_PRIMARY_RESOURCE_KEYS,
  DATASET_STATUS_RESOURCE_KEYS,
  MONITOR_MARKET_OPTIONS,
  MONITOR_CURRENCY_OPTIONS,
  PUSH_MODULE_LABELS,
  MONITOR_LOOKUP_DEBOUNCE_MS,
  PREMIUM_SORT_OPTIONS,
  SUBSCRIPTION_STAGES,
  TABLE_DEFAULTS,
  TABLE_SEARCH_CONFIG,
  normalizePositiveNumber: CONST_normalizePositiveNumber,
} = require('./constants');

const { safeGet } = require('./constants');

const state = {
  activeTab: 'cb-arb',
  cbArbSubview: 'home',
  lofSubview: 'index',
  cbRightsIssueMarketSubview: 'sh',
  mergerSubview: 'a_event',
  eventsBound: false,
  savingPush: false,
  savingCbArbPush: false,
  savingCbRightsIssuePush: false,
  savingLofArbPush: false,
  savingMonitor: false,
  cacheRevalidated: {},
  resourceMeta: {},
  autoRefreshTimer: null,
  autoRefreshTickRunning: false,
  tableScrollOffsets: {},
  searchComposition: {
    cbArb: false,
    cbArbSmallRedemption: false,
    ah: false,
    ab: false,
    lofArb: false,
    cbRightsIssueShApply: false,
    cbRightsIssueShAmbush: false,
    cbRightsIssueShWait: false,
    cbRightsIssueSzApply: false,
    cbRightsIssueSzAmbush: false,
    cbRightsIssueSzWait: false,
  },
  monitorEditor: createMonitorEditorState(),
  expandedRows: {
    cbArb: {},
    ah: {},
    ab: {},
    monitor: {},
    merger: {},
    eventArbHk: {},
    eventArbCn: {},
    eventArbA: {},
    eventArbAnnouncement: {},
  },
  tables: {
    cbArb: createTableState('cbArb'),
    cbArbSmallRedemption: createTableState('cbArbSmallRedemption'),
    ah: createTableState('ah'),
    ab: createTableState('ab'),
    monitor: createTableState('monitor'),
    dividend: createTableState('dividend'),
    merger: createTableState('merger'),
    lofArb: createTableState('lofArb'),
    cbRightsIssueShApply: createTableState('cbRightsIssueShApply'),
    cbRightsIssueShAmbush: createTableState('cbRightsIssueShAmbush'),
    cbRightsIssueShWait: createTableState('cbRightsIssueShWait'),
    cbRightsIssueSzApply: createTableState('cbRightsIssueSzApply'),
    cbRightsIssueSzAmbush: createTableState('cbRightsIssueSzAmbush'),
    cbRightsIssueSzWait: createTableState('cbRightsIssueSzWait'),
    eventArbHk: createTableState('eventArbHk'),
    eventArbCn: createTableState('eventArbCn'),
    eventArbA: createTableState('eventArbA'),
    eventArbAnnouncement: createTableState('eventArbAnnouncement'),
  },
  resources: {
    uiConfig: resourceState(),
    health: resourceState(),
    exchangeRate: resourceState(),
    ipo: resourceState(),
    bonds: resourceState(),
    cbArb: resourceState(),
    cbRightsIssue: resourceState(),
    lofArb: resourceState(),
    ah: resourceState(),
    ab: resourceState(),
    monitor: resourceState(),
    dividend: resourceState(),
    merger: resourceState(),
    pushConfig: resourceState(),
    cbArbPushConfig: resourceState(),
    cbRightsIssuePushConfig: resourceState(),
    lofArbPushConfig: resourceState(),
  },
};

const dom = {
  tabButtons: Array.from(document.querySelectorAll('.tab-button')),
  tabPanels: {
    'cb-arb': document.getElementById('panel-cb-arb'),
    ah: document.getElementById('panel-ah'),
    ab: document.getElementById('panel-ab'),
    'lof-arb': document.getElementById('panel-lof-arb'),
    monitor: document.getElementById('panel-monitor'),
    dividend: document.getElementById('panel-dividend'),
    merger: document.getElementById('panel-merger'),
    'cb-rights-issue': document.getElementById('panel-cb-rights-issue'),
  },
  statusLine: document.getElementById('status-line'),
  statusUpdateText: document.getElementById('status-update-text'),
  buildVersionText: document.getElementById('build-version-text'),
  lastRefreshText: document.getElementById('last-refresh-text'),
  subscriptionSummary: document.getElementById('subscription-summary'),
  pushStateText: document.getElementById('push-state-text'),
  pushAlertStateText: document.getElementById('push-alert-state-text'),
  pushForm: document.getElementById('push-form'),
  cbArbPushSettingsHost: document.getElementById('cb-arb-push-settings-host'),
  pushTime1: document.getElementById('push-time-1'),
  pushTime2: document.getElementById('push-time-2'),
  savePushButton: document.getElementById('save-push-button'),
  reloadDataButton: document.getElementById('reload-data-button'),
  toast: document.getElementById('toast'),
};

function normalizePositiveNumber(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function normalizeTableUiConfig(payload) {
  const root = payload && typeof payload === 'object' ? payload : {};
  const tableUi = root.tableUi && typeof root.tableUi === 'object' ? root.tableUi : root;
  const minWidthSource = tableUi.minWidthByKind && typeof tableUi.minWidthByKind === 'object'
    ? tableUi.minWidthByKind
    : {};
  return {
    desktopFontPx: normalizePositiveNumber(tableUi.desktopFontPx, DEFAULT_TABLE_UI_CONFIG.desktopFontPx),
    desktopHeaderFontPx: normalizePositiveNumber(tableUi.desktopHeaderFontPx, DEFAULT_TABLE_UI_CONFIG.desktopHeaderFontPx),
    desktopLineHeight: normalizePositiveNumber(tableUi.desktopLineHeight, DEFAULT_TABLE_UI_CONFIG.desktopLineHeight),
    desktopCellPaddingY: normalizePositiveNumber(tableUi.desktopCellPaddingY, DEFAULT_TABLE_UI_CONFIG.desktopCellPaddingY),
    desktopCellPaddingX: normalizePositiveNumber(tableUi.desktopCellPaddingX, DEFAULT_TABLE_UI_CONFIG.desktopCellPaddingX),
    tabletFontPx: normalizePositiveNumber(tableUi.tabletFontPx, DEFAULT_TABLE_UI_CONFIG.tabletFontPx),
    minWidthByKind: {
      subscription: normalizePositiveNumber(minWidthSource.subscription, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.subscription),
      convertible: Math.min(
        normalizePositiveNumber(minWidthSource.convertible, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.convertible),
        DEFAULT_TABLE_UI_CONFIG.minWidthByKind.convertible
      ),
      premium: normalizePositiveNumber(minWidthSource.premium, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.premium),
      monitor: normalizePositiveNumber(minWidthSource.monitor, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.monitor),
      dividend: normalizePositiveNumber(minWidthSource.dividend, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.dividend),
      merger: normalizePositiveNumber(minWidthSource.merger, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.merger),
      lof: normalizePositiveNumber(minWidthSource.lof, DEFAULT_TABLE_UI_CONFIG.minWidthByKind.lof),
    },
  };
}

function normalizeAutoRefreshConfig(payload) {
  const root = payload && typeof payload === 'object' ? payload : {};
  const config = root.autoRefresh && typeof root.autoRefresh === 'object' ? root.autoRefresh : root;
  const intervalMs = normalizePositiveNumber(config.intervalMs ?? config.interval_ms, DEFAULT_AUTO_REFRESH_CONFIG.intervalMs);
  return {
    enabled: config.enabled !== false,
    intervalMs,
    mode: String(config.mode || DEFAULT_AUTO_REFRESH_CONFIG.mode).trim() || DEFAULT_AUTO_REFRESH_CONFIG.mode,
    currentTabOnly: config.currentTabOnly !== false && config.current_tab_only !== false,
    reloadDataOnCacheChange: config.reloadDataOnCacheChange !== false && config.reload_data_on_cache_change !== false,
  };
}

function normalizeDashboardTheme(value) {
  const normalized = String(value || 'classic').trim().toLowerCase();
  return normalized === 'clean_data' ? 'clean_data' : 'classic';
}

function readDashboardTheme() {
  const payload = state.resources.uiConfig?.data?.data || {};
  return normalizeDashboardTheme(payload.dashboardTheme || payload.dashboard_theme);
}

function applyDashboardTheme(theme = readDashboardTheme()) {
  document.documentElement.dataset.dashboardTheme = normalizeDashboardTheme(theme);
}

function applyTableUiConfig(rawPayload) {
  const tableUi = normalizeTableUiConfig(rawPayload);
  const root = document.documentElement;
  root.style.setProperty('--table-font-size-desktop', `${tableUi.desktopFontPx}px`);
  root.style.setProperty('--table-header-font-size-desktop', `${tableUi.desktopHeaderFontPx}px`);
  root.style.setProperty('--table-line-height-desktop', String(tableUi.desktopLineHeight));
  root.style.setProperty('--table-cell-padding-y-desktop', `${tableUi.desktopCellPaddingY}px`);
  root.style.setProperty('--table-cell-padding-x-desktop', `${tableUi.desktopCellPaddingX}px`);
  root.style.setProperty('--table-font-size-tablet', `${tableUi.tabletFontPx}px`);
  root.style.setProperty('--table-min-width-subscription', `${tableUi.minWidthByKind.subscription}px`);
  root.style.setProperty('--table-min-width-convertible', `${tableUi.minWidthByKind.convertible}px`);
  root.style.setProperty('--table-min-width-premium', `${tableUi.minWidthByKind.premium}px`);
  root.style.setProperty('--table-min-width-monitor', `${tableUi.minWidthByKind.monitor}px`);
  root.style.setProperty('--table-min-width-dividend', `${tableUi.minWidthByKind.dividend}px`);
  root.style.setProperty('--table-min-width-merger', `${tableUi.minWidthByKind.merger}px`);
  root.style.setProperty('--table-min-width-lof', `${tableUi.minWidthByKind.lof}px`);
}

function applyTableUiConfigFromState() {
  const payload = state.resources.uiConfig?.data?.data || null;
  applyTableUiConfig(payload);
}

function readDashboardAutoRefreshConfig() {
  const payload = state.resources.uiConfig?.data?.data || {};
  return normalizeAutoRefreshConfig(payload.autoRefresh || payload);
}

function readDashboardModuleNotes() {
  const payload = state.resources.uiConfig?.data?.data || {};
  const notes = payload?.moduleNotes && typeof payload.moduleNotes === 'object' ? payload.moduleNotes : {};
  return notes;
}

function readModuleNote(moduleKey) {
  const item = readDashboardModuleNotes()[moduleKey];
  return item && typeof item === 'object'
    ? {
      dataSources: Array.isArray(item.dataSources) ? item.dataSources.filter(Boolean) : [],
      formulas: Array.isArray(item.formulas) ? item.formulas.filter(Boolean) : [],
      strategyNotes: Array.isArray(item.strategyNotes) ? item.strategyNotes.filter(Boolean) : [],
    }
    : { dataSources: [], formulas: [], strategyNotes: [] };
}

function renderModuleFootnote(moduleKey) {
  const note = readModuleNote(moduleKey);
  const sections = [
    { title: '数据来源', items: note.dataSources },
    { title: '计算公式', items: note.formulas },
    { title: '策略说明', items: note.strategyNotes },
  ].filter((section) => section.items.length);

  if (!sections.length) return '';

  return `
    <div class="module-footnote-card">
      <h3>页面注释</h3>
      <div class="module-footnote-grid">
        ${sections.map((section) => `
          <div class="module-footnote-section">
            <div class="module-footnote-title">${escapeHtml(section.title)}</div>
            <div class="module-footnote-lines">
              ${section.items.map((item) => `<div class="module-footnote-line">${escapeHtml(item)}</div>`).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function renderDashboardUiState() {
  applyDashboardTheme();
  applyTableUiConfigFromState();
  restartAutoRefreshLoop();
  renderEverything();
}

function createTableState(key) {
  return { ...TABLE_DEFAULTS[key] };
}

function createMonitorDraft(source = {}) {
  return {
    id: source.id || '',
    name: source.name || '',
    acquirerName: source.acquirerName || '',
    acquirerCode: source.acquirerCode || '',
    acquirerMarket: source.acquirerMarket || 'A',
    acquirerCurrency: source.acquirerCurrency || 'CNY',
    targetName: source.targetName || '',
    targetCode: source.targetCode || '',
    targetMarket: source.targetMarket || 'A',
    targetCurrency: source.targetCurrency || 'CNY',
    stockRatio: source.stockRatio ?? '',
    safetyFactor: source.safetyFactor ?? 1,
    cashDistribution: source.cashDistribution ?? '',
    cashDistributionCurrency: source.cashDistributionCurrency || 'CNY',
    cashOptionPrice: source.cashOptionPrice ?? '',
    cashOptionCurrency: source.cashOptionCurrency || 'CNY',
    note: source.note || '',
  };
}

function createMonitorResolvedCandidate(source = {}, role = 'acquirer') {
  const isAcquirer = role === 'acquirer';
  const name = String(isAcquirer ? source.acquirerName : source.targetName || '').trim();
  const code = String(isAcquirer ? source.acquirerCode : source.targetCode || '').trim();
  if (!code) return null;
  return {
    name: name || code,
    code,
    market: String(isAcquirer ? source.acquirerMarket : source.targetMarket || 'A').trim().toUpperCase() || 'A',
    currency: String(isAcquirer ? source.acquirerCurrency : source.targetCurrency || 'CNY').trim().toUpperCase() || 'CNY',
  };
}

function createMonitorLookupSlot(source = {}, role = 'acquirer') {
  return {
    loading: false,
    error: '',
    items: [],
    timer: null,
    requestToken: 0,
    resolved: createMonitorResolvedCandidate(source, role),
  };
}

function createMonitorEditorState(source = {}, mode = 'create', open = false) {
  const draft = createMonitorDraft(source);
  return {
    mode,
    open,
    draft,
    lookup: {
      acquirer: createMonitorLookupSlot(draft, 'acquirer'),
      target: createMonitorLookupSlot(draft, 'target'),
    },
  };
}

function resourceState() {
  return {
    status: 'idle',
    data: null,
    error: null,
    refreshing: false,
  };
}

function readExpandedState(tableKey, rowId) {
  if (!tableKey || !rowId) return false;
  return Boolean(state.expandedRows?.[tableKey]?.[rowId]);
}

function toggleExpandedState(tableKey, rowId) {
  if (!tableKey || !rowId) return;
  if (!state.expandedRows[tableKey]) {
    state.expandedRows[tableKey] = {};
  }
  state.expandedRows[tableKey][rowId] = !state.expandedRows[tableKey][rowId];
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function readArray(payload) {
  if (Array.isArray(payload)) return payload;
  if (payload && Array.isArray(payload.data)) return payload.data;
  if (payload && Array.isArray(payload.rows)) return payload.rows;
  if (payload && Array.isArray(payload.list)) return payload.list;
  return [];
}

function readObject(payload) {
  return payload && typeof payload === 'object' ? payload : {};
}

function readValueByPathSafe(source, path) {
  return String(path || '')
    .split('.')
    .reduce((acc, key) => (acc && typeof acc === 'object' ? acc[key] : undefined), source);
}

function readFirstDefinedValue(source, paths = []) {
  for (const path of paths) {
    const value = readValueByPathSafe(source, path);
    if (value !== undefined && value !== null && value !== '') return value;
  }
  return null;
}

function readFirstNumberValue(source, paths = []) {
  for (const path of paths) {
    const value = toNumber(readValueByPathSafe(source, path));
    if (value !== null) return value;
  }
  return null;
}

function readResourceArray(key) {
  return readArray(state.resources[key].data);
}

function readResourceObject(key) {
  return readObject(state.resources[key].data);
}

function readResourcePayload(key) {
  return readResourceObject(key);
}

function readResourceStatusMeta(key) {
  const payload = readResourcePayload(key);
  const meta = state.resourceMeta && typeof state.resourceMeta[key] === 'object' ? state.resourceMeta[key] : null;
  return meta ? { ...payload, ...meta } : payload;
}

function resourceServedFromCache(key) {
  return Boolean(readResourceStatusMeta(key).servedFromCache);
}

function resourceRefreshing(key) {
  return Boolean(state.resources[key]?.refreshing || readResourceStatusMeta(key).refreshing);
}

function buildEndpointUrl(endpoint, options = {}) {
  if (!options.force) return endpoint;
  return `${endpoint}${endpoint.includes('?') ? '&' : '?'}force=1`;
}

function buildDashboardStatusUrl(keys) {
  const list = (Array.isArray(keys) ? keys : [])
    .map((item) => String(item || '').trim())
    .filter(Boolean);
  const query = encodeURIComponent(list.join(','));
  return `${ENDPOINTS.resourceStatus}?keys=${query}`;
}

function readTabResourceKeys(tabKey = state.activeTab) {
  return [...(TAB_PRIMARY_RESOURCE_KEYS[tabKey] || [])];
}

function readActiveTabDatasetStatusKeys() {
  return readTabResourceKeys()
    .filter((key) => DATASET_STATUS_RESOURCE_KEYS.includes(key));
}

function readAutoRefreshDatasetStatusKeys(config = readDashboardAutoRefreshConfig()) {
  if (!config.currentTabOnly) {
    return [...new Set(DATASET_STATUS_RESOURCE_KEYS)];
  }
  return [...new Set(['exchangeRate', 'ipo', 'bonds', ...readActiveTabDatasetStatusKeys()])];
}

function toNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatNumber(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  return parsed.toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatSignedNumber(value, digits = 2, suffix = '') {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  const sign = parsed > 0 ? '+' : '';
  return `${sign}${formatNumber(parsed, digits)}${suffix}`;
}

function formatPercent(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  const sign = parsed > 0 ? '+' : '';
  return `${sign}${formatNumber(parsed, digits)}%`;
}

function formatSmallRedemptionPercent(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  const normalized = Math.abs(parsed) <= 1 ? parsed * 100 : parsed;
  return formatPercent(normalized, digits);
}

function statusText(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '涨幅 --';
  return `涨幅 ${formatPercent(parsed, digits)}`;
}

function formatRatioPercent(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  // 可转债波动率字段返回的是 0.x 比例值，展示时需要转成 100 倍百分数
  return `${formatNumber(parsed * 100, digits)}%`;
}

function formatRemainingTerm(value) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  return `${formatNumber(parsed, 2)}年`;
}

function formatYiValue(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  return `${formatNumber(parsed, digits)}\u4ebf`;
}

function formatCurrencyCompact(value, digits = 2) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  const absolute = Math.abs(parsed);
  if (absolute >= 100000000) return `${formatNumber(parsed / 100000000, digits)}\u4ebf`;
  if (absolute >= 10000) return `${formatNumber(parsed / 10000, digits)}\u4e07`;
  return `${formatNumber(parsed, absolute >= 1000 ? digits : 0)}\u5143`;
}

/**
 * 活跃强赎只用于页面提示与摘要排除：
 * 1. 必须已有真实 forceRedeemStatus；
 * 2. 只识别“已公告强赎/强制赎回”语义；
 * 3. 不把“不强赎”或“已完成摘牌”误标成活跃风险。
 */
function isConvertibleActiveForceRedeem(row) {
  const status = String(row?.forceRedeemStatus || '').trim();
  if (!status) return false;
  const today = todayKey();
  const ceaseDate = normalizeDateKey(row?.ceaseDate);
  const delistDate = normalizeDateKey(row?.delistDate);
  if (/(不强赎|暂不强赎|不提前赎回|不赎回)/.test(status)) return false;
  if (/(完成|摘牌|终止|退市)/.test(status)) return false;
  if ((ceaseDate && ceaseDate <= today) || (delistDate && delistDate <= today)) return false;
  return /(已公告强赎|强赎进行中|实施赎回|公告赎回)/.test(status);
}

function readConvertibleForceRedeemStatus(row) {
  return String(row?.forceRedeemStatus || '').trim() || '--';
}

function readConvertibleForceRedeemNoticeDate(row) {
  return normalizeDateKey(row?.forceRedeemNoticeDate);
}

function readConvertibleForceRedeemReason(row) {
  if (!isConvertibleActiveForceRedeem(row)) return '';
  const status = readConvertibleForceRedeemStatus(row);
  const noticeDate = formatDateOnly(readConvertibleForceRedeemNoticeDate(row));
  return noticeDate !== '--' ? `${status} ${noticeDate}` : status;
}

function readConvertibleMaturityReason(row) {
  const maturityDate = formatDateOnly(row?.maturityDate);
  if (maturityDate === '--') return '';
  const maturityRedeemPrice = toNumber(row?.maturityRedeemPrice);
  if (maturityRedeemPrice === null) return `到期 ${maturityDate}`;
  return `到期 ${maturityDate} / 到期价 ${formatNumber(maturityRedeemPrice, 2)}`;
}

function renderConvertibleBondIdentity(row) {
  const bondName = escapeHtml(row?.bondName || '--');
  const codeLine = `<span class="mono-text">${escapeHtml(row?.code || '--')}</span>`;
  const reasonLines = [];
  const forceRedeemReason = readConvertibleForceRedeemReason(row);
  if (forceRedeemReason) reasonLines.push(escapeHtml(forceRedeemReason));
  const maturityReason = readConvertibleMaturityReason(row);
  if (maturityReason) reasonLines.push(escapeHtml(maturityReason));

  const nameHtml = isConvertibleActiveForceRedeem(row)
    ? `${bondName}<span class="bond-risk-marker" title="活跃强赎提示">!</span>`
    : bondName;

  return renderCompactCell(nameHtml, [codeLine, ...reasonLines]);
}

function formatInt(value) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  return Math.round(parsed).toLocaleString('zh-CN');
}

function formatDate(value) {
  if (!value) return '--';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString('zh-CN', {
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatDateOnly(value) {
  if (!value) return '--';
  const text = String(value).trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(text)) return text;
  const parsed = new Date(text);
  if (Number.isNaN(parsed.getTime())) return text;
  return parsed.toLocaleDateString('zh-CN');
}

function formatCompactDate(value) {
  const normalized = normalizeDateKey(value);
  if (!normalized) return '--';
  const parts = normalized.split('-');
  return `${parts[0].slice(2)}${parts[1]}${parts[2]}`;
}

function formatCompactRange(start, end) {
  const startText = formatCompactDate(start);
  const endText = formatCompactDate(end);
  if (startText === '--' && endText === '--') return '--';
  if (startText === '--') return endText;
  if (endText === '--') return startText;
  return `${startText}-${endText}`;
}

function normalizeDateKey(value) {
  if (!value) return '';
  const text = String(value).trim();
  const simple = text.match(/^(\d{4})[-/.](\d{2})[-/.](\d{2})/);
  if (simple) return `${simple[1]}-${simple[2]}-${simple[3]}`;
  const parsed = new Date(text);
  if (Number.isNaN(parsed.getTime())) return '';
  const year = parsed.getFullYear();
  const month = String(parsed.getMonth() + 1).padStart(2, '0');
  const day = String(parsed.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function normalizeSearchText(value) {
  return String(value || '').trim().toLowerCase();
}

function readTableSearchConfig(tableKey) {
  return TABLE_SEARCH_CONFIG[tableKey] || null;
}

function readTableSearchQuery(tableKey) {
  return normalizeSearchText(state.tables?.[tableKey]?.searchQuery || '');
}

function readTableSearchTokens(tableKey) {
  const query = readTableSearchQuery(tableKey);
  return query ? query.split(/\s+/).filter(Boolean) : [];
}

function buildTableSearchHaystack(tableKey, row) {
  const config = readTableSearchConfig(tableKey);
  if (!config) return '';
  return config.fields
    .map((field) => normalizeSearchText(row?.[field]))
    .filter(Boolean)
    .join(' ');
}

function applyTableSearch(tableKey, rows) {
  const tokens = readTableSearchTokens(tableKey);
  if (!tokens.length) return [...rows];
  return rows.filter((row) => {
    const haystack = buildTableSearchHaystack(tableKey, row);
    return tokens.every((token) => haystack.includes(token));
  });
}

function setTableSearchCompositionState(tableKey, composing) {
  if (!state.searchComposition || !Object.prototype.hasOwnProperty.call(state.searchComposition, tableKey)) return;
  state.searchComposition[tableKey] = Boolean(composing);
}

function buildTableSearchFocusSnapshot(tableKey, element = null, fallbackValue = null) {
  if (!readTableSearchConfig(tableKey)) return null;
  const effectiveValue = String(
    fallbackValue ?? element?.value ?? state.tables?.[tableKey]?.searchQuery ?? ''
  );
  const defaultCaret = effectiveValue.length;
  return {
    tableKey,
    selectionStart: typeof element?.selectionStart === 'number' ? element.selectionStart : defaultCaret,
    selectionEnd: typeof element?.selectionEnd === 'number' ? element.selectionEnd : defaultCaret,
    selectionDirection: typeof element?.selectionDirection === 'string' ? element.selectionDirection : 'none',
  };
}

function restoreTableSearchFocus(snapshot) {
  if (!snapshot?.tableKey) return;
  window.requestAnimationFrame(() => {
    const field = document.querySelector(`[data-table-search-key="${snapshot.tableKey}"]`);
    if (!(field instanceof HTMLInputElement)) return;
    field.focus({ preventScroll: true });
    if (typeof field.setSelectionRange !== 'function') return;
    const max = field.value.length;
    const start = Math.max(0, Math.min(snapshot.selectionStart ?? max, max));
    const end = Math.max(start, Math.min(snapshot.selectionEnd ?? max, max));
    field.setSelectionRange(start, end, snapshot.selectionDirection || 'none');
  });
}

function renderSearchableTablePanel(tableKey) {
  if (tableKey === 'cbArb' || tableKey === 'cbArbSmallRedemption') {
    renderConvertibleBondPanel();
    return;
  }
  if (tableKey === 'ah') {
    renderPremiumPanel('ah');
    return;
  }
  if (tableKey === 'ab') {
    renderPremiumPanel('ab');
    return;
  }
  if (tableKey === 'lofArb') {
    renderLofArbPanel();
    return;
  }
  if (isCbRightsIssueTableKey(tableKey)) {
    renderCbRightsIssuePanel();
  }
}

function renderSearchableTableHostContent(tableKey) {
  if (tableKey === 'cbArb') {
    return renderPaginatedTable({
      tableKey: 'cbArb',
      tableKind: 'convertible',
      columns: buildConvertibleColumns(),
      rows: readCbArbMainRows(),
      emptyMessage: '转债套利暂时没有返回数据',
    });
  }
  if (tableKey === 'cbArbSmallRedemption') {
    return renderPaginatedTable({
      tableKey: 'cbArbSmallRedemption',
      tableKind: 'convertible',
      columns: buildCbArbSmallRedemptionColumns(),
      rows: readCbArbSmallRedemptionRows(),
      emptyMessage: '\u5f53\u524d\u6ca1\u6709\u7b26\u5408\u6761\u4ef6\u7684\u5c0f\u989d\u521a\u5151\u6807\u7684',
    });
  }
  if (tableKey === 'ah' || tableKey === 'ab') {
    return renderPaginatedTable({
      tableKey,
      tableKind: 'premium',
      columns: buildPremiumColumns(tableKey),
      rows: readResourceArray(tableKey),
      emptyMessage: `${getPremiumConfig(tableKey).title} 暂无数据`,
    });
  }
  if (tableKey === 'lofArb') {
    return renderPaginatedTable({
      tableKey: 'lofArb',
      tableKind: 'lof',
      columns: buildLofArbColumns(),
      rows: readLofArbVisibleRows(),
      emptyMessage: '当前分组没有符合条件的 LOF 套利数据',
    });
  }
  if (isCbRightsIssueTableKey(tableKey)) {
    const parsed = parseCbRightsIssueTableKey(tableKey);
    const meta = readCbRightsIssueSubviewMeta(parsed.marketKey, parsed.subview);
    return renderPaginatedTable({
      tableKey: meta.tableKey,
      tableKind: 'convertible',
      columns: buildCbRightsIssueColumns({
        includeRecordDate: meta.includeRecordDate,
        includeMarginColumns: meta.includeMarginColumns,
        includePeelColumns: meta.includePeelColumns,
      }),
      rows: meta.rows,
      emptyMessage: meta.emptyMessage,
    });
  }
  return '';
}

function syncSearchBarDomState(tableKey) {
  const input = document.querySelector(`[data-table-search-key="${tableKey}"]`);
  const clearButton = document.querySelector(`[data-table-search-clear="${tableKey}"]`);
  const query = String(state.tables?.[tableKey]?.searchQuery || '');
  if (input instanceof HTMLInputElement && input.value !== query) {
    input.value = query;
  }
  if (clearButton instanceof HTMLButtonElement) {
    clearButton.disabled = !query;
  }
}

function patchSearchableTableResults(tableKey) {
  const host = document.querySelector(`[data-table-host="${tableKey}"]`);
  if (!host) return false;
  host.innerHTML = renderSearchableTableHostContent(tableKey);
  syncSearchBarDomState(tableKey);
  return true;
}

function setTableSearchQuery(tableKey, query, options = {}) {
  if (!state.tables?.[tableKey]) return;
  state.tables[tableKey].searchQuery = String(query || '');
  state.tables[tableKey].page = 1;
  if (options.render === false) return;
  if (patchSearchableTableResults(tableKey)) {
    restoreTableSearchFocus(options.focusSnapshot);
    return;
  }
  renderSearchableTablePanel(tableKey);
  restoreTableSearchFocus(options.focusSnapshot);
}

function todayKey() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function readUpdateTime(key) {
  const payload = readResourceStatusMeta(key);
  return payload.updateTime || null;
}

function maxUpdateTime(keys) {
  return keys
    .map((key) => readUpdateTime(key))
    .filter(Boolean)
    .sort()
    .pop() || null;
}

function statusClass(value) {
  const parsed = toNumber(value);
  if (parsed === null) return '';
  if (parsed > 0) return 'positive';
  if (parsed < 0) return 'negative';
  return '';
}

function readFreshnessText(keys) {
  const targetKeys = Array.isArray(keys) ? keys : [keys];
  if (targetKeys.some((key) => resourceRefreshing(key))) {
    return '缓存快照校准中';
  }
  if (targetKeys.some((key) => resourceServedFromCache(key))) {
    return '当前显示缓存值';
  }
  return '实时快照';
}

function readCbArbPayload() {
  return readResourceObject('cbArb');
}

function readCbArbMainRows() {
  const payload = readCbArbPayload();
  if (Array.isArray(payload?.data)) return payload.data;
  if (payload?.data && Array.isArray(payload.data.rows)) return payload.data.rows;
  if (payload?.data && Array.isArray(payload.data.list)) return payload.data.list;
  if (Array.isArray(payload?.rows)) return payload.rows;
  return readArray(payload);
}

function readCbArbSummary() {
  const payload = readCbArbPayload();
  return payload?.summary && typeof payload.summary === 'object'
    ? payload.summary
    : (payload?.data?.summary && typeof payload.data.summary === 'object' ? payload.data.summary : {});
}

function readCbArbPremiumMonitorSummary() {
  const payload = readCbArbPayload();
  return payload?.premiumMonitorSummary && typeof payload.premiumMonitorSummary === 'object'
    ? payload.premiumMonitorSummary
    : (payload?.data?.premiumMonitorSummary && typeof payload.data.premiumMonitorSummary === 'object'
      ? payload.data.premiumMonitorSummary
      : { items: [] });
}

function readCbArbSmallRedemptionSection() {
  const payload = readCbArbPayload();
  return payload?.smallRedemption && typeof payload.smallRedemption === 'object'
    ? payload.smallRedemption
    : (payload?.data?.smallRedemption && typeof payload.data.smallRedemption === 'object'
      ? payload.data.smallRedemption
      : {});
}

function readCbArbSmallRedemptionRows() {
  const section = readCbArbSmallRedemptionSection();
  if (Array.isArray(section?.rows)) return section.rows;
  if (section?.data && Array.isArray(section.data.rows)) return section.data.rows;
  if (section?.data && Array.isArray(section.data.list)) return section.data.list;
  return readArray(section);
}

function readCbArbSmallRedemptionSummary() {
  const section = readCbArbSmallRedemptionSection();
  return section?.summary && typeof section.summary === 'object' ? section.summary : {};
}

function readCbArbSmallRedemptionMeta() {
  const section = readCbArbSmallRedemptionSection();
  return section?.meta && typeof section.meta === 'object' ? section.meta : {};
}

function ensureCbArbSubview() {
  if (!CB_ARB_SUBTAB_SEQUENCE.includes(state.cbArbSubview)) {
    state.cbArbSubview = 'home';
  }
  return state.cbArbSubview;
}

function readCbRightsIssueDataset() {
  const payload = readResourceObject('cbRightsIssue');
  return payload?.data && typeof payload.data === 'object' ? payload.data : {};
}

function readCbRightsIssueSourceRows() {
  const dataset = readCbRightsIssueDataset();
  return Array.isArray(dataset.sourceRows) ? dataset.sourceRows : [];
}

function normalizeCbRightsIssueProgressText(value) {
  return String(value || '')
    .replaceAll('<br>', ' ')
    .replaceAll('<br/>', ' ')
    .replaceAll('<br />', ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function normalizeCbRightsIssueMarketKey(row) {
  const market = String(row?.market || '').trim().toLowerCase();
  if (market === 'sh' || market === 'sz') return market;
  const stockCode = String(row?.stockCode || '').trim();
  if (stockCode.startsWith('6')) return 'sh';
  if (stockCode.startsWith('0') || stockCode.startsWith('3')) return 'sz';
  return '';
}

function buildCbRightsIssueTableKey(marketKey, subview) {
  const marketPart = String(marketKey || '').trim().toLowerCase() === 'sz' ? 'Sz' : 'Sh';
  const subviewPart = subview === 'ambush' ? 'Ambush' : (subview === 'wait' ? 'Wait' : 'Apply');
  return `cbRightsIssue${marketPart}${subviewPart}`;
}

function parseCbRightsIssueTableKey(tableKey) {
  const text = String(tableKey || '').trim();
  const match = /^cbRightsIssue(Sh|Sz)(Apply|Ambush|Wait)$/.exec(text);
  if (!match) return null;
  return {
    marketKey: match[1] === 'Sz' ? 'sz' : 'sh',
    subview: match[2] === 'Ambush' ? 'ambush' : (match[2] === 'Wait' ? 'wait' : 'apply'),
  };
}

function isCbRightsIssueTableKey(tableKey) {
  return Boolean(parseCbRightsIssueTableKey(tableKey));
}

function ensureCbRightsIssueMarketSubview() {
  if (!CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE.includes(state.cbRightsIssueMarketSubview)) {
    state.cbRightsIssueMarketSubview = 'sh';
  }
  return state.cbRightsIssueMarketSubview;
}

function isCbRightsIssueAmbushRow(row) {
  if (row?.inApplyStage) return false;
  const progressText = normalizeCbRightsIssueProgressText(row?.progressName);
  const isTargetStage = ['上市委通过', '同意注册', '注册生效'].some((keyword) => progressText.includes(keyword));
  return isTargetStage && (toNumber(row?.expectedReturnRate) ?? -Infinity) > 6;
}

function readCbRightsIssueRowsByMarketAndSubview(marketKey, subview) {
  const rows = readCbRightsIssueSourceRows().filter((row) => normalizeCbRightsIssueMarketKey(row) === marketKey);
  if (subview === 'apply') {
    return rows.filter((row) => Boolean(row?.inApplyStage));
  }
  if (subview === 'ambush') {
    return rows.filter((row) => isCbRightsIssueAmbushRow(row));
  }
  return rows.filter((row) => !row?.inApplyStage && !isCbRightsIssueAmbushRow(row));
}

function readCbRightsIssueRowsByMarket(marketKey) {
  return readCbRightsIssueSourceRows().filter((row) => normalizeCbRightsIssueMarketKey(row) === marketKey);
}

function readCbRightsIssueActiveMarketMeta(marketKey = ensureCbRightsIssueMarketSubview()) {
  const active = CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE.includes(marketKey) ? marketKey : 'sh';
  const metaByMarket = {
    sh: {
      key: 'sh',
      label: '沪市',
      note: '沪市保留申购阶段、埋伏阶段、等待阶段三张竖排表，并继续展示两融与去皮相关字段。',
    },
    sz: {
      key: 'sz',
      label: '深市',
      note: '深市同样按三阶段竖排展示，但不再显示两融收益率、两融所需股数及去皮收益率列。',
    },
  };
  return {
    ...metaByMarket[active],
    rows: readCbRightsIssueRowsByMarket(active),
  };
}

function readCbRightsIssueSubviewMeta(marketKey, subview) {
  const activeMarket = CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE.includes(marketKey) ? marketKey : ensureCbRightsIssueMarketSubview();
  const activeSubview = CB_RIGHTS_ISSUE_SUBTAB_SEQUENCE.includes(subview) ? subview : 'apply';
  const metaBySubview = {
    apply: {
      key: 'apply',
      label: '申购阶段',
      note: '展示已进入申购阶段的项目，保留股权登记日字段，便于直接执行申购跟踪。',
      includeRecordDate: true,
      emptyMessage: '当前没有进入申购阶段的股票',
    },
    ambush: {
      key: 'ambush',
      label: '埋伏阶段',
      note: '展示上市委通过、同意注册或注册生效且预期收益率大于 6% 的项目，用于提前埋伏。',
      includeRecordDate: false,
      emptyMessage: '当前没有满足埋伏条件的股票',
    },
    wait: {
      key: 'wait',
      label: '等待阶段',
      note: '展示未进入申购阶段、也未达到埋伏门槛的项目，便于后续继续观察。',
      includeRecordDate: false,
      emptyMessage: '当前没有等待阶段的股票',
    },
  };
  const isShenzhen = activeMarket === 'sz';
  return {
    ...metaBySubview[activeSubview],
    marketKey: activeMarket,
    marketLabel: activeMarket === 'sz' ? '深市' : '沪市',
    tableKey: buildCbRightsIssueTableKey(activeMarket, activeSubview),
    includeMarginColumns: !isShenzhen,
    includePeelColumns: !isShenzhen,
    rows: readCbRightsIssueRowsByMarketAndSubview(activeMarket, activeSubview),
  };
}

function readCbRightsIssueSummary() {
  const dataset = readCbRightsIssueDataset();
  return dataset?.sourceSummary && typeof dataset.sourceSummary === 'object' ? dataset.sourceSummary : {};
}

function readCbRightsIssueRebuildStatus() {
  const dataset = readCbRightsIssueDataset();
  return dataset?.rebuildStatus && typeof dataset.rebuildStatus === 'object' ? dataset.rebuildStatus : {};
}

function readLofArbDataset() {
  const payload = readResourceObject('lofArb');
  return payload?.data && typeof payload.data === 'object' ? payload.data : {};
}

function readLofArbRows() {
  const dataset = readLofArbDataset();
  return Array.isArray(dataset.rows) ? dataset.rows : [];
}

function readLofArbGroups() {
  const dataset = readLofArbDataset();
  const groups = Array.isArray(dataset.groups) ? dataset.groups : [];
  return groups.length ? groups : [
    { key: 'index', label: '指数LOF' },
    { key: 'asia', label: 'QDII亚洲' },
  ];
}

function ensureLofSubview() {
  const groups = readLofArbGroups();
  const allowed = groups.map((item) => String(item?.key || '').trim()).filter(Boolean);
  const fallback = String(readLofArbDataset().defaultGroup || 'index').trim() || 'index';
  if (!allowed.length) {
    state.lofSubview = fallback;
    return fallback;
  }
  if (!allowed.includes(state.lofSubview)) {
    state.lofSubview = allowed.includes(fallback) ? fallback : allowed[0];
  }
  return state.lofSubview;
}

function readLofArbVisibleRows() {
  const activeGroup = ensureLofSubview();
  return readLofArbRows().filter((row) => String(row.marketGroup || '').trim() === activeGroup);
}

function readLofArbSummary() {
  const dataset = readLofArbDataset();
  return dataset?.sourceSummary && typeof dataset.sourceSummary === 'object' ? dataset.sourceSummary : {};
}

function readLofArbRebuildStatus() {
  const dataset = readLofArbDataset();
  return dataset?.rebuildStatus && typeof dataset.rebuildStatus === 'object' ? dataset.rebuildStatus : {};
}

function readLofArbLimitedRows() {
  const dataset = readLofArbDataset();
  return Array.isArray(dataset.limitedMonitorRows) ? dataset.limitedMonitorRows : [];
}

function readLofArbUnlimitedRows() {
  const dataset = readLofArbDataset();
  return Array.isArray(dataset.unlimitedMonitorRows) ? dataset.unlimitedMonitorRows : [];
}

function readLofArbPushConfigViewModel() {
  const payload = readResourceObject('lofArbPushConfig');
  return payload?.data && typeof payload.data === 'object' ? payload.data : {};
}

function readCbArbPushConfigViewModel() {
  const payload = readResourceObject('cbArbPushConfig');
  return payload?.data && typeof payload.data === 'object' ? payload.data : payload;
}

function showToast(message, isError = false) {
  if (!dom.toast) return;
  dom.toast.textContent = String(message || (isError ? '操作失败' : '操作成功'));
  dom.toast.classList.toggle('error', Boolean(isError));
  dom.toast.classList.add('show');
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    dom.toast.classList.remove('show');
  }, 2200);
}

async function fetchJson(url, options = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  const rawText = await response.text();
  let payload = null;
  try {
    payload = rawText ? JSON.parse(rawText) : null;
  } catch {
    const preview = String(rawText || '').replace(/\s+/g, ' ').slice(0, 160);
    throw new Error(`接口返回了无法解析的响应：${url} (HTTP ${response.status}) ${preview}`);
  }

  if (!response.ok || payload?.success === false) {
    throw new Error(payload?.error || `请求失败：${response.status}`);
  }
  return payload;
}

async function fetchResourceStatus(keys) {
  const payload = await fetchJson(buildDashboardStatusUrl(keys), { cache: 'no-store' });
  return readObject(payload?.data || payload);
}

function resourceStatusSignature(payload) {
  const meta = readObject(payload);
  return [
    String(meta.updateTime || ''),
    String(meta.cacheTime || ''),
    meta.servedFromCache ? '1' : '0',
  ].join('|');
}

function shouldReloadResourceByMeta(key, nextMeta) {
  if (!nextMeta || typeof nextMeta !== 'object') return false;
  const resource = state.resources[key];
  if (!resource || resource.status === 'idle' || resource.status === 'error' || !resource.data) return true;
  return resourceStatusSignature(readResourceStatusMeta(key)) !== resourceStatusSignature(nextMeta);
}

async function loadResource(key, endpoint, onRender, options = {}) {
  const previousData = state.resources[key].data;
  const keepVisibleData = Boolean(options.background && previousData);
  state.resources[key].refreshing = keepVisibleData;
  state.resources[key].status = keepVisibleData ? 'ready' : 'loading';
  state.resources[key].error = null;
  onRender();

  try {
    const payload = await fetchJson(buildEndpointUrl(endpoint, options));
    state.resources[key].status = 'ready';
    state.resources[key].data = payload;
    state.resources[key].error = null;
  } catch (error) {
    state.resources[key].status = keepVisibleData ? 'ready' : 'error';
    state.resources[key].error = error;
    if (!keepVisibleData) {
      state.resources[key].data = null;
    }
  } finally {
    state.resources[key].refreshing = false;
  }

  onRender();
}

async function refreshDividendResource(options = {}) {
  const background = options.background !== false;
  await loadResource('dividend', ENDPOINTS.dividendRefresh, renderEverything, {
    force: Boolean(options.force),
    background,
  });
}

function bindEvents() {
  if (state.eventsBound) return;

  dom.tabButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const nextTab = button.dataset.tab;
      if (!TAB_SEQUENCE.includes(nextTab)) return;
      state.activeTab = nextTab;
      renderTabs();
      renderActivePanel();
      void ensureActiveTabResourcesLoaded({ background: false });
    });
  });

  dom.reloadDataButton?.addEventListener('click', () => {
    void reloadAllData();
  });

  dom.pushForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    await savePushConfig();
  });

  document.addEventListener('submit', (event) => {
    const cbArbPushForm = event.target.closest('#cb-arb-push-form');
    if (cbArbPushForm) {
      event.preventDefault();
      void saveCbArbPushConfig(cbArbPushForm);
      return;
    }

    const lofArbPushForm = event.target.closest('#lof-arb-push-form');
    if (lofArbPushForm) {
      event.preventDefault();
      void saveLofArbPushConfig(lofArbPushForm);
      return;
    }

    const monitorForm = event.target.closest('#monitor-editor-form');
    if (!monitorForm) return;
    event.preventDefault();
    void saveMonitorFromForm(monitorForm);
  });

  document.addEventListener('input', (event) => {
    const tableSearchField = event.target.closest('[data-table-search-key]');
    if (tableSearchField) {
      const tableKey = String(tableSearchField.dataset.tableSearchKey || '').trim();
      const focusSnapshot = buildTableSearchFocusSnapshot(tableKey, tableSearchField, tableSearchField.value);
      setTableSearchQuery(
        tableKey,
        String(tableSearchField.value || ''),
        {
          render: !(event.isComposing || state.searchComposition?.[tableKey]),
          focusSnapshot,
        }
      );
      return;
    }

    const monitorField = event.target.closest('#monitor-editor-form [name]');
    if (!monitorField) return;
    const fieldName = String(monitorField.name || '').trim();
    const fieldValue = String(monitorField.value || '');
    syncMonitorDraftField(fieldName, fieldValue);

    if (fieldName === 'acquirerName') {
      queueMonitorLookup('acquirer', fieldValue);
      return;
    }
    if (fieldName === 'targetName') {
      queueMonitorLookup('target', fieldValue);
    }
  });

  document.addEventListener('change', (event) => {
    const monitorField = event.target.closest('#monitor-editor-form [name]');
    if (!monitorField) return;
    syncMonitorDraftField(String(monitorField.name || '').trim(), String(monitorField.value || ''));
  });

  document.addEventListener('compositionstart', (event) => {
    const tableSearchField = event.target.closest('[data-table-search-key]');
    if (!tableSearchField) return;
    setTableSearchCompositionState(String(tableSearchField.dataset.tableSearchKey || '').trim(), true);
  });

  document.addEventListener('compositionend', (event) => {
    const tableSearchField = event.target.closest('[data-table-search-key]');
    if (!tableSearchField) return;
    const tableKey = String(tableSearchField.dataset.tableSearchKey || '').trim();
    setTableSearchCompositionState(tableKey, false);
    setTableSearchQuery(tableKey, String(tableSearchField.value || ''), {
      focusSnapshot: buildTableSearchFocusSnapshot(tableKey, tableSearchField, tableSearchField.value),
    });
  });

  document.addEventListener('click', (event) => {
    const monitorAction = event.target.closest('[data-monitor-action]');
    if (monitorAction) {
      const action = monitorAction.dataset.monitorAction;
      const monitorId = monitorAction.dataset.monitorId || '';
      if (action === 'open-create') {
        openMonitorCreateMode();
        renderMonitorPanel();
        return;
      }
      if (action === 'close-editor') {
        closeMonitorEditor();
        renderMonitorPanel();
        return;
      }
      if (action === 'edit') {
        enterMonitorEditMode(monitorId);
        renderMonitorPanel();
        return;
      }
      if (action === 'delete') {
        void deleteMonitorById(monitorId);
        return;
      }
    }

    const monitorLookupSelect = event.target.closest('[data-monitor-lookup-role][data-monitor-lookup-index]');
    if (monitorLookupSelect) {
      applyMonitorLookupCandidate(
        String(monitorLookupSelect.dataset.monitorLookupRole || '').trim(),
        Number(monitorLookupSelect.dataset.monitorLookupIndex || -1)
      );
      return;
    }

    const sortTarget = event.target.closest('.sort-head[data-table-key][data-sort-key]');
    if (sortTarget) {
      handleSortClick(sortTarget.dataset.tableKey, sortTarget.dataset.sortKey);
      return;
    }

    const pageTarget = event.target.closest('.pagination-button[data-table-key][data-page-action]');
    if (pageTarget) {
      handlePageClick(pageTarget.dataset.tableKey, pageTarget.dataset.pageAction);
      return;
    }

    const clearSearchTarget = event.target.closest('[data-table-search-clear]');
    if (clearSearchTarget) {
      const tableKey = String(clearSearchTarget.dataset.tableSearchClear || '').trim();
      setTableSearchQuery(tableKey, '', {
        focusSnapshot: buildTableSearchFocusSnapshot(tableKey, null, ''),
      });
      return;
    }

    const expandTarget = event.target.closest('.expand-button[data-table-key][data-row-id]');
    if (expandTarget) {
      const tableKey = expandTarget.dataset.tableKey;
      const rowId = expandTarget.dataset.rowId;
      toggleExpandedState(tableKey, rowId);
      if (tableKey === 'cbArb' || tableKey === 'cbArbSmallRedemption') return renderConvertibleBondPanel();
      if (tableKey === 'ah') return renderPremiumPanel('ah');
      if (tableKey === 'ab') return renderPremiumPanel('ab');
      if (tableKey === 'lofArb') return renderLofArbPanel();
      if (tableKey === 'monitor') return renderMonitorPanel();
      if (tableKey === 'merger' || tableKey.startsWith('eventArb')) return renderMergerPanel();
    }

    const cbArbSubtabTarget = event.target.closest('[data-cb-arb-subtab]');
    if (cbArbSubtabTarget) {
      const subtab = String(cbArbSubtabTarget.dataset.cbArbSubtab || '').trim();
      if (!CB_ARB_SUBTAB_SEQUENCE.includes(subtab)) return;
      state.cbArbSubview = subtab;
      renderConvertibleBondPanel();
      return;
    }

    const lofSubviewTarget = event.target.closest('[data-lof-subview]');
    if (lofSubviewTarget) {
      const subview = String(lofSubviewTarget.dataset.lofSubview || '').trim();
      const allowed = readLofArbGroups().map((item) => String(item.key || '').trim());
      if (!allowed.includes(subview)) return;
      state.lofSubview = subview;
      state.tables.lofArb.page = 1;
      renderLofArbPanel();
      return;
    }

    const eventArbSubtab = event.target.closest('[data-event-arb-subtab]');
    if (eventArbSubtab) {
      const subtab = String(eventArbSubtab.dataset.eventArbSubtab || '').trim();
      if (!EVENT_ARB_SUBTAB_SEQUENCE.includes(subtab)) return;
      state.mergerSubview = subtab;
      renderMergerPanel();
      return;
    }

    const cbRightsIssueMarketSubtab = event.target.closest('[data-cb-rights-issue-market-subtab]');
    if (cbRightsIssueMarketSubtab) {
      const subtab = String(cbRightsIssueMarketSubtab.dataset.cbRightsIssueMarketSubtab || '').trim();
      if (!CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE.includes(subtab)) return;
      state.cbRightsIssueMarketSubview = subtab;
      renderCbRightsIssuePanel();
      return;
    }

  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) return;
    void runAutoRefreshTick('visibility');
  });

  state.eventsBound = true;
}

function renderHeaderOnly() {
  renderStatusLine();
  renderRuntimeVersionText();
  renderSubscriptionSummary();
  renderPushSettings();
}

function renderEverything() {
  renderHeaderOnly();
  renderActivePanel();
}

function renderCallbackForResource(key) {
  if (['exchangeRate', 'ipo', 'bonds', 'pushConfig', 'cbArbPushConfig'].includes(key)) {
    return (key === 'pushConfig' || key === 'cbArbPushConfig') ? renderPushSettings : renderHeaderOnly;
  }
  return renderEverything;
}

function buildHeaderLoadTasks(options = {}) {
  const forceMarket = Boolean(options.forceMarket);
  const background = Boolean(options.background);
  const tasks = [];
  if (options.includeUiConfig) {
    tasks.push(loadResource('uiConfig', ENDPOINTS.uiConfig, renderDashboardUiState, { background }));
  }
  tasks.push(loadResource('health', ENDPOINTS.health, renderHeaderOnly, { background }));
  tasks.push(loadResource('pushConfig', ENDPOINTS.pushConfig, renderPushSettings, { background }));
  tasks.push(loadResource('cbArbPushConfig', ENDPOINTS.cbArbPushConfig, renderPushSettings, { background }));
  tasks.push(loadResource('exchangeRate', ENDPOINTS.exchangeRate, renderHeaderOnly, { force: forceMarket, background }));
  tasks.push(loadResource('ipo', ENDPOINTS.ipo, renderHeaderOnly, { force: forceMarket, background }));
  tasks.push(loadResource('bonds', ENDPOINTS.bonds, renderHeaderOnly, { force: forceMarket, background }));
  return tasks;
}

function buildActiveTabLoadTasks(options = {}) {
  const forceMarket = Boolean(options.forceMarket);
  const background = Boolean(options.background);
  if (state.activeTab === 'cb-arb') {
    return [loadResource('cbArb', ENDPOINTS.cbArb, renderEverything, { force: forceMarket, background })];
  }
  if (state.activeTab === 'ah') {
    return [loadResource('ah', ENDPOINTS.ah, renderEverything, { force: forceMarket, background })];
  }
  if (state.activeTab === 'ab') {
    return [loadResource('ab', ENDPOINTS.ab, renderEverything, { force: forceMarket, background })];
  }
  if (state.activeTab === 'lof-arb') {
    return [
      loadResource('lofArb', ENDPOINTS.lofArb, renderEverything, { force: forceMarket, background }),
      loadResource('lofArbPushConfig', ENDPOINTS.lofArbPushConfig, renderEverything, { background }),
    ];
  }
  if (state.activeTab === 'monitor') {
    return [loadResource('monitor', ENDPOINTS.monitor, renderEverything, { background })];
  }
  if (state.activeTab === 'dividend') {
    return [loadResource('dividend', ENDPOINTS.dividend, renderEverything, { background })];
  }
  if (state.activeTab === 'merger') {
    return [loadResource('merger', ENDPOINTS.merger, renderEverything, { force: forceMarket, background })];
  }
  if (state.activeTab === 'cb-rights-issue') {
    return [
      loadResource('cbRightsIssue', ENDPOINTS.cbRightsIssue, renderEverything, { force: forceMarket, background }),
    ];
  }
  return [];
}

async function ensureActiveTabResourcesLoaded(options = {}) {
  const resourceKeys = readTabResourceKeys();
  if (!resourceKeys.length) return;
  const needsLoad = Boolean(options.force)
    || resourceKeys.some((key) => {
      const resource = state.resources[key];
      return !resource || resource.status === 'idle' || !resource.data;
    });
  if (!needsLoad) return;
  await Promise.allSettled(buildActiveTabLoadTasks({
    forceMarket: Boolean(options.force),
    background: Boolean(options.background),
  }));
  if (state.activeTab === 'dividend') {
    void refreshDividendResource({ background: true, force: Boolean(options.force) });
  }
}

async function revalidateCriticalResourcesOnce() {
  const currentTabDatasetKeys = readActiveTabDatasetStatusKeys().filter((key) => CRITICAL_CACHE_REVALIDATION_KEYS.includes(key));
  const tasks = [...new Set(['exchangeRate', ...currentTabDatasetKeys])]
    .filter((key) => resourceServedFromCache(key))
    .filter((key) => !state.cacheRevalidated[key])
    .map((key) => {
      state.cacheRevalidated[key] = true;
      return loadResource(key, ENDPOINTS[key], renderCallbackForResource(key), { force: true, background: true });
    });

  if (tasks.length) {
    await Promise.allSettled(tasks);
  }
}

async function bootstrap(options = {}) {
  bindEvents();
  applyDashboardTheme();
  applyTableUiConfigFromState();
  renderAll();
  const forceMarket = Boolean(options.forceMarket);
  const skipCacheRevalidation = Boolean(options.skipCacheRevalidation);

  const tasks = [
    ...buildHeaderLoadTasks({ includeUiConfig: true, forceMarket }),
    ...buildActiveTabLoadTasks({ forceMarket }),
  ];

  await Promise.allSettled(tasks);
  renderAll();

  if (state.activeTab === 'dividend' && !forceMarket) {
    void refreshDividendResource({ background: true });
  }

  if (!forceMarket && !skipCacheRevalidation) {
    await revalidateCriticalResourcesOnce();
  }
}

async function runAutoRefreshTick(_reason = 'interval') {
  const config = readDashboardAutoRefreshConfig();
  if (!config.enabled || state.autoRefreshTickRunning) return;
  if (document.hidden) return;
  state.autoRefreshTickRunning = true;
  try {
    const statusKeys = readAutoRefreshDatasetStatusKeys(config);
    const changedDatasetKeys = [];
    if (statusKeys.length) {
      try {
        const statusMap = await fetchResourceStatus(statusKeys);
        for (const key of Object.keys(statusMap)) {
          if (shouldReloadResourceByMeta(key, statusMap[key])) {
            changedDatasetKeys.push(key);
          }
        }
        state.resourceMeta = {
          ...state.resourceMeta,
          ...statusMap,
        };
        renderHeaderOnly();
        renderActivePanel();
      } catch (_error) {
        // 状态轮询失败时不打断现有页面，只保留旧快照。
      }
    }

    const tasks = [
      loadResource('health', ENDPOINTS.health, renderHeaderOnly, { background: true }),
      loadResource('pushConfig', ENDPOINTS.pushConfig, renderPushSettings, { background: true }),
      loadResource('cbArbPushConfig', ENDPOINTS.cbArbPushConfig, renderPushSettings, { background: true }),
    ];

    if (changedDatasetKeys.includes('exchangeRate')) {
      tasks.push(loadResource('exchangeRate', ENDPOINTS.exchangeRate, renderHeaderOnly, { background: true }));
    }
    if (changedDatasetKeys.includes('ipo')) {
      tasks.push(loadResource('ipo', ENDPOINTS.ipo, renderHeaderOnly, { background: true }));
    }
    if (changedDatasetKeys.includes('bonds')) {
      tasks.push(loadResource('bonds', ENDPOINTS.bonds, renderHeaderOnly, { background: true }));
    }

    const activeDatasetKeys = readActiveTabDatasetStatusKeys();
    if (state.activeTab === 'cb-arb') {
      tasks.push(...buildActiveTabLoadTasks({ background: true, forceMarket: true }));
    } else if (config.reloadDataOnCacheChange && activeDatasetKeys.some((key) => changedDatasetKeys.includes(key))) {
      tasks.push(...buildActiveTabLoadTasks({ background: true }));
    } else if (!activeDatasetKeys.length) {
      tasks.push(...buildActiveTabLoadTasks({ background: true }));
    }

    if (tasks.length) {
      await Promise.allSettled(tasks);
    }
  } finally {
    state.autoRefreshTickRunning = false;
  }
}

function restartAutoRefreshLoop() {
  if (state.autoRefreshTimer) {
    window.clearInterval(state.autoRefreshTimer);
    state.autoRefreshTimer = null;
  }
  const config = readDashboardAutoRefreshConfig();
  if (!config.enabled) return;
  state.autoRefreshTimer = window.setInterval(() => {
    void runAutoRefreshTick('interval');
  }, config.intervalMs);
}

async function reloadAllData() {
  showToast('正在强制刷新当前页相关数据');
  await bootstrap({ forceMarket: true, skipCacheRevalidation: true });
  showToast('当前页相关数据已刷新');
}

function renderAll() {
  renderTabs();
  renderStatusLine();
  renderSubscriptionSummary();
  renderPushSettings();
  renderActivePanel();
}

function renderTabs() {
  dom.tabButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.tab === state.activeTab);
  });

  Object.entries(dom.tabPanels).forEach(([key, panel]) => {
    if (!panel) return;
    panel.classList.toggle('active', key === state.activeTab);
  });
}

function readHealthResponse() {
  return readResourceObject('health').data || readResourceObject('health');
}

function renderRuntimeVersionText() {
  if (!dom.buildVersionText) return;

  const resource = state.resources.health;
  if (resource.status === 'loading' || resource.status === 'idle') {
    dom.buildVersionText.textContent = '版本信息读取中';
    return;
  }

  if (resource.status === 'error') {
    dom.buildVersionText.textContent = '版本信息读取失败';
    return;
  }

  const version = readObject(readHealthResponse().version);
  const parts = [];
  if (version.gitBranch || version.gitShortSha) {
    parts.push(`${String(version.gitBranch || '--')} @ ${String(version.gitShortSha || 'unknown')}`);
  } else if (version.gitSha) {
    parts.push(String(version.gitSha).slice(0, 7));
  }
  if (version.appVersion) {
    parts.push(`v${String(version.appVersion)}`);
  }
  if (version.startedAt) {
    parts.push(`启动 ${formatDate(version.startedAt)}`);
  }

  dom.buildVersionText.textContent = parts.length
    ? `当前版本 ${parts.join(' / ')}`
    : '版本信息暂未返回';
}

function renderStatusLine() {
  if (!dom.statusLine || !dom.statusUpdateText) return;

  const exchangeResource = state.resources.exchangeRate;
  const cbResource = state.resources.cbArb;

  if (
    (exchangeResource.status === 'loading' || exchangeResource.status === 'idle') &&
    (cbResource.status === 'loading' || cbResource.status === 'idle')
  ) {
    dom.statusLine.innerHTML = loadingInlineStatus();
    dom.statusUpdateText.textContent = '正在连接市场接口';
    return;
  }

  if (exchangeResource.status === 'error' && cbResource.status === 'error') {
    dom.statusLine.innerHTML = `
      <span class="status-inline-item"><span>市场状态</span><strong>加载失败</strong></span>
      <span class="status-separator">/</span>
      <span class="status-inline-item"><span>请确认</span><strong>云端服务可访问</strong></span>
    `;
    dom.statusUpdateText.textContent = '请先确认云端服务健康并可访问';
    return;
  }

  const exchange = readResourceObject('exchangeRate').data || readResourceObject('exchangeRate');
  const cbPayload = readResourceObject('cbArb');
  const segments = [
    { label: 'HKD/CNY', value: formatNumber(exchange.hkToCny ?? exchange.hkdToCny, 4) },
    { label: 'USD/CNY', value: formatNumber(exchange.usdToCny, 4) },
    {
      label: '十年期国债收益率',
      value: cbPayload.treasuryYield10y != null ? `${formatNumber(cbPayload.treasuryYield10y, 2)}%` : '暂未返回',
    },
  ];

  const updateTime = maxUpdateTime(['exchangeRate', 'cbArb']);
  const statusItems = [
    ...segments.map((item) => `
      <span class="status-inline-item">
        <span>${escapeHtml(item.label)}</span>
        <strong>${escapeHtml(item.value)}</strong>
      </span>
    `),
    updateTime
      ? `
        <span class="status-inline-item">
          <span>更新时间</span>
          <strong>${escapeHtml(formatDate(updateTime))}</strong>
        </span>
      `
      : '',
  ].filter(Boolean);
  dom.statusLine.innerHTML = statusItems.join('<span class="status-separator">/</span>');
  if (resourceRefreshing('exchangeRate') || resourceRefreshing('cbArb')) {
    dom.statusUpdateText.textContent = '当前先显示缓存快照，后台正在校准实时值';
    return;
  }
  if (resourceServedFromCache('exchangeRate') || resourceServedFromCache('cbArb')) {
    dom.statusUpdateText.textContent = '当前显示缓存快照，可点击“刷新”强制拉取实时值';
    return;
  }
  dom.statusUpdateText.textContent = updateTime ? '实时数据已连接' : '等待更多数据返回';
}

function renderSubscriptionSummary() {
  if (!dom.subscriptionSummary || !dom.lastRefreshText) return;

  const ipoResource = state.resources.ipo;
  const bondResource = state.resources.bonds;

  if (
    (ipoResource.status === 'loading' || ipoResource.status === 'idle') &&
    (bondResource.status === 'loading' || bondResource.status === 'idle')
  ) {
    dom.subscriptionSummary.innerHTML = loadingSubscriptionTable();
    dom.lastRefreshText.textContent = '正在聚合今日打新事件';
    return;
  }

  if (ipoResource.status === 'error' && bondResource.status === 'error') {
    dom.subscriptionSummary.innerHTML = simpleEmpty('今日打新数据加载失败');
    dom.lastRefreshText.textContent = '请稍后重试';
    return;
  }

  const rows = buildTodaySubscriptionRows(readResourceArray('ipo'), readResourceArray('bonds'));
  dom.subscriptionSummary.innerHTML = `${renderSubscriptionTable(rows)}${renderModuleFootnote('subscription')}`;

  const updateTime = maxUpdateTime(['ipo', 'bonds']);
  dom.lastRefreshText.textContent = updateTime ? `最近更新时间：${formatDate(updateTime)}` : '等待打新接口返回';
}

function buildTodaySubscriptionRows(ipoRows, bondRows) {
  const today = todayKey();
  const rows = [];

  const pushRow = (records, typeLabel, recordType) => {
    records.forEach((row) => {
      // “中签缴款日”必须回到真实缴款日口径，不能再拿摇号/中签公告日顶替。
      const paymentDisplayDate = row.paymentDate;
      const stages = [];
      if (normalizeDateKey(row.subscribeDate) === today) stages.push(SUBSCRIPTION_STAGES[0]);
      if (normalizeDateKey(paymentDisplayDate) === today) stages.push(SUBSCRIPTION_STAGES[1]);
      if (normalizeDateKey(row.listingDate) === today) stages.push(SUBSCRIPTION_STAGES[2]);
      stages.forEach((stage) => {
        rows.push({
          // 申购总览表按字段拆列展示，避免“名称/代码”“发行价/转股价”耦合后占用额外行高
          stageLabel: stage.label,
          stageClassName: stage.className,
          typeLabel,
          name: row.name || row.bondName || row.stockName || '--',
          code: row.code || row.bondCode || row.stockCode || '--',
          subscribeDate: row.subscribeDate,
          paymentDisplayDate,
          listingDate: row.listingDate,
          subscribeLimit: row.subscribeLimit,
          issuePrice: recordType === 'ipo' ? row.issuePrice : null,
          convertPrice: recordType === 'ipo' ? null : row.convertPrice,
        });
      });
    });
  };

  pushRow(ipoRows, '新股', 'ipo');
  pushRow(bondRows, '转债', 'bond');

  return rows.sort((a, b) => {
    const stageDiff = stageOrder(a.stageClassName) - stageOrder(b.stageClassName);
    if (stageDiff !== 0) return stageDiff;
    return `${a.typeLabel}-${a.code}`.localeCompare(`${b.typeLabel}-${b.code}`, 'zh-CN');
  });
}

function stageOrder(className) {
  const index = SUBSCRIPTION_STAGES.findIndex((item) => item.className === className);
  return index >= 0 ? index : 999;
}

function renderSubscriptionTable(rows) {
  const tableRows = rows.length
    ? rows.map((row) => `
    <tr class="subscription-row ${escapeHtml(row.stageClassName)}">
      <td><span class="stage-pill ${escapeHtml(row.stageClassName)}">${escapeHtml(row.stageLabel)}</span></td>
      <td><span class="type-tag">${escapeHtml(row.typeLabel)}</span></td>
      <td>${escapeHtml(row.name)}</td>
      <td><span class="mono-text">${escapeHtml(row.code)}</span></td>
      <td>${escapeHtml(formatDateOnly(row.subscribeDate))}</td>
      <td>${escapeHtml(formatDateOnly(row.paymentDisplayDate))}</td>
      <td>${escapeHtml(formatDateOnly(row.listingDate))}</td>
      <td>${escapeHtml(formatSubscribeLimit(row.subscribeLimit))}</td>
      <td>${escapeHtml(formatNumber(row.issuePrice, 2))}</td>
      <td>${escapeHtml(formatNumber(row.convertPrice, 2))}</td>
    </tr>
  `).join('')
    : `
      <tr>
        <td colspan="10">
          <div class="empty-state">今日无数据</div>
        </td>
      </tr>
    `;

  return `
    <div class="table-wrap">
      <table data-table-kind="subscription">
        <thead>
          <tr>
            <th>当前阶段</th>
            <th>类型</th>
            <th>名称</th>
            <th>代码</th>
            <th>申购日</th>
            <th>中签缴款日</th>
            <th>上市日</th>
            <th>申购上限</th>
            <th>发行价</th>
            <th>转股价</th>
          </tr>
        </thead>
        <tbody>${tableRows}</tbody>
      </table>
    </div>
  `;
}

function formatSubscribeLimit(value) {
  const parsed = toNumber(value);
  if (parsed === null) return '--';
  return `${formatInt(parsed)} 手`;
}

function loadingInlineStatus() {
  return `
    <span class="loading-line short"></span>
    <span class="loading-line short"></span>
    <span class="loading-line short"></span>
  `;
}

function loadingSubscriptionTable() {
  return `
    <div class="table-wrap">
      <table data-table-kind="subscription">
        <thead>
          <tr>
            <th>当前阶段</th>
            <th>类型</th>
            <th>名称</th>
            <th>代码</th>
            <th>申购日</th>
            <th>中签缴款日</th>
            <th>上市日</th>
            <th>申购上限</th>
            <th>发行价</th>
            <th>转股价</th>
          </tr>
        </thead>
        <tbody>
          ${Array.from({ length: 3 }, () => `
            <tr>
              <td colspan="10">
                <div class="loading-line"></div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function readPushConfigViewModel() {
  return readResourceObject("pushConfig").data || readResourceObject("pushConfig");
}

function resolvePushConfigTimes(config = {}) {
  const times = Array.isArray(config.times) ? config.times : [];
  return {
    times,
    mainTime1: times[0] || config.time || "",
    mainTime2: times[1] || "",
  };
}

function applyPushConfigToInputs(config = {}) {
  const next = resolvePushConfigTimes(config);
  if (dom.pushTime1) dom.pushTime1.value = next.mainTime1;
  if (dom.pushTime2) dom.pushTime2.value = next.mainTime2;
}

function readEnabledPushModules(config = {}) {
  const modules = (config.modules && typeof config.modules === 'object') ? config.modules : {};
  return Object.entries(modules)
    .filter(([, enabled]) => Boolean(enabled))
    .map(([key]) => PUSH_MODULE_LABELS[key] || key);
}

function shortErrorText(value) {
  return String(value || '').replace(/\s+/g, ' ').slice(0, 48);
}

function buildPushStateText(config = {}) {
  const next = resolvePushConfigTimes(config);
  const delivery = config.deliveryStatus || {};
  const discountStrategyStatus = (config.discountStrategyStatus && typeof config.discountStrategyStatus === 'object')
    ? config.discountStrategyStatus
    : {};
  const moduleText = readEnabledPushModules(config).join(' / ') || '--';

  const summaryLine = [
    config.enabled === false
      ? '定时推送已关闭'
      : `定时推送 ${[next.mainTime1, next.mainTime2].filter(Boolean).join(' / ') || '--'}`,
    `模块 ${moduleText}`,
    `调度 ${delivery.calendarMode || '--'}`,
    delivery.webhookConfigured === false ? 'Webhook 未配置' : 'Webhook 已配置',
    delivery.pushHtmlUrlConfigured === false ? '网页入口未配置' : '网页入口已配置',
    delivery.schedulerEnabled === false
      ? (delivery.schedulerDisabledReason === 'loopback_public_base_url' ? '本地运行已禁用服务端推送调度' : '服务端调度已关闭')
      : '',
    delivery.lastMainPushSuccessAt ? `最近成功 ${formatDate(delivery.lastMainPushSuccessAt)}` : '',
    delivery.lastMainPushError ? `最近失败 ${shortErrorText(delivery.lastMainPushError)}` : '',
  ].filter(Boolean).join(' / ');

  const monitorSlotCount = Array.isArray(discountStrategyStatus.monitorSessionTimes)
    ? discountStrategyStatus.monitorSessionTimes.length
    : 0;
  const sessionText = Array.isArray(discountStrategyStatus.sessionWindows) && discountStrategyStatus.sessionWindows.length
    ? discountStrategyStatus.sessionWindows.join(' / ')
    : '--';

  const alertLine = [
    discountStrategyStatus.enabled === false ? '低溢价推送已关闭' : '低溢价推送开启',
    `买入阈值 ${formatPercent(discountStrategyStatus.buyThreshold, 2)}`,
    `卖出阈值 ${formatPercent(discountStrategyStatus.sellThreshold, 2)}`,
    `交易时段 ${sessionText}`,
    `监控时点 ${monitorSlotCount} 个`,
    discountStrategyStatus.lastBuySignalSuccessAt ? `买入最近成功 ${formatDate(discountStrategyStatus.lastBuySignalSuccessAt)}` : '',
    discountStrategyStatus.lastBuySignalError ? `买入最近失败 ${shortErrorText(discountStrategyStatus.lastBuySignalError)}` : '',
    discountStrategyStatus.lastSellSignalSuccessAt ? `卖出最近成功 ${formatDate(discountStrategyStatus.lastSellSignalSuccessAt)}` : '',
    discountStrategyStatus.lastSellSignalError ? `卖出最近失败 ${shortErrorText(discountStrategyStatus.lastSellSignalError)}` : '',
    discountStrategyStatus.lastMonitorPushSuccessAt ? `监控最近成功 ${formatDate(discountStrategyStatus.lastMonitorPushSuccessAt)}` : '',
    discountStrategyStatus.lastMonitorPushError ? `监控最近失败 ${shortErrorText(discountStrategyStatus.lastMonitorPushError)}` : '',
  ].filter(Boolean).join(' / ');

  return { summaryLine, alertLine };
}

function resolveCbArbPushConfigTimes(config = {}) {
  const times = Array.isArray(config.times) ? config.times.filter(Boolean) : [];
  return {
    times,
    time1: times[0] || '08:00',
    time2: times[1] || '14:30',
  };
}

function buildCbArbPushStateText(config = {}) {
  const delivery = config?.deliveryStatus && typeof config.deliveryStatus === 'object' ? config.deliveryStatus : {};
  const next = resolveCbArbPushConfigTimes(config);
  return [
    config.enabled === false ? '\u72ec\u7acb\u63a8\u9001\u5df2\u5173\u95ed' : `\u65f6\u95f4 ${next.times.join(' / ') || '--'}`,
    delivery.webhookConfigured === false ? 'Webhook \u672a\u914d\u7f6e' : 'Webhook \u5df2\u914d\u7f6e',
    delivery.schedulerEnabled === false
      ? (delivery.schedulerDisabledReason === 'loopback_public_base_url'
        ? '\u672c\u5730\u8fd0\u884c\u5df2\u7981\u7528\u670d\u52a1\u7aef\u8c03\u5ea6'
        : '\u670d\u52a1\u7aef\u8c03\u5ea6\u5df2\u5173\u95ed')
      : '',
    delivery.lastSuccessAt ? `\u6700\u8fd1\u6210\u529f ${formatDate(delivery.lastSuccessAt)}` : '',
    delivery.lastError ? `\u6700\u8fd1\u5931\u8d25 ${shortErrorText(delivery.lastError)}` : '',
  ].filter(Boolean).join(' / ');
}

function renderCbArbPushSettingsCard() {
  const host = dom.cbArbPushSettingsHost;
  if (!host) return;

  const resource = state.resources.cbArbPushConfig;
  const config = readCbArbPushConfigViewModel();
  const next = resolveCbArbPushConfigTimes(config);
  const statusText = resource.status === 'loading' && !resource.data
    ? '\u6b63\u5728\u8bfb\u53d6\u53ef\u8f6c\u503a\u5957\u5229\u72ec\u7acb\u63a8\u9001\u72b6\u6001'
    : resource.status === 'error' && !Object.keys(config || {}).length
      ? '\u72ec\u7acb\u63a8\u9001\u914d\u7f6e\u8bfb\u53d6\u5931\u8d25'
      : state.savingCbArbPush
        ? '\u6b63\u5728\u4fdd\u5b58\u53ef\u8f6c\u503a\u5957\u5229\u63a8\u9001\u914d\u7f6e'
        : buildCbArbPushStateText(config) || '\u5f85\u540e\u7aef\u63a5\u5165';

  host.innerHTML = `
    <div class="list-card">
      <div class="module-toolbar">
        <div>
          <h3>\u53ef\u8f6c\u503a\u5957\u5229\u63a8\u9001</h3>
          <div class="section-note">\u72ec\u7acb\u4e8e 8 \u70b9\u4e3b\u6458\u8981\u63a8\u9001\uff0c\u8fd9\u91cc\u53ea\u8d1f\u8d23\u524d\u7aef\u914d\u7f6e\u8bfb\u5199\uff1b\u5177\u4f53\u53bb\u91cd\u4e0e\u6d88\u606f\u6a21\u677f\u4ecd\u7531\u540e\u7aef\u5b9e\u73b0\u3002</div>
        </div>
        <div class="panel-meta">
          <span>${escapeHtml(statusText)}</span>
        </div>
      </div>
      <form id="cb-arb-push-form" class="push-form">
        <div class="input-group">
          <label for="cb-arb-push-time-1">\u63a8\u9001\u65f6\u95f4 1</label>
          <input id="cb-arb-push-time-1" name="time1" type="time" value="${escapeHtml(next.time1)}" ${resource.status === 'loading' || state.savingCbArbPush ? 'disabled' : ''} />
        </div>
        <div class="input-group">
          <label for="cb-arb-push-time-2">\u63a8\u9001\u65f6\u95f4 2</label>
          <input id="cb-arb-push-time-2" name="time2" type="time" value="${escapeHtml(next.time2)}" ${resource.status === 'loading' || state.savingCbArbPush ? 'disabled' : ''} />
        </div>
        <div class="button-row inline">
          <button type="submit" class="btn-primary" ${resource.status === 'loading' || state.savingCbArbPush ? 'disabled' : ''}>\u4fdd\u5b58</button>
        </div>
      </form>
    </div>
  `;
}

function renderPushSettings() {
  renderCbArbPushSettingsCard();
  const resource = state.resources.pushConfig;
  if (!dom.pushStateText || !dom.pushAlertStateText || !dom.savePushButton) return;

  dom.savePushButton.disabled = resource.status === "loading" || state.savingPush;
  if (dom.reloadDataButton) {
    dom.reloadDataButton.disabled = resource.status === "loading" || state.savingPush;
  }

  if (resource.status === "loading" && !resource.data) {
    dom.pushStateText.textContent = "正在读取定时推送状态";
    dom.pushAlertStateText.textContent = "正在读取低溢价推送状态";
    return;
  }

  const config = readPushConfigViewModel();
  const hasConfig = Boolean(config && Object.keys(config).length);

  if (resource.status !== "error" && hasConfig && !state.savingPush) {
    applyPushConfigToInputs(config);
  }

  if (resource.status === "error" && !hasConfig) {
    dom.pushStateText.textContent = "推送配置读取失败";
    dom.pushAlertStateText.textContent = "低溢价推送状态读取失败";
    return;
  }

  if (state.savingPush) {
    dom.pushStateText.textContent = "正在保存推送设置";
    dom.pushAlertStateText.textContent = "正在同步低溢价推送状态";
    return;
  }

  if (resource.status === "error") {
    dom.pushStateText.textContent = "推送配置读取失败，保留当前输入";
    dom.pushAlertStateText.textContent = "低溢价推送状态读取失败，保留当前输入";
    return;
  }

  const pushState = buildPushStateText(config);
  dom.pushStateText.textContent = pushState.summaryLine;
  dom.pushAlertStateText.textContent = pushState.alertLine;
}

async function savePushConfig() {
  const config = readPushConfigViewModel();
  const time1 = dom.pushTime1?.value.trim();
  const time2 = dom.pushTime2?.value.trim();
  const validTimes = [time1, time2].filter(Boolean);

  if (!time1 || !time2) {
    showToast("两个定时推送时间都需要填写", true);
    return;
  }

  state.savingPush = true;
  renderPushSettings();

  try {
    const payload = await fetchJson(ENDPOINTS.pushConfig, {
      method: "POST",
      body: JSON.stringify({
        enabled: config.enabled !== false,
        modules: config.modules || {},
        times: validTimes,
      }),
    });

    state.resources.pushConfig.status = "ready";
    state.resources.pushConfig.data = payload;
    state.resources.pushConfig.error = null;
    const syncedPayload = await fetchJson(ENDPOINTS.pushConfig, { method: "GET" });
    state.resources.pushConfig.status = "ready";
    state.resources.pushConfig.data = syncedPayload;
    state.resources.pushConfig.error = null;
    showToast("推送设置已保存并同步到当前页面");
  } catch (error) {
    state.resources.pushConfig.status = "error";
    state.resources.pushConfig.error = error;
    showToast(error.message || "推送设置保存失败", true);
  } finally {
    state.savingPush = false;
    renderPushSettings();
  }
}

async function saveCbArbPushConfig(form) {
  const config = readCbArbPushConfigViewModel();
  const formData = new FormData(form);
  const time1 = String(formData.get('time1') || '').trim();
  const time2 = String(formData.get('time2') || '').trim();
  const validTimes = [time1, time2].filter(Boolean);

  if (!time1 || !time2) {
    showToast('\u53ef\u8f6c\u503a\u5957\u5229\u72ec\u7acb\u63a8\u9001\u9700\u8981\u4e24\u4e2a\u65f6\u95f4\u70b9', true);
    return;
  }

  state.savingCbArbPush = true;
  renderPushSettings();

  try {
    const payload = await fetchJson(ENDPOINTS.cbArbPushConfig, {
      method: 'POST',
      body: JSON.stringify({
        enabled: config.enabled !== false,
        times: validTimes,
      }),
    });

    state.resources.cbArbPushConfig.status = 'ready';
    state.resources.cbArbPushConfig.data = payload;
    state.resources.cbArbPushConfig.error = null;
    const syncedPayload = await fetchJson(ENDPOINTS.cbArbPushConfig, { method: 'GET' });
    state.resources.cbArbPushConfig.status = 'ready';
    state.resources.cbArbPushConfig.data = syncedPayload;
    state.resources.cbArbPushConfig.error = null;
    showToast('\u53ef\u8f6c\u503a\u5957\u5229\u63a8\u9001\u914d\u7f6e\u5df2\u4fdd\u5b58');
  } catch (error) {
    state.resources.cbArbPushConfig.status = 'error';
    state.resources.cbArbPushConfig.error = error;
    showToast(error.message || '\u53ef\u8f6c\u503a\u5957\u5229\u63a8\u9001\u914d\u7f6e\u4fdd\u5b58\u5931\u8d25', true);
  } finally {
    state.savingCbArbPush = false;
    renderPushSettings();
  }
}

async function saveLofArbPushConfig(form) {
  const config = readLofArbPushConfigViewModel();
  const formData = new FormData(form);
  const time = String(formData.get('time1') || '').trim() || '14:00';

  state.savingLofArbPush = true;
  renderLofArbPanel();
  try {
    const payload = await fetchJson(ENDPOINTS.lofArbPushConfig, {
      method: 'POST',
      body: JSON.stringify({
        enabled: config.enabled !== false,
        times: [time],
      }),
    });
    state.resources.lofArbPushConfig.status = 'ready';
    state.resources.lofArbPushConfig.data = payload;
    state.resources.lofArbPushConfig.error = null;
    showToast('LOF 套利推送时间已保存');
  } catch (error) {
    state.resources.lofArbPushConfig.status = 'error';
    state.resources.lofArbPushConfig.error = error;
    showToast(error.message || 'LOF 套利推送时间保存失败', true);
  } finally {
    state.savingLofArbPush = false;
    renderLofArbPanel();
  }
}

function readMonitorEditorDraft() {
  return state.monitorEditor?.draft || createMonitorDraft();
}

function clearMonitorLookupTimers() {
  ['acquirer', 'target'].forEach((role) => {
    const timer = state.monitorEditor?.lookup?.[role]?.timer;
    if (timer) {
      window.clearTimeout(timer);
      state.monitorEditor.lookup[role].timer = null;
    }
  });
}

function setMonitorEditorDraft(draft, mode = 'create', open = false) {
  clearMonitorLookupTimers();
  state.monitorEditor = createMonitorEditorState(draft, mode, open);
}

function openMonitorCreateMode() {
  setMonitorEditorDraft(createMonitorDraft(), 'create', true);
}

function closeMonitorEditor() {
  setMonitorEditorDraft(createMonitorDraft(), 'create', false);
}

function findMonitorById(monitorId) {
  return readResourceArray('monitor').find((item) => String(item.id) === String(monitorId)) || null;
}

function enterMonitorEditMode(monitorId) {
  const target = findMonitorById(monitorId);
  if (!target) {
    showToast('未找到要编辑的监控项目', true);
    return;
  }
  setMonitorEditorDraft(target, 'edit', true);
}

function readMonitorFormPayload(form) {
  const formData = new FormData(form);
  const currentDraft = readMonitorEditorDraft();
  return {
    id: String(formData.get('id') || '').trim() || currentDraft.id || undefined,
    acquirerName: String(formData.get('acquirerName') || '').trim(),
    targetName: String(formData.get('targetName') || '').trim(),
    stockRatio: String(formData.get('stockRatio') || '').trim(),
    safetyFactor: String(formData.get('safetyFactor') || '').trim(),
    cashDistribution: String(formData.get('cashDistribution') || '').trim(),
    cashDistributionCurrency: String(formData.get('cashDistributionCurrency') || 'CNY').trim(),
    cashOptionPrice: String(formData.get('cashOptionPrice') || '').trim(),
    cashOptionCurrency: String(formData.get('cashOptionCurrency') || 'CNY').trim(),
    name: currentDraft.name || '',
    acquirerCode: currentDraft.acquirerCode || '',
    acquirerMarket: currentDraft.acquirerMarket || 'A',
    acquirerCurrency: currentDraft.acquirerCurrency || 'CNY',
    targetCode: currentDraft.targetCode || '',
    targetMarket: currentDraft.targetMarket || 'A',
    targetCurrency: currentDraft.targetCurrency || 'CNY',
    note: currentDraft.note || '',
  };
}

function getMonitorLookupConfig(role) {
  return role === 'target'
    ? {
      fieldName: 'targetName',
      codeField: 'targetCode',
      marketField: 'targetMarket',
      currencyField: 'targetCurrency',
    }
    : {
      fieldName: 'acquirerName',
      codeField: 'acquirerCode',
      marketField: 'acquirerMarket',
      currencyField: 'acquirerCurrency',
    };
}

function getMonitorLookupSlot(role) {
  return state.monitorEditor?.lookup?.[role] || null;
}

function syncMonitorDraftField(fieldName, fieldValue) {
  if (!fieldName || !state.monitorEditor?.draft) return;
  state.monitorEditor.draft[fieldName] = fieldValue;
}

function normalizeMonitorEntityText(value) {
  return String(value || '').trim().replace(/\s+/g, '').toLowerCase();
}

function isSameMonitorEntityInput(inputText, draftName, draftCode) {
  const current = normalizeMonitorEntityText(inputText);
  if (!current) return false;
  return current === normalizeMonitorEntityText(draftName) || current === normalizeMonitorEntityText(draftCode);
}

function scoreMonitorSearchMatch(item, keyword) {
  const text = normalizeMonitorEntityText(keyword);
  const code = normalizeMonitorEntityText(item?.code);
  const name = normalizeMonitorEntityText(item?.name);
  const pinyin = normalizeMonitorEntityText(item?.pinyin);
  let score = 0;
  if (code && code === text) score += 120;
  if (name && name === text) score += 100;
  if (name && name.includes(text)) score += 60;
  if (text && pinyin === text) score += 40;
  if (text && pinyin.startsWith(text)) score += 20;
  return score;
}

function isExactMonitorSearchMatch(item, keyword) {
  const text = normalizeMonitorEntityText(keyword);
  if (!text) return false;
  return (
    normalizeMonitorEntityText(item?.code) === text ||
    normalizeMonitorEntityText(item?.name) === text
  );
}

function renderMonitorLookupMarkup(role) {
  const slot = getMonitorLookupSlot(role);
  if (!slot) return '';

  const parts = [];
  if (slot.resolved) {
    parts.push(
      `<div class="monitor-lookup-hint monitor-lookup-resolved">已识别：${escapeHtml(slot.resolved.name || '--')} (${escapeHtml(slot.resolved.code || '--')}) · ${escapeHtml(slot.resolved.market || '--')} · ${escapeHtml(slot.resolved.currency || '--')}</div>`
    );
  }
  if (slot.loading) {
    parts.push('<div class="monitor-lookup-hint">正在检索候选股票…</div>');
  } else if (slot.error) {
    parts.push(`<div class="monitor-lookup-hint monitor-lookup-error">${escapeHtml(slot.error)}</div>`);
  }
  if (Array.isArray(slot.items) && slot.items.length) {
    parts.push(`
      <div class="monitor-lookup-list">
        ${slot.items.map((item, index) => `
          <button type="button" class="monitor-lookup-chip" data-monitor-lookup-role="${escapeHtml(role)}" data-monitor-lookup-index="${index}">
            ${escapeHtml(item.name || '--')} (${escapeHtml(item.code || '--')}) · ${escapeHtml(item.market || '--')} · ${escapeHtml(item.currency || '--')}
          </button>
        `).join('')}
      </div>
    `);
  }
  return parts.join('');
}

function updateMonitorLookupUi(role) {
  const container = document.getElementById(`monitor-${role}-lookup`);
  if (!container) return;
  container.innerHTML = renderMonitorLookupMarkup(role);
}

function clearMonitorLookupResults(role) {
  const slot = getMonitorLookupSlot(role);
  if (!slot) return;
  if (slot.timer) {
    window.clearTimeout(slot.timer);
    slot.timer = null;
  }
  slot.loading = false;
  slot.error = '';
  slot.items = [];
}

function clearMonitorResolvedEntity(role) {
  const cfg = getMonitorLookupConfig(role);
  const slot = getMonitorLookupSlot(role);
  if (!state.monitorEditor?.draft || !slot) return;
  slot.resolved = null;
  state.monitorEditor.draft[cfg.codeField] = '';
  state.monitorEditor.draft[cfg.marketField] = '';
  state.monitorEditor.draft[cfg.currencyField] = '';
}

function applyMonitorResolvedEntity(role, candidate) {
  const cfg = getMonitorLookupConfig(role);
  const slot = getMonitorLookupSlot(role);
  if (!candidate || !state.monitorEditor?.draft || !slot) return;
  state.monitorEditor.draft[cfg.fieldName] = candidate.name || candidate.code || '';
  state.monitorEditor.draft[cfg.codeField] = candidate.code || '';
  state.monitorEditor.draft[cfg.marketField] = candidate.market || 'A';
  state.monitorEditor.draft[cfg.currencyField] = candidate.currency || 'CNY';
  slot.resolved = {
    name: candidate.name || candidate.code || '',
    code: candidate.code || '',
    market: candidate.market || 'A',
    currency: candidate.currency || 'CNY',
  };
  slot.loading = false;
  slot.error = '';
  slot.items = [];
  const input = document.querySelector(`#monitor-editor-form [name="${cfg.fieldName}"]`);
  if (input) {
    input.value = candidate.name || candidate.code || '';
  }
  updateMonitorLookupUi(role);
}

function applyMonitorLookupCandidate(role, index) {
  const slot = getMonitorLookupSlot(role);
  if (!slot || !Array.isArray(slot.items)) return;
  const candidate = slot.items[index];
  if (!candidate) return;
  applyMonitorResolvedEntity(role, candidate);
}

async function runMonitorLookup(role, keyword) {
  const slot = getMonitorLookupSlot(role);
  const query = String(keyword || '').trim();
  if (!slot || !query) return;

  const token = (slot.requestToken || 0) + 1;
  slot.requestToken = token;
  slot.loading = true;
  slot.error = '';
  updateMonitorLookupUi(role);

  try {
    const endpoint = `${ENDPOINTS.stockSearch}?keyword=${encodeURIComponent(query)}&limit=6`;
    const payload = await fetchJson(endpoint);
    if (slot.requestToken !== token) return;
    const rows = Array.isArray(payload?.data) ? payload.data : [];
    const ranked = [...rows]
      .sort((a, b) => scoreMonitorSearchMatch(b, query) - scoreMonitorSearchMatch(a, query))
      .slice(0, 5)
      .map((item) => ({
        name: String(item.name || '').trim(),
        code: String(item.code || '').trim(),
        market: String(item.marketType || '').trim().toUpperCase() || 'A',
        currency: String(item.currency || '').trim().toUpperCase() || 'CNY',
      }))
      .filter((item) => item.code);

    slot.loading = false;
    slot.items = ranked;
    slot.error = ranked.length ? '' : '未找到明确候选，请继续输入更准确的名称或代码';

    const exact = ranked.find((item) => isExactMonitorSearchMatch(item, query));
    if (exact) {
      applyMonitorResolvedEntity(role, exact);
      return;
    }

    updateMonitorLookupUi(role);
  } catch (error) {
    if (slot.requestToken !== token) return;
    slot.loading = false;
    slot.items = [];
    slot.error = error?.message || '股票检索失败';
    updateMonitorLookupUi(role);
  }
}

function queueMonitorLookup(role, keyword) {
  const slot = getMonitorLookupSlot(role);
  if (!slot) return;
  const query = String(keyword || '').trim();
  clearMonitorLookupResults(role);

  if (!query) {
    clearMonitorResolvedEntity(role);
    updateMonitorLookupUi(role);
    return;
  }

  if (slot.resolved && !isSameMonitorEntityInput(query, slot.resolved.name, slot.resolved.code)) {
    clearMonitorResolvedEntity(role);
  }

  updateMonitorLookupUi(role);
  if (query.length < 2 && !/^\d{4,}$/.test(query)) return;

  slot.timer = window.setTimeout(() => {
    slot.timer = null;
    void runMonitorLookup(role, query);
  }, MONITOR_LOOKUP_DEBOUNCE_MS);
}

async function resolveMonitorEntity(keyword, draft = {}) {
  const rawKeyword = String(keyword || '').trim();
  if (!rawKeyword) return null;

  if (isSameMonitorEntityInput(rawKeyword, draft.name, draft.code) && draft.code) {
    return {
      name: draft.name || rawKeyword,
      code: draft.code,
      market: draft.market || 'A',
      currency: draft.currency || 'CNY',
    };
  }

  const endpoint = `${ENDPOINTS.stockSearch}?keyword=${encodeURIComponent(rawKeyword)}&limit=8`;
  const payload = await fetchJson(endpoint);
  const rows = Array.isArray(payload?.data) ? payload.data : [];
  if (!rows.length) {
    if (draft.code) {
      return {
        name: draft.name || rawKeyword,
        code: draft.code,
        market: draft.market || 'A',
        currency: draft.currency || 'CNY',
      };
    }
    return null;
  }

  const best = [...rows].sort((a, b) => scoreMonitorSearchMatch(b, rawKeyword) - scoreMonitorSearchMatch(a, rawKeyword))[0];
  if (!best?.code) return null;
  return {
    name: best.name || rawKeyword,
    code: String(best.code || '').trim(),
    market: String(best.marketType || draft.market || 'A').trim().toUpperCase(),
    currency: String(best.currency || draft.currency || 'CNY').trim().toUpperCase(),
  };
}

async function refreshMonitorResource() {
  await loadResource('monitor', ENDPOINTS.monitor, renderEverything, { force: true, background: false });
}

async function saveMonitorFromForm(form) {
  const payload = readMonitorFormPayload(form);
  if (!payload.acquirerName || !payload.targetName) {
    showToast('收购方和目标方都需要填写', true);
    return;
  }

  state.savingMonitor = true;
  renderMonitorPanel();

  try {
    const currentDraft = readMonitorEditorDraft();
    const [acquirerResolved, targetResolved] = await Promise.all([
      resolveMonitorEntity(payload.acquirerName, {
        name: currentDraft.acquirerName,
        code: currentDraft.acquirerCode,
        market: currentDraft.acquirerMarket,
        currency: currentDraft.acquirerCurrency,
      }),
      resolveMonitorEntity(payload.targetName, {
        name: currentDraft.targetName,
        code: currentDraft.targetCode,
        market: currentDraft.targetMarket,
        currency: currentDraft.targetCurrency,
      }),
    ]);

    if (!acquirerResolved || !targetResolved) {
      showToast('无法自动识别收购方或目标方，请输入更准确的公司简称或代码', true);
      return;
    }

    await fetchJson(ENDPOINTS.monitor, {
      method: 'POST',
      body: JSON.stringify({
        ...payload,
        acquirerName: acquirerResolved.name,
        acquirerCode: acquirerResolved.code,
        acquirerMarket: acquirerResolved.market,
        acquirerCurrency: acquirerResolved.currency,
        targetName: targetResolved.name,
        targetCode: targetResolved.code,
        targetMarket: targetResolved.market,
        targetCurrency: targetResolved.currency,
      }),
    });
    await refreshMonitorResource();
    closeMonitorEditor();
    renderMonitorPanel();
    showToast(payload.id ? '监控参数已更新' : '监控项目已新增');
  } catch (error) {
    showToast(error.message || '监控项目保存失败', true);
  } finally {
    state.savingMonitor = false;
    renderMonitorPanel();
  }
}

async function deleteMonitorById(monitorId) {
  if (!monitorId) return;
  if (typeof window !== 'undefined' && !window.confirm('确认删除这个监控项目吗？')) {
    return;
  }

  state.savingMonitor = true;
  renderMonitorPanel();

  try {
    await fetchJson(`${ENDPOINTS.monitor}/${encodeURIComponent(monitorId)}`, { method: 'DELETE' });
    await refreshMonitorResource();
    if (String(readMonitorEditorDraft().id || '') === String(monitorId)) {
      closeMonitorEditor();
    }
    showToast('监控项目已删除');
  } catch (error) {
    showToast(error.message || '监控项目删除失败', true);
  } finally {
    state.savingMonitor = false;
    renderMonitorPanel();
  }
}

function handleSortClick(tableKey, sortKey) {
  const columns = getTableColumns(tableKey);
  const column = columns.find((item) => item.key === sortKey && item.sortable);
  if (!column) return;

  const tableState = state.tables[tableKey];
  if (!tableState) return;
  rememberTableScroll(tableKey);

  const defaultDir = column.defaultDir || 'desc';
  if (tableState.sortKey === sortKey) {
    tableState.sortDir = tableState.sortDir === 'desc' ? 'asc' : 'desc';
  } else {
    tableState.sortKey = sortKey;
    tableState.sortDir = defaultDir;
  }
  tableState.page = 1;

  if (tableKey === 'cbArb' || tableKey === 'cbArbSmallRedemption') renderConvertibleBondPanel();
  if (tableKey === 'ah') renderPremiumPanel('ah');
  if (tableKey === 'ab') renderPremiumPanel('ab');
  if (tableKey === 'lofArb') renderLofArbPanel();
  if (isCbRightsIssueTableKey(tableKey)) renderCbRightsIssuePanel();
  restoreTableScroll(tableKey);
}

function handlePageClick(tableKey, action) {
  const tableState = state.tables[tableKey];
  if (!tableState) return;
  rememberTableScroll(tableKey);

  const totalRows = readTableSourceRows(tableKey).length;
  const totalPages = Math.max(1, Math.ceil(totalRows / tableState.pageSize));

  if (action === 'first') tableState.page = 1;
  if (action === 'prev') tableState.page = Math.max(1, tableState.page - 1);
  if (action === 'next') tableState.page = Math.min(totalPages, tableState.page + 1);
  if (action === 'last') tableState.page = totalPages;

  if (tableKey === 'cbArb' || tableKey === 'cbArbSmallRedemption') renderConvertibleBondPanel();
  if (tableKey === 'ah') renderPremiumPanel('ah');
  if (tableKey === 'ab') renderPremiumPanel('ab');
  if (tableKey === 'lofArb') renderLofArbPanel();
  if (tableKey === 'monitor') renderMonitorPanel();
  if (tableKey === 'dividend') renderDividendPanel();
  if (isCbRightsIssueTableKey(tableKey)) renderCbRightsIssuePanel();
  if (tableKey === 'merger' || tableKey.startsWith('eventArb')) renderMergerPanel();
  restoreTableScroll(tableKey);
}

function readTableSourceRows(tableKey) {
  if (tableKey === 'cbArb') return readCbArbMainRows();
  if (tableKey === 'cbArbSmallRedemption') return readCbArbSmallRedemptionRows();
  if (tableKey === 'lofArb') return readLofArbVisibleRows();
  if (isCbRightsIssueTableKey(tableKey)) {
    const parsed = parseCbRightsIssueTableKey(tableKey);
    return readCbRightsIssueRowsByMarketAndSubview(parsed.marketKey, parsed.subview);
  }
  if (tableKey === 'ah') return readResourceArray('ah');
  if (tableKey === 'ab') return readResourceArray('ab');
  if (tableKey === 'monitor') return readResourceArray('monitor');
  if (tableKey === 'dividend') return readResourceArray('dividend');
  if (tableKey === 'merger' || tableKey === 'eventArbAnnouncement') return readEventArbitrageCategoryRows('announcement_pool');
  if (tableKey === 'eventArbHk') return readEventArbitrageCategoryRows('hk_private');
  if (tableKey === 'eventArbCn') return readEventArbitrageCategoryRows('cn_private');
  if (tableKey === 'eventArbA') return readEventArbitrageCategoryRows('a_event');
  return [];
}

function getTableColumns(tableKey) {
  if (tableKey === 'cbArb') return buildConvertibleColumns();
  if (tableKey === 'cbArbSmallRedemption') return buildCbArbSmallRedemptionColumns();
  if (tableKey === 'lofArb') return buildLofArbColumns();
  if (isCbRightsIssueTableKey(tableKey)) {
    const parsed = parseCbRightsIssueTableKey(tableKey);
    const meta = readCbRightsIssueSubviewMeta(parsed.marketKey, parsed.subview);
    return buildCbRightsIssueColumns({
      includeRecordDate: meta.includeRecordDate,
      includeMarginColumns: meta.includeMarginColumns,
      includePeelColumns: meta.includePeelColumns,
    });
  }
  if (tableKey === 'ah') return buildPremiumColumns('ah');
  if (tableKey === 'ab') return buildPremiumColumns('ab');
  return [];
}

function getPremiumConfig(type) {
  if (type === 'ah') {
    return {
      title: 'AH溢价',
      peerCodeKey: 'hCode',
      peerCodeLabel: 'H股代码',
      peerNameKey: 'hName',
      peerNameLabel: 'H股名称',
      peerMarketPriceKey: 'hPrice',
      peerMarketPriceLabel: 'H股价',
      peerPriceKey: 'hPriceCny',
      peerPriceLabel: 'H股人民币价',
    };
  }

  return {
    title: 'AB溢价',
    peerCodeKey: 'bCode',
    peerCodeLabel: 'B股代码',
    peerNameKey: 'bName',
    peerNameLabel: 'B股名称',
    peerMarketPriceKey: 'bPrice',
    peerMarketPriceLabel: 'B股价',
    peerPriceKey: 'bPriceCny',
    peerPriceLabel: 'B股人民币价',
  };
}

function computePremiumGap(row, peerPriceKey) {
  const peerPrice = toNumber(row?.[peerPriceKey]);
  const aPrice = toNumber(row?.aPrice);
  if (peerPrice === null || aPrice === null) return null;
  return peerPrice - aPrice;
}

function normalizeComparableValue(value, sortType) {
  if (sortType === 'number') return toNumber(value);
  if (sortType === 'date') {
    const normalized = normalizeDateKey(value);
    return normalized ? normalized.replaceAll('-', '') : null;
  }
  const text = String(value ?? '').trim();
  return text ? text : null;
}

function findTableWrap(tableKey) {
  return Array.from(document.querySelectorAll('.table-wrap[data-table-key]'))
    .find((node) => String(node?.dataset?.tableKey || '') === String(tableKey || '')) || null;
}

function rememberTableScroll(tableKey) {
  const wrap = findTableWrap(tableKey);
  if (!wrap) return;
  state.tableScrollOffsets[tableKey] = {
    left: Number(wrap.scrollLeft) || 0,
    top: Number(wrap.scrollTop) || 0,
  };
}

function restoreTableScroll(tableKey) {
  const snapshot = state.tableScrollOffsets[tableKey];
  if (!snapshot) return;
  requestAnimationFrame(() => {
    const wrap = findTableWrap(tableKey);
    if (!wrap) return;
    wrap.scrollLeft = Number(snapshot.left) || 0;
    wrap.scrollTop = Number(snapshot.top) || 0;
  });
}

function compareText(a, b) {
  return String(a).localeCompare(String(b), 'zh-CN');
}

function sortRowsByColumn(rows, column, direction, options = {}) {
  const dir = direction === 'asc' ? 1 : -1;
  return [...rows].sort((a, b) => {
    const rawA = typeof column.sortValue === 'function' ? column.sortValue(a) : a[column.key];
    const rawB = typeof column.sortValue === 'function' ? column.sortValue(b) : b[column.key];
    const valueA = normalizeComparableValue(rawA, column.sortType);
    const valueB = normalizeComparableValue(rawB, column.sortType);

    if (valueA === null && valueB === null) return 0;
    if (valueA === null) return 1;
    if (valueB === null) return -1;

    if (column.sortType === 'number' || column.sortType === 'date') {
      if (valueA === valueB) return 0;
      return valueA > valueB ? dir : -dir;
    }

    return compareText(valueA, valueB) * dir;
  });
}

function getProcessedTableRows(tableKey, rows, columns) {
  const tableState = state.tables[tableKey];
  const filteredRows = applyTableSearch(tableKey, rows);
  const sortColumn = columns.find((item) => item.key === tableState.sortKey && item.sortable);
  const sortedRows = sortColumn
    ? sortRowsByColumn(filteredRows, sortColumn, tableState.sortDir, { tableKey })
    : [...filteredRows];
  const totalRows = sortedRows.length;
  const totalPages = Math.max(1, Math.ceil(totalRows / tableState.pageSize));
  const page = Math.min(Math.max(tableState.page, 1), totalPages);
  tableState.page = page;
  const startIndex = (page - 1) * tableState.pageSize;
  return {
    rows: sortedRows.slice(startIndex, startIndex + tableState.pageSize),
    sortedRows,
    page,
    totalRows,
    rawTotalRows: rows.length,
    totalPages,
    startIndex,
    sortColumn,
  };
}

function renderTableHeader(columns, tableKey, options = {}) {
  const tableState = state.tables[tableKey];
  const includeDetails = Boolean(options.includeDetails);
  const cells = columns
    .map((column) => {
      if (column.key === 'index') return '<th class="col-index">序号</th>';
      const columnClass = escapeHtml([column.columnClassName || '', column.headerClassName || ''].filter(Boolean).join(' '));
      const baseLabel = column.headerHtml || escapeHtml(column.label);
      const label = column.group
        ? `${baseLabel}<span class="th-group-tag">${escapeHtml(column.group)}</span>`
        : baseLabel;

      if (!column.sortable) {
        return `<th${columnClass ? ` class="${columnClass}"` : ''}>${label}</th>`;
      }

      const isActive = tableState.sortKey === column.key;
      const indicator = isActive ? (tableState.sortDir === 'desc' ? '↓' : '↑') : '↕';
      return `
        <th${columnClass ? ` class="${columnClass}"` : ''}>
          <button
            type="button"
            class="sort-head ${isActive ? 'active' : ''}"
            data-table-key="${escapeHtml(tableKey)}"
            data-sort-key="${escapeHtml(column.key)}"
          >
            <span class="sort-indicator">${escapeHtml(indicator)}</span>
            <span class="sort-label">${label}</span>
          </button>
        </th>
      `;
    })
    .join('');

  const detailHead = includeDetails ? '<th aria-label="展开控制"></th>' : '';
  return `<tr>${cells}${detailHead}</tr>`;
}

function renderTableCell(column, row, rowNumber) {
  if (column.key === 'index') {
    return `<td class="mono-text col-index">${escapeHtml(String(rowNumber))}</td>`;
  }

  const value = typeof column.render === 'function' ? column.render(row, rowNumber) : escapeHtml(row[column.key] || '--');
  const semanticClass = typeof column.className === 'function' ? column.className(row, rowNumber) : column.className || '';
  const cellClass = [column.columnClassName || '', semanticClass].filter(Boolean).join(' ');
  return `<td${cellClass ? ` class="${escapeHtml(cellClass)}"` : ''}>${value}</td>`;
}

function resolveRowId(tableKey, row, fallbackIndex) {
  if (tableKey === 'cbArb') return String(row.code || row.bondName || fallbackIndex);
  if (tableKey === 'cbArbSmallRedemption') return String(row.code || row.bondName || fallbackIndex);
  if (tableKey === 'ah') return `${row.aCode || ''}-${row.hCode || ''}-${fallbackIndex}`;
  if (tableKey === 'ab') return `${row.aCode || ''}-${row.bCode || ''}-${fallbackIndex}`;
  if (tableKey === 'lofArb') return String(row.code || row.name || fallbackIndex);
  if (tableKey === 'monitor') return String(row.id || row.name || fallbackIndex);
  if (isCbRightsIssueTableKey(tableKey)) {
    return String(row.stockCode || row.stockName || fallbackIndex);
  }
  if (tableKey === 'merger') return String(row.announcementId || `${row.secCode || ''}-${row.announcementTime || ''}-${fallbackIndex}`);
  if (tableKey === 'eventArbAnnouncement') return String(row.announcementId || `${row.secCode || ''}-${row.announcementTime || ''}-${fallbackIndex}`);
  if (tableKey === 'eventArbHk' || tableKey === 'eventArbCn' || tableKey === 'eventArbA') {
    return String(row.id || `${row.symbol || ''}-${row.detailUrl || fallbackIndex}`);
  }
  return String(fallbackIndex);
}

function renderDetailGrid(items) {
  if (!Array.isArray(items) || !items.length) return '<div class="muted">无补充字段</div>';
  return `
    <div class="detail-grid">
      ${items.map((item) => `
        <div class="detail-item">
          <div class="detail-label">${escapeHtml(item.label || '--')}</div>
          <div class="detail-value">${escapeHtml(item.value || '--')}</div>
        </div>
      `).join('')}
    </div>
  `;
}

function renderPagination(tableKey, model) {
  const totalText = model.rawTotalRows > model.totalRows
    ? `${model.totalRows} / ${model.rawTotalRows} 条`
    : `${model.totalRows} 条`;
  return `
    <div class="pagination-bar">
      <div class="pagination-status">
        第 ${escapeHtml(String(model.page))} / ${escapeHtml(String(model.totalPages))} 页，${escapeHtml(totalText)}
      </div>
      <div class="pagination-buttons">
        <button type="button" class="pagination-button" data-table-key="${escapeHtml(tableKey)}" data-page-action="first" ${model.page <= 1 ? 'disabled' : ''}>首页</button>
        <button type="button" class="pagination-button" data-table-key="${escapeHtml(tableKey)}" data-page-action="prev" ${model.page <= 1 ? 'disabled' : ''}>上一页</button>
        <button type="button" class="pagination-button active" disabled>第 ${escapeHtml(String(model.page))} 页</button>
        <button type="button" class="pagination-button" data-table-key="${escapeHtml(tableKey)}" data-page-action="next" ${model.page >= model.totalPages ? 'disabled' : ''}>下一页</button>
        <button type="button" class="pagination-button" data-table-key="${escapeHtml(tableKey)}" data-page-action="last" ${model.page >= model.totalPages ? 'disabled' : ''}>末页</button>
      </div>
    </div>
  `;
}

function renderPaginatedTable(options) {
  const { tableKey, tableKind, columns, rows, emptyMessage, rowClassName, detailRenderer, detailMode = 'toggle' } = options;
  if (!rows.length) {
    return `
      <div class="empty-state">
        <div>${escapeHtml(emptyMessage)}</div>
      </div>
    `;
  }

  const model = getProcessedTableRows(tableKey, rows, columns);
  const hasDetails = typeof detailRenderer === 'function';
  const inlineDetails = hasDetails && detailMode === 'always';
  const toggleDetails = hasDetails && !inlineDetails;
  const body = model.rows
    .map((row, index) => {
      const rowNumber = model.startIndex + index + 1;
      const rowId = resolveRowId(tableKey, row, rowNumber);
      const className = typeof rowClassName === 'function' ? rowClassName(row) : '';
      const cells = columns.map((column) => renderTableCell(column, row, rowNumber)).join('');
      const detailsCell = toggleDetails
        ? `<td><button type="button" class="expand-button" data-table-key="${escapeHtml(tableKey)}" data-row-id="${escapeHtml(rowId)}">${readExpandedState(tableKey, rowId) ? '收起' : '展开'}</button></td>`
        : '';
      const mainRow = `<tr${className ? ` class="${escapeHtml(className)}"` : ''}>${cells}${detailsCell}</tr>`;
      const shouldRenderDetail = inlineDetails || (toggleDetails && readExpandedState(tableKey, rowId));
      if (!shouldRenderDetail) return mainRow;
      const detailHtml = detailRenderer(row, rowNumber);
      return `${mainRow}<tr class="detail-row"><td colspan="${columns.length + (toggleDetails ? 1 : 0)}">${detailHtml}</td></tr>`;
    })
    .join('');

  return `
    <div class="table-wrap" data-table-key="${escapeHtml(tableKey)}">
      <table data-table-kind="${escapeHtml(tableKind)}">
        <thead>${renderTableHeader(columns, tableKey, { includeDetails: toggleDetails })}</thead>
        <tbody>${body}</tbody>
      </table>
    </div>
    ${renderPagination(tableKey, model)}
  `;
}

function renderSimpleTable(options) {
  const { tableKind, tableKey, columns, rows, emptyMessage, rowClassName, detailRenderer } = options;
  if (!rows.length) {
    return `
      <div class="empty-state">
        <div>${escapeHtml(emptyMessage)}</div>
      </div>
    `;
  }

  const hasDetails = Boolean(tableKey) && typeof detailRenderer === 'function';
  return `
    <div class="table-wrap"${tableKey ? ` data-table-key="${escapeHtml(tableKey)}"` : ''}>
      <table data-table-kind="${escapeHtml(tableKind)}">
        <thead>
          <tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join('')}${hasDetails ? '<th aria-label="展开控制"></th>' : ''}</tr>
        </thead>
        <tbody>
          ${rows
            .map((row, index) => {
              const rowNumber = index + 1;
              const rowId = resolveRowId(tableKey, row, rowNumber);
              const className = typeof rowClassName === 'function' ? rowClassName(row, rowNumber) : '';
              const cells = columns
                .map((column) => {
                  const value = typeof column.render === 'function' ? column.render(row, rowNumber) : escapeHtml(row[column.key] || '--');
                  const cellClass = typeof column.className === 'function' ? column.className(row, rowNumber) : column.className || '';
                  return `<td${cellClass ? ` class="${escapeHtml(cellClass)}"` : ''}>${value}</td>`;
                })
                .join('');
              const detailsCell = hasDetails
                ? `<td><button type="button" class="expand-button" data-table-key="${escapeHtml(tableKey)}" data-row-id="${escapeHtml(rowId)}">${readExpandedState(tableKey, rowId) ? '收起' : '展开'}</button></td>`
                : '';
              const mainRow = `<tr${className ? ` class="${escapeHtml(className)}"` : ''}>${cells}${detailsCell}</tr>`;
              if (!hasDetails || !readExpandedState(tableKey, rowId)) return mainRow;
              const detailHtml = detailRenderer(row, rowNumber);
              return `${mainRow}<tr class="detail-row"><td colspan="${columns.length + 1}">${detailHtml}</td></tr>`;
            })
            .join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderSummaryCard(title, rows, extraClass = "") {
  const body = Array.isArray(rows) && rows.length
    ? renderStackItems(rows)
    : '<div class="muted">暂无数据</div>';
  return `
    <section class="summary-card ${escapeHtml(extraClass)}">
      <h3>${escapeHtml(title)}</h3>
      ${body}
    </section>
  `;
}

function renderCompactCell(primaryHtml, secondaryHtmlList = [], extraClass = '') {
  const secondary = (Array.isArray(secondaryHtmlList) ? secondaryHtmlList : [])
    .filter(Boolean)
    .map((line) => `<div class="table-cell-subtle">${line}</div>`)
    .join('');
  return `
    <div class="table-cell-stack ${escapeHtml(extraClass)}">
      <div class="table-cell-primary">${primaryHtml || '--'}</div>
      ${secondary}
    </div>
  `;
}

function renderTableSearchBar(tableKey) {
  const config = readTableSearchConfig(tableKey);
  if (!config) return '';
  const query = String(state.tables?.[tableKey]?.searchQuery || '');
  if (tableKey === 'cbArb' || tableKey === 'cbArbSmallRedemption') {
    return `
      <div class="table-search-bar">
        <div class="table-search-main">
          <input
            type="text"
            class="table-search-input"
            data-table-search-key="${escapeHtml(tableKey)}"
            value="${escapeHtml(query)}"
            placeholder="${escapeHtml('筛选代码/转债/正股')}"
          />
        </div>
      </div>
    `;
  }
  return `
    <div class="table-search-bar">
      <div class="table-search-main">
        <input
          type="text"
          class="table-search-input"
          data-table-search-key="${escapeHtml(tableKey)}"
          value="${escapeHtml(query)}"
          placeholder="${escapeHtml(config.placeholder)}"
        />
        <button
          type="button"
          class="btn-secondary table-search-clear"
          data-table-search-clear="${escapeHtml(tableKey)}"
          ${query ? '' : 'disabled'}
        >清空</button>
      </div>
      <div class="table-search-hint">${escapeHtml(config.hint)}</div>
    </div>
  `;
}

function buildConvertibleColumns() {
  return [
    {
      key: 'bondName',
      label: '转债名称',
      columnClassName: 'col-name col-bond-sticky col-cb-identity',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => String(row.bondName || row.code || ''),
      render: (row) => renderConvertibleBondIdentity(row),
    },
    {
      key: 'bondQuote',
      label: '转债价',
      columnClassName: 'col-name col-cb-quote',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.price),
      render: (row) => renderCompactCell(
        formatNumber(row.price, 2),
        [statusText(row.changePercent, 2)],
        statusClass(row.changePercent)
      ),
    },
    {
      key: 'stockIdentity',
      label: '正股',
      columnClassName: 'col-name col-cb-identity',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => String(row.stockName || row.stockCode || ''),
      render: (row) => renderCompactCell(
        escapeHtml(row.stockName || '--'),
        [`<span class="mono-text">${escapeHtml(row.stockCode || '--')}</span>`]
      ),
    },
    {
      key: 'stockQuote',
      label: '正股价',
      columnClassName: 'col-name col-cb-quote',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.stockPrice),
      render: (row) => renderCompactCell(
        formatNumber(row.stockPrice, 2),
        [statusText(row.stockChangePercent, 2)],
        statusClass(row.stockChangePercent)
      ),
    },
    {
      key: 'stockAvgTurnoverAmount20Yi',
      label: '正股成交',
      columnClassName: 'col-name col-cb-volume',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.stockAvgTurnoverAmount20Yi),
      render: (row) => renderCompactCell(
        `${formatNumber(row.stockAvgTurnoverAmount20Yi, 2)}亿`,
        [`5日 ${formatNumber(row.stockAvgTurnoverAmount5Yi, 2)}亿`]
      ),
    },
    {
      key: 'convertPrice',
      label: '转股价',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.convertPrice),
      render: (row) => formatNumber(row.convertPrice, 2),
    },
    {
      key: 'convertValue',
      label: '转股价值',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.convertValue),
      render: (row) => formatNumber(row.convertValue, 2),
    },
    {
      key: 'premiumRate',
      label: '转股溢价',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.premiumRate),
      className: (row) => statusClass(row.premiumRate),
      render: (row) => renderCompactCell(
        formatPercent(row.premiumRate, 2),
        [`溢价额 ${formatSignedNumber(computeConvertiblePremiumAmount(row), 2)}`],
        statusClass(row.premiumRate)
      ),
    },
    {
      key: 'bondToStockMarketValueRatio',
      label: '转债市值比',
      headerHtml: '转债<br>市值比',
      columnClassName: 'col-name col-cb-factor',
      sortable: true,
      sortType: 'number',
      defaultDir: 'asc',
      sortValue: (row) => toNumber(row.bondToStockMarketValueRatio),
      render: (row) => renderCompactCell(
        formatRatioPercent(row.bondToStockMarketValueRatio, 3),
        [`剩余规模 ${formatNumber(row.remainingSizeYi, 2)}亿 / 正股流通市值 ${formatNumber(row.stockMarketValueYi, 2)}亿`]
      ),
    },
    {
      key: 'discountAtrRatio',
      label: '折价ATR比',
      headerHtml: '折价<br>ATR比',
      columnClassName: 'col-name col-cb-factor',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.discountAtrRatio),
      render: (row) => renderCompactCell(
        formatRatioPercent(row.discountAtrRatio, 3),
        [`ATR% ${formatPercent(row.stockAtr20Pct, 2)}`]
      ),
    },
    {
      key: 'boardType',
      label: '市场',
      columnClassName: 'col-name col-cb-market',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => String(readConvertibleBoardLabel(row) || ''),
      render: (row) => escapeHtml(readConvertibleBoardLabel(row)),
    },
    { key: 'doubleLow', label: '双低', columnClassName: 'col-num col-cb-num', sortable: true, sortType: 'number', defaultDir: 'asc', sortValue: (row) => toNumber(row.doubleLow), render: (row) => formatNumber(row.doubleLow, 2) },
    {
      key: 'pureBondPremiumRate',
      label: '纯债溢价',
      headerHtml: '纯债<br>溢价',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => computePureBondPremiumRate(row),
      className: (row) => statusClass(computePureBondPremiumRate(row)),
      render: (row) => renderCompactCell(
        formatPercent(computePureBondPremiumRate(row), 2),
        [`纯债值 ${formatNumber(readPureBondBase(row), 2)}`],
        statusClass(computePureBondPremiumRate(row))
      ),
    },
    {
      key: 'theoreticalPremiumRate',
      label: '理论溢价',
      headerHtml: '理论<br>溢价',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.theoreticalPremiumRate),
      className: (row) => statusClass(row.theoreticalPremiumRate),
      render: (row) => renderCompactCell(
        formatPercent(row.theoreticalPremiumRate, 2),
        [`溢价额 ${formatSignedNumber(computeConvertibleTheoreticalPremiumAmount(row), 2)}`],
        statusClass(row.theoreticalPremiumRate)
      ),
    },
    {
      key: 'theoreticalOptionValue',
      label: '理论期权价值',
      headerHtml: '理论期<br>权价值',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => computeOptionTheoreticalValue(row),
      render: (row) => formatNumber(computeOptionTheoreticalValue(row), 2),
    },
    {
      key: 'implicitOptionValue',
      label: '隐含期权价值',
      headerHtml: '隐含期<br>权价值',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => computeImplicitOptionValue(row),
      render: (row) => formatNumber(computeImplicitOptionValue(row), 2),
    },
    {
      key: 'optionValueGap',
      label: '期权折价率',
      headerHtml: '期权<br>折价率',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => computeOptionDiscountRate(row),
      className: (row) => statusClass(computeOptionDiscountRate(row)),
      render: (row) => renderCompactCell(
        formatPercent(computeOptionDiscountRate(row), 2),
        [`价差 ${formatSignedNumber(computeOptionValueGap(row), 2)}`],
        statusClass(computeOptionDiscountRate(row))
      ),
    },
    {
      key: 'remainingSizeYi',
      label: '剩余规模',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.remainingSizeYi),
      render: (row) => formatNumber(row.remainingSizeYi, 2),
    },
    {
      key: 'volatility250',
      label: '250日波动率',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.volatility250 ?? row.volatility60 ?? row.annualizedVolatility),
      render: (row) => formatRatioPercent(row.volatility250 ?? row.volatility60 ?? row.annualizedVolatility, 2),
    },
    {
      key: 'remainingYears',
      label: '剩余期限',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'asc',
      sortValue: (row) => toNumber(row.remainingYears),
      render: (row) => formatRemainingTerm(row.remainingYears),
    },
  ];
}

function buildCbArbSmallRedemptionColumns() {
  return [
    {
      key: 'bondName',
      label: '\u53ef\u8f6c\u503a\u4ee3\u7801&\u540d\u79f0',
      columnClassName: 'col-name col-bond-sticky col-cb-identity',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => String(row.bondName || row.code || ''),
      render: (row) => renderConvertibleBondIdentity(row),
    },
    {
      key: 'bondQuote',
      label: '\u53ef\u8f6c\u503a\u4ef7\u683c&\u6da8\u8dcc\u5e45',
      columnClassName: 'col-name col-cb-quote',
      sortable: true,
      sortType: 'number',
      defaultDir: 'asc',
      sortValue: (row) => toNumber(row.price),
      render: (row) => renderCompactCell(formatNumber(row.price, 2), [statusText(row.changePercent, 2)], statusClass(row.changePercent)),
    },
    {
      key: 'stockIdentity',
      label: '\u6b63\u80a1\u540d\u79f0&\u4ee3\u7801',
      columnClassName: 'col-name col-cb-identity',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => String(row.stockName || row.stockCode || ''),
      render: (row) => renderCompactCell(escapeHtml(row.stockName || '--'), [`<span class="mono-text">${escapeHtml(row.stockCode || '--')}</span>`]),
    },
    {
      key: 'stockQuote',
      label: '\u6b63\u80a1\u4ef7\u683c&\u6da8\u8dcc\u5e45',
      columnClassName: 'col-name col-cb-quote',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.stockPrice),
      render: (row) => renderCompactCell(formatNumber(row.stockPrice, 2), [statusText(row.stockChangePercent, 2)], statusClass(row.stockChangePercent)),
    },
    {
      key: 'holderCount',
      label: '\u6301\u6709\u4eba\u6570',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbHolderCount(row),
      render: (row) => formatInt(readCbArbHolderCount(row)),
    },
    {
      key: 'remainingSizeYi',
      label: '\u5269\u4f59\u89c4\u6a21',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionRemainingSizeYi(row),
      render: (row) => formatYiValue(readCbArbSmallRedemptionRemainingSizeYi(row), 2),
    },
    {
      key: 'redemptionAmount',
      label: '\u521a\u5151\u91d1\u989d',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionAmount(row),
      render: (row) => formatCurrencyCompact(readCbArbSmallRedemptionAmount(row), 2),
    },
    {
      key: 'redemptionYield',
      label: '\u521a\u5151\u6536\u76ca\u7387',
      headerClassName: 'cb-arb-highlight-head',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionYield(row),
      className: (row) => statusClass(readCbArbSmallRedemptionYield(row)),
      render: (row) => formatSmallRedemptionPercent(readCbArbSmallRedemptionYield(row), 2),
    },
    {
      key: 'expectedDurationYears',
      label: '\u9884\u671f\u8017\u65f6',
      headerClassName: 'cb-arb-highlight-head',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'asc',
      sortValue: (row) => readCbArbSmallRedemptionExpectedDurationYears(row),
      render: (row) => renderCbArbExpectedDurationCell(row),
    },
    {
      key: 'annualizedYield',
      label: '\u521a\u5151\u5e74\u5316',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionAnnualizedYield(row),
      className: (row) => statusClass(readCbArbSmallRedemptionAnnualizedYield(row)),
      render: (row) => formatSmallRedemptionPercent(readCbArbSmallRedemptionAnnualizedYield(row), 2),
    },
    {
      key: 'redemptionTotal',
      label: '\u521a\u5151\u603b\u989d',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionTotal(row),
      render: (row) => formatCurrencyCompact(readCbArbSmallRedemptionTotal(row), 2),
    },
    {
      key: 'liabilityExposureYi',
      label: '\u8d1f\u503a\u655e\u53e3',
      columnClassName: 'col-name col-cb-factor',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbLiabilityExposureYi(row),
      render: (row) => renderCbArbLiabilityExposureCell(row),
    },
    {
      key: 'netAssetYi',
      label: '\u51c0\u8d44\u4ea7',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbNetAssetYi(row),
      render: (row) => formatYiValue(readCbArbNetAssetYi(row), 2),
    },
    {
      key: 'optionValue',
      label: '\u671f\u6743\u4ef7\u503c',
      columnClassName: 'col-num col-cb-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionOptionValue(row),
      render: (row) => formatNumber(readCbArbSmallRedemptionOptionValue(row), 2),
    },
    {
      key: 'optionAnnualizedYield',
      label: '\u671f\u6743\u5e74\u5316',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionOptionAnnualizedYield(row),
      className: (row) => statusClass(readCbArbSmallRedemptionOptionAnnualizedYield(row)),
      render: (row) => formatSmallRedemptionPercent(readCbArbSmallRedemptionOptionAnnualizedYield(row), 2),
    },
    {
      key: 'totalAnnualizedYield',
      label: '\u603b\u5e74\u5316\u6536\u76ca\u7387',
      columnClassName: 'col-percent col-cb-percent',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => readCbArbSmallRedemptionTotalAnnualizedYield(row),
      className: (row) => statusClass(readCbArbSmallRedemptionTotalAnnualizedYield(row)),
      render: (row) => formatSmallRedemptionPercent(readCbArbSmallRedemptionTotalAnnualizedYield(row), 2),
    },
  ];
}

function buildPremiumColumns(type) {
  const config = getPremiumConfig(type);
  return [
    { key: 'index', label: '序号' },
    { key: 'aCode', label: 'A股代码', columnClassName: 'col-code', sortable: true, sortType: 'text', defaultDir: 'asc', sortValue: (row) => String(row.aCode || ''), render: (row) => `<span class="mono-text">${escapeHtml(row.aCode || '--')}</span>` },
    { key: 'aName', label: 'A股名称', columnClassName: 'col-name', sortable: true, sortType: 'text', defaultDir: 'asc', sortValue: (row) => String(row.aName || ''), render: (row) => escapeHtml(row.aName || '--') },
    { key: config.peerCodeKey, label: config.peerCodeKey === 'hCode' ? 'H股代码' : 'B股代码', columnClassName: 'col-code', sortable: true, sortType: 'text', defaultDir: 'asc', sortValue: (row) => String(row[config.peerCodeKey] || ''), render: (row) => `<span class="mono-text">${escapeHtml(row[config.peerCodeKey] || '--')}</span>` },
    { key: config.peerNameKey, label: config.peerNameKey === 'hName' ? 'H股名称' : 'B股名称', columnClassName: 'col-name', sortable: true, sortType: 'text', defaultDir: 'asc', sortValue: (row) => String(row[config.peerNameKey] || ''), render: (row) => escapeHtml(row[config.peerNameKey] || '--') },
    { key: 'aPrice', label: 'A股现价', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.aPrice), render: (row) => formatNumber(row.aPrice, 2) },
    {
      key: config.peerMarketPriceKey,
      label: config.peerMarketPriceKey === 'hPrice' ? 'H股现价' : 'B股现价',
      columnClassName: 'col-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row[config.peerMarketPriceKey]),
      render: (row) => formatNumber(row[config.peerMarketPriceKey], 2),
    },
    { key: config.peerPriceKey, label: config.peerPriceKey === 'hPriceCny' ? 'H股人民币价' : 'B股人民币价', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row[config.peerPriceKey]), render: (row) => formatNumber(row[config.peerPriceKey], 2) },
    {
      key: 'priceGap',
      label: '价差',
      columnClassName: 'col-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => computePremiumGap(row, config.peerPriceKey),
      className: (row) => statusClass(computePremiumGap(row, config.peerPriceKey)),
      render: (row) => formatSignedNumber(computePremiumGap(row, config.peerPriceKey), 2),
    },
    { key: 'premium', label: '溢价率', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.premium), className: (row) => statusClass(row.premium), render: (row) => formatPercent(row.premium, 2) },
    { key: 'percentile', label: '近三年分位', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.percentile), render: (row) => formatPercent(row.percentile, 2) },
    {
      key: 'historyCount',
      label: '样本数',
      columnClassName: 'col-num',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.historyCount),
      render: (row) => formatInt(row.historyCount),
    },
    { key: 'historyRange', label: '样本区间', columnClassName: 'col-range', sortable: false, render: (row) => `<span class="mono-text">${escapeHtml(formatHistoryRange(row))}</span>` },
  ];
}

function renderActivePanel() {
  if (state.activeTab === 'cb-arb') return renderConvertibleBondPanel();
  if (state.activeTab === 'ah') return renderPremiumPanel('ah');
  if (state.activeTab === 'ab') return renderPremiumPanel('ab');
  if (state.activeTab === 'lof-arb') return renderLofArbPanel();
  if (state.activeTab === 'monitor') return renderMonitorPanel();
  if (state.activeTab === 'dividend') return renderDividendPanel();
  if (state.activeTab === 'merger') return renderMergerPanel();
  if (state.activeTab === 'cb-rights-issue') return renderCbRightsIssuePanel();
}

function renderConvertibleBondPanel() {
  const panel = dom.tabPanels["cb-arb"];
  const resource = state.resources.cbArb;
  if (!panel) return;

  if (resource.status === "loading" || resource.status === "idle") {
    panel.innerHTML = moduleLoading("转债套利正在拉取真实数据");
    return;
  }

  if (resource.status === "error") {
    panel.innerHTML = moduleError("转债套利加载失败", resource.error?.message);
    return;
  }

  const rows = readCbArbMainRows();
  const smallRedemptionRows = readCbArbSmallRedemptionRows();
  if (!rows.length && !smallRedemptionRows.length) {
    panel.innerHTML = moduleEmpty("转债套利暂时没有返回数据");
    return;
  }

  const cbSummary = readCbArbSummary();
  const topDoubleLowItems = Array.isArray(cbSummary.topDoubleLow) ? cbSummary.topDoubleLow : [];
  const topTheoryItems = Array.isArray(cbSummary.topTheoreticalPremiumRate) ? cbSummary.topTheoreticalPremiumRate : [];
  const premiumMonitorSummary = readCbArbPremiumMonitorSummary();
  const premiumMonitorItems = Array.isArray(premiumMonitorSummary.items) ? premiumMonitorSummary.items : [];

  const summaryCards = [
    renderSummaryCard(
      "双低前3",
      topDoubleLowItems.map((row) => ({
        title: `${row.bondName || "--"} ${row.code || ""}`.trim(),
        subtitle: `现价 ${formatNumber(row.price, 2)} / 溢价率 ${formatPercent(row.premiumRate, 2)} / 正股 ${row.stockName || "--"}`,
        value: `双低值 ${formatNumber(row.doubleLow, 2)}`,
      })),
      "compact-card"
    ),
    renderSummaryCard(
      "理论溢价前3",
      topTheoryItems.map((row) => ({
        title: `${row.bondName || "--"} ${row.code || ""}`.trim(),
        subtitle: `现价 ${formatNumber(row.price, 2)} / 理论价 ${formatNumber(row.theoreticalPrice, 2)}`,
        value: `理论溢价率 ${formatPercent(row.theoreticalPremiumRate, 2)}`,
        valueClass: statusClass(row.theoreticalPremiumRate),
      })),
      "compact-card"
    ),
    renderSummaryCard(
      "低溢价监控",
      premiumMonitorItems.length
        ? premiumMonitorItems.map((row) => ({
          title: `${row.bondName || "--"}`.trim(),
          subtitle: `转债市值比 ${formatRatioPercent(row.bondToStockMarketValueRatio, 3)} / 折价ATR比 ${formatRatioPercent(row.discountAtrRatio, 3)} / 转债代码 ${row.code || "--"}`,
          value: formatPercent(row.premiumRate, 2),
          valueClass: statusClass(row.premiumRate),
        }))
        : [{ title: '暂无监控名单', subtitle: '', value: '--', valueClass: '' }],
      "compact-card"
    ),
  ].join("");

  const activeSubview = ensureCbArbSubview();
  const activeContent = activeSubview === 'small-redemption'
    ? renderCbArbSmallRedemptionView(smallRedemptionRows)
    : `
      <div class="summary-grid summary-grid-three">${summaryCards}</div>
      <div class="list-card">
        <h3>鍒楄〃</h3>
        ${renderTableSearchBar('cbArb')}
        <div data-table-host="cbArb">
          ${renderPaginatedTable({
            tableKey: "cbArb",
            tableKind: "convertible",
            columns: buildConvertibleColumns(),
            rows,
            emptyMessage: "转债套利暂无数据",
          })}
        </div>
        <div class="slim-note">${buildConvertibleExplainText(rows)}</div>
      </div>
    `;

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">转债套利</div>
        </div>
        <div class="panel-meta">
          <span>总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime("cbArb")))}</span>
          <span>${escapeHtml(readFreshnessText('cbArb'))}</span>
        </div>
      </div>
      <div class="summary-grid summary-grid-three">${summaryCards}</div>
      <div class="list-card">
        <h3>列表</h3>
        ${renderTableSearchBar('cbArb')}
        <div data-table-host="cbArb">
          ${renderPaginatedTable({
            tableKey: "cbArb",
            tableKind: "convertible",
            columns: buildConvertibleColumns(),
            rows,
            emptyMessage: "转债套利暂时没有返回数据",
          })}
        </div>
        <div class="slim-note">${buildConvertibleExplainText(rows)}</div>
      </div>
    </div>
  `;
  const shell = panel.querySelector('.module-shell');
  if (shell) {
    shell.innerHTML = `
      <div class="module-toolbar">
        <div>
          <div class="tab-title">\u53ef\u8f6c\u503a\u5957\u5229</div>
        </div>
        <div class="panel-meta">
          <span>\u4e3b\u9875\u6837\u672c ${escapeHtml(formatInt(rows.length))}</span>
          <span>\u5c0f\u989d\u521a\u5151 ${escapeHtml(formatInt(smallRedemptionRows.length))}</span>
          <span>\u6700\u8fd1\u66f4\u65b0 ${escapeHtml(formatDate(readUpdateTime("cbArb")))}</span>
          <span>${escapeHtml(readFreshnessText('cbArb'))}</span>
        </div>
      </div>
      ${renderCbArbSubtabs(activeSubview)}
      <div class="cb-arb-subtab-shell">${activeContent}</div>
    `;
  }
}

function renderCbArbSubtabs(activeSubview = ensureCbArbSubview()) {
  const tabs = [
    { key: 'home', label: '\u4e3b\u9875' },
    { key: 'small-redemption', label: '\u5c0f\u989d\u521a\u5151' },
  ];
  return `
    <div class="subtab-nav">
      ${tabs.map((tab) => `
        <button
          type="button"
          class="subtab-button ${activeSubview === tab.key ? 'active' : ''}"
          data-cb-arb-subtab="${escapeHtml(tab.key)}"
        >${escapeHtml(tab.label)}</button>
      `).join('')}
    </div>
  `;
}

function renderCbArbSmallRedemptionView(rows) {
  const summary = readCbArbSmallRedemptionSummary();
  const meta = readCbArbSmallRedemptionMeta();
  const reportPeriod = meta.reportPeriod || meta.report_period || summary.reportPeriod || '--';
  const reportSourceUrl = meta.reportSourceUrl || meta.report_source_url || summary.reportSourceUrl || '';
  const holderFallback = Boolean(meta.holderCountFallbackUsed ?? meta.holder_count_fallback_used);
  const priceThreshold = readFirstDefinedValue(summary, ['priceThreshold', 'price_threshold']) ?? 100;
  const holderCountKnown = rows.filter((row) => readCbArbHolderCount(row) !== null).length;

  return `
    <div class="list-card">
      <div class="module-toolbar">
        <div>
          <h3>\u5c0f\u989d\u521a\u5151</h3>
          <div class="section-note">\u5165\u9009\u6807\u51c6\uff1a\u53ef\u8f6c\u503a\u4ef7\u683c &lt; ${escapeHtml(formatNumber(priceThreshold, 2))}\uff1b\u7f3a\u5931\u5b57\u6bb5\u4fdd\u7559\u6837\u672c\u5e76\u663e\u793a --\u3002</div>
        </div>
        <div class="panel-meta">
          <span>\u6837\u672c ${escapeHtml(formatInt(rows.length))}</span>
          <span>\u6709\u6301\u6709\u4eba\u6570 ${escapeHtml(formatInt(holderCountKnown))}</span>
          <span>\u62a5\u544a\u671f ${escapeHtml(reportPeriod)}</span>
          <span>${holderFallback ? '\u6301\u6709\u4eba\u6570\u5df2\u56de\u9000' : '\u4f18\u5148\u6700\u65b0\u62a5\u544a'}</span>
          ${reportSourceUrl ? `<span>\u62a5\u544a ${buildAnchor(reportSourceUrl, '\u6253\u5f00')}</span>` : ''}
        </div>
      </div>
      ${renderTableSearchBar('cbArbSmallRedemption')}
      <div data-table-host="cbArbSmallRedemption">
        ${renderPaginatedTable({
          tableKey: 'cbArbSmallRedemption',
          tableKind: 'convertible',
          columns: buildCbArbSmallRedemptionColumns(),
          rows,
          emptyMessage: '\u5f53\u524d\u6ca1\u6709\u7b26\u5408\u6761\u4ef6\u7684\u5c0f\u989d\u521a\u5151\u6807\u7684',
        })}
      </div>
    </div>
  `;
}

function buildConvertibleExplainText(rows) {
  const baseText = '250日波动率基于历史K线库真实后复权收盘价、按最近250个对数收益率样本年化计算；理论价值相关字段继续作为参考指标。';
  const exampleRow = Array.isArray(rows)
    ? rows.find((row) => {
      const bondBase = readPureBondBase(row);
      return (
        toNumber(row?.theoreticalPrice) !== null &&
        toNumber(row?.callOptionValue) !== null &&
        bondBase !== null &&
        toNumber(row?.volatility250 ?? row?.volatility60 ?? row?.annualizedVolatility) !== null
      );
    })
    : null;

  if (!exampleRow) return escapeHtml(baseText);

  const bondBase = readPureBondBase(exampleRow);
  const callValue = toNumber(exampleRow.callOptionValue);
  const putValue = toNumber(exampleRow.putOptionValue);
  const longCallValue = toNumber(exampleRow.longCallOptionValue);
  const shortCallValue = toNumber(exampleRow.shortCallOptionValue);
  const theoreticalPrice = toNumber(exampleRow.theoreticalPrice);
  const pricingFormula = String(exampleRow.pricingFormula || '').trim();
  const formulaText = pricingFormula === 'bond+callspread'
    ? `${formatNumber(bondBase, 2)} + max(${formatNumber(longCallValue, 2)} - ${formatNumber(shortCallValue, 2)}, 0) = ${formatNumber(theoreticalPrice, 2)}`
    : pricingFormula === 'bond+call-put'
      ? `${formatNumber(bondBase, 2)} + ${formatNumber(callValue, 2)} - ${formatNumber(putValue ?? 0, 2)} = ${formatNumber(theoreticalPrice, 2)}`
      : `${formatNumber(bondBase, 2)} + ${formatNumber(callValue, 2)} = ${formatNumber(theoreticalPrice, 2)}`;
  const detailText = [
    `例：${exampleRow.bondName || '--'} ${exampleRow.code || ''}`.trim(),
    `正股 ${exampleRow.stockName || '--'} ${exampleRow.stockCode || ''}`.trim(),
    `现价 ${formatNumber(exampleRow.stockPrice, 2)}`,
    `多头行权价 ${formatNumber(exampleRow.callStrike ?? exampleRow.convertPrice, 2)}`,
    `转股价 ${formatNumber(exampleRow.convertPrice, 2)}`,
    pricingFormula === 'bond+callspread' ? `强赎价 ${formatNumber(exampleRow.redeemTriggerPrice ?? exampleRow.redeemCallStrike, 2)}` : '',
    `250日波动率 ${formatRatioPercent(exampleRow.volatility250 ?? exampleRow.volatility60 ?? exampleRow.annualizedVolatility, 2)}`,
    `债底 ${formatNumber(bondBase, 2)}`,
    pricingFormula === 'bond+callspread'
      ? `理论价按“债底 + 净看涨价差价值”口径参考计算；净看涨价差 = call(max(转股价, 债底折算行权价)) - call(强赎价)：${formulaText}`
      : pricingFormula === 'bond+call-put'
        ? `理论价按“债底 + 看涨期权 - 看跌期权”口径参考计算：${formulaText}`
        : `理论价按“债底 + 看涨期权”口径参考计算：${formulaText}`,
  ].join('；');

  return escapeHtml(`${baseText} ${detailText}。`);
}

function buildLofArbPushStateText() {
  const config = readLofArbPushConfigViewModel();
  const deliveryStatus = config?.deliveryStatus && typeof config.deliveryStatus === 'object' ? config.deliveryStatus : {};
  const times = Array.isArray(config?.times) ? config.times.filter(Boolean) : [];
  const parts = [
    times.length ? `时间 ${times.join(' / ')}` : '时间 --',
    deliveryStatus.webhookConfigured ? 'Webhook已配置' : 'Webhook未配置',
    deliveryStatus.schedulerEnabled === false
      ? (deliveryStatus.schedulerDisabledReason === 'loopback_public_base_url' ? '本地运行已禁用服务端推送调度' : '服务端调度已关闭')
      : '',
    deliveryStatus.lastSuccessAt ? `定时成功 ${formatDate(deliveryStatus.lastSuccessAt)}` : '',
    deliveryStatus.lastError ? `定时失败 ${String(deliveryStatus.lastError).slice(0, 60)}` : '',
  ].filter(Boolean);
  return parts.join(' / ');
}

function renderLofArbPushCard() {
  const config = readLofArbPushConfigViewModel();
  const times = Array.isArray(config?.times) ? config.times : ['14:00'];

  return `
    <div class="list-card">
      <div class="module-toolbar">
        <div>
          <h3>独立推送</h3>
          <div class="section-note">仅保留交易日下午 14:00 一次全量推送，已取消新入池、买入、卖出等即时推送。</div>
        </div>
        <div class="panel-meta">
          <span>${escapeHtml(buildLofArbPushStateText() || '正在读取推送状态')}</span>
        </div>
      </div>
      <div class="push-form">
        <div class="input-group">
          <label>固定推送时间</label>
          <input type="time" value="${escapeHtml(times[0] || '14:00')}" disabled />
        </div>
        <div class="section-note">
          当前策略固定为：交易日 14:00 推送全部监控池结果；空监控池不推送。
        </div>
      </div>
    </div>
  `;
}

function buildLofArbColumns() {
  return [
    { key: 'index', label: '序号' },
    {
      key: 'identity',
      label: '名称/代码',
      columnClassName: 'col-lof-identity',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row.name || ''} ${row.code || ''}`.trim(),
      render: (row) => renderCompactCell(
        escapeHtml(row.name || '--'),
        [
          `<span class="mono-text">${escapeHtml(row.code || '--')}</span>`,
          `${escapeHtml(row.marketLabel || '--')} / ${escapeHtml(row.timeNote || '--')}`,
        ],
      ),
    },
    {
      key: 'quote',
      label: '现价/涨幅',
      columnClassName: 'col-lof-quote',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.price),
      render: (row) => renderCompactCell(
        escapeHtml(formatNumber(row.price, 3)),
        [
          `<span class="${escapeHtml(statusClass(row.changeRate) || '')}">${escapeHtml(formatPercent(row.changeRate, 2))}</span>`,
        ],
      ),
    },
    {
      key: 'turnoverWan',
      label: '成交额/份额',
      columnClassName: 'col-lof-volume',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.turnoverWan),
      render: (row) => renderCompactCell(
        `${escapeHtml(formatNumber(row.turnoverWan, 2))}万`,
        [
          `份额 ${escapeHtml(formatNumber(row.shareAmountWan, 2))}万 / 新增 ${escapeHtml(formatNumber(row.shareAmountIncreaseWan, 2))}`,
        ],
      ),
    },
    {
      key: 'navDate',
      label: '净值/日期',
      columnClassName: 'col-lof-nav',
      sortable: true,
      sortType: 'date',
      defaultDir: 'desc',
      sortValue: (row) => normalizeDateKey(row.navDate),
      render: (row) => renderCompactCell(
        escapeHtml(formatNumber(row.nav, 4)),
        [
          escapeHtml(formatDateOnly(row.navDate)),
        ],
      ),
    },
    {
      key: 'indexInfo',
      label: '相关指数/人民币涨幅',
      columnClassName: 'col-lof-index',
      sortable: true,
      sortType: 'number',
      defaultDir: 'desc',
      sortValue: (row) => toNumber(row.navAlignedIndexChangeRate),
      render: (row) => renderCompactCell(
        escapeHtml(row.indexName || '--'),
        [
          `<span class="${escapeHtml(statusClass(row.navAlignedIndexChangeRate) || '')}">${escapeHtml(formatPercent(row.navAlignedIndexChangeRate, 2))}</span>`,
        ],
      ),
    },
    {
      key: 'applyInfo',
      label: '申购',
      columnClassName: 'col-lof-fee',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row.applyStatusText || row.applyStatus || ''} ${row.applyFee || ''}`.trim(),
      render: (row) => renderCompactCell(
        escapeHtml(row.applyStatusText || row.applyStatus || '--'),
        [
          `申购费 ${escapeHtml(formatPercent(row.applyFee, 2))}`,
        ],
      ),
    },
    {
      key: 'redeemInfo',
      label: '赎回/托管',
      columnClassName: 'col-lof-fee',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row.redeemStatus || ''} ${row.redeemFee || ''} ${row.custodianFee || ''}`.trim(),
      render: (row) => renderCompactCell(
        escapeHtml(row.redeemStatus || '--'),
        [
          `赎回费 ${escapeHtml(formatPercent(row.redeemFee, 2))}`,
          `托管费 ${escapeHtml(formatPercent(row.custodianFee, 2))}`,
        ],
      ),
    },
    { key: 'iopv', label: 'IOPV', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.iopv), render: (row) => formatNumber(row.iopv, 4) },
    { key: 'premiumRate', label: '溢价', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.premiumRate), className: (row) => statusClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate, 2) },
  ];
}

function renderLofMonitorSummaryCard(title, rows, emptyText, extraClass = '') {
  const visibleRows = Array.isArray(rows) ? rows.slice(0, 8) : [];
  const body = visibleRows.length
    ? `
      <div class="stack-list lof-monitor-list">
        ${visibleRows.map((row) => `
          <div class="stack-row lof-monitor-row">
            <div class="item-main">
              <div class="item-title">
                ${escapeHtml(row.name || '--')}
                <span class="item-subtitle mono-text">${escapeHtml(row.code || '--')}</span>
              </div>
              <div class="lof-monitor-meta">
                <span>${escapeHtml(row.marketLabel || '--')}</span>
                <span>${escapeHtml(row.groupLabel || '--')}</span>
                <span>申购 ${escapeHtml(row.applyStatusText || row.applyStatus || '--')}</span>
                <span>现价 ${escapeHtml(formatNumber(row.price, 3))}</span>
                <span>涨幅 ${escapeHtml(formatPercent(row.changeRate, 2))}</span>
                <span>成交额 ${escapeHtml(formatNumber(row.turnoverWan, 2))}万</span>
                <span>申购费 ${escapeHtml(formatPercent(row.applyFee, 2))}</span>
                <span>赎回费 ${escapeHtml(formatPercent(row.redeemFee, 2))}</span>
                <span>${escapeHtml(row.timeNote || '--')}</span>
              </div>
            </div>
            <div class="item-value ${escapeHtml(statusClass(row.premiumRate) || '')}">${escapeHtml(formatPercent(row.premiumRate, 2))}</div>
          </div>
        `).join('')}
      </div>
    `
    : `<div class="empty-state"><div>${escapeHtml(emptyText)}</div></div>`;

  return `
    <section class="summary-card lof-monitor-card ${escapeHtml(extraClass)}">
      <h3>${escapeHtml(title)}</h3>
      ${body}
    </section>
  `;
}

function renderLofArbGroupTabs() {
  const active = ensureLofSubview();
  return `
    <div class="subtab-nav">
      ${readLofArbGroups().map((group) => `
        <button
          type="button"
          class="subtab-button ${active === group.key ? 'active' : ''}"
          data-lof-subview="${escapeHtml(group.key)}"
        >${escapeHtml(group.label || group.key)}</button>
      `).join('')}
    </div>
  `;
}

function renderLofArbPanel() {
  const panel = dom.tabPanels['lof-arb'];
  const resource = state.resources.lofArb;
  if (!panel) return;

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading('LOF 套利正在抓取集思录 LOF / QDII 来源');
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError('LOF 套利加载失败', resource.error?.message);
    return;
  }

  ensureLofSubview();
  const rows = readLofArbRows();
  const visibleRows = readLofArbVisibleRows();
  const limitedRows = readLofArbLimitedRows();
  const unlimitedRows = readLofArbUnlimitedRows();
  const summary = readLofArbSummary();
  const rebuildStatus = readLofArbRebuildStatus();
  const activeGroup = readLofArbGroups().find((item) => item.key === state.lofSubview);
  const groupSummary = summary.groups && typeof summary.groups === 'object' ? summary.groups[state.lofSubview] : null;
  const sourceVisibleCount = (() => {
    const allCount = Number(groupSummary?.allCount || 0);
    if (Number.isFinite(allCount) && allCount > 0) return allCount;
    const visibleCount = Number(groupSummary?.visibleCount || 0);
    if (Number.isFinite(visibleCount) && visibleCount > 0) return visibleCount;
    return visibleRows.length;
  })();

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">LOF套利</div>
          <div class="section-note">固定锚定集思录 LOF / QDII 页面家族，顶部只保留监控池，列表按分组查看 IOPV 与溢价率。</div>
        </div>
      </div>
      <div class="summary-grid">
        ${renderLofMonitorSummaryCard('限购池', limitedRows, '满足限购 + 溢价 + 成交额规则后才会入池')}
        ${renderLofMonitorSummaryCard('非限池', unlimitedRows, '满足不限购且溢价率绝对值超过阈值后才会入池', 'negative-card')}
      </div>
      <div class="list-card">
        <div class="module-toolbar">
          <div>
            <h3>列表</h3>
            <div class="section-note">${escapeHtml((activeGroup?.label || '当前分组'))} / 当前展示 ${formatInt(visibleRows.length)} 条 / 源侧可见 ${formatInt(sourceVisibleCount)} 条</div>
          </div>
          <div class="panel-meta">
            <span>最近更新 ${escapeHtml(formatDate(readUpdateTime('lofArb') || rebuildStatus.lastRebuildAt))}</span>
            <span>${escapeHtml(readFreshnessText('lofArb'))}</span>
            <span>${groupSummary?.guestLimited ? '当前为游客可见范围' : '当前为完整可见范围'}</span>
          </div>
        </div>
        ${renderLofArbGroupTabs()}
        ${renderTableSearchBar('lofArb')}
        <div data-table-host="lofArb">
          ${renderPaginatedTable({
            tableKey: 'lofArb',
            tableKind: 'lof',
            columns: buildLofArbColumns(),
            rows: visibleRows,
            emptyMessage: '当前分组没有符合条件的 LOF 套利数据',
          })}
        </div>
      </div>
      ${renderLofArbPushCard()}
    </div>
  `;
}

function buildCbRightsIssueColumns(options = {}) {
  const includeRecordDate = Boolean(options.includeRecordDate);
  const includeMarginColumns = options.includeMarginColumns !== false;
  const includePeelColumns = options.includePeelColumns !== false;
  const columns = [
    { key: 'index', label: '序号' },
    { key: 'stockCode', label: '正股代码', columnClassName: 'col-code', sortable: true, sortType: 'text', defaultDir: 'asc', sortValue: (row) => String(row.stockCode || ''), render: (row) => `<span class="mono-text">${escapeHtml(row.stockCode || '--')}</span>` },
    {
      key: 'stockName',
      label: '正股名称',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => String(row.stockName || ''),
      render: (row) => escapeHtml(row.stockName || '--'),
    },
    { key: 'progressName', label: '方案进展', sortable: true, sortType: 'text', defaultDir: 'asc', sortValue: (row) => String(row.progressName || ''), render: (row) => escapeHtml(row.progressName || '--') },
    { key: 'progressDate', label: '进展公告日', columnClassName: 'col-date', sortable: true, sortType: 'date', defaultDir: 'desc', sortValue: (row) => normalizeDateKey(row.progressDate), render: (row) => escapeHtml(formatDateOnly(row.progressDate)) },
    { key: 'issueScaleYi', label: '发行规模', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.issueScaleYi), render: (row) => toNumber(row.issueScaleYi) === null ? '--' : `${formatNumber(row.issueScaleYi, 2)}亿` },
    { key: 'stockMarketValueYi', label: '流通市值', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.stockMarketValueYi), render: (row) => toNumber(row.stockMarketValueYi) === null ? '--' : `${formatNumber(row.stockMarketValueYi, 2)}亿` },
    { key: 'issueRatio', label: '发行比例', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.issueRatio), render: (row) => formatRatioPercent(row.issueRatio, 2) },
    { key: 'rawRequiredShares', label: '原始所需股数', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.rawRequiredShares), render: (row) => formatNumber(row.rawRequiredShares, 2) },
    { key: 'placementShares', label: '配售股数', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.placementShares), render: (row) => formatNumber(row.placementShares, 2) },
    { key: 'convertPrice', label: '转股价', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.convertPrice), render: (row) => formatNumber(row.convertPrice, 2) },
    { key: 'volatility250', label: '波动率', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.volatility250 ?? row.volatility60), render: (row) => formatRatioPercent(row.volatility250 ?? row.volatility60, 2) },
    { key: 'optionUnitValue', label: '单位期权价值', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.optionUnitValue), render: (row) => formatNumber(row.optionUnitValue, 4) },
    { key: 'optionValue', label: '期权价值', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.optionValue), render: (row) => formatNumber(row.optionValue, 2) },
    { key: 'requiredFunds', label: '所需资金', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.requiredFunds), render: (row) => toNumber(row.requiredFunds) === null ? '--' : `¥${formatNumber(row.requiredFunds, 2)}` },
  ];
  if (includeMarginColumns) {
    columns.splice(9, 0, { key: 'marginRequiredShares', label: '两融所需股数', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.marginRequiredShares), render: (row) => formatInt(row.marginRequiredShares) });
    columns.splice(10, 0, { key: 'marginRequiredFunds', label: '两融所需资金', columnClassName: 'col-num', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.marginRequiredFunds), render: (row) => toNumber(row.marginRequiredFunds) === null ? '--' : `¥${formatNumber(row.marginRequiredFunds, 2)}` });
  }
  if (includeRecordDate) {
    columns.push({
      key: 'recordDate',
      label: '股权登记日',
      columnClassName: 'col-date',
      sortable: true,
      sortType: 'date',
      defaultDir: 'desc',
      sortValue: (row) => normalizeDateKey(row.recordDate),
      render: (row) => escapeHtml(formatDateOnly(row.recordDate)),
    });
  }
  columns.push({ key: 'expectedReturnRate', label: '预期收益率', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.expectedReturnRate), className: (row) => statusClass(row.expectedReturnRate), render: (row) => formatPercent(row.expectedReturnRate, 2) });
  if (includeMarginColumns) {
    columns.push({ key: 'marginReturnRate', label: '两融收益率', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.marginReturnRate), className: (row) => statusClass(row.marginReturnRate), render: (row) => formatPercent(row.marginReturnRate, 2) });
  }
  if (includePeelColumns) {
    columns.push({ key: 'expectedPeelReturnRate', label: '预期收益率去皮', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.expectedPeelReturnRate), className: (row) => statusClass(row.expectedPeelReturnRate), render: (row) => formatPercent(row.expectedPeelReturnRate, 2) });
  }
  if (includeMarginColumns && includePeelColumns) {
    columns.push({ key: 'marginPeelReturnRate', label: '两融收益率去皮', columnClassName: 'col-percent', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.marginPeelReturnRate), className: (row) => statusClass(row.marginPeelReturnRate), render: (row) => formatPercent(row.marginPeelReturnRate, 2) });
  }
  return columns;
}

function renderCbRightsIssueMarketTabs() {
  const active = ensureCbRightsIssueMarketSubview();
  return `
    <div class="subtab-nav">
      ${CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE.map((marketKey) => {
        const meta = readCbRightsIssueActiveMarketMeta(marketKey);
        return `
          <button
            type="button"
            class="subtab-button ${active === marketKey ? 'active' : ''}"
            data-cb-rights-issue-market-subtab="${escapeHtml(marketKey)}"
          >
            ${escapeHtml(meta.label)}（${escapeHtml(formatInt(meta.rows.length))}）
          </button>
        `;
      }).join('')}
    </div>
  `;
}

function renderCbRightsIssueStageSection(meta) {
  return `
    <section class="list-card">
      <div class="module-toolbar">
        <div>
          <h3>${escapeHtml(meta.label)}</h3>
          <div class="section-note">${escapeHtml(meta.note)}</div>
        </div>
        <div class="panel-meta">
          <span>${escapeHtml(meta.marketLabel)} ${escapeHtml(formatInt(meta.rows.length))} 条</span>
          <span>来源页 ${buildAnchor(readCbRightsIssueSummary().sourceUrl, '打开') || '--'}</span>
        </div>
      </div>
      ${renderTableSearchBar(meta.tableKey)}
      <div data-table-host="${escapeHtml(meta.tableKey)}">
        ${renderPaginatedTable({
          tableKind: 'convertible',
          tableKey: meta.tableKey,
          columns: buildCbRightsIssueColumns({
            includeRecordDate: meta.includeRecordDate,
            includeMarginColumns: meta.includeMarginColumns,
            includePeelColumns: meta.includePeelColumns,
          }),
          rows: meta.rows,
          emptyMessage: meta.emptyMessage,
        })}
      </div>
    </section>
  `;
}

function renderCbRightsIssuePanel() {
  const panel = dom.tabPanels['cb-rights-issue'];
  const resource = state.resources.cbRightsIssue;
  if (!panel) return;

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading('可转债抢权配售正在抓取固定来源与历史库数据');
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError('可转债抢权配售加载失败', resource.error?.message);
    return;
  }

  const activeMarketMeta = readCbRightsIssueActiveMarketMeta();
  const shCounts = {
    apply: readCbRightsIssueRowsByMarketAndSubview('sh', 'apply').length,
    ambush: readCbRightsIssueRowsByMarketAndSubview('sh', 'ambush').length,
    wait: readCbRightsIssueRowsByMarketAndSubview('sh', 'wait').length,
  };
  const szCounts = {
    apply: readCbRightsIssueRowsByMarketAndSubview('sz', 'apply').length,
    ambush: readCbRightsIssueRowsByMarketAndSubview('sz', 'ambush').length,
    wait: readCbRightsIssueRowsByMarketAndSubview('sz', 'wait').length,
  };
  const summary = readCbRightsIssueSummary();
  const rebuildStatus = readCbRightsIssueRebuildStatus();

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">可转债抢权配售</div>
          <div class="section-note">页面拆为沪市与深市两个页签；每个页签内部按申购阶段、埋伏阶段、等待阶段三张独立表格竖向展示。深市不再显示两融与去皮玩法相关列。</div>
        </div>
        <div class="panel-meta">
          <span>固定源总数 ${escapeHtml(formatInt(summary.totalRows))}</span>
          <span>申购阶段 ${escapeHtml(formatInt(summary.applyStageCount))}</span>
          <span>沪市 ${escapeHtml(formatInt(readCbRightsIssueRowsByMarket('sh').length))}</span>
          <span>深市 ${escapeHtml(formatInt(readCbRightsIssueRowsByMarket('sz').length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime('cbRightsIssue') || rebuildStatus.lastRebuildAt))}</span>
          <span>${escapeHtml(readFreshnessText('cbRightsIssue'))}</span>
        </div>
      </div>
      <div class="list-card">
        <div class="module-toolbar">
          <div>
            <h3>${escapeHtml(activeMarketMeta.label)}</h3>
            <div class="section-note">${escapeHtml(activeMarketMeta.note)}</div>
          </div>
          <div class="panel-meta">
            <span>${escapeHtml(activeMarketMeta.label)}申购 ${escapeHtml(formatInt(activeMarketMeta.key === 'sh' ? shCounts.apply : szCounts.apply))}</span>
            <span>${escapeHtml(activeMarketMeta.label)}埋伏 ${escapeHtml(formatInt(activeMarketMeta.key === 'sh' ? shCounts.ambush : szCounts.ambush))}</span>
            <span>${escapeHtml(activeMarketMeta.label)}等待 ${escapeHtml(formatInt(activeMarketMeta.key === 'sh' ? shCounts.wait : szCounts.wait))}</span>
          </div>
        </div>
        ${renderCbRightsIssueMarketTabs()}
      </div>
      ${CB_RIGHTS_ISSUE_SUBTAB_SEQUENCE.map((subview) => renderCbRightsIssueStageSection(readCbRightsIssueSubviewMeta(activeMarketMeta.key, subview))).join('')}
      ${renderModuleFootnote('cbRightsIssue')}
    </div>
  `;
}

function renderPremiumPanel(type) {
  const panel = dom.tabPanels[type];
  const resource = state.resources[type];
  if (!panel) return;

  const config = getPremiumConfig(type);

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading(`${config.title} 正在加载`);
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError(`${config.title} 加载失败`, resource.error?.message);
    return;
  }

  const rows = readResourceArray(type);
  if (!rows.length) {
    panel.innerHTML = moduleEmpty(`${config.title} 暂无数据`);
    return;
  }

  const columns = buildPremiumColumns(type);
  const tableModel = getProcessedTableRows(type, rows, columns);
  const summaryColumn = resolvePremiumSummaryColumn(type, tableModel.sortColumn, columns);
  const summaryLabel = summaryColumn?.label || '溢价率';
  const topRows = sortRowsByColumn(rows, summaryColumn, 'desc').slice(0, 3);
  const bottomRows = sortRowsByColumn(rows, summaryColumn, 'asc').slice(0, 3);

  panel.innerHTML = `
    <div class="module-shell">
      <div class="premium-toolbar">
        <div>
          <div class="tab-title">${config.title}</div>
        </div>
        <div class="panel-meta">
          <span>总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime(type)))}</span>
          <span>${escapeHtml(readFreshnessText(type))}</span>
        </div>
      </div>
      <div class="summary-grid">
        ${renderSummaryCard(
          `${summaryLabel}前3`,
          buildPremiumSummaryRows(topRows, config, summaryColumn)
        )}
        ${renderSummaryCard(
          `${summaryLabel}后3`,
          buildPremiumSummaryRows(bottomRows, config, summaryColumn),
          'negative-card'
        )}
      </div>
      <div class="list-card">
        <h3>列表</h3>
        ${renderTableSearchBar(type)}
        <div data-table-host="${escapeHtml(type)}">
          ${renderPaginatedTable({
            tableKey: type,
            tableKind: 'premium',
            columns,
            rows,
            emptyMessage: `${config.title} 暂无数据`,
          })}
        </div>
        <div class="slim-note">${buildPremiumExplainText(type, rows)}</div>
      </div>
      ${renderModuleFootnote(type)}
    </div>
  `;
}

function buildPremiumSummaryRows(rows, config, summaryColumn) {
  return rows.map((row) => ({
    title: `${row.aName || '--'} ${row.aCode || ''}`.trim(),
    subtitle: `${config.peerPriceLabel} ${formatNumber(row[config.peerPriceKey], 2)} / 样本区间 ${formatHistoryRange(row)}`,
    value: readPremiumSummaryValue(row, summaryColumn, config.peerPriceKey),
    valueClass: readPremiumSummaryClass(row, summaryColumn, config.peerPriceKey),
  }));
}

function buildPremiumExplainText(type, rows) {
  const parts = ['“近三年分位”基于当前可用历史样本计算；A股历史价格优先使用后复权收盘价，“样本区间”显示实际覆盖起止日期。'];
  const catlRow = type === 'ah' ? rows.find((row) => String(row.aCode) === '300750') : null;
  if (catlRow) {
    parts.push(`宁德时代 300750 / 03750 当前样本区间为 ${formatHistoryRange(catlRow)}，可用样本数为 ${formatInt(catlRow.historyCount)}。`);
  }
  return escapeHtml(parts.join(' '));
}

function formatHistoryRange(row) {
  return formatCompactRange(row?.historyStartDate, row?.historyEndDate);
}

function readPremiumSummaryValue(row, summaryColumn, peerPriceKey) {
  if (!summaryColumn) return '--';
  if (summaryColumn.key === 'priceGap') return formatSignedNumber(computePremiumGap(row, peerPriceKey), 2);
  if (summaryColumn.key === 'premium' || summaryColumn.key === 'percentile') return formatPercent(row[summaryColumn.key], 2);
  if (summaryColumn.key === 'aPrice' || summaryColumn.key === peerPriceKey) return formatNumber(row[summaryColumn.key], 2);
  return '--';
}

function readPremiumSummaryClass(row, summaryColumn, peerPriceKey) {
  if (!summaryColumn) return '';
  if (summaryColumn.key === 'priceGap') return statusClass(computePremiumGap(row, peerPriceKey));
  if (summaryColumn.key === 'premium' || summaryColumn.key === 'percentile') return statusClass(row[summaryColumn.key]);
  return '';
}

function resolvePremiumSummaryColumn(type, activeColumn, columns) {
  if (type === 'ab') {
    return columns.find((item) => item.key === 'premium') || activeColumn;
  }
  const supportedKeys = new Set(['priceGap', 'premium', 'percentile', 'aPrice', 'hPriceCny', 'bPriceCny']);
  if (activeColumn && supportedKeys.has(activeColumn.key)) return activeColumn;
  return columns.find((item) => item.key === 'premium') || activeColumn;
}

function renderMonitorPanel() {
  const panel = dom.tabPanels.monitor;
  const resource = state.resources.monitor;
  if (!panel) return;

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading('监控套利正在加载');
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError('监控套利加载失败', summarizeMonitorError(resource.error?.message));
    return;
  }

  const payload = readResourceObject('monitor');
  const rows = [...readResourceArray('monitor')].sort((a, b) => (bestMonitorYield(b) ?? -Infinity) - (bestMonitorYield(a) ?? -Infinity));
  if (!rows.length && payload?.error) {
    panel.innerHTML = moduleError('监控套利加载失败', summarizeMonitorError(payload.error));
    return;
  }

  const columns = [
    {
      key: 'name',
      label: '监控项',
      render: (row) => `
        <div class="monitor-item-head">
          <span>${escapeHtml(row.name || '--')}</span>
          <span class="monitor-item-actions">
            <button type="button" class="mini-action" data-monitor-action="edit" data-monitor-id="${escapeHtml(String(row.id || ''))}">编辑</button>
            <button type="button" class="mini-action danger" data-monitor-action="delete" data-monitor-id="${escapeHtml(String(row.id || ''))}" ${state.savingMonitor ? 'disabled' : ''}>删除</button>
          </span>
        </div>
        <div class="muted">${escapeHtml(row.acquirerName || '--')} → ${escapeHtml(row.targetName || '--')}</div>
      `,
    },
    {
      key: 'targetPrice',
      label: '目标现价',
      render: (row) => `¥${formatNumber(readMonitorTargetPrice(row), 3)}`,
    },
    {
      key: 'stockYieldRate',
      label: '股票腿收益率',
      className: (row) => statusClass(row.stockYieldRate),
      render: (row) => formatPercent(row.stockYieldRate, 3),
    },
    {
      key: 'cashYieldRate',
      label: '现金腿收益率',
      className: (row) => statusClass(row.cashYieldRate),
      render: (row) => formatPercent(row.cashYieldRate, 3),
    },
    {
      key: 'bestYield',
      label: '最优收益率',
      className: (row) => statusClass(bestMonitorYield(row)),
      render: (row) => formatPercent(bestMonitorYield(row), 3),
    },
  ];

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">监控套利</div>
          <div class="section-note">新增/编辑表单默认收起，点击后直接在当前页内向下展开；代码、市场、币种等由股票检索自动判断并显示确认。</div>
        </div>
        <div class="button-row inline">
          <span class="meta-chip">总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span class="meta-chip">最近更新 ${escapeHtml(formatDate(readUpdateTime('monitor')))}</span>
          <button type="button" class="btn-primary" data-monitor-action="open-create" ${state.savingMonitor ? 'disabled' : ''}>新增监控</button>
        </div>
      </div>
      ${renderMonitorEditor()}
      ${renderPaginatedTable({
        tableKind: 'monitor',
        tableKey: 'monitor',
        columns,
        rows,
        emptyMessage: '当前没有监控套利项目',
        detailRenderer: (row) => renderDetailGrid(buildMonitorDetailItems(row)),
        detailMode: 'always',
      })}
      ${renderModuleFootnote('monitor')}
    </div>
  `;
}

function renderMonitorEditor() {
  const draft = readMonitorEditorDraft();
  const isOpen = Boolean(state.monitorEditor?.open);
  const isEditMode = state.monitorEditor?.mode === 'edit' && draft.id;
  const submitLabel = isEditMode ? '保存修改' : '新增监控';
  if (!isOpen) return '';

  return `
    <div class="list-card monitor-editor-card monitor-editor-inline" data-monitor-inline-editor="1">
      <div class="monitor-editor-head">
        <div>
          <h3>${isEditMode ? '编辑监控项目' : '新增监控项目'}</h3>
          <div class="section-note">表单直接在当前页内展开。输入股票简称或代码后会自动检索，并明确显示系统识别到的证券；保存后自动收起。</div>
        </div>
        <div class="button-row">
          <button type="button" class="btn-secondary" data-monitor-action="close-editor" ${state.savingMonitor ? 'disabled' : ''}>收起</button>
        </div>
      </div>
      <div class="formula-box formula-box-compact">
        <h3>计算口径</h3>
        <div class="formula-lines">
          <div class="formula-line">股票腿理论对价 = 收购方股价 × 换股比例 × 安全系数 + 现金对价</div>
          <div class="formula-line">现金腿收益率 = (现金选择权 - 目标现价) / 目标现价 × 100</div>
        </div>
      </div>
      <form id="monitor-editor-form" class="monitor-editor-form">
        <input type="hidden" name="id" value="${escapeHtml(draft.id)}" />
        <div class="monitor-form-grid monitor-form-grid-simple">
          <div class="input-group">
            <label for="monitor-acquirer-name">收购方</label>
            <input
              id="monitor-acquirer-name"
              name="acquirerName"
              type="text"
              value="${escapeHtml(draft.acquirerName)}"
              placeholder="例如 中金公司 / 601995"
              autocomplete="off"
            />
            <div id="monitor-acquirer-lookup" class="monitor-lookup-zone" aria-live="polite">${renderMonitorLookupMarkup('acquirer')}</div>
          </div>
          <div class="input-group">
            <label for="monitor-target-name">目标方</label>
            <input
              id="monitor-target-name"
              name="targetName"
              type="text"
              value="${escapeHtml(draft.targetName)}"
              placeholder="例如 东兴证券 / 601198 / 02688"
              autocomplete="off"
            />
            <div id="monitor-target-lookup" class="monitor-lookup-zone" aria-live="polite">${renderMonitorLookupMarkup('target')}</div>
          </div>
          <div class="input-group">
            <label for="monitor-stock-ratio">换股比例</label>
            <input id="monitor-stock-ratio" name="stockRatio" type="number" step="0.0001" value="${escapeHtml(String(draft.stockRatio ?? ''))}" placeholder="例如 0.4373" />
          </div>
          <div class="input-group">
            <label for="monitor-safety-factor">安全系数</label>
            <input id="monitor-safety-factor" name="safetyFactor" type="number" min="0" max="1" step="0.0001" value="${escapeHtml(String(draft.safetyFactor ?? 1))}" />
          </div>
          <div class="input-group">
            <label for="monitor-cash-distribution">现金对价</label>
            <input id="monitor-cash-distribution" name="cashDistribution" type="number" step="0.0001" value="${escapeHtml(String(draft.cashDistribution ?? ''))}" />
          </div>
          <div class="input-group">
            <label for="monitor-cash-distribution-currency">现金对价币种</label>
            <select id="monitor-cash-distribution-currency" name="cashDistributionCurrency">${renderSelectOptions(MONITOR_CURRENCY_OPTIONS, draft.cashDistributionCurrency)}</select>
          </div>
          <div class="input-group">
            <label for="monitor-cash-option-price">现金选择权</label>
            <input id="monitor-cash-option-price" name="cashOptionPrice" type="number" step="0.0001" value="${escapeHtml(String(draft.cashOptionPrice ?? ''))}" />
          </div>
          <div class="input-group">
            <label for="monitor-cash-option-currency">现金选择权币种</label>
            <select id="monitor-cash-option-currency" name="cashOptionCurrency">${renderSelectOptions(MONITOR_CURRENCY_OPTIONS, draft.cashOptionCurrency)}</select>
          </div>
        </div>
        <div class="button-row">
          <button type="submit" class="btn-primary" ${state.savingMonitor ? 'disabled' : ''}>${submitLabel}</button>
          <button type="button" class="btn-secondary" data-monitor-action="close-editor" ${state.savingMonitor ? 'disabled' : ''}>取消</button>
        </div>
      </form>
    </div>
  `;
}

function renderSelectOptions(options, selectedValue) {
  return options
    .map((item) => `<option value="${escapeHtml(item)}" ${item === selectedValue ? 'selected' : ''}>${escapeHtml(item)}</option>`)
    .join('');
}

function renderDividendPanel() {
  const panel = dom.tabPanels.dividend;
  const resource = state.resources.dividend;
  if (!panel) return;

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading('分红提醒正在刷新');
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError('分红提醒加载失败', resource.error?.message);
    return;
  }

  const rows = readResourceArray('dividend');
  if (!rows.length) {
    panel.innerHTML = moduleEmpty('当前没有分红观察名单');
    return;
  }

  const today = todayKey();
  const todayRows = rows.filter((row) => normalizeDateKey(row?.dividendData?.recordDate) === today);
  const sortedByYield = [...rows].sort(
    (a, b) => (toNumber(b?.dividendData?.dividendYield) ?? -Infinity) - (toNumber(a?.dividendData?.dividendYield) ?? -Infinity)
  );
  const tableColumns = [
    { key: 'code', label: '代码', render: (row) => escapeHtml(row.code || '--') },
    { key: 'name', label: '名称', render: (row) => escapeHtml(row.name || '--') },
    { key: 'recordDate', label: '登记日', render: (row) => formatDateOnly(row?.dividendData?.recordDate) },
    { key: 'exDividendDate', label: '除权日', render: (row) => formatDateOnly(row?.dividendData?.exDividendDate) },
    { key: 'payDate', label: '派息日', render: (row) => formatDateOnly(row?.dividendData?.payDate) },
    { key: 'dividendPerShare', label: '每股分红', render: (row) => formatNumber(row?.dividendData?.dividendPerShare, 3) },
    {
      key: 'dividendYield',
      label: '股息率',
      className: (row) => statusClass(row?.dividendData?.dividendYield),
      render: (row) => formatPercent(row?.dividendData?.dividendYield, 2),
    },
  ];

  const todayList = todayRows.map((row) => ({
    title: `${row.name || '--'} ${row.code || ''}`.trim(),
    subtitle: `除权 ${formatDateOnly(row?.dividendData?.exDividendDate)} / 派息 ${formatDateOnly(row?.dividendData?.payDate)}`,
    value: formatPercent(row?.dividendData?.dividendYield, 2),
  }));

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">分红提醒</div>
          <div class="section-note">优先强调今日登记日提醒，再展示完整观察名单。</div>
        </div>
        <div class="panel-meta">
          <span>今日提醒 ${escapeHtml(formatInt(todayRows.length))}</span>
          <span>总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime('dividend')))}</span>
        </div>
      </div>
      <div class="list-card card-stack">
        <h3>今日登记日提醒</h3>
        ${todayList.length ? renderStackItems(todayList) : '<div class="empty-state"><div>今天没有登记日提醒</div></div>'}
      </div>
      <div class="list-card card-stack">
        <h3>分红观察名单</h3>
        ${renderPaginatedTable({
          tableKind: 'dividend',
          tableKey: 'dividend',
          columns: tableColumns,
          rows: sortedByYield,
          emptyMessage: '当前没有分红观察名单',
        })}
      </div>
      ${renderModuleFootnote('dividend')}
    </div>
  `;
}

function renderRiskFlags(flags) {
  const items = Array.isArray(flags) ? flags.filter(Boolean) : [];
  return items.length ? items.join('；') : '--';
}
function readEventArbitrageResponse() {
  return readResourcePayload('merger');
}

function readEventArbitrageData() {
  return readObject(readEventArbitrageResponse().data);
}

function readEventArbitrageCategories() {
  return readObject(readEventArbitrageData().categories);
}

function readEventArbitrageCategoryRows(category) {
  const rows = readEventArbitrageCategories()[category];
  return Array.isArray(rows) ? rows : [];
}

function readEventArbitrageOverview() {
  return readObject(readEventArbitrageData().overview);
}

function readEventArbitrageSourceStatus() {
  return readObject(readEventArbitrageData().sourceStatus);
}

function readEventArbitrageStatus(category) {
  return readObject(readEventArbitrageSourceStatus()[category]);
}

function readEventArbitrageSubview() {
  return EVENT_ARB_SUBTAB_SEQUENCE.includes(state.mergerSubview) ? state.mergerSubview : 'a_event';
}

function eventArbStatusLabel(status) {
  const map = {
    ok: '正常',
    empty: '暂无数据',
    error: '抓取失败',
    stale_cache: '使用缓存',
    disabled: '已关闭',
    disabled_no_public_source: '待接入',
    pending: '待聚合',
  };
  return map[String(status || '').trim()] || '未知';
}

function eventArbCategoryLabel(category) {
  const map = {
    a_event: 'A股套利',
    hk_private: '港股套利',
    cn_private: '中概私有',
    rights_issue: '港供套利',
    announcement_pool: '最新公告',
  };
  return map[category] || category;
}

function formatBooleanLabel(value) {
  if (value === true) return '是';
  if (value === false) return '否';
  return '--';
}

function buildAnchor(url, label) {
  const href = String(url || '').trim();
  if (!href) return '';
  return `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
}

function renderEventArbitrageLinks(row) {
  const links = [
    buildAnchor(row?.detailUrl, '详情链接'),
    buildAnchor(row?.announcementUrl, row?.category === 'a_event' ? '官方公告' : '公告链接'),
    buildAnchor(row?.officialMatch?.pdfUrl, '匹配PDF'),
  ].filter(Boolean);
  return links.length ? links.join(' / ') : '--';
}

function renderEventArbitrageMatchText(row) {
  const match = row?.officialMatch;
  if (!match || match.matched !== true) return '未匹配';
  return match.reportAvailable ? '已匹配 / 可生成AI报告' : '已匹配';
}

function renderEventArbitrageDetail(row) {
  const items = [
    { label: '类别', value: eventArbCategoryLabel(row?.category) },
    { label: '事件阶段', value: row?.eventStage || '--' },
    { label: '事件类型', value: row?.eventType || '--' },
    { label: '来源', value: row?.source || '--' },
    { label: '最新公告标题', value: row?.officialMatch?.title || '--' },
    { label: '公告日期', value: formatDateOnly(row?.officialMatch?.announcementDate) },
    { label: 'AI报告', value: row?.officialMatch?.reportAvailable ? '可生成' : '不可生成' },
    { label: '备注', value: row?.summary || '--' },
  ];
  const links = renderEventArbitrageLinks(row);
  return `
    ${renderDetailGrid(items)}
    <div class="slim-note detail-note">链接：${links}</div>
  `;
}

function renderEventArbitrageSubtabs() {
  const active = readEventArbitrageSubview();
  return `
    <div class="subtab-nav">
      ${EVENT_ARB_SUBTAB_SEQUENCE.map((key) => {
        const disabled = key === 'rights_issue';
        const label = eventArbCategoryLabel(key);
        return `
          <button
            type="button"
            class="subtab-button ${active === key ? 'active' : ''} ${disabled ? 'disabled' : ''}"
            data-event-arb-subtab="${escapeHtml(key)}"
          >
            ${escapeHtml(label)}
          </button>
        `;
      }).join('')}
    </div>
  `;
}

function renderEventArbitrageOverviewView() {
  const overview = readEventArbitrageOverview();
  const sourceStatus = readEventArbitrageSourceStatus();
  const freshness = readEventArbitrageData().servedFromCache ? '当前展示聚合缓存' : '当前展示实时聚合结果';
  const statusRows = ['hk_private', 'cn_private', 'a_event', 'announcement_pool', 'rights_issue'].map((key) => {
    const status = readObject(sourceStatus[key]);
    return {
      title: eventArbCategoryLabel(key),
      subtitle: `${eventArbStatusLabel(status.status)} / 更新时间 ${formatDate(status.updateTime || readUpdateTime('merger'))}`,
      value: formatInt(status.itemCount || 0),
      valueClass: status.status === 'error' ? 'negative' : (status.status === 'stale_cache' ? '' : 'positive'),
    };
  });

  return `
    <div class="summary-grid">
      <section class="summary-card">
        <h3>公开事件总数</h3>
        <div class="item-value">${escapeHtml(formatInt(overview.totalCount || 0))}</div>
        <div class="item-subtitle">港股 + 中概股 + A股事件的统一总览</div>
      </section>
      <section class="summary-card">
        <h3>正套利数量</h3>
        <div class="item-value positive">${escapeHtml(formatInt(overview.positiveCount || 0))}</div>
        <div class="item-subtitle">按当前外部事件源返回的正套利空间统计</div>
      </section>
      <section class="summary-card">
        <h3>公告池匹配</h3>
        <div class="item-value">${escapeHtml(formatInt(overview.todayMatchedCount || 0))}</div>
        <div class="item-subtitle">按证券代码精确匹配的当日公告命中数</div>
      </section>
      <section class="summary-card">
        <h3>公告池条数</h3>
        <div class="item-value">${escapeHtml(formatInt(overview.announcementPoolCount || 0))}</div>
        <div class="item-subtitle">辅助校验与 AI 报告所用的现有公告池</div>
      </section>
    </div>
    <div class="list-card">
      <h3>来源状态</h3>
      <div class="section-note detail-note">${escapeHtml(freshness)}，最近更新 ${escapeHtml(formatDate(readUpdateTime('merger')))}</div>
      ${renderStackItems(statusRows)}
    </div>
  `;
}

function buildEventArbHkColumns() {
  return [
    { key: 'symbol', label: '代码', render: (row) => `<div class="mono-text">${escapeHtml(row.symbol || '--')}</div>` },
    { key: 'name', label: '名称', render: (row) => escapeHtml(row.name || '--') },
    { key: 'currentPrice', label: '现价', render: (row) => formatNumber(row.currentPrice, 2) },
    { key: 'changeRate', label: '涨跌幅', className: (row) => statusClass(row.changeRate), render: (row) => formatPercent(row.changeRate, 2) },
    { key: 'marketValue', label: '市值', render: (row) => escapeHtml(row.marketValueText || '--') },
    { key: 'offerPriceText', label: '私有化价格', render: (row) => escapeHtml(row.offerPriceText || '--') },
    { key: 'spreadRate', label: '套利空间', className: (row) => statusClass(row.spreadRate), render: (row) => formatPercent(row.spreadRate, 2) },
    { key: 'eventStage', label: '私有化进程', render: (row) => escapeHtml(row.eventStage || '--') },
    { key: 'offeror', label: '要约方', render: (row) => escapeHtml(row.offeror || '--') },
    { key: 'offerorHoldingText', label: '要约方持股', render: (row) => escapeHtml(row.offerorHoldingText || '--') },
    { key: 'registryPlace', label: '注册地', render: (row) => escapeHtml(row.registryPlace || '--') },
    { key: 'dealMethod', label: '收购方式', render: (row) => escapeHtml(row.dealMethod || '--') },
    { key: 'canCounter', label: '是否可反套', render: (row) => escapeHtml(formatBooleanLabel(row.canCounter)) },
    { key: 'canShort', label: '是否可卖空', render: (row) => escapeHtml(formatBooleanLabel(row.canShort)) },
    { key: 'detailUrl', label: '核心公告', render: (row) => buildAnchor(row.detailUrl, '核心公告') || '--' },
  ];
}

function buildEventArbCnColumns() {
  return [
    { key: 'symbol', label: '代码', render: (row) => `<div class="mono-text">${escapeHtml(row.symbol || '--')}</div>` },
    { key: 'name', label: '名称', render: (row) => escapeHtml(row.name || '--') },
    { key: 'currentPrice', label: '现价', render: (row) => formatNumber(row.currentPrice, 2) },
    { key: 'changeRate', label: '涨跌幅', className: (row) => statusClass(row.changeRate), render: (row) => formatPercent(row.changeRate, 2) },
    { key: 'marketValue', label: '市值', render: (row) => escapeHtml(row.marketValueText || '--') },
    { key: 'offerPriceText', label: '私有化价格', render: (row) => escapeHtml(row.offerPriceText || '--') },
    { key: 'spreadRate', label: '套利空间', className: (row) => statusClass(row.spreadRate), render: (row) => formatPercent(row.spreadRate, 2) },
    { key: 'eventStage', label: '进程', render: (row) => escapeHtml(row.eventStage || '--') },
    { key: 'offeror', label: '要约方', render: (row) => escapeHtml(row.offeror || '--') },
    { key: 'dealMethod', label: '收购方式', render: (row) => escapeHtml(row.dealMethod || '--') },
    { key: 'detailUrl', label: '详情链接', render: (row) => buildAnchor(row.detailUrl, '详情链接') || '--' },
  ];
}

function buildEventArbAColumns() {
  return [
    { key: 'symbol', label: '代码', render: (row) => `<div class="mono-text">${escapeHtml(row.symbol || '--')}</div>` },
    { key: 'name', label: '名称', render: (row) => escapeHtml(row.name || '--') },
    { key: 'currentPrice', label: '现价', render: (row) => formatNumber(row.currentPrice, 2) },
    { key: 'changeRate', label: '涨跌幅', className: (row) => statusClass(row.changeRate), render: (row) => formatPercent(row.changeRate, 2) },
    { key: 'safePriceText', label: '安全边际价', render: (row) => escapeHtml(row.safePriceText || '--') },
    { key: 'safeDiscountRate', label: '安全边际折价', className: (row) => statusClass(row.safeDiscountRate), render: (row) => formatPercent(row.safeDiscountRate, 2) },
    { key: 'choosePriceText', label: '现金选择权价格', render: (row) => escapeHtml(row.choosePriceText || '--') },
    { key: 'chooseDiscountRate', label: '现金选择权折价', className: (row) => statusClass(row.chooseDiscountRate), render: (row) => formatPercent(row.chooseDiscountRate, 2) },
    { key: 'currency', label: '币种', render: (row) => escapeHtml(row.currency || '--') },
    { key: 'eventType', label: '事件类型', render: (row) => escapeHtml(row.eventType || '--') },
    { key: 'announcementUrl', label: '官方公告', render: (row) => buildAnchor(row.announcementUrl || row.detailUrl, '官方公告') || '--' },
  ];
}

function buildEventArbAnnouncementColumns() {
  return [
    {
      key: 'announcementTime',
      label: '公告时间',
      render: (row) => `
        <div>${escapeHtml(readAnnouncementLabel(row))}</div>
        ${isTodayAnnouncement(row) ? '<div class="today-badge-row"><span class="today-badge">今日公告</span></div>' : ''}
      `,
    },
    {
      key: 'secName',
      label: '公司 / 代码',
      render: (row) => `
        <div>${escapeHtml(row.secName || row.stockName || '--')}</div>
        <div class="muted mono-text">${escapeHtml(row.secCode || '--')}</div>
      `,
    },
    {
      key: 'dealType',
      label: '交易类型',
      render: (row) => `
        <div>${escapeHtml(row.dealType || '--')}</div>
        <div class="muted">${row.isCore ? '<span class="core-badge">核心</span>' : ''}</div>
      `,
    },
    { key: 'offerPrice', label: '报价', render: (row) => formatNumber(row.offerPrice, 2) },
    { key: 'latestPrice', label: '目标现价', className: (row) => statusClass(readMergerLatestPrice(row)), render: (row) => formatNumber(readMergerLatestPrice(row), 2) },
    { key: 'premiumRate', label: '报价溢价', className: (row) => statusClass(readMergerPremiumRate(row)), render: (row) => formatPercent(readMergerPremiumRate(row), 2) },
    { key: 'links', label: '链接', render: (row) => buildMergerLinks(row) },
  ];
}

function renderEventArbitrageSummaryDetail(row) {
  return `
    <div class="detail-grid single-column">
      <div class="detail-item full-span">
        <div class="detail-label">摘要</div>
        <div class="detail-value">${escapeHtml(row?.summary || '--')}</div>
      </div>
    </div>
  `;
}

function renderEventArbitrageRemarkDetail(row, value) {
  return `
    <div class="detail-grid single-column">
      <div class="detail-item full-span">
        <div class="detail-label">备注</div>
        <div class="detail-value">${escapeHtml(value || '--')}</div>
      </div>
    </div>
  `;
}

function renderEventArbitrageTableView(options) {
  const { title, note, tableKey, tableKind, rows, columns, emptyMessage, rowClassName, detailRenderer, detailMode } = options;
  const status = readEventArbitrageStatus(options.categoryKey || '');
  return `
    <div class="list-card">
      <div class="module-toolbar">
        <div>
          <h3>${escapeHtml(title)}</h3>
          <div class="section-note">${escapeHtml(note)}</div>
        </div>
        <div class="panel-meta">
          <span>来源状态 ${escapeHtml(eventArbStatusLabel(status.status))}</span>
          <span>数据条数 ${escapeHtml(formatInt(rows.length))}</span>
        </div>
      </div>
      ${renderPaginatedTable({
        tableKind,
        tableKey,
        columns,
        rows,
        emptyMessage,
        rowClassName,
        detailRenderer,
        detailMode,
      })}
    </div>
  `;
}

function renderEventArbitrageSubview() {
  const subtab = readEventArbitrageSubview();
  if (subtab === 'hk_private') {
    return renderEventArbitrageTableView({
      title: '港股套利',
      note: '只保留抓取到的核心字段与源侧原始公告链接。',
      categoryKey: 'hk_private',
      tableKey: 'eventArbHk',
      tableKind: 'merger',
      rows: readEventArbitrageCategoryRows('hk_private'),
      columns: buildEventArbHkColumns(),
      emptyMessage: '当前没有港股套利数据',
      detailRenderer: (row) => renderEventArbitrageRemarkDetail(row, row?.summary),
      detailMode: 'always',
    });
  }
  if (subtab === 'cn_private') {
    return renderEventArbitrageTableView({
      title: '中概私有',
      note: '公开接口为空时保持空表，不使用假数据填充。',
      categoryKey: 'cn_private',
      tableKey: 'eventArbCn',
      tableKind: 'merger',
      rows: readEventArbitrageCategoryRows('cn_private'),
      columns: buildEventArbCnColumns(),
      emptyMessage: '当前公开源没有中概股私有化数据',
      detailRenderer: (row) => renderEventArbitrageRemarkDetail(row, row?.feesHint || row?.summary),
      detailMode: 'always',
    });
  }
  if (subtab === 'a_event') {
    return renderEventArbitrageTableView({
      title: 'A股套利',
      note: '主表展示安全边际价、现金选择权与公开公告链接。',
      categoryKey: 'a_event',
      tableKey: 'eventArbA',
      tableKind: 'merger',
      rows: readEventArbitrageCategoryRows('a_event'),
      columns: buildEventArbAColumns(),
      emptyMessage: '当前没有 A 股事件套利数据',
      detailRenderer: (row) => renderEventArbitrageSummaryDetail(row),
      detailMode: 'always',
    });
  }
  if (subtab === 'announcement_pool') {
    const rows = [...readEventArbitrageCategoryRows('announcement_pool')].sort((a, b) => readAnnouncementSortValue(b) - readAnnouncementSortValue(a));
    return renderEventArbitrageTableView({
      title: '最新公告',
      note: '用于辅助校验和深挖，不再作为默认主列表。',
      categoryKey: 'announcement_pool',
      tableKey: 'eventArbAnnouncement',
      tableKind: 'merger',
      rows,
      columns: buildEventArbAnnouncementColumns(),
      emptyMessage: '当前没有公告池数据',
      rowClassName: (row) => (isTodayAnnouncement(row) ? 'merger-row-today' : ''),
    });
  }
  const status = readEventArbitrageStatus('rights_issue');
  return `
    <div class="list-card disabled-card">
      <h3>港供套利</h3>
      <div class="section-note">当前按“零登录”约束不接入该页。现有公开源需要登录或权限校验，第一阶段只保留信息架构和禁用态说明。</div>
      <div class="slim-note detail-note">状态：${escapeHtml(eventArbStatusLabel(status.status))} / 最近更新 ${escapeHtml(formatDate(status.updateTime || readUpdateTime('merger')))}</div>
    </div>
  `;
}

function renderMergerPanel() {
  const panel = dom.tabPanels.merger;
  const resource = state.resources.merger;
  if (!panel) return;

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading('事件套利正在聚合公开数据');
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError('事件套利加载失败', resource.error?.message);
    return;
  }

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">事件套利</div>
          <div class="section-note">统一承接港股私有化、中概私有化、A股套利与公告池辅助校验。</div>
        </div>
        <div class="panel-meta">
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime('merger')))}</span>
          <span>${escapeHtml(readEventArbitrageData().servedFromCache ? '当前显示缓存聚合结果' : '当前显示实时聚合结果')}</span>
        </div>
      </div>
      ${renderEventArbitrageSubtabs()}
      ${renderEventArbitrageSubview()}
      ${renderModuleFootnote('merger')}
    </div>
  `;
}

function buildMergerLinks(row) {
  const links = [];
  if (row.announcementUrl) {
    links.push(`<a href="${escapeHtml(row.announcementUrl)}" target="_blank" rel="noreferrer">公告页</a>`);
  }
  if (row.pdfUrl) {
    links.push(`<a href="${escapeHtml(row.pdfUrl)}" target="_blank" rel="noreferrer">PDF</a>`);
  }
  return links.length ? links.join(' / ') : '--';
}

function readAnnouncementSortValue(row) {
  const timestamp = toNumber(row?.announcementTime);
  if (timestamp !== null) return timestamp;
  const normalized = normalizeDateKey(row?.announcementDate);
  return normalized ? Number(normalized.replaceAll('-', '')) : 0;
}

function readAnnouncementLabel(row) {
  const timestamp = toNumber(row?.announcementTime);
  if (timestamp !== null) return formatDate(timestamp);
  return formatDateOnly(row?.announcementDate);
}

function isTodayAnnouncement(row) {
  if (normalizeDateKey(row?.announcementDate) === todayKey()) return true;
  const timestamp = toNumber(row?.announcementTime);
  if (timestamp === null) return false;
  return normalizeDateKey(new Date(timestamp).toISOString()) === todayKey();
}

function renderStackItems(rows) {
  if (!rows.length) {
    return '<div class="empty-state"><div>暂无数据</div></div>';
  }

  return `
    <div class="stack-list">
      ${rows
        .map(
          (row) => `
            <div class="stack-row">
              <div class="item-main">
                <div class="item-title">
                  ${escapeHtml(row.title)}
                  ${row.subtitle ? `<span class="item-subtitle">${escapeHtml(row.subtitle)}</span>` : ''}
                </div>
              </div>
              <div class="item-value ${escapeHtml(row.valueClass || '')}">${escapeHtml(row.value)}</div>
            </div>
          `
        )
        .join('')}
    </div>
  `;
}

function simpleEmpty(message) {
  return `<div class="empty-state"><div>${escapeHtml(message)}</div></div>`;
}

function moduleLoading(message) {
  return `
    <div class="module-shell">
      <div class="loading-state">
        <div>${escapeHtml(message)}</div>
        <div class="loading-line"></div>
        <div class="loading-line short"></div>
      </div>
    </div>
  `;
}

function moduleError(title, message) {
  return `
    <div class="module-shell">
      <div class="error-state">
        <div>${escapeHtml(title)}</div>
        <div class="muted">${escapeHtml(message || '请稍后重试')}</div>
      </div>
    </div>
  `;
}

function moduleEmpty(message) {
  return `
    <div class="module-shell">
      <div class="empty-state">
        <div>${escapeHtml(message)}</div>
      </div>
    </div>
  `;
}

function highestBy(rows, key) {
  return [...rows].sort((a, b) => (readNumberByPath(b, key) ?? -Infinity) - (readNumberByPath(a, key) ?? -Infinity))[0] || null;
}

function readPath(source, path) {
  return String(path)
    .split('.')
    .reduce((acc, key) => (acc && typeof acc === 'object' ? acc[key] : undefined), source);
}

function readNumberByPath(source, path) {
  return toNumber(readPath(source, path));
}

function computeConvertSpread(row) {
  const convertValue = toNumber(row.convertValue);
  const price = toNumber(row.price);
  if (convertValue === null || price === null || price === 0) return null;
  return ((convertValue - price) / price) * 100;
}

// 可转债主表双值列统一按展示金额口径计算，避免前端重复散落公式。
function computeConvertiblePremiumAmount(row) {
  const price = toNumber(row?.price);
  const convertValue = toNumber(row?.convertValue);
  if (price === null || convertValue === null) return null;
  return price - convertValue;
}



function computeConvertibleTheoreticalPremiumAmount(row) {
  const price = toNumber(row?.price);
  const theoreticalPrice = toNumber(row?.theoreticalPrice);
  if (price === null || theoreticalPrice === null) return null;
  return price - theoreticalPrice;
}

function readConvertibleBoardLabel(row) {
  const code = String(row?.stockCode || "").trim();
  if (code.startsWith("688")) return "科创板";
  if (code.startsWith("300") || code.startsWith("301")) return "创业板";
  return "主板";
}

function readPureBondBase(row) {
  return toNumber(row?.pureBondValue);
}

function computePureBondPremiumRate(row) {
  const bondBase = readPureBondBase(row);
  const price = toNumber(row.price);
  if (bondBase === null || bondBase <= 0 || price === null) return null;
  return ((price / bondBase) - 1) * 100;
}

function computeOptionTheoreticalValue(row) {
  const callValue = toNumber(row.callOptionValue);
  const putValue = toNumber(row.putOptionValue);
  const pricingFormula = String(row?.pricingFormula || '').trim();
  if (pricingFormula === 'bond+callspread' && callValue !== null) {
    return callValue;
  }
  if (callValue !== null || putValue !== null) {
    return (callValue ?? 0) - (putValue ?? 0);
  }
  const theoreticalPrice = toNumber(row.theoreticalPrice);
  const bondBase = readPureBondBase(row);
  if (theoreticalPrice === null || bondBase === null) return null;
  return theoreticalPrice - bondBase;
}

function computeImplicitOptionValue(row) {
  const price = toNumber(row?.price);
  const bondBase = readPureBondBase(row);
  if (price === null || bondBase === null) return null;
  return price - bondBase;
}

function computeOptionDiscountRate(row) {
  const theoreticalOptionValue = computeOptionTheoreticalValue(row);
  const implicitOptionValue = computeImplicitOptionValue(row);
  if (theoreticalOptionValue === null || implicitOptionValue === null) return null;
  if (theoreticalOptionValue === 0) return null;
  return (implicitOptionValue / theoreticalOptionValue - 1) * 100;
}

function computeOptionValueGap(row) {
  const theoreticalOptionValue = computeOptionTheoreticalValue(row);
  const implicitOptionValue = computeImplicitOptionValue(row);
  if (theoreticalOptionValue === null || implicitOptionValue === null) return null;
  return theoreticalOptionValue - implicitOptionValue;
}

function readScaledMoneyValue(source, options = {}) {
  const rawValue = readFirstNumberValue(source, options.raw || []);
  if (rawValue !== null) return rawValue;
  const wanValue = readFirstNumberValue(source, options.wan || []);
  if (wanValue !== null) return wanValue * 10000;
  const yiValue = readFirstNumberValue(source, options.yi || []);
  if (yiValue !== null) return yiValue * 100000000;
  return null;
}

function readCbArbSmallRedemptionYield(row) {
  return readFirstNumberValue(row, ['redemptionYield', 'smallRedemptionYield', 'rigidRedemptionYield']);
}

function readCbArbSmallRedemptionExpectedDurationYears(row) {
  return readFirstNumberValue(row, ['expectedDurationYears', 'expectedDuration', 'expectedHoldingYears', 'redemptionDurationYears']);
}

function readCbArbSmallRedemptionRemainingYears(row) {
  return readFirstNumberValue(row, ['remainingYears', 'remainingTermYears', 'remainingDurationYears']);
}

function readCbArbSmallRedemptionAnnualizedYield(row) {
  return readFirstNumberValue(row, ['annualizedYield', 'smallRedemptionAnnualizedYield', 'annualizedRedemptionYield']);
}

function readCbArbSmallRedemptionRemainingSizeYi(row) {
  return readFirstNumberValue(row, ['remainingSizeYi', 'remainingScaleYi', 'remainingIssueSizeYi', 'balanceYi', 'outstandingSizeYi']);
}

function readCbArbSmallRedemptionAmount(row) {
  return readScaledMoneyValue(row, {
    raw: ['redemptionAmount', 'smallRedemptionAmount', 'rigidRedemptionAmount'],
    wan: ['redemptionAmountWan', 'smallRedemptionAmountWan', 'rigidRedemptionAmountWan'],
    yi: ['redemptionAmountYi', 'smallRedemptionAmountYi'],
  });
}

function readCbArbSmallRedemptionTotal(row) {
  return readScaledMoneyValue(row, {
    raw: ['redemptionTotal', 'smallRedemptionTotal', 'rigidRedemptionTotal'],
    wan: ['redemptionTotalWan', 'smallRedemptionTotalWan'],
    yi: ['redemptionTotalYi', 'smallRedemptionTotalYi'],
  });
}

function readCbArbLiabilityExposureYi(row) {
  return readFirstNumberValue(row, ['liabilityExposureYi', 'debtExposureYi', 'netDebtExposureYi']);
}

function readCbArbInterestBearingDebtYi(row) {
  return readFirstNumberValue(row, ['interestBearingDebtYi', 'interestDebtYi', 'financials.interestBearingDebtYi']);
}

function readCbArbBroadCashYi(row) {
  return readFirstNumberValue(row, ['broadCashYi', 'generalizedCashYi', 'generalCashYi', 'financials.broadCashYi']);
}

function readCbArbNetAssetYi(row) {
  return readFirstNumberValue(row, ['netAssetYi', 'netAssetsYi', 'equityYi', 'financials.netAssetYi']);
}

function readCbArbSmallRedemptionOptionValue(row) {
  return readFirstNumberValue(row, [
    'smallRedemptionOptionValue',
    'redemptionOptionValue',
    'optionValue',
    'theoreticalOptionValue',
    'optionValueAmount',
  ]);
}

function readCbArbSmallRedemptionOptionYield(row) {
  return readFirstNumberValue(row, [
    'smallRedemptionOptionYield',
    'optionYield',
    'redemptionOptionYield',
  ]);
}

function readCbArbSmallRedemptionOptionAnnualizedYield(row) {
  return readFirstNumberValue(row, [
    'smallRedemptionOptionAnnualizedYield',
    'optionAnnualizedYield',
    'redemptionOptionAnnualizedYield',
  ]);
}

function readCbArbSmallRedemptionTotalAnnualizedYield(row) {
  return readFirstNumberValue(row, [
    'smallRedemptionTotalAnnualizedYield',
    'totalAnnualizedYield',
  ]);
}

function readCbArbHolderCount(row) {
  return readFirstNumberValue(row, ['holderCount', 'bondHolderCount', 'convertibleHolderCount']);
}

function renderCbArbLiabilityExposureCell(row) {
  return `
    <div class="cb-arb-liability-stack">
      <div class="table-cell-primary">${escapeHtml(formatYiValue(readCbArbLiabilityExposureYi(row), 2))}</div>
      <div class="table-cell-subtle">\u6709\u606f\u8d1f\u503a ${escapeHtml(formatYiValue(readCbArbInterestBearingDebtYi(row), 2))}</div>
      <div class="table-cell-subtle">\u5e7f\u4e49\u73b0\u91d1 ${escapeHtml(formatYiValue(readCbArbBroadCashYi(row), 2))}</div>
    </div>
  `;
}

function renderCbArbExpectedDurationCell(row) {
  return renderCompactCell(
    escapeHtml(formatRemainingTerm(readCbArbSmallRedemptionExpectedDurationYears(row))),
    [`\u5269\u4f59\u671f\u9650 ${escapeHtml(formatRemainingTerm(readCbArbSmallRedemptionRemainingYears(row)))}`]
  );
}

function bestMonitorYield(row) {
  return Math.max(toNumber(row?.stockYieldRate) ?? -Infinity, toNumber(row?.cashYieldRate) ?? -Infinity);
}

function buildConvertibleDetailItems(row) {
  return [
    { label: '转债涨跌幅', value: formatPercent(row.changePercent, 2) },
    { label: '正股涨跌幅', value: formatPercent(row.stockChangePercent, 2) },
    { label: '转股价', value: formatNumber(row.convertPrice, 2) },
    { label: '转股价值', value: formatNumber(row.convertValue, 2) },
    { label: '成交额(亿)', value: formatNumber(row.turnoverAmountYi, 2) },
    { label: '剩余规模(亿)', value: formatNumber(row.remainingSizeYi, 2) },
    { label: '评级', value: row.rating || '--' },
    { label: '剩余年限', value: formatNumber(row.remainingYears, 2) },
    { label: '上市日', value: formatDateOnly(row.listingDate) },
    { label: '转股起始日', value: formatDateOnly(row.convertStartDate) },
  ];
}

function buildPremiumDetailItems(type, row) {
  const config = getPremiumConfig(type);
  return [
    { label: 'A股代码', value: row.aCode || '--' },
    { label: 'A股名称', value: row.aName || '--' },
    { label: config.peerCodeLabel, value: row[config.peerCodeKey] || '--' },
    { label: config.peerNameLabel, value: row[config.peerNameKey] || '--' },
    { label: config.peerMarketPriceLabel, value: formatNumber(row[config.peerMarketPriceKey], 2) },
    { label: '对手人民币价', value: formatNumber(row[config.peerPriceKey], 2) },
    { label: '价差', value: formatSignedNumber(computePremiumGap(row, config.peerPriceKey), 2) },
    { label: '可用样本数', value: formatInt(row.historyCount) },
    { label: '样本起始', value: formatDateOnly(row.historyStartDate) },
    { label: '样本结束', value: formatDateOnly(row.historyEndDate) },
  ];
}

function hasMonitorStockLeg(row) {
  return (toNumber(row?.stockRatio) ?? 0) !== 0 || (toNumber(row?.cashDistributionCny ?? row?.cashDistribution) ?? 0) !== 0;
}

function hasMonitorCashLeg(row) {
  return (toNumber(row?.cashPayout ?? row?.cashOptionPrice) ?? 0) !== 0;
}

function buildMonitorPricingText(row) {
  if (!hasMonitorStockLeg(row)) return '未配置股票腿';
  return [
    formatNumber(row.acquirerPrice, 3),
    '×',
    formatNumber(row.stockRatio, 3),
    '×',
    formatNumber(row.safetyFactor, 3),
    '+',
    formatNumber(row.cashDistributionCny, 3),
  ].join(' ');
}

function summarizeMonitorError(message) {
  const text = String(message || '').trim();
  if (!text) return '请稍后重试，或点击“刷新”重新拉取。';

  if (text.includes('python: not found') || text.includes('python3: not found')) {
    return '服务器缺少 Python 运行时，请使用部署链路自动安装并重启服务。';
  }

  if (text.includes("No module named 'akshare'") || text.includes('No module named akshare') || text.includes('missing python modules')) {
    return '服务器缺少 Python 依赖（akshare / pandas / requests），请执行部署脚本安装 requirements 后重试。';
  }

  return text.replace(/\s+/g, ' ').slice(0, 180);
}

function readMonitorTargetPrice(row) {
  return toNumber(row?.targetPrice ?? row?.targetLastPrice ?? row?.targetNowPrice);
}

function buildMonitorDetailItems(row) {
  const stockLegEnabled = hasMonitorStockLeg(row);
  const cashLegEnabled = hasMonitorCashLeg(row);
  return [
    { label: '收购方股价', value: `¥${formatNumber(row.acquirerPrice, 3)}` },
    { label: '目标方股价', value: `¥${formatNumber(readMonitorTargetPrice(row), 3)}` },
    { label: '换股比例', value: formatNumber(row.stockRatio, 3) },
    { label: '安全系数', value: formatNumber(row.safetyFactor, 3) },
    { label: '现金对价', value: `¥${formatNumber(row.cashDistributionCny, 3)}` },
    { label: '理论对价计算说明', value: buildMonitorPricingText(row) },
    { label: '股票腿理论对价', value: stockLegEnabled ? `¥${formatNumber(row.stockPayout, 3)}` : '未配置股票腿' },
    { label: '股票腿价差', value: stockLegEnabled ? formatSignedNumber(row.stockSpread, 3) : '未配置股票腿' },
    { label: '现金选择权', value: cashLegEnabled ? `¥${formatNumber(row.cashPayout, 3)}` : '未配置现金腿' },
    { label: '现金腿价差', value: cashLegEnabled ? formatSignedNumber(row.cashSpread, 3) : '未配置现金腿' },
    { label: '备注', value: row.note || '无' },
  ];
}

function readMergerLatestPrice(row) {
  return toNumber(row?.latestPrice ?? row?.stockPrice ?? row?.price);
}

function readMergerPremiumRate(row) {
  const latestPrice = readMergerLatestPrice(row);
  const offerPrice = toNumber(row?.offerPrice ?? row?.bidPrice);
  if (latestPrice === null || offerPrice === null || latestPrice === 0) return null;
  return ((offerPrice - latestPrice) / latestPrice) * 100;
}

function buildMergerDetailItems(row) {
  return [
    { label: '公告标题', value: row.title || '--' },
    { label: '关键词', value: row.searchKeyword || '--' },
    { label: '公告ID', value: row.announcementId || '--' },
    { label: '公告日期', value: formatDateOnly(row.announcementDate) },
    { label: '公告链接', value: row.announcementUrl || '--' },
    { label: 'PDF链接', value: row.pdfUrl || '--' },
  ];
}

if (document.readyState === 'loading') {
  window.addEventListener('DOMContentLoaded', () => {
    void bootstrap();
  });
} else {
  void bootstrap();
}
