"use strict";

/**
 * 模块级定时推送配置存储。
 * 负责 enabled/times/tradingDaysOnly 这类模块推送配置字段。
 */
function createModulePushConfigStore(options = {}) {
  const state = options.state || {};
  const defaultConfig = options.defaultConfig || {};
  const save = typeof options.save === "function" ? options.save : () => state;
  const maxTimes = Number.isFinite(Number(options.maxTimes)) && Number(options.maxTimes) > 0
    ? Math.max(1, Math.floor(Number(options.maxTimes)))
    : 2;

  function parsePushMinutes(timeText) {
    const [hour, minute] = String(timeText || "").split(":").map((item) => Number(item));
    if (!Number.isFinite(hour) || !Number.isFinite(minute)) return null;
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
    return (hour * 60) + minute;
  }

  function normalizeTimes(inputTimes) {
    const fallbackTimes = Array.isArray(defaultConfig.times) ? defaultConfig.times : ["08:00", "14:30"];
    const values = Array.isArray(inputTimes) ? inputTimes : fallbackTimes;
    const parsedEntries = values
      .map((item) => {
        const timeText = String(item || "").trim();
        if (!/^\d{2}:\d{2}$/.test(timeText)) return null;
        const minutes = parsePushMinutes(timeText);
        if (minutes === null) return null;
        return { timeText, minutes };
      })
      .filter(Boolean);

    const uniqueEntries = Array.from(new Map(
      parsedEntries.map((entry) => [entry.timeText, entry])
    ).values()).sort((a, b) => a.minutes - b.minutes);

    const normalized = uniqueEntries.map((entry) => entry.timeText);
    return normalized.length ? normalized.slice(0, maxTimes) : fallbackTimes.slice(0, maxTimes);
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
    return normalizeConfig(state);
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
