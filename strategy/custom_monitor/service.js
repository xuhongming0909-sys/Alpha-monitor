"use strict";

const MONITOR_DECIMALS = 3;

function round(value, digits = MONITOR_DECIMALS) {
  if (!Number.isFinite(value)) return null;
  const scale = 10 ** digits;
  return Math.round(value * scale) / scale;
}

function toFiniteNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function normalizeMarket(value, fallback = "A") {
  const market = String(value || fallback).toUpperCase();
  return ["A", "H", "B"].includes(market) ? market : fallback;
}

function normalizeCurrency(value, fallback = "CNY") {
  const currency = String(value || fallback).toUpperCase();
  return ["CNY", "HKD", "USD"].includes(currency) ? currency : fallback;
}

function normalizeSafetyFactor(value, fallback = 1) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  if (parsed < 0) return fallback;
  return Math.min(1, parsed);
}

function inferBMarketFromCode(code, fallback = "sh") {
  const normalized = String(code || "").trim();
  if (normalized.startsWith("9")) return "sh";
  if (normalized.startsWith("2")) return "sz";
  return fallback;
}

function hasMonitorTerms(input) {
  return ["stockRatio", "cashDistribution", "cashOptionPrice"]
    .map((key) => Number(input?.[key] || 0))
    .some((value) => Number.isFinite(value) && value !== 0);
}

function toCny(amount, currency, rates) {
  if (!Number.isFinite(amount)) return null;
  const ccy = String(currency || "CNY").toUpperCase();
  if (ccy === "CNY") return amount;
  if (ccy === "HKD") return Number.isFinite(rates?.hkToCny) ? amount * rates.hkToCny : null;
  if (ccy === "USD") return Number.isFinite(rates?.usdToCny) ? amount * rates.usdToCny : null;
  return null;
}

function recalculateMonitor(monitor, rates, nowIso = () => new Date().toISOString()) {
  const targetOriginal = toFiniteNumber(monitor.targetPriceOriginal);
  const targetFallback = toFiniteNumber(monitor.targetPrice);
  const acquirerOriginal = toFiniteNumber(monitor.acquirerPriceOriginal);
  const acquirerFallback = toFiniteNumber(monitor.acquirerPrice);
  const targetPriceCny = toCny(targetOriginal ?? targetFallback, monitor.targetCurrency, rates);
  const acquirerPriceCny = toCny(acquirerOriginal ?? acquirerFallback, monitor.acquirerCurrency, rates);
  const stockRatio = Number(monitor.stockRatio || 0);
  const safetyFactor = normalizeSafetyFactor(monitor.safetyFactor, 1);
  const cashDistributionCny = toCny(Number(monitor.cashDistribution || 0), monitor.cashDistributionCurrency, rates);
  const cashOptionPriceCny = toCny(Number(monitor.cashOptionPrice || 0), monitor.cashOptionCurrency, rates);
  const hasStockLeg = stockRatio !== 0 || Number(monitor.cashDistribution || 0) !== 0;
  const hasCashLeg = Number(monitor.cashOptionPrice || 0) !== 0;
  const stockPayout = hasStockLeg && Number.isFinite(acquirerPriceCny) && Number.isFinite(cashDistributionCny)
    ? acquirerPriceCny * stockRatio * safetyFactor + cashDistributionCny
    : null;
  const stockSpread = Number.isFinite(stockPayout) && Number.isFinite(targetPriceCny)
    ? stockPayout - targetPriceCny
    : null;
  const stockYieldRate = Number.isFinite(stockPayout) && Number.isFinite(targetPriceCny) && targetPriceCny !== 0
    ? (stockSpread / targetPriceCny) * 100
    : null;
  const cashSpread = hasCashLeg && Number.isFinite(cashOptionPriceCny) && Number.isFinite(targetPriceCny)
    ? cashOptionPriceCny - targetPriceCny
    : null;
  const cashYieldRate = hasCashLeg && Number.isFinite(cashOptionPriceCny) && Number.isFinite(targetPriceCny) && targetPriceCny !== 0
    ? (cashSpread / targetPriceCny) * 100
    : null;

  return {
    ...monitor,
    acquirerPrice: round(acquirerPriceCny),
    targetPrice: round(targetPriceCny),
    cashDistributionCny: round(cashDistributionCny),
    cashPayout: hasCashLeg ? round(cashOptionPriceCny) : null,
    stockPayout: round(stockPayout),
    stockSpread: round(stockSpread),
    safetyFactor: round(safetyFactor),
    stockYieldRate: round(stockYieldRate),
    cashSpread: round(cashSpread),
    cashYieldRate: round(cashYieldRate),
    updateTime: nowIso(),
  };
}

function summarizeMonitor(monitor) {
  const stock = Number.isFinite(monitor.stockYieldRate) ? monitor.stockYieldRate : null;
  const cash = Number.isFinite(monitor.cashYieldRate) ? monitor.cashYieldRate : null;
  return {
    id: monitor.id,
    name: monitor.name,
    stockYieldRate: stock,
    cashYieldRate: cash,
    maxYieldRate: stock === null ? cash : cash === null ? stock : Math.max(stock, cash),
  };
}

module.exports = {
  round,
  toFiniteNumber,
  normalizeMarket,
  normalizeCurrency,
  normalizeSafetyFactor,
  inferBMarketFromCode,
  hasMonitorTerms,
  toCny,
  recalculateMonitor,
  summarizeMonitor,
  MONITOR_DECIMALS,
};

