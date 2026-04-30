"use strict";

/**
 * 自定义套利监控运行态服务。
 * 这一层负责读取/保存运行态监控列表、刷新最新价格、并调用策略层公式重算收益。
 */
function createCustomMonitorRuntimeService(options = {}) {
  const {
    stateRegistry,
    nowIso,
    fetchExchangeRates,
    getStockPrice,
    round,
    toFiniteNumber,
    normalizeMarket,
    normalizeCurrency,
    normalizeSafetyFactor,
    inferBMarketFromCode,
    hasMonitorTerms,
    recalculateMonitor,
  } = options;

  function normalizeMonitors(rawData) {
    return Array.isArray(rawData?.monitors) ? rawData.monitors : [];
  }

  function loadMonitors() {
    return normalizeMonitors(
      stateRegistry.read("arbitrage_monitors", "custom_monitors.json", { monitors: [] })
    );
  }

  function saveMonitors(monitors) {
    stateRegistry.write("arbitrage_monitors", "custom_monitors.json", { monitors });
  }

  async function getAllMonitors(runtimeOptions = {}) {
    const monitors = loadMonitors();
    const rateResult = await fetchExchangeRates();
    if (!rateResult?.success || !rateResult?.data) {
      throw new Error(rateResult?.error || "exchange_rate数据不可用，无法计算套利监控");
    }

    const rates = {
      hkToCny: Number(rateResult.data.hkToCny),
      usdToCny: Number(rateResult.data.usdToCny),
    };
    if (!Number.isFinite(rates.hkToCny) || !Number.isFinite(rates.usdToCny)) {
      throw new Error("exchange_rate数据异常，无法计算套利监控");
    }

    const source = runtimeOptions.refreshPrices
      ? await Promise.all(monitors.map(async (monitor) => {
        const next = { ...monitor };
        const acquirerMarket = normalizeMarket(monitor.acquirerMarket, "A");
        const targetMarket = normalizeMarket(monitor.targetMarket, "A");

        const acquirerRes = await getStockPrice(
          monitor.acquirerCode,
          acquirerMarket === "A" ? "a" : acquirerMarket === "H" ? "h" : "b",
          acquirerMarket === "B" ? inferBMarketFromCode(monitor.acquirerCode, "sh") : "sh"
        );
        const targetRes = await getStockPrice(
          monitor.targetCode,
          targetMarket === "A" ? "a" : targetMarket === "H" ? "h" : "b",
          targetMarket === "B" ? inferBMarketFromCode(monitor.targetCode, "sh") : "sh"
        );

        const acquirerPrice = toFiniteNumber(acquirerRes?.data?.price);
        const targetPrice = toFiniteNumber(targetRes?.data?.price);
        if (acquirerRes?.success && acquirerPrice !== null && acquirerPrice > 0) next.acquirerPriceOriginal = acquirerPrice;
        if (targetRes?.success && targetPrice !== null && targetPrice > 0) next.targetPriceOriginal = targetPrice;
        return next;
      }))
      : monitors;

    const recalculated = source.map((monitor) => recalculateMonitor(monitor, rates));
    saveMonitors(recalculated);
    return recalculated;
  }

  async function upsertMonitor(input) {
    if (!input || typeof input !== "object") throw new Error("请求体必须为对象");

    const acquirerCode = String(input.acquirerCode || "").trim();
    const targetCode = String(input.targetCode || "").trim();
    if (!acquirerCode || !targetCode) throw new Error("acquirerCode 和 targetCode 不能为空");
    if (!hasMonitorTerms(input)) throw new Error("换股比例、现金对价、现金选择权至少填写一项");

    const monitors = loadMonitors();
    const monitorId = input.id || `arb-${Date.now()}`;
    const now = nowIso();
    const draft = {
      id: monitorId,
      name: input.name || `${input.acquirerName || acquirerCode}-${input.targetName || targetCode}`,
      acquirerCode,
      acquirerName: input.acquirerName,
      acquirerMarket: normalizeMarket(input.acquirerMarket, "A"),
      targetCode,
      targetName: input.targetName,
      targetMarket: normalizeMarket(input.targetMarket, "A"),
      stockRatio: Number(input.stockRatio || 0),
      safetyFactor: normalizeSafetyFactor(input.safetyFactor, 1),
      cashDistribution: Number(input.cashDistribution || 0),
      cashDistributionCurrency: normalizeCurrency(input.cashDistributionCurrency, "CNY"),
      cashOptionPrice: Number(input.cashOptionPrice || 0),
      cashOptionCurrency: normalizeCurrency(input.cashOptionCurrency, "CNY"),
      note: input.note || "",
      acquirerPriceOriginal: toFiniteNumber(input.acquirerPriceOriginal ?? input.acquirerPrice),
      targetPriceOriginal: toFiniteNumber(input.targetPriceOriginal ?? input.targetPrice),
      acquirerCurrency: normalizeCurrency(input.acquirerCurrency, "CNY"),
      targetCurrency: normalizeCurrency(input.targetCurrency, "CNY"),
      createTime: input.createTime || now,
      updateTime: now,
    };

    const index = monitors.findIndex((item) => item.id === monitorId);
    if (index >= 0) {
      monitors[index] = {
        ...monitors[index],
        ...draft,
        createTime: monitors[index].createTime || draft.createTime,
        updateTime: now,
      };
    } else {
      monitors.push(draft);
    }

    saveMonitors(monitors);
    const all = await getAllMonitors({ refreshPrices: true });
    return all.find((item) => item.id === monitorId);
  }

  async function deleteMonitor(id) {
    const trimmedId = String(id || "").trim();
    if (!trimmedId) throw new Error("id 不能为空");
    const next = loadMonitors().filter((item) => item.id !== trimmedId);
    saveMonitors(next);
    return next;
  }

  return {
    round,
    loadMonitors,
    saveMonitors,
    getAllMonitors,
    upsertMonitor,
    deleteMonitor,
  };
}

module.exports = {
  createCustomMonitorRuntimeService,
};


