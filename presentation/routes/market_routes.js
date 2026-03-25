"use strict";

/**
 * Market-data routes.
 * This layer only validates HTTP params and shapes responses.
 */
function registerMarketRoutes(options = {}) {
  const {
    app,
    nowIso,
    getDataset,
    normalizeDatasetPayload,
    sendSuccess,
    sendError,
    sendServiceResult,
    callDataCore,
    getStockPrice,
    stockSearchDefaultLimit = 10,
    stockSearchMaxLimit = 100,
    stockSearchTimeoutMs = 30000,
    historicalPremiumDefaultDays = 1825,
    historicalPremiumMaxDays = 10000,
    historicalPremiumTimeoutMs = 100000,
  } = options;

  function queryForce(req) {
    return String(req?.query?.force || "0") === "1";
  }

  function registerDatasetRoute(routePath, key, defaultData = null, buildOptions = null) {
    app.get(routePath, async (req, res) => {
      try {
        const force = queryForce(req);
        const requestOptions = typeof buildOptions === "function" ? buildOptions(req, force) : { force };
        return sendServiceResult(res, await getDataset(key, requestOptions), defaultData);
      } catch (error) {
        return sendError(res, error, 500, defaultData);
      }
    });
  }

  registerDatasetRoute("/api/market/ah", "ah", [], (_req, force) => ({ force, forcePairs: force }));
  registerDatasetRoute("/api/market/ab", "ab", [], (_req, force) => ({ force, forcePairs: force }));
  registerDatasetRoute("/api/market/exchange-rate", "exchangeRate", null, (_req, force) => ({ force }));
  registerDatasetRoute("/api/market/ipo", "ipo", [], (_req, force) => ({ force }));
  registerDatasetRoute("/api/market/convertible-bonds", "bonds", [], (_req, force) => ({ force }));
  registerDatasetRoute("/api/market/convertible-bond-arbitrage", "cbArb", [], (_req, force) => ({ force, syncUniverse: force }));
  registerDatasetRoute("/api/market/cb-rights-issue", "cbRightsIssue", { monitorList: [], sourceRows: [], sourceSummary: {}, rebuildStatus: {} }, (_req, force) => ({ force }));
  registerDatasetRoute("/api/market/merger", "merger", [], (_req, force) => ({ force }));
  registerDatasetRoute("/api/market/event-arbitrage", "eventArb", {}, (_req, force) => ({ force }));

  app.get("/api/market/subscriptions", async (req, res) => {
    try {
      const force = queryForce(req);
      const [ipoRaw, bondsRaw] = await Promise.all([
        getDataset("ipo", { force }),
        getDataset("bonds", { force }),
      ]);
      const ipo = normalizeDatasetPayload("ipo", ipoRaw) || {};
      const bonds = normalizeDatasetPayload("bonds", bondsRaw) || {};
      const latest = [ipo.updateTime, bonds.updateTime]
        .map((item) => String(item || "").trim())
        .filter(Boolean)
        .sort()
        .pop() || nowIso();

      return sendSuccess(res, {
        ipo: {
          upcoming: Array.isArray(ipo.upcoming) ? ipo.upcoming : [],
          data: Array.isArray(ipo.data) ? ipo.data : [],
          updateTime: ipo.updateTime || latest,
        },
        bonds: {
          upcoming: Array.isArray(bonds.upcoming) ? bonds.upcoming : [],
          data: Array.isArray(bonds.data) ? bonds.data : [],
          updateTime: bonds.updateTime || latest,
        },
        updateTime: latest,
      });
    } catch (error) {
      return sendError(res, error, 500, {
        ipo: { upcoming: [], data: [] },
        bonds: { upcoming: [], data: [] },
        updateTime: nowIso(),
      });
    }
  });

  app.get("/api/market/historical-premium", async (req, res) => {
    try {
      const type = String(req.query.type || "AH").toUpperCase();
      const code = String(req.query.code || "").trim();
      const days = Number(req.query.days || historicalPremiumDefaultDays);
      if (!code) return sendError(res, "缺少股票代码 code", 400, []);
      if (!["AH", "AB"].includes(type)) return sendError(res, "type 仅支持 AH / AB", 400, []);
      if (!Number.isFinite(days) || days < 1 || days > historicalPremiumMaxDays) {
        return sendError(res, `days 必须是 1-${historicalPremiumMaxDays} 的数字`, 400, []);
      }
      return sendServiceResult(
        res,
        await callDataCore(["historical-premium", type, code, String(days)], { timeout: historicalPremiumTimeoutMs }),
        []
      );
    } catch (error) {
      return sendError(res, error, 500, []);
    }
  });

  app.get("/api/stock/search", async (req, res) => {
    try {
      const keyword = String(req.query.keyword || "").trim();
      const limit = Number(req.query.limit || stockSearchDefaultLimit);
      if (!keyword) return sendError(res, "keyword 不能为空", 400, []);
      if (!Number.isFinite(limit) || limit < 1 || limit > stockSearchMaxLimit) {
        return sendError(res, `limit 必须是 1-${stockSearchMaxLimit} 的数字`, 400, []);
      }
      return sendServiceResult(
        res,
        await callDataCore(["search", keyword, String(limit)], { timeout: stockSearchTimeoutMs }),
        []
      );
    } catch (error) {
      return sendError(res, error, 500, []);
    }
  });

  app.get("/api/stock/price", async (req, res) => {
    try {
      const code = String(req.query.code || "").trim();
      const market = String(req.query.market || "a").trim().toLowerCase();
      const bMarket = String(req.query.bMarket || "sh").trim().toLowerCase();
      if (!code) return sendError(res, "code 不能为空", 400);
      if (!["a", "h", "b"].includes(market)) return sendError(res, "market 仅支持 a/h/b", 400);
      if (market === "b" && !["sh", "sz"].includes(bMarket)) return sendError(res, "bMarket 仅支持 sh/sz", 400);
      return sendServiceResult(res, await getStockPrice(code, market, bMarket));
    } catch (error) {
      return sendError(res, error);
    }
  });
}

module.exports = {
  registerMarketRoutes,
};
