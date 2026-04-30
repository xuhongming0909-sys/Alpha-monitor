// AI-SUMMARY: AB 溢价 Node 适配器：Python 计算结果转为 API 响应
// 对应 INDEX.md §9 文件摘要索引

"use strict";

const { pickTopRowsByField, pickBottomRowsByField } = require("../../shared/utils/ranking");

function pickTopPremiumRows(rows, count = 5) {
  return pickTopRowsByField(rows, "premium", count);
}

function pickBottomPremiumRows(rows, count = 5) {
  return pickBottomRowsByField(rows, "premium", count);
}

module.exports = {
  pickTopPremiumRows,
  pickBottomPremiumRows,
};
