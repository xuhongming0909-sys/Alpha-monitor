// AI-SUMMARY: 每日摘要组装：聚合所有模块生成推送 Markdown
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * 定时摘要推送服务。
 * 负责收集摘要数据、拼装 Markdown，并调用发送器发送。
 */
function createMainSummaryService(options = {}) {
  const collectSummaryDatasets = options.collectSummaryDatasets;
  const buildSummaryMarkdown = options.buildSummaryMarkdown;
  const sendMarkdown = options.sendMarkdown;
  const getPushConfig = options.getPushConfig;
  const normalizePushConfig = options.normalizePushConfig;
  const nowIso = options.nowIso || (() => new Date().toISOString());

  async function pushSummaryToWeCom(input = {}) {
    const datasets = await collectSummaryDatasets();
    const modules = normalizePushConfig({ modules: input.modules || getPushConfig().modules }).modules;
    const markdown = buildSummaryMarkdown(datasets, modules);
    const payload = await sendMarkdown(markdown);
    return {
      sentAt: nowIso(),
      errcode: payload.errcode,
      errmsg: payload.errmsg,
      markdown,
      modules,
    };
  }

  async function pushByModulesToWeCom(input = {}) {
    const normalizedModules = normalizePushConfig({ modules: input.modules || getPushConfig().modules }).modules;
    const hasSummaryModules = Object.entries(normalizedModules).some(([, enabled]) => Boolean(enabled));
    if (!hasSummaryModules) {
      throw new Error("请至少选择一个推送模块");
    }

    const summary = await pushSummaryToWeCom({ modules: normalizedModules });
    return {
      sentAt: nowIso(),
      modules: normalizedModules,
      summary,
      summarySent: Boolean(summary),
    };
  }

  return {
    pushSummaryToWeCom,
    pushByModulesToWeCom,
  };
}

module.exports = {
  createMainSummaryService,
};
