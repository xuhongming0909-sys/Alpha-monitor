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
  return `${formatNumber(parsed, digits)}%`;
}

function buildCbRightsIssueMarkdown(payload = {}, options = {}) {
  const rows = Array.isArray(payload.monitorList) ? payload.monitorList : [];
  const updateTime = String(payload.updateTime || options.updateTime || "").trim();
  const sourceUrl = String(payload.sourceUrl || options.sourceUrl || "").trim();
  const maxItems = Math.max(1, Number(options.maxItems) || 10);
  const items = rows.slice(0, maxItems);

  const lines = [
    "# 可转债抢权配售监控",
    updateTime ? `> 更新 ${updateTime}` : "> 更新 --",
    `> 当前入池 ${rows.length} 项`,
    "",
  ];

  if (!items.length) {
    lines.push("当前监控列表为空，本次不推送项目明细。");
  } else {
    items.forEach((row, index) => {
      lines.push(
        `${index + 1}. ${row.bondName || "--"}(${row.bondCode || "--"}) / ${row.stockName || "--"}(${row.stockCode || "--"}) / ${row.progressName || "--"} / 登记日 ${row.recordDate || "--"} / 配10张股数 ${formatNumber(row.requiredSharesFinal, 0)} / 资金 ${formatNumber(row.requiredFunds, 2)} / 预期收益 ${formatNumber(row.expectedProfit, 2)} / 收益率 ${formatPercent(row.expectedReturnRate, 2)}`
      );
    });
    if (rows.length > items.length) {
      lines.push("");
      lines.push(`其余 ${rows.length - items.length} 项请打开页面查看。`);
    }
  }

  if (sourceUrl) {
    lines.push("");
    lines.push(`来源页面：${sourceUrl}`);
  }

  return lines.join("\n");
}

module.exports = {
  buildCbRightsIssueMarkdown,
};
