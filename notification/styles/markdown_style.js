// AI-SUMMARY: 推送 Markdown 样式：通用格式化模板
// 对应 INDEX.md §9 文件摘要索引

"use strict";

const { collectTodaySubscriptionEvents } = require("../../strategy/subscription/service");

/**
 * 企业微信 Markdown 长度有限，这里统一做裁剪。
 */
function trimMarkdownForWeCom(markdown, maxLength = 3900) {
  const raw = String(markdown || "");
  const maxBytes = Math.max(512, Number(maxLength) || 3900);
  if (Buffer.byteLength(raw, "utf8") <= maxBytes) return raw;

  const suffix = "\n\n> 内容过长，已截断。";
  const suffixBytes = Buffer.byteLength(suffix, "utf8");
  let left = 0;
  let right = raw.length;
  let best = "";

  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    const candidate = raw.slice(0, mid);
    const size = Buffer.byteLength(candidate, "utf8") + suffixBytes;
    if (size <= maxBytes) {
      best = candidate;
      left = mid + 1;
    } else {
      right = mid - 1;
    }
  }

  return `${best}${suffix}`;
}

/**
 * 在推送末尾追加网页入口，方便直接回到实时页面。
 */
function appendHtmlLinkForPush(markdown, pushHtmlUrl = "") {
  const raw = String(markdown || "").trimEnd();
  const url = String(pushHtmlUrl || "").trim();
  if (!url) return raw;
  if (raw.includes(url)) return raw;
  return `${raw}\n\n[查看实时网页](${url})`;
}

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

function topN(rows, count, compareFn) {
  return [...rows].sort(compareFn).slice(0, Math.max(0, count));
}

function buildSection(lines, title, rows) {
  lines.push(`**${title}**`);
  if (!rows.length) {
    lines.push("- 暂无重点项");
  } else {
    rows.forEach((row) => lines.push(row));
  }
  lines.push("");
}

function buildPremiumRows(rows, prefix, topCount) {
  const premiumRows = topN(
    rows.filter((row) => toNum(row.premium) !== null),
    topCount,
    (a, b) => (toNum(b.premium) ?? Number.NEGATIVE_INFINITY) - (toNum(a.premium) ?? Number.NEGATIVE_INFINITY)
  );
  const discountRows = topN(
    rows.filter((row) => toNum(row.premium) !== null),
    topCount,
    (a, b) => (toNum(a.premium) ?? Number.POSITIVE_INFINITY) - (toNum(b.premium) ?? Number.POSITIVE_INFINITY)
  );

  const picked = [];
  premiumRows.forEach((row) => {
    const pairPrice = row.hPriceCny ?? row.bPriceCny ?? row.hPrice ?? row.bPrice;
    picked.push(
      `- ${prefix}溢价 | ${pickText(row.aName)} ${pickText(row.aCode)} | 溢价 ${pctText(row.premium)} | 分位 ${pctText(row.percentile)} | A ${priceText(row.aPrice)} / 对侧 ${priceText(pairPrice)}`
    );
  });
  discountRows.forEach((row) => {
    const pairPrice = row.hPriceCny ?? row.bPriceCny ?? row.hPrice ?? row.bPrice;
    picked.push(
      `- ${prefix}折价 | ${pickText(row.aName)} ${pickText(row.aCode)} | 溢价 ${pctText(row.premium)} | 分位 ${pctText(row.percentile)} | A ${priceText(row.aPrice)} / 对侧 ${priceText(pairPrice)}`
    );
  });
  return picked;
}

function buildSubscriptionLines(input, todayText) {
  const events = collectTodaySubscriptionEvents(input?.ipo, input?.bonds, todayText);
  return events.map((item) => `- ${item.type}${item.event} | ${pickText(item.name)} ${pickText(item.code)} | ${pickText(item.date)}`);
}

function buildMonitorLines(monitors) {
  return (Array.isArray(monitors) ? monitors : []).map((item) => {
    const stock = toNum(item.stockYieldRate);
    const cash = toNum(item.cashYieldRate);
    const maxYield = Number.isFinite(stock) && Number.isFinite(cash)
      ? Math.max(stock, cash)
      : Number.isFinite(stock) ? stock : cash;
    return `- ${pickText(item.name)} | 换股 ${pctText(stock, 3)} | 现金 ${pctText(cash, 3)} | 最大 ${pctText(maxYield, 3)}`;
  });
}

/**
 * 构建定时摘要 Markdown。
 * 可转债套利已拆为独立推送，这里兼容忽略旧 cbArb 选择。
 */
function buildSummaryMarkdown(input, modules, options = {}) {
  const selected = modules || {};
  const summaryConfig = options.summaryConfig || {};
  const ahRows = Array.isArray(input?.ah?.data) ? input.ah.data : [];
  const abRows = Array.isArray(input?.ab?.data) ? input.ab.data : [];
  const monitors = Array.isArray(input?.monitors) ? input.monitors : [];
  const nowText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const todayText = String(options.todayText || nowText.slice(0, 10)).trim();
  const lines = [
    "# Alpha Monitor 定时推送",
    `> ${nowText}`,
    "",
  ];

  if (selected.subscription) {
    buildSection(lines, "今日打新", buildSubscriptionLines(input, todayText));
  }

  if (selected.monitor) {
    buildSection(lines, "自定义监控", buildMonitorLines(monitors));
  }

  if (selected.ahab) {
    buildSection(lines, "AH", buildPremiumRows(ahRows, "AH", Math.max(1, Number(summaryConfig.ahTopN) || 2)));
    buildSection(lines, "AB", buildPremiumRows(abRows, "AB", Math.max(1, Number(summaryConfig.abTopN) || 2)));
  }

  return lines.join("\n");
}

module.exports = {
  trimMarkdownForWeCom,
  appendHtmlLinkForPush,
  buildSummaryMarkdown,
};
