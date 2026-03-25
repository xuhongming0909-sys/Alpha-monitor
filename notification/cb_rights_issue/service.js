"use strict";

/**
 * 可转债抢权配售定时推送服务。
 * 只负责独立模块自己的推送，不参与主摘要推送逻辑。
 */
function createCbRightsIssuePushService(options = {}) {
  const getConfig = typeof options.getConfig === "function" ? options.getConfig : () => ({ enabled: false, times: [] });
  const runtimeStore = options.runtimeStore;
  const getDataset = options.getDataset;
  const sendMarkdown = options.sendMarkdown;
  const buildMarkdown = options.buildMarkdown;
  const getShanghaiParts = options.getShanghaiParts;
  const parsePushMinutes = options.parsePushMinutes;
  const isTradingWeekday = typeof options.isTradingWeekday === "function" ? options.isTradingWeekday : () => true;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();
  const logInfo = options.logInfo || ((message) => console.info(message));
  const logError = options.logError || ((scope, error) => console.error(scope, error));

  async function readPayload() {
    const result = await getDataset("cbRightsIssue");
    if (!result || result.success === false) {
      throw new Error(result?.error || "cb_rights_issue_dataset_unavailable");
    }
    const payload = result?.data && typeof result.data === "object" ? result.data : {};
    return {
      monitorList: Array.isArray(payload.monitorList) ? payload.monitorList : [],
      sourceRows: Array.isArray(payload.sourceRows) ? payload.sourceRows : [],
      sourceSummary: payload.sourceSummary && typeof payload.sourceSummary === "object" ? payload.sourceSummary : {},
      rebuildStatus: payload.rebuildStatus && typeof payload.rebuildStatus === "object" ? payload.rebuildStatus : {},
      updateTime: result?.updateTime || payload?.updateTime || null,
      sourceUrl: result?.sourceUrl || payload?.sourceSummary?.sourceUrl || null,
    };
  }

  async function pushNow() {
    const payload = await readPayload();
    if (!payload.monitorList.length) {
      return { success: false, skipped: true, reason: "empty_monitor_list", total: 0 };
    }

    const attemptAt = nowIso();
    runtimeStore.setAttempt(attemptAt);
    runtimeStore.save();
    try {
      const markdown = buildMarkdown(payload, { maxItems: 10 });
      await sendMarkdown(markdown);
      runtimeStore.setSuccess(attemptAt);
      runtimeStore.save();
      return { success: true, skipped: false, total: payload.monitorList.length, attemptAt };
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
      logInfo(`[push][cb_rights_issue] sanitized dirty records date=${sh.date} kept=${sentTimes.join(",") || "none"}`);
    }

    for (const timeText of scheduleTimes) {
      const targetMinutes = parsePushMinutes(timeText);
      if (targetMinutes === null) continue;
      if (nowMinutes < targetMinutes) {
        logInfo(`[push][cb_rights_issue] slot=${timeText} date=${sh.date} skipped=not_due_yet`);
        continue;
      }
      if (sentTimes.includes(timeText)) {
        logInfo(`[push][cb_rights_issue] slot=${timeText} date=${sh.date} skipped=already_sent`);
        continue;
      }

      logInfo(`[push][cb_rights_issue] slot=${timeText} date=${sh.date} action=attempt`);
      try {
        const result = await pushNow();
        if (result?.skipped) {
          logInfo(`[push][cb_rights_issue] slot=${timeText} date=${sh.date} skipped=${result.reason || "empty"}`);
          continue;
        }
        sentTimes.push(timeText);
        runtimeStore.setPushRecord(sh.date, sentTimes);
        runtimeStore.save();
        logInfo(`[push][cb_rights_issue] slot=${timeText} date=${sh.date} action=success`);
      } catch (error) {
        logInfo(`[push][cb_rights_issue] slot=${timeText} date=${sh.date} action=failed error=${error?.message || error}`);
        logError("[push][cb_rights_issue] schedule failed:", error?.message || error);
      }
    }
  }

  return {
    readPayload,
    pushNow,
    runIfNeeded,
  };
}

module.exports = {
  createCbRightsIssuePushService,
};
