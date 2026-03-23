"use strict";

/**
 * 异动提醒服务。
 * 负责收集候选、执行冷却判断、拼装提醒并调用发送器，不直接操作页面或抓取层。
 */
function createEventAlertService(options = {}) {
  const collectAlertDatasets = options.collectAlertDatasets;
  const buildConvertibleBondAlertCandidates = options.buildConvertibleBondAlertCandidates;
  const buildConvertibleBondAlertMarkdown = options.buildConvertibleBondAlertMarkdown;
  const sendMarkdown = options.sendMarkdown;
  const getPushConfig = options.getPushConfig;
  const runtimeStore = options.runtimeStore;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();

  async function pushConvertibleBondAlerts(input = {}) {
    const config = getPushConfig();
    const eventAlert = config?.eventAlert || {};
    const cooldownMinutes = Math.max(1, Number(eventAlert.cooldownMinutes) || 30);
    const convertPremiumLt = Number(eventAlert?.convertibleBond?.convertPremiumLt);
    const force = Boolean(input.force);

    if (!force && eventAlert.enabled === false) {
      return {
        sent: false,
        skipped: true,
        reason: "event_alert_disabled",
        items: [],
      };
    }

    const datasets = await collectAlertDatasets();
    const rows = Array.isArray(datasets?.cbArb?.data) ? datasets.cbArb.data : [];
    const candidates = buildConvertibleBondAlertCandidates(rows, {
      convertPremiumLt,
      limit: 20,
    });
    const sendableItems = candidates.filter((item) => (
      force || runtimeStore.isEventAlertDue(item.alertKey, cooldownMinutes)
    ));

    if (!sendableItems.length) {
      return {
        sent: false,
        skipped: true,
        reason: "no_due_items",
        threshold: convertPremiumLt,
        cooldownMinutes,
        hitCount: candidates.length,
        items: [],
      };
    }

    const attemptAt = nowIso();
    runtimeStore.setPushAttempt("event_alert", attemptAt);

    try {
      const markdown = buildConvertibleBondAlertMarkdown(sendableItems, {
        generatedAtText: new Date().toLocaleString("zh-CN", { hour12: false }),
        convertPremiumLt,
      });
      const payload = await sendMarkdown(markdown);
      runtimeStore.setPushSuccess("event_alert", attemptAt);
      sendableItems.forEach((item) => runtimeStore.setEventAlertRecord(item.alertKey, {
        sentAt: attemptAt,
        code: item.code,
        ruleKey: item.ruleKey,
      }));
      runtimeStore.save();
      return {
        sent: true,
        sentAt: attemptAt,
        threshold: convertPremiumLt,
        cooldownMinutes,
        hitCount: candidates.length,
        sentCount: sendableItems.length,
        items: sendableItems,
        errcode: payload?.errcode,
        errmsg: payload?.errmsg,
      };
    } catch (error) {
      runtimeStore.setPushError("event_alert", error?.message || error);
      runtimeStore.save();
      throw error;
    }
  }

  return {
    pushConvertibleBondAlerts,
  };
}

module.exports = {
  createEventAlertService,
};
