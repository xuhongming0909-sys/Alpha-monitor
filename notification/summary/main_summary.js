"use strict";

/**
 * main_summary推送服务。
 * 负责把各模块摘要拼装为 Markdown，并调用推送client发送。
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
      throw new Error("请至少选择一个推送板块");
    }

    const summary = await pushSummaryToWeCom({ modules: normalizedModules });
    return {
      sentAt: nowIso(),
      modules: normalizedModules,
      summary,
      summarySent: Boolean(summary),
      mergerSentCount: 0,
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


