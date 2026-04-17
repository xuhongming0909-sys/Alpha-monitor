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
 * 低溢价策略推送模板统一在这里收口，保证页面与推送字段口径一致。
 */
function buildConvertibleBondDiscountMarkdown(signalType, items, options = {}) {
  const list = Array.isArray(items) ? items : [];
  const generatedAtText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const titles = {
    buy: "可转债低溢价买入提醒",
    sell: "可转债转股溢价率卖出提醒",
    monitor: "可转债低溢价监控",
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
    const weightedText = pctText(item.weightedDiscountRate);
    const premiumText = pctText(item.premiumRate);
    const convertValueText = toNum(item.convertValue)?.toFixed(2) ?? "--";

    if (signalType === "monitor") {
      lines.push(
        `- ${pickText(item.bondName)} ${pickText(item.code)} | 转股溢价率 ${premiumText} | 加权折价率 ${weightedText} | 转股价值 ${convertValueText}`
      );
      return;
    }

    lines.push(
      `- ${pickText(item.bondName)} ${pickText(item.code)} | ${pickText(item.stockName)} ${pickText(item.stockCode)} | 转股溢价率 ${premiumText} | 加权折价率 ${weightedText} | 转股价值 ${convertValueText}`
    );
    lines.push(
      `  正股现价 ${toNum(item.stockPrice)?.toFixed(2) ?? "--"} | 板块 ${pickText(item.boardType)} | ${pickText(item.reason)}`
    );
  });

  return lines.join("\n");
}

module.exports = {
  buildConvertibleBondDiscountMarkdown,
};
