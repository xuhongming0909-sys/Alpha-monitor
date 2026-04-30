"use strict";

const { pickTopRowsByField, pickBottomRowsByField } = require("../../shared/utils/ranking");

function buildOverviewViewModel(options = {}) {
  const ahRows = Array.isArray(options?.ah?.data) ? options.ah.data : [];
  const abRows = Array.isArray(options?.ab?.data) ? options.ab.data : [];
  const mergerRows = Array.isArray(options?.merger?.data) ? options.merger.data : [];
  const monitors = Array.isArray(options?.monitors) ? options.monitors : [];
  const today = String(options.today || new Date().toISOString().split("T")[0]);
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : (() => new Date().toISOString());
  const summarizeMonitor = typeof options.summarizeMonitor === "function" ? options.summarizeMonitor : ((item) => item);

  return {
    success: true,
    data: {
      updateTime: nowIso(),
      ah: {
        highestPremium: pickTopRowsByField(ahRows, "premium", 5),
        lowestPremium: pickBottomRowsByField(ahRows, "premium", 5),
      },
      ab: {
        lowestPremium: pickBottomRowsByField(abRows, "premium", 5),
      },
      subscriptions: {
        ipo: Array.isArray(options?.ipo?.upcoming) ? options.ipo.upcoming.slice(0, 5) : [],
        bonds: Array.isArray(options?.bonds?.upcoming) ? options.bonds.upcoming.slice(0, 5) : [],
      },
      merger: mergerRows.filter((row) => row.announcementDate === today).slice(0, 5),
      monitors: monitors.map(summarizeMonitor).sort((a, b) => (b.maxYieldRate || -999) - (a.maxYieldRate || -999)).slice(0, 5),
    },
  };
}

module.exports = {
  buildOverviewViewModel,
};


