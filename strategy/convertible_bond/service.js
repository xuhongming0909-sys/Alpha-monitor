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
  return metrics.reduce((sum, value) => sum + ((value !== null && value !== undefined && String(value).trim() !== "") ? 1 : 0), 0);
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

const DEFAULT_ATR_ANCHORS = [
  { x: 0, y: 0 },
  { x: 0.25, y: 0.5 },
  { x: 0.5, y: 0.8 },
  { x: 1, y: 1 },
];

const DEFAULT_SELL_PRESSURE_ANCHORS = [
  { x: 0.5, y: 1 },
  { x: 1, y: 0.8 },
  { x: 5, y: 0.5 },
  { x: 20, y: 0 },
];

const DEFAULT_BOARD_COEFFICIENTS = {
  科创板: 1,
  创业板: 0.85,
  主板: 0.8,
};

/**
 * 折价策略的锚点必须来自明确数值，避免页面、推送、调度各自兜底。
 */
function normalizeAnchorPoints(points, fallback) {
  const source = Array.isArray(points) && points.length ? points : fallback;
  const normalized = source
    .map((item) => ({
      x: toNum(item?.x),
      y: toNum(item?.y),
    }))
    .filter((item) => item.x !== null && item.y !== null)
    .sort((a, b) => a.x - b.x);
  return normalized.length >= 2 ? normalized : fallback;
}

function interpolateByAnchors(value, points, fallbackPoints) {
  const num = toNum(value);
  const anchors = normalizeAnchorPoints(points, fallbackPoints);
  if (num === null) return null;
  if (num <= anchors[0].x) return anchors[0].y;

  for (let index = 1; index < anchors.length; index += 1) {
    const left = anchors[index - 1];
    const right = anchors[index];
    if (num <= right.x) {
      if (right.x === left.x) return right.y;
      const ratio = (num - left.x) / (right.x - left.x);
      return left.y + ((right.y - left.y) * ratio);
    }
  }

  return anchors[anchors.length - 1].y;
}

function normalizeBoardCoefficients(input = {}) {
  return {
    科创板: toNum(input.科创板) ?? DEFAULT_BOARD_COEFFICIENTS.科创板,
    创业板: toNum(input.创业板) ?? DEFAULT_BOARD_COEFFICIENTS.创业板,
    主板: toNum(input.主板) ?? DEFAULT_BOARD_COEFFICIENTS.主板,
  };
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

function compareDiscountMonitorRows(a, b) {
  const compareDesc = (left, right) => {
    const aValue = toNum(left);
    const bValue = toNum(right);
    if (aValue === null && bValue === null) return 0;
    if (aValue === null) return 1;
    if (bValue === null) return -1;
    return bValue - aValue;
  };

  const weightedDiff = compareDesc(a?.weightedDiscountRate, b?.weightedDiscountRate);
  if (weightedDiff !== 0) return weightedDiff;

  const discountDiff = compareDesc(a?.discountRate, b?.discountRate);
  if (discountDiff !== 0) return discountDiff;

  const atrDiff = compareDesc(a?.atrCoefficient, b?.atrCoefficient);
  if (atrDiff !== 0) return atrDiff;

  return String(a?.code || "").localeCompare(String(b?.code || ""), "zh-CN");
}

function buildDiscountStrategyOptions(options = {}) {
  return {
    buyThreshold: toNum(options.buyThreshold) ?? 2,
    sellThreshold: toNum(options.sellThreshold) ?? 0.5,
    atrAnchors: normalizeAnchorPoints(options.atrAnchors, DEFAULT_ATR_ANCHORS),
    sellPressureAnchors: normalizeAnchorPoints(options.sellPressureAnchors, DEFAULT_SELL_PRESSURE_ANCHORS),
    boardCoefficients: normalizeBoardCoefficients(options.boardCoefficients),
    nowIsoText: String(options.nowIsoText || new Date().toISOString()),
    todayDate: String(options.todayDate || todayShanghaiDate()),
  };
}

/**
 * 折价策略只做真实字段派生，不负责推送和持久化。
 */
function enrichDiscountStrategyRow(row, options = {}) {
  const config = buildDiscountStrategyOptions(options);
  const premiumRate = toNum(row?.premiumRate);
  const stockPrice = toNum(row?.stockPrice);
  const stockAtr20 = toNum(row?.stockAtr20);
  const remainingSizeYi = toNum(row?.remainingSizeYi);
  const stockAvgTurnoverAmount20Yi = toNum(row?.stockAvgTurnoverAmount20Yi);
  const discountRate = premiumRate === null ? null : -premiumRate;
  const hasPositiveDiscount = discountRate !== null && discountRate > 0;
  const stockAtr20Pct = (stockPrice !== null && stockPrice > 0 && stockAtr20 !== null)
    ? (stockAtr20 / stockPrice) * 100
    : null;
  const atrRatio = (hasPositiveDiscount && stockAtr20Pct !== null && stockAtr20Pct > 0)
    ? discountRate / stockAtr20Pct
    : null;
  const atrCoefficient = interpolateByAnchors(atrRatio, config.atrAnchors, DEFAULT_ATR_ANCHORS);
  const sellPressureRatio = (
    remainingSizeYi !== null &&
    stockAvgTurnoverAmount20Yi !== null &&
    stockAvgTurnoverAmount20Yi > 0
  )
    ? remainingSizeYi / stockAvgTurnoverAmount20Yi
    : null;
  const sellPressureCoefficient = interpolateByAnchors(
    sellPressureRatio,
    config.sellPressureAnchors,
    DEFAULT_SELL_PRESSURE_ANCHORS
  );
  const boardType = normalizeBoardType(row?.stockCode);
  const boardCoefficient = toNum(config.boardCoefficients[boardType]);
  const weightedDiscountRate = (
    hasPositiveDiscount &&
    atrCoefficient !== null &&
    sellPressureCoefficient !== null &&
    boardCoefficient !== null
  )
    ? discountRate * atrCoefficient * sellPressureCoefficient * boardCoefficient
    : null;
  const buyZoneActive = Boolean(
    discountRate !== null &&
    discountRate > config.buyThreshold &&
    hasPassedConvertStart(row)
  );
  const sellZoneActive = Boolean(discountRate !== null && discountRate < config.sellThreshold);

  return {
    ...row,
    discountRate,
    stockAtr20Pct,
    atrRatio,
    atrCoefficient,
    sellPressureRatio,
    sellPressureCoefficient,
    boardType,
    boardCoefficient,
    weightedDiscountRate,
    buyZoneActive,
    sellZoneActive,
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

function buildDiscountMonitorSummaryItems(rows) {
  return [...rows]
    .sort(compareDiscountMonitorRows)
    .map((row) => ({
      code: pickText(row.code),
      bondName: pickText(row.bondName),
      stockCode: pickText(row.stockCode),
      stockName: pickText(row.stockName),
      discountRate: row.discountRate,
      weightedDiscountRate: row.weightedDiscountRate,
      atrCoefficient: row.atrCoefficient,
      sellPressureCoefficient: row.sellPressureCoefficient,
      boardType: row.boardType,
      boardCoefficient: row.boardCoefficient,
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
    discountRate: row.discountRate,
    weightedDiscountRate: row.weightedDiscountRate,
    atrCoefficient: row.atrCoefficient,
    sellPressureCoefficient: row.sellPressureCoefficient,
    boardType: row.boardType,
    reason: signalType === "buy"
      ? "折价率进入买入区"
      : "折价率进入卖出区",
  };
}

/**
 * 这里统一产出折价策略快照：
 * 1. enrichedRows 给页面与接口使用
 * 2. buySignals / sellSignals 给推送服务使用
 * 3. nextState 只描述下一状态，不在这里直接写文件
 */
function buildConvertibleBondDiscountSnapshot(rows, runtimeState = {}, options = {}) {
  const config = buildDiscountStrategyOptions(options);
  const cleanRows = sanitizeCbArbRows(rows).map((row) => enrichDiscountStrategyRow(row, config));
  const previousState = normalizeDiscountStrategyState(runtimeState);
  const previousMonitorMap = { ...previousState.monitorMap };
  const previousSignalStateMap = { ...previousState.signalStateMap };
  const rowMap = new Map(cleanRows.map((row) => [pickText(row.code), row]));
  const nextMonitorMap = { ...previousMonitorMap };
  const nextSignalStateMap = {};
  const buySignals = [];
  const sellSignals = [];
  const isBootstrap = !previousState.initializedDate;

  cleanRows.forEach((row) => {
    const code = pickText(row.code);
    if (!code) return;
    const previousSignalState = previousSignalStateMap[code] || {};
    const buyZoneActive = Boolean(row.buyZoneActive);
    const sellZoneActive = Boolean(row.sellZoneActive);

    nextSignalStateMap[code] = {
      buyZoneActive,
      sellZoneActive,
    };

    if (isBootstrap) {
      if (buyZoneActive) {
        nextMonitorMap[code] = {
          code,
          enteredAt: previousMonitorMap[code]?.enteredAt || config.nowIsoText,
        };
      }
      return;
    }

    if (!previousSignalState.buyZoneActive && buyZoneActive) {
      nextMonitorMap[code] = {
        code,
        enteredAt: previousMonitorMap[code]?.enteredAt || config.nowIsoText,
      };
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
  const monitorRows = enrichedRows.filter((row) => activeCodes.has(pickText(row.code)));
  const monitorItems = buildDiscountMonitorSummaryItems(monitorRows);

  return {
    rows: enrichedRows,
    buySignals,
    sellSignals,
    isBootstrap,
    discountMonitorSummary: {
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

function isTerminalZeroTurnoverRow(row) {
  if (!row || typeof row !== "object") return false;
  const turnover = Number(row.turnoverAmountYi);
  if (!Number.isFinite(turnover) || turnover > 0) return false;

  const ceaseDate = normalizeComparableDate(row.ceaseDate);
  const delistDate = normalizeComparableDate(row.delistDate);
  if (ceaseDate || delistDate) return true;

  const remainingYears = Number(row.remainingYears);
  const maturityDate = normalizeComparableDate(row.maturityDate);
  if (maturityDate && Number.isFinite(remainingYears) && remainingYears <= 0.02) return true;

  const forceRedeemStatus = String(row.forceRedeemStatus || "").trim();
  return /(完成|摘牌|终止|退市|赎回)/.test(forceRedeemStatus);
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

function cbArbOpportunitySets(rows) {
  const cleanRows = sanitizeCbArbRows(rows);
  const formatDate = (value) => String(value || "").trim();
  const hasPassedConvertStart = (row) => {
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
      reason: `正股接近/触及涨停：${pctText(row.stockChangePercent)}`,
    })),
    convert: topN(
      cleanRows.filter((row) => {
        const spread = convertSpreadRate(row);
        return spread !== null && spread > 2 && hasPassedConvertStart(row);
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
 * 输入是转债套利公开行，输出是满足阈值的提醒对象，不负责发送与冷却。
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
  cbArbOpportunitySets,
  buildConvertibleBondDiscountSnapshot,
  enrichDiscountStrategyRow,
};

