"use strict";

function buildPushConfigResponse(config, runtimeState = {}, deliveryStatus = {}) {
  const modules = (config?.modules && typeof config.modules === "object") ? config.modules : {};
  const selectedModules = Object.entries(modules)
    .filter(([, enabled]) => Boolean(enabled))
    .map(([key]) => key);

  return {
    ...config,
    times: config?.times,
    mergerSchedule: config?.mergerSchedule,
    lastMainPushDate: runtimeState?.lastMainPushDate || null,
    lastMergerReportDate: runtimeState?.lastMergerReportDate || null,
    deliveryStatus: {
      webhookConfigured: Boolean(deliveryStatus?.webhookConfigured),
      schedulerEnabled: deliveryStatus?.schedulerEnabled !== false,
      calendarMode: deliveryStatus?.calendarMode || null,
      selectedModules,
      lastMainPushAttemptAt: runtimeState?.lastMainPushAttemptAt || null,
      lastMainPushSuccessAt: runtimeState?.lastMainPushSuccessAt || null,
      lastMainPushError: runtimeState?.lastMainPushError || null,
      lastMergerPushAttemptAt: runtimeState?.lastMergerPushAttemptAt || null,
      lastMergerPushSuccessAt: runtimeState?.lastMergerPushSuccessAt || null,
      lastMergerPushError: runtimeState?.lastMergerPushError || null,
    },
  };
}

module.exports = {
  buildPushConfigResponse,
};
