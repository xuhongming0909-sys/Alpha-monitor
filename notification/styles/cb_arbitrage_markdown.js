"use strict";

function toNum(value) {
  return Number.isFinite(Number(value)) ? Number(value) : null;
}

function pickText(value, fallback = "--") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function firstFiniteValue(row, keys) {
  for (const key of keys) {
    const value = toNum(row?.[key]);
    if (value !== null) return value;
  }
  return null;
}

function formatNumber(value, digits = 2) {
  const num = toNum(value);
  if (num === null) return "--";
  return num.toFixed(digits).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1");
}

function formatPercent(value, digits = 2) {
  const num = toNum(value);
  if (num === null) return "--";
  const sign = num > 0 ? "+" : "";
  return `${sign}${formatNumber(num * 100, digits)}%`;
}

function formatPremiumPercent(value, digits = 2) {
  const num = toNum(value);
  if (num === null) return "--";
  const sign = num > 0 ? "+" : "";
  return `${sign}${formatNumber(num, digits)}%`;
}

function formatYears(value, digits = 2) {
  const text = formatNumber(value, digits);
  return text === "--" ? "--" : `${text}年`;
}

function formatYi(value, digits = 2) {
  const text = formatNumber(value, digits);
  return text === "--" ? "--" : `${text}亿`;
}

function resolveExpectedDurationYears(row = {}) {
  const direct = firstFiniteValue(row, [
    "expectedDurationYears",
    "smallRedemptionExpectedDurationYears",
    "smallRedemptionExpectedYears",
    "expectedHoldingYears",
    "expectedDuration",
  ]);
  if (direct !== null) return direct;
  const remainingYears = resolveRemainingYears(row);
  return remainingYears === null ? null : remainingYears + 0.5;
}

function resolveRemainingYears(row = {}) {
  return firstFiniteValue(row, [
    "remainingYears",
    "remainingTermYears",
  ]);
}

function resolveTotalAnnualizedYield(row = {}) {
  const directDecimal = firstFiniteValue(row, [
    "smallRedemptionTotalAnnualizedYield",
    "totalAnnualizedYield",
  ]);
  if (directDecimal !== null) return directDecimal;
  return null;
}

function buildBondLine(row = {}) {
  const name = pickText(row.bondName || row.name);
  const code = pickText(row.code || row.bondCode || row.secuCode || row.symbol, "");
  if (row.isSmallRedemption) {
    return [
      `- ${name}${code ? ` ${code}` : ""}`,
      `价格 ${formatNumber(row.price, 2)}`,
      `溢价 ${formatPremiumPercent(row.premiumRate)}`,
      `总年化 ${formatPercent(resolveTotalAnnualizedYield(row))}`,
      `耗时 ${formatYears(resolveExpectedDurationYears(row))}`,
      `规模 ${formatYi(row.remainingSizeYi)}`,
    ].join(" | ");
  }
  return [
    `- ${name}${code ? ` ${code}` : ""}`,
    `价格 ${formatNumber(row.price, 2)}`,
    `溢价 ${formatPremiumPercent(row.premiumRate)}`,
    `双低 ${formatNumber(row.doubleLow, 2)}`,
    `理论溢价 ${formatPremiumPercent(row.theoreticalPremiumRate)}`,
  ].join(" | ");
}

function buildCbArbitrageMarkdown(payload = {}, options = {}) {
  const rows = Array.isArray(payload.rows) ? payload.rows : [];
  const maxItems = Math.max(1, Number(options.maxItems) || rows.length || 1);
  const updateTime = pickText(payload.updateTime);
  const blocks = rows.slice(0, maxItems).map((row) => buildBondLine(row));

  return [
    "# 可转债套利推送",
    `更新时间：${updateTime}`,
    `标的数量：${rows.length}`,
    "",
    blocks.join("\n"),
  ].join("\n").trim();
}

module.exports = {
  buildCbArbitrageMarkdown,
};
