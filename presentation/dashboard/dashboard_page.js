'use strict';

const API_BASE = window.location.protocol === 'file:' ? 'http://127.0.0.1:5000' : '';
const PAGE_SIZE = 50;

const ENDPOINTS = {
  exchangeRate: '/api/market/exchange-rate',
  ipo: '/api/market/ipo',
  bonds: '/api/market/convertible-bonds',
  cbArb: '/api/market/convertible-bond-arbitrage',
  ah: '/api/market/ah',
  ab: '/api/market/ab',
  monitor: '/api/monitors',
  dividend: '/api/dividend?action=refresh',
  merger: '/api/market/merger',
  pushConfig: '/api/push/config',
};

const TAB_SEQUENCE = ['cb-arb', 'ah', 'ab', 'monitor', 'dividend', 'merger'];

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
  cbArb: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE },
  ah: { sortKey: 'premium', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE },
  ab: { sortKey: 'premium', sortDir: 'desc', page: 1, pageSize: PAGE_SIZE },
  monitor: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE },
  dividend: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE },
  merger: { sortKey: null, sortDir: 'desc', page: 1, pageSize: PAGE_SIZE },
};

const state = {
  activeTab: 'cb-arb',
  eventsBound: false,
  savingPush: false,
  expandedRows: {
    cbArb: {},
    ah: {},
    ab: {},
    monitor: {},
    merger: {},
  },
  tables: {
    cbArb: createTableState('cbArb'),
    ah: createTableState('ah'),
    ab: createTableState('ab'),
    monitor: createTableState('monitor'),
    dividend: createTableState('dividend'),
    merger: createTableState('merger'),
  },
  resources: {
    exchangeRate: resourceState(),
    ipo: resourceState(),
    bonds: resourceState(),
    cbArb: resourceState(),
    ah: resourceState(),
    ab: resourceState(),
    monitor: resourceState(),
    dividend: resourceState(),
    merger: resourceState(),
    pushConfig: resourceState(),
  },
};

const dom = {
  tabButtons: Array.from(document.querySelectorAll('.tab-button')),
  tabPanels: {
    'cb-arb': document.getElementById('panel-cb-arb'),
    ah: document.getElementById('panel-ah'),
    ab: document.getElementById('panel-ab'),
    monitor: document.getElementById('panel-monitor'),
    dividend: document.getElementById('panel-dividend'),
    merger: document.getElementById('panel-merger'),
  },
  statusLine: document.getElementById('status-line'),
  statusUpdateText: document.getElementById('status-update-text'),
  lastRefreshText: document.getElementById('last-refresh-text'),
  subscriptionSummary: document.getElementById('subscription-summary'),
  pushStateText: document.getElementById('push-state-text'),
  pushForm: document.getElementById('push-form'),
  pushTime1: document.getElementById('push-time-1'),
  pushTime2: document.getElementById('push-time-2'),
  pushTime3: document.getElementById('push-time-3'),
  savePushButton: document.getElementById('save-push-button'),
  reloadDataButton: document.getElementById('reload-data-button'),
  toast: document.getElementById('toast'),
};

function createTableState(key) {
  return { ...TABLE_DEFAULTS[key] };
}

function resourceState() {
  return {
    status: 'idle',
    data: null,
    error: null,
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

function readResourceArray(key) {
  return readArray(state.resources[key].data);
}

function readResourceObject(key) {
  return readObject(state.resources[key].data);
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

function todayKey() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function readUpdateTime(key) {
  const payload = readObject(state.resources[key].data);
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

async function loadResource(key, endpoint, onRender) {
  state.resources[key].status = 'loading';
  state.resources[key].error = null;
  onRender();

  try {
    const payload = await fetchJson(endpoint);
    state.resources[key].status = 'ready';
    state.resources[key].data = payload;
    state.resources[key].error = null;
  } catch (error) {
    state.resources[key].status = 'error';
    state.resources[key].error = error;
    state.resources[key].data = null;
  }

  onRender();
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
    });
  });

  dom.reloadDataButton?.addEventListener('click', () => {
    void reloadAllData();
  });

  dom.pushForm?.addEventListener('submit', async (event) => {
    event.preventDefault();
    await savePushConfig();
  });

  document.addEventListener('click', (event) => {
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

    const expandTarget = event.target.closest('.expand-button[data-table-key][data-row-id]');
    if (expandTarget) {
      const tableKey = expandTarget.dataset.tableKey;
      const rowId = expandTarget.dataset.rowId;
      toggleExpandedState(tableKey, rowId);
      if (tableKey === 'cbArb') return renderConvertibleBondPanel();
      if (tableKey === 'ah') return renderPremiumPanel('ah');
      if (tableKey === 'ab') return renderPremiumPanel('ab');
      if (tableKey === 'monitor') return renderMonitorPanel();
      if (tableKey === 'merger') return renderMergerPanel();
    }
  });

  state.eventsBound = true;
}

async function bootstrap() {
  bindEvents();
  renderAll();

  const renderHeaderOnly = () => {
    renderStatusLine();
    renderSubscriptionSummary();
    renderPushSettings();
  };

  const renderEverything = () => {
    renderHeaderOnly();
    renderActivePanel();
  };

  const tasks = [
    loadResource('exchangeRate', ENDPOINTS.exchangeRate, renderHeaderOnly),
    loadResource('ipo', ENDPOINTS.ipo, renderHeaderOnly),
    loadResource('bonds', ENDPOINTS.bonds, renderHeaderOnly),
    loadResource('pushConfig', ENDPOINTS.pushConfig, renderPushSettings),
    loadResource('cbArb', ENDPOINTS.cbArb, renderEverything),
    loadResource('ah', ENDPOINTS.ah, renderEverything),
    loadResource('ab', ENDPOINTS.ab, renderEverything),
    loadResource('monitor', ENDPOINTS.monitor, renderEverything),
    loadResource('dividend', ENDPOINTS.dividend, renderEverything),
    loadResource('merger', ENDPOINTS.merger, renderEverything),
  ];

  await Promise.allSettled(tasks);
  renderAll();
}

async function reloadAllData() {
  showToast('正在刷新页面数据');
  await bootstrap();
  showToast('页面数据已刷新');
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
    panel.classList.toggle('active', key === state.activeTab);
  });
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
      <span class="status-inline-item"><span>请确认</span><strong>本地服务已启动</strong></span>
    `;
    dom.statusUpdateText.textContent = '请先确认本地服务已经启动';
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
  dom.subscriptionSummary.innerHTML = renderSubscriptionTable(rows);

  const updateTime = maxUpdateTime(['ipo', 'bonds']);
  dom.lastRefreshText.textContent = updateTime ? `最近更新时间：${formatDate(updateTime)}` : '等待打新接口返回';
}

function buildTodaySubscriptionRows(ipoRows, bondRows) {
  const today = todayKey();
  const rows = [];

  const pushRow = (records, typeLabel, recordType) => {
    records.forEach((row) => {
      const stages = [];
      if (normalizeDateKey(row.subscribeDate) === today) stages.push(SUBSCRIPTION_STAGES[0]);
      if (normalizeDateKey(row.paymentDate) === today) stages.push(SUBSCRIPTION_STAGES[1]);
      if (normalizeDateKey(row.listingDate) === today) stages.push(SUBSCRIPTION_STAGES[2]);
      stages.forEach((stage) => {
        rows.push({
          stageLabel: stage.label,
          stageClassName: stage.className,
          typeLabel,
          name: row.name || row.bondName || row.stockName || '--',
          code: row.code || row.bondCode || row.stockCode || '--',
          subscribeDate: row.subscribeDate,
          paymentDisplayDate: row.lotteryDate || row.paymentDate,
          listingDate: row.listingDate,
          subscribeLimit: row.subscribeLimit,
          issueOrConvertLabel: recordType === 'ipo' ? '发行价' : '转股价',
          issueOrConvertValue: recordType === 'ipo' ? row.issuePrice : row.convertPrice,
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
      <td>
        <div>${escapeHtml(row.name)}</div>
        <div class="muted mono-text">${escapeHtml(row.code)}</div>
      </td>
      <td>${escapeHtml(formatDateOnly(row.subscribeDate))}</td>
      <td>${escapeHtml(formatDateOnly(row.paymentDisplayDate))}</td>
      <td>${escapeHtml(formatDateOnly(row.listingDate))}</td>
      <td>${escapeHtml(formatSubscribeLimit(row.subscribeLimit))}</td>
      <td>${escapeHtml(`${row.issueOrConvertLabel} ${formatNumber(row.issueOrConvertValue, 2)}`)}</td>
    </tr>
  `).join('')
    : `
      <tr>
        <td colspan="8">
          <div class="empty-state" style="min-height: 120px; padding: 20px;">今日无数据</div>
        </td>
      </tr>
    `;

  return `
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>当前阶段</th>
            <th>类型</th>
            <th>名称 / 代码</th>
            <th>申购日</th>
            <th>中签缴款日</th>
            <th>上市日</th>
            <th>申购上限</th>
            <th>发行价 / 转股价</th>
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
      <table>
        <thead>
          <tr>
            <th>当前阶段</th>
            <th>类型</th>
            <th>名称 / 代码</th>
            <th>申购日</th>
            <th>中签缴款日</th>
            <th>上市日</th>
            <th>申购上限</th>
            <th>发行价 / 转股价</th>
          </tr>
        </thead>
        <tbody>
          ${Array.from({ length: 3 }, () => `
            <tr>
              <td colspan="9">
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
    mergerTime: config?.mergerSchedule?.time || times[2] || "",
  };
}

function applyPushConfigToInputs(config = {}) {
  const next = resolvePushConfigTimes(config);
  if (dom.pushTime1) dom.pushTime1.value = next.mainTime1;
  if (dom.pushTime2) dom.pushTime2.value = next.mainTime2;
  if (dom.pushTime3) dom.pushTime3.value = next.mergerTime;
}

function buildPushStateText(config = {}) {
  const next = resolvePushConfigTimes(config);
  const mainText = config.enabled === false
    ? "主推送已关闭"
    : `主推送 ${[next.mainTime1, next.mainTime2].filter(Boolean).join(" / ") || "--"}`;
  const mergerText = config?.mergerSchedule?.enabled === false
    ? "收购私有专报已关闭"
    : `收购私有 ${next.mergerTime || "--"}`;
  const lastParts = [
    config.lastMainPushDate ? `最近主推送 ${config.lastMainPushDate}` : "",
    config.lastMergerReportDate ? `最近专报 ${config.lastMergerReportDate}` : "",
  ].filter(Boolean);
  return [mainText, mergerText, ...lastParts].join(" / ");
}

function renderPushSettings() {
  const resource = state.resources.pushConfig;
  if (!dom.pushStateText || !dom.savePushButton) return;

  dom.savePushButton.disabled = resource.status === "loading" || state.savingPush;
  if (dom.reloadDataButton) {
    dom.reloadDataButton.disabled = resource.status === "loading" || state.savingPush;
  }

  if (resource.status === "loading" && !resource.data) {
    dom.pushStateText.textContent = "正在读取推送配置";
    return;
  }

  const config = readPushConfigViewModel();
  const hasConfig = Boolean(config && Object.keys(config).length);

  if (resource.status !== "error" && hasConfig && !state.savingPush) {
    applyPushConfigToInputs(config);
  }

  if (resource.status === "error" && !hasConfig) {
    dom.pushStateText.textContent = "推送配置读取失败";
    return;
  }

  if (state.savingPush) {
    dom.pushStateText.textContent = "正在保存推送设置";
    return;
  }

  if (resource.status === "error") {
    dom.pushStateText.textContent = "推送配置读取失败，保留当前输入";
    return;
  }

  dom.pushStateText.textContent = buildPushStateText(config);
}

async function savePushConfig() {
  const config = readPushConfigViewModel();
  const time1 = dom.pushTime1?.value.trim();
  const time2 = dom.pushTime2?.value.trim();
  const time3 = dom.pushTime3?.value.trim();
  const validTimes = [time1, time2].filter(Boolean);

  if (!time1 || !time2 || !time3) {
    showToast("三个时间框都需要填写", true);
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
        mergerSchedule: {
          enabled: true,
          time: time3,
        },
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

function handleSortClick(tableKey, sortKey) {
  const columns = getTableColumns(tableKey);
  const column = columns.find((item) => item.key === sortKey && item.sortable);
  if (!column) return;

  const tableState = state.tables[tableKey];
  if (!tableState) return;

  const defaultDir = column.defaultDir || 'desc';
  if (tableState.sortKey === sortKey) {
    tableState.sortDir = tableState.sortDir === 'desc' ? 'asc' : 'desc';
  } else {
    tableState.sortKey = sortKey;
    tableState.sortDir = defaultDir;
  }
  tableState.page = 1;

  if (tableKey === 'cbArb') renderConvertibleBondPanel();
  if (tableKey === 'ah') renderPremiumPanel('ah');
  if (tableKey === 'ab') renderPremiumPanel('ab');
}

function handlePageClick(tableKey, action) {
  const tableState = state.tables[tableKey];
  if (!tableState) return;

  const totalRows = readTableSourceRows(tableKey).length;
  const totalPages = Math.max(1, Math.ceil(totalRows / tableState.pageSize));

  if (action === 'first') tableState.page = 1;
  if (action === 'prev') tableState.page = Math.max(1, tableState.page - 1);
  if (action === 'next') tableState.page = Math.min(totalPages, tableState.page + 1);
  if (action === 'last') tableState.page = totalPages;

  if (tableKey === 'cbArb') renderConvertibleBondPanel();
  if (tableKey === 'ah') renderPremiumPanel('ah');
  if (tableKey === 'ab') renderPremiumPanel('ab');
  if (tableKey === 'monitor') renderMonitorPanel();
  if (tableKey === 'dividend') renderDividendPanel();
  if (tableKey === 'merger') renderMergerPanel();
}

function readTableSourceRows(tableKey) {
  if (tableKey === 'cbArb') return readResourceArray('cbArb');
  if (tableKey === 'ah') return readResourceArray('ah');
  if (tableKey === 'ab') return readResourceArray('ab');
  if (tableKey === 'monitor') return readResourceArray('monitor');
  if (tableKey === 'dividend') return readResourceArray('dividend');
  if (tableKey === 'merger') return readResourceArray('merger');
  return [];
}

function getTableColumns(tableKey) {
  if (tableKey === 'cbArb') return buildConvertibleColumns();
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

function compareText(a, b) {
  return String(a).localeCompare(String(b), 'zh-CN');
}

function sortRowsByColumn(rows, column, direction) {
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
  const sortColumn = columns.find((item) => item.key === tableState.sortKey && item.sortable);
  const sortedRows = sortColumn ? sortRowsByColumn(rows, sortColumn, tableState.sortDir) : [...rows];
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
      if (column.key === 'index') return '<th>序号</th>';
      const labelText = escapeHtml(column.label);
      const label = column.group
        ? `${labelText}<span class="th-group-tag">${escapeHtml(column.group)}</span>`
        : labelText;

      if (!column.sortable) {
        return `<th>${label}</th>`;
      }

      const isActive = tableState.sortKey === column.key;
      const indicator = isActive ? (tableState.sortDir === 'desc' ? '↓' : '↑') : '↕';
      return `
        <th>
          <button
            type="button"
            class="sort-head ${isActive ? 'active' : ''}"
            data-table-key="${escapeHtml(tableKey)}"
            data-sort-key="${escapeHtml(column.key)}"
          >
            <span>${label}</span>
            <span class="sort-indicator">${escapeHtml(indicator)}</span>
          </button>
        </th>
      `;
    })
    .join('');

  const detailHead = includeDetails ? '<th>详情</th>' : '';
  return `<tr>${cells}${detailHead}</tr>`;
}

function renderTableCell(column, row, rowNumber) {
  if (column.key === 'index') {
    return `<td class="mono-text">${escapeHtml(String(rowNumber))}</td>`;
  }

  const value = typeof column.render === 'function' ? column.render(row, rowNumber) : escapeHtml(row[column.key] || '--');
  const cellClass = typeof column.className === 'function' ? column.className(row, rowNumber) : column.className || '';
  return `<td${cellClass ? ` class="${escapeHtml(cellClass)}"` : ''}>${value}</td>`;
}

function resolveRowId(tableKey, row, fallbackIndex) {
  if (tableKey === 'cbArb') return String(row.code || row.bondName || fallbackIndex);
  if (tableKey === 'ah') return `${row.aCode || ''}-${row.hCode || ''}-${fallbackIndex}`;
  if (tableKey === 'ab') return `${row.aCode || ''}-${row.bCode || ''}-${fallbackIndex}`;
  if (tableKey === 'monitor') return String(row.id || row.name || fallbackIndex);
  if (tableKey === 'merger') return String(row.announcementId || `${row.secCode || ''}-${row.announcementTime || ''}-${fallbackIndex}`);
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
  return `
    <div class="pagination-bar">
      <div class="pagination-status">
        第 ${escapeHtml(String(model.page))} / ${escapeHtml(String(model.totalPages))} 页，共 ${escapeHtml(String(model.totalRows))} 条
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
  const { tableKey, tableKind, columns, rows, emptyMessage, rowClassName, detailRenderer } = options;
  if (!rows.length) {
    return `
      <div class="empty-state">
        <div>${escapeHtml(emptyMessage)}</div>
      </div>
    `;
  }

  const model = getProcessedTableRows(tableKey, rows, columns);
  const hasDetails = typeof detailRenderer === 'function';
  const body = model.rows
    .map((row, index) => {
      const rowNumber = model.startIndex + index + 1;
      const rowId = resolveRowId(tableKey, row, rowNumber);
      const className = typeof rowClassName === 'function' ? rowClassName(row) : '';
      const cells = columns.map((column) => renderTableCell(column, row, rowNumber)).join('');
      const detailsCell = hasDetails
        ? `<td><button type="button" class="expand-button" data-table-key="${escapeHtml(tableKey)}" data-row-id="${escapeHtml(rowId)}">${readExpandedState(tableKey, rowId) ? '收起' : '展开'}</button></td>`
        : '';
      const mainRow = `<tr${className ? ` class="${escapeHtml(className)}"` : ''}>${cells}${detailsCell}</tr>`;
      if (!hasDetails || !readExpandedState(tableKey, rowId)) return mainRow;
      const detailHtml = detailRenderer(row, rowNumber);
      return `${mainRow}<tr class="detail-row"><td colspan="${columns.length + 1}">${detailHtml}</td></tr>`;
    })
    .join('');

  return `
    <div class="table-wrap">
      <table data-table-kind="${escapeHtml(tableKind)}">
        <thead>${renderTableHeader(columns, tableKey, { includeDetails: hasDetails })}</thead>
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
    <div class="table-wrap">
      <table data-table-kind="${escapeHtml(tableKind)}">
        <thead>
          <tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join('')}${hasDetails ? '<th>详情</th>' : ''}</tr>
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

function buildConvertibleColumns() {
  return [
    { key: 'index', label: '序号' },
    {
      key: 'bondInfo',
      label: '转债',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row.bondName || ''}-${row.code || ''}`,
      render: (row) => `
        <div>${escapeHtml(row.bondName || '--')}</div>
        <div class="muted mono-text">${escapeHtml(row.code || '--')}</div>
      `,
    },
    {
      key: 'stockInfo',
      label: '正股',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row.stockName || ''}-${row.stockCode || ''}`,
      render: (row) => `
        <div>${escapeHtml(row.stockName || '--')}</div>
        <div class="muted mono-text">${escapeHtml(row.stockCode || '--')}</div>
      `,
    },
    { key: 'price', label: '转债现价', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.price), render: (row) => formatNumber(row.price, 2) },
    { key: 'stockPrice', label: '正股现价', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.stockPrice), render: (row) => formatNumber(row.stockPrice, 2) },
    { key: 'premiumRate', label: '转股溢价率', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.premiumRate), className: (row) => statusClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate, 2) },
    { key: 'doubleLow', label: '双低', sortable: true, sortType: 'number', defaultDir: 'asc', sortValue: (row) => toNumber(row.doubleLow), render: (row) => formatNumber(row.doubleLow, 2) },
    { key: 'theoreticalPremiumRate', label: '理论溢价率', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.theoreticalPremiumRate), className: (row) => statusClass(row.theoreticalPremiumRate), render: (row) => formatPercent(row.theoreticalPremiumRate, 2) },
  ];
}

function buildPremiumColumns(type) {
  const config = getPremiumConfig(type);
  return [
    { key: 'index', label: '序号' },
    {
      key: 'aInfo',
      label: 'A股',
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row.aName || ''}-${row.aCode || ''}`,
      render: (row) => `
        <div>${escapeHtml(row.aName || '--')}</div>
        <div class="muted mono-text">${escapeHtml(row.aCode || '--')}</div>
      `,
    },
    {
      key: 'peerInfo',
      label: config.peerNameLabel,
      sortable: true,
      sortType: 'text',
      defaultDir: 'asc',
      sortValue: (row) => `${row[config.peerNameKey] || ''}-${row[config.peerCodeKey] || ''}`,
      render: (row) => `
        <div>${escapeHtml(row[config.peerNameKey] || '--')}</div>
        <div class="muted mono-text">${escapeHtml(row[config.peerCodeKey] || '--')}</div>
      `,
    },
    { key: 'aPrice', label: 'A股价', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.aPrice), render: (row) => formatNumber(row.aPrice, 2) },
    { key: config.peerPriceKey, label: '对手人民币价', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row[config.peerPriceKey]), render: (row) => formatNumber(row[config.peerPriceKey], 2) },
    { key: 'premium', label: '溢价率', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.premium), className: (row) => statusClass(row.premium), render: (row) => formatPercent(row.premium, 2) },
    { key: 'percentile', label: '近三年分位', sortable: true, sortType: 'number', defaultDir: 'desc', sortValue: (row) => toNumber(row.percentile), render: (row) => formatPercent(row.percentile, 2) },
    { key: 'sampleRange', label: '样本区间', sortable: false, render: (row) => escapeHtml(formatHistoryRange(row)) },
  ];
}

function renderActivePanel() {
  if (state.activeTab === 'cb-arb') return renderConvertibleBondPanel();
  if (state.activeTab === 'ah') return renderPremiumPanel('ah');
  if (state.activeTab === 'ab') return renderPremiumPanel('ab');
  if (state.activeTab === 'monitor') return renderMonitorPanel();
  if (state.activeTab === 'dividend') return renderDividendPanel();
  if (state.activeTab === 'merger') return renderMergerPanel();
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

  const rows = readResourceArray("cbArb");
  if (!rows.length) {
    panel.innerHTML = moduleEmpty("转债套利暂时没有返回数据");
    return;
  }

  const sortedByDoubleLow = [...rows].sort(
    (a, b) => (toNumber(a.doubleLow) ?? Number.POSITIVE_INFINITY) - (toNumber(b.doubleLow) ?? Number.POSITIVE_INFINITY)
  );
  const sortedByTheory = [...rows].sort(
    (a, b) => (toNumber(b.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY) - (toNumber(a.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY)
  );
  const convertRows = [...rows]
    .map((row) => ({ ...row, convertSpread: computeConvertSpread(row) }))
    .filter((row) => row.convertSpread !== null && row.convertSpread > 2)
    .sort((a, b) => (toNumber(b.convertSpread) ?? Number.NEGATIVE_INFINITY) - (toNumber(a.convertSpread) ?? Number.NEGATIVE_INFINITY));

  const summaryCards = [
    renderSummaryCard(
      "双低靠前",
      sortedByDoubleLow.slice(0, 3).map((row) => ({
        title: `${row.bondName || "--"} ${row.code || ""}`.trim(),
        subtitle: `溢价率 ${formatPercent(row.premiumRate, 2)} / 正股 ${row.stockName || "--"}`,
        value: formatNumber(row.doubleLow, 2),
      })),
      "compact-card"
    ),
    renderSummaryCard(
      "理论溢价率靠前",
      sortedByTheory.slice(0, 3).map((row) => ({
        title: `${row.bondName || "--"} ${row.code || ""}`.trim(),
        subtitle: `现价 ${formatNumber(row.price, 2)} / 双低 ${formatNumber(row.doubleLow, 2)}`,
        value: formatPercent(row.theoreticalPremiumRate, 2),
        valueClass: statusClass(row.theoreticalPremiumRate),
      })),
      "compact-card"
    ),
    renderSummaryCard(
      "转股套利候选",
      convertRows.slice(0, 3).map((row) => ({
        title: `${row.bondName || "--"} ${row.code || ""}`.trim(),
        subtitle: `转股价值 ${formatNumber(row.convertValue, 2)} / 转股价 ${formatNumber(row.convertPrice, 2)}`,
        value: formatPercent(row.convertSpread, 2),
        valueClass: statusClass(row.convertSpread),
      })),
      "compact-card"
    ),
  ].join("");

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">转债套利</div>
          <div class="section-note">主表默认仅展示关键列；补充字段统一放到行内展开，桌面端不依赖横向滚动查看核心信息。</div>
        </div>
        <div class="panel-meta">
          <span>总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime("cbArb")))}</span>
        </div>
      </div>
      <div class="summary-grid summary-grid-three">${summaryCards}</div>
      <div class="list-card">
        <h3>转债套利主表</h3>
        <div class="section-note">保持现有计算口径不变，只优化摘要密度、表格可读性与桌面端阅读体验。</div>
        ${renderPaginatedTable({
          tableKey: "cbArb",
          tableKind: "convertible",
          columns: buildConvertibleColumns(),
          rows,
          emptyMessage: "转债套利暂时没有返回数据",
          detailRenderer: (row) => renderDetailGrid(buildConvertibleDetailItems(row)),
        })}
      </div>
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
  const summaryColumn = resolvePremiumSummaryColumn(tableModel.sortColumn, columns);
  const summaryLabel = summaryColumn?.label || '溢价率';
  const topRows = sortRowsByColumn(rows, summaryColumn, 'desc').slice(0, 3);
  const bottomRows = sortRowsByColumn(rows, summaryColumn, 'asc').slice(0, 3);

  panel.innerHTML = `
    <div class="module-shell">
      <div class="premium-toolbar">
        <div>
          <div class="tab-title">${config.title}</div>
          <div class="section-note">主表按关键列紧凑展示，默认 50 条分页；补充字段通过“展开”查看，不再依赖模块内滚动。</div>
        </div>
        <div class="panel-meta">
          <span>总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime(type)))}</span>
        </div>
      </div>
      <div class="summary-grid">
        ${renderSummaryCard(
          `${summaryLabel}前三`,
          buildPremiumSummaryRows(topRows, config, summaryColumn)
        )}
        ${renderSummaryCard(
          `${summaryLabel}倒数前三`,
          buildPremiumSummaryRows(bottomRows, config, summaryColumn),
          'negative-card'
        )}
      </div>
      <div class="list-card">
        <h3>${config.title}主表</h3>
        <div class="section-note">样本区间采用压缩格式显示，例如 250520-260321；样本数放入说明区，不在主表单独占列。</div>
        ${renderPaginatedTable({
          tableKey: type,
          tableKind: 'premium',
          columns,
          rows,
          emptyMessage: `${config.title} 暂无数据`,
          detailRenderer: (row) => renderDetailGrid(buildPremiumDetailItems(type, row)),
        })}
        <div class="slim-note">${buildPremiumExplainText(type, rows)}</div>
      </div>
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
  const parts = ['“近三年百分位”按数据库当前可用历史样本计算，“样本区间”显示的是当前可用样本起止日期，不等于完整三年交易日。'];
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

function resolvePremiumSummaryColumn(activeColumn, columns) {
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
  if (!rows.length) {
    panel.innerHTML = moduleEmpty('当前没有监控套利项目');
    return;
  }

  const columns = [
    {
      key: 'name',
      label: '监控项',
      render: (row) => `
        <div>${escapeHtml(row.name || '--')}</div>
        <div class="muted">${escapeHtml(row.acquirerName || '--')} → ${escapeHtml(row.targetName || '--')}</div>
      `,
    },
    {
      key: 'targetPrice',
      label: '目标现价',
      render: (row) => `¥${formatNumber(readMonitorTargetPrice(row), 2)}`,
    },
    {
      key: 'stockYieldRate',
      label: '股票腿收益率',
      className: (row) => statusClass(row.stockYieldRate),
      render: (row) => formatPercent(row.stockYieldRate, 2),
    },
    {
      key: 'cashYieldRate',
      label: '现金腿收益率',
      className: (row) => statusClass(row.cashYieldRate),
      render: (row) => formatPercent(row.cashYieldRate, 2),
    },
    {
      key: 'bestYield',
      label: '最优收益率',
      className: (row) => statusClass(bestMonitorYield(row)),
      render: (row) => formatPercent(bestMonitorYield(row), 2),
    },
  ];

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">监控套利</div>
          <div class="section-note">主表仅保留收益决策关键字段；换股比例、安全系数、公式等放在“展开”里查看。</div>
        </div>
        <div class="panel-meta">
          <span>总样本 ${escapeHtml(formatInt(rows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime('monitor')))}</span>
        </div>
      </div>
      ${renderPaginatedTable({
        tableKind: 'monitor',
        tableKey: 'monitor',
        columns,
        rows,
        emptyMessage: '当前没有监控套利项目',
        detailRenderer: (row) => renderDetailGrid(buildMonitorDetailItems(row)),
      })}
    </div>
  `;
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
          <div class="section-note">页面主内容直接强调“今日登记日提醒”</div>
        </div>
        <div class="section-note">最近更新 ${escapeHtml(formatDate(readUpdateTime('dividend')))}</div>
      </div>
      <div class="list-card" style="margin-bottom: 14px;">
        <h3>今日登记日提醒</h3>
        ${todayList.length ? renderStackItems(todayList) : '<div class="empty-state"><div>今天没有登记日提醒</div></div>'}
      </div>
      <div class="list-card">
        <h3>分红观察名单</h3>
        ${renderPaginatedTable({
          tableKind: 'dividend',
          tableKey: 'dividend',
          columns: tableColumns,
          rows: sortedByYield,
          emptyMessage: '当前没有分红观察名单',
        })}
      </div>
    </div>
  `;
}

function renderMergerPanel() {
  const panel = dom.tabPanels.merger;
  const resource = state.resources.merger;
  if (!panel) return;

  if (resource.status === 'loading' || resource.status === 'idle') {
    panel.innerHTML = moduleLoading('收购私有正在拉取公告');
    return;
  }

  if (resource.status === 'error') {
    panel.innerHTML = moduleError('收购私有加载失败', resource.error?.message);
    return;
  }

  const rows = [...readResourceArray('merger')].sort((a, b) => readAnnouncementSortValue(b) - readAnnouncementSortValue(a));
  if (!rows.length) {
    panel.innerHTML = moduleEmpty('当前没有收购私有 / 并购公告');
    return;
  }

  const todayRows = rows.filter((row) => isTodayAnnouncement(row));
  const columns = [
    {
      key: 'announcementTime',
      label: '公告时间',
      render: (row) => `
        <div>${escapeHtml(readAnnouncementLabel(row))}</div>
        ${isTodayAnnouncement(row) ? '<div style="margin-top: 6px;"><span class="today-badge">今日公告</span></div>' : ''}
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

  panel.innerHTML = `
    <div class="module-shell">
      <div class="module-toolbar">
        <div>
          <div class="tab-title">收购私有</div>
          <div class="section-note">页面展示全量公告，默认按公告时间倒序；今日公告用高亮底色和标签标出。</div>
        </div>
        <div class="panel-meta">
          <span>总公告 ${escapeHtml(formatInt(rows.length))}</span>
          <span>今日公告 ${escapeHtml(formatInt(todayRows.length))}</span>
          <span>最近更新 ${escapeHtml(formatDate(readUpdateTime('merger')))}</span>
        </div>
      </div>
      ${renderPaginatedTable({
        tableKind: 'merger',
        tableKey: 'merger',
        columns,
        rows,
        rowClassName: (row) => (isTodayAnnouncement(row) ? 'merger-row-today' : ''),
        emptyMessage: '当前没有收购私有 / 并购公告',
        detailRenderer: (row) => renderDetailGrid(buildMergerDetailItems(row)),
      })}
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
                <div class="item-title">${escapeHtml(row.title)}</div>
                <div class="item-subtitle">${escapeHtml(row.subtitle)}</div>
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
    { label: '到期税前收益率', value: formatPercent(row.yieldToMaturityPretax, 2) },
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

function buildStockFormulaText(row) {
  return [
    formatNumber(row.acquirerPrice, 2),
    '×',
    formatNumber(row.stockRatio, 4),
    '×',
    formatNumber(row.safetyFactor, 4),
    '+',
    formatNumber(row.cashDistributionCny, 2),
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
  return [
    { label: '收购方现价', value: `¥${formatNumber(row.acquirerPrice, 2)}` },
    { label: '目标方现价', value: `¥${formatNumber(readMonitorTargetPrice(row), 2)}` },
    { label: '换股比例', value: formatNumber(row.stockRatio, 4) },
    { label: '安全系数', value: formatNumber(row.safetyFactor, 4) },
    { label: '现金分派', value: `¥${formatNumber(row.cashDistributionCny, 2)}` },
    { label: '股票腿公式', value: buildStockFormulaText(row) },
    { label: '股票腿理论对价', value: `¥${formatNumber(row.stockPayout, 2)}` },
    { label: '股票腿价差', value: formatSignedNumber(row.stockSpread, 2) },
    { label: '现金腿对价', value: `¥${formatNumber(row.cashPayout, 2)}` },
    { label: '现金腿价差', value: formatSignedNumber(row.cashSpread, 2) },
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
