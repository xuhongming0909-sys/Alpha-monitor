"use strict";
// LOF IOPV 推送服务（替代旧 lof_arbitrage push）

function createLofIopvPushService(options = {}) {
  const getConfig = typeof options.getConfig === "function" ? options.getConfig : () => ({ enabled: false, times: [] });
  const runtimeStore = options.runtimeStore;
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

  async function readPayload() {
    const result = await getDataset("lofArb");
    if (!result || !result.data) return { rows: [] };
    return result.data;
  }

  async function pushNow() {
    const payload = await readPayload();
    const rows = payload.rows || [];
    if (!rows.length) return { skipped: true, reason: "no_data" };
    const md = buildMarkdown(payload);
    await sendMarkdown(md);
    return { skipped: false };
  }

  async function runIfNeeded() {
    if (!isDeliveryAvailable()) return;
    const config = getConfig();
    if (!config.enabled) return;
    if (!isTradingWeekday()) return;

    const sh = getShanghaiParts();
    const times = Array.isArray(config.times) ? config.times : [];
    const sentTimes = runtimeStore?.getPushRecord?.(sh.date) || [];

    for (const timeText of times) {
      const targetMinutes = parsePushMinutes(timeText);
      if (targetMinutes === null) continue;
      const nowMinutes = sh.hour * 60 + sh.minute;
      if (nowMinutes < targetMinutes) {
        logInfo(`[push][lof_iopv] slot=${timeText} date=${sh.date} skipped=not_due_yet`);
        continue;
      }
      if (sentTimes.includes(timeText)) {
        logInfo(`[push][lof_iopv] slot=${timeText} date=${sh.date} skipped=already_sent`);
        continue;
      }
      logInfo(`[push][lof_iopv] slot=${timeText} date=${sh.date} action=attempt`);
      try {
        const result = await pushNow();
        if (result?.skipped) {
          logInfo(`[push][lof_iopv] slot=${timeText} date=${sh.date} skipped=${result.reason || "empty"}`);
          continue;
        }
        sentTimes.push(timeText);
        runtimeStore.setPushRecord(sh.date, sentTimes);
        runtimeStore.save();
        logInfo(`[push][lof_iopv] slot=${timeText} date=${sh.date} action=success`);
      } catch (error) {
        logInfo(`[push][lof_iopv] slot=${timeText} date=${sh.date} action=failed error=${error?.message || error}`);
        logError("[push][lof_iopv] schedule failed:", error?.message || error);
      }
    }
  }

  return { readPayload, pushNow, runIfNeeded };
}

module.exports = { createLofIopvPushService };