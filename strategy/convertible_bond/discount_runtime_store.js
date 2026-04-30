// AI-SUMMARY: convertible_bond 配置/状态存储：运行时数据持久化
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * 可转债折价策略运行态只负责状态持久化，不参与公式计算。
 * 这样推送、页面、策略都从统一状态读取，但职责边界仍然清晰。
 */
function createConvertibleBondDiscountRuntimeStore(options = {}) {
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
    if (!state.monitorMap || typeof state.monitorMap !== "object") state.monitorMap = {};
    if (!state.signalStateMap || typeof state.signalStateMap !== "object") state.signalStateMap = {};
    if (!state.monitorPushRecords || typeof state.monitorPushRecords !== "object") state.monitorPushRecords = {};
    if (!Object.prototype.hasOwnProperty.call(state, "initializedDate")) state.initializedDate = null;
    if (!Object.prototype.hasOwnProperty.call(state, "lastBootstrapDate")) state.lastBootstrapDate = null;
    return state;
  }

  function getState() {
    return ensureStateShape();
  }

  function replaceStrategyState(nextState = {}) {
    ensureStateShape();
    state.initializedDate = nextState.initializedDate || null;
    state.lastBootstrapDate = nextState.lastBootstrapDate || null;
    state.monitorMap = (nextState.monitorMap && typeof nextState.monitorMap === "object")
      ? { ...nextState.monitorMap }
      : {};
    state.signalStateMap = (nextState.signalStateMap && typeof nextState.signalStateMap === "object")
      ? { ...nextState.signalStateMap }
      : {};
  }

  function normalizePushTimes(items) {
    return Array.from(new Set(
      (Array.isArray(items) ? items : [])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));
  }

  function getMonitorPushRecord(dateText) {
    ensureStateShape();
    return normalizePushTimes(state.monitorPushRecords[String(dateText || "").trim()]);
  }

  function setMonitorPushRecord(dateText, times) {
    ensureStateShape();
    const date = String(dateText || "").trim();
    if (!date) return;
    state.monitorPushRecords[date] = normalizePushTimes(times);
    const keepDates = Object.keys(state.monitorPushRecords).sort().slice(-10);
    state.monitorPushRecords = Object.fromEntries(
      keepDates.map((item) => [item, state.monitorPushRecords[item]])
    );
  }

  function setAttempt(key, value) {
    state[key] = value || null;
  }

  function setSuccess(attemptKey, successKey, errorKey, value) {
    state[attemptKey] = value || null;
    state[successKey] = value || null;
    state[errorKey] = null;
  }

  function setError(attemptKey, errorKey, attemptAt, error) {
    state[attemptKey] = attemptAt || null;
    state[errorKey] = String(error || "").trim() || null;
  }

  function setBuySignalAttempt(value) {
    setAttempt("lastBuySignalAttemptAt", value);
  }

  function setBuySignalSuccess(value) {
    setSuccess("lastBuySignalAttemptAt", "lastBuySignalSuccessAt", "lastBuySignalError", value);
  }

  function setBuySignalError(value, error) {
    setError("lastBuySignalAttemptAt", "lastBuySignalError", value, error);
  }

  function setSellSignalAttempt(value) {
    setAttempt("lastSellSignalAttemptAt", value);
  }

  function setSellSignalSuccess(value) {
    setSuccess("lastSellSignalAttemptAt", "lastSellSignalSuccessAt", "lastSellSignalError", value);
  }

  function setSellSignalError(value, error) {
    setError("lastSellSignalAttemptAt", "lastSellSignalError", value, error);
  }

  function setMonitorPushAttempt(value) {
    setAttempt("lastMonitorPushAttemptAt", value);
  }

  function setMonitorPushSuccess(value) {
    setSuccess("lastMonitorPushAttemptAt", "lastMonitorPushSuccessAt", "lastMonitorPushError", value);
  }

  function setMonitorPushError(value, error) {
    setError("lastMonitorPushAttemptAt", "lastMonitorPushError", value, error);
  }

  return {
    state,
    getState,
    replaceStrategyState,
    setBuySignalAttempt,
    setBuySignalSuccess,
    setBuySignalError,
    setSellSignalAttempt,
    setSellSignalSuccess,
    setSellSignalError,
    setMonitorPushAttempt,
    setMonitorPushSuccess,
    setMonitorPushError,
    getMonitorPushRecord,
    setMonitorPushRecord,
    save,
  };
}

module.exports = {
  createConvertibleBondDiscountRuntimeStore,
};
