// AI-SUMMARY: 并购套利 Node 适配器：报告生成调度
// 对应 INDEX.md §9 文件摘要索引

"use strict";

function createMergerStrategy(options = {}) {
  const normalizeDateText = options.normalizeDateText || ((value) => String(value || "").trim().slice(0, 10));
  const pickText = options.pickText || ((value, fallback = "--") => {
    const text = String(value ?? "").trim();
    return text || fallback;
  });

  function mergerAnnouncementDate(row) {
    return normalizeDateText(row?.announcementDate || row?.date || row?.publishDate);
  }

  function mergerCompanyCode(row) {
    return pickText(row?.secCode || row?.code || row?.targetCode, "");
  }

  function mergerCompanyName(row) {
    return pickText(row?.secName || row?.targetName || row?.name, "");
  }

  function mergerCompanyKey({ date, code, name }) {
    return `${normalizeDateText(date)}|${pickText(code, "--")}|${pickText(name, "--")}`;
  }

  function groupTodayMergerRowsByCompany(mergerRows, date) {
    const groups = new Map();
    for (const row of Array.isArray(mergerRows) ? mergerRows : []) {
      const announcementDate = mergerAnnouncementDate(row);
      if (announcementDate !== date) continue;
      const code = mergerCompanyCode(row);
      const name = mergerCompanyName(row);
      const key = mergerCompanyKey({ date, code, name });
      const list = groups.get(key) || [];
      list.push(row);
      groups.set(key, list);
    }
    return groups;
  }

  return {
    mergerAnnouncementDate,
    mergerCompanyCode,
    mergerCompanyName,
    mergerCompanyKey,
    groupTodayMergerRowsByCompany,
  };
}

module.exports = {
  createMergerStrategy,
};


