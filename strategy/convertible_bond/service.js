"use strict";

const { getShanghaiParts, normalizeDateText } = require("../../shared/time/shanghai_time");

function topN(rows, count, compareFn) {
  return [...rows].sort(compareFn).slice(0, count);
}

function toNum(value) {
  return Number.isFinite(Number(value)) ? Number(value) : null;
}

function pctText(value, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "--";
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(digits)}%`;
}

function pickText(value, fallback = "--") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function isFiniteNum(value) {
  return Number.isFinite(Number(value));
}

function cbArbRowScore(row) {
  if (!row || typeof row !== "object") return 0;
  const metrics = [
    row.code,
    row.bondName,
    row.stockCode,
    row.stockName,
    row.price,
    row.stockPrice,
    row.convertPrice,
    row.convertValue,
    row.remainingYears,
  ];
  return metrics.reduce((sum, value) => (
    sum + ((value !== null && value !== undefined && String(value).trim() !== "") ? 1 : 0)
  ), 0);
}

function isValidCbArbRow(row) {
  if (!row || typeof row !== "object") return false;
  const code = String(row.code || "").trim();
  const bondName = String(row.bondName || "").trim();
  const stockCode = String(row.stockCode || "").trim();
  const stockName = String(row.stockName || "").trim();
  return Boolean(
    code &&
    bondName &&
    stockCode &&
    stockName &&
    isFiniteNum(row.price) &&
    isFiniteNum(row.stockPrice) &&
    isFiniteNum(row.convertPrice) &&
    isFiniteNum(row.convertValue)
  );
}

function todayShanghaiDate() {
  return getShanghaiParts().date;
}

function normalizeComparableDate(value) {
  const text = normalizeDateText(value);
  return /^\d{4}-\d{2}-\d{2}$/.test(text) ? text : "";
}

function normalizeBoardType(stockCode) {
  const code = String(stockCode || "").trim();
  if (code.startsWith("688")) return "科创板";
  if (code.startsWith("300") || code.startsWith("301")) return "创业板";
  return "主板";
}

function hasPassedConvertStart(row) {
  const text = String(row?.convertStartDate || row?.convertStartDateTime || "").trim();
  if (!text) return false;
  const timestamp = Date.parse(text);
  return Number.isFinite(timestamp) ? timestamp <= Date.now() : false;
}

function compareNumAsc(left, right) {
  const aValue = toNum(left);
  const bValue = toNum(right);
  if (aValue === null && bValue === null) return 0;
  if (aValue === null) return 1;
  if (bValue === null) return -1;
  return aValue - bValue;
}

function compareNumDesc(left, right) {
  return compareNumAsc(right, left);
}

function comparePremiumMonitorRows(a, b) {
  const premiumDiff = compareNumAsc(a?.premiumRate, b?.premiumRate);
  if (premiumDiff !== 0) return premiumDiff;

  const discountAtrDiff = compareNumDesc(a?.discountAtrRatio, b?.discountAtrRatio);
  if (discountAtrDiff !== 0) return discountAtrDiff;

  const marketValueRatioDiff = compareNumAsc(a?.bondToStockMarketValueRatio, b?.bondToStockMarketValueRatio);
  if (marketValueRatioDiff !== 0) return marketValueRatioDiff;

  return String(a?.code || "").localeCompare(String(b?.code || ""), "zh-CN");
}

function buildDiscountStrategyOptions(options = {}) {
  return {
    buyThreshold: toNum(options.buyThreshold) ?? -2,
    sellThreshold: toNum(options.sellThreshold) ?? -0.5,
    nowIsoText: String(options.nowIsoText || new Date().toISOString()),
    todayDate: String(options.todayDate || todayShanghaiDate()),
  };
}

function normalizeDiscountStrategyState(input = {}) {
  return {
    initializedDate: String(input?.initializedDate || "").trim() || null,
    lastBootstrapDate: String(input?.lastBootstrapDate || "").trim() || null,
    monitorMap: (input?.monitorMap && typeof input.monitorMap === "object") ? { ...input.monitorMap } : {},
    signalStateMap: (input?.signalStateMap && typeof input.signalStateMap === "object") ? { ...input.signalStateMap } : {},
  };
}

function isTerminalZeroTurnoverRow(row, today = todayShanghaiDate()) {
  if (!row || typeof row !== "object") return false;
  const turnover = toNum(row.turnoverAmountYi);
  const hasZeroTurnover = turnover !== null && turnover <= 0;

  const ceaseDate = normalizeComparableDate(row.ceaseDate);
  const delistDate = normalizeComparableDate(row.delistDate);
  if (hasZeroTurnover && ((ceaseDate && ceaseDate <= today) || (delistDate && delistDate <= today))) {
    return true;
  }

  const remainingYears = Number(row.remainingYears);
  const maturityDate = normalizeComparableDate(row.maturityDate);
  if (hasZeroTurnover && maturityDate && Number.isFinite(remainingYears) && remainingYears <= 0.02) {
    return true;
  }

  const forceRedeemStatus = String(row.forceRedeemStatus || "").trim();
  return /(完成强赎|强赎完成|完成赎回|赎回完成|摘牌|终止|退市|停止交易)/.test(forceRedeemStatus);
}

function isCbArbRowDelistedOrExpired(row, today = todayShanghaiDate()) {
  if (!row || typeof row !== "object") return true;
  if (row.isDelistedOrExpired === true) return true;

  const price = Number(row.price);
  if (Number.isFinite(price) && price <= 0) return true;
  if (isTerminalZeroTurnoverRow(row)) return true;

  for (const key of ["delistDate", "ceaseDate"]) {
    const dateText = normalizeComparableDate(row[key]);
    if (dateText && dateText <= today) return true;
  }

  const maturityDate = normalizeComparableDate(row.maturityDate);
  return Boolean(maturityDate && maturityDate < today);
}

function isCbArbRowActiveForceRedeem(row) {
  if (!row || typeof row !== "object") return false;
  const status = String(row.forceRedeemStatus || "").trim();
  if (!status) return false;
  if (/(不强赎|暂不强赎|不提前赎回|不赎回)/.test(status)) return false;
  if (/(完成强赎|强赎完成|完成赎回|赎回完成|摘牌|终止|退市|停止交易)/.test(status)) return false;
  return /(已公告强赎|强赎进行中|实施赎回|公告赎回)/.test(status);
}

function sanitizeCbArbRows(rows) {
  const today = todayShanghaiDate();
  const map = new Map();
  for (const row of Array.isArray(rows) ? rows : []) {
    if (isCbArbRowDelistedOrExpired(row, today)) continue;
    if (!isValidCbArbRow(row)) continue;
    const key = String(row.code || "").trim();
    const existing = map.get(key);
    if (!existing || cbArbRowScore(row) > cbArbRowScore(existing)) {
      map.set(key, row);
    }
  }
  return Array.from(map.values());
}

/**
 * 低溢价策略只做真实字段派生，不做推送和持久化。
 */
function enrichDiscountStrategyRow(row, options = {}) {
  const config = buildDiscountStrategyOptions(options);
  const {
    discountRate: _legacyDiscountRate,
    lowPremiumMagnitude: _legacyLowPremiumMagnitude,
    atrRatio: _legacyAtrRatio,
    atrCoefficient: _legacyAtrCoefficient,
    sellPressureRatio: _legacySellPressureRatio,
    sellPressureCoefficient: _legacySellPressureCoefficient,
    boardCoefficient: _legacyBoardCoefficient,
    weightedDiscountRate: _legacyWeightedDiscountRate,
    ...baseRow
  } = row || {};
  const premiumRate = toNum(baseRow?.premiumRate);
  const stockPrice = toNum(baseRow?.stockPrice);
  const stockAtr20 = toNum(baseRow?.stockAtr20);
  const remainingSizeYi = toNum(baseRow?.remainingSizeYi);
  const stockMarketValueYi = toNum(baseRow?.stockMarketValueYi);
  const premiumMagnitude = premiumRate === null ? null : Math.abs(premiumRate);
  const stockAtr20Pct = (stockPrice !== null && stockPrice > 0 && stockAtr20 !== null)
    ? (stockAtr20 / stockPrice) * 100
    : null;
  const discountAtrRatio = (premiumMagnitude !== null && stockAtr20Pct !== null && stockAtr20Pct > 0)
    ? premiumMagnitude / stockAtr20Pct
    : null;
  const bondToStockMarketValueRatio = (
    remainingSizeYi !== null &&
    stockMarketValueYi !== null &&
    stockMarketValueYi > 0
  )
    ? remainingSizeYi / stockMarketValueYi
    : null;
  const forceRedeemActive = isCbArbRowActiveForceRedeem(baseRow);
  const buyZoneActive = Boolean(
    premiumRate !== null &&
    premiumRate < config.buyThreshold &&
    hasPassedConvertStart(row)
  );
  const sellZoneActive = Boolean(premiumRate !== null && premiumRate > config.sellThreshold);

  return {
    ...baseRow,
    stockAtr20Pct,
    discountAtrRatio,
    bondToStockMarketValueRatio,
    boardType: normalizeBoardType(baseRow?.stockCode),
    forceRedeemActive,
    forceRedeemLabel: forceRedeemActive ? "强赎中" : "非强赎",
    buyZoneActive,
    sellZoneActive,
  };
}

function buildDiscountMonitorSummaryItems(rows) {
  return [...rows]
    .sort(comparePremiumMonitorRows)
    .map((row) => ({
      code: pickText(row.code),
      bondName: pickText(row.bondName),
      premiumRate: row.premiumRate,
      bondToStockMarketValueRatio: row.bondToStockMarketValueRatio,
      discountAtrRatio: row.discountAtrRatio,
      forceRedeemActive: row.forceRedeemActive === true,
      forceRedeemLabel: pickText(row.forceRedeemLabel, "非强赎"),
    }));
}

function buildDiscountSignal(row, signalType) {
  return {
    signalType,
    code: pickText(row.code),
    bondName: pickText(row.bondName),
    stockCode: pickText(row.stockCode),
    stockName: pickText(row.stockName),
    price: row.price,
    stockPrice: row.stockPrice,
    stockChangePercent: row.stockChangePercent,
    convertValue: row.convertValue,
    premiumRate: row.premiumRate,
    bondToStockMarketValueRatio: row.bondToStockMarketValueRatio,
    discountAtrRatio: row.discountAtrRatio,
    forceRedeemActive: row.forceRedeemActive === true,
    forceRedeemLabel: pickText(row.forceRedeemLabel, "非强赎"),
    reason: signalType === "buy"
      ? "转股溢价率进入低溢价买入区"
      : "转股溢价率回到卖出区",
  };
}

/**
 * 统一生成低溢价策略快照。
 * 首次启动时如果已经处于买入区，也直接发一次信号，避免因运行态丢失吞掉真实穿越。
 */
function buildConvertibleBondDiscountSnapshot(rows, runtimeState = {}, options = {}) {
  const config = buildDiscountStrategyOptions(options);
  const cleanRows = sanitizeCbArbRows(rows).map((row) => enrichDiscountStrategyRow(row, config));
  const pushEligibleRows = cleanRows.filter((row) => !row.forceRedeemActive);
  const previousState = normalizeDiscountStrategyState(runtimeState);
  const previousMonitorMap = { ...previousState.monitorMap };
  const previousSignalStateMap = { ...previousState.signalStateMap };
  const rowMap = new Map(pushEligibleRows.map((row) => [pickText(row.code), row]));
  const nextMonitorMap = { ...previousMonitorMap };
  const nextSignalStateMap = {};
  const buySignals = [];
  const sellSignals = [];
  const isBootstrap = !previousState.initializedDate;

  pushEligibleRows.forEach((row) => {
    const code = pickText(row.code);
    if (!code) return;

    const previousSignalState = previousSignalStateMap[code] || {};
    const buyZoneActive = Boolean(row.buyZoneActive);
    const sellZoneActive = Boolean(row.sellZoneActive);

    nextSignalStateMap[code] = { buyZoneActive, sellZoneActive };

    if (buyZoneActive) {
      nextMonitorMap[code] = {
        code,
        enteredAt: previousMonitorMap[code]?.enteredAt || config.nowIsoText,
      };
    }

    if (isBootstrap) {
      if (buyZoneActive) buySignals.push(buildDiscountSignal(row, "buy"));
      return;
    }

    if (!previousSignalState.buyZoneActive && buyZoneActive) {
      buySignals.push(buildDiscountSignal(row, "buy"));
    }

    if (nextMonitorMap[code] && !previousSignalState.sellZoneActive && sellZoneActive) {
      sellSignals.push(buildDiscountSignal(row, "sell"));
      delete nextMonitorMap[code];
    }
  });

  Object.keys(nextMonitorMap).forEach((code) => {
    if (!rowMap.has(code)) delete nextMonitorMap[code];
  });

  const activeCodes = new Set(Object.keys(nextMonitorMap));
  const enrichedRows = cleanRows.map((row) => ({
    ...row,
    isDiscountMonitorActive: activeCodes.has(pickText(row.code)),
  }));
  const monitorRows = pushEligibleRows.filter((row) => activeCodes.has(pickText(row.code)));
  const monitorItems = buildDiscountMonitorSummaryItems(monitorRows);

  return {
    rows: enrichedRows,
    buySignals,
    sellSignals,
    isBootstrap,
    premiumMonitorSummary: {
      count: monitorItems.length,
      items: monitorItems,
    },
    nextState: {
      initializedDate: previousState.initializedDate || config.todayDate,
      lastBootstrapDate: isBootstrap ? config.todayDate : previousState.lastBootstrapDate,
      monitorMap: nextMonitorMap,
      signalStateMap: nextSignalStateMap,
    },
  };
}

/**
 * 转债顶部摘要与定时主推送共用同一套候选规则，避免页面前三与推送口径再次分叉。
 */
function isCbArbSummaryEligibleRow(row, today = todayShanghaiDate()) {
  if (!row || typeof row !== "object") return false;
  if (!isValidCbArbRow(row)) return false;
  if (isCbArbRowDelistedOrExpired(row, today)) return false;
  if (isCbArbRowActiveForceRedeem(row)) return false;
  return true;
}

function selectCbArbSummaryRows(rows, today = todayShanghaiDate()) {
  return sanitizeCbArbRows(rows).filter((row) => isCbArbSummaryEligibleRow(row, today));
}

function cbArbOpportunitySets(rows) {
  const cleanRows = selectCbArbSummaryRows(rows);
  const formatDate = (value) => String(value || "").trim();
  const hasStartedConvert = (row) => {
    const text = formatDate(row.convertStartDate || row.convertStartDateTime);
    if (!text) return false;
    const t = Date.parse(text);
    return Number.isFinite(t) ? t <= Date.now() : false;
  };
  const putbackValue = (row) => {
    const putbackPrice = toNum(row.putbackPrice);
    const putbackTrigger = toNum(row.putbackTriggerPrice);
    if (putbackPrice !== null && putbackPrice > 0) return putbackPrice;
    if (putbackTrigger !== null && putbackTrigger > 0) return putbackTrigger;
    return null;
  };
  const convertSpreadRate = (row) => {
    const convertValue = toNum(row.convertValue);
    const price = toNum(row.price);
    if (convertValue === null || price === null || price === 0) return null;
    return ((convertValue - price) / price) * 100;
  };

  return {
    doubleLow: topN(
      cleanRows.filter((row) => toNum(row.doubleLow) !== null),
      3,
      (a, b) => (toNum(a.doubleLow) ?? Number.POSITIVE_INFINITY) - (toNum(b.doubleLow) ?? Number.POSITIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `双低最低：${(toNum(row.doubleLow) ?? 0).toFixed(2)}`,
    })),
    theoPremium: topN(
      cleanRows.filter((row) => toNum(row.theoreticalPremiumRate) !== null),
      3,
      (a, b) => (toNum(b.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY) - (toNum(a.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `理论溢价率最高：${pctText(row.theoreticalPremiumRate)}`,
    })),
    redeem: topN(
      cleanRows.filter((row) => {
        const price = toNum(row.price);
        const stockPrice = toNum(row.stockPrice);
        const redeemValue = putbackValue(row);
        const years = toNum(row.remainingYears);
        return price !== null && stockPrice !== null && redeemValue !== null && years !== null
          && price < redeemValue && stockPrice < redeemValue && years <= 2;
      }),
      3,
      (a, b) => ((putbackValue(b) ?? 0) - (toNum(b.price) ?? 0)) - ((putbackValue(a) ?? 0) - (toNum(a.price) ?? 0))
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `回售执行价高于现价，差额 ${((putbackValue(row) ?? 0) - (toNum(row.price) ?? 0)).toFixed(2)}`,
    })),
    limitUp: topN(
      cleanRows.filter((row) => (toNum(row.stockChangePercent) ?? -999) >= 9.5),
      3,
      (a, b) => (toNum(b.stockChangePercent) ?? Number.NEGATIVE_INFINITY) - (toNum(a.stockChangePercent) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `正股接近/触及涨停，${pctText(row.stockChangePercent)}`,
    })),
    convert: topN(
      cleanRows.filter((row) => {
        const spread = convertSpreadRate(row);
        return spread !== null && spread > 2 && hasStartedConvert(row);
      }),
      3,
      (a, b) => (convertSpreadRate(b) ?? Number.NEGATIVE_INFINITY) - (convertSpreadRate(a) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `转股套利空间 ${pctText(convertSpreadRate(row))}`,
    })),
    delist: topN(
      cleanRows.filter((row) => (toNum(row.price) ?? 9999) < 100),
      3,
      (a, b) => (toNum(a.price) ?? Number.POSITIVE_INFINITY) - (toNum(b.price) ?? Number.POSITIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `低于面值博弈，现价 ${(toNum(row.price) ?? 0).toFixed(2)}`,
    })),
  };
}

/**
 * 构建可转债异动提醒候选。
 */
function buildConvertibleBondAlertCandidates(rows, options = {}) {
  const cleanRows = sanitizeCbArbRows(rows);
  const threshold = Number(options.convertPremiumLt);
  const limit = Number.isFinite(Number(options.limit)) ? Number(options.limit) : 20;
  const effectiveThreshold = Number.isFinite(threshold) ? threshold : -3;

  return cleanRows
    .filter((row) => Number.isFinite(Number(row.premiumRate)) && Number(row.premiumRate) < effectiveThreshold)
    .sort((a, b) => {
      const premiumDiff = (Number(a.premiumRate) || 0) - (Number(b.premiumRate) || 0);
      if (premiumDiff !== 0) return premiumDiff;
      return (Number(b.convertValue) || 0) - (Number(a.convertValue) || 0);
    })
    .slice(0, Math.max(1, limit))
    .map((row) => ({
      ruleKey: "convert_premium_lt",
      alertKey: `cb:${pickText(row.code)}:convert_premium_lt`,
      code: pickText(row.code),
      bondName: pickText(row.bondName),
      price: row.price,
      changePercent: row.changePercent,
      stockCode: pickText(row.stockCode),
      stockName: pickText(row.stockName),
      stockPrice: row.stockPrice,
      stockChangePercent: row.stockChangePercent,
      convertValue: row.convertValue,
      premiumRate: row.premiumRate,
      doubleLow: row.doubleLow,
      theoreticalPremiumRate: row.theoreticalPremiumRate,
      forceRedeemStatus: pickText(row.forceRedeemStatus, ""),
      putbackStatus: pickText(row.putbackStatus, ""),
      reason: `转股溢价率低于 ${pctText(effectiveThreshold)}`,
    }));
}

module.exports = {
  sanitizeCbArbRows,
  isCbArbRowActiveForceRedeem,
  isCbArbSummaryEligibleRow,
  selectCbArbSummaryRows,
  cbArbOpportunitySets,
  buildConvertibleBondDiscountSnapshot,
  enrichDiscountStrategyRow,
};
