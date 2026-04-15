"use strict";

function formatNumber(value, digits = 2) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  return parsed.toLocaleString("zh-CN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

function formatPercent(value, digits = 2) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  return `${parsed >= 0 ? "+" : ""}${formatNumber(parsed, digits)}%`;
}

function formatRatioPercent(value, digits = 2) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  return `${formatNumber(parsed * 100, digits)}%`;
}

function formatInt(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  return String(Math.round(parsed));
}

function buildRowLine(row, index) {
  return [
    `${index + 1}. ${row.stockName || "--"}(${row.stockCode || "--"})`,
    `\u65b9\u6848\u8fdb\u5c55 ${row.progressName || "--"}`,
    `\u8fdb\u5c55\u516c\u544a\u65e5 ${row.progressDate || "--"}`,
    `\u53d1\u884c\u89c4\u6a21 ${formatNumber(row.issueScaleYi, 2)}\u4ebf`,
    `\u603b\u5e02\u503c ${formatNumber(row.stockMarketValueYi, 2)}\u4ebf`,
    `\u53d1\u884c\u6bd4\u4f8b ${formatRatioPercent(row.issueRatio, 2)}`,
    `\u4e24\u878d\u6240\u9700\u80a1\u6570 ${formatInt(row.marginRequiredShares)}`,
    `\u80a1\u6743\u767b\u8bb0\u65e5 ${row.recordDate || "--"}`,
    `\u9884\u671f\u6536\u76ca\u7387 ${formatPercent(row.expectedReturnRate, 2)}`,
    `\u4e24\u878d\u6536\u76ca\u7387 ${formatPercent(row.marginReturnRate, 2)}`,
    `\u4e24\u878d\u6536\u76ca\u7387\u53bb\u76ae ${formatPercent(row.marginPeelReturnRate, 2)}`,
    `\u5e74\u5316\u6536\u76ca\u7387 ${formatPercent(row.annualizedReturnRate, 2)}`,
  ].join(" / ");
}

function buildGroupLines(title, rows, maxItems) {
  const items = rows.slice(0, maxItems);
  const lines = [`## ${title}`, `\u5171 ${rows.length} \u9879`, ""];
  if (!items.length) {
    lines.push("\u5f53\u524d\u65e0\u9879\u76ee\u3002");
    return lines;
  }

  items.forEach((row, index) => {
    lines.push(buildRowLine(row, index));
  });
  if (rows.length > items.length) {
    lines.push("");
    lines.push(`\u5176\u4f59 ${rows.length - items.length} \u9879\u8bf7\u5728\u9875\u9762\u67e5\u770b\u3002`);
  }
  return lines;
}

function buildCbRightsIssueMarkdown(payload = {}, options = {}) {
  const rows = Array.isArray(payload.monitorList) ? payload.monitorList : [];
  const updateTime = String(payload.updateTime || options.updateTime || "").trim();
  const sourceUrl = String(payload.sourceUrl || options.sourceUrl || "").trim();
  const maxItems = Math.max(1, Number(options.maxItems) || 10);

  const applyStageRows = rows.filter((row) => Boolean(row?.inApplyStage));
  const highReturnRows = rows.filter((row) => !row?.inApplyStage && Number(row?.expectedReturnRate) > 6);

  const lines = [
    "# \u53ef\u8f6c\u503a\u62a2\u6743\u914d\u552e\u76d1\u63a7",
    updateTime ? `> \u66f4\u65b0 ${updateTime}` : "> \u66f4\u65b0 --",
    `> \u7533\u8d2d\u9636\u6bb5 ${applyStageRows.length} \u9879 / \u9884\u671f\u6536\u76ca\u7387>6% ${highReturnRows.length} \u9879`,
    "",
  ];

  if (!applyStageRows.length && !highReturnRows.length) {
    lines.push("\u5f53\u524d\u6ca1\u6709\u6ee1\u8db3\u63a8\u9001\u6761\u4ef6\u7684\u9879\u76ee\u3002");
  } else {
    lines.push(...buildGroupLines("\u7533\u8d2d\u9636\u6bb5\u9879\u76ee", applyStageRows, maxItems));
    lines.push("");
    lines.push(...buildGroupLines("\u9884\u671f\u6536\u76ca\u7387 > 6% \u9879\u76ee", highReturnRows, maxItems));
  }

  if (sourceUrl) {
    lines.push("");
    lines.push(`\u6765\u6e90\u9875\u9762\uff1a${sourceUrl}`);
  }

  return lines.join("\n");
}

module.exports = {
  buildCbRightsIssueMarkdown,
};
