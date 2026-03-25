"use strict";

/**
 * 模块级定时推送配置存储。
 * 只负责 enabled/times，不混入其他业务字段。
 */
function createModulePushConfigStore(options = {}) {
  const state = options.state || {};
  const defaultConfig = options.defaultConfig || {};
  const save = typeof options.save === "function" ? options.save : () => state;

  function parsePushMinutes(timeText) {
    const [hour, minute] = String(timeText || "").split(":").map((item) => Number(item));
    if (!Number.isFinite(hour) || !Number.isFinite(minute)) return null;
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
    return (hour * 60) + minute;
  }

  function normalizeTimes(inputTimes) {
    const fallbackTimes = Array.isArray(defaultConfig.times) ? defaultConfig.times : ["08:00", "14:30"];
    const values = Array.isArray(inputTimes) ? inputTimes : fallbackTimes;
    const normalized = Array.from(new Set(
      values
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));

    return normalized.length ? normalized.slice(0, 2) : fallbackTimes.slice(0, 2);
  }

  function normalizeConfig(input = {}) {
    return {
      enabled: typeof input.enabled === "boolean" ? input.enabled : Boolean(defaultConfig.enabled),
      times: normalizeTimes(input.times),
      tradingDaysOnly: typeof input.tradingDaysOnly === "boolean"
        ? input.tradingDaysOnly
        : defaultConfig.tradingDaysOnly !== false,
    };
  }

  function getConfig() {
    const normalized = normalizeConfig(state);
    state.enabled = normalized.enabled;
    state.times = normalized.times;
    state.tradingDaysOnly = normalized.tradingDaysOnly;
    return normalized;
  }

  function updateConfig(input = {}) {
    const normalized = normalizeConfig(input);
    state.enabled = normalized.enabled;
    state.times = normalized.times;
    state.tradingDaysOnly = normalized.tradingDaysOnly;
    save();
    return normalized;
  }

  return {
    state,
    parsePushMinutes,
    normalizeConfig,
    getConfig,
    updateConfig,
    save,
  };
}

module.exports = {
  createModulePushConfigStore,
};
