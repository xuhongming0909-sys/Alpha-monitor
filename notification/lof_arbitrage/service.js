"use strict";

function createLofArbitragePushService(options = {}) {
  const getConfig = typeof options.getConfig === "function" ? options.getConfig : () => ({ enabled: false, times: [] });
  const runtimeStore = options.runtimeStore;
  const stateStore = options.stateStore || {};
  const saveStateStore = typeof options.saveStateStore === "function" ? options.saveStateStore : () => {};
  const getDataset = options.getDataset;
  const sendMarkdown = options.sendMarkdown;
  const buildMarkdown = options.buildMarkdown;
  const getShanghaiParts = options.getShanghaiParts;
  const parsePushMinutes = options.parsePushMinutes;
  const isTradingWeekday = typeof options.isTradingWeekday === "function" ? options.isTradingWeekday : () => true;
  const isDeliveryAvailable = typeof options.isDeliveryAvailable === "function" ? options.isDeliveryAvailable : () => true;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();
  const logInfo = options.logInfo || ((message) => console.info(message));
  const logError = options.logError || ((scope, error) => console.error(scope, error));

  function ensureStateShape() {
    if (!stateStore.seenEntryMap || typeof stateStore.seenEntryMap !== "object") stateStore.seenEntryMap = {};
    if (!Object.prototype.hasOwnProperty.call(stateStore, "lastInstantAttemptAt")) stateStore.lastInstantAttemptAt = null;
    if (!Object.prototype.hasOwnProperty.call(stateStore, "lastInstantSuccessAt")) stateStore.lastInstantSuccessAt = null;
    if (!Object.prototype.hasOwnProperty.call(stateStore, "lastInstantError")) stateStore.lastInstantError = null;
  }

  function setSeenEntryMap(nextMap) {
    ensureStateShape();
    stateStore.seenEntryMap = nextMap;
    saveStateStore();
  }

  function buildEntryKey(poolType, row) {
    return `${poolType}:${row?.code || ""}`;
  }

  async function readPayload() {
    const result = await getDataset("lofArb");
    if (!result || result.success === false) {
      throw new Error(result?.error || "lof_arbitrage_dataset_unavailable");
    }
    const payload = result?.data && typeof result.data === "object" ? result.data : {};
    return {
      rows: Array.isArray(payload.rows) ? payload.rows : [],
      limitedMonitorRows: Array.isArray(payload.limitedMonitorRows) ? payload.limitedMonitorRows : [],
      unlimitedMonitorRows: Array.isArray(payload.unlimitedMonitorRows) ? payload.unlimitedMonitorRows : [],
      sourceSummary: payload.sourceSummary && typeof payload.sourceSummary === "object" ? payload.sourceSummary : {},
      rebuildStatus: payload.rebuildStatus && typeof payload.rebuildStatus === "object" ? payload.rebuildStatus : {},
      updateTime: result?.updateTime || payload?.updateTime || null,
    };
  }

  function collectNewEntries(payload) {
    ensureStateShape();
    const nextMap = {};
    const newLimitedRows = [];
    const newUnlimitedRows = [];
    const seenEntryMap = stateStore.seenEntryMap || {};

    for (const row of payload.limitedMonitorRows) {
      const key = buildEntryKey("limited", row);
      nextMap[key] = payload.updateTime || nowIso();
      if (!seenEntryMap[key]) newLimitedRows.push(row);
    }
    for (const row of payload.unlimitedMonitorRows) {
      const key = buildEntryKey("unlimited", row);
      nextMap[key] = payload.updateTime || nowIso();
      if (!seenEntryMap[key]) newUnlimitedRows.push(row);
    }

    return {
      nextMap,
      newLimitedRows,
      newUnlimitedRows,
    };
  }

  async function pushInstantIfNeeded() {
    const payload = await readPayload();
    const config = getConfig();
    const { nextMap, newLimitedRows, newUnlimitedRows } = collectNewEntries(payload);
    const newCount = newLimitedRows.length + newUnlimitedRows.length;

    if (!newCount || !config.enabled) {
      setSeenEntryMap(nextMap);
      return { success: true, skipped: true, reason: newCount ? "module_disabled" : "no_new_entries", total: newCount };
    }
    if (!isDeliveryAvailable()) {
      return { success: true, skipped: true, reason: "delivery_not_configured", total: newCount };
    }

    const attemptAt = nowIso();
    ensureStateShape();
    stateStore.lastInstantAttemptAt = attemptAt;
    stateStore.lastInstantError = null;
    saveStateStore();

    try {
      const markdown = buildMarkdown(payload, {
        mode: "instant",
        limitedRows: newLimitedRows,
        unlimitedRows: newUnlimitedRows,
        maxItems: 20,
      });
      await sendMarkdown(markdown);
      stateStore.lastInstantSuccessAt = attemptAt;
      stateStore.lastInstantError = null;
      stateStore.seenEntryMap = nextMap;
      saveStateStore();
      return { success: true, skipped: false, total: newCount, attemptAt };
    } catch (error) {
      stateStore.lastInstantError = String(error?.message || error || "unknown_error");
      saveStateStore();
      throw error;
    }
  }

  async function pushNow() {
    const payload = await readPayload();
    const total = payload.limitedMonitorRows.length + payload.unlimitedMonitorRows.length;
    if (!total) {
      return { success: false, skipped: true, reason: "empty_monitor_pools", total: 0 };
    }
    if (!isDeliveryAvailable()) {
      return { success: true, skipped: true, reason: "delivery_not_configured", total };
    }

    const attemptAt = nowIso();
    runtimeStore.setAttempt(attemptAt);
    runtimeStore.save();
    try {
      const markdown = buildMarkdown(payload, { mode: "scheduled", maxItems: 20 });
      await sendMarkdown(markdown);
      runtimeStore.setSuccess(attemptAt);
      runtimeStore.save();
      return { success: true, skipped: false, total, attemptAt };
    } catch (error) {
      runtimeStore.setError(attemptAt, error?.message || error);
      runtimeStore.save();
      throw error;
    }
  }

  async function runIfNeeded() {
    const config = getConfig();
    if (!config.enabled) return;
    if (config.tradingDaysOnly !== false && !isTradingWeekday()) return;

    const sh = getShanghaiParts();
    const scheduleTimes = runtimeStore.normalizePushTimes(config.times);
    if (!scheduleTimes.length) return;

    const sanitized = runtimeStore.sanitizeScheduledPushRecord(sh.date, scheduleTimes);
    const sentTimes = sanitized.times.slice();
    const nowMinutes = sh.hour * 60 + sh.minute;
    if (sanitized.changed) {
      runtimeStore.save();
      logInfo(`[push][lof_arbitrage] sanitized dirty records date=${sh.date} kept=${sentTimes.join(",") || "none"}`);
    }

    for (const timeText of scheduleTimes) {
      const targetMinutes = parsePushMinutes(timeText);
      if (targetMinutes === null) continue;
      if (nowMinutes < targetMinutes) {
        logInfo(`[push][lof_arbitrage] slot=${timeText} date=${sh.date} skipped=not_due_yet`);
        continue;
      }
      if (sentTimes.includes(timeText)) {
        logInfo(`[push][lof_arbitrage] slot=${timeText} date=${sh.date} skipped=already_sent`);
        continue;
      }

      logInfo(`[push][lof_arbitrage] slot=${timeText} date=${sh.date} action=attempt`);
      try {
        const result = await pushNow();
        if (result?.skipped) {
          logInfo(`[push][lof_arbitrage] slot=${timeText} date=${sh.date} skipped=${result.reason || "empty"}`);
          continue;
        }
        sentTimes.push(timeText);
        runtimeStore.setPushRecord(sh.date, sentTimes);
        runtimeStore.save();
        logInfo(`[push][lof_arbitrage] slot=${timeText} date=${sh.date} action=success`);
      } catch (error) {
        logInfo(`[push][lof_arbitrage] slot=${timeText} date=${sh.date} action=failed error=${error?.message || error}`);
        logError("[push][lof_arbitrage] schedule failed:", error?.message || error);
      }
    }
  }

  return {
    ensureStateShape,
    readPayload,
    pushInstantIfNeeded,
    pushNow,
    runIfNeeded,
  };
}

module.exports = {
  createLofArbitragePushService,
};
