"use strict";

const { collectTodaySubscriptionEvents } = require("../../strategy/subscription/service");
const { cbArbOpportunitySets } = require("../../strategy/convertible_bond/service");

/**
 * wecom Markdown 长度受限，这里统一做截断处理。
 * 样式层只关心展示文本，不掺入业务抓取和调度逻辑。
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
 * 推送末尾追加 HTML 看板链接，避免样式文件直接依赖服务端实现。
 */
function appendHtmlLinkForPush(markdown, pushHtmlUrl = "") {
  const raw = String(markdown || "").trimEnd();
  const url = String(pushHtmlUrl || "").trim();
  if (!url) return raw;
  if (raw.includes(url)) return raw;
  return `${raw}\n\n[查看 HTML 看板](${url})`;
}

function topN(rows, count, compareFn) {
  return [...rows].sort(compareFn).slice(0, count);
}

function pctText(value, digits = 2) {
  const num = Number(value);
  if (!Number.isFinite(num)) return "--";
  const sign = num > 0 ? "+" : "";
  return `${sign}${num.toFixed(digits)}%`;
}

function pickText(value, fallback = "--") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

/**
 * 主推送摘要模板。
 * 输入必须已经是上游准备好的数据集，样式层只负责拼文案。
 */
function buildSummaryMarkdown(input, modules, options = {}) {
  const selected = modules || {};
  const ahRows = Array.isArray(input?.ah?.data) ? input.ah.data : [];
  const abRows = Array.isArray(input?.ab?.data) ? input.ab.data : [];
  const cbRows = Array.isArray(input?.cbArb?.data) ? input.cbArb.data : [];
  const monitors = Array.isArray(input?.monitors) ? input.monitors : [];
  const nowText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const todayText = String(options.todayText || nowText.slice(0, 10)).trim();
  const todayDividendRecord = Array.isArray(options.todayDividendRecord) ? options.todayDividendRecord : [];

  const lines = [
    "# Alpha Monitor 主推送",
    `> ${nowText}`,
    "",
  ];

  const pushSectionTitle = (title) => {
    if (lines.length && lines[lines.length - 1] !== "") lines.push("");
    lines.push(`**${title}**`);
  };

  if (selected.ahab) {
    const ahPremium = topN(ahRows, 3, (a, b) => (Number(b.premium) || -999) - (Number(a.premium) || -999));
    const ahDiscount = topN(ahRows, 3, (a, b) => (Number(a.premium) || 999) - (Number(b.premium) || 999));
    const abPremium = topN(abRows, 3, (a, b) => (Number(b.premium) || -999) - (Number(a.premium) || -999));
    const abDiscount = topN(abRows, 3, (a, b) => (Number(a.premium) || 999) - (Number(b.premium) || 999));

    pushSectionTitle("AH 溢价折价（各 3 只）");
    ahPremium.forEach((row, index) => lines.push(`- AH 溢价#${index + 1}：${pickText(row.aName)}(${pickText(row.aCode)}) ${pctText(row.premium)}`));
    ahDiscount.forEach((row, index) => lines.push(`- AH 折价#${index + 1}：${pickText(row.aName)}(${pickText(row.aCode)}) ${pctText(row.premium)}`));
    if (!ahPremium.length && !ahDiscount.length) lines.push("- 暂无 AH 数据");
    lines.push("");

    pushSectionTitle("AB 溢价折价（各 3 只）");
    abPremium.forEach((row, index) => lines.push(`- AB 溢价#${index + 1}：${pickText(row.aName)}(${pickText(row.aCode)}) ${pctText(row.premium)}`));
    abDiscount.forEach((row, index) => lines.push(`- AB 折价#${index + 1}：${pickText(row.aName)}(${pickText(row.aCode)}) ${pctText(row.premium)}`));
    if (!abPremium.length && !abDiscount.length) lines.push("- 暂无 AB 数据");
    lines.push("");
  }

  if (selected.subscription) {
    const events = collectTodaySubscriptionEvents(input?.ipo, input?.bonds, todayText);
    pushSectionTitle("subscription提醒（今天：申购 / 缴款 / 上市）");
    if (!events.length) {
      lines.push("- 今天无申购 / 缴款 / 上市事件");
    } else {
      events.forEach((item) => lines.push(`- ${item.type}${item.event}：${item.name}(${item.code}) ${item.date}`));
    }
    lines.push("");
  }

  if (selected.cbArb) {
    const sets = cbArbOpportunitySets(cbRows);
    const labels = {
      doubleLow: "双低",
      theoPremium: "理论溢价率",
      redeem: "回售套利",
      limitUp: "涨停套利",
      convert: "转股套利",
      delist: "低于面值",
    };

    pushSectionTitle("convertible_bond套利（每类最多 3 条）");
    Object.entries(labels).forEach(([key, title]) => {
      const list = sets[key] || [];
      if (!list.length) return;
      lines.push(`- ${title}：`);
      list.forEach((item) => lines.push(`  - ${item.name}(${item.code})，理由：${item.reason}`));
    });
    if (Object.values(sets).every((list) => !list.length)) lines.push("- 暂无convertible_bond机会");
    lines.push("");
  }

  if (selected.monitor) {
    pushSectionTitle("自定义套利监控（全量）");
    if (!monitors.length) {
      lines.push("- 暂无监控项目");
    } else {
      monitors.forEach((item) => {
        const stock = Number(item.stockYieldRate);
        const cash = Number(item.cashYieldRate);
        const maxYield = Number.isFinite(stock) && Number.isFinite(cash)
          ? Math.max(stock, cash)
          : Number.isFinite(stock) ? stock : cash;
        lines.push(`- ${pickText(item.name)}：换股 ${pctText(stock)} / 现金 ${pctText(cash)} / 最大 ${pctText(maxYield)}`);
      });
    }
    lines.push("");
  }

  if (selected.dividend) {
    pushSectionTitle("dividend提醒（当天股权登记日）");
    if (!todayDividendRecord.length) {
      lines.push("- 今天无股权登记日");
    } else {
      todayDividendRecord.forEach((row) => {
        lines.push(`- ${pickText(row.name)}(${pickText(row.code)}) 登记日 ${pickText(row.dividendData?.recordDate)}，除权日 ${pickText(row.dividendData?.exDividendDate)}`);
      });
    }
    lines.push("");
  }

  return lines.join("\n");
}

module.exports = {
  trimMarkdownForWeCom,
  appendHtmlLinkForPush,
  buildSummaryMarkdown,
};



