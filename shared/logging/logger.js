// AI-SUMMARY: logging 日志服务：统一日志输出
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * 统一logger。
 * 当前先提供最基础的控制台日志能力，后续再把入口层日志逐步迁过来。
 */

const { getConfig } = require("../config/node_config");

const LEVEL_ORDER = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

function resolveLoggingConfig() {
  const config = getConfig();
  const logging = config.logging || {};
  return {
    level: String(logging.level || "info").toLowerCase(),
    consoleEnabled: logging.console_enabled !== false,
  };
}

function shouldLog(targetLevel, currentLevel) {
  return (LEVEL_ORDER[targetLevel] || 999) >= (LEVEL_ORDER[currentLevel] || LEVEL_ORDER.info);
}

function formatLine(level, scope, args) {
  const timestamp = new Date().toISOString();
  const prefix = `[${timestamp}] [${level.toUpperCase()}]${scope ? ` [${scope}]` : ""}`;
  return [prefix, ...args];
}

function createLogger(scope = "") {
  const config = resolveLoggingConfig();

  const logWithLevel = (level, args) => {
    if (!config.consoleEnabled) return;
    if (!shouldLog(level, config.level)) return;
    const line = formatLine(level, scope, args);
    const writer = level === "error" ? console.error : level === "warn" ? console.warn : console.log;
    writer(...line);
  };

  return {
    debug: (...args) => logWithLevel("debug", args),
    info: (...args) => logWithLevel("info", args),
    warn: (...args) => logWithLevel("warn", args),
    error: (...args) => logWithLevel("error", args),
  };
}

module.exports = {
  LEVEL_ORDER,
  resolveLoggingConfig,
  createLogger,
};


