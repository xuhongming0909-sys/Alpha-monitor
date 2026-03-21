"use strict";

/**
 * 推送接口路由。
 * 把配置读写和人工触发入口统一放到展示层 API，主入口只负责装配依赖。
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
    pushMergerReportToWeCom,
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

  app.post("/api/push/wecom", async (req, res) => {
    try {
      const modules = req.body && typeof req.body === "object" ? req.body.modules : undefined;
      return sendSuccess(res, await pushByModulesToWeCom({ modules }));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });

  app.post("/api/push/wecom/merger-report", async (req, res) => {
    try {
      const force = Boolean(req.body && typeof req.body === "object" && req.body.force);
      return sendSuccess(res, await pushMergerReportToWeCom({ force }));
    } catch (error) {
      return sendError(res, error, 500, null);
    }
  });
}

module.exports = {
  registerPushRoutes,
};

