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
  const defaultMergerSchedule = options.defaultMergerSchedule || { enabled: false, time: "08:00" };
  const logError = options.logError || ((scope, error) => console.error(scope, error));

  async function runMainPushIfNeeded() {
    const config = getPushConfig();
    if (!config.enabled) return;
    const sh = getShanghaiParts();
    if (sh.weekday < 1 || sh.weekday > 5) return;

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
      try {
        await pushByModulesToWeCom({ modules: config.modules });
      } catch (error) {
        logError("[push] main schedule failed:", error?.message || error);
      }
      sentTimes.push(timeText);
      updated = true;
    }

    if (updated) {
      runtimeStore.setPushRecord("main", sh.date, sentTimes);
      runtimeStore.setLastMainPushDate(sh.date);
      runtimeStore.save();
    }
  }

  async function runMergerPushIfNeeded() {
    const config = getPushConfig();
    const mergerConfig = config.mergerSchedule || defaultMergerSchedule;
    if (!mergerConfig.enabled) return;

    const sh = getShanghaiParts();
    if (sh.weekday < 1 || sh.weekday > 5) return;
    const targetMinutes = parsePushMinutes(mergerConfig.time);
    if (targetMinutes === null) return;
    const nowMinutes = sh.hour * 60 + sh.minute;
    if (nowMinutes < targetMinutes) return;

    const sentTimes = runtimeStore.getPushRecord("merger", sh.date);
    if (sentTimes.includes(mergerConfig.time)) return;

    try {
      const result = await pushMergerReportToWeCom({ force: false });
      if (result?.sentCount > 0) {
        runtimeStore.setLastMergerReportDate(sh.date);
      }
    } catch (error) {
      logError("[push] merger schedule failed:", error?.message || error);
    } finally {
      sentTimes.push(mergerConfig.time);
      runtimeStore.setPushRecord("merger", sh.date, sentTimes);
      runtimeStore.save();
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


