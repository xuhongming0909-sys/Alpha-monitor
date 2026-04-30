"use strict";

/**
 * 按字段降序排列后取前 N 条。
 */
function pickTopRowsByField(rows, field, count = 5) {
  return [...(Array.isArray(rows) ? rows : [])]
    .sort((a, b) => (Number(b?.[field]) || -999) - (Number(a?.[field]) || -999))
    .slice(0, count);
}

/**
 * 按字段升序排列后取前 N 条。
 */
function pickBottomRowsByField(rows, field, count = 5) {
  return [...(Array.isArray(rows) ? rows : [])]
    .sort((a, b) => (Number(a?.[field]) || 999) - (Number(b?.[field]) || 999))
    .slice(0, count);
}

module.exports = {
  pickTopRowsByField,
  pickBottomRowsByField,
};
