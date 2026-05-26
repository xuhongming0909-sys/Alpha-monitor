"use strict";
// LOF IOPV 推送 Markdown 格式化

function formatPercent(value, digits = 2) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? `${parsed.toFixed(digits)}%` : "--";
}

function buildLofIopvMarkdown(payload = {}, options = {}) {
  const maxItems = Math.max(1, Number(options.maxItems) || 20);
  const rows = Array.isArray(payload.rows) ? payload.rows : [];
  const updateTime = payload.updateTime || "--";

  const items = rows
    .filter(r => r.premiumRate != null)
    .sort((a, b) => Math.abs(b.premiumRate) - Math.abs(a.premiumRate))
    .slice(0, maxItems);

  if (!items.length) {
    return `# LOF/QDII 估值推送\n更新时间：${updateTime}\n\n暂无数据`;
  }

  const lines = items.map(r =>
    `- ${r.code || "--"} ${r.name || "--"} | 溢价率 ${formatPercent(r.premiumRate)} | IOPV ${r.iopv?.toFixed(4) || "--"} | ${r.calcMode || "--"} | ${r.fundType || "?"}类`
  );

  return [
    "# LOF/QDII 估值推送",
    `更新时间：${updateTime}`,
    `共 ${rows.length} 只 (${items.length} 只有溢价率)`,
    "",
    ...lines,
  ].join("\n");
}

module.exports = { buildLofIopvMarkdown };