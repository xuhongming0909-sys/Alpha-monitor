// AI-SUMMARY: 推送配置 API 路由：/api/push/* 端点定义
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * 推送接口路由。
 * 统一承接推送配置读写、手工摘要推送和手工异动推送入口。
 */
function registerPushRoutes(options = {}) {
  const {
    app,
    sendSuccess,
    sendError,
    getPushConfig,
    updatePushConfig,
    buildPushConfigResponse,
    getPushRuntimeState,
    pushByModulesToWeCom,
    pushEventAlertsToWeCom,
    getCbArbitragePushConfig,
    updateCbArbitragePushConfig,
    buildCbArbitragePushConfigResponse,
    getCbRightsIssuePushConfig,
    updateCbRightsIssuePushConfig,
    buildCbRightsIssuePushConfigResponse,
    getLofArbPushConfig,
    updateLofArbPushConfig,
    buildLofArbPushConfigResponse,
  } = options;

  app.get("/api/push/config", (_req, res) => {
    const config = getPushConfig();
    return sendSuccess(res, buildPushConfigResponse(config, getPushRuntimeState()));
  });

  app.post("/api/push/config", (req, res) => {
    try {
      const next = updatePushConfig(req.body || {});
      return sendSuccess(res, buildPushConfigResponse(next, getPushRuntimeState()));
    } catch (error) {
      return sendError(res, error, 400, null);
    }
  });

  app.get("/api/push/cb-arbitrage-config", (_req, res) => {
    try {
      return sendSuccess(res, buildCbArbitragePushConfigResponse(getCbArbitragePushConfig()));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.post("/api/push/cb-arbitrage-config", (req, res) => {
    try {
      const next = updateCbArbitragePushConfig(req.body || {});
      return sendSuccess(res, buildCbArbitragePushConfigResponse(next));
    } catch (error) {
      return sendError(res, error, 400, null);
    }
  });

  app.get("/api/push/cb-rights-issue-config", (_req, res) => {
    try {
      return sendSuccess(res, buildCbRightsIssuePushConfigResponse(getCbRightsIssuePushConfig()));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.post("/api/push/cb-rights-issue-config", (req, res) => {
    try {
      const next = updateCbRightsIssuePushConfig(req.body || {});
      return sendSuccess(res, buildCbRightsIssuePushConfigResponse(next));
    } catch (error) {
      return sendError(res, error, 400, null);
    }
  });

  app.get("/api/push/lof-arbitrage-config", (_req, res) => {
    try {
      return sendSuccess(res, buildLofArbPushConfigResponse(getLofArbPushConfig()));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.post("/api/push/lof-arbitrage-config", (req, res) => {
    try {
      const next = updateLofArbPushConfig(req.body || {});
      return sendSuccess(res, buildLofArbPushConfigResponse(next));
    } catch (error) {
      return sendError(res, error, 400, null);
    }
  });

  app.get("/api/push/rules", (_req, res) => {
    return sendSuccess(res, {
      links: [
        {
          name: "主摘要定时推送",
          type: "scheduled",
          times: ["08:00", "20:18"],
          modules: ["ahab", "subscription", "cb_arb", "custom_monitor", "dividend", "event_arbitrage"],
          channel: "wecom",
        },
        {
          name: "转债套利折价策略提醒",
          type: "realtime",
          session: "09:30 ~ 14:50",
          intervalMinutes: 10,
          buyThreshold: -2,
          sellThreshold: -0.5,
          conditions: ["已过转股日"],
          channel: "wecom",
        },
        {
          name: "转债抢权配售独立推送",
          type: "scheduled",
          times: ["08:00", "14:30"],
          tradingDaysOnly: true,
          channel: "wecom",
        },
        {
          name: "LOF 套利独立推送",
          type: "scheduled+instant",
          times: ["13:30", "14:00", "14:30"],
          tradingDaysOnly: true,
          channel: "wecom",
        },
        {
          name: "并购报告推送",
          type: "scheduled",
          times: ["00:00"],
          channel: "wecom",
        },
      ],
    });
  });

  app.post("/api/push/wecom", async (req, res) => {
    try {
      const modules = req.body && typeof req.body === "object" ? req.body.modules : undefined;
      return sendSuccess(res, await pushByModulesToWeCom({ modules }));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.post("/api/push/wecom/event-alerts", async (req, res) => {
    try {
      const force = Boolean(req.body && typeof req.body === "object" && req.body.force);
      return sendSuccess(res, await pushEventAlertsToWeCom({ force }));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });
}

module.exports = {
  registerPushRoutes,
};
