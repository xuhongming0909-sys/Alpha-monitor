"use strict";

/**
 * 折价策略推送服务：
 * 1. 读取最新可转债结果
 * 2. 调用策略层生成买入/卖出/监控名单快照
 * 3. 负责发送与运行态记录
 * 不在这里做页面展示逻辑。
 */
function createEventAlertService(options = {}) {
  const collectAlertDatasets = options.collectAlertDatasets;
  const buildDiscountSnapshot = options.buildDiscountSnapshot;
  const buildDiscountMarkdown = options.buildDiscountMarkdown;
  const sendMarkdown = options.sendMarkdown;
  const getDiscountStrategyConfig = options.getDiscountStrategyConfig;
  const pushRuntimeStore = options.pushRuntimeStore;
  const discountRuntimeStore = options.discountRuntimeStore;
  const parsePushMinutes = options.parsePushMinutes || ((value) => {
    const [hour, minute] = String(value || "").split(":").map((item) => Number(item));
    if (!Number.isFinite(hour) || !Number.isFinite(minute)) return null;
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
    return (hour * 60) + minute;
  });
  const getShanghaiParts = typeof options.getShanghaiParts === "function"
    ? options.getShanghaiParts
    : () => ({ date: new Date().toISOString().slice(0, 10), hour: 0, minute: 0 });
  const isTradingSession = typeof options.isTradingSession === "function"
    ? options.isTradingSession
    : () => true;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();

  function normalizeScheduleTimes(items) {
    return Array.from(new Set(
      (Array.isArray(items) ? items : [])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}$/.test(item) && parsePushMinutes(item) !== null)
    )).sort((a, b) => (parsePushMinutes(a) ?? 0) - (parsePushMinutes(b) ?? 0));
  }

  async function sendSignalBatch(signalType, items) {
    if (!Array.isArray(items) || !items.length) {
      return { sent: false, sentCount: 0, skipped: true, reason: "no_items" };
    }

    const attemptAt = nowIso();
    if (signalType === "buy") discountRuntimeStore.setBuySignalAttempt(attemptAt);
    if (signalType === "sell") discountRuntimeStore.setSellSignalAttempt(attemptAt);

    try {
      const markdown = buildDiscountMarkdown(signalType, items, {
        generatedAtText: new Date().toLocaleString("zh-CN", { hour12: false }),
      });
      const payload = await sendMarkdown(markdown);
      if (signalType === "buy") discountRuntimeStore.setBuySignalSuccess(attemptAt);
      if (signalType === "sell") discountRuntimeStore.setSellSignalSuccess(attemptAt);
      discountRuntimeStore.save();
      return {
        sent: true,
        sentAt: attemptAt,
        sentCount: items.length,
        errcode: payload?.errcode,
        errmsg: payload?.errmsg,
      };
    } catch (error) {
      if (signalType === "buy") discountRuntimeStore.setBuySignalError(attemptAt, error?.message || error);
      if (signalType === "sell") discountRuntimeStore.setSellSignalError(attemptAt, error?.message || error);
      discountRuntimeStore.save();
      throw error;
    }
  }

  async function sendMonitorBatch(items, dateText, dueSlots) {
    if (!Array.isArray(items) || !items.length) {
      return { sent: false, sentCount: 0, skipped: true, reason: "empty_monitor_list" };
    }

    const attemptAt = nowIso();
    discountRuntimeStore.setMonitorPushAttempt(attemptAt);
    try {
      const markdown = buildDiscountMarkdown("monitor", items, {
        generatedAtText: new Date().toLocaleString("zh-CN", { hour12: false }),
      });
      const payload = await sendMarkdown(markdown);
      discountRuntimeStore.setMonitorPushSuccess(attemptAt);
      const sentTimes = discountRuntimeStore.getMonitorPushRecord(dateText);
      discountRuntimeStore.setMonitorPushRecord(dateText, [...sentTimes, ...(Array.isArray(dueSlots) ? dueSlots : [])]);
      discountRuntimeStore.save();
      return {
        sent: true,
        sentAt: attemptAt,
        sentCount: items.length,
        errcode: payload?.errcode,
        errmsg: payload?.errmsg,
      };
    } catch (error) {
      discountRuntimeStore.setMonitorPushError(attemptAt, error?.message || error);
      discountRuntimeStore.save();
      throw error;
    }
  }

  async function pushConvertibleBondAlerts(input = {}) {
    const force = Boolean(input.force);
    if (!force && !isTradingSession(new Date())) {
      return {
        sent: false,
        skipped: true,
        reason: "outside_trading_session",
      };
    }

    const strategyConfig = getDiscountStrategyConfig();
    const datasets = await collectAlertDatasets();
    const rows = Array.isArray(datasets?.cbArb?.data) ? datasets.cbArb.data : [];
    const snapshot = buildDiscountSnapshot(rows, discountRuntimeStore.getState(), {
      buyThreshold: strategyConfig.buyThreshold,
      sellThreshold: strategyConfig.sellThreshold,
      atrAnchors: strategyConfig.atrAnchors,
      sellPressureAnchors: strategyConfig.sellPressureAnchors,
      boardCoefficients: strategyConfig.boardCoefficients,
      nowIsoText: nowIso(),
      todayDate: getShanghaiParts().date,
    });

    discountRuntimeStore.replaceStrategyState(snapshot.nextState);
    discountRuntimeStore.save();

    if (snapshot.isBootstrap && !force) {
      return {
        sent: false,
        skipped: true,
        reason: "bootstrap_seed_only",
        buyCount: snapshot.buySignals.length,
        sellCount: snapshot.sellSignals.length,
        monitorCount: snapshot.discountMonitorSummary.count,
      };
    }

    const buyResult = await sendSignalBatch("buy", snapshot.buySignals);
    const sellResult = await sendSignalBatch("sell", snapshot.sellSignals);

    const sh = getShanghaiParts();
    const nowMinutes = (sh.hour * 60) + sh.minute;
    const scheduleTimes = normalizeScheduleTimes(strategyConfig.monitorSessionTimes);
    const sentTimes = discountRuntimeStore.getMonitorPushRecord(sh.date);
    const dueSlots = scheduleTimes.filter((item) => {
      const targetMinutes = parsePushMinutes(item);
      if (targetMinutes === null) return false;
      return targetMinutes <= nowMinutes && !sentTimes.includes(item);
    });

    let monitorResult = { sent: false, sentCount: 0, skipped: true, reason: "not_due" };
    if (dueSlots.length) {
      monitorResult = await sendMonitorBatch(snapshot.discountMonitorSummary.items, sh.date, dueSlots);
    }

    pushRuntimeStore.save();
    return {
      sent: Boolean(buyResult.sent || sellResult.sent || monitorResult.sent),
      buyResult,
      sellResult,
      monitorResult,
      monitorCount: snapshot.discountMonitorSummary.count,
    };
  }

  return {
    pushConvertibleBondAlerts,
  };
}

module.exports = {
  createEventAlertService,
};
