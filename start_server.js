const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const { promisify } = require('util');
const { getConfig, loadEnvFile } = require('./shared/config/node_config');
const { getPathPolicy, ensureDir } = require('./shared/paths/node_paths');
const { readJson: sharedReadJson, writeJson: sharedWriteJson } = require('./shared/runtime/json_store');
const { createStateRegistry } = require('./shared/runtime/state_registry');
const {
  nowIso: sharedNowIso,
  getShanghaiParts: sharedGetShanghaiParts,
  normalizeDateText: sharedNormalizeDateText,
  isTradingSession: sharedIsTradingSession,
  isAfterCutoff: sharedIsAfterCutoff,
} = require('./shared/time/shanghai_time');
const { normalizeError: sharedNormalizeError } = require('./shared/models/service_result');
const { createPushConfigStore } = require('./notification/scheduler/push_config_store');
const { createPushRuntimeStore } = require('./notification/scheduler/push_runtime_store');
const { createWeComClient } = require('./notification/wecom/client');
const { buildSummaryMarkdown: buildNotificationSummaryMarkdown } = require('./notification/styles/markdown_style');
const { createMainSummaryService } = require('./notification/summary/main_summary');
const { createMergerReportService } = require('./notification/merger_report/service');
const { createWeComScheduler } = require('./notification/scheduler/wecom_scheduler');
const {
  sanitizeSubscriptionRows: strategySanitizeSubscriptionRows,
  sanitizeSubscriptionResult: strategySanitizeSubscriptionResult,
} = require('./strategy/subscription/service');
const { sanitizeCbArbRows: strategySanitizeCbArbRows } = require('./strategy/convertible_bond/service');
const {
  round: monitorRound,
  toFiniteNumber: monitorToFiniteNumber,
  normalizeMarket: monitorNormalizeMarket,
  normalizeCurrency: monitorNormalizeCurrency,
  normalizeSafetyFactor: monitorNormalizeSafetyFactor,
  inferBMarketFromCode: monitorInferBMarketFromCode,
  hasMonitorTerms: monitorHasMonitorTerms,
  toCny: monitorToCny,
  recalculateMonitor: monitorRecalculateMonitor,
  summarizeMonitor,
} = require('./strategy/custom_monitor/service');
const { createCustomMonitorRuntimeService } = require('./strategy/custom_monitor/runtime_service');
const { createDividendRuntimeService } = require('./strategy/dividend/runtime_service');
const { createMergerStrategy } = require('./strategy/merger/service');
const { buildOverviewViewModel } = require('./presentation/view_models/overview');
const { buildPushConfigResponse } = require('./presentation/view_models/push_payload');
const { registerMarketRoutes } = require('./presentation/routes/market_routes');
const { registerPushRoutes } = require('./presentation/routes/push_routes');
const { registerDashboardRoutes } = require('./presentation/routes/dashboard_routes');

const ROOT = __dirname;
loadEnvFile();
const PYTHON_PATH_SEPARATOR = process.platform === 'win32' ? ';' : ':';

const APP_CONFIG = getConfig();
const PATH_POLICY = getPathPolicy();
const STATE_REGISTRY = createStateRegistry({ config: APP_CONFIG });
const DATA_FETCH_CONFIG = APP_CONFIG?.data_fetch?.plugins || {};
const STRATEGY_CONFIG = APP_CONFIG?.strategy || {};
const PRESENTATION_CONFIG = APP_CONFIG?.presentation || {};
const NOTIFICATION_CONFIG = APP_CONFIG?.notification || {};
const PRESENTATION_STOCK_SEARCH_CONFIG = PRESENTATION_CONFIG?.stock_search || {};
const PRESENTATION_DIVIDEND_CONFIG = PRESENTATION_CONFIG?.dividend || {};
const PRESENTATION_HISTORICAL_PREMIUM_CONFIG = PRESENTATION_CONFIG?.historical_premium || {};
const EVENT_ARB_STRATEGY_CONFIG = STRATEGY_CONFIG?.event_arbitrage || {};
const INDEX_FILE = path.resolve(ROOT, PRESENTATION_CONFIG.dashboard_entry || './index.html');
const STATIC_DATA_DIR = PATH_POLICY.dataRootDir;
const SHARED_DATA_DIR = PATH_POLICY.sharedDataDir;
const DATA_PROFILE = PATH_POLICY.dbProfile;
const RUNTIME_DATA_DIR = PATH_POLICY.runtimeDataDir;
const execAsync = promisify(exec);

function toIntConfig(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function toBooleanConfig(value, fallback = false) {
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') {
    const normalized = value.trim().toLowerCase();
    if (['1', 'true', 'yes', 'on'].includes(normalized)) return true;
    if (['0', 'false', 'no', 'off'].includes(normalized)) return false;
  }
  return fallback;
}

function normalizePathConfig(value, fallback) {
  const text = String(value || '').trim();
  if (!text) return fallback;
  return text.startsWith('/') ? text : `/${text}`;
}

function normalizeTimeConfig(value, fallback) {
  const text = String(value || '').trim();
  const hit = text.match(/^(\d{2}):(\d{2})$/);
  if (!hit) return fallback;
  const hour = Number(hit[1]);
  const minute = Number(hit[2]);
  if (!Number.isFinite(hour) || !Number.isFinite(minute)) return fallback;
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return fallback;
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
}

function normalizeTimeListConfig(values, fallback) {
  const source = Array.isArray(values) ? values : [];
  const items = Array.from(new Set(
    source
      .map((item) => normalizeTimeConfig(item, ''))
      .filter(Boolean)
  )).sort();
  return items.length ? items : [fallback];
}

function pluginFetchConfig(key) {
  const config = DATA_FETCH_CONFIG?.[key];
  return config && typeof config === 'object' ? config : {};
}

function buildNotificationModuleDefaults() {
  const raw = (NOTIFICATION_CONFIG.enabled_modules && typeof NOTIFICATION_CONFIG.enabled_modules === 'object')
    ? NOTIFICATION_CONFIG.enabled_modules
    : {};
  return {
    ahab: raw.ahab !== false,
    subscription: raw.subscription !== false,
    cbArb: raw.cb_arb !== false,
    monitor: raw.custom_monitor !== false,
    dividend: raw.dividend !== false,
  };
}

const PORT = toIntConfig(APP_CONFIG?.app?.port, 5000);
const HOST = String(APP_CONFIG?.app?.host || '0.0.0.0').trim() || '0.0.0.0';
const SERVER_BASE_URL = String(APP_CONFIG?.app?.server_base_url || `http://127.0.0.1:${PORT}`).trim() || `http://127.0.0.1:${PORT}`;
const APP_ENVIRONMENT = String(APP_CONFIG?.app?.environment || process.env.NODE_ENV || 'development').trim() || 'development';
const TRUST_PROXY = toBooleanConfig(APP_CONFIG?.app?.trust_proxy, false);
const HEALTHCHECK_PATH = normalizePathConfig(
  APP_CONFIG?.deployment?.healthcheck?.public_path || APP_CONFIG?.app?.healthcheck_path,
  '/api/health'
);
const PUBLIC_BASE_URL = String(APP_CONFIG?.deployment?.public_base_url || SERVER_BASE_URL).trim() || SERVER_BASE_URL;
const PUBLIC_HEALTHCHECK_URL = `${PUBLIC_BASE_URL.replace(/\/+$/, '')}${HEALTHCHECK_PATH}`;
const REVERSE_PROXY_ENABLED = toBooleanConfig(APP_CONFIG?.deployment?.reverse_proxy?.enabled, false);
const REVERSE_PROXY_TYPE = String(APP_CONFIG?.deployment?.reverse_proxy?.type || 'none').trim() || 'none';
const SYSTEMD_SERVICE_NAME = String(APP_CONFIG?.deployment?.systemd?.service_name || 'alpha-monitor').trim() || 'alpha-monitor';
const SCHEDULER_TICK_INTERVAL_MS = toIntConfig(APP_CONFIG?.app?.scheduler_tick_interval_ms, 60 * 1000);
const SHUTDOWN_GRACE_TIMEOUT_MS = toIntConfig(APP_CONFIG?.app?.shutdown_grace_timeout_ms, 5000);
const PYTHON_EXEC_TIMEOUT_MS = toIntConfig(APP_CONFIG?.app?.python_exec_timeout_ms, 60 * 1000);
const PYTHON_EXEC_MAX_BUFFER = toIntConfig(APP_CONFIG?.app?.python_exec_max_buffer_mb, 50) * 1024 * 1024;
const WECOM_WEBHOOK_URL = String(NOTIFICATION_CONFIG?.wecom?.webhook_url || '').trim();
const PUSH_HTML_URL = String(
  NOTIFICATION_CONFIG?.wecom?.push_html_url || ''
).trim();
const WECOM_MAX_MARKDOWN_LENGTH = toIntConfig(NOTIFICATION_CONFIG?.wecom?.max_markdown_length, 3900);
const DEEPSEEK_API_KEY = String(STRATEGY_CONFIG?.merger?.deepseek_api_key || '').trim();
const DEEPSEEK_BASE_URL = String(STRATEGY_CONFIG?.merger?.deepseek_base_url || 'https://api.deepseek.com').trim();
const MERGER_REPORT_MAX_CHARS = toIntConfig(STRATEGY_CONFIG?.merger?.report_max_chars, 500);
const MERGER_PROMPT_TEMPLATE_CODE = String(
  STRATEGY_CONFIG?.merger?.prompt_template_code || 'MERGER_DEAL_OVERVIEW_V1'
).trim() || 'MERGER_DEAL_OVERVIEW_V1';
const EVENT_ARB_MATCH_MODE = String(EVENT_ARB_STRATEGY_CONFIG?.match_by || 'sec_code_only').trim().toLowerCase() || 'sec_code_only';
const EVENT_ARB_MATCH_LOOKBACK_DAYS = toIntConfig(EVENT_ARB_STRATEGY_CONFIG?.match_lookback_days, 365);
const PYTHON_CANDIDATES = Array.from(new Set(
  [
    ...(Array.isArray(APP_CONFIG?.app?.python_bin_candidates) ? APP_CONFIG.app.python_bin_candidates : []),
    ...(process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python']),
  ]
    .map((item) => String(item || '').trim())
    .filter(Boolean)
));
const DAILY_SYNC_CUTOFF_TIME = normalizeTimeConfig(APP_CONFIG?.data_fetch?.daily_sync?.cutoff_time, '16:10');
const DEFAULT_MAIN_PUSH_TIME = normalizeTimeConfig(NOTIFICATION_CONFIG?.default_full_push_time, '08:00');
const DEFAULT_MAIN_PUSH_TIMES = normalizeTimeListConfig(
  NOTIFICATION_CONFIG?.scheduler?.default_times,
  DEFAULT_MAIN_PUSH_TIME
);
const PUSH_CALENDAR_MODE = String(
  NOTIFICATION_CONFIG?.scheduler?.calendar_mode || 'daily'
).trim().toLowerCase() || 'daily';
const DEFAULT_NOTIFICATION_MODULES = buildNotificationModuleDefaults();
const DEFAULT_MERGER_PUSH_TIME = normalizeTimeConfig(
  NOTIFICATION_CONFIG?.scheduler?.merger_schedule?.default_time,
  DEFAULT_MAIN_PUSH_TIME
);
const DEFAULT_PUSH_CONFIG = {
  enabled: Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled),
  time: DEFAULT_MAIN_PUSH_TIMES[0],
  times: DEFAULT_MAIN_PUSH_TIMES,
  modules: DEFAULT_NOTIFICATION_MODULES,
  mergerSchedule: {
    enabled: Boolean(NOTIFICATION_CONFIG?.scheduler?.merger_schedule?.enabled),
    time: DEFAULT_MERGER_PUSH_TIME,
  },
};

function readJson(filePath, fallbackValue) {
  return sharedReadJson(filePath, fallbackValue);
}

function writeJson(filePath, data) {
  return sharedWriteJson(filePath, data);
}

function quoteArg(value) {
  return `"${String(value ?? '').replace(/"/g, '\\"')}"`;
}

function parseJsonText(text) {
  const normalized = String(text || '').trim();
  if (!normalized) throw new Error('Python script returned empty stdout');

  try {
    return JSON.parse(normalized);
  } catch {
    const objectStart = normalized.lastIndexOf('{');
    const arrayStart = normalized.lastIndexOf('[');
    const start = Math.max(objectStart, arrayStart);
    if (start >= 0) return JSON.parse(normalized.slice(start));
    throw new Error('Python stdout is not valid JSON');
  }
}

function parseJsonFromStdout(stdout) {
  if (!Buffer.isBuffer(stdout)) return parseJsonText(stdout);

  const labels = ['utf-8', 'gb18030', 'gbk'];
  const errors = [];
  for (const label of labels) {
    try {
      return parseJsonText(new TextDecoder(label, { fatal: false }).decode(stdout));
    } catch (error) {
      errors.push(`${label}: ${error.message}`);
    }
  }
  throw new Error(`Python stdout decode failed (${errors.join('; ')})`);
}

async function runPython(scriptName, args = [], options = {}) {
  const scriptPath = path.join(ROOT, scriptName);
  let lastError;
  const attempts = [];

  for (const pythonBin of PYTHON_CANDIDATES) {
    const command = `${pythonBin} ${quoteArg(scriptPath)} ${args.map(quoteArg).join(' ')}`.trim();
    try {
      const result = await execAsync(command, {
        cwd: ROOT,
        timeout: options.timeout || PYTHON_EXEC_TIMEOUT_MS,
        maxBuffer: options.maxBuffer || PYTHON_EXEC_MAX_BUFFER,
        windowsHide: true,
        encoding: 'buffer',
        env: {
          ...process.env,
          PYTHONIOENCODING: 'utf-8',
          PYTHONUTF8: '1',
          PYTHONPATH: process.env.PYTHONPATH
            ? `${ROOT}${PYTHON_PATH_SEPARATOR}${process.env.PYTHONPATH}`
            : ROOT,
        },
      });

      return {
        command,
        data: parseJsonFromStdout(result.stdout),
        stderr: Buffer.isBuffer(result.stderr) ? result.stderr.toString('utf8') : result.stderr || '',
      };
    } catch (error) {
      lastError = error;
      const stderrText = Buffer.isBuffer(error?.stderr) ? error.stderr.toString('utf8') : String(error?.stderr || '').trim();
      attempts.push({
        pythonBin,
        message: String(error?.message || error || 'Python execution failed'),
        stderr: stderrText,
      });
    }
  }

  if (lastError) {
    const message = attempts
      .map((item) => `${item.pythonBin}: ${item.stderr || item.message}`)
      .join(' | ');
    lastError.message = `Failed to execute ${scriptName}. Attempts: ${message || lastError.message}`;
  }

  throw lastError || new Error(`Failed to execute ${scriptName}`);
}

function nowIso() {
  return sharedNowIso();
}

function getShanghaiParts(date = new Date()) {
  return sharedGetShanghaiParts(date);
}

function isTradingSession(date = new Date()) {
  return sharedIsTradingSession(date);
}

function isAfterDailySyncCutoff(date = new Date(), hour = 16, minute = 10) {
  return sharedIsAfterCutoff(date, `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`);
}

async function callDataCore(args, options = {}) {
  try {
    const { data } = await runPython('data_dispatch.py', args, options);
    if (data && typeof data === 'object') return data;
    return { success: false, error: 'data_dispatch.py returned invalid payload', data: [], updateTime: nowIso() };
  } catch (error) {
    return {
      success: false,
      error: String(error?.message || error || 'data_dispatch.py failed'),
      data: [],
      updateTime: nowIso(),
    };
  }
}

async function fetchExchangeRates() {
  const result = await callDataCore(['exchange-rate'], { timeout: 30000 });
  if (!result.success || !result.data) {
    return { success: false, error: result.error || 'exchange rate fetch failed', data: null, updateTime: nowIso() };
  }

  const hkToCny = Number(result.data.hkdToCny ?? result.data.hkToCny);
  const usdToCny = Number(result.data.usdToCny);
  if (!Number.isFinite(hkToCny) || !Number.isFinite(usdToCny)) {
    return { success: false, error: 'exchange rate payload invalid', data: null, updateTime: nowIso() };
  }

  return {
    success: true,
    data: {
      hkToCny,
      usdToCny,
      updateTime: result.data.updateTime || result.updateTime || nowIso(),
      source: result.data.source || result.source || 'tencent',
    },
    updateTime: result.updateTime || nowIso(),
  };
}

const DATASETS = {
  ah: {
    intraday: pluginFetchConfig('ah_premium').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('ah_premium').refresh_interval_ms, 5 * 60 * 1000),
    dbDailySync: pluginFetchConfig('ah_premium').daily_incremental_sync !== false,
    fetch: (options = {}) => callDataCore(['ah', ...(options.forcePairs ? ['--force-pairs'] : [])], { timeout: 80000 }),
    dailySync: () => callDataCore(['ah', '--force-pairs'], { timeout: 80000 }),
  },
  ab: {
    intraday: pluginFetchConfig('ab_premium').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('ab_premium').refresh_interval_ms, 5 * 60 * 1000),
    dbDailySync: pluginFetchConfig('ab_premium').daily_incremental_sync !== false,
    fetch: (options = {}) => callDataCore(['ab', ...(options.forcePairs ? ['--force-pairs'] : [])], { timeout: 80000 }),
    dailySync: () => callDataCore(['ab', '--force-pairs'], { timeout: 80000 }),
  },
  exchangeRate: {
    intraday: pluginFetchConfig('exchange_rate').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('exchange_rate').refresh_interval_ms, 5 * 60 * 1000),
    dbDailySync: Boolean(pluginFetchConfig('exchange_rate').daily_incremental_sync),
    fetch: () => fetchExchangeRates(),
  },
  ipo: {
    intraday: pluginFetchConfig('subscription').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('subscription').refresh_interval_ms, 15 * 60 * 1000),
    dbDailySync: pluginFetchConfig('subscription').daily_incremental_sync !== false,
    fetch: () => callDataCore(['ipo'], { timeout: 70000 }),
    dailySync: () => callDataCore(['ipo'], { timeout: 70000 }),
  },
  bonds: {
    intraday: pluginFetchConfig('subscription').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('subscription').refresh_interval_ms, 15 * 60 * 1000),
    dbDailySync: pluginFetchConfig('subscription').daily_incremental_sync !== false,
    fetch: () => callDataCore(['bonds'], { timeout: 70000 }),
    dailySync: () => callDataCore(['bonds'], { timeout: 70000 }),
  },
  cbArb: {
    intraday: pluginFetchConfig('convertible_bond').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('convertible_bond').refresh_interval_ms, 5 * 60 * 1000),
    dbDailySync: pluginFetchConfig('convertible_bond').daily_incremental_sync !== false,
    fetch: async (options = {}) => {
      if (options.force || options.syncUniverse) {
        await callDataCore(['sync-cb-stock-history'], { timeout: 900000, maxBuffer: 1024 * 1024 * 50 });
      }
      return callDataCore(['cb-arb'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 });
    },
    dailySync: async () => {
      await callDataCore(['sync-cb-stock-history'], { timeout: 900000, maxBuffer: 1024 * 1024 * 50 });
      return callDataCore(['cb-arb'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 });
    },
  },
  merger: {
    intraday: Boolean(pluginFetchConfig('merger').intraday),
    dbDailySync: Boolean(pluginFetchConfig('merger').daily_incremental_sync),
    fetch: () => callDataCore(['merger'], { timeout: 120000, maxBuffer: 1024 * 1024 * 100 }),
  },
  eventArb: {
    intraday: pluginFetchConfig('event_arbitrage').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('event_arbitrage').refresh_interval_ms, 5 * 60 * 1000),
    dbDailySync: Boolean(pluginFetchConfig('event_arbitrage').daily_incremental_sync),
    fetch: (options = {}) => buildEventArbitrageDataset(options),
  },
};
const stateStore = STATE_REGISTRY.read('market_refresh_state', 'market_refresh_state.json', {
  lastDailySyncDate: null,
  lastPremiumHistorySyncDate: null,
});
const pushConfigStore = STATE_REGISTRY.read('push_config', 'push_config.json', JSON.parse(JSON.stringify(DEFAULT_PUSH_CONFIG)));
const pushRuntimeState = STATE_REGISTRY.read('push_runtime_state', 'push_runtime_state.json', {
  lastMainPushDate: null,
  lastMergerReportDate: null,
  lastMainPushAttemptAt: null,
  lastMainPushSuccessAt: null,
  lastMainPushError: null,
  lastMergerPushAttemptAt: null,
  lastMergerPushSuccessAt: null,
  lastMergerPushError: null,
  mainPushRecords: {},
  mergerPushRecords: {},
});
const mergerReportStore = STATE_REGISTRY.read('merger_company_reports', 'merger_company_reports.json', { reports: {} });
const refreshLocks = new Map();
const intradayLastRun = new Map();
const datasetCache = new Map();
let schedulerStarted = false;
let refreshTimer = null;
let schedulerTickRunning = false;
let shuttingDown = false;

function logFatal(tag, error) {
  const message = error?.stack || error?.message || String(error || tag);
  console.error(`[fatal] ${tag}: ${message}`);
}

function saveStateStore() {
  STATE_REGISTRY.write('market_refresh_state', 'market_refresh_state.json', stateStore);
}

function savePushConfigStore() {
  STATE_REGISTRY.write('push_config', 'push_config.json', pushConfigStore);
}

function savePushRuntimeState() {
  STATE_REGISTRY.write('push_runtime_state', 'push_runtime_state.json', pushRuntimeState);
}

function saveMergerReportStore() {
  STATE_REGISTRY.write('merger_company_reports', 'merger_company_reports.json', mergerReportStore);
}

function cloneJsonSafe(value, fallback = null) {
  try {
    return JSON.parse(JSON.stringify(value));
  } catch {
    return fallback;
  }
}

function createHealthSection(status, message, details = {}) {
  return {
    status,
    message,
    updatedAt: sharedNowIso(),
    lastSuccessAt: null,
    lastFailureAt: null,
    details: cloneJsonSafe(details, {}),
  };
}

const runtimeHealth = {
  web: createHealthSection('starting', 'HTTP service is starting', {
    environment: APP_ENVIRONMENT,
    host: HOST,
    port: PORT,
    internalUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
    healthcheckPath: HEALTHCHECK_PATH,
    trustProxy: TRUST_PROXY,
    reverseProxyEnabled: REVERSE_PROXY_ENABLED,
    reverseProxyType: REVERSE_PROXY_TYPE,
    systemdServiceName: SYSTEMD_SERVICE_NAME,
    indexFile: INDEX_FILE,
  }),
  data_jobs: createHealthSection('starting', 'Background data jobs have not run yet'),
  push_scheduler: createHealthSection('starting', 'Push scheduler has not run yet'),
};

function updateHealthSection(name, status, message, details = {}) {
  const previous = runtimeHealth[name] || createHealthSection('starting', '');
  const next = {
    ...previous,
    status,
    message,
    updatedAt: sharedNowIso(),
    details: {
      ...(previous.details && typeof previous.details === 'object' ? previous.details : {}),
      ...cloneJsonSafe(details, {}),
    },
  };

  if (status === 'ok') next.lastSuccessAt = next.updatedAt;
  if (status === 'warn' || status === 'fail') next.lastFailureAt = next.updatedAt;
  runtimeHealth[name] = next;
  return next;
}

function buildHealthSnapshot() {
  const sections = cloneJsonSafe(runtimeHealth, {});
  const indexFileExists = fs.existsSync(INDEX_FILE);

  if (!indexFileExists) {
    sections.web = {
      ...sections.web,
      status: 'fail',
      message: 'Dashboard entry file is missing',
      updatedAt: sharedNowIso(),
      lastFailureAt: sharedNowIso(),
      details: {
        ...(sections.web?.details || {}),
        indexFile: INDEX_FILE,
        indexFileExists,
      },
    };
  } else {
    sections.web = {
      ...sections.web,
      details: {
        ...(sections.web?.details || {}),
        indexFile: INDEX_FILE,
        indexFileExists,
      },
    };
  }

  let overallStatus = sections.web?.status === 'ok' ? 'ok' : 'fail';
  if (overallStatus === 'ok') {
    const backgroundStatuses = ['data_jobs', 'push_scheduler']
      .map((key) => sections[key]?.status)
      .filter(Boolean);
    if (backgroundStatuses.some((status) => status === 'fail' || status === 'warn' || status === 'starting')) {
      overallStatus = 'warn';
    }
  }

  return {
    status: overallStatus,
    timestamp: sharedNowIso(),
    environment: APP_ENVIRONMENT,
    projectRoot: ROOT,
    url: PUBLIC_BASE_URL,
    internalUrl: SERVER_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
    healthcheckPath: HEALTHCHECK_PATH,
    reverseProxy: {
      enabled: REVERSE_PROXY_ENABLED,
      type: REVERSE_PROXY_TYPE,
    },
    pid: process.pid,
    sections,
  };
}

function datasetCacheRegistryKey(key) {
  return `market_cache_${key}`;
}

function datasetCacheFilename(key) {
  return `market_cache_${key}.json`;
}

function readDatasetCache(key) {
  if (datasetCache.has(key)) return datasetCache.get(key);
  const cached = STATE_REGISTRY.read(datasetCacheRegistryKey(key), datasetCacheFilename(key), null);
  const normalized = cached && typeof cached === 'object' ? cached : null;
  datasetCache.set(key, normalized);
  return normalized;
}

function writeDatasetCache(key, payload) {
  const nextPayload = {
    ...cloneJsonSafe(payload, {}),
    cacheTime: nowIso(),
  };
  datasetCache.set(key, nextPayload);
  STATE_REGISTRY.write(datasetCacheRegistryKey(key), datasetCacheFilename(key), nextPayload);
  return nextPayload;
}

function readDatasetCachePayload(key) {
  const cached = readDatasetCache(key);
  if (!cached || typeof cached !== 'object' || cached.success === false) return null;
  return cloneJsonSafe(cached);
}

function readDatasetTimestamp(result) {
  const candidates = [
    result?.cacheTime,
    result?.updateTime,
    result?.data?.updateTime,
  ];
  for (const value of candidates) {
    const text = String(value || '').trim();
    if (!text) continue;
    const timestamp = Date.parse(text);
    if (Number.isFinite(timestamp)) return timestamp;
  }
  return 0;
}

function isDatasetCacheFresh(key, cached) {
  const intervalMs = Number(DATASETS?.[key]?.refreshIntervalMs) || 0;
  if (!intervalMs) return false;
  const timestamp = readDatasetTimestamp(cached);
  if (!timestamp) return false;
  return (Date.now() - timestamp) < intervalMs;
}

function withCachedDatasetMeta(cached, extra = {}) {
  return {
    ...cloneJsonSafe(cached, {}),
    servedFromCache: true,
    cacheTime: cached?.cacheTime || nowIso(),
    ...extra,
  };
}

function scheduleDatasetRefresh(key, options = {}) {
  void refreshDataset(key, options).catch((error) => {
    console.error(`[dataset_refresh_failed] ${key}: ${error?.message || error}`);
  });
}

// 通知域服务在这里统一组装，主入口仅保留薄封装。
const pushConfigDomain = createPushConfigStore({
  state: pushConfigStore,
  defaultConfig: DEFAULT_PUSH_CONFIG,
  save: savePushConfigStore,
});
const pushRuntimeDomain = createPushRuntimeStore({
  state: pushRuntimeState,
  save: savePushRuntimeState,
  parsePushMinutes: (value) => pushConfigDomain.parsePushMinutes(value),
});
const weComClient = createWeComClient({
  webhookUrl: WECOM_WEBHOOK_URL,
  pushHtmlUrl: PUSH_HTML_URL,
  maxLength: WECOM_MAX_MARKDOWN_LENGTH,
  fetchImpl: globalThis.fetch,
});
const mainSummaryService = createMainSummaryService({
  collectSummaryDatasets,
  buildSummaryMarkdown: buildWeComSummaryMarkdown,
  sendMarkdown: (markdown) => weComClient.sendMarkdown(markdown),
  getPushConfig,
  normalizePushConfig,
  nowIso,
});
const mergerReportService = createMergerReportService({
  nowIso,
  sendMarkdown: (markdown) => weComClient.sendMarkdown(markdown),
  getTodayMergerGroups,
  getMergerReportByCompany,
  upsertMergerReportByCompany,
  normalizeDateText,
  pickText,
  mergerCompanyCode,
  mergerCompanyName,
  mergerAnnouncementDate,
  normalizeError,
  reportMaxChars: MERGER_REPORT_MAX_CHARS,
  promptTemplateCode: MERGER_PROMPT_TEMPLATE_CODE,
  deepseekApiKey: DEEPSEEK_API_KEY,
  deepseekBaseUrl: DEEPSEEK_BASE_URL,
  fetchImpl: globalThis.fetch,
});
const weComScheduler = createWeComScheduler({
  getPushConfig,
  runtimeStore: pushRuntimeDomain,
  pushByModulesToWeCom,
  pushMergerReportToWeCom,
  getShanghaiParts,
  parsePushMinutes: (value) => pushConfigDomain.parsePushMinutes(value),
  calendarMode: PUSH_CALENDAR_MODE,
  isTradingSession,
  defaultMergerSchedule: DEFAULT_PUSH_CONFIG.mergerSchedule,
  nowIso,
  logError: (scope, error) => console.error(scope, error?.message || error),
});

function getPushDeliveryStatus() {
  return {
    webhookConfigured: Boolean(WECOM_WEBHOOK_URL),
    schedulerEnabled: Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled),
    calendarMode: PUSH_CALENDAR_MODE,
  };
}

function buildPushConfigViewModel(config) {
  return buildPushConfigResponse(config, pushRuntimeState, getPushDeliveryStatus());
}

function getStateDate(key) {
  const text = String(stateStore?.[key] || '').trim();
  return text || null;
}

function setStateDate(key, value) {
  stateStore[key] = value;
  stateStore[`${key}Time`] = nowIso();
  saveStateStore();
}

function normalizeYmd(value) {
  const text = String(value || '').trim();
  if (!text) return '';
  const hit = text.match(/\d{4}-\d{2}-\d{2}/);
  return hit ? hit[0] : text.slice(0, 10);
}

function subscriptionCode(row, type) {
  if (!row || typeof row !== 'object') return '';
  const raw = type === 'ipo'
    ? (row.stockCode || row.code || row.symbol)
    : (row.bondCode || row.code || row.symbol);
  return String(raw || '').trim();
}

function subscriptionName(row, type) {
  if (!row || typeof row !== 'object') return '';
  const raw = type === 'ipo'
    ? (row.stockName || row.name)
    : (row.bondName || row.name);
  return String(raw || '').trim();
}

function subscriptionDate(row) {
  if (!row || typeof row !== 'object') return '';
  return normalizeYmd(row.subscribeDate || row.subscriptionDate || row.date);
}

function subscriptionRowScore(row, type) {
  const fields = [
    subscriptionCode(row, type),
    subscriptionName(row, type),
    subscriptionDate(row),
    normalizeYmd(row.paymentDate || row.payment_date || row.lotteryPaymentDate),
    normalizeYmd(row.lotteryDate || row.lottery_date),
    normalizeYmd(row.listingDate || row.listing_date),
    String(row.status || row.state || '').trim(),
  ];
  return fields.reduce((sum, value) => sum + (value ? 1 : 0), 0);
}

function normalizeSubscriptionRow(row, type) {
  const code = subscriptionCode(row, type);
  const name = subscriptionName(row, type);
  const subscribeDate = subscriptionDate(row);
  if (!code || !name || !subscribeDate) return null;
  const cloned = { ...row };
  if (type === 'ipo') {
    cloned.stockCode = code;
    cloned.stockName = name;
  } else {
    cloned.bondCode = code;
    cloned.bondName = name;
  }
  cloned.code = code;
  if (!cloned.name) cloned.name = name;
  cloned.subscribeDate = subscribeDate;
  if (cloned.subscriptionDate) cloned.subscriptionDate = subscribeDate;
  return cloned;
}

function sanitizeSubscriptionRows(rows, type) {
  return strategySanitizeSubscriptionRows(rows, type);
}

function sanitizeSubscriptionResult(result, type) {
  return strategySanitizeSubscriptionResult(result, type);
}

function isFiniteNum(value) {
  return Number.isFinite(Number(value));
}

function cbArbRowScore(row) {
  if (!row || typeof row !== 'object') return 0;
  const metrics = [
    row.code,
    row.bondName,
    row.stockCode,
    row.stockName,
    row.price,
    row.stockPrice,
    row.convertPrice,
    row.convertValue,
    row.remainingYears,
  ];
  return metrics.reduce((sum, value) => sum + ((value !== null && value !== undefined && String(value).trim() !== '') ? 1 : 0), 0);
}

function isValidCbArbRow(row) {
  if (!row || typeof row !== 'object') return false;
  const code = String(row.code || '').trim();
  const bondName = String(row.bondName || '').trim();
  const stockCode = String(row.stockCode || '').trim();
  const stockName = String(row.stockName || '').trim();
  return Boolean(
    code &&
    bondName &&
    stockCode &&
    stockName &&
    isFiniteNum(row.price) &&
    isFiniteNum(row.stockPrice) &&
    isFiniteNum(row.convertPrice) &&
    isFiniteNum(row.convertValue)
  );
}

function sanitizeCbArbRows(rows) {
  return strategySanitizeCbArbRows(rows);
}

function normalizeDatasetPayload(key, result) {
  if (!result || typeof result !== 'object') return result;
  if (result.success === false) return result;
  if (key === 'ipo') return sanitizeSubscriptionResult(result, 'ipo');
  if (key === 'bonds') return sanitizeSubscriptionResult(result, 'bond');
  if (key === 'cbArb') {
    const rows = sanitizeCbArbRows(result.data);
    return {
      ...result,
      data: rows,
      list: rows,
      rows,
    };
  }
  return result;
}

function shouldRetryDatasetBySchema(key, result) {
  if (!result || typeof result !== 'object' || result.success === false) return false;
  if (key === 'cbArb') return !isCbArbSchemaReady(result);
  if (key === 'ah') return !isAhSchemaReady(result);
  return false;
}

function normalizeDatasetRetryOptions(key, options = {}) {
  if (key === 'cbArb') return { ...options, force: true, syncUniverse: true };
  if (key === 'ah') return { ...options, forcePairs: true };
  return options;
}

async function fetchDatasetOnce(key, options = {}) {
  const dataset = DATASETS[key];
  if (!dataset) throw new Error(`Unknown dataset: ${key}`);
  const refresher = options.dailySync && typeof dataset.dailySync === 'function' ? dataset.dailySync : dataset.fetch;
  const rawResult = await refresher(options);
  return normalizeDatasetPayload(key, rawResult);
}

async function refreshDataset(key, options = {}) {
  const lockKey = `${key}:${options.dailySync ? 'daily' : 'normal'}`;
  if (refreshLocks.has(lockKey)) return refreshLocks.get(lockKey);

  const task = (async () => {
    const first = await fetchDatasetOnce(key, options);
    let finalResult = first;
    if (shouldRetryDatasetBySchema(key, first)) {
      finalResult = await fetchDatasetOnce(key, normalizeDatasetRetryOptions(key, options));
    }
    if (finalResult && typeof finalResult === 'object' && finalResult.success !== false) {
      writeDatasetCache(key, finalResult);
      return finalResult;
    }

    const cached = readDatasetCachePayload(key);
    if (!options.force && !options.dailySync && cached) {
      return withCachedDatasetMeta(cached, {
        refreshError: normalizeError(finalResult?.error || 'refresh_failed'),
      });
    }
    return finalResult;
  })().finally(() => refreshLocks.delete(lockKey));

  refreshLocks.set(lockKey, task);
  return task;
}

function shouldRunIntradayDataset(key, intervalMs) {
  const now = Date.now();
  const previous = Number(intradayLastRun.get(key) || 0);
  if (!previous || now - previous >= intervalMs) {
    intradayLastRun.set(key, now);
    return true;
  }
  return false;
}

function isCbArbSchemaReady(result) {
  const rows = Array.isArray(result?.data) ? result.data : [];
  const row = rows[0];
  const baseReady = Boolean(
    row &&
    typeof row === 'object' &&
    Object.prototype.hasOwnProperty.call(row, 'pureBondValue') &&
    Object.prototype.hasOwnProperty.call(row, 'maturityDate') &&
    Object.prototype.hasOwnProperty.call(row, 'remainingYears') &&
    Object.prototype.hasOwnProperty.call(row, 'callOptionValue60') &&
    Object.prototype.hasOwnProperty.call(row, 'putOptionValue60')
  );
  if (!baseReady) return false;
  if (!rows.length) return true;
  const hasStockChange = rows.some((item) => Number.isFinite(Number(item?.stockChangePercent)));
  if (!hasStockChange) return false;

  const volatilityCount = rows.filter((item) => Number.isFinite(Number(item?.volatility60))).length;
  const volatilityCoverage = volatilityCount / rows.length;
  return volatilityCoverage >= 0.55;
}

function normalizeComparableName(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/\s+/g, '')
    .replace(/[()（）\-_.·,，]/g, '')
    .replace(/股份有限公司|股份|有限公司|集团|控股/g, '');
}

function isPairNameConsistent(aName, pairName) {
  const a = normalizeComparableName(aName);
  const b = normalizeComparableName(pairName);
  if (!a || !b) return true;
  return a.includes(b) || b.includes(a);
}

function isAhSchemaReady(result) {
  const rows = Array.isArray(result?.data) ? result.data : [];
  if (!rows.length) return false;

  for (const row of rows) {
    const aCode = String(row?.aCode || '').trim();
    const hCode = String(row?.hCode || '').trim();
    if (!aCode || !hCode) return false;

    if (aCode === '301039' && hCode === '02039') return false;

    const aName = String(row?.aName || '').trim();
    const hName = String(row?.hName || '').trim();
    const percentile = toFiniteNumber(row?.percentile);
    const historyCount = toFiniteNumber(row?.historyCount) ?? 0;
    if (!isPairNameConsistent(aName, hName) && historyCount === 0 && percentile === null) {
      return false;
    }
  }

  return true;
}

async function getDataset(key, options = {}) {
  if (!DATASETS[key]) throw new Error(`Unknown dataset: ${key}`);
  if (options.force || options.dailySync) {
    return refreshDataset(key, options);
  }

  const cached = readDatasetCachePayload(key);
  if (cached) {
    if (!isDatasetCacheFresh(key, cached)) {
      const lockKey = `${key}:normal`;
      if (!refreshLocks.has(lockKey)) scheduleDatasetRefresh(key, options);
    }
    return withCachedDatasetMeta(cached);
  }

  return refreshDataset(key, options);
}

async function runIntradayRefreshCycle() {
  const tasks = Object.entries(DATASETS)
    .filter(([, dataset]) => dataset.intraday)
    .filter(([key, dataset]) => shouldRunIntradayDataset(key, Number(dataset.refreshIntervalMs) || 5 * 60 * 1000))
    .map(([key]) => refreshDataset(key));
  if (tasks.length) await Promise.allSettled(tasks);
}

async function runPremiumHistorySync() {
  const result = await runPython('tools/rebuild_premium_db.py', ['--mode', 'update'], {
    timeout: 1000 * 60 * 20,
    maxBuffer: 1024 * 1024 * 50,
  });
  const payload = result?.data;
  if (payload && typeof payload === 'object' && payload.success === false) {
    throw new Error(payload.error || 'premium history sync failed');
  }
}

async function runDailySync() {
  const shanghai = getShanghaiParts();
  const [cutoffHour, cutoffMinute] = DAILY_SYNC_CUTOFF_TIME.split(':').map((item) => Number(item));
  if (!isAfterDailySyncCutoff(new Date(), cutoffHour, cutoffMinute)) return;

  if (getStateDate('lastDailySyncDate') !== shanghai.date) {
    const tasks = Object.entries(DATASETS)
      .filter(([, dataset]) => dataset.dbDailySync)
      .map(([key]) => refreshDataset(key, { dailySync: true, force: true }));
    await Promise.allSettled(tasks);
    setStateDate('lastDailySyncDate', shanghai.date);
  }

  if (getStateDate('lastPremiumHistorySyncDate') !== shanghai.date) {
    await runPremiumHistorySync();
    setStateDate('lastPremiumHistorySyncDate', shanghai.date);
  }
}

async function runDataJobsCycle(context = 'tick', options = {}) {
  const details = {
    context,
    tradingSession: isTradingSession(),
    dailySyncCutoffTime: DAILY_SYNC_CUTOFF_TIME,
  };

  try {
    if (options.preloadDatasets) {
      const preloadKeys = ['exchangeRate', 'ah', 'ab', 'cbArb', 'merger', 'eventArb', 'ipo', 'bonds'];
      await Promise.allSettled(preloadKeys.map((key) => getDataset(key)));
      details.preloadedDatasets = preloadKeys;
    }

    if (details.tradingSession) await runIntradayRefreshCycle();
    await runDailySync();
    updateHealthSection('data_jobs', 'ok', 'Background data jobs are healthy', details);
  } catch (error) {
    updateHealthSection('data_jobs', 'warn', `Background data jobs degraded: ${error?.message || error}`, {
      ...details,
      error: String(error?.message || error || 'unknown error'),
    });
    throw error;
  }
}

async function runPushSchedulerCycle(context = 'tick') {
  const details = { context };

  try {
    await runMainPushIfNeeded();
    await runMergerPushIfNeeded();
    updateHealthSection('push_scheduler', 'ok', 'Push scheduler is healthy', details);
  } catch (error) {
    updateHealthSection('push_scheduler', 'warn', `Push scheduler degraded: ${error?.message || error}`, {
      ...details,
      error: String(error?.message || error || 'unknown error'),
    });
    throw error;
  }
}

function startScheduler() {
  if (schedulerStarted) return;
  schedulerStarted = true;
  updateHealthSection('data_jobs', 'starting', 'Background data jobs are starting');
  updateHealthSection('push_scheduler', 'starting', 'Push scheduler is starting');

  refreshTimer = setInterval(async () => {
    if (schedulerTickRunning) return;
    schedulerTickRunning = true;
    try {
      try {
        await runDataJobsCycle('tick');
      } catch (error) {
        console.error('[scheduler][data_jobs] tick failed:', error?.message || error);
      }

      try {
        await runPushSchedulerCycle('tick');
      } catch (error) {
        console.error('[scheduler][push_scheduler] tick failed:', error?.message || error);
      }
    } finally {
      schedulerTickRunning = false;
    }
  }, SCHEDULER_TICK_INTERVAL_MS);

  if (typeof refreshTimer.unref === 'function') refreshTimer.unref();

  Promise.resolve()
    .then(async () => {
      try {
        await runDataJobsCycle('warmup', { preloadDatasets: true });
      } catch (error) {
        console.error('[scheduler][data_jobs] warmup failed:', error?.message || error);
      }

      try {
        await runPushSchedulerCycle('warmup');
      } catch (error) {
        console.error('[scheduler][push_scheduler] warmup failed:', error?.message || error);
      }
    })
    .catch((error) => console.error('[scheduler] warmup failed:', error?.message || error));
}

function round(value, digits = 4) {
  return monitorRound(value, digits);
}

function toFiniteNumber(value) {
  return monitorToFiniteNumber(value);
}

function normalizeMarket(value, fallback = 'A') {
  return monitorNormalizeMarket(value, fallback);
}

function normalizeCurrency(value, fallback = 'CNY') {
  return monitorNormalizeCurrency(value, fallback);
}

function normalizeSafetyFactor(value, fallback = 1) {
  return monitorNormalizeSafetyFactor(value, fallback);
}

function inferBMarketFromCode(code, fallback = 'sh') {
  return monitorInferBMarketFromCode(code, fallback);
}

function hasMonitorTerms(input) {
  return monitorHasMonitorTerms(input);
}

function toCny(amount, currency, rates) {
  return monitorToCny(amount, currency, rates);
}

function recalculateMonitor(monitor, rates) {
  return monitorRecalculateMonitor(monitor, rates, nowIso);
}

async function getStockPrice(code, market = 'a', bMarket = 'sh') {
  return callDataCore(['price', code, market, bMarket], { timeout: 30000 });
}
const customMonitorRuntimeService = createCustomMonitorRuntimeService({
  stateRegistry: STATE_REGISTRY,
  nowIso,
  fetchExchangeRates,
  getStockPrice,
  round,
  toFiniteNumber,
  normalizeMarket,
  normalizeCurrency,
  normalizeSafetyFactor,
  inferBMarketFromCode,
  hasMonitorTerms,
  recalculateMonitor,
});

const dividendRuntimeService = createDividendRuntimeService({
  stateRegistry: STATE_REGISTRY,
  nowIso,
  callDataCore,
  getStockPrice,
});

const {
  loadMonitors,
  getAllMonitors,
  upsertMonitor,
  deleteMonitor,
} = customMonitorRuntimeService;

const {
  loadPortfolio,
  refreshPortfolio,
  addDividendStock,
  removeDividendStock,
  upcomingDividends,
} = dividendRuntimeService;
function getOverviewFromDatasets({ ah, ab, ipo, bonds, merger, monitors = [] }) {
  return buildOverviewViewModel({
    ah,
    ab,
    ipo,
    bonds,
    merger,
    monitors,
    today: getShanghaiParts().date,
    nowIso,
    summarizeMonitor,
  });
}

function pctText(value, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return '--';
  const sign = num > 0 ? '+' : '';
  return `${sign}${num.toFixed(digits)}%`;
}

function pickText(value, fallback = '--') {
  const text = String(value ?? '').trim();
  return text || fallback;
}

function normalizePushConfig(input = {}) {
  return pushConfigDomain.normalizePushConfig(input);
}

function getPushConfig() {
  return pushConfigDomain.getPushConfig();
}

function topN(rows, count, compareFn) {
  return [...rows].sort(compareFn).slice(0, count);
}

function normalizeDateText(value) {
  return sharedNormalizeDateText(value);
}

let mergerStrategyDomain = null;

function getMergerStrategyDomain() {
  if (!mergerStrategyDomain) {
    // 并购策略只接收通用日期与文本工具，保持与抓取层、通知层解耦。
    mergerStrategyDomain = createMergerStrategy({
      normalizeDateText,
      pickText,
    });
  }
  return mergerStrategyDomain;
}

function mergerAnnouncementDate(row) {
  return getMergerStrategyDomain().mergerAnnouncementDate(row);
}

function mergerCompanyCode(row) {
  return getMergerStrategyDomain().mergerCompanyCode(row);
}

function mergerCompanyName(row) {
  return getMergerStrategyDomain().mergerCompanyName(row);
}

function mergerCompanyKey({ date, code, name }) {
  return getMergerStrategyDomain().mergerCompanyKey({ date, code, name });
}

function getMergerReportsMap() {
  if (!mergerReportStore.reports || typeof mergerReportStore.reports !== 'object') {
    mergerReportStore.reports = {};
  }
  return mergerReportStore.reports;
}

function getMergerReportByCompany({ date, code, name }) {
  const key = mergerCompanyKey({ date, code, name });
  return getMergerReportsMap()[key] || null;
}

function createEmptyEventArbitrageCategories() {
  return {
    hk_private: [],
    cn_private: [],
    a_event: [],
    rights_issue: [],
    announcement_pool: [],
  };
}

function normalizeSecurityCode(value) {
  return String(value || '')
    .trim()
    .toUpperCase()
    .replace(/[^0-9A-Z]/g, '');
}

function buildEventArbitrageSourceStatusEntry(sourceName, patch = {}) {
  const defaults = {
    hk_private: {
      enabled: true,
      status: 'empty',
      itemCount: 0,
      source: 'jisilu',
      sourceUrl: 'https://www.jisilu.cn/data/taoligu/hk_arbitrage_list/',
      servedFromCache: false,
      updateTime: nowIso(),
    },
    cn_private: {
      enabled: true,
      status: 'empty',
      itemCount: 0,
      source: 'jisilu',
      sourceUrl: 'https://www.jisilu.cn/data/taoligu/cn_arbitrage_list/',
      servedFromCache: false,
      updateTime: nowIso(),
    },
    a_event: {
      enabled: true,
      status: 'empty',
      itemCount: 0,
      source: 'jisilu',
      sourceUrl: 'https://www.jisilu.cn/data/taoligu/astock_arbitrage_list/',
      servedFromCache: false,
      updateTime: nowIso(),
    },
    rights_issue: {
      enabled: false,
      status: 'disabled_no_public_source',
      itemCount: 0,
      source: 'jisilu',
      sourceUrl: '',
      servedFromCache: false,
      updateTime: nowIso(),
    },
    announcement_pool: {
      enabled: true,
      status: 'empty',
      itemCount: 0,
      source: 'cninfo',
      sourceUrl: '/api/market/merger',
      servedFromCache: false,
      updateTime: nowIso(),
    },
  };
  return { ...(defaults[sourceName] || {}), ...cloneJsonSafe(patch, {}) };
}

function buildExternalEventArbitrageFallback(error) {
  const message = normalizeError(error || 'event_arbitrage fetch failed');
  const categories = createEmptyEventArbitrageCategories();
  return {
    success: true,
    data: {
      overview: {
        totalCount: 0,
        positiveCount: 0,
        hkPrivateCount: 0,
        cnPrivateCount: 0,
        aEventCount: 0,
        announcementPoolCount: 0,
      },
      categories,
      sourceStatus: {
        hk_private: buildEventArbitrageSourceStatusEntry('hk_private', { status: 'error', error: message }),
        cn_private: buildEventArbitrageSourceStatusEntry('cn_private', { status: 'error', error: message }),
        a_event: buildEventArbitrageSourceStatusEntry('a_event', { status: 'error', error: message }),
        rights_issue: buildEventArbitrageSourceStatusEntry('rights_issue'),
        announcement_pool: buildEventArbitrageSourceStatusEntry('announcement_pool', { status: 'pending' }),
      },
      updateTime: nowIso(),
      cacheTime: null,
      servedFromCache: false,
    },
    error: null,
    updateTime: nowIso(),
    source: 'jisilu',
  };
}

function readEventArbitrageCategories(payload) {
  const categories = payload?.data?.categories;
  return categories && typeof categories === 'object' ? categories : createEmptyEventArbitrageCategories();
}

function readEventArbitrageSourceStatus(payload) {
  const sourceStatus = payload?.data?.sourceStatus;
  return sourceStatus && typeof sourceStatus === 'object' ? sourceStatus : {};
}

function eventArbitrageLatestTime(...values) {
  return values
    .map((item) => String(item || '').trim())
    .filter(Boolean)
    .sort()
    .pop() || nowIso();
}

function isAnnouncementWithinLookback(row, lookbackDays = EVENT_ARB_MATCH_LOOKBACK_DAYS) {
  if (!lookbackDays || lookbackDays < 0) return true;
  const normalizedDate = normalizeDateText(mergerAnnouncementDate(row));
  if (!normalizedDate) return false;
  const timestamp = Date.parse(`${normalizedDate}T00:00:00+08:00`);
  if (!Number.isFinite(timestamp)) return false;
  return (Date.now() - timestamp) <= (lookbackDays * 24 * 60 * 60 * 1000);
}

function buildAnnouncementPoolSourceStatus(mergerPayload, rows) {
  if (mergerPayload?.success === false) {
    return buildEventArbitrageSourceStatusEntry('announcement_pool', {
      status: 'error',
      error: normalizeError(mergerPayload?.error || 'announcement pool fetch failed'),
      itemCount: Array.isArray(rows) ? rows.length : 0,
      servedFromCache: false,
      updateTime: mergerPayload?.updateTime || nowIso(),
    });
  }
  return buildEventArbitrageSourceStatusEntry('announcement_pool', {
    status: mergerPayload?.servedFromCache ? 'stale_cache' : (Array.isArray(rows) && rows.length ? 'ok' : 'empty'),
    itemCount: Array.isArray(rows) ? rows.length : 0,
    servedFromCache: Boolean(mergerPayload?.servedFromCache),
    updateTime: mergerPayload?.updateTime || nowIso(),
  });
}

function buildMergerAnnouncementIndex(rows, lookbackDays = EVENT_ARB_MATCH_LOOKBACK_DAYS) {
  const index = new Map();
  for (const row of Array.isArray(rows) ? rows : []) {
    const code = normalizeSecurityCode(mergerCompanyCode(row));
    if (!code || !isAnnouncementWithinLookback(row, lookbackDays)) continue;
    const current = index.get(code);
    const nextTime = Number(row?.announcementTime || 0);
    const currentTime = Number(current?.announcementTime || 0);
    if (!current || nextTime >= currentTime) {
      index.set(code, row);
    }
  }
  return index;
}

function buildOfficialMatch(row) {
  const date = mergerAnnouncementDate(row);
  const code = mergerCompanyCode(row);
  const name = mergerCompanyName(row);
  const report = getMergerReportByCompany({ date, code, name });
  return {
    matched: true,
    announcementId: row?.announcementId || null,
    title: pickText(row?.title, ''),
    announcementDate: date || '',
    pdfUrl: pickText(row?.pdfUrl, ''),
    reportAvailable: Boolean(report?.reportMarkdown),
  };
}

function enrichEventArbitrageRows(rows, announcementIndex) {
  return (Array.isArray(rows) ? rows : []).map((row) => {
    if (!row || typeof row !== 'object') return row;
    const symbol = normalizeSecurityCode(row?.symbol || row?.raw?.stock_code || row?.raw?.stock_id);
    const matchedRow = EVENT_ARB_MATCH_MODE === 'sec_code_only' ? announcementIndex.get(symbol) : null;
    return {
      ...row,
      officialMatch: matchedRow ? buildOfficialMatch(matchedRow) : null,
    };
  });
}

function buildEventArbitrageOverview(categories, sourceStatus) {
  const hkRows = Array.isArray(categories?.hk_private) ? categories.hk_private : [];
  const cnRows = Array.isArray(categories?.cn_private) ? categories.cn_private : [];
  const aRows = Array.isArray(categories?.a_event) ? categories.a_event : [];
  const rightsRows = Array.isArray(categories?.rights_issue) ? categories.rights_issue : [];
  const announcementRows = Array.isArray(categories?.announcement_pool) ? categories.announcement_pool : [];
  const eventRows = [...hkRows, ...cnRows, ...aRows];
  const matchedRows = eventRows.filter((row) => row?.officialMatch?.matched);
  const latestUpdateTime = eventArbitrageLatestTime(
    ...Object.values(sourceStatus || {}).map((item) => item?.updateTime)
  );
  return {
    totalCount: eventRows.length,
    positiveCount: eventRows.filter((row) => Number(row?.spreadRate) > 0).length,
    hkPrivateCount: hkRows.length,
    cnPrivateCount: cnRows.length,
    aEventCount: aRows.length,
    rightsIssueCount: rightsRows.length,
    announcementPoolCount: announcementRows.length,
    matchedCount: matchedRows.length,
    todayMatchedCount: matchedRows.filter((row) => normalizeDateText(row?.officialMatch?.announcementDate) === getShanghaiParts().date).length,
    latestUpdateTime,
  };
}

function buildEventArbitrageDatasetPayload(externalPayload, mergerPayload) {
  const basePayload = externalPayload?.success === false ? buildExternalEventArbitrageFallback(externalPayload?.error) : externalPayload;
  const categories = createEmptyEventArbitrageCategories();
  const externalCategories = readEventArbitrageCategories(basePayload);
  const announcementPoolRows = Array.isArray(mergerPayload?.data) ? mergerPayload.data : [];
  const announcementIndex = buildMergerAnnouncementIndex(announcementPoolRows, EVENT_ARB_MATCH_LOOKBACK_DAYS);

  categories.hk_private = enrichEventArbitrageRows(externalCategories.hk_private, announcementIndex);
  categories.cn_private = enrichEventArbitrageRows(externalCategories.cn_private, announcementIndex);
  categories.a_event = enrichEventArbitrageRows(externalCategories.a_event, announcementIndex);
  categories.rights_issue = Array.isArray(externalCategories.rights_issue) ? externalCategories.rights_issue : [];
  categories.announcement_pool = announcementPoolRows;

  const sourceStatus = {
    hk_private: buildEventArbitrageSourceStatusEntry('hk_private', readEventArbitrageSourceStatus(basePayload).hk_private),
    cn_private: buildEventArbitrageSourceStatusEntry('cn_private', readEventArbitrageSourceStatus(basePayload).cn_private),
    a_event: buildEventArbitrageSourceStatusEntry('a_event', readEventArbitrageSourceStatus(basePayload).a_event),
    rights_issue: buildEventArbitrageSourceStatusEntry('rights_issue', readEventArbitrageSourceStatus(basePayload).rights_issue),
    announcement_pool: buildAnnouncementPoolSourceStatus(mergerPayload, announcementPoolRows),
  };

  const updateTime = eventArbitrageLatestTime(
    basePayload?.data?.updateTime,
    basePayload?.updateTime,
    mergerPayload?.updateTime
  );
  const cacheTime = eventArbitrageLatestTime(
    basePayload?.data?.cacheTime,
    basePayload?.cacheTime,
    mergerPayload?.cacheTime
  );
  const servedFromCache = Boolean(basePayload?.servedFromCache || mergerPayload?.servedFromCache);
  const overview = buildEventArbitrageOverview(categories, sourceStatus);

  return {
    success: true,
    data: {
      overview,
      categories,
      sourceStatus,
      updateTime,
      cacheTime,
      servedFromCache,
    },
    error: null,
    updateTime,
    cacheTime,
    servedFromCache,
  };
}

async function buildEventArbitrageDataset(options = {}) {
  const externalPayload = await callDataCore(['event-arbitrage'], {
    timeout: 120000,
    maxBuffer: 1024 * 1024 * 50,
  });
  let mergerPayload = null;
  try {
    mergerPayload = await getDataset('merger', options.force ? { force: true } : {});
  } catch (error) {
    mergerPayload = {
      success: false,
      data: [],
      error: normalizeError(error),
      updateTime: nowIso(),
    };
  }
  return buildEventArbitrageDatasetPayload(externalPayload, mergerPayload);
}

function upsertMergerReportByCompany(report) {
  const key = mergerCompanyKey(report || {});
  const map = getMergerReportsMap();
  map[key] = {
    key,
    date: normalizeDateText(report?.date),
    code: pickText(report?.code, '--'),
    name: pickText(report?.name, '--'),
    reportMarkdown: String(report?.reportMarkdown || '').trim(),
    questionPrompt: String(report?.questionPrompt || '').trim(),
    announcements: Array.isArray(report?.announcements) ? report.announcements : [],
    snapshot: String(report?.snapshot || '').trim(),
    createdAt: report?.createdAt || nowIso(),
    updatedAt: nowIso(),
  };
  saveMergerReportStore();
  return map[key];
}

function groupTodayMergerRowsByCompany(mergerRows, date = getShanghaiParts().date) {
  return getMergerStrategyDomain().groupTodayMergerRowsByCompany(mergerRows, date);
}

function collectTodaySubscriptionEvents(ipo, bonds) {
  const today = getShanghaiParts().date;
  const ipoRows = [
    ...(Array.isArray(ipo?.upcoming) ? ipo.upcoming : []),
    ...(Array.isArray(ipo?.data) ? ipo.data : []),
  ];
  const bondRows = [
    ...(Array.isArray(bonds?.upcoming) ? bonds.upcoming : []),
    ...(Array.isArray(bonds?.data) ? bonds.data : []),
  ];

  const build = (rows, typeLabel) => rows.flatMap((row) => {
    const name = pickText(row.name || row.stockName || row.bondName);
    const code = pickText(row.code || row.stockCode || row.bondCode);
    const events = [];
    if (String(row.subscribeDate || '') === today) events.push({ event: '申购', date: row.subscribeDate, type: typeLabel, code, name });
    if (String(row.paymentDate || '') === today) events.push({ event: '缴款', date: row.paymentDate, type: typeLabel, code, name });
    if (String(row.listingDate || '') === today) events.push({ event: '上市', date: row.listingDate, type: typeLabel, code, name });
    return events;
  });
  const eventOrder = { '申购': 0, '缴款': 1, '上市': 2 };
  const typeOrder = { '新股': 0, '新债': 1 };
  return [...build(ipoRows, '新股'), ...build(bondRows, '新债')].sort((a, b) => {
    const eventDelta = (eventOrder[a.event] ?? 99) - (eventOrder[b.event] ?? 99);
    if (eventDelta !== 0) return eventDelta;
    const typeDelta = (typeOrder[a.type] ?? 99) - (typeOrder[b.type] ?? 99);
    if (typeDelta !== 0) return typeDelta;
    return String(a.code || '').localeCompare(String(b.code || ''), 'zh-Hans-CN');
  });
}

function cbArbOpportunitySets(rows) {
  const toNum = (value) => (Number.isFinite(Number(value)) ? Number(value) : null);
  const formatDate = (value) => String(value || '').trim();
  const hasPassedConvertStart = (row) => {
    const text = formatDate(row.convertStartDate || row.convertStartDateTime);
    if (!text) return false;
    const t = Date.parse(text);
    return Number.isFinite(t) ? t <= Date.now() : false;
  };
  const putbackValue = (row) => {
    const putbackPrice = toNum(row.putbackPrice);
    const putbackTrigger = toNum(row.putbackTriggerPrice);
    if (putbackPrice !== null && putbackPrice > 0) return putbackPrice;
    if (putbackTrigger !== null && putbackTrigger > 0) return putbackTrigger;
    return null;
  };
  const convertSpreadRate = (row) => {
    const convertValue = toNum(row.convertValue);
    const price = toNum(row.price);
    if (convertValue === null || price === null || price === 0) return null;
    return ((convertValue - price) / price) * 100;
  };

  return {
    doubleLow: topN(
      rows.filter((row) => toNum(row.doubleLow) !== null),
      3,
      (a, b) => (toNum(a.doubleLow) ?? Number.POSITIVE_INFINITY) - (toNum(b.doubleLow) ?? Number.POSITIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `双低最低：${(toNum(row.doubleLow) ?? 0).toFixed(2)}`,
    })),
    theoPremium: topN(
      rows.filter((row) => toNum(row.theoreticalPremiumRate) !== null),
      3,
      (a, b) => (toNum(b.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY) - (toNum(a.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `理论溢价率最高：${pctText(row.theoreticalPremiumRate)}`,
    })),
    redeem: topN(
      rows.filter((row) => {
        const price = toNum(row.price);
        const stockPrice = toNum(row.stockPrice);
        const redeemValue = putbackValue(row);
        const years = toNum(row.remainingYears);
        return price !== null && stockPrice !== null && redeemValue !== null && years !== null
          && price < redeemValue && stockPrice < redeemValue && years <= 2;
      }),
      3,
      (a, b) => ((putbackValue(b) ?? 0) - (toNum(b.price) ?? 0)) - ((putbackValue(a) ?? 0) - (toNum(a.price) ?? 0))
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `回售执行价高于现价，差额 ${(putbackValue(row) - (toNum(row.price) || 0)).toFixed(2)}`,
    })),
    limitUp: topN(
      rows.filter((row) => (toNum(row.stockChangePercent) ?? -999) >= 9.5),
      3,
      (a, b) => (toNum(b.stockChangePercent) ?? Number.NEGATIVE_INFINITY) - (toNum(a.stockChangePercent) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `正股接近/触及涨停：${pctText(row.stockChangePercent)}`,
    })),
    convert: topN(
      rows.filter((row) => {
        const spread = convertSpreadRate(row);
        return spread !== null && spread > 2 && hasPassedConvertStart(row);
      }),
      3,
      (a, b) => (convertSpreadRate(b) ?? Number.NEGATIVE_INFINITY) - (convertSpreadRate(a) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `转股套利空间 ${pctText(convertSpreadRate(row))}`,
    })),
    delist: topN(
      rows.filter((row) => (toNum(row.price) ?? 9999) < 100),
      3,
      (a, b) => (toNum(a.price) ?? Number.POSITIVE_INFINITY) - (toNum(b.price) ?? Number.POSITIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `低于面值博弈，现价 ${(toNum(row.price) ?? 0).toFixed(2)}`,
    })),
  };
}

function buildWeComSummaryMarkdown(input, modules) {
  return buildNotificationSummaryMarkdown(input, modules || getPushConfig().modules, {
    generatedAtText: new Date().toLocaleString('zh-CN', { hour12: false }),
    todayText: getShanghaiParts().date,
    todayDividendRecord: upcomingDividends(1),
  });
}

async function sendWeComMarkdown(markdown) {
  return weComClient.sendMarkdown(markdown);
}

async function collectSummaryDatasets() {
  const [ah, ab, ipo, bonds, cbArb, merger, monitors] = await Promise.all([
    getDataset('ah'),
    getDataset('ab'),
    getDataset('ipo'),
    getDataset('bonds'),
    getDataset('cbArb'),
    getDataset('merger'),
    getAllMonitors(),
  ]);
  return { ah, ab, ipo, bonds, cbArb, merger, monitors };
}

async function pushSummaryToWeCom(options = {}) {
  return mainSummaryService.pushSummaryToWeCom(options);
}

function getPushRecordMap(recordType) {
  return pushRuntimeDomain.getPushRecordMap(recordType);
}

function getPushRecord(recordType, date) {
  return pushRuntimeDomain.getPushRecord(recordType, date);
}

function setPushRecord(recordType, date, times) {
  return pushRuntimeDomain.setPushRecord(recordType, date, times);
}

async function callDeepSeekChatCompletion({ systemPrompt, userPrompt, temperature = 0.2 }) {
  if (!DEEPSEEK_API_KEY) {
    throw new Error('未配置 DEEPSEEK_API_KEY');
  }
  const response = await fetch(`${DEEPSEEK_BASE_URL.replace(/\/$/, '')}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${DEEPSEEK_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      temperature,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
    }),
  });

  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  const content = payload?.choices?.[0]?.message?.content;
  if (!response.ok || !content) {
    const message = payload?.error?.message || payload?.message || 'DeepSeek 返回异常';
    throw new Error(`DeepSeek 分析失败: ${message}`);
  }
  return String(content || '').trim();
}

function buildMergerCompanyQuestionPrompt(company, rows, date) {
  const first = rows[0] || {};
  const dealType = pickText(first.dealType || first.type, '--');
  const sourceHints = rows
    .slice(0, 5)
    .map((row) => pickText(row.announcementUrl || row.url || row.link, ''))
    .filter(Boolean)
    .join('；');

  return [
    `模板代码:${MERGER_PROMPT_TEMPLATE_CODE}。`,
    '你是并购事实核验分析师。请先联网搜索并交叉验证（公司公告、交易所、主流财经媒体），不得臆测或编造。',
    `公司:${pickText(company.name)}(${pickText(company.code)}) 截止日期:${date} 交易类型:${dealType}`,
    '只做两件事：介绍这笔交易 + 说明交易对价。',
    `线索链接:${sourceHints || '无'}`,
    '按固定字段输出：',
    '【交易介绍】收购方、被收购方、交易对象、交易方式（如要约收购/资产收购等）、当前交易状态。',
    '【交易对价】总对价、单价、现金与换股安排（含换股比例）、支付安排与生效条件；未披露项明确写“未披露”。',
    '【信息来源】列出1-2条可核验链接。',
    `必须中文，信息完整，回答总长度不超过${MERGER_REPORT_MAX_CHARS}字。`,
  ].join(' ');
}

function buildMergerCompanySnapshot(rows) {
  return JSON.stringify(
    rows.map((row) => ({
      t: pickText(row.title || row.announcementTitle, ''),
      d: mergerAnnouncementDate(row),
      p: Number(row.stockPrice || row.price),
      o: Number(row.offerPrice || row.bidPrice),
      u: pickText(row.announcementUrl || row.url || row.link, ''),
    }))
  );
}

async function buildMergerCompanyReportMarkdown(company, rows, date) {
  const questionPrompt = buildMergerCompanyQuestionPrompt(company, rows, date);
  let content = await callDeepSeekChatCompletion({
    systemPrompt: `你是严谨的并购信息分析师。严格按用户给定模板代码与字段顺序作答，只输出“交易介绍”和“交易对价”相关信息，不要扩展到套利、风险或公告解读。最终回答必须为中文，且总长度不超过${MERGER_REPORT_MAX_CHARS}字。`,
    userPrompt: questionPrompt,
    temperature: 0.2,
  });
  let conciseContent = String(content || '').trim();
  if (Array.from(conciseContent).length > MERGER_REPORT_MAX_CHARS) {
    content = await callDeepSeekChatCompletion({
      systemPrompt: '你是金融编辑，负责在不丢失关键信息的前提下做压缩改写。',
      userPrompt: `请将以下内容压缩改写为中文，仅保留“交易介绍”和“交易对价”核心信息，不要新增事实，严格控制在${MERGER_REPORT_MAX_CHARS}字以内：\n${conciseContent}`,
      temperature: 0.1,
    });
    conciseContent = String(content || '').trim();
  }
  return {
    markdown: `# 并购公司报告：${pickText(company.name)}(${pickText(company.code)})\n> ${new Date().toLocaleString('zh-CN', { hour12: false })}\n\n${conciseContent}`,
    questionPrompt,
  };
}

async function getTodayMergerGroups() {
  const merger = await getDataset('merger');
  const mergerRows = Array.isArray(merger?.data) ? merger.data : [];
  const date = getShanghaiParts().date;
  const groups = groupTodayMergerRowsByCompany(mergerRows, date);
  return { date, groups };
}

async function ensureMergerCompanyReport({ date, code, name, force = false }) {
  return mergerReportService.ensureMergerCompanyReport({ date, code, name, force });
}

async function pushMergerReportsByCompanyToWeCom(options = {}) {
  return mergerReportService.pushMergerReportsByCompanyToWeCom(options);
}

async function pushMergerReportToWeCom(options = {}) {
  const result = await mergerReportService.pushMergerReportsByCompanyToWeCom(options);
  if (result.sentCount > 0) {
    pushRuntimeDomain.setLastMergerReportDate(result.date);
    pushRuntimeDomain.save();
  }
  return result;
}

async function pushByModulesToWeCom(options = {}) {
  return mainSummaryService.pushByModulesToWeCom(options);
}

async function runMainPushIfNeeded() {
  return weComScheduler.runMainPushIfNeeded();
}

async function runMergerPushIfNeeded() {
  return weComScheduler.runMergerPushIfNeeded();
}

function normalizeError(error) {
  return sharedNormalizeError(error);
}

function pickExtra(payload = {}) {
  const extra = {};
  if (!payload || typeof payload !== 'object') return extra;
  for (const [key, value] of Object.entries(payload)) {
    if (!['success', 'data', 'error'].includes(key)) extra[key] = value;
  }
  return extra;
}

function sendSuccess(res, data = null, extra = {}, status = 200) {
  return res.status(status).json({ success: true, data, error: null, ...extra });
}

function sendError(res, error, status = 500, data = null, extra = {}) {
  return res.status(status).json({ success: false, data, error: normalizeError(error), ...extra });
}

function sendServiceResult(res, result, defaultData = null, errorStatus = 500) {
  if (result && typeof result === 'object' && Object.prototype.hasOwnProperty.call(result, 'success')) {
    if (result.success) {
      return sendSuccess(
        res,
        Object.prototype.hasOwnProperty.call(result, 'data') ? result.data : defaultData,
        pickExtra(result)
      );
    }
    return sendError(
      res,
      result.error || 'Request failed',
      Number(result.statusCode || errorStatus),
      Object.prototype.hasOwnProperty.call(result, 'data') ? result.data : defaultData,
      pickExtra(result)
    );
  }
  return sendSuccess(res, result ?? defaultData);
}

const app = express();
app.set('trust proxy', TRUST_PROXY);
app.use(cors());
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: false }));
app.use('/presentation', express.static(path.resolve(ROOT, 'presentation')));

registerMarketRoutes({
  app,
  nowIso,
  getDataset,
  normalizeDatasetPayload,
  sendSuccess,
  sendError,
  sendServiceResult,
  callDataCore,
  getStockPrice,
  stockSearchDefaultLimit: toIntConfig(PRESENTATION_STOCK_SEARCH_CONFIG.default_limit, 10),
  stockSearchMaxLimit: toIntConfig(PRESENTATION_STOCK_SEARCH_CONFIG.max_limit, 100),
  stockSearchTimeoutMs: toIntConfig(PRESENTATION_STOCK_SEARCH_CONFIG.timeout_ms, 30000),
  historicalPremiumDefaultDays: toIntConfig(PRESENTATION_HISTORICAL_PREMIUM_CONFIG.default_days, 1825),
  historicalPremiumMaxDays: toIntConfig(PRESENTATION_HISTORICAL_PREMIUM_CONFIG.max_days, 10000),
  historicalPremiumTimeoutMs: toIntConfig(PRESENTATION_HISTORICAL_PREMIUM_CONFIG.timeout_ms, 100000),
});

registerPushRoutes({
  app,
  sendSuccess,
  sendError,
  getPushConfig,
  updatePushConfig: (payload) => pushConfigDomain.updatePushConfig(payload),
  buildPushConfigResponse: buildPushConfigViewModel,
  getPushRuntimeState: () => pushRuntimeState,
  pushByModulesToWeCom,
  pushMergerReportToWeCom,
});

registerDashboardRoutes({
  app,
  nowIso,
  getHealthSnapshot: buildHealthSnapshot,
  getShanghaiParts,
  normalizeDateText,
  pickText,
  sendSuccess,
  sendError,
  sendServiceResult,
  getAllMonitors,
  upsertMonitor,
  deleteMonitor,
  loadPortfolio,
  refreshPortfolio,
  addDividendStock,
  removeDividendStock,
  upcomingDividends,
  callDataCore,
  getDataset,
  getTodayMergerGroups,
  getMergerReportByCompany,
  ensureMergerCompanyReport,
  mergerCompanyCode,
  mergerCompanyName,
  mergerCompanyKey,
  mergerAnnouncementDate,
  getOverviewFromDatasets,
  dividendUpcomingDefaultDays: toIntConfig(PRESENTATION_DIVIDEND_CONFIG.default_upcoming_days, 7),
  dividendUpcomingMaxDays: toIntConfig(PRESENTATION_DIVIDEND_CONFIG.max_upcoming_days, 365),
  stockSearchDefaultLimit: toIntConfig(PRESENTATION_STOCK_SEARCH_CONFIG.default_limit, 10),
  stockSearchMaxLimit: toIntConfig(PRESENTATION_STOCK_SEARCH_CONFIG.max_limit, 100),
  stockSearchTimeoutMs: toIntConfig(PRESENTATION_STOCK_SEARCH_CONFIG.timeout_ms, 30000),
});

app.use('/api', (req, res) => {
  return sendError(
    res,
    `API not found: ${req.method} ${req.path}`,
    404,
    null
  );
});

app.get('*', (_req, res) => res.sendFile(INDEX_FILE));

const server = app.listen(PORT, HOST, () => {
  updateHealthSection('web', 'ok', 'HTTP service is healthy', {
    environment: APP_ENVIRONMENT,
    host: HOST,
    port: PORT,
    internalUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
    healthcheckPath: HEALTHCHECK_PATH,
    trustProxy: TRUST_PROXY,
    reverseProxyEnabled: REVERSE_PROXY_ENABLED,
    reverseProxyType: REVERSE_PROXY_TYPE,
    systemdServiceName: SYSTEMD_SERVICE_NAME,
  });
  console.log(`Alpha Monitor internal URL: ${SERVER_BASE_URL}`);
  console.log(`Alpha Monitor public URL : ${PUBLIC_BASE_URL}`);
  console.log(`Alpha Monitor health URL : ${PUBLIC_HEALTHCHECK_URL}`);
  startScheduler();
});

server.on('error', (error) => {
  updateHealthSection('web', 'fail', `HTTP service failed: ${error?.message || error}`, {
    environment: APP_ENVIRONMENT,
    host: HOST,
    port: PORT,
    internalUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
    errorCode: error?.code || '',
  });
  logFatal('server_error', error);
  if (error?.code === 'EADDRINUSE') {
    console.error(`[fatal] port ${PORT} already in use`);
  }
  process.exit(1);
});

function gracefulShutdown(signal) {
  if (shuttingDown) return;
  shuttingDown = true;
  updateHealthSection('web', 'fail', `HTTP service is stopping due to ${signal}`, {
    environment: APP_ENVIRONMENT,
    host: HOST,
    port: PORT,
    internalUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
  });
  console.log(`[shutdown] received ${signal}`);
  if (refreshTimer) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
  server.close(() => {
    console.log('[shutdown] http server closed');
    process.exit(0);
  });
  setTimeout(() => process.exit(0), SHUTDOWN_GRACE_TIMEOUT_MS).unref?.();
}

process.on('uncaughtException', (error) => {
  updateHealthSection('web', 'fail', `Process crashed with uncaughtException: ${error?.message || error}`, {
    environment: APP_ENVIRONMENT,
    host: HOST,
    port: PORT,
    internalUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
  });
  logFatal('uncaughtException', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  updateHealthSection('web', 'fail', `Process crashed with unhandledRejection: ${reason?.message || reason}`, {
    environment: APP_ENVIRONMENT,
    host: HOST,
    port: PORT,
    internalUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
  });
  logFatal('unhandledRejection', reason);
  process.exit(1);
});

process.on('SIGINT', () => gracefulShutdown('SIGINT'));
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));





