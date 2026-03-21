"use strict";

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
