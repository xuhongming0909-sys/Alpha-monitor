"use strict";

/**
 * 推送运行态状态存储。
 * 负责记录某天哪些推送时点已经发送，避免重复推送。
 */

function createPushRuntimeStore(options = {}) {
  const state = options.state || {};
  const save = typeof options.save === "function" ? options.save : () => state;
  const parsePushMinutes = options.parsePushMinutes || ((value) => {
    const [h, m] = String(value || "").split(":").map((item) => Number(item));
    if (!Number.isFinite(h) || !Number.isFinite(m)) return null;
    if (h < 0 || h > 23 || m < 0 || m > 59) return null;
    return h * 60 + m;
  });

  function normalizePushTimes(items) {
    return Array.from(new Set(
      (Array.isArray(items) ? items : [])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));
  }

  function getPushRecordMap(recordType) {
    const key = recordType === "merger" ? "mergerPushRecords" : "mainPushRecords";
    const records = (state[key] && typeof state[key] === "object") ? state[key] : {};
    state[key] = records;
    return records;
  }

  function getPushRecord(recordType, date) {
    const records = getPushRecordMap(recordType);
    return normalizePushTimes(records[date]);
  }

  function setPushRecord(recordType, date, times) {
    const records = getPushRecordMap(recordType);
    records[date] = normalizePushTimes(times);
    const keepDates = Object.keys(records).sort().slice(-10);
    state[recordType === "merger" ? "mergerPushRecords" : "mainPushRecords"] = Object.fromEntries(
      keepDates.map((item) => [item, records[item]])
    );
  }

  function setLastMainPushDate(date) {
    state.lastMainPushDate = date || null;
  }

  function setLastMergerReportDate(date) {
    state.lastMergerReportDate = date || null;
  }

  function setPushAttempt(recordType, isoText) {
    const value = isoText || null;
    if (recordType === "merger") {
      state.lastMergerPushAttemptAt = value;
      return;
    }
    state.lastMainPushAttemptAt = value;
  }

  function setPushSuccess(recordType, isoText, dateText) {
    const value = isoText || null;
    if (recordType === "merger") {
      state.lastMergerPushSuccessAt = value;
      state.lastMergerPushError = null;
      if (dateText) state.lastMergerReportDate = dateText;
      return;
    }
    state.lastMainPushSuccessAt = value;
    state.lastMainPushError = null;
    if (dateText) state.lastMainPushDate = dateText;
  }

  function setPushError(recordType, message) {
    const text = String(message || "").trim() || null;
    if (recordType === "merger") {
      state.lastMergerPushError = text;
      return;
    }
    state.lastMainPushError = text;
  }

  return {
    state,
    normalizePushTimes,
    getPushRecordMap,
    getPushRecord,
    setPushRecord,
    setLastMainPushDate,
    setLastMergerReportDate,
    setPushAttempt,
    setPushSuccess,
    setPushError,
    save,
  };
}

module.exports = {
  createPushRuntimeStore,
};

