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

/**
 * 三类折价策略推送模板统一在这里收口，保证页面与推送字段口径一致。
 */
function buildConvertibleBondDiscountMarkdown(signalType, items, options = {}) {
  const list = Array.isArray(items) ? items : [];
  const generatedAtText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const titles = {
    buy: "可转债折价买入提醒",
    sell: "可转债折价卖出提醒",
    monitor: "可转债折价监控",
  };
  const subtitleMap = {
    buy: "触发条件：折价率进入买入区",
    sell: "触发条件：折价率进入卖出区",
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
    if (signalType === "monitor") {
      lines.push(
        `- ${pickText(item.bondName)} ${pickText(item.code)} | 折价率 ${pctText(item.discountRate)} | 加权折价率 ${pctText(item.weightedDiscountRate)}`
      );
      return;
    }

    lines.push(
      `- ${pickText(item.bondName)} ${pickText(item.code)} | ${pickText(item.stockName)} ${pickText(item.stockCode)} | 折价率 ${pctText(item.discountRate)} | 加权折价率 ${pctText(item.weightedDiscountRate)}`
    );
    lines.push(
      `  ATR系数 ${toNum(item.atrCoefficient)?.toFixed(2) ?? "--"} | 抛压系数 ${toNum(item.sellPressureCoefficient)?.toFixed(2) ?? "--"} | 板块 ${pickText(item.boardType)} | ${pickText(item.reason)}`
    );
  });

  return lines.join("\n");
}

module.exports = {
  buildConvertibleBondDiscountMarkdown,
};
