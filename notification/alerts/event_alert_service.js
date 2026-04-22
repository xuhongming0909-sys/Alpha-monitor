"use strict";

/**
 * 低溢价推送服务：
 * 1. 读取最新可转债结果
 * 2. 调用策略层生成买入/卖出/监控名单快照
 * 3. 负责发送与运行态记录
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

  function normalizeSessionWindows(items) {
    return Array.from(new Set(
      (Array.isArray(items) ? items : [])
        .map((item) => String(item || "").trim())
        .filter((item) => /^\d{2}:\d{2}\s*-\s*\d{2}:\d{2}$/.test(item))
        .map((item) => item.replace(/\s+/g, ""))
    ))
      .map((item) => {
        const [startText, endText] = item.split("-");
        const startMinutes = parsePushMinutes(startText);
        const endMinutes = parsePushMinutes(endText);
        if (startMinutes === null || endMinutes === null || startMinutes >= endMinutes) return null;
        return {
          text: `${startText}-${endText}`,
          startMinutes,
          endMinutes,
        };
      })
      .filter(Boolean);
  }

  function isTradingWeekday(parts) {
    return Number(parts?.weekday) >= 1 && Number(parts?.weekday) <= 5;
  }

  function isInsideSessionWindows(nowMinutes, windows) {
    return windows.some((item) => nowMinutes >= item.startMinutes && nowMinutes <= item.endMinutes);
  }

  /**
   * 可转债低溢价推送遵循 A 股交易日和交易时段。
   */
  function shouldRunDiscountPush(strategyConfig, force = false) {
    if (force) {
      return {
        allowed: true,
        reason: "forced",
        shanghaiParts: getShanghaiParts(new Date()),
        nowMinutes: null,
        sessionWindows: normalizeSessionWindows(strategyConfig?.sessionWindows),
      };
    }

    const shanghaiParts = getShanghaiParts(new Date());
    const sessionWindows = normalizeSessionWindows(strategyConfig?.sessionWindows);
    const nowMinutes = (Number(shanghaiParts?.hour) * 60) + Number(shanghaiParts?.minute);
    const tradingDaysOnly = strategyConfig?.tradingDaysOnly !== false;
    const latestSessionEnd = sessionWindows.reduce(
      (max, item) => Math.max(max, Number(item?.endMinutes) || 0),
      0
    );

    if (tradingDaysOnly && !isTradingWeekday(shanghaiParts)) {
      return { allowed: false, reason: "outside_trading_weekday", shanghaiParts, nowMinutes, sessionWindows };
    }
    if (latestSessionEnd > 0 && nowMinutes >= latestSessionEnd) {
      return { allowed: false, reason: "outside_discount_session", shanghaiParts, nowMinutes, sessionWindows };
    }
    if (sessionWindows.length && !isInsideSessionWindows(nowMinutes, sessionWindows)) {
      return { allowed: false, reason: "outside_discount_session", shanghaiParts, nowMinutes, sessionWindows };
    }
    if (!sessionWindows.length && !isTradingSession(new Date())) {
      return { allowed: false, reason: "outside_trading_session_fallback", shanghaiParts, nowMinutes, sessionWindows };
    }

    return { allowed: true, reason: "ok", shanghaiParts, nowMinutes, sessionWindows };
  }

  function collectDueMonitorSlots(scheduleTimes, sentTimes, nowMinutes, sessionWindows) {
    return scheduleTimes.filter((item) => {
      const targetMinutes = parsePushMinutes(item);
      if (targetMinutes === null) return false;
      if (Array.isArray(sentTimes) && sentTimes.includes(item)) return false;
      if (targetMinutes > nowMinutes) return false;
      if (sessionWindows.length && !isInsideSessionWindows(targetMinutes, sessionWindows)) return false;
      return true;
    });
  }

  function cloneStrategyState(state) {
    return {
      initializedDate: String(state?.initializedDate || "").trim() || null,
      lastBootstrapDate: String(state?.lastBootstrapDate || "").trim() || null,
      monitorMap: (state?.monitorMap && typeof state.monitorMap === "object") ? { ...state.monitorMap } : {},
      signalStateMap: (state?.signalStateMap && typeof state.signalStateMap === "object") ? { ...state.signalStateMap } : {},
    };
  }

  function commitSignalRows(currentState, nextState, signals) {
    const committed = cloneStrategyState(currentState);
    committed.initializedDate = String(nextState?.initializedDate || "").trim() || committed.initializedDate;
    committed.lastBootstrapDate = String(nextState?.lastBootstrapDate || "").trim() || committed.lastBootstrapDate;

    (Array.isArray(signals) ? signals : []).forEach((item) => {
      const code = String(item?.code || "").trim();
      if (!code) return;

      if (nextState?.signalStateMap && Object.prototype.hasOwnProperty.call(nextState.signalStateMap, code)) {
        committed.signalStateMap[code] = { ...nextState.signalStateMap[code] };
      } else {
        delete committed.signalStateMap[code];
      }

      if (nextState?.monitorMap && Object.prototype.hasOwnProperty.call(nextState.monitorMap, code)) {
        committed.monitorMap[code] = { ...nextState.monitorMap[code] };
      } else {
        delete committed.monitorMap[code];
      }
    });

    return committed;
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
    const strategyConfig = getDiscountStrategyConfig();
    const sessionDecision = shouldRunDiscountPush(strategyConfig, force);
    if (!sessionDecision.allowed) {
      return {
        sent: false,
        skipped: true,
        reason: sessionDecision.reason,
      };
    }

    const datasets = await collectAlertDatasets();
    const rows = Array.isArray(datasets?.cbArb?.data) ? datasets.cbArb.data : [];
    const currentStrategyState = cloneStrategyState(discountRuntimeStore.getState());
    const snapshot = buildDiscountSnapshot(rows, currentStrategyState, {
      buyThreshold: strategyConfig.buyThreshold,
      sellThreshold: strategyConfig.sellThreshold,
      nowIsoText: nowIso(),
      todayDate: sessionDecision.shanghaiParts?.date || getShanghaiParts().date,
    });

    if (snapshot.isBootstrap && !force && !snapshot.buySignals.length && !snapshot.sellSignals.length) {
      discountRuntimeStore.replaceStrategyState(snapshot.nextState);
      discountRuntimeStore.save();
      return {
        sent: false,
        skipped: true,
        reason: "bootstrap_seed_only",
        buyCount: snapshot.buySignals.length,
        sellCount: snapshot.sellSignals.length,
        monitorCount: snapshot.premiumMonitorSummary.count,
      };
    }

    const buyResult = await sendSignalBatch("buy", snapshot.buySignals);
    if (buyResult.sent) {
      discountRuntimeStore.replaceStrategyState(
        commitSignalRows(currentStrategyState, snapshot.nextState, snapshot.buySignals)
      );
      discountRuntimeStore.save();
    }

    const sellResult = await sendSignalBatch("sell", snapshot.sellSignals);
    if (sellResult.sent) {
      discountRuntimeStore.replaceStrategyState(
        commitSignalRows(discountRuntimeStore.getState(), snapshot.nextState, snapshot.sellSignals)
      );
      discountRuntimeStore.save();
    }

    discountRuntimeStore.replaceStrategyState(snapshot.nextState);
    discountRuntimeStore.save();

    const sh = sessionDecision.shanghaiParts || getShanghaiParts();
    const nowMinutes = Number.isFinite(sessionDecision.nowMinutes) ? sessionDecision.nowMinutes : ((sh.hour * 60) + sh.minute);
    const scheduleTimes = normalizeScheduleTimes(strategyConfig.monitorSessionTimes);
    const sentTimes = discountRuntimeStore.getMonitorPushRecord(sh.date);
    const dueSlots = collectDueMonitorSlots(scheduleTimes, sentTimes, nowMinutes, sessionDecision.sessionWindows || []);

    let monitorResult = { sent: false, sentCount: 0, skipped: true, reason: "not_due" };
    if (dueSlots.length) {
      monitorResult = await sendMonitorBatch(snapshot.premiumMonitorSummary.items, sh.date, dueSlots);
    }

    pushRuntimeStore.save();
    return {
      sent: Boolean(buyResult.sent || sellResult.sent || monitorResult.sent),
      buyResult,
      sellResult,
      monitorResult,
      monitorCount: snapshot.premiumMonitorSummary.count,
      isBootstrap: snapshot.isBootstrap,
    };
  }

  return {
    pushConvertibleBondAlerts,
  };
}

module.exports = {
  createEventAlertService,
};
