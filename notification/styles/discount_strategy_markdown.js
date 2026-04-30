// AI-SUMMARY: styles Markdown 格式化：推送内容模板
// 对应 INDEX.md §9 文件摘要索引

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

function ratioText(value, digits = 3) {
  const num = toNum(value);
  return num === null ? "--" : `${(num * 100).toFixed(digits)}%`;
}

function priceText(value, digits = 2) {
  const num = toNum(value);
  return num === null ? "--" : `${num.toFixed(digits)}`;
}

function buildForceRedeemText(item) {
  if (String(item?.forceRedeemLabel || "").trim()) return String(item.forceRedeemLabel).trim();
  return item?.forceRedeemActive ? "强赎中" : "非强赎";
}

/**
 * 低溢价策略推送模板统一在这里收口，保证页面与推送字段口径一致。
 */
function buildConvertibleBondDiscountMarkdown(signalType, items, options = {}) {
  const list = Array.isArray(items) ? items : [];
  const generatedAtText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const titles = {
    buy: "转债套利低溢价买入提醒",
    sell: "转债套利溢价率卖出提醒",
    monitor: "转债套利低溢价监控",
  };
  const subtitleMap = {
    buy: "触发条件：转股溢价率低于买入阈值",
    sell: "触发条件：转股溢价率回到卖出阈值上方",
    monitor: "当前监控名单",
  };

  const lines = [
    `# ${titles[signalType] || titles.monitor}`,
    `> ${generatedAtText}`,
    `> ${subtitleMap[signalType] || subtitleMap.monitor}`,
    "",
  ];

  if (!list.length) {
    lines.push("- 暂无数据");
    return lines.join("\n");
  }

  list.forEach((item) => {
    const stockPriceText = priceText(item.stockPrice);
    const stockChangeText = pctText(item.stockChangePercent, 2);
    const stockDisplay = stockChangeText !== "--"
      ? `${stockPriceText}(${stockChangeText})`
      : stockPriceText;
    lines.push(
      `- ${pickText(item.code)} ${pickText(item.bondName)} | 价格 ${priceText(item.price)} | 溢价率 ${pctText(item.premiumRate)} | 正股 ${stockDisplay} | 转股价值 ${priceText(item.convertValue)} | ${buildForceRedeemText(item)}`
    );
  });

  return lines.join("\n");
}

module.exports = {
  buildConvertibleBondDiscountMarkdown,
};
