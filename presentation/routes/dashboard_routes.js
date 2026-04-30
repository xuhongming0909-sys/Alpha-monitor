"use strict";

/**
 * 看板接口路由。
 * 这里承接overview、监控、dividend、merger_report等偏展示交互的 API。
 */
function registerDashboardRoutes(options = {}) {
  const {
    app,
    nowIso,
    getHealthSnapshot,
    getDashboardUiConfig,
    getDashboardResourceStatus,
    getShanghaiParts,
    normalizeDateText,
    pickText,
    sendSuccess,
    sendError,
    sendServiceResult,
    getAllMonitors,
    upsertMonitor,
    deleteMonitor,
    loadPortfolio,
    refreshPortfolio,
    addDividendStock,
    removeDividendStock,
    upcomingDividends,
    callDataCore,
    getDataset,
    getTodayMergerGroups,
    getMergerReportByCompany,
    ensureMergerCompanyReport,
    mergerCompanyCode,
    mergerCompanyName,
    mergerCompanyKey,
    mergerAnnouncementDate,
    getOverviewFromDatasets,
    dividendUpcomingDefaultDays = 7,
    dividendUpcomingMaxDays = 365,
    stockSearchDefaultLimit = 10,
    stockSearchMaxLimit = 100,
    stockSearchTimeoutMs = 30000,
  } = options;

  app.get("/api/health", (_req, res) => sendSuccess(
    res,
    typeof getHealthSnapshot === "function"
      ? getHealthSnapshot()
      : { status: "ok", timestamp: nowIso() }
  ));

  app.get("/api/dashboard/ui-config", (_req, res) => sendSuccess(
    res,
    typeof getDashboardUiConfig === "function"
      ? getDashboardUiConfig()
      : { tableUi: null }
  ));

  app.get("/api/dashboard/access-info", (_req, res) => sendSuccess(
    res,
    typeof options.getAccessInfo === "function"
      ? options.getAccessInfo()
      : {
          serverBaseUrl: "",
          publicBaseUrl: "",
          publicHealthUrl: "",
          environment: "",
        }
  ));

  app.get("/api/dashboard/resource-status", (req, res) => {
    try {
      const keys = String(req.query.keys || "")
        .split(",")
        .map((item) => String(item || "").trim())
        .filter(Boolean);
      return sendSuccess(
        res,
        typeof getDashboardResourceStatus === "function"
          ? getDashboardResourceStatus(keys)
          : {}
      );
    } catch (error) {
      return sendError(res, error, 500, {});
    }
  });

  app.get("/api/merger/reports/today", async (_req, res) => {
    try {
      const { date, groups } = await getTodayMergerGroups();
      const items = Array.from(groups.values()).map((rows) => {
        const first = rows[0] || {};
        const code = mergerCompanyCode(first);
        const name = mergerCompanyName(first);
        const report = getMergerReportByCompany({ date, code, name });
        return {
          date,
          code,
          name,
          key: mergerCompanyKey({ date, code, name }),
          announcementCount: rows.length,
          announcements: rows.map((row) => ({
            title: pickText(row.title || row.announcementTitle),
            date: mergerAnnouncementDate(row),
            url: pickText(row.announcementUrl || row.url || row.link, ""),
          })),
          hasReport: Boolean(report?.reportMarkdown),
          updatedAt: report?.updatedAt || null,
        };
      });
      return sendSuccess(res, items, { total: items.length, date });
    } catch (error) {
      return sendError(res, error, 500, []);
    }
  });

  app.get("/api/merger/report", async (req, res) => {
    try {
      const date = normalizeDateText(req.query.date || getShanghaiParts().date);
      const code = String(req.query.code || "").trim();
      const name = String(req.query.name || "").trim();
      if (!code && !name) return sendError(res, "缺少公司标识，code 或 name 至少填写一个", 400, null);
      const report = getMergerReportByCompany({ date, code, name });
      if (!report) return sendError(res, "数据库中暂无该公司当日报告", 404, null);
      return sendSuccess(res, report);
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.post("/api/merger/report/generate", async (req, res) => {
    try {
      const body = req.body && typeof req.body === "object" ? req.body : {};
      const date = normalizeDateText(body.date || getShanghaiParts().date);
      const code = String(body.code || "").trim();
      const name = String(body.name || "").trim();
      const force = Boolean(body.force);
      if (!code && !name) return sendError(res, "缺少公司标识，code 或 name 至少填写一个", 400, null);
      return sendSuccess(res, await ensureMergerCompanyReport({ date, code, name, force }));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.get("/api/market/overview", async (_req, res) => {
    try {
      const monitors = await getAllMonitors();
      const datasets = await Promise.all([
        getDataset("ah"),
        getDataset("ab"),
        getDataset("ipo"),
        getDataset("bonds"),
        getDataset("merger"),
      ]);
      return sendServiceResult(res, getOverviewFromDatasets({
        ah: datasets[0],
        ab: datasets[1],
        ipo: datasets[2],
        bonds: datasets[3],
        merger: datasets[4],
        monitors,
      }));
    } catch (error) {
      return sendError(res, error);
    }
  });

  app.get("/api/monitors", async (req, res) => {
    try {
      const refreshPrices = String(req.query.refresh ?? "1") !== "0";
      const rows = await getAllMonitors({ refreshPrices });
      return sendSuccess(res, rows, { total: rows.length, updateTime: nowIso() });
    } catch (error) {
      return sendError(res, error, 500, []);
    }
  });

  app.post("/api/monitors", async (req, res) => {
    try {
      if (!req.body || typeof req.body !== "object") return sendError(res, "请求体必须为 JSON 对象", 400);
      return sendSuccess(res, await upsertMonitor(req.body || {}));
    } catch (error) {
      return sendError(res, error, 400);
    }
  });

  app.delete("/api/monitors/:id", async (req, res) => {
    try {
      const id = String(req.params.id || "").trim();
      if (!id) return sendError(res, "id 不能为空", 400, []);
      const rows = await deleteMonitor(id);
      return sendSuccess(res, rows, { total: rows.length });
    } catch (error) {
      return sendError(res, error, 500, []);
    }
  });

  app.get("/api/dividend", async (req, res) => {
    try {
      const action = String(req.query.action || "portfolio");
      if (action === "portfolio") {
        const rows = loadPortfolio();
        return sendSuccess(res, rows, { total: rows.length });
      }
      if (action === "upcoming") {
        const days = Number(req.query.days || dividendUpcomingDefaultDays);
        if (!Number.isFinite(days) || days < 1 || days > dividendUpcomingMaxDays) {
          return sendError(res, `days 必须是 1-${dividendUpcomingMaxDays} 的数字`, 400, []);
        }
        const rows = upcomingDividends(days);
        return sendSuccess(res, rows, { total: rows.length });
      }
      if (action === "refresh") {
        const rows = await refreshPortfolio();
        return sendSuccess(res, rows, { total: rows.length });
      }
      if (action === "search") {
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
      }
      return sendError(res, "不支持的 action", 400);
    } catch (error) {
      return sendError(res, error);
    }
  });

  app.post("/api/dividend", async (req, res) => {
    try {
      if (!req.body || typeof req.body !== "object") return sendError(res, "请求体必须为 JSON 对象", 400);
      const rows = await addDividendStock(req.body || {});
      return sendSuccess(res, rows, { total: rows.length });
    } catch (error) {
      return sendError(res, error, 400);
    }
  });

  app.delete("/api/dividend/:code", (req, res) => {
    try {
      const code = String(req.params.code || "").trim();
      if (!code) return sendError(res, "code 不能为空", 400, []);
      const rows = removeDividendStock(code);
      return sendSuccess(res, rows, { total: rows.length });
    } catch (error) {
      return sendError(res, error, 500, []);
    }
  });
}

module.exports = {
  registerDashboardRoutes,
};

