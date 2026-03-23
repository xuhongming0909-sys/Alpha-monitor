"use strict";

/**
 * 企业微信定时调度器。
 * 负责读取推送配置，在固定时间发送摘要，并在每次 tick 中检查异动提醒。
 */
function createWeComScheduler(options = {}) {
  const getPushConfig = options.getPushConfig;
  const runtimeStore = options.runtimeStore;
  const pushByModulesToWeCom = options.pushByModulesToWeCom;
  const pushEventAlertsToWeCom = options.pushEventAlertsToWeCom;
  const syncEventArbSummaryState = options.syncEventArbSummaryState;
  const getShanghaiParts = options.getShanghaiParts;
  const parsePushMinutes = options.parsePushMinutes;
  const calendarMode = String(options.calendarMode || "daily").trim().toLowerCase();
  const isTradingSession = typeof options.isTradingSession === "function"
    ? options.isTradingSession
    : () => true;
  const logError = options.logError || ((scope, error) => console.error(scope, error));
  const nowIso = typeof options.nowIso === "function"
    ? options.nowIso
    : () => new Date().toISOString();

  function shouldRunToday(shParts) {
    if (calendarMode === "daily") return true;
    if (calendarMode === "workdays") return shParts.weekday >= 1 && shParts.weekday <= 5;
    if (calendarMode === "trading_days") return Boolean(isTradingSession(new Date()));
    return true;
  }

  async function runMainPushIfNeeded() {
    const config = getPushConfig();
    if (!config.enabled) return;
    const sh = getShanghaiParts();
    if (!shouldRunToday(sh)) return;

    const scheduleTimes = Array.from(new Set(
      (Array.isArray(config.times) ? config.times : [config.time])
        .map((item) => String(item || "").trim())
        .filter((item) => parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));
    if (!scheduleTimes.length) return;

    const sentTimes = runtimeStore.getPushRecord("main", sh.date);
    const nowMinutes = sh.hour * 60 + sh.minute;
    let updated = false;

    for (const timeText of scheduleTimes) {
      const targetMinutes = parsePushMinutes(timeText);
      if (targetMinutes === null) continue;
      if (nowMinutes < targetMinutes) continue;
      if (sentTimes.includes(timeText)) continue;
      const attemptAt = nowIso();
      runtimeStore.setPushAttempt("main", attemptAt);
      try {
        await pushByModulesToWeCom({ modules: config.modules });
        sentTimes.push(timeText);
        updated = true;
        runtimeStore.setPushRecord("main", sh.date, sentTimes);
        runtimeStore.setPushSuccess("main", attemptAt, sh.date);
        runtimeStore.save();
      } catch (error) {
        runtimeStore.setPushError("main", error?.message || error);
        runtimeStore.save();
        logError("[push] main schedule failed:", error?.message || error);
      }
    }

    if (updated) runtimeStore.save();
  }

  async function runEventAlertsIfNeeded() {
    const sh = getShanghaiParts();
    if (!shouldRunToday(sh)) return;
    try {
      await pushEventAlertsToWeCom({ force: false });
    } catch (error) {
      logError("[push] event alert failed:", error?.message || error);
    }
  }

  async function runTick() {
    if (typeof syncEventArbSummaryState === "function") {
      try {
        await syncEventArbSummaryState();
      } catch (error) {
        logError("[push] event-arbitrage summary sync failed:", error?.message || error);
      }
    }
    await runMainPushIfNeeded();
    await runEventAlertsIfNeeded();
  }

  return {
    runMainPushIfNeeded,
    runEventAlertsIfNeeded,
    runTick,
  };
}

module.exports = {
  createWeComScheduler,
};
