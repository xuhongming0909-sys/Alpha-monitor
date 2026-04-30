// AI-SUMMARY: 可转债套利推送：独立推送逻辑与格式化
// 对应 INDEX.md §9 文件摘要索引

"use strict";

function toNum(value) {
  return Number.isFinite(Number(value)) ? Number(value) : null;
}

function pickText(value, fallback = "") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function pickCode(row = {}) {
  return pickText(row.code || row.bondCode || row.secuCode || row.symbol);
}

function mergeRows(primary = {}, secondary = {}) {
  return {
    ...primary,
    ...secondary,
  };
}

function readRootPayload(result) {
  if (!result || typeof result !== "object") return {};
  if (Array.isArray(result.data)) return result;
  return result.data && typeof result.data === "object" ? result.data : result;
}

function readMainRows(payload = {}) {
  if (Array.isArray(payload.data)) return payload.data;
  if (Array.isArray(payload.rows)) return payload.rows;
  return [];
}

function readSmallRedemptionRows(payload = {}) {
  const section = payload.smallRedemption && typeof payload.smallRedemption === "object"
    ? payload.smallRedemption
    : {};
  if (Array.isArray(section.rows)) return section.rows;
  return [];
}

function readSummaryCandidateRows(payload = {}) {
  const summary = payload.summary && typeof payload.summary === "object" ? payload.summary : {};
  return Object.values(summary).flatMap((value) => (Array.isArray(value) ? value : []));
}

function buildCandidateRows(payload = {}) {
  const mainRows = readMainRows(payload);
  const smallRedemptionRows = readSmallRedemptionRows(payload);
  const summaryRows = readSummaryCandidateRows(payload);
  const rowMap = new Map();

  mainRows.forEach((row) => {
    const code = pickCode(row);
    if (code) rowMap.set(code, row);
  });

  const ordered = [];
  const seen = new Set();
  const smallRedemptionSet = new Set();

  smallRedemptionRows.forEach((row) => {
    const code = pickCode(row);
    if (code) smallRedemptionSet.add(code);
  });

  function pushRow(row, isSmallRedemption = false) {
    const code = pickCode(row);
    if (!code) return;
    if (seen.has(code)) {
      const index = ordered.findIndex((item) => pickCode(item) === code);
      if (index >= 0) {
        ordered[index] = {
          ...ordered[index],
          ...row,
          isSmallRedemption: ordered[index].isSmallRedemption || isSmallRedemption || smallRedemptionSet.has(code),
        };
      }
      return;
    }
    const merged = mergeRows(rowMap.get(code) || {}, row);
    ordered.push({
      ...merged,
      isSmallRedemption: isSmallRedemption || smallRedemptionSet.has(code),
    });
    seen.add(code);
  }

  summaryRows.forEach((row) => pushRow(row, false));
  smallRedemptionRows.forEach((row) => pushRow(row, true));

  return ordered;
}

function createCbArbitragePushService(options = {}) {
  const getConfig = typeof options.getConfig === "function" ? options.getConfig : () => ({ enabled: false, times: [] });
  const runtimeStore = options.runtimeStore;
  const getDataset = options.getDataset;
  const sendMarkdown = options.sendMarkdown;
  const buildMarkdown = options.buildMarkdown;
  const getShanghaiParts = options.getShanghaiParts;
  const parsePushMinutes = options.parsePushMinutes;
  const isTradingWeekday = typeof options.isTradingWeekday === "function" ? options.isTradingWeekday : () => true;
  const isDeliveryAvailable = typeof options.isDeliveryAvailable === "function" ? options.isDeliveryAvailable : () => true;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();
  const logInfo = options.logInfo || ((message) => console.info(message));
  const logError = options.logError || ((scope, error) => console.error(scope, error));

  async function readPayload() {
    const result = await getDataset("cbArb");
    if (!result || result.success === false) {
      throw new Error(result?.error || "cb_arbitrage_dataset_unavailable");
    }
    const payload = readRootPayload(result);
    return {
      rows: buildCandidateRows(payload),
      summary: payload.summary && typeof payload.summary === "object" ? payload.summary : {},
      smallRedemption: payload.smallRedemption && typeof payload.smallRedemption === "object" ? payload.smallRedemption : {},
      updateTime: result?.updateTime || payload?.updateTime || null,
    };
  }

  async function pushNow() {
    const payload = await readPayload();
    const total = payload.rows.length;
    if (!total) {
      return { success: false, skipped: true, reason: "empty_cb_arbitrage_candidates", total: 0 };
    }
    if (!isDeliveryAvailable()) {
      return { success: true, skipped: true, reason: "delivery_not_configured", total };
    }

    const attemptAt = nowIso();
    runtimeStore.setAttempt(attemptAt);
    runtimeStore.save();
    try {
      const markdown = buildMarkdown(payload, { mode: "scheduled" });
      await sendMarkdown(markdown);
      runtimeStore.setSuccess(attemptAt);
      runtimeStore.save();
      return { success: true, skipped: false, total, attemptAt };
    } catch (error) {
      runtimeStore.setError(attemptAt, error?.message || error);
      runtimeStore.save();
      throw error;
    }
  }

  async function runIfNeeded() {
    const config = getConfig();
    if (!config.enabled) return;
    if (config.tradingDaysOnly !== false && !isTradingWeekday()) return;

    const sh = getShanghaiParts();
    const scheduleTimes = runtimeStore.normalizePushTimes(config.times);
    if (!scheduleTimes.length) return;

    const sanitized = runtimeStore.sanitizeScheduledPushRecord(sh.date, scheduleTimes);
    const sentTimes = sanitized.times.slice();
    const nowMinutes = sh.hour * 60 + sh.minute;
    if (sanitized.changed) {
      runtimeStore.save();
      logInfo(`[push][cb_arbitrage] sanitized dirty records date=${sh.date} kept=${sentTimes.join(",") || "none"}`);
    }

    for (const timeText of scheduleTimes) {
      const targetMinutes = parsePushMinutes(timeText);
      if (targetMinutes === null) continue;
      if (nowMinutes < targetMinutes) {
        logInfo(`[push][cb_arbitrage] slot=${timeText} date=${sh.date} skipped=not_due_yet`);
        continue;
      }
      if (sentTimes.includes(timeText)) {
        logInfo(`[push][cb_arbitrage] slot=${timeText} date=${sh.date} skipped=already_sent`);
        continue;
      }

      logInfo(`[push][cb_arbitrage] slot=${timeText} date=${sh.date} action=attempt`);
      try {
        const result = await pushNow();
        if (result?.skipped) {
          logInfo(`[push][cb_arbitrage] slot=${timeText} date=${sh.date} skipped=${result.reason || "empty"}`);
          continue;
        }
        sentTimes.push(timeText);
        runtimeStore.setPushRecord(sh.date, sentTimes);
        runtimeStore.save();
        logInfo(`[push][cb_arbitrage] slot=${timeText} date=${sh.date} action=success`);
      } catch (error) {
        logInfo(`[push][cb_arbitrage] slot=${timeText} date=${sh.date} action=failed error=${error?.message || error}`);
        logError("[push][cb_arbitrage] schedule failed:", error?.message || error);
      }
    }
  }

  return {
    readPayload,
    pushNow,
    runIfNeeded,
  };
}

module.exports = {
  createCbArbitragePushService,
};
