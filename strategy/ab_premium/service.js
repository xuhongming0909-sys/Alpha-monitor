"use strict";

/**
 * AB 溢价策略只负责本插件自己的排序口径。
 * 这里直接保留一份本地实现，避免跨插件引用。
 */
function pickTopPremiumRows(rows, count = 5) {
  return [...(Array.isArray(rows) ? rows : [])]
    .sort((a, b) => (Number(b?.premium) || -999) - (Number(a?.premium) || -999))
    .slice(0, count);
}

function pickBottomPremiumRows(rows, count = 5) {
  return [...(Array.isArray(rows) ? rows : [])]
    .sort((a, b) => (Number(a?.premium) || 999) - (Number(b?.premium) || 999))
    .slice(0, count);
}

module.exports = {
  pickTopPremiumRows,
  pickBottomPremiumRows,
};
