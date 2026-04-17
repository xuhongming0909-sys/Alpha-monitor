"use strict";

function buildPushConfigResponse(config, runtimeState = {}, deliveryStatus = {}, premiumMonitorStatus = {}) {
  const modules = (config?.modules && typeof config.modules === "object") ? config.modules : {};
  const selectedModules = Object.entries(modules)
    .filter(([, enabled]) => Boolean(enabled))
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
