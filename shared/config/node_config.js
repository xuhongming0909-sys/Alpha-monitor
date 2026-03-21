"use strict";

/**
 * Node 侧统一配置读取器。
 * 规则是“配置即合同，密钥可由环境变量注入”，不再对普通业务参数做环境变量兜底。
 */

const fs = require("fs");
const path = require("path");
const { parse } = require("yaml");

const ROOT_DIR = path.resolve(__dirname, "..", "..");
const CONFIG_FILE = path.join(ROOT_DIR, "config.yaml");
const ENV_FILE = path.join(ROOT_DIR, ".env");

let cachedConfig = null;

const SECRET_ENV_PATHS = [
  { path: ["notification", "wecom", "webhook_url"], env: "WECOM_WEBHOOK_URL" },
  { path: ["notification", "wecom", "push_html_url"], env: "PUSH_HTML_URL" },
  { path: ["notification", "wecom", "push_html_url"], env: "ALPHA_MONITOR_HTML_URL" },
  { path: ["strategy", "merger", "deepseek_api_key"], env: "DEEPSEEK_API_KEY" },
  { path: ["strategy", "merger", "deepseek_base_url"], env: "DEEPSEEK_BASE_URL" },
  { path: ["data_fetch", "plugins", "convertible_bond", "jisilu_cookie"], env: "JISILU_COOKIE" },
];

function loadEnvFile(filePath = ENV_FILE) {
  if (!fs.existsSync(filePath)) return;

  const lines = fs.readFileSync(filePath, "utf8").split(/\r?\n/);
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;

    const index = trimmed.indexOf("=");
    if (index <= 0) continue;

    const key = trimmed.slice(0, index).trim();
    if (!key || Object.prototype.hasOwnProperty.call(process.env, key)) continue;

    let value = trimmed.slice(index + 1).trim();
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }
    process.env[key] = value;
  }
}

function deepClone(value) {
  if (Array.isArray(value)) return value.map(deepClone);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, deepClone(item)]));
  }
  return value;
}

function getAtPath(target, pathParts) {
  let current = target;
  for (const part of pathParts) {
    if (!current || typeof current !== "object" || !(part in current)) {
      return undefined;
    }
    current = current[part];
  }
  return current;
}

function setAtPath(target, pathParts, value) {
  let current = target;
  for (let index = 0; index < pathParts.length - 1; index += 1) {
    const part = pathParts[index];
    if (!current[part] || typeof current[part] !== "object" || Array.isArray(current[part])) {
      current[part] = {};
    }
    current = current[part];
  }
  current[pathParts[pathParts.length - 1]] = value;
}

function isMissingValue(value) {
  return value === undefined || value === null || value === "";
}

function resolveEnvPlaceholders(value) {
  if (Array.isArray(value)) {
    return value.map(resolveEnvPlaceholders);
  }

  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, resolveEnvPlaceholders(item)]));
  }

  if (typeof value !== "string") return value;

  const exactMatch = value.match(/^\$\{([A-Z0-9_]+)\}$/);
  if (exactMatch) {
    return process.env[exactMatch[1]] ?? "";
  }

  return value.replace(/\$\{([A-Z0-9_]+)\}/g, (_, envName) => process.env[envName] ?? "");
}

function applySecretEnv(config) {
  for (const item of SECRET_ENV_PATHS) {
    const currentValue = getAtPath(config, item.path);
    if (!isMissingValue(currentValue)) continue;

    const envValue = process.env[item.env];
    if (isMissingValue(envValue)) continue;
    setAtPath(config, item.path, envValue);
  }
  return config;
}

function normalizePythonCandidates(config) {
  if (!config.app || typeof config.app !== "object" || Array.isArray(config.app)) {
    config.app = {};
  }
  const current = Array.isArray(config?.app?.python_bin_candidates)
    ? config.app.python_bin_candidates.filter(Boolean)
    : [];
  const configuredPython = String(config?.app?.python_bin || "").trim();
  if (configuredPython) {
    config.app.python_bin = configuredPython;
    config.app.python_bin_candidates = Array.from(new Set([configuredPython, ...current]));
    return config;
  }

  const platformDefaults = process.platform === "win32" ? ["python", "python3"] : ["python3", "python"];
  config.app.python_bin_candidates = Array.from(new Set([...current, ...platformDefaults]));
  return config;
}

function readConfigFile() {
  if (!fs.existsSync(CONFIG_FILE)) return {};
  const text = fs.readFileSync(CONFIG_FILE, "utf8");
  const parsed = parse(text);
  return parsed && typeof parsed === "object" ? parsed : {};
}

function loadConfig(options = {}) {
  if (cachedConfig && !options.reload) return deepClone(cachedConfig);

  loadEnvFile();
  const config = normalizePythonCandidates(applySecretEnv(resolveEnvPlaceholders(readConfigFile())));
  cachedConfig = config;
  return deepClone(config);
}

function getConfig() {
  return loadConfig();
}

module.exports = {
  ROOT_DIR,
  CONFIG_FILE,
  ENV_FILE,
  loadEnvFile,
  loadConfig,
  getConfig,
};

