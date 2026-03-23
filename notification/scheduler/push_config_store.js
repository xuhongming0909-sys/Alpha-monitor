"use strict";

/**
 * 推送配置存储。
 * 负责规范化 UI 写入的时间与冷却参数，不参与真正的推送判断。
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

  function normalizeCooldownMinutes(value, fallback) {
    const num = Number(value);
    if (!Number.isFinite(num)) return fallback;
    return Math.max(1, Math.min(1440, Math.round(num)));
  }

  function normalizePushConfig(input = {}) {
    const fallbackModules = { ...(defaultConfig.modules || {}) };
    const rawModules = (input.modules && typeof input.modules === "object") ? input.modules : fallbackModules;
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

    const defaultEventAlert = (defaultConfig.eventAlert && typeof defaultConfig.eventAlert === "object")
      ? defaultConfig.eventAlert
      : {};
    const rawEventAlert = (input.eventAlert && typeof input.eventAlert === "object")
      ? input.eventAlert
      : {};
    const defaultCbAlert = (defaultEventAlert.convertibleBond && typeof defaultEventAlert.convertibleBond === "object")
      ? defaultEventAlert.convertibleBond
      : {};
    const rawCbAlert = (rawEventAlert.convertibleBond && typeof rawEventAlert.convertibleBond === "object")
      ? rawEventAlert.convertibleBond
      : {};

    return {
      enabled: typeof input.enabled === "boolean" ? input.enabled : Boolean(defaultConfig.enabled),
      time: times[0],
      times,
      modules,
      eventAlert: {
        enabled: typeof rawEventAlert.enabled === "boolean"
          ? rawEventAlert.enabled
          : Boolean(defaultEventAlert.enabled),
        cooldownMinutes: normalizeCooldownMinutes(
          rawEventAlert.cooldownMinutes,
          normalizeCooldownMinutes(defaultEventAlert.cooldownMinutes, 30)
        ),
        convertibleBond: {
          convertPremiumLt: Number.isFinite(Number(rawCbAlert.convertPremiumLt))
            ? Number(rawCbAlert.convertPremiumLt)
            : Number(defaultCbAlert.convertPremiumLt ?? -3),
        },
      },
    };
  }

  function getPushConfig() {
    const normalized = normalizePushConfig(state);
    state.enabled = normalized.enabled;
    state.time = normalized.time;
    state.times = normalized.times;
    state.modules = normalized.modules;
    state.eventAlert = normalized.eventAlert;
    return normalized;
  }

  function updatePushConfig(input = {}) {
    const normalized = normalizePushConfig(input);
    state.enabled = normalized.enabled;
    state.time = normalized.time;
    state.times = normalized.times;
    state.modules = normalized.modules;
    state.eventAlert = normalized.eventAlert;
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
