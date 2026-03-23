"use strict";

function toNum(value) {
  return Number.isFinite(Number(value)) ? Number(value) : null;
}

function pickText(value, fallback = "--") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function pctText(value, digits = 2) {
  const num = toNum(value);
  if (num === null) return "--";
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(digits)}%`;
}

function priceText(value, digits = 2) {
  const num = toNum(value);
  return num === null ? "--" : num.toFixed(digits);
}

/**
 * 构建可转债异动提醒 Markdown。
 * 这里只负责把已命中的候选压缩成可读消息，不做阈值和冷却判断。
 */
function buildConvertibleBondAlertMarkdown(items, options = {}) {
  const list = Array.isArray(items) ? items : [];
  const generatedAtText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const thresholdText = Number.isFinite(Number(options.convertPremiumLt))
    ? `${Number(options.convertPremiumLt).toFixed(2)}%`
    : "-3.00%";

  const lines = [
    "# 可转债异动提醒",
    `> ${generatedAtText}`,
    `> 触发条件：转股溢价率 < ${thresholdText}`,
    "",
  ];

  if (!list.length) {
    lines.push("- 当前无命中项");
    return lines.join("\n");
  }

  list.forEach((item) => {
    lines.push(
      `- ${pickText(item.bondName)} ${pickText(item.code)} | 转股溢价 ${pctText(item.premiumRate)} | 现价 ${priceText(item.price)} | 转股价值 ${priceText(item.convertValue)}`
    );
    lines.push(
      `  正股 ${pickText(item.stockName)} ${pickText(item.stockCode)} | 正股涨跌 ${pctText(item.stockChangePercent)} | ${pickText(item.reason)}`
    );
  });

  return lines.join("\n");
}

module.exports = {
  buildConvertibleBondAlertMarkdown,
};
