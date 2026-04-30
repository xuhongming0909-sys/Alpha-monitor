// AI-SUMMARY: 看板 UI 常量：端点、Tab 序列、表格配置、样式默认值
// 对应 INDEX.md §9 文件摘要索引

'use strict';

const API_BASE = (function resolveApiBaseFromSearch() {
  if (typeof window === 'undefined' || window.location.protocol !== 'file:') return '';
  const params = new URLSearchParams(window.location.search);
  const raw = params.get('apiBase') || '';
  return raw.endsWith('/') ? raw.slice(0, -1) : raw;
})();

function toNumber(val) {
  const n = Number(val);
  return Number.isFinite(n) ? n : null;
}

function formatPercent(value, decimals) {
  if (value === null || value === undefined) return '-';
  const n = toNumber(value);
  if (n === null) return '-';
  return `${(n * 100).toFixed(decimals)}%`;
}

const PAGE_SIZE = 50;
const CRITICAL_CACHE_REVALIDATION_KEYS = ['exchangeRate', 'cbArb', 'ah', 'ab'];
const DEFAULT_AUTO_REFRESH_CONFIG = Object.freeze({
  enabled: true,
  intervalMs: 30 * 1000,
  mode: 'status',
  currentTabOnly: true,
  reloadDataOnCacheChange: true,
});
const DEFAULT_TABLE_UI_CONFIG = Object.freeze({
  desktopFontPx: 14,
  desktopHeaderFontPx: 14,
  desktopLineHeight: 1.58,
  desktopCellPaddingY: 10,
  desktopCellPaddingX: 12,
  tabletFontPx: 13,
  minWidthByKind: {
    subscription: 1180,
    convertible: 1340,
    premium: 1240,
    monitor: 1320,
    dividend: 1100,
    merger: 1280,
    lof: 1680,
  },
});

const ENDPOINTS = {
  uiConfig: '/api/dashboard/ui-config',
  resourceStatus: '/api/dashboard/resource-status',
  health: '/api/health',
  exchangeRate: '/api/market/exchange-rate',
  ipo: '/api/market/ipo',
  bonds: '/api/market/convertible-bonds',
  cbArb: '/api/market/convertible-bond-arbitrage',
  cbRightsIssue: '/api/market/cb-rights-issue',
  lofArb: '/api/market/lof-arbitrage',
  ah: '/api/market/ah',
  ab: '/api/market/ab',
  monitor: '/api/monitors',
  stockSearch: '/api/stock/search',
  dividend: '/api/dividend?action=portfolio',
  dividendRefresh: '/api/dividend?action=refresh',
  merger: '/api/market/event-arbitrage',
  pushConfig: '/api/push/config',
  cbArbPushConfig: '/api/push/cb-arbitrage-config',
  cbRightsIssuePushConfig: '/api/push/cb-rights-issue-config',
  lofArbPushConfig: '/api/push/lof-arbitrage-config',
};

const TAB_SEQUENCE = ['cb-arb', 'ah', 'ab', 'lof-arb', 'monitor', 'dividend', 'merger', 'cb-rights-issue'];
const CB_ARB_SUBTAB_SEQUENCE = ['home', 'small-redemption'];
const CB_RIGHTS_ISSUE_SUBTAB_SEQUENCE = ['apply', 'ambush', 'wait'];
const CB_RIGHTS_ISSUE_MARKET_SUBTAB_SEQUENCE = ['sh', 'sz'];
const CB_RIGHTS_ISSUE_TABLE_KEYS = [
  'cbRightsIssueShApply',
  'cbRightsIssueShAmbush',
  'cbRightsIssueShWait',
  'cbRightsIssueSzApply',
  'cbRightsIssueSzAmbush',
  'cbRightsIssueSzWait',
];
const EVENT_ARB_SUBTAB_SEQUENCE = ['a_event', 'hk_private', 'cn_private', 'rights_issue', 'announcement_pool'];
const TAB_PRIMARY_RESOURCE_KEYS = Object.freeze({
  'cb-arb': ['cbArb'],
  ah: ['ah'],
  ab: ['ab'],
  'lof-arb': ['lofArb', 'lofArbPushConfig'],
  monitor: ['monitor'],
  dividend: ['dividend'],
  merger: ['merger'],
  'cb-rights-issue': ['cbRightsIssue'],
});
const DATASET_STATUS_RESOURCE_KEYS = Object.freeze(['exchangeRate', 'ipo', 'bonds', 'cbArb', 'ah', 'ab', 'lofArb', 'merger', 'cbRightsIssue']);
const MONITOR_MARKET_OPTIONS = ['A', 'H', 'B'];
const MONITOR_CURRENCY_OPTIONS = ['CNY', 'HKD', 'USD'];
const PUSH_MODULE_LABELS = {
  ahab: 'AH/AB',
  subscription: '打新',
  cbArb: '转债',
  monitor: '监控',
  dividend: '分红',
  eventArb: '事件套利',
};
const MONITOR_LOOKUP_DEBOUNCE_MS = 280;

const PREMIUM_SORT_OPTIONS = {
  premium: {
    label: '按溢价率排序',
    valueLabel: '溢价率',
    sort: (a, b) => (toNumber(b.premium) ?? -Infinity) - (toNumber(a.premium) ?? -Infinity),
    readValue: (row) => formatPercent(row?.premium, 2),
  },
  percentile: {
    label: '按近三年可用样本分位排序',
    valueLabel: '近三年可用样本分位',
    sort: (a, b) => (toNumber(b.percentile) ?? -Infinity) - (toNumber(a.percentile) ?? -Infinity),
    readValue: (row) => formatPercent(row?.percentile, 2),
  },
};

const SUBSCRIPTION_STAGES = [
  { key: 'subscribe', label: '今日申购', className: 'stage-subscribe' },
  { key: 'payment', label: '今日中签缴款', className: 'stage-payment' },
  { key: 'listing', label: '今日上市', className: 'stage-listing' },
];

const TABLE_DEFAULTS = {
  cbArb: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbArbSmallRedemption: { sortKey: 'redemptionYield', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  ah: { sortKey: 'premium', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  ab: { sortKey: 'premium', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  monitor: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  dividend: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  merger: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  lofArb: { sortKey: 'premiumRate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbRightsIssueShApply: { sortKey: 'recordDate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbRightsIssueShAmbush: { sortKey: 'marginReturnRate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbRightsIssueShWait: { sortKey: 'progressDate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbRightsIssueSzApply: { sortKey: 'recordDate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbRightsIssueSzAmbush: { sortKey: 'expectedReturnRate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  cbRightsIssueSzWait: { sortKey: 'progressDate', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  eventArbHk: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  eventArbCn: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  eventArbA: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
  eventArbAnnouncement: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE, searchQuery: '' },
};

const TABLE_SEARCH_CONFIG = Object.freeze({
  cbArb: {
    placeholder: '搜索转债代码/名称、正股代码/名称',
    hint: '可按转债代码、转债名称、正股代码、正股名称搜索',
    fields: ['code', 'bondName', 'stockCode', 'stockName'],
  },
  cbArbSmallRedemption: {
    placeholder: '搜索转债代码/名称、正股代码/名称',
    hint: '可按转债代码、转债名称、正股代码、正股名称搜索',
    fields: ['code', 'bondName', 'stockCode', 'stockName'],
  },
  ah: {
    placeholder: '搜索A股/H股代码或名称',
    hint: '可按A股代码、A股名称、H股代码、H股名称搜索',
    fields: ['aCode', 'aName', 'hCode', 'hName'],
  },
  ab: {
    placeholder: '搜索A股/B股代码或名称',
    hint: '可按A股代码、A股名称、B股代码、B股名称搜索',
    fields: ['aCode', 'aName', 'bCode', 'bName'],
  },
  lofArb: {
    placeholder: '搜索LOF代码、名称或相关指数',
    hint: '可按LOF代码、LOF名称、相关指数搜索',
    fields: ['code', 'name', 'indexName'],
  },
  cbRightsIssueShApply: {
    placeholder: '搜索正股代码、名称或方案进展',
    hint: '可按正股代码、正股名称、方案进展搜索',
    fields: ['stockCode', 'stockName', 'progressName'],
  },
  cbRightsIssueShAmbush: {
    placeholder: '搜索正股代码、名称或方案进展',
    hint: '可按正股代码、正股名称、方案进展搜索',
    fields: ['stockCode', 'stockName', 'progressName'],
  },
  cbRightsIssueShWait: {
    placeholder: '搜索正股代码、名称或方案进展',
    hint: '可按正股代码、正股名称、方案进展搜索',
    fields: ['stockCode', 'stockName', 'progressName'],
  },
  cbRightsIssueSzApply: {
    placeholder: '搜索正股代码、名称或方案进展',
    hint: '可按正股代码、正股名称、方案进展搜索',
    fields: ['stockCode', 'stockName', 'progressName'],
  },
  cbRightsIssueSzAmbush: {
    placeholder: '搜索正股代码、名称或方案进展',
    hint: '可按正股代码、正股名称、方案进展搜索',
    fields: ['stockCode', 'stockName', 'progressName'],
  },
  cbRightsIssueSzWait: {
    placeholder: '搜索正股代码、名称或方案进展',
    hint: '可按正股代码、正股名称、方案进展搜索',
    fields: ['stockCode', 'stockName', 'progressName'],
  },
});

// Re-export helpers needed by dashboard_page.js
function normalizePositiveNumber(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function formatNumber(value, decimals) {
  if (value === null || value === undefined) return '-';
  const n = toNumber(value);
  if (n === null) return '-';
  return n.toFixed(decimals);
}

function formatTimestamp(value) {
  if (!value) return '-';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '-';
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

function safeGet(obj, ...keys) {
  let cur = obj;
  for (const k of keys) {
    if (cur == null || typeof cur !== 'object') return undefined;
    cur = cur[k];
  }
  return cur;
}

module.exports = {
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
  // helpers
  toNumber,
  formatPercent,
  formatNumber,
  formatTimestamp,
  normalizePositiveNumber,
  safeGet,
};