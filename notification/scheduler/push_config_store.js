"use strict";

/**
 * 推送配置存储。
 * 页面只允许修改定时摘要时间与模块开关，旧可转债冷却规则已退役。
 */
function createPushConfigStore(options = {}) {
  const state = options.state || {};
  const defaultConfig = options.defaultConfig || {};
  const save = typeof options.save === "function" ? options.save : () => state;

  function parsePushMinutes(timeText) {
    const [hour, minute] = String(timeText || "").split(":").map((item) => Number(item));
    if (!Number.isFinite(hour) || !Number.isFinite(minute)) return null;
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
    return (hour * 60) + minute;
  }

  function normalizePushConfig(input = {}) {
    const fallbackModules = { ...(defaultConfig.modules || {}) };
    const rawModules = {
      ...fallbackModules,
      ...((input.modules && typeof input.modules === "object") ? input.modules : {}),
    };
    const modules = Object.fromEntries(
      Object.keys(fallbackModules).map((key) => [key, Boolean(rawModules[key])])
    );

    const defaultTime = String(defaultConfig.time || "08:00").trim();
    const rawTimes = Array.isArray(input.times) ? input.times : defaultConfig.times;
    const times = Array.from(new Set(
      (Array.isArray(rawTimes) ? rawTimes : [defaultTime])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    ))
      .sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0))
      .slice(0, 2);

    while (times.length < 2) {
      times.push(times[0] || defaultTime);
    }

    return {
      enabled: typeof input.enabled === "boolean" ? input.enabled : Boolean(defaultConfig.enabled),
      time: times[0],
      times,
      modules,
    };
  }

  function getPushConfig() {
    const normalized = normalizePushConfig(state);
    state.enabled = normalized.enabled;
    state.time = normalized.time;
    state.times = normalized.times;
    state.modules = normalized.modules;
    return normalized;
  }

  function updatePushConfig(input = {}) {
    const normalized = normalizePushConfig(input);
    state.enabled = normalized.enabled;
    state.time = normalized.time;
    state.times = normalized.times;
    state.modules = normalized.modules;
    save();
    return normalized;
  }

  return {
    state,
    parsePushMinutes,
    normalizePushConfig,
    getPushConfig,
    updatePushConfig,
    save,
  };
}

module.exports = {
  createPushConfigStore,
};
