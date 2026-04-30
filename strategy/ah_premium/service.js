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
