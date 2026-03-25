"use strict";

/**
 * 模块级推送运行态。
 * 只记录独立模块自己的定时发送记录与最近成功/失败状态。
 */
function createModulePushRuntimeStore(options = {}) {
  const state = options.state || {};
  const save = typeof options.save === "function" ? options.save : () => state;
  const parsePushMinutes = typeof options.parsePushMinutes === "function"
    ? options.parsePushMinutes
    : ((value) => {
      const [hour, minute] = String(value || "").split(":").map((item) => Number(item));
      if (!Number.isFinite(hour) || !Number.isFinite(minute)) return null;
      if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
      return (hour * 60) + minute;
    });

  function ensureStateShape() {
    if (!state.pushRecords || typeof state.pushRecords !== "object") state.pushRecords = {};
    if (!Object.prototype.hasOwnProperty.call(state, "lastAttemptAt")) state.lastAttemptAt = null;
    if (!Object.prototype.hasOwnProperty.call(state, "lastSuccessAt")) state.lastSuccessAt = null;
    if (!Object.prototype.hasOwnProperty.call(state, "lastError")) state.lastError = null;
    return state;
  }

  function normalizePushTimes(items) {
    return Array.from(new Set(
      (Array.isArray(items) ? items : [])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));
  }

  function getPushRecord(dateText) {
    ensureStateShape();
    return normalizePushTimes(state.pushRecords[String(dateText || "").trim()]);
  }

  function setPushRecord(dateText, times) {
    ensureStateShape();
    const date = String(dateText || "").trim();
    if (!date) return;
    state.pushRecords[date] = normalizePushTimes(times);
    const keepDates = Object.keys(state.pushRecords).sort().slice(-10);
    state.pushRecords = Object.fromEntries(
      keepDates.map((item) => [item, state.pushRecords[item]])
    );
  }

  function sanitizeScheduledPushRecord(dateText, scheduleTimes) {
    const existing = getPushRecord(dateText);
    const allowed = new Set(normalizePushTimes(scheduleTimes));
    const next = existing.filter((item) => allowed.has(item));
    const changed = next.length !== existing.length || next.some((item, index) => item !== existing[index]);
    if (changed) {
      setPushRecord(dateText, next);
    }
    return { times: next, changed };
  }

  function setAttempt(value) {
    ensureStateShape();
    state.lastAttemptAt = value || null;
  }

  function setSuccess(value) {
    ensureStateShape();
    state.lastAttemptAt = value || null;
    state.lastSuccessAt = value || null;
    state.lastError = null;
  }

  function setError(value, error) {
    ensureStateShape();
    state.lastAttemptAt = value || null;
    state.lastError = String(error || "").trim() || null;
  }

  return {
    state,
    ensureStateShape,
    normalizePushTimes,
    getPushRecord,
    setPushRecord,
    sanitizeScheduledPushRecord,
    setAttempt,
    setSuccess,
    setError,
    save,
  };
}

module.exports = {
  createModulePushRuntimeStore,
};
