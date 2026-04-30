// AI-SUMMARY: 服务器配置加载：端口/路径/策略/超时等配置读取
// 对应 INDEX.md §9 文件摘要索引

'use strict';

const path = require('path');
const { getConfig } = require('./shared/config/node_config');
const { getPathPolicy } = require('./shared/paths/node_paths');

function toIntConfig(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function toPositiveNumberConfig(value, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function toNumConfigOrFallback(value, fallback) {
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

function normalizeSessionWindowText(value) {
  const text = String(value || '').trim();
  const hit = text.match(/^(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})$/);
  if (!hit) return '';
  const start = normalizeTimeConfig(hit[1], '');
  const end = normalizeTimeConfig(hit[2], '');
  if (!start || !end || start >= end) return '';
  return `${start}-${end}`;
}

function normalizeSessionWindowListConfig(values, fallback = []) {
  const source = Array.isArray(values) ? values : [];
  const items = Array.from(new Set(
    source
      .map((item) => normalizeSessionWindowText(item))
      .filter(Boolean)
  ));
  return items.length ? items : [...fallback];
}

function isLoopbackHost(hostname) {
  const text = String(hostname || '').trim().toLowerCase();
  return text === '127.0.0.1' || text === 'localhost' || text === '0.0.0.0';
}

function isLoopbackUrl(urlText) {
  const text = String(urlText || '').trim();
  if (!text) return true;
  try {
    const parsed = new URL(text);
    return isLoopbackHost(parsed.hostname);
  } catch {
    return false;
  }
}

function pluginFetchConfig(dataFetchConfig, key) {
  const config = dataFetchConfig?.[key];
  return config && typeof config === 'object' ? config : {};
}

function buildNotificationModuleDefaults(notificationConfig) {
  const raw = (notificationConfig.enabled_modules && typeof notificationConfig.enabled_modules === 'object')
    ? notificationConfig.enabled_modules
    : {};
  return {
    ahab: raw.ahab !== false,
    subscription: raw.subscription !== false,
    monitor: raw.custom_monitor !== false,
    dividend: raw.dividend !== false,
    eventArb: raw.event_arbitrage !== false,
  };
}

function loadServerConfig() {
  const ROOT = path.resolve(__dirname);
  const APP_CONFIG = getConfig();
  const PATH_POLICY = getPathPolicy();
  const DATA_FETCH_CONFIG = APP_CONFIG?.data_fetch?.plugins || {};
  const STRATEGY_CONFIG = APP_CONFIG?.strategy || {};
  const PRESENTATION_CONFIG = APP_CONFIG?.presentation || {};
  const NOTIFICATION_CONFIG = APP_CONFIG?.notification || {};
  const PRESENTATION_STOCK_SEARCH_CONFIG = PRESENTATION_CONFIG?.stock_search || {};
  const PRESENTATION_DIVIDEND_CONFIG = PRESENTATION_CONFIG?.dividend || {};
  const PRESENTATION_HISTORICAL_PREMIUM_CONFIG = PRESENTATION_CONFIG?.historical_premium || {};
  const PRESENTATION_DASHBOARD_TABLE_UI_CONFIG = PRESENTATION_CONFIG?.dashboard_table_ui || {};
  const PRESENTATION_DASHBOARD_MODULE_NOTES_CONFIG = PRESENTATION_CONFIG?.dashboard_module_notes || {};
  const PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG = PRESENTATION_CONFIG?.dashboard_auto_refresh || {};
  const EVENT_ARB_STRATEGY_CONFIG = STRATEGY_CONFIG?.event_arbitrage || {};
  const CONVERTIBLE_BOND_STRATEGY_CONFIG = (STRATEGY_CONFIG?.convertible_bond && typeof STRATEGY_CONFIG.convertible_bond === 'object')
    ? STRATEGY_CONFIG.convertible_bond
    : {};
  const CB_RIGHTS_ISSUE_STRATEGY_CONFIG = (STRATEGY_CONFIG?.cb_rights_issue && typeof STRATEGY_CONFIG.cb_rights_issue === 'object')
    ? STRATEGY_CONFIG.cb_rights_issue
    : {};
  const CB_RIGHTS_ISSUE_NOTIFICATION_CONFIG = (NOTIFICATION_CONFIG?.cb_rights_issue && typeof NOTIFICATION_CONFIG.cb_rights_issue === 'object')
    ? NOTIFICATION_CONFIG.cb_rights_issue
    : {};
  const CB_ARBITRAGE_NOTIFICATION_CONFIG = (NOTIFICATION_CONFIG?.cb_arbitrage && typeof NOTIFICATION_CONFIG.cb_arbitrage === 'object')
    ? NOTIFICATION_CONFIG.cb_arbitrage
    : {};
  const LOF_ARBITRAGE_NOTIFICATION_CONFIG = (NOTIFICATION_CONFIG?.lof_arbitrage && typeof NOTIFICATION_CONFIG.lof_arbitrage === 'object')
    ? NOTIFICATION_CONFIG.lof_arbitrage
    : {};

  const INDEX_FILE = path.resolve(
    ROOT,
    PRESENTATION_CONFIG.dashboard_entry || './ui/templates/dashboard_template.html'
  );

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
  const PUSH_HTML_URL = String(NOTIFICATION_CONFIG?.wecom?.push_html_url || '').trim();
  const WECOM_MAX_MARKDOWN_LENGTH = toIntConfig(NOTIFICATION_CONFIG?.wecom?.max_markdown_length, 3900);
  const DEEPSEEK_API_KEY = String(STRATEGY_CONFIG?.merger?.deepseek_api_key || '').trim();
  const DEEPSEEK_BASE_URL = String(STRATEGY_CONFIG?.merger?.deepseek_base_url || 'https://api.deepseek.com').trim();
  const MERGER_AI_MODEL = String(STRATEGY_CONFIG?.merger?.ai_model || 'deepseek-chat').trim();
  const MERGER_REPORT_MAX_CHARS = toIntConfig(STRATEGY_CONFIG?.merger?.report_max_chars, 500);
  const MERGER_PROMPT_TEMPLATE_CODE = String(STRATEGY_CONFIG?.merger?.prompt_template_code || 'MERGER_DEAL_OVERVIEW_V1').trim() || 'MERGER_DEAL_OVERVIEW_V1';
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
  const CB_ARB_FORCE_REQUEST_SOFT_TIMEOUT_MS = toIntConfig(
    pluginFetchConfig(DATA_FETCH_CONFIG, 'convertible_bond').force_request_soft_timeout_ms,
    55 * 1000
  );
  const DEFAULT_MAIN_PUSH_TIME = normalizeTimeConfig(NOTIFICATION_CONFIG?.default_full_push_time, '08:00');
  const DEFAULT_MAIN_PUSH_TIMES = normalizeTimeListConfig(
    NOTIFICATION_CONFIG?.scheduler?.default_times,
    DEFAULT_MAIN_PUSH_TIME
  );
  const NOTIFICATION_SUMMARY_CONFIG = (NOTIFICATION_CONFIG?.summary && typeof NOTIFICATION_CONFIG.summary === 'object')
    ? NOTIFICATION_CONFIG.summary
    : {};
  const PUSH_CALENDAR_MODE = String(NOTIFICATION_CONFIG?.scheduler?.calendar_mode || 'daily').trim().toLowerCase() || 'daily';
  const PUSH_SCHEDULER_RUNTIME_ENABLED = Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled) && !isLoopbackUrl(PUBLIC_BASE_URL);
  const PUSH_SCHEDULER_DISABLED_REASON = PUSH_SCHEDULER_RUNTIME_ENABLED
    ? ''
    : (Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled) ? 'loopback_public_base_url' : 'scheduler_config_disabled');
  const DEFAULT_NOTIFICATION_MODULES = buildNotificationModuleDefaults(NOTIFICATION_CONFIG);

  const DEFAULT_DISCOUNT_STRATEGY_MONITOR_TIMES = [
    '09:30', '09:40', '09:50', '10:00', '10:10', '10:20', '10:30', '10:40', '10:50', '11:00', '11:10', '11:20', '11:30',
    '13:00', '13:10', '13:20', '13:30', '13:40', '13:50', '14:00', '14:10', '14:20', '14:30', '14:40', '14:50',
  ];
  const DEFAULT_DISCOUNT_STRATEGY_CONFIG = {
    tradingDaysOnly: true,
    sessionWindows: ['09:30-11:30', '13:00-15:00'],
    buyThreshold: -2,
    sellThreshold: -0.5,
    monitorIntervalMinutes: 10,
    monitorSessionTimes: DEFAULT_DISCOUNT_STRATEGY_MONITOR_TIMES,
  };
  const DISCOUNT_STRATEGY_CONFIG = {
    tradingDaysOnly: toBooleanConfig(
      CONVERTIBLE_BOND_STRATEGY_CONFIG?.discount_strategy?.trading_days_only,
      DEFAULT_DISCOUNT_STRATEGY_CONFIG.tradingDaysOnly
    ),
    sessionWindows: normalizeSessionWindowListConfig(
      CONVERTIBLE_BOND_STRATEGY_CONFIG?.discount_strategy?.session_windows,
      DEFAULT_DISCOUNT_STRATEGY_CONFIG.sessionWindows
    ),
    buyThreshold: toNumConfigOrFallback(CONVERTIBLE_BOND_STRATEGY_CONFIG?.discount_strategy?.buy_threshold, DEFAULT_DISCOUNT_STRATEGY_CONFIG.buyThreshold),
    sellThreshold: toNumConfigOrFallback(CONVERTIBLE_BOND_STRATEGY_CONFIG?.discount_strategy?.sell_threshold, DEFAULT_DISCOUNT_STRATEGY_CONFIG.sellThreshold),
    monitorIntervalMinutes: toIntConfig(CONVERTIBLE_BOND_STRATEGY_CONFIG?.discount_strategy?.monitor_interval_minutes, DEFAULT_DISCOUNT_STRATEGY_CONFIG.monitorIntervalMinutes),
    monitorSessionTimes: Array.isArray(CONVERTIBLE_BOND_STRATEGY_CONFIG?.discount_strategy?.monitor_session_times)
      ? normalizeTimeListConfig(
        CONVERTIBLE_BOND_STRATEGY_CONFIG.discount_strategy.monitor_session_times,
        DEFAULT_DISCOUNT_STRATEGY_MONITOR_TIMES[0]
      )
      : DEFAULT_DISCOUNT_STRATEGY_MONITOR_TIMES,
  };
  const DEFAULT_PUSH_CONFIG = {
    enabled: Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled),
    time: DEFAULT_MAIN_PUSH_TIMES[0],
    times: DEFAULT_MAIN_PUSH_TIMES.slice(0, 2),
    modules: DEFAULT_NOTIFICATION_MODULES,
  };
  const DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG = {
    enabled: Boolean(CB_RIGHTS_ISSUE_NOTIFICATION_CONFIG?.enabled),
    times: normalizeTimeListConfig(
      CB_RIGHTS_ISSUE_NOTIFICATION_CONFIG?.default_times,
      '08:00'
    ).slice(0, 2),
    tradingDaysOnly: CB_RIGHTS_ISSUE_NOTIFICATION_CONFIG?.trading_days_only !== false,
  };
  const DEFAULT_CB_ARBITRAGE_PUSH_TIMES = (() => {
    if (!Array.isArray(CB_ARBITRAGE_NOTIFICATION_CONFIG?.default_times)) {
      return ['08:00', '14:30'];
    }
    const normalized = normalizeTimeListConfig(
      CB_ARBITRAGE_NOTIFICATION_CONFIG?.default_times,
      '08:00'
    );
    return normalized.slice(0, 2);
  })();
  const DEFAULT_CB_ARBITRAGE_PUSH_CONFIG = {
    enabled: typeof CB_ARBITRAGE_NOTIFICATION_CONFIG?.enabled === 'boolean'
      ? CB_ARBITRAGE_NOTIFICATION_CONFIG.enabled
      : (((NOTIFICATION_CONFIG?.enabled_modules && typeof NOTIFICATION_CONFIG.enabled_modules === 'object')
        ? NOTIFICATION_CONFIG.enabled_modules.cb_arb
        : true) !== false),
    times: DEFAULT_CB_ARBITRAGE_PUSH_TIMES,
    tradingDaysOnly: CB_ARBITRAGE_NOTIFICATION_CONFIG?.trading_days_only !== false,
  };
  const DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG = {
    enabled: Boolean(LOF_ARBITRAGE_NOTIFICATION_CONFIG?.enabled),
    times: normalizeTimeListConfig(
      LOF_ARBITRAGE_NOTIFICATION_CONFIG?.default_times,
      '08:00'
    ).slice(0, 2),
    tradingDaysOnly: LOF_ARBITRAGE_NOTIFICATION_CONFIG?.trading_days_only !== false,
  };

  const DASHBOARD_TABLE_UI = {
    desktopFontPx: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.desktop_font_px, 14),
    desktopHeaderFontPx: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.desktop_header_font_px, 14),
    desktopLineHeight: toNumConfigOrFallback(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.desktop_line_height, 1.58),
    desktopCellPaddingY: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.desktop_cell_padding_y, 10),
    desktopCellPaddingX: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.desktop_cell_padding_x, 12),
    tabletFontPx: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.tablet_font_px, 13),
    minWidthByKind: {
      subscription: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.subscription, 1180),
      convertible: Math.min(toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.convertible, 1340), 1340),
      premium: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.premium, 1240),
      monitor: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.monitor, 1320),
      dividend: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.dividend, 1100),
      merger: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.merger, 1280),
      lof: toIntConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG.min_width_by_kind?.lof, 1680),
    },
  };

  const DEFAULT_AUTO_REFRESH_CONFIG = {
    enabled: true,
    intervalMs: 30 * 1000,
    mode: 'status',
    currentTabOnly: true,
    reloadDataOnCacheChange: true,
  };
  const DASHBOARD_AUTO_REFRESH = {
    enabled: PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG?.enabled !== false,
    intervalMs: toPositiveNumberConfig(PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG?.interval_ms, DEFAULT_AUTO_REFRESH_CONFIG.intervalMs),
    mode: String(PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG?.mode || DEFAULT_AUTO_REFRESH_CONFIG.mode).trim() || DEFAULT_AUTO_REFRESH_CONFIG.mode,
    currentTabOnly: PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG?.current_tab_only !== false,
    reloadDataOnCacheChange: PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG?.reload_data_on_cache_change !== false,
  };

  const rawTheme = String(PRESENTATION_CONFIG?.dashboard_theme || 'classic').trim().toLowerCase();
  const DASHBOARD_THEME = rawTheme === 'clean_data' ? 'clean_data' : 'classic';

  const DASHBOARD_MODULE_NOTES = (() => {
    const config = PRESENTATION_DASHBOARD_MODULE_NOTES_CONFIG;
    if (!config || typeof config !== 'object') return {};
    const result = {};
    for (const [key, value] of Object.entries(config)) {
      if (value && typeof value === 'object') {
        result[key] = {
          dataSources: Array.isArray(value.dataSources) ? value.dataSources.filter(Boolean) : [],
          formulas: Array.isArray(value.formulas) ? value.formulas.filter(Boolean) : [],
          strategyNotes: Array.isArray(value.strategyNotes) ? value.strategyNotes.filter(Boolean) : [],
        };
      }
    }
    return result;
  })();

  return {
    ROOT,
    APP_CONFIG,
    PATH_POLICY,
    DATA_FETCH_CONFIG,
    STRATEGY_CONFIG,
    PRESENTATION_CONFIG,
    NOTIFICATION_CONFIG,
    PRESENTATION_STOCK_SEARCH_CONFIG,
    PRESENTATION_DIVIDEND_CONFIG,
    PRESENTATION_HISTORICAL_PREMIUM_CONFIG,
    PRESENTATION_DASHBOARD_TABLE_UI_CONFIG,
    PRESENTATION_DASHBOARD_MODULE_NOTES_CONFIG,
    PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG,
    EVENT_ARB_STRATEGY_CONFIG,
    CONVERTIBLE_BOND_STRATEGY_CONFIG,
    CB_RIGHTS_ISSUE_STRATEGY_CONFIG,
    CB_RIGHTS_ISSUE_NOTIFICATION_CONFIG,
    CB_ARBITRAGE_NOTIFICATION_CONFIG,
    LOF_ARBITRAGE_NOTIFICATION_CONFIG,
    INDEX_FILE,
    STATIC_DATA_DIR: PATH_POLICY.dataRootDir,
    SHARED_DATA_DIR: PATH_POLICY.sharedDataDir,
    DATA_PROFILE: PATH_POLICY.dbProfile,
    RUNTIME_DATA_DIR: PATH_POLICY.runtimeDataDir,
    PORT,
    HOST,
    SERVER_BASE_URL,
    APP_ENVIRONMENT,
    TRUST_PROXY,
    HEALTHCHECK_PATH,
    PUBLIC_BASE_URL,
    PUBLIC_HEALTHCHECK_URL,
    REVERSE_PROXY_ENABLED,
    REVERSE_PROXY_TYPE,
    SYSTEMD_SERVICE_NAME,
    SCHEDULER_TICK_INTERVAL_MS,
    SHUTDOWN_GRACE_TIMEOUT_MS,
    PYTHON_EXEC_TIMEOUT_MS,
    PYTHON_EXEC_MAX_BUFFER,
    WECOM_WEBHOOK_URL,
    PUSH_HTML_URL,
    WECOM_MAX_MARKDOWN_LENGTH,
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    MERGER_AI_MODEL,
    MERGER_REPORT_MAX_CHARS,
    MERGER_PROMPT_TEMPLATE_CODE,
    EVENT_ARB_MATCH_MODE,
    EVENT_ARB_MATCH_LOOKBACK_DAYS,
    PYTHON_CANDIDATES,
    DAILY_SYNC_CUTOFF_TIME,
    CB_ARB_FORCE_REQUEST_SOFT_TIMEOUT_MS,
    DEFAULT_MAIN_PUSH_TIME,
    DEFAULT_MAIN_PUSH_TIMES,
    NOTIFICATION_SUMMARY_CONFIG,
    PUSH_CALENDAR_MODE,
    PUSH_SCHEDULER_RUNTIME_ENABLED,
    PUSH_SCHEDULER_DISABLED_REASON,
    DEFAULT_NOTIFICATION_MODULES,
    DEFAULT_DISCOUNT_STRATEGY_MONITOR_TIMES,
    DEFAULT_DISCOUNT_STRATEGY_CONFIG,
    DISCOUNT_STRATEGY_CONFIG,
    DEFAULT_PUSH_CONFIG,
    DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG,
    DEFAULT_CB_ARBITRAGE_PUSH_TIMES,
    DEFAULT_CB_ARBITRAGE_PUSH_CONFIG,
    DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG,
    DASHBOARD_TABLE_UI,
    DASHBOARD_AUTO_REFRESH,
    DASHBOARD_THEME,
    DASHBOARD_MODULE_NOTES,
    DEFAULT_AUTO_REFRESH_CONFIG,
    // helpers
    toIntConfig,
    toPositiveNumberConfig,
    toNumConfigOrFallback,
    normalizeTimeConfig,
    normalizeTimeListConfig,
    normalizeSessionWindowListConfig,
    pluginFetchConfig,
    buildNotificationModuleDefaults,
  };
}

module.exports = { loadServerConfig, toIntConfig, toPositiveNumberConfig, toNumConfigOrFallback, normalizeTimeConfig, normalizeTimeListConfig, normalizeSessionWindowListConfig, isLoopbackHost, isLoopbackUrl, pluginFetchConfig, buildNotificationModuleDefaults };