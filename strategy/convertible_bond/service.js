"use strict";

function topN(rows, count, compareFn) {
  return [...rows].sort(compareFn).slice(0, count);
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

function sanitizeCbArbRows(rows) {
  const map = new Map();
  for (const row of Array.isArray(rows) ? rows : []) {
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
  const toNum = (value) => (Number.isFinite(Number(value)) ? Number(value) : null);
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
      rows.filter((row) => toNum(row.doubleLow) !== null),
      3,
      (a, b) => (toNum(a.doubleLow) ?? Number.POSITIVE_INFINITY) - (toNum(b.doubleLow) ?? Number.POSITIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `双低最低：${(toNum(row.doubleLow) ?? 0).toFixed(2)}`,
    })),
    theoPremium: topN(
      rows.filter((row) => toNum(row.theoreticalPremiumRate) !== null),
      3,
      (a, b) => (toNum(b.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY) - (toNum(a.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `理论溢价率最高：${pctText(row.theoreticalPremiumRate)}`,
    })),
    redeem: topN(
      rows.filter((row) => {
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
      rows.filter((row) => (toNum(row.stockChangePercent) ?? -999) >= 9.5),
      3,
      (a, b) => (toNum(b.stockChangePercent) ?? Number.NEGATIVE_INFINITY) - (toNum(a.stockChangePercent) ?? Number.NEGATIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `正股接近/触及涨停：${pctText(row.stockChangePercent)}`,
    })),
    convert: topN(
      rows.filter((row) => {
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
      rows.filter((row) => (toNum(row.price) ?? 9999) < 100),
      3,
      (a, b) => (toNum(a.price) ?? Number.POSITIVE_INFINITY) - (toNum(b.price) ?? Number.POSITIVE_INFINITY)
    ).map((row) => ({
      code: pickText(row.code),
      name: pickText(row.bondName),
      reason: `低于面值博弈，现价 ${(toNum(row.price) ?? 0).toFixed(2)}`,
    })),
  };
}

module.exports = {
  sanitizeCbArbRows,
  cbArbOpportunitySets,
};

