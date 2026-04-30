// AI-SUMMARY: 推送配置响应格式：推送配置数据结构整形
// 对应 INDEX.md §9 文件摘要索引

"use strict";

function buildPushConfigResponse(config, runtimeState = {}, deliveryStatus = {}, premiumMonitorStatus = {}) {
  const modules = (config?.modules && typeof config.modules === "object") ? config.modules : {};
  const selectedModules = Object.entries(modules)
    .filter(([key, enabled]) => key !== "cbArb" && Boolean(enabled))
    .map(([key]) => key);

  return {
    ...config,
    times: config?.times,
    lastMainPushDate: runtimeState?.lastMainPushDate || null,
    premiumMonitorStatus,
    deliveryStatus: {
      webhookConfigured: Boolean(deliveryStatus?.webhookConfigured),
      pushHtmlUrlConfigured: Boolean(deliveryStatus?.pushHtmlUrlConfigured),
      schedulerEnabled: deliveryStatus?.schedulerEnabled !== false,
      schedulerDisabledReason: deliveryStatus?.schedulerDisabledReason || null,
      calendarMode: deliveryStatus?.calendarMode || null,
      selectedModules,
      lastMainPushAttemptAt: runtimeState?.lastMainPushAttemptAt || null,
      lastMainPushSuccessAt: runtimeState?.lastMainPushSuccessAt || null,
      lastMainPushError: runtimeState?.lastMainPushError || null,
    },
  };
}

module.exports = {
  buildPushConfigResponse,
};
