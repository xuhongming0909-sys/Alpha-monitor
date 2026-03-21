"use strict";

function normalizeYmd(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  const hit = text.match(/\d{4}-\d{2}-\d{2}/);
  return hit ? hit[0] : text.slice(0, 10);
}

function subscriptionCode(row, type) {
  if (!row || typeof row !== "object") return "";
  const raw = type === "ipo"
    ? (row.stockCode || row.code || row.symbol)
    : (row.bondCode || row.code || row.symbol);
  return String(raw || "").trim();
}

function subscriptionName(row, type) {
  if (!row || typeof row !== "object") return "";
  const raw = type === "ipo"
    ? (row.stockName || row.name)
    : (row.bondName || row.name);
  return String(raw || "").trim();
}

function subscriptionDate(row) {
  if (!row || typeof row !== "object") return "";
  return normalizeYmd(row.subscribeDate || row.subscriptionDate || row.date);
}

function subscriptionRowScore(row, type) {
  const fields = [
    subscriptionCode(row, type),
    subscriptionName(row, type),
    subscriptionDate(row),
    normalizeYmd(row.paymentDate || row.payment_date || row.lotteryPaymentDate),
    normalizeYmd(row.lotteryDate || row.lottery_date),
    normalizeYmd(row.listingDate || row.listing_date),
    String(row.status || row.state || "").trim(),
  ];
  return fields.reduce((sum, value) => sum + (value ? 1 : 0), 0);
}

function normalizeSubscriptionRow(row, type) {
  const code = subscriptionCode(row, type);
  const name = subscriptionName(row, type);
  const subscribeDate = subscriptionDate(row);
  if (!code || !name || !subscribeDate) return null;
  const cloned = { ...row };
  if (type === "ipo") {
    cloned.stockCode = code;
    cloned.stockName = name;
  } else {
    cloned.bondCode = code;
    cloned.bondName = name;
  }
  cloned.code = code;
  if (!cloned.name) cloned.name = name;
  cloned.subscribeDate = subscribeDate;
  if (cloned.subscriptionDate) cloned.subscriptionDate = subscribeDate;
  return cloned;
}

function sanitizeSubscriptionRows(rows, type) {
  const map = new Map();
  for (const row of Array.isArray(rows) ? rows : []) {
    const normalized = normalizeSubscriptionRow(row, type);
    if (!normalized) continue;
    const key = [
      subscriptionCode(normalized, type),
      subscriptionDate(normalized),
      normalizeYmd(normalized.paymentDate || normalized.payment_date || normalized.lotteryPaymentDate),
      normalizeYmd(normalized.listingDate || normalized.listing_date),
    ].join("|");
    const existing = map.get(key);
    if (!existing || subscriptionRowScore(normalized, type) > subscriptionRowScore(existing, type)) {
      map.set(key, normalized);
    }
  }
  return Array.from(map.values());
}

function sanitizeSubscriptionResult(result, type) {
  if (!result || typeof result !== "object") return result;
  if (result.success === false) return result;
  const upcoming = sanitizeSubscriptionRows(result.upcoming, type);
  const dataRows = sanitizeSubscriptionRows(result.data, type);
  const upcomingKeys = new Set(upcoming.map((row) => `${subscriptionCode(row, type)}|${subscriptionDate(row)}`));
  const mergedData = [...upcoming, ...dataRows.filter((row) => !upcomingKeys.has(`${subscriptionCode(row, type)}|${subscriptionDate(row)}`))];
  return {
    ...result,
    upcoming,
    data: mergedData,
    list: mergedData,
    rows: mergedData,
  };
}

function collectTodaySubscriptionEvents(ipo, bonds, todayText) {
  const ipoRows = [
    ...(Array.isArray(ipo?.upcoming) ? ipo.upcoming : []),
    ...(Array.isArray(ipo?.data) ? ipo.data : []),
  ];
  const bondRows = [
    ...(Array.isArray(bonds?.upcoming) ? bonds.upcoming : []),
    ...(Array.isArray(bonds?.data) ? bonds.data : []),
  ];

  const build = (rows, typeLabel) => rows.flatMap((row) => {
    const name = String(row.name || row.stockName || row.bondName || "").trim();
    const code = String(row.code || row.stockCode || row.bondCode || "").trim();
    const events = [];
    if (String(row.subscribeDate || "") === todayText) events.push({ event: "申购", date: row.subscribeDate, type: typeLabel, code, name });
    if (String(row.paymentDate || "") === todayText) events.push({ event: "缴款", date: row.paymentDate, type: typeLabel, code, name });
    if (String(row.listingDate || "") === todayText) events.push({ event: "上市", date: row.listingDate, type: typeLabel, code, name });
    return events;
  });
  const eventOrder = { "申购": 0, "缴款": 1, "上市": 2 };
  const typeOrder = { "新股": 0, "新债": 1 };
  return [...build(ipoRows, "新股"), ...build(bondRows, "新债")].sort((a, b) => {
    const eventDelta = (eventOrder[a.event] ?? 99) - (eventOrder[b.event] ?? 99);
    if (eventDelta !== 0) return eventDelta;
    const typeDelta = (typeOrder[a.type] ?? 99) - (typeOrder[b.type] ?? 99);
    if (typeDelta !== 0) return typeDelta;
    return String(a.code || "").localeCompare(String(b.code || ""), "zh-Hans-CN");
  });
}

module.exports = {
  sanitizeSubscriptionRows,
  sanitizeSubscriptionResult,
  collectTodaySubscriptionEvents,
};

