"use strict";

/**
 * The Bus 标准记录模型。
 * 这里只定义抓取层和策略层之间的公共数据契约，
 * 不承载任何具体业务插件的策略或抓取细节。
 */

const REQUIRED_FIELDS = [
  "plugin",
  "market",
  "symbol",
  "name",
  "event_type",
  "quote_time",
  "metrics",
  "raw",
  "status",
];

const ALLOWED_STATUS = new Set(["ok", "empty", "error"]);

/**
 * 校验一条标准记录是否满足 The Bus v1 的最低结构要求。
 */
function validateMarketRecord(payload) {
  const missing = REQUIRED_FIELDS.filter((fieldName) => !(fieldName in (payload || {})));
  if (missing.length) {
    throw new Error(`missing required bus fields: ${missing.join(", ")}`);
  }

  if (!ALLOWED_STATUS.has(String(payload.status || "").trim())) {
    throw new Error(`invalid bus status: ${payload.status}`);
  }

  if (!payload.metrics || typeof payload.metrics !== "object" || Array.isArray(payload.metrics)) {
    throw new Error("metrics must be an object");
  }

  if (!payload.raw || typeof payload.raw !== "object" || Array.isArray(payload.raw)) {
    throw new Error("raw must be an object");
  }
}

/**
 * 创建一条经过校验的标准记录。
 * 返回普通对象而不是 class 实例，是为了降低旧代码接入成本。
 */
function createMarketRecord(input) {
  const payload = {
    plugin: String(input.plugin || ""),
    market: String(input.market || ""),
    symbol: String(input.symbol || ""),
    name: String(input.name || ""),
    event_type: String(input.event_type || ""),
    quote_time: String(input.quote_time || ""),
    metrics: input.metrics || {},
    raw: input.raw || {},
    status: String(input.status || ""),
    currency: input.currency ?? null,
    source: input.source ?? null,
    date: input.date ?? null,
    tags: Array.isArray(input.tags) ? input.tags.slice() : [],
    message: String(input.message || ""),
    extra: input.extra && typeof input.extra === "object" && !Array.isArray(input.extra) ? input.extra : {},
  };

  validateMarketRecord(payload);
  return payload;
}

module.exports = {
  REQUIRED_FIELDS,
  validateMarketRecord,
  createMarketRecord,
  validate_market_record: validateMarketRecord,
  create_market_record: createMarketRecord,
};


