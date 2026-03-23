"use strict";

function buildPushConfigResponse(config, runtimeState = {}, deliveryStatus = {}) {
  const modules = (config?.modules && typeof config.modules === "object") ? config.modules : {};
  const selectedModules = Object.entries(modules)
    .filter(([, enabled]) => Boolean(enabled))
    .map(([key]) => key);

  return {
    ...config,
    times: config?.times,
    eventAlert: config?.eventAlert,
    lastMainPushDate: runtimeState?.lastMainPushDate || null,
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
      lastEventAlertAttemptAt: runtimeState?.lastEventAlertAttemptAt || null,
      lastEventAlertSuccessAt: runtimeState?.lastEventAlertSuccessAt || null,
      lastEventAlertError: runtimeState?.lastEventAlertError || null,
    },
  };
}

module.exports = {
  buildPushConfigResponse,
};
