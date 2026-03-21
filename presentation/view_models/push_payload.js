"use strict";

function buildPushConfigResponse(config, runtimeState = {}) {
  return {
    ...config,
    times: config?.times,
    mergerSchedule: config?.mergerSchedule,
    lastMainPushDate: runtimeState?.lastMainPushDate || null,
    lastMergerReportDate: runtimeState?.lastMergerReportDate || null,
  };
}

module.exports = {
  buildPushConfigResponse,
};
