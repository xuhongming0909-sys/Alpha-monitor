// AI-SUMMARY: 推送运行时存储：推送状态与历史
// 对应 INDEX.md §9 文件摘要索引

"use strict";

const { getShanghaiParts } = require("../../shared/time/shanghai_time");

/**
 * 推送运行态存储。
 * 负责记录定时推送记录、异动冷却记录，以及事件套利新增项的次日汇总缓冲。
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
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();
  function normalizePushTimes(items) {
    return Array.from(new Set(
      (Array.isArray(items) ? items : [])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));
  }

  function getPushRecordMap(recordType) {
    const key = recordType === "main" ? "mainPushRecords" : "mainPushRecords";
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
    state.mainPushRecords = Object.fromEntries(
      keepDates.map((item) => [item, records[item]])
    );
  }

  function getPushSuccessIso(recordType) {
    if (recordType === "event_alert") {
      return state.lastEventAlertSuccessAt || null;
    }
    return state.lastMainPushSuccessAt || null;
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

  function sanitizeScheduledPushRecord(recordType, dateText, scheduleTimes) {
    const date = String(dateText || "").trim();
    if (!date) {
      return { times: [], changed: false };
    }

    const existing = getPushRecord(recordType, date);
    const allowedTimes = new Set(normalizePushTimes(scheduleTimes));
    let next = existing.filter((item) => allowedTimes.has(item));

    const today = getShanghaiPartsFromIso(nowIso())?.date || null;
    const latestSuccess = getShanghaiPartsFromIso(getPushSuccessIso(recordType));
    if (today && date === today) {
      if (latestSuccess?.date === today) {
        next = next.filter((item) => (parsePushMinutes(item) ?? Number.POSITIVE_INFINITY) <= latestSuccess.minutes);
      } else {
        next = [];
      }
    }

    const changed = next.length !== existing.length || next.some((item, index) => item !== existing[index]);
    if (changed) {
      setPushRecord(recordType, date, next);
    }
    return { times: next, changed };
  }

  function setPushAttempt(recordType, isoText) {
    const value = isoText || null;
    if (recordType === "event_alert") {
      state.lastEventAlertAttemptAt = value;
      return;
    }
    state.lastMainPushAttemptAt = value;
  }

  function setPushSuccess(recordType, isoText, dateText) {
    const value = isoText || null;
    if (recordType === "event_alert") {
      state.lastEventAlertSuccessAt = value;
      state.lastEventAlertError = null;
      return;
    }
    state.lastMainPushSuccessAt = value;
    state.lastMainPushError = null;
    if (dateText) state.lastMainPushDate = dateText;
  }

  function setPushError(recordType, message) {
    const text = String(message || "").trim() || null;
    if (recordType === "event_alert") {
      state.lastEventAlertError = text;
      return;
    }
    state.lastMainPushError = text;
  }

  function getEventAlertRecordMap() {
    const records = (state.eventAlertRecords && typeof state.eventAlertRecords === "object")
      ? state.eventAlertRecords
      : {};
    state.eventAlertRecords = records;
    return records;
  }

  function getEventAlertRecord(alertKey) {
    const records = getEventAlertRecordMap();
    const record = records[String(alertKey || "").trim()];
    return record && typeof record === "object" ? record : null;
  }

  function isEventAlertDue(alertKey, cooldownMinutes) {
    const record = getEventAlertRecord(alertKey);
    if (!record?.sentAt) return true;
    const sentAt = Date.parse(record.sentAt);
    if (!Number.isFinite(sentAt)) return true;
    const cooldownMs = Math.max(1, Number(cooldownMinutes) || 30) * 60 * 1000;
    return (Date.now() - sentAt) >= cooldownMs;
  }

  function setEventAlertRecord(alertKey, payload = {}) {
    const key = String(alertKey || "").trim();
    if (!key) return;
    const records = getEventAlertRecordMap();
    records[key] = {
      ...(records[key] && typeof records[key] === "object" ? records[key] : {}),
      ...payload,
    };
    const entries = Object.entries(records).sort((a, b) => {
      const aTime = Date.parse(a[1]?.sentAt || "") || 0;
      const bTime = Date.parse(b[1]?.sentAt || "") || 0;
      return bTime - aTime;
    }).slice(0, 500);
    state.eventAlertRecords = Object.fromEntries(entries);
  }

  function getEventArbSeenMap() {
    const map = (state.eventArbSeenItems && typeof state.eventArbSeenItems === "object")
      ? state.eventArbSeenItems
      : {};
    state.eventArbSeenItems = map;
    return map;
  }

  function getEventArbDailyNewMap() {
    const map = (state.eventArbDailyNewItems && typeof state.eventArbDailyNewItems === "object")
      ? state.eventArbDailyNewItems
      : {};
    state.eventArbDailyNewItems = map;
    return map;
  }

  function summarizeEventArbRow(row, dateText) {
    const category = String(row?.category || "").trim();
    const categoryLabelMap = {
      hk_private: "港股私有化",
      cn_private: "中概私有化",
      a_event: "A股事件",
      rights_issue: "配股",
      announcement_pool: "公告池",
    };
    const symbol = String(row?.symbol || "").trim();
    const eventType = String(row?.eventType || "").trim();
    const stage = String(row?.eventStage || "").trim();
    const spreadText = String(row?.spreadText || row?.spreadRateText || "").trim();
    return {
      id: String(row?.id || `${category}:${symbol}:${eventType}:${stage}`).trim(),
      category,
      categoryLabel: categoryLabelMap[category] || category,
      symbol,
      name: String(row?.name || "").trim(),
      eventType,
      eventStage: stage,
      spreadText,
      firstSeenDate: dateText,
    };
  }

  function syncEventArbSeenItems(rows, dateText) {
    const seenMap = getEventArbSeenMap();
    const dailyMap = getEventArbDailyNewMap();
    const today = String(dateText || "").trim();
    const currentItems = (Array.isArray(rows) ? rows : [])
      .filter((row) => row && typeof row === "object")
      .map((row) => summarizeEventArbRow(row, today))
      .filter((item) => item.id);

    if (!Object.keys(seenMap).length) {
      currentItems.forEach((item) => {
        seenMap[item.id] = {
          firstSeenDate: today,
          lastSeenAt: nowIso(),
        };
      });
      return { seeded: true, newItems: [] };
    }

    const newItems = [];
    currentItems.forEach((item) => {
      if (!seenMap[item.id]) {
        seenMap[item.id] = {
          firstSeenDate: today,
          lastSeenAt: nowIso(),
        };
        newItems.push(item);
      } else {
        seenMap[item.id].lastSeenAt = nowIso();
      }
    });

    if (newItems.length) {
      const existing = Array.isArray(dailyMap[today]) ? dailyMap[today] : [];
      const merged = [...existing];
      const seenIds = new Set(existing.map((item) => item.id));
      newItems.forEach((item) => {
        if (!seenIds.has(item.id)) {
          merged.push(item);
          seenIds.add(item.id);
        }
      });
      dailyMap[today] = merged;
      const keepDates = Object.keys(dailyMap).sort().slice(-10);
      state.eventArbDailyNewItems = Object.fromEntries(keepDates.map((item) => [item, dailyMap[item]]));
    }

    return { seeded: false, newItems };
  }

  function getEventArbDailyNewItems(dateText) {
    const dailyMap = getEventArbDailyNewMap();
    return Array.isArray(dailyMap[dateText]) ? dailyMap[dateText] : [];
  }

  return {
    state,
    normalizePushTimes,
    getPushRecordMap,
    getPushRecord,
    setPushRecord,
    getPushSuccessIso,
    getShanghaiPartsFromIso,
    sanitizeScheduledPushRecord,
    setPushAttempt,
    setPushSuccess,
    setPushError,
    getEventAlertRecordMap,
    getEventAlertRecord,
    isEventAlertDue,
    setEventAlertRecord,
    syncEventArbSeenItems,
    getEventArbDailyNewItems,
    save,
  };
}

module.exports = {
  createPushRuntimeStore,
};
