"use strict";

/**
 * wecom定时调度器。
 * 负责读取推送配置、查询已发送记录，并在达到时间点时触发推送。
 */

function createWeComScheduler(options = {}) {
  const getPushConfig = options.getPushConfig;
  const runtimeStore = options.runtimeStore;
  const pushByModulesToWeCom = options.pushByModulesToWeCom;
  const pushMergerReportToWeCom = options.pushMergerReportToWeCom;
  const getShanghaiParts = options.getShanghaiParts;
  const parsePushMinutes = options.parsePushMinutes;
  const calendarMode = String(options.calendarMode || "daily").trim().toLowerCase();
  const isTradingSession = typeof options.isTradingSession === "function"
    ? options.isTradingSession
    : () => true;
  const defaultMergerSchedule = options.defaultMergerSchedule || { enabled: false, time: "08:00" };
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
        continue;
      }
    }

    if (updated) runtimeStore.save();
  }

  async function runMergerPushIfNeeded() {
    const config = getPushConfig();
    const mergerConfig = config.mergerSchedule || defaultMergerSchedule;
    if (!mergerConfig.enabled) return;

    const sh = getShanghaiParts();
    if (!shouldRunToday(sh)) return;
    const targetMinutes = parsePushMinutes(mergerConfig.time);
    if (targetMinutes === null) return;
    const nowMinutes = sh.hour * 60 + sh.minute;
    if (nowMinutes < targetMinutes) return;

    const sentTimes = runtimeStore.getPushRecord("merger", sh.date);
    if (sentTimes.includes(mergerConfig.time)) return;

    const attemptAt = nowIso();
    runtimeStore.setPushAttempt("merger", attemptAt);
    try {
      const result = await pushMergerReportToWeCom({ force: false });
      runtimeStore.setPushRecord("merger", sh.date, [...sentTimes, mergerConfig.time]);
      runtimeStore.setPushSuccess("merger", attemptAt, sh.date);
      runtimeStore.save();
      return result;
    } catch (error) {
      runtimeStore.setPushError("merger", error?.message || error);
      runtimeStore.save();
      logError("[push] merger schedule failed:", error?.message || error);
    }
  }

  return {
    runMainPushIfNeeded,
    runMergerPushIfNeeded,
  };
}

module.exports = {
  createWeComScheduler,
};


