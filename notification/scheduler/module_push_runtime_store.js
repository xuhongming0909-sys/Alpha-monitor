"use strict";

const { getShanghaiParts } = require("../../shared/time/shanghai_time");

/**
 * 模块级推送运行态。
 * 只记录独立模块自己的定时发送记录与最近成功/失败状态，
 * 并在读取当日计划时自动清理不可信的未来时段记录。
 */
function createModulePushRuntimeStore(options = {}) {
  const state = options.state || {};
  const save = typeof options.save === "function" ? options.save : () => state;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();
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

  function getPushSuccessIso() {
    ensureStateShape();
    return state.lastSuccessAt || null;
  }

  function getShanghaiPartsFromIso(isoText) {
    const timestamp = Date.parse(String(isoText || "").trim());
    if (!Number.isFinite(timestamp)) return null;
    const parts = getShanghaiParts(new Date(timestamp));
    const hour = Number(parts?.hour);
    const minute = Number(parts?.minute);
    if (!parts || !Number.isFinite(hour) || !Number.isFinite(minute)) return null;
    return {
      date: String(parts.date || "").trim(),
      hour,
      minute,
      minutes: hour * 60 + minute,
    };
  }

  function sanitizeScheduledPushRecord(dateText, scheduleTimes) {
    const date = String(dateText || "").trim();
    if (!date) return { times: [], changed: false };

    const existing = getPushRecord(date);
    const allowed = new Set(normalizePushTimes(scheduleTimes));
    let next = existing.filter((item) => allowed.has(item));

    const today = getShanghaiPartsFromIso(nowIso())?.date || null;
    const latestSuccess = getShanghaiPartsFromIso(getPushSuccessIso());
    if (today && date === today) {
      if (latestSuccess?.date === today) {
        next = next.filter((item) => (parsePushMinutes(item) ?? Number.POSITIVE_INFINITY) <= latestSuccess.minutes);
      } else {
        next = [];
      }
    }

    const changed = next.length !== existing.length || next.some((item, index) => item !== existing[index]);
    if (changed) {
      setPushRecord(date, next);
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
    getPushSuccessIso,
    getShanghaiPartsFromIso,
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
