"use strict";

const { collectTodaySubscriptionEvents } = require("../../strategy/subscription/service");
const { selectCbArbSummaryRows } = require("../../strategy/convertible_bond/service");

/**
 * 企业微信 Markdown 长度有限，这里统一做裁剪。
 * 样式层只处理文本展示，不参与业务判断。
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

function computeOptionTheoreticalValue(row) {
  const callValue = toNum(row?.callOptionValue);
  const putValue = toNum(row?.putOptionValue);
  const pricingFormula = String(row?.pricingFormula || "").trim();
  if (pricingFormula === "bond+callspread" && callValue !== null) {
    return callValue;
  }
  if (callValue !== null || putValue !== null) {
    return (callValue ?? 0) - (putValue ?? 0);
  }
  const theoreticalPrice = toNum(row?.theoreticalPrice);
  const pureBondValue = toNum(row?.pureBondValue);
  if (theoreticalPrice === null || pureBondValue === null) return null;
  return theoreticalPrice - pureBondValue;
}

function computeImplicitOptionValue(row) {
  const price = toNum(row?.price);
  const pureBondValue = toNum(row?.pureBondValue);
  if (price === null || pureBondValue === null) return null;
  return price - pureBondValue;
}

function computeOptionDiscountRate(row) {
  const theoreticalOptionValue = computeOptionTheoreticalValue(row);
  const implicitOptionValue = computeImplicitOptionValue(row);
  if (theoreticalOptionValue === null || implicitOptionValue === null) return null;
  if (theoreticalOptionValue === 0) return null;
  return (implicitOptionValue / theoreticalOptionValue - 1) * 100;
}

function buildCbSummaryLines(rows, options = {}) {
  const topCount = 3;
  const summaryRows = selectCbArbSummaryRows(rows);
  const doubleLowRows = topN(
    summaryRows.filter((row) => toNum(row.doubleLow) !== null),
    topCount,
    (a, b) => (toNum(a.doubleLow) ?? Number.POSITIVE_INFINITY) - (toNum(b.doubleLow) ?? Number.POSITIVE_INFINITY)
  );
  const theoryRows = topN(
    summaryRows.filter((row) => toNum(row.theoreticalPremiumRate) !== null),
    topCount,
    (a, b) => (toNum(b.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY) - (toNum(a.theoreticalPremiumRate) ?? Number.NEGATIVE_INFINITY)
  );

  const picked = [];
  doubleLowRows.forEach((row) => {
    picked.push(
      `- 双低前三名 | ${pickText(row.bondName)} ${pickText(row.code)} | 双低 ${priceText(row.doubleLow)} | 转股溢价 ${pctText(row.premiumRate)} | 转股价值 ${priceText(row.convertValue)} | 现价 ${priceText(row.price)}`
    );
  });
  theoryRows.forEach((row) => {
    picked.push(
      `- 理论溢价率前三名 | ${pickText(row.bondName)} ${pickText(row.code)} | 理论溢价 ${pctText(row.theoreticalPremiumRate)} | 期权折价率 ${pctText(computeOptionDiscountRate(row))} | 双低 ${priceText(row.doubleLow)} | 现价 ${priceText(row.price)}`
    );
  });
  return picked;
  const seen = new Set();
  for (const item of flattened) {
    if (!item?.code || seen.has(item.code)) continue;
    const row = rowMap.get(item.code);
    if (!row) continue;
    seen.add(item.code);
    picked.push(
      `- ${pickText(row.bondName)} ${pickText(row.code)} | 现价 ${priceText(row.price)} | 转股溢价 ${pctText(row.premiumRate)} | 转股价值 ${priceText(row.convertValue)} | 双低 ${priceText(row.doubleLow)} | 理论溢价 ${pctText(row.theoreticalPremiumRate)} | ${pickText(item.reason)}`
    );
    if (picked.length >= topCount) break;
  }
  return picked;
}

function buildSubscriptionLines(input, todayText) {
  const events = collectTodaySubscriptionEvents(input?.ipo, input?.bonds, todayText);
  return events.map((item) => `- ${item.type}${item.event} | ${pickText(item.name)} ${pickText(item.code)} | ${pickText(item.date)}`);
}

function buildMonitorLines(monitors) {
  return buildMonitorLinesPrecise(monitors);
  return (Array.isArray(monitors) ? monitors : []).map((item) => {
    const stock = toNum(item.stockYieldRate);
    const cash = toNum(item.cashYieldRate);
    const maxYield = Number.isFinite(stock) && Number.isFinite(cash)
      ? Math.max(stock, cash)
      : Number.isFinite(stock) ? stock : cash;
    return `- ${pickText(item.name)} | 换股 ${pctText(stock)} | 现金 ${pctText(cash)} | 最大 ${pctText(maxYield)}`;
  });
}

function buildMonitorLinesPrecise(monitors) {
  return (Array.isArray(monitors) ? monitors : []).map((item) => {
    const stock = toNum(item.stockYieldRate);
    const cash = toNum(item.cashYieldRate);
    const maxYield = Number.isFinite(stock) && Number.isFinite(cash)
      ? Math.max(stock, cash)
      : Number.isFinite(stock) ? stock : cash;
    return `- ${pickText(item.name)} | 换股 ${pctText(stock, 3)} | 现金 ${pctText(cash, 3)} | 最大 ${pctText(maxYield, 3)}`;
  });
}

function buildDividendLines(rows) {
  return (Array.isArray(rows) ? rows : []).map((row) => (
    `- ${pickText(row.name)} ${pickText(row.code)} | 登记日 ${pickText(row.dividendData?.recordDate)} | 除权日 ${pickText(row.dividendData?.exDividendDate)}`
  ));
}

function buildEventArbSummaryLines(items, topCount) {
  return (Array.isArray(items) ? items : [])
    .slice(0, Math.max(1, topCount))
    .map((item) => (
      `- ${pickText(item.name)} ${pickText(item.symbol)} | ${pickText(item.eventType)} | ${pickText(item.eventStage || item.categoryLabel || item.category)} | ${pickText(item.spreadText, "") || "新进入事件池"}`
    ));
}

/**
 * 构建定时摘要 Markdown。
 * 输入必须是已经准备好的真实数据和通知运行态摘要。
 */
function buildSummaryMarkdown(input, modules, options = {}) {
  const selected = modules || {};
  const summaryConfig = options.summaryConfig || {};
  const ahRows = Array.isArray(input?.ah?.data) ? input.ah.data : [];
  const abRows = Array.isArray(input?.ab?.data) ? input.ab.data : [];
  const cbRows = Array.isArray(input?.cbArb?.data) ? input.cbArb.data : [];
  const monitors = Array.isArray(input?.monitors) ? input.monitors : [];
  const todayDividendRecord = Array.isArray(options.todayDividendRecord) ? options.todayDividendRecord : [];
  const eventArbNewItems = Array.isArray(input?.eventArbNextDaySummary) ? input.eventArbNextDaySummary : [];
  const nowText = String(
    options.generatedAtText || new Date().toLocaleString("zh-CN", { hour12: false })
  ).trim();
  const todayText = String(options.todayText || nowText.slice(0, 10)).trim();
  const lines = [
    "# Alpha Monitor 定时推送",
    `> ${nowText}`,
    "",
  ];

  if (selected.ahab) {
    buildSection(lines, "AH / AB 极值", [
      ...buildPremiumRows(ahRows, "AH", Math.max(1, Number(summaryConfig.ahTopN) || 2)),
      ...buildPremiumRows(abRows, "AB", Math.max(1, Number(summaryConfig.abTopN) || 2)),
    ]);
  }

  if (selected.cbArb) {
    buildSection(lines, "可转债机会", buildCbSummaryLines(cbRows, {
      cbTopN: summaryConfig.cbTopN,
      pushCategories: options.cbPushCategories,
    }));
  }

  if (selected.subscription) {
    buildSection(lines, "今日打新", buildSubscriptionLines(input, todayText));
  }

  if (selected.dividend) {
    buildSection(lines, "分红提醒", buildDividendLines(todayDividendRecord));
  }

  if (selected.monitor) {
    buildSection(lines, "自定义监控（全量）", buildMonitorLines(monitors));
  }

  if (selected.eventArb) {
    buildSection(
      lines,
      "昨日新增事件套利",
      buildEventArbSummaryLines(eventArbNewItems, Number(summaryConfig.eventArbitrageTopN) || 6)
    );
  }

  return lines.join("\n");
}

module.exports = {
  trimMarkdownForWeCom,
  appendHtmlLinkForPush,
  buildSummaryMarkdown,
};
