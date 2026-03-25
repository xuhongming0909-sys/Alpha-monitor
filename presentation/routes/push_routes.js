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
