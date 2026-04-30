// AI-SUMMARY: 推送调度器：定时 tick 触发各模块推送
// 对应 INDEX.md §9 文件摘要索引

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
  const logInfo = options.logInfo || ((message) => console.info(message));
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

    const sanitized = runtimeStore.sanitizeScheduledPushRecord("main", sh.date, scheduleTimes);
    const sentTimes = sanitized.times.slice();
    const nowMinutes = sh.hour * 60 + sh.minute;
    let updated = false;

    if (sanitized.changed) {
      runtimeStore.save();
      logInfo(`[push][main] sanitized dirty scheduled records date=${sh.date} kept=${sentTimes.join(",") || "none"}`);
    }

    logInfo(
      `[push][main] evaluating date=${sh.date} now=${String(sh.hour).padStart(2, "0")}:${String(sh.minute).padStart(2, "0")} schedule=${scheduleTimes.join(",") || "none"} sent=${sentTimes.join(",") || "none"}`
    );

    for (const timeText of scheduleTimes) {
      const targetMinutes = parsePushMinutes(timeText);
      if (targetMinutes === null) continue;
      if (nowMinutes < targetMinutes) {
        logInfo(`[push][main] slot=${timeText} date=${sh.date} skipped=not_due_yet`);
        continue;
      }
      if (sentTimes.includes(timeText)) {
        logInfo(`[push][main] slot=${timeText} date=${sh.date} skipped=already_sent`);
        continue;
      }
      const attemptAt = nowIso();
      runtimeStore.setPushAttempt("main", attemptAt);
      logInfo(`[push][main] slot=${timeText} date=${sh.date} action=attempt at=${attemptAt}`);
      try {
        await pushByModulesToWeCom({ modules: config.modules });
        sentTimes.push(timeText);
        updated = true;
        runtimeStore.setPushRecord("main", sh.date, sentTimes);
        runtimeStore.setPushSuccess("main", attemptAt, sh.date);
        runtimeStore.save();
        logInfo(`[push][main] slot=${timeText} date=${sh.date} action=success at=${attemptAt}`);
      } catch (error) {
        runtimeStore.setPushError("main", error?.message || error);
        runtimeStore.save();
        logInfo(`[push][main] slot=${timeText} date=${sh.date} action=failed at=${attemptAt} error=${error?.message || error}`);
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
