"use strict";

/**
 * 推送配置存储。
 * 负责normalizer UI 传入配置、读取当前配置、写回运行态配置文件。
 */

function createPushConfigStore(options = {}) {
  const state = options.state || {};
  const defaultConfig = options.defaultConfig || {};
  const save = typeof options.save === "function" ? options.save : () => state;

  function parsePushMinutes(timeText) {
    const [h, m] = String(timeText || "").split(":").map((item) => Number(item));
    if (!Number.isFinite(h) || !Number.isFinite(m)) return null;
    if (h < 0 || h > 23 || m < 0 || m > 59) return null;
    return h * 60 + m;
  }

  function normalizePushConfig(input = {}) {
    const fallbackModules = { ...(defaultConfig.modules || {}) };
    const rawModules = (input.modules && typeof input.modules === "object") ? input.modules : fallbackModules;
    const modules = Object.fromEntries(
      Object.keys(fallbackModules).map((key) => [key, Boolean(rawModules[key])])
    );

    const defaultTime = String(defaultConfig.time || "08:00").trim();
    const rawTime = String(input.time || defaultTime).trim();
    const timeFallback = /^\d{2}:\d{2}$/.test(rawTime) && parsePushMinutes(rawTime) !== null
      ? rawTime
      : defaultTime;
    const rawTimes = Array.isArray(input.times) ? input.times : [timeFallback];
    const times = Array.from(new Set(
      rawTimes
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    ))
      .sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0))
      .slice(0, 3);
    if (!times.length) times.push(defaultTime);

    const defaultMergerSchedule = defaultConfig.mergerSchedule || { enabled: false, time: defaultTime };
    const rawMergerSchedule = (input.mergerSchedule && typeof input.mergerSchedule === "object")
      ? input.mergerSchedule
      : {};
    const mergerTime = String(rawMergerSchedule.time || defaultMergerSchedule.time || defaultTime).trim();
    const mergerSchedule = {
      enabled: typeof rawMergerSchedule.enabled === "boolean"
        ? rawMergerSchedule.enabled
        : Boolean(defaultMergerSchedule.enabled),
      time: /^\d{2}:\d{2}$/.test(mergerTime) && parsePushMinutes(mergerTime) !== null
        ? mergerTime
        : String(defaultMergerSchedule.time || defaultTime),
    };

    return {
      enabled: typeof input.enabled === "boolean" ? input.enabled : Boolean(defaultConfig.enabled),
      time: times[0],
      times,
      modules,
      mergerSchedule,
    };
  }

  function getPushConfig() {
    const normalized = normalizePushConfig(state);
    state.enabled = normalized.enabled;
    state.time = normalized.time;
    state.times = normalized.times;
    state.modules = normalized.modules;
    state.mergerSchedule = normalized.mergerSchedule;
    return normalized;
  }

  function updatePushConfig(input = {}) {
    const normalized = normalizePushConfig(input);
    state.enabled = normalized.enabled;
    state.time = normalized.time;
    state.times = normalized.times;
    state.modules = normalized.modules;
    state.mergerSchedule = normalized.mergerSchedule;
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


