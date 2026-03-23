"use strict";

const { createDividendStrategy } = require("./service");

/**
 * dividend运行态服务。
 * 这一层负责维护用户自选dividend组合、刷新dividend数据，并把“登记日提醒”规则交给策略层处理。
 */
function createDividendRuntimeService(options = {}) {
  const {
    stateRegistry,
    nowIso,
    callDataCore,
    getStockPrice,
  } = options;

  function loadPortfolio() {
    const rows = stateRegistry.read("dividend_portfolio", "dividend_portfolio.json", []);
    return Array.isArray(rows) ? rows : [];
  }

  function savePortfolio(rows) {
    stateRegistry.write("dividend_portfolio", "dividend_portfolio.json", rows);
  }

  function isMissingOrCodeName(name, code) {
    const safeName = String(name || "").trim();
    const safeCode = String(code || "").trim();
    if (!safeName) return true;
    if (!safeCode) return false;
    return safeName === safeCode;
  }

  async function fetchDividend(code) {
    try {
      const result = await callDataCore(["dividend", code], { timeout: 90000 });
      return result?.success && result?.data ? result.data : null;
    } catch {
      return null;
    }
  }

  async function resolveStockNameByCode(code, fallback = "") {
    const safeCode = String(code || "").trim();
    if (!safeCode) return String(fallback || "").trim();
    try {
      const result = await callDataCore(["search", safeCode, "12"], { timeout: 30000 });
      const rows = Array.isArray(result?.data) ? result.data : [];
      const exact = rows.find((item) => String(item?.code || "").trim() === safeCode);
      const candidate = exact || rows[0] || null;
      const name = String(candidate?.name || "").trim();
      return name || String(fallback || "").trim();
    } catch {
      return String(fallback || "").trim();
    }
  }

  async function resolveStockMetaByCode(code) {
    const safeCode = String(code || "").trim();
    if (!safeCode) return null;
    try {
      const result = await callDataCore(["search", safeCode, "20"], { timeout: 30000 });
      const rows = Array.isArray(result?.data) ? result.data : [];
      const exact = rows.find((item) => String(item?.code || "").trim() === safeCode);
      if (!exact) return null;
      return {
        code: safeCode,
        name: String(exact?.name || "").trim(),
        market: String(exact?.market || "").trim().toLowerCase(),
        marketType: String(exact?.marketType || "").trim().toUpperCase(),
      };
    } catch {
      return null;
    }
  }

  async function refreshPortfolio() {
    const refreshed = await Promise.all(loadPortfolio().map(async (row) => {
      try {
        const latest = await fetchDividend(row.code);
        if (latest) {
          const latestRawName = String(latest.name || "").trim();
          const fallbackName = String(row.name || row.dividendData?.name || "").trim();
          const resolvedName = isMissingOrCodeName(latestRawName, row.code)
            ? await resolveStockNameByCode(row.code, fallbackName)
            : latestRawName;
          return {
            ...row,
            name: resolvedName || row.code,
            dividendData: {
              ...latest,
              name: resolvedName || latestRawName || row.code,
            },
          };
        }

        if (!row.dividendData) return row;
        const market = row.code.startsWith("9") || row.code.startsWith("2") ? "b" : "a";
        const bMarket = row.code.startsWith("9") ? "sh" : "sz";
        const priceResult = await getStockPrice(row.code, market, bMarket);
        const latestPrice = Number(priceResult?.data?.price || 0);
        if (!latestPrice) return row;

        const dividendPerShare = Number(row.dividendData.dividendPerShare || 0);
        const dividendYield = latestPrice ? (dividendPerShare / latestPrice) * 100 : null;
        return {
          ...row,
          name: isMissingOrCodeName(row.name, row.code)
            ? (await resolveStockNameByCode(row.code, row.dividendData?.name || "")) || row.code
            : row.name,
          dividendData: {
            ...row.dividendData,
            currentPrice: latestPrice,
            dividendYield: Number.isFinite(dividendYield) ? Number(dividendYield.toFixed(2)) : null,
          },
        };
      } catch {
        return row;
      }
    }));

    savePortfolio(refreshed);
    return refreshed;
  }

  async function addDividendStock({ code, name }) {
    const trimmed = String(code || "").trim();
    if (!trimmed) throw new Error("股票代码不能为空");
    if (!/^\d{5,6}$/.test(trimmed)) throw new Error("股票代码格式错误");

    const portfolio = loadPortfolio();
    if (portfolio.find((row) => row.code === trimmed)) throw new Error("该股票已在dividend组合中");

    const stockMeta = await resolveStockMetaByCode(trimmed);
    if (!stockMeta?.name) throw new Error("无效股票代码，无法添加到dividend组合");

    const preferredName = isMissingOrCodeName(name, trimmed)
      ? stockMeta.name
      : String(name || "").trim();

    portfolio.push({
      code: trimmed,
      name: preferredName || trimmed,
      addTime: nowIso(),
      dividendData: await fetchDividend(trimmed),
    });
    savePortfolio(portfolio);
    return portfolio;
  }

  function removeDividendStock(code) {
    const trimmed = String(code || "").trim();
    const next = loadPortfolio().filter((row) => row.code !== trimmed);
    savePortfolio(next);
    return next;
  }

  // dividend提醒规则只消费当前组合快照，不直接依赖 UI。
  const strategy = createDividendStrategy({ loadPortfolio });

  return {
    loadPortfolio,
    savePortfolio,
    refreshPortfolio,
    addDividendStock,
    removeDividendStock,
    upcomingDividends: (days = 7) => strategy.upcomingDividends(days),
  };
}

module.exports = {
  createDividendRuntimeService,
};


