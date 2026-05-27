"use strict";
// LOF IOPV 推送服务 - 重写版
// 推送条件：限购金额存在 AND 溢价率 > 2%
// 推送内容：代码 名称 溢价率 限购金额

function createLofIopvPushService(options = {}) {
  const getConfig = typeof options.getConfig === "function" ? options.getConfig : () => ({ enabled: false, times: [] });
  const runtimeStore = options.runtimeStore;
  const getDataset = options.getDataset;
  const sendMarkdown = options.sendMarkdown;
  const getShanghaiParts = options.getShanghaiParts;
  const parsePushMinutes = options.parsePushMinutes;
  const isTradingWeekday = typeof options.isTradingWeekday === "function" ? options.isTradingWeekday : () => true;
  const isDeliveryAvailable = typeof options.isDeliveryAvailable === "function" ? options.isDeliveryAvailable : () => true;
  const nowIso = typeof options.nowIso === "function" ? options.nowIso : () => new Date().toISOString();
  const logInfo = options.logInfo || ((msg) => console.info(msg));
  const logError = options.logError || ((scope, err) => console.error(scope, err));

  // 推送筛选：有限购金额 + 溢价率 > 2%
  function filterPushRows(rows) {
    if (!rows || !Array.isArray(rows)) return [];
    return rows.filter(r => {
      const premium = r.premiumRate;
      const minAmt = r.minAmt;
      if (premium === null || premium === undefined) return false;
      if (minAmt === null || minAmt === undefined || minAmt === "" || minAmt === 0) return false;
      return premium > 2.0;
    });
  }

  // 构建推送Markdown
  function buildPushMarkdown(rows) {
    if (!rows || rows.length === 0) return null;
    let md = "**LOF限购套利提醒**\n\n";
    md += "| 代码 | 名称 | 溢价率 | 限购金额 |\n";
    md += "|------|------|--------|----------|\n";
    for (const r of rows) {
      const code = r.code || "";
      const name = r.name || "";
      const premium = r.premiumRate !== null ? r.premiumRate.toFixed(2) + "%" : "-";
      const amt = r.minAmt ? r.minAmt + "万" : "-";
      md += `| ${code} | ${name} | ${premium} | ${amt} |\n`;
    }
    md += `\n共${rows.length}只 | ${new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" })}`;
    return md;
  }

  async function pushNow(dataset) {
    const rows = (dataset && dataset.rows) || [];
    const filtered = filterPushRows(rows);
    if (filtered.length === 0) {
      logInfo("[push][lof_iopv] 无符合条件的基金（需有限购+溢价>2%）");
      return;
    }
    const md = buildPushMarkdown(filtered);
    if (!md) return;
    try {
      await sendMarkdown(md);
      logInfo(`[push][lof_iopv] 推送成功: ${filtered.length}只`);
    } catch (err) {
      logError("[push][lof_iopv] 推送失败:", err);
    }
  }

  async function runIfNeeded() {
    const cfg = getConfig();
    if (!cfg.enabled) return;
    if (!isTradingWeekday()) return;

    const now = new Date();
    const parts = getShanghaiParts(now);
    const hhmm = `${String(parts.hour).padStart(2, "0")}${String(parts.minute).padStart(2, "0")}`;
    const pushMinutes = parsePushMinutes(cfg.times || []);

    if (!pushMinutes.includes(Number(hhmm))) return;

    const sentTimes = runtimeStore.getSentTimes ? runtimeStore.getSentTimes(parts.dateStr) : [];
    if (sentTimes.includes(hhmm)) return;

    try {
      if (!isDeliveryAvailable()) return;
      const dataset = await getDataset();
      await pushNow(dataset);

      sentTimes.push(hhmm);
      if (runtimeStore.setPushRecord) runtimeStore.setPushRecord(parts.dateStr, sentTimes);
      if (runtimeStore.save) runtimeStore.save();
    } catch (err) {
      logError("[push][lof_iopv] error:", err);
    }
  }

  return { pushNow, runIfNeeded };
}

module.exports = { createLofIopvPushService };