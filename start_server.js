const fs = require('fs');
const path = require('path');
const express = require('express');
const cors = require('cors');
const { exec, execSync } = require('child_process');
const { promisify } = require('util');
const { getConfig, loadEnvFile } = require('./shared/config/node_config');
const { getPathPolicy, ensureDir } = require('./shared/paths/node_paths');
const { readJson: sharedReadJson, writeJson: sharedWriteJson } = require('./shared/runtime/json_store');
const { createStateRegistry } = require('./shared/runtime/state_registry');
const {
  nowIso: sharedNowIso,
  getShanghaiParts: sharedGetShanghaiParts,
  normalizeDateText: sharedNormalizeDateText,
  isTradingWeekday: sharedIsTradingWeekday,
  isTradingSession: sharedIsTradingSession,
  isAfterCutoff: sharedIsAfterCutoff,
} = require('./shared/time/shanghai_time');
const { normalizeError: sharedNormalizeError } = require('./shared/models/service_result');
const { createPushConfigStore } = require('./notification/scheduler/push_config_store');
const { createPushRuntimeStore } = require('./notification/scheduler/push_runtime_store');
const { createModulePushConfigStore } = require('./notification/scheduler/module_push_config_store');
const { createModulePushRuntimeStore } = require('./notification/scheduler/module_push_runtime_store');
const { createWeComClient } = require('./notification/wecom/client');
const { buildSummaryMarkdown: buildNotificationSummaryMarkdown } = require('./notification/styles/markdown_style');
const { buildCbRightsIssueMarkdown } = require('./notification/styles/cb_rights_issue_markdown');
const { buildLofArbitrageMarkdown } = require('./notification/styles/lof_arbitrage_markdown');
const { buildConvertibleBondDiscountMarkdown } = require('./notification/styles/discount_strategy_markdown');
const { createMainSummaryService } = require('./notification/summary/main_summary');
const { createEventAlertService } = require('./notification/alerts/event_alert_service');
const { createCbRightsIssuePushService } = require('./notification/cb_rights_issue/service');
const { createLofArbitragePushService } = require('./notification/lof_arbitrage/service');
const { createMergerReportService } = require('./notification/merger_report/service');
const { createWeComScheduler } = require('./notification/scheduler/wecom_scheduler');
const {
  sanitizeSubscriptionRows: strategySanitizeSubscriptionRows,
  sanitizeSubscriptionResult: strategySanitizeSubscriptionResult,
} = require('./strategy/subscription/service');
const {
  sanitizeCbArbRows: strategySanitizeCbArbRows,
  isCbArbRowActiveForceRedeem: strategyIsCbArbRowActiveForceRedeem,
  selectCbArbSummaryRows: strategySelectCbArbSummaryRows,
  buildConvertibleBondDiscountSnapshot: strategyBuildConvertibleBondDiscountSnapshot,
} = require('./strategy/convertible_bond/service');
const { createConvertibleBondDiscountRuntimeStore } = require('./strategy/convertible_bond/discount_runtime_store');
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
const PACKAGE_JSON_PATH = path.resolve(ROOT, 'package.json');

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
const LOF_ARBITRAGE_NOTIFICATION_CONFIG = (NOTIFICATION_CONFIG?.lof_arbitrage && typeof NOTIFICATION_CONFIG.lof_arbitrage === 'object')
  ? NOTIFICATION_CONFIG.lof_arbitrage
  : {};
const INDEX_FILE = path.resolve(
  ROOT,
  PRESENTATION_CONFIG.dashboard_entry || './presentation/templates/dashboard_template.html'
);
const STATIC_DATA_DIR = PATH_POLICY.dataRootDir;
const SHARED_DATA_DIR = PATH_POLICY.sharedDataDir;
const DATA_PROFILE = PATH_POLICY.dbProfile;
const RUNTIME_DATA_DIR = PATH_POLICY.runtimeDataDir;
const execAsync = promisify(exec);

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
    eventArb: raw.event_arbitrage !== false,
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
const CB_ARB_FORCE_REQUEST_SOFT_TIMEOUT_MS = toIntConfig(
  pluginFetchConfig('convertible_bond').force_request_soft_timeout_ms,
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
const PUSH_CALENDAR_MODE = String(
  NOTIFICATION_CONFIG?.scheduler?.calendar_mode || 'daily'
).trim().toLowerCase() || 'daily';
const PUSH_SCHEDULER_RUNTIME_ENABLED = Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled) && !isLoopbackUrl(PUBLIC_BASE_URL);
const PUSH_SCHEDULER_DISABLED_REASON = PUSH_SCHEDULER_RUNTIME_ENABLED
  ? ''
  : (Boolean(NOTIFICATION_CONFIG?.scheduler?.enabled) ? 'loopback_public_base_url' : 'scheduler_config_disabled');
const DEFAULT_NOTIFICATION_MODULES = buildNotificationModuleDefaults();
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
const DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG = {
  enabled: Boolean(LOF_ARBITRAGE_NOTIFICATION_CONFIG?.enabled),
  times: normalizeTimeListConfig(
    LOF_ARBITRAGE_NOTIFICATION_CONFIG?.default_times,
    '14:00'
  ).slice(0, 1),
  tradingDaysOnly: LOF_ARBITRAGE_NOTIFICATION_CONFIG?.trading_days_only !== false,
};

function buildDashboardTableUiConfig(config = {}) {
  const minWidthSource = config && typeof config.min_width_by_kind === 'object' ? config.min_width_by_kind : {};
  return {
    desktopFontPx: toPositiveNumberConfig(config.desktop_font_px, 14),
    desktopHeaderFontPx: toPositiveNumberConfig(config.desktop_header_font_px, 14),
    desktopLineHeight: toPositiveNumberConfig(config.desktop_line_height, 1.58),
    desktopCellPaddingY: toPositiveNumberConfig(config.desktop_cell_padding_y, 10),
    desktopCellPaddingX: toPositiveNumberConfig(config.desktop_cell_padding_x, 12),
    tabletFontPx: toPositiveNumberConfig(config.tablet_font_px, 13),
    minWidthByKind: {
      subscription: toPositiveNumberConfig(minWidthSource.subscription, 1180),
      convertible: toPositiveNumberConfig(minWidthSource.convertible, 1560),
      premium: toPositiveNumberConfig(minWidthSource.premium, 1240),
      monitor: toPositiveNumberConfig(minWidthSource.monitor, 1320),
      dividend: toPositiveNumberConfig(minWidthSource.dividend, 1100),
      merger: toPositiveNumberConfig(minWidthSource.merger, 1280),
      lof: toPositiveNumberConfig(minWidthSource.lof, 1680),
    },
  };
}

function buildDashboardAutoRefreshConfig(config = {}) {
  return {
    enabled: toBooleanConfig(config.enabled, true),
    intervalMs: toPositiveNumberConfig(config.interval_ms, 60 * 1000),
    mode: String(config.mode || 'status').trim() || 'status',
    currentTabOnly: config.current_tab_only !== false,
    reloadDataOnCacheChange: config.reload_data_on_cache_change !== false,
  };
}

function normalizeDashboardThemeConfig(value) {
  const normalized = String(value || 'classic').trim().toLowerCase();
  return ['classic', 'clean_data'].includes(normalized) ? normalized : 'classic';
}

function normalizeStringListConfig(values) {
  return (Array.isArray(values) ? values : [])
    .map((item) => String(item || '').trim())
    .filter(Boolean);
}

// 展示注释只做配置归一化，不在这里混入业务计算，保证解释文本和页面渲染解耦。
function buildDashboardModuleNotesConfig(config = {}) {
  const buildModuleNote = (moduleKey) => {
    const item = config && typeof config[moduleKey] === 'object' ? config[moduleKey] : {};
    return {
      dataSources: normalizeStringListConfig(item.data_sources),
      formulas: normalizeStringListConfig(item.formulas),
      strategyNotes: normalizeStringListConfig(item.strategy_notes),
    };
  };

  const result = {};
  for (const moduleKey of ['subscription', 'cbArb', 'ah', 'ab', 'lofArb', 'monitor', 'dividend', 'merger', 'cbRightsIssue']) {
    const note = buildModuleNote(moduleKey);
    if (note.dataSources.length || note.formulas.length || note.strategyNotes.length) {
      result[moduleKey] = note;
    }
  }
  return result;
}

const DASHBOARD_TABLE_UI = buildDashboardTableUiConfig(PRESENTATION_DASHBOARD_TABLE_UI_CONFIG);
const DASHBOARD_MODULE_NOTES = buildDashboardModuleNotesConfig(PRESENTATION_DASHBOARD_MODULE_NOTES_CONFIG);
const DASHBOARD_AUTO_REFRESH = buildDashboardAutoRefreshConfig(PRESENTATION_DASHBOARD_AUTO_REFRESH_CONFIG);
const DASHBOARD_THEME = normalizeDashboardThemeConfig(PRESENTATION_CONFIG?.dashboard_theme);
const PROCESS_STARTED_AT = sharedNowIso();
const APP_PACKAGE_VERSION = (() => {
  try {
    const raw = fs.readFileSync(PACKAGE_JSON_PATH, 'utf8');
    const parsed = JSON.parse(raw);
    return String(parsed?.version || '0.0.0').trim() || '0.0.0';
  } catch {
    return '0.0.0';
  }
})();

function safeExecTrim(command) {
  try {
    return execSync(command, {
      cwd: ROOT,
      stdio: ['ignore', 'pipe', 'ignore'],
      encoding: 'utf8',
    }).trim();
  } catch {
    return '';
  }
}

function resolveRuntimeVersionMetadata() {
  const envGitSha = String(process.env.APP_GIT_SHA || '').trim();
  const envGitShortSha = String(process.env.APP_GIT_SHORT_SHA || '').trim();
  const envGitBranch = String(process.env.APP_GIT_BRANCH || '').trim();
  const envGitCommitTime = String(process.env.APP_GIT_COMMIT_TIME || '').trim();

  if (envGitSha || envGitShortSha || envGitBranch || envGitCommitTime) {
    return {
      appVersion: APP_PACKAGE_VERSION,
      gitSha: envGitSha || null,
      gitShortSha: envGitShortSha || (envGitSha ? envGitSha.slice(0, 7) : null),
      gitBranch: envGitBranch || null,
      gitCommitTime: envGitCommitTime || null,
      startedAt: PROCESS_STARTED_AT,
      source: 'env',
    };
  }

  const gitSha = safeExecTrim('git rev-parse HEAD');
  const gitShortSha = safeExecTrim('git rev-parse --short HEAD') || (gitSha ? gitSha.slice(0, 7) : '');
  const gitBranch = safeExecTrim('git rev-parse --abbrev-ref HEAD');
  const gitCommitTime = safeExecTrim('git log -1 --format=%cI');
  const hasGitMetadata = Boolean(gitSha || gitShortSha || gitBranch || gitCommitTime);

  return {
    appVersion: APP_PACKAGE_VERSION,
    gitSha: gitSha || null,
    gitShortSha: gitShortSha || null,
    gitBranch: gitBranch || null,
    gitCommitTime: gitCommitTime || null,
    startedAt: PROCESS_STARTED_AT,
    source: hasGitMetadata ? 'git' : 'package_only',
  };
}

const RUNTIME_VERSION = resolveRuntimeVersionMetadata();

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

function isTradingWeekday(date = new Date()) {
  return sharedIsTradingWeekday(date);
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
      if (options.syncUniverse) {
        await callDataCore(['sync-cb-stock-history'], { timeout: 900000, maxBuffer: 1024 * 1024 * 50 });
      }
      return callDataCore(['cb-arb'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 });
    },
    dailySync: async () => {
      await callDataCore(['sync-cb-stock-history'], { timeout: 900000, maxBuffer: 1024 * 1024 * 50 });
      return callDataCore(['cb-arb'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 });
    },
  },
  cbRightsIssue: {
    intraday: pluginFetchConfig('cb_rights_issue').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('cb_rights_issue').refresh_interval_ms, 15 * 60 * 1000),
    dbDailySync: pluginFetchConfig('cb_rights_issue').daily_incremental_sync !== false,
    fetch: async (options = {}) => {
      if (pluginFetchConfig('cb_rights_issue').sync_stock_history_before_strategy !== false && (options.force || options.dailySync)) {
        await callDataCore(['sync-cb-rights-issue-stock-history'], { timeout: 900000, maxBuffer: 1024 * 1024 * 50 });
      }
      return callDataCore(['cb-rights-issue'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 });
    },
    dailySync: async () => {
      if (pluginFetchConfig('cb_rights_issue').sync_stock_history_before_strategy !== false) {
        await callDataCore(['sync-cb-rights-issue-stock-history'], { timeout: 900000, maxBuffer: 1024 * 1024 * 50 });
      }
      return callDataCore(['cb-rights-issue'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 });
    },
  },
  lofArb: {
    intraday: pluginFetchConfig('lof_arbitrage').intraday !== false,
    refreshIntervalMs: toIntConfig(pluginFetchConfig('lof_arbitrage').refresh_interval_ms, 5 * 60 * 1000),
    dbDailySync: Boolean(pluginFetchConfig('lof_arbitrage').daily_incremental_sync),
    fetch: () => callDataCore(['lof-arbitrage'], { timeout: 300000, maxBuffer: 1024 * 1024 * 50 }),
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
  lastMainPushAttemptAt: null,
  lastMainPushSuccessAt: null,
  lastMainPushError: null,
  lastEventAlertAttemptAt: null,
  lastEventAlertSuccessAt: null,
  lastEventAlertError: null,
  mainPushRecords: {},
  eventAlertRecords: {},
  eventArbSeenItems: {},
  eventArbDailyNewItems: {},
});
const cbRightsIssueStateStore = STATE_REGISTRY.read('cb_rights_issue_state', 'cb_rights_issue_state.json', {
  monitorList: [],
  sourceRows: [],
  sourceSummary: {},
  lastRebuildAt: null,
  lastRebuildDate: null,
  lastRebuildError: null,
  updateTime: null,
  source: null,
  sourceUrl: null,
  sourceTitle: null,
});
const cbRightsIssuePushConfigStore = STATE_REGISTRY.read('cb_rights_issue_push_config', 'cb_rights_issue_push_config.json', {
  enabled: DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG.enabled,
  times: [...DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG.times],
  tradingDaysOnly: DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG.tradingDaysOnly,
});
const cbRightsIssuePushRuntimeState = STATE_REGISTRY.read('cb_rights_issue_push_runtime', 'cb_rights_issue_push_runtime.json', {
  pushRecords: {},
  lastAttemptAt: null,
  lastSuccessAt: null,
  lastError: null,
});
const lofArbStateStore = STATE_REGISTRY.read('lof_arbitrage_state', 'lof_arbitrage_state.json', {
  rows: [],
  limitedMonitorRows: [],
  unlimitedMonitorRows: [],
  sourceSummary: {},
  lastRebuildAt: null,
  lastRebuildDate: null,
  lastRebuildError: null,
  updateTime: null,
  source: null,
  seenEntryMap: {},
  lastInstantAttemptAt: null,
  lastInstantSuccessAt: null,
  lastInstantError: null,
});
const lofArbPushConfigStore = STATE_REGISTRY.read('lof_arbitrage_push_config', 'lof_arbitrage_push_config.json', {
  enabled: DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.enabled,
  times: [...DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.times],
  tradingDaysOnly: DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.tradingDaysOnly,
});
const lofArbPushRuntimeState = STATE_REGISTRY.read('lof_arbitrage_push_runtime', 'lof_arbitrage_push_runtime.json', {
  pushRecords: {},
  lastAttemptAt: null,
  lastSuccessAt: null,
  lastError: null,
});
const cbDiscountStrategyState = STATE_REGISTRY.read('cb_discount_strategy_state', 'cb_discount_strategy_state.json', {
  initializedDate: null,
  lastBootstrapDate: null,
  monitorMap: {},
  signalStateMap: {},
  monitorPushRecords: {},
  lastBuySignalAttemptAt: null,
  lastBuySignalSuccessAt: null,
  lastBuySignalError: null,
  lastSellSignalAttemptAt: null,
  lastSellSignalSuccessAt: null,
  lastSellSignalError: null,
  lastMonitorPushAttemptAt: null,
  lastMonitorPushSuccessAt: null,
  lastMonitorPushError: null,
});
const mergerReportStore = STATE_REGISTRY.read('merger_company_reports', 'merger_company_reports.json', { reports: {} });
const refreshLocks = new Map();
const intradayLastRun = new Map();
const datasetCache = new Map();
const datasetRefreshMeta = new Map();
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

function saveCbRightsIssueStateStore() {
  STATE_REGISTRY.write('cb_rights_issue_state', 'cb_rights_issue_state.json', cbRightsIssueStateStore);
}

function saveCbRightsIssuePushConfigStore() {
  STATE_REGISTRY.write('cb_rights_issue_push_config', 'cb_rights_issue_push_config.json', cbRightsIssuePushConfigStore);
}

function saveCbRightsIssuePushRuntimeState() {
  STATE_REGISTRY.write('cb_rights_issue_push_runtime', 'cb_rights_issue_push_runtime.json', cbRightsIssuePushRuntimeState);
}

function saveLofArbStateStore() {
  STATE_REGISTRY.write('lof_arbitrage_state', 'lof_arbitrage_state.json', lofArbStateStore);
}

function saveLofArbPushConfigStore() {
  STATE_REGISTRY.write('lof_arbitrage_push_config', 'lof_arbitrage_push_config.json', lofArbPushConfigStore);
}

// LOF 推送本轮固定为交易日 14:00 一次全量推送，启动时主动把旧三时点运行态收敛到单时点。
function migrateLofArbPushConfigStore() {
  const nextEnabled = typeof lofArbPushConfigStore.enabled === 'boolean'
    ? lofArbPushConfigStore.enabled
    : DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.enabled;
  const nextTradingDaysOnly = typeof lofArbPushConfigStore.tradingDaysOnly === 'boolean'
    ? lofArbPushConfigStore.tradingDaysOnly
    : DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.tradingDaysOnly;
  const changed = (
    lofArbPushConfigStore.enabled !== nextEnabled ||
    lofArbPushConfigStore.tradingDaysOnly !== nextTradingDaysOnly ||
    !Array.isArray(lofArbPushConfigStore.times) ||
    lofArbPushConfigStore.times.length !== 1 ||
    lofArbPushConfigStore.times[0] !== '14:00'
  );
  lofArbPushConfigStore.enabled = nextEnabled;
  lofArbPushConfigStore.tradingDaysOnly = nextTradingDaysOnly;
  lofArbPushConfigStore.times = ['14:00'];
  if (changed) saveLofArbPushConfigStore();
}

function saveLofArbPushRuntimeState() {
  STATE_REGISTRY.write('lof_arbitrage_push_runtime', 'lof_arbitrage_push_runtime.json', lofArbPushRuntimeState);
}

function saveCbDiscountStrategyState() {
  STATE_REGISTRY.write('cb_discount_strategy_state', 'cb_discount_strategy_state.json', cbDiscountStrategyState);
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
    version: RUNTIME_VERSION,
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
    version: cloneJsonSafe(RUNTIME_VERSION, {}),
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
  return normalizeDatasetPayload(key, cloneJsonSafe(cached));
}

function hasNonEmptyRows(value) {
  return Array.isArray(value) && value.length > 0;
}

function shouldBypassStaleEmptySubscriptionCache(key, payload) {
  if (!['ipo', 'bonds'].includes(key)) return false;
  if (!payload || typeof payload !== 'object') return false;
  const historyCount = Number(payload.historyCount);
  const hasVisibleRows = hasNonEmptyRows(payload.data) || hasNonEmptyRows(payload.upcoming);
  return !hasVisibleRows && (!Number.isFinite(historyCount) || historyCount <= 0);
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

function markDatasetRefreshSuccess(key, result) {
  datasetRefreshMeta.set(key, {
    servedFromCache: false,
    refreshError: null,
    updateTime: String(result?.updateTime || result?.data?.updateTime || '').trim() || null,
    cacheTime: null,
    lastAttemptAt: nowIso(),
    lastSuccessAt: nowIso(),
    lastFailureAt: null,
  });
}

function markDatasetRefreshFallback(key, error, cached = null) {
  const previous = datasetRefreshMeta.get(key);
  datasetRefreshMeta.set(key, {
    servedFromCache: Boolean(cached),
    refreshError: normalizeError(error || 'refresh_failed'),
    updateTime: String(cached?.updateTime || cached?.data?.updateTime || previous?.updateTime || '').trim() || null,
    cacheTime: String(cached?.cacheTime || previous?.cacheTime || '').trim() || null,
    lastAttemptAt: nowIso(),
    lastSuccessAt: previous?.lastSuccessAt || null,
    lastFailureAt: nowIso(),
  });
}

const DASHBOARD_RESOURCE_STATUS_DATASET_KEYS = Object.freeze({
  exchangeRate: 'exchangeRate',
  ipo: 'ipo',
  bonds: 'bonds',
  cbArb: 'cbArb',
  ah: 'ah',
  ab: 'ab',
  lofArb: 'lofArb',
  merger: 'eventArb',
  cbRightsIssue: 'cbRightsIssue',
  eventArb: 'eventArb',
});

function readCachedDatasetStatus(resourceKey) {
  const datasetKey = DASHBOARD_RESOURCE_STATUS_DATASET_KEYS[resourceKey];
  if (!datasetKey || !DATASETS[datasetKey]) return null;
  const cached = readDatasetCache(datasetKey);
  const runtimeMeta = datasetRefreshMeta.get(datasetKey);
  const updateTime = String(cached?.updateTime || cached?.data?.updateTime || '').trim() || null;
  const cacheTime = String(cached?.cacheTime || '').trim() || null;
  return {
    resourceKey,
    datasetKey,
    updateTime: runtimeMeta?.updateTime || updateTime,
    cacheTime: runtimeMeta?.cacheTime || cacheTime,
    servedFromCache: typeof runtimeMeta?.servedFromCache === 'boolean'
      ? runtimeMeta.servedFromCache
      : Boolean(cached),
    refreshError: runtimeMeta?.refreshError || null,
    refreshing: refreshLocks.has(`${datasetKey}:normal`) || refreshLocks.has(`${datasetKey}:daily`),
    intraday: Boolean(DATASETS[datasetKey]?.intraday),
    refreshIntervalMs: Number(DATASETS[datasetKey]?.refreshIntervalMs) || null,
  };
}

function getDashboardResourceStatus(keys = []) {
  const requested = (Array.isArray(keys) ? keys : [])
    .map((item) => String(item || '').trim())
    .filter(Boolean);
  const uniqueKeys = requested.length ? [...new Set(requested)] : Object.keys(DASHBOARD_RESOURCE_STATUS_DATASET_KEYS);
  const result = {};
  for (const key of uniqueKeys) {
    const snapshot = readCachedDatasetStatus(key);
    if (snapshot) result[key] = snapshot;
  }
  return result;
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
  nowIso,
});
const cbRightsIssuePushConfigDomain = createModulePushConfigStore({
  state: cbRightsIssuePushConfigStore,
  defaultConfig: DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG,
  save: saveCbRightsIssuePushConfigStore,
});
const cbRightsIssuePushRuntimeDomain = createModulePushRuntimeStore({
  state: cbRightsIssuePushRuntimeState,
  save: saveCbRightsIssuePushRuntimeState,
  parsePushMinutes: (value) => cbRightsIssuePushConfigDomain.parsePushMinutes(value),
});
migrateLofArbPushConfigStore();
const lofArbPushConfigDomain = createModulePushConfigStore({
  state: lofArbPushConfigStore,
  defaultConfig: DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG,
  save: saveLofArbPushConfigStore,
  maxTimes: 1,
});
const lofArbPushRuntimeDomain = createModulePushRuntimeStore({
  state: lofArbPushRuntimeState,
  save: saveLofArbPushRuntimeState,
  parsePushMinutes: (value) => lofArbPushConfigDomain.parsePushMinutes(value),
});
const cbDiscountStrategyDomain = createConvertibleBondDiscountRuntimeStore({
  state: cbDiscountStrategyState,
  save: saveCbDiscountStrategyState,
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
const eventAlertService = createEventAlertService({
  collectAlertDatasets,
  buildDiscountSnapshot: buildConvertibleBondDiscountSnapshot,
  buildDiscountMarkdown: buildConvertibleBondDiscountMarkdown,
  sendMarkdown: (markdown) => weComClient.sendMarkdown(markdown),
  getDiscountStrategyConfig,
  pushRuntimeStore: pushRuntimeDomain,
  discountRuntimeStore: cbDiscountStrategyDomain,
  parsePushMinutes: (value) => pushConfigDomain.parsePushMinutes(value),
  getShanghaiParts,
  isTradingSession,
  nowIso,
});
const cbRightsIssuePushService = createCbRightsIssuePushService({
  getConfig: () => cbRightsIssuePushConfigDomain.getConfig(),
  runtimeStore: cbRightsIssuePushRuntimeDomain,
  getDataset,
  sendMarkdown: (markdown) => weComClient.sendMarkdown(markdown),
  buildMarkdown: buildCbRightsIssueMarkdown,
  getShanghaiParts,
  parsePushMinutes: (value) => cbRightsIssuePushConfigDomain.parsePushMinutes(value),
  isTradingWeekday,
  isDeliveryAvailable: () => Boolean(WECOM_WEBHOOK_URL),
  nowIso,
  logInfo: (message) => console.info(message),
  logError: (scope, error) => console.error(scope, error?.message || error),
});
const lofArbPushService = createLofArbitragePushService({
  getConfig: () => lofArbPushConfigDomain.getConfig(),
  runtimeStore: lofArbPushRuntimeDomain,
  stateStore: lofArbStateStore,
  saveStateStore: saveLofArbStateStore,
  getDataset,
  sendMarkdown: (markdown) => weComClient.sendMarkdown(markdown),
  buildMarkdown: buildLofArbitrageMarkdown,
  getShanghaiParts,
  parsePushMinutes: (value) => lofArbPushConfigDomain.parsePushMinutes(value),
  isTradingWeekday,
  isDeliveryAvailable: () => Boolean(WECOM_WEBHOOK_URL),
  nowIso,
  logInfo: (message) => console.info(message),
  logError: (scope, error) => console.error(scope, error?.message || error),
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
  pushEventAlertsToWeCom,
  syncEventArbSummaryState,
  getShanghaiParts,
  parsePushMinutes: (value) => pushConfigDomain.parsePushMinutes(value),
  calendarMode: PUSH_CALENDAR_MODE,
  isTradingSession,
  nowIso,
  logError: (scope, error) => console.error(scope, error?.message || error),
});

function getPushDeliveryStatus() {
  return {
    webhookConfigured: Boolean(WECOM_WEBHOOK_URL),
    pushHtmlUrlConfigured: Boolean(PUSH_HTML_URL),
    schedulerEnabled: PUSH_SCHEDULER_RUNTIME_ENABLED,
    calendarMode: PUSH_CALENDAR_MODE,
    schedulerDisabledReason: PUSH_SCHEDULER_DISABLED_REASON || null,
  };
}

function getCbRightsIssuePushDeliveryStatus() {
  const config = cbRightsIssuePushConfigDomain.getConfig();
  return {
    webhookConfigured: Boolean(WECOM_WEBHOOK_URL),
    schedulerEnabled: PUSH_SCHEDULER_RUNTIME_ENABLED,
    schedulerDisabledReason: PUSH_SCHEDULER_DISABLED_REASON || null,
    tradingDaysOnly: config.tradingDaysOnly !== false,
    lastAttemptAt: cbRightsIssuePushRuntimeState.lastAttemptAt || null,
    lastSuccessAt: cbRightsIssuePushRuntimeState.lastSuccessAt || null,
    lastError: cbRightsIssuePushRuntimeState.lastError || null,
  };
}

function getLofArbPushDeliveryStatus() {
  const config = lofArbPushConfigDomain.getConfig();
  return {
    webhookConfigured: Boolean(WECOM_WEBHOOK_URL),
    schedulerEnabled: PUSH_SCHEDULER_RUNTIME_ENABLED,
    schedulerDisabledReason: PUSH_SCHEDULER_DISABLED_REASON || null,
    tradingDaysOnly: config.tradingDaysOnly !== false,
    lastAttemptAt: lofArbPushRuntimeState.lastAttemptAt || null,
    lastSuccessAt: lofArbPushRuntimeState.lastSuccessAt || null,
    lastError: lofArbPushRuntimeState.lastError || null,
  };
}

function getDiscountStrategyConfig() {
  return {
    ...DISCOUNT_STRATEGY_CONFIG,
    sessionWindows: [...DISCOUNT_STRATEGY_CONFIG.sessionWindows],
    monitorSessionTimes: [...DISCOUNT_STRATEGY_CONFIG.monitorSessionTimes],
  };
}

function buildDiscountStrategyStatus() {
  return {
    enabled: true,
    tradingDaysOnly: DISCOUNT_STRATEGY_CONFIG.tradingDaysOnly !== false,
    sessionWindows: [...DISCOUNT_STRATEGY_CONFIG.sessionWindows],
    monitorSessionTimes: [...DISCOUNT_STRATEGY_CONFIG.monitorSessionTimes],
    buyThreshold: DISCOUNT_STRATEGY_CONFIG.buyThreshold,
    sellThreshold: DISCOUNT_STRATEGY_CONFIG.sellThreshold,
    monitorIntervalMinutes: DISCOUNT_STRATEGY_CONFIG.monitorIntervalMinutes,
    lastBuySignalSuccessAt: cbDiscountStrategyState.lastBuySignalSuccessAt || null,
    lastBuySignalError: cbDiscountStrategyState.lastBuySignalError || null,
    lastSellSignalSuccessAt: cbDiscountStrategyState.lastSellSignalSuccessAt || null,
    lastSellSignalError: cbDiscountStrategyState.lastSellSignalError || null,
    lastMonitorPushSuccessAt: cbDiscountStrategyState.lastMonitorPushSuccessAt || null,
    lastMonitorPushError: cbDiscountStrategyState.lastMonitorPushError || null,
  };
}

function buildPushConfigViewModel(config) {
  return buildPushConfigResponse(config, pushRuntimeState, getPushDeliveryStatus(), buildDiscountStrategyStatus());
}

function buildCbRightsIssuePushConfigViewModel(config) {
  return {
    enabled: config?.enabled !== false,
    times: Array.isArray(config?.times) ? config.times : [...DEFAULT_CB_RIGHTS_ISSUE_PUSH_CONFIG.times],
    tradingDaysOnly: config?.tradingDaysOnly !== false,
    deliveryStatus: getCbRightsIssuePushDeliveryStatus(),
  };
}

function buildLofArbPushConfigViewModel(config) {
  return {
    enabled: config?.enabled !== false,
    times: Array.isArray(config?.times) ? config.times : [...DEFAULT_LOF_ARBITRAGE_PUSH_CONFIG.times],
    tradingDaysOnly: config?.tradingDaysOnly !== false,
    deliveryStatus: getLofArbPushDeliveryStatus(),
  };
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

function isCbArbRowActiveForceRedeem(row) {
  return strategyIsCbArbRowActiveForceRedeem(row);
}

const CB_ARB_PUBLIC_ROW_KEYS = [
  'code',
  'bondName',
  'stockCode',
  'stockName',
  'price',
  'changePercent',
  'stockPrice',
  'stockChangePercent',
  'stockAtr20',
  'stockAvgTurnoverAmount20Yi',
  'stockAvgTurnoverAmount5Yi',
  'stockAvgRoe3Y',
  'stockDebtRatio',
  'convertPrice',
  'convertValue',
  'premiumRate',
  'bondValue',
  'doubleLow',
  'stockAtr20Pct',
  'discountAtrRatio',
  'boardType',
  'bondToStockMarketValueRatio',
  'stockMarketValueYi',
  'isDiscountMonitorActive',
  'redeemTriggerPrice',
  'putbackPrice',
  'volatility250',
  'volatility60',
  'annualizedVolatility',
  'pureBondValue',
  'pricingFormula',
  'callStrike',
  'redeemCallStrike',
  'longCallOptionValue',
  'shortCallOptionValue',
  'callSpreadOptionValue',
  'callOptionValue',
  'putOptionValue',
  'theoreticalPrice',
  'theoreticalPremiumRate',
  'yieldToMaturityPretax',
  'rating',
  'forceRedeemActive',
  'forceRedeemLabel',
  'forceRedeemStatus',
  'forceRedeemNoticeDate',
  'delistDate',
  'ceaseDate',
  'maturityDate',
  'maturityRedeemPrice',
  'remainingYears',
  'remainingSizeYi',
  'turnoverAmountYi',
  'listingDate',
  'convertStartDate',
];

function shapeCbArbPublicRows(rows) {
  return (Array.isArray(rows) ? rows : []).map((row) => {
    if (!row || typeof row !== 'object') return row;
    const shaped = {};
    for (const key of CB_ARB_PUBLIC_ROW_KEYS) {
      if (Object.prototype.hasOwnProperty.call(row, key)) {
        shaped[key] = row[key];
      }
    }
    return shaped;
  });
}

function normalizeDatasetPayload(key, result) {
  if (!result || typeof result !== 'object') return result;
  if (result.success === false) return result;
  if (key === 'ipo') return sanitizeSubscriptionResult(result, 'ipo');
  if (key === 'bonds') return sanitizeSubscriptionResult(result, 'bond');
  if (key === 'cbArb') {
    const snapshot = buildConvertibleBondDiscountSnapshot(result.data, cbDiscountStrategyDomain.getState(), {
      ...getDiscountStrategyConfig(),
      nowIsoText: nowIso(),
      todayDate: getShanghaiParts().date,
    });
    const rows = shapeCbArbPublicRows(snapshot.rows);
    const summaryRows = strategySelectCbArbSummaryRows(rows);
    const sortedByDoubleLow = [...summaryRows].sort(
      (a, b) => (Number.isFinite(Number(a?.doubleLow)) ? Number(a.doubleLow) : Number.POSITIVE_INFINITY)
        - (Number.isFinite(Number(b?.doubleLow)) ? Number(b.doubleLow) : Number.POSITIVE_INFINITY)
    );
    const sortedByTheory = [...summaryRows].sort(
      (a, b) => (Number.isFinite(Number(b?.theoreticalPremiumRate)) ? Number(b.theoreticalPremiumRate) : Number.NEGATIVE_INFINITY)
        - (Number.isFinite(Number(a?.theoreticalPremiumRate)) ? Number(a.theoreticalPremiumRate) : Number.NEGATIVE_INFINITY)
    );
    const { data: _rawData, list: _legacyList, rows: _legacyRows, ...rest } = result;
    return {
      ...rest,
      data: rows,
      premiumMonitorSummary: snapshot.premiumMonitorSummary,
      summary: {
        topDoubleLow: sortedByDoubleLow.slice(0, 3),
        topTheoreticalPremiumRate: sortedByTheory.slice(0, 3),
      },
    };
  }
  if (key === 'cbRightsIssue') {
    const payload = result.data && typeof result.data === 'object' ? result.data : {};
    const rebuildAt = String(payload.rebuildStatus?.lastRebuildAt || result.updateTime || '').trim();
    const rebuildDate = normalizeYmd(rebuildAt);
    const todayDate = getShanghaiParts().date;
    if (rebuildDate && rebuildDate !== todayDate) {
      return {
        ...result,
        data: {
          ...payload,
          monitorList: [],
          rebuildStatus: {
            ...(payload.rebuildStatus && typeof payload.rebuildStatus === 'object' ? payload.rebuildStatus : {}),
            sameDayCleared: true,
            clearedForDate: todayDate,
          },
        },
      };
    }
  }
  return result;
}

function persistCbRightsIssueStateFromResult(result) {
  if (!result || typeof result !== 'object') return;
  if (result.success === false) {
    cbRightsIssueStateStore.lastRebuildAt = nowIso();
    cbRightsIssueStateStore.lastRebuildDate = getShanghaiParts().date;
    cbRightsIssueStateStore.lastRebuildError = normalizeError(result.error || 'cb_rights_issue_refresh_failed');
    saveCbRightsIssueStateStore();
    return;
  }

  const payload = result.data && typeof result.data === 'object' ? result.data : {};
  cbRightsIssueStateStore.monitorList = Array.isArray(payload.monitorList) ? payload.monitorList : [];
  cbRightsIssueStateStore.sourceRows = Array.isArray(payload.sourceRows) ? payload.sourceRows : [];
  cbRightsIssueStateStore.sourceSummary = payload.sourceSummary && typeof payload.sourceSummary === 'object' ? payload.sourceSummary : {};
  cbRightsIssueStateStore.lastRebuildAt = payload.rebuildStatus?.lastRebuildAt || result.updateTime || nowIso();
  cbRightsIssueStateStore.lastRebuildDate = getShanghaiParts().date;
  cbRightsIssueStateStore.lastRebuildError = payload.rebuildStatus?.lastRebuildError || null;
  cbRightsIssueStateStore.updateTime = result.updateTime || null;
  cbRightsIssueStateStore.source = result.source || null;
  cbRightsIssueStateStore.sourceUrl = result.sourceUrl || payload.sourceSummary?.sourceUrl || null;
  cbRightsIssueStateStore.sourceTitle = result.sourceTitle || payload.sourceSummary?.sourceTitle || null;
  saveCbRightsIssueStateStore();
}

function persistLofArbStateFromResult(result) {
  if (!result || typeof result !== 'object') return;
  if (result.success === false) {
    lofArbStateStore.lastRebuildAt = nowIso();
    lofArbStateStore.lastRebuildDate = getShanghaiParts().date;
    lofArbStateStore.lastRebuildError = normalizeError(result.error || 'lof_arbitrage_refresh_failed');
    saveLofArbStateStore();
    return;
  }

  const payload = result.data && typeof result.data === 'object' ? result.data : {};
  lofArbStateStore.rows = Array.isArray(payload.rows) ? payload.rows : [];
  lofArbStateStore.limitedMonitorRows = Array.isArray(payload.limitedMonitorRows) ? payload.limitedMonitorRows : [];
  lofArbStateStore.unlimitedMonitorRows = Array.isArray(payload.unlimitedMonitorRows) ? payload.unlimitedMonitorRows : [];
  lofArbStateStore.sourceSummary = payload.sourceSummary && typeof payload.sourceSummary === 'object' ? payload.sourceSummary : {};
  lofArbStateStore.lastRebuildAt = payload.rebuildStatus?.lastRebuildAt || result.updateTime || nowIso();
  lofArbStateStore.lastRebuildDate = getShanghaiParts().date;
  lofArbStateStore.lastRebuildError = payload.rebuildStatus?.lastRebuildError || null;
  lofArbStateStore.updateTime = result.updateTime || null;
  lofArbStateStore.source = result.source || null;
  saveLofArbStateStore();
}

function shouldRetryDatasetBySchema(key, result) {
  if (!result || typeof result !== 'object' || result.success === false) return false;
  if (key === 'cbArb') return !isCbArbSchemaReady(result);
  if (key === 'ah') return !isAhSchemaReady(result);
  return false;
}

function normalizeDatasetRetryOptions(key, options = {}) {
  if (key === 'cbArb') return { ...options, force: true };
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
    if (key === 'cbRightsIssue') {
      persistCbRightsIssueStateFromResult(finalResult);
    }
    if (key === 'lofArb') {
      persistLofArbStateFromResult(finalResult);
    }
    if (finalResult && typeof finalResult === 'object' && finalResult.success !== false) {
      writeDatasetCache(key, finalResult);
      markDatasetRefreshSuccess(key, finalResult);
      return finalResult;
    }

    const cached = readDatasetCachePayload(key);
    markDatasetRefreshFallback(key, finalResult?.error || 'refresh_failed', cached);
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
    (Object.prototype.hasOwnProperty.call(row, 'pureBondValue') || Object.prototype.hasOwnProperty.call(row, 'bondValue')) &&
    Object.prototype.hasOwnProperty.call(row, 'maturityDate') &&
    Object.prototype.hasOwnProperty.call(row, 'remainingYears') &&
    Object.prototype.hasOwnProperty.call(row, 'theoreticalPrice') &&
    Object.prototype.hasOwnProperty.call(row, 'callOptionValue') &&
    Object.prototype.hasOwnProperty.call(row, 'putOptionValue')
  );
  if (!baseReady) return false;
  if (!rows.length) return true;
  const hasStockChange = rows.some((item) => Number.isFinite(Number(item?.stockChangePercent)));
  if (!hasStockChange) return false;

  const volatilityCount = rows.filter((item) => Number.isFinite(Number(item?.volatility250 ?? item?.volatility60))).length;
  const volatilityCoverage = volatilityCount / rows.length;
  if (volatilityCoverage < 0.55) return false;

  const atrCount = rows.filter((item) => Number.isFinite(Number(item?.stockAtr20))).length;
  const turnoverCount = rows.filter((item) => Number.isFinite(Number(item?.stockAvgTurnoverAmount20Yi))).length;
  return (atrCount / rows.length) >= 0.45 && (turnoverCount / rows.length) >= 0.45;
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
    if (
      key === 'cbArb'
      && options.force
      && !options.dailySync
      && CB_ARB_FORCE_REQUEST_SOFT_TIMEOUT_MS > 0
    ) {
      const cached = readDatasetCachePayload(key);
      if (cached) {
        const task = refreshDataset(key, options);
        const fallback = new Promise((resolve) => {
          setTimeout(() => {
            resolve(withCachedDatasetMeta(cached, {
              refreshing: true,
              forceAccepted: true,
              forceRefreshDeferred: true,
            }));
          }, CB_ARB_FORCE_REQUEST_SOFT_TIMEOUT_MS);
        });
        return Promise.race([task, fallback]);
      }
    }
    return refreshDataset(key, options);
  }

  const cached = readDatasetCachePayload(key);
  if (cached) {
    if (shouldBypassStaleEmptySubscriptionCache(key, cached)) {
      return refreshDataset(key, options);
    }
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
    const datasetEntries = Object.entries(DATASETS)
      .filter(([, dataset]) => dataset.dbDailySync)
      .map(([key]) => key);
    const settled = await Promise.allSettled(
      datasetEntries.map((key) => refreshDataset(key, { dailySync: true, force: true }))
    );
    const failures = settled
      .map((item, index) => ({ key: datasetEntries[index], item }))
      .filter(({ item }) => (
        item.status === 'rejected'
        || (item.status === 'fulfilled' && item.value && typeof item.value === 'object' && item.value.success === false)
      ))
      .map(({ key, item }) => ({
        key,
        error: item.status === 'rejected'
          ? normalizeError(item.reason || 'daily_sync_failed')
          : normalizeError(item.value?.error || 'daily_sync_failed'),
      }));

    if (!failures.length) {
      setStateDate('lastDailySyncDate', shanghai.date);
    } else {
      console.error('[daily_sync_failed]', JSON.stringify({
        date: shanghai.date,
        failures,
      }, null, 2));
    }
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
      const preloadKeys = ['exchangeRate', 'ah', 'ab', 'cbArb', 'lofArb', 'cbRightsIssue', 'merger', 'eventArb', 'ipo', 'bonds'];
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
  const details = {
    context,
    runtimeEnabled: PUSH_SCHEDULER_RUNTIME_ENABLED,
    disabledReason: PUSH_SCHEDULER_DISABLED_REASON || null,
    publicBaseUrl: PUBLIC_BASE_URL,
  };

  if (!PUSH_SCHEDULER_RUNTIME_ENABLED) {
    updateHealthSection('push_scheduler', 'ok', 'Push scheduler is intentionally disabled in local runtime', details);
    return;
  }

  try {
    await weComScheduler.runTick();
    await cbRightsIssuePushService.runIfNeeded();
    await lofArbPushService.runIfNeeded();
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
  if (PUSH_SCHEDULER_RUNTIME_ENABLED) {
    updateHealthSection('push_scheduler', 'starting', 'Push scheduler is starting', {
      runtimeEnabled: true,
      publicBaseUrl: PUBLIC_BASE_URL,
    });
  } else {
    updateHealthSection('push_scheduler', 'ok', 'Push scheduler is disabled in local runtime', {
      runtimeEnabled: false,
      disabledReason: PUSH_SCHEDULER_DISABLED_REASON || null,
      publicBaseUrl: PUBLIC_BASE_URL,
    });
  }

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
  loadMonitors: () => customMonitorRuntimeService.loadMonitors(),
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
    summaryConfig: {
      ahTopN: toIntConfig(NOTIFICATION_SUMMARY_CONFIG.ah_top_n, 2),
      abTopN: toIntConfig(NOTIFICATION_SUMMARY_CONFIG.ab_top_n, 2),
      cbTopN: toIntConfig(NOTIFICATION_SUMMARY_CONFIG.cb_top_n, 4),
      eventArbitrageTopN: toIntConfig(NOTIFICATION_SUMMARY_CONFIG.event_arbitrage_top_n, 6),
    },
    cbPushCategories: Array.isArray(STRATEGY_CONFIG?.convertible_bond?.push_categories)
      ? STRATEGY_CONFIG.convertible_bond.push_categories
      : [],
  });
}

async function sendWeComMarkdown(markdown) {
  return weComClient.sendMarkdown(markdown);
}

function buildConvertibleBondDiscountSnapshot(rows, runtimeState = {}, options = {}) {
  return strategyBuildConvertibleBondDiscountSnapshot(rows, runtimeState, options);
}

function shiftShanghaiDate(dateText, days) {
  const base = Date.parse(`${normalizeDateText(dateText)}T00:00:00+08:00`);
  if (!Number.isFinite(base)) return '';
  return new Date(base + (days * 24 * 60 * 60 * 1000)).toISOString().slice(0, 10);
}

function flattenEventArbRows(payload) {
  const root = payload?.data && typeof payload.data === 'object' ? payload.data : payload;
  const categories = root?.categories && typeof root.categories === 'object' ? root.categories : {};
  return Object.values(categories).flatMap((items) => Array.isArray(items) ? items : []);
}

async function syncEventArbSummaryState() {
  const payload = await getDataset('eventArb');
  const rows = flattenEventArbRows(payload);
  const result = pushRuntimeDomain.syncEventArbSeenItems(rows, getShanghaiParts().date);
  if (result.seeded || result.newItems.length) {
    pushRuntimeDomain.save();
  }
  return result;
}

async function collectSummaryDatasets() {
  const [ah, ab, ipo, bonds, cbArb, monitors] = await Promise.all([
    getDataset('ah'),
    getDataset('ab'),
    getDataset('ipo'),
    getDataset('bonds'),
    getDataset('cbArb'),
    getAllMonitors(),
  ]);
  const yesterday = shiftShanghaiDate(getShanghaiParts().date, -1);
  return {
    ah,
    ab,
    ipo,
    bonds,
    cbArb,
    monitors,
    eventArbNextDaySummary: pushRuntimeDomain.getEventArbDailyNewItems(yesterday),
  };
}

async function collectAlertDatasets() {
  const cbArb = await getDataset('cbArb');
  return { cbArb };
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

async function pushEventAlertsToWeCom(options = {}) {
  return eventAlertService.pushConvertibleBondAlerts(options);
}

async function pushManualEventAlertsToWeCom(options = {}) {
  return pushEventAlertsToWeCom({ ...options, force: true });
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

async function pushByModulesToWeCom(options = {}) {
  return mainSummaryService.pushByModulesToWeCom(options);
}

async function pushManualSummaryToWeCom(options = {}) {
  const attemptAt = nowIso();
  pushRuntimeDomain.setPushAttempt('main', attemptAt);
  try {
    const result = await mainSummaryService.pushByModulesToWeCom(options);
    pushRuntimeDomain.setPushSuccess('main', attemptAt, getShanghaiParts().date);
    pushRuntimeDomain.save();
    return result;
  } catch (error) {
    pushRuntimeDomain.setPushError('main', error?.message || error);
    pushRuntimeDomain.save();
    throw error;
  }
}

async function runMainPushIfNeeded() {
  return weComScheduler.runMainPushIfNeeded();
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
  pushByModulesToWeCom: pushManualSummaryToWeCom,
  pushEventAlertsToWeCom: pushManualEventAlertsToWeCom,
  getCbRightsIssuePushConfig: () => cbRightsIssuePushConfigDomain.getConfig(),
  updateCbRightsIssuePushConfig: (payload) => cbRightsIssuePushConfigDomain.updateConfig(payload),
  buildCbRightsIssuePushConfigResponse: buildCbRightsIssuePushConfigViewModel,
  getLofArbPushConfig: () => lofArbPushConfigDomain.getConfig(),
  updateLofArbPushConfig: (payload) => lofArbPushConfigDomain.updateConfig({
    ...(payload && typeof payload === 'object' ? payload : {}),
    times: ['14:00'],
  }),
  buildLofArbPushConfigResponse: buildLofArbPushConfigViewModel,
});

registerDashboardRoutes({
  app,
  nowIso,
  getHealthSnapshot: buildHealthSnapshot,
  getDashboardUiConfig: () => ({
    dashboardTheme: DASHBOARD_THEME,
    tableUi: {
      desktopFontPx: DASHBOARD_TABLE_UI.desktopFontPx,
      desktopHeaderFontPx: DASHBOARD_TABLE_UI.desktopHeaderFontPx,
      desktopLineHeight: DASHBOARD_TABLE_UI.desktopLineHeight,
      desktopCellPaddingY: DASHBOARD_TABLE_UI.desktopCellPaddingY,
      desktopCellPaddingX: DASHBOARD_TABLE_UI.desktopCellPaddingX,
      tabletFontPx: DASHBOARD_TABLE_UI.tabletFontPx,
      minWidthByKind: { ...DASHBOARD_TABLE_UI.minWidthByKind },
    },
    autoRefresh: {
      enabled: DASHBOARD_AUTO_REFRESH.enabled,
      intervalMs: DASHBOARD_AUTO_REFRESH.intervalMs,
      mode: DASHBOARD_AUTO_REFRESH.mode,
      currentTabOnly: DASHBOARD_AUTO_REFRESH.currentTabOnly,
      reloadDataOnCacheChange: DASHBOARD_AUTO_REFRESH.reloadDataOnCacheChange,
    },
    moduleNotes: { ...DASHBOARD_MODULE_NOTES },
  }),
  getDashboardResourceStatus,
  getAccessInfo: () => ({
    serverBaseUrl: SERVER_BASE_URL,
    publicBaseUrl: PUBLIC_BASE_URL,
    publicHealthUrl: PUBLIC_HEALTHCHECK_URL,
    environment: APP_ENVIRONMENT,
  }),
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
  console.log(`Alpha Monitor version    : ${RUNTIME_VERSION.gitShortSha || APP_PACKAGE_VERSION}`);
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





