// AI-SUMMARY: styles Markdown 格式化：推送内容模板
// 对应 INDEX.md §9 文件摘要索引

"use strict";

function normalizeDateText(value) {
  const text = String(value || "").trim();
  const hit = text.match(/\d{4}-\d{2}-\d{2}/);
  return hit ? hit[0] : "";
}

function shiftDate(dateText, days) {
  const base = Date.parse(`${normalizeDateText(dateText)}T00:00:00+08:00`);
  if (!Number.isFinite(base)) return "";
  return new Date(base + (days * 24 * 60 * 60 * 1000)).toISOString().slice(0, 10);
}

function compactDateText(value) {
  const text = normalizeDateText(value);
  if (!text) return "--";
  const [year, month, day] = text.split("-");
  return `${year}-${Number(month)}-${Number(day)}`;
}

function formatMoney(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  const fixed = parsed.toFixed(2).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1");
  return `￥${fixed}`;
}

function formatPercent(value, digits = 2, signed = false) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  const text = parsed.toFixed(digits).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1");
  if (!signed) return `${text}%`;
  return `${parsed >= 0 ? "+" : ""}${text}%`;
}

function formatInt(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  return String(Math.round(parsed));
}

function formatIssueScale(value) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "--";
  return `${parsed.toFixed(2).replace(/\.00$/, "").replace(/(\.\d)0$/, "$1")}亿`;
}

function normalizeProgressText(value) {
  return String(value || "")
    .replaceAll("<br>", " ")
    .replaceAll("<br/>", " ")
    .replaceAll("<br />", " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function isAmbushRow(row) {
  if (row?.inApplyStage) return false;
  const progressText = normalizeProgressText(row?.progressName);
  const isTargetStage = ["上市委通过", "同意注册", "注册生效"].some((keyword) => progressText.includes(keyword));
  return isTargetStage && Number(row?.expectedReturnRate) > 6;
}

function resolveCbRightsIssuePushGroups(payload = {}, options = {}) {
  const rows = Array.isArray(payload.sourceRows) ? payload.sourceRows : [];
  const today = normalizeDateText(options.today || "");
  const tomorrow = normalizeDateText(options.tomorrow || shiftDate(today, 1));
  const shRows = rows.filter((row) => String(row?.market || "").trim().toLowerCase() === "sh");

  const buyRows = shRows.filter((row) => {
    const recordDate = normalizeDateText(row?.recordDate);
    return Boolean(row?.inApplyStage) && Boolean(recordDate) && (recordDate === today || recordDate === tomorrow);
  });

  const sellRows = shRows.filter((row) => {
    const applyDate = normalizeDateText(row?.applyDate);
    return Boolean(row?.inApplyStage) && Boolean(applyDate) && applyDate === today;
  });

  const ambushRows = shRows.filter((row) => isAmbushRow(row));

  buyRows.sort((left, right) => {
    const dateCompare = normalizeDateText(left?.recordDate).localeCompare(normalizeDateText(right?.recordDate));
    if (dateCompare !== 0) return dateCompare;
    return String(left?.stockCode || "").localeCompare(String(right?.stockCode || ""));
  });

  sellRows.sort((left, right) => {
    const applyDateCompare = normalizeDateText(left?.applyDate).localeCompare(normalizeDateText(right?.applyDate));
    if (applyDateCompare !== 0) return applyDateCompare;
    const recordDateCompare = normalizeDateText(left?.recordDate).localeCompare(normalizeDateText(right?.recordDate));
    if (recordDateCompare !== 0) return recordDateCompare;
    return String(left?.stockCode || "").localeCompare(String(right?.stockCode || ""));
  });

  ambushRows.sort((left, right) => {
    const marginPeelGap = Number(right?.marginPeelReturnRate || -Infinity) - Number(left?.marginPeelReturnRate || -Infinity);
    if (Number.isFinite(marginPeelGap) && marginPeelGap !== 0) return marginPeelGap;
    const progressDateCompare = normalizeDateText(right?.progressDate).localeCompare(normalizeDateText(left?.progressDate));
    if (progressDateCompare !== 0) return progressDateCompare;
    return String(left?.stockCode || "").localeCompare(String(right?.stockCode || ""));
  });

  return {
    buyRows,
    sellRows,
    ambushRows,
    total: buyRows.length + sellRows.length + ambushRows.length,
  };
}

function buildBuyLine(row) {
  return [
    row.stockName || "--",
    compactDateText(row.recordDate),
    `${formatInt(row.marginRequiredShares)}股`,
    formatMoney(row.marginRequiredFunds),
    formatIssueScale(row.issueScaleYi),
    formatPercent(Number(row.issueRatio) * 100, 1, false),
    formatPercent(row.marginPeelReturnRate, 2, true),
  ].join(" ");
}

function buildSellLine(row) {
  return [
    row.stockName || "--",
    compactDateText(row.applyDate),
    `${formatInt(row.marginRequiredShares)}股`,
    formatMoney(row.marginRequiredFunds),
    formatIssueScale(row.issueScaleYi),
    formatPercent(Number(row.issueRatio) * 100, 1, false),
    formatPercent(row.marginPeelReturnRate, 2, true),
  ].join(" ");
}

function buildAmbushLine(row) {
  return [
    row.stockName || "--",
    normalizeProgressText(row.progressName) || "--",
    compactDateText(row.progressDate),
    `${formatInt(row.marginRequiredShares)}股`,
    formatMoney(row.marginRequiredFunds),
    formatIssueScale(row.issueScaleYi),
    formatPercent(Number(row.issueRatio) * 100, 1, false),
    formatPercent(row.marginPeelReturnRate, 2, true),
  ].join(" ");
}

function buildCbRightsIssueMarkdown(payload = {}, options = {}) {
  const groups = resolveCbRightsIssuePushGroups(payload, options);
  const lines = [];

  if (groups.buyRows.length) {
    lines.push("买入提醒");
    groups.buyRows.forEach((row) => lines.push(buildBuyLine(row)));
  }

  if (groups.sellRows.length) {
    if (lines.length) lines.push("");
    lines.push("卖出提醒");
    groups.sellRows.forEach((row) => lines.push(buildSellLine(row)));
  }

  if (groups.ambushRows.length) {
    if (lines.length) lines.push("");
    lines.push("埋伏阶段");
    groups.ambushRows.forEach((row) => lines.push(buildAmbushLine(row)));
  }

  return {
    markdown: lines.join("\n"),
    total: groups.total,
    buyCount: groups.buyRows.length,
    sellCount: groups.sellRows.length,
    ambushCount: groups.ambushRows.length,
  };
}

module.exports = {
  buildCbRightsIssueMarkdown,
  resolveCbRightsIssuePushGroups,
};
