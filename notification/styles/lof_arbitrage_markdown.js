"use strict";

function formatNumber(value, digits = 2) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toFixed(digits) : "--";
}

function formatPercent(value, digits = 2) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${parsed.toFixed(digits)}%` : "--";
}

function buildRowLine(row = {}) {
  return [
    `- ${row.code || "--"} ${row.name || "--"}`,
    `溢价率 ${formatPercent(row.premiumRate)}`,
    `${row.marketLabel || "--"}`,
    `涨跌幅 ${formatPercent(row.changeRate)}`,
    `成交额 ${formatNumber(row.turnoverWan)}万`,
    `申购 ${row.applyStatusText || row.applyStatus || "--"}`,
    `申购费 ${formatPercent(row.applyFee)}`,
    `赎回费 ${formatPercent(row.redeemFee)}`,
    `时间 ${row.timeNote || "--"}`,
  ].join(" | ");
}

function buildSection(title, rows, maxItems) {
  const list = Array.isArray(rows) ? rows.slice(0, maxItems) : [];
  if (!list.length) {
    return `## ${title}\n暂无符合条件标的`;
  }
  return `## ${title}\n${list.map((row) => buildRowLine(row)).join("\n")}`;
}

function buildLofArbitrageMarkdown(payload = {}, options = {}) {
  const mode = String(options.mode || "scheduled").trim() || "scheduled";
  const maxItems = Math.max(1, Number(options.maxItems) || 20);
  const limitedRows = Array.isArray(options.limitedRows) ? options.limitedRows : (payload.limitedMonitorRows || []);
  const unlimitedRows = Array.isArray(options.unlimitedRows) ? options.unlimitedRows : (payload.unlimitedMonitorRows || []);
  const title = mode === "instant" ? "LOF套利新入池提醒" : "LOF套利监控池全量推送";
  const updateTime = payload.updateTime || payload.rebuildStatus?.lastRebuildAt || "--";

  return [
    `# ${title}`,
    `更新时间：${updateTime}`,
    `限购监控池：${limitedRows.length} 只`,
    `非限购监控池：${unlimitedRows.length} 只`,
    "",
    buildSection("限购监控池", limitedRows, maxItems),
    "",
    buildSection("非限购监控池", unlimitedRows, maxItems),
  ].join("\n");
}

module.exports = {
  buildLofArbitrageMarkdown,
};

