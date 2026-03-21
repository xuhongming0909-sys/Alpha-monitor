"use strict";

function createDividendStrategy(options = {}) {
  const loadPortfolio = typeof options.loadPortfolio === "function" ? options.loadPortfolio : () => [];

  function upcomingDividends(days = 7) {
    const today = new Date();
    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const deadline = new Date();
    deadline.setDate(deadline.getDate() + days);
    const deadlineEnd = new Date(deadline.getFullYear(), deadline.getMonth(), deadline.getDate(), 23, 59, 59, 999);

    return loadPortfolio()
      .filter((row) => row.dividendData?.recordDate)
      .filter((row) => {
        const recordDate = new Date(row.dividendData.recordDate);
        return !Number.isNaN(recordDate.getTime()) && recordDate >= todayStart && recordDate <= deadlineEnd;
      })
      .sort((a, b) => String(a.dividendData.recordDate || "").localeCompare(String(b.dividendData.recordDate || "")))
      .map((row) => ({
        ...row,
        name: row.name || row.dividendData?.name || row.code,
      }));
  }

  return {
    upcomingDividends,
  };
}

module.exports = {
  createDividendStrategy,
};
