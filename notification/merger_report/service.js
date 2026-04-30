// AI-SUMMARY: 并购报告推送：DeepSeek AI 报告生成与推送
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * merger_report推送服务。
 * 负责生成单家公司并购简报，并按wecom逐家公司推送。
 */

function createMergerReportService(options = {}) {
  const nowIso = options.nowIso || (() => new Date().toISOString());
  const sendMarkdown = options.sendMarkdown;
  const getTodayMergerGroups = options.getTodayMergerGroups;
  const getMergerReportByCompany = options.getMergerReportByCompany;
  const upsertMergerReportByCompany = options.upsertMergerReportByCompany;
  const normalizeDateText = options.normalizeDateText;
  const pickText = options.pickText;
  const mergerCompanyCode = options.mergerCompanyCode;
  const mergerCompanyName = options.mergerCompanyName;
  const mergerAnnouncementDate = options.mergerAnnouncementDate;
  const normalizeError = options.normalizeError;
  const reportMaxChars = options.reportMaxChars || 500;
  const promptTemplateCode = options.promptTemplateCode || "MERGER_DEAL_OVERVIEW_V1";
  const deepseekApiKey = String(options.deepseekApiKey || "").trim();
  const deepseekBaseUrl = String(options.deepseekBaseUrl || "https://api.deepseek.com").trim();
  const aiModel = String(options.aiModel || "deepseek-chat").trim();
  const fetchImpl = options.fetchImpl || globalThis.fetch;

  async function callDeepSeekChatCompletion({ systemPrompt, userPrompt, temperature = 0.2 }) {
    if (!deepseekApiKey) {
      throw new Error("未配置 DEEPSEEK_API_KEY");
    }
    const response = await fetchImpl(`${deepseekBaseUrl.replace(/\/$/, "")}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${deepseekApiKey}`,
      },
      body: JSON.stringify({
        model: aiModel,
        temperature,
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
      }),
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    const content = payload?.choices?.[0]?.message?.content;
    if (!response.ok || !content) {
      const message = payload?.error?.message || payload?.message || "DeepSeek 返回异常";
      throw new Error(`DeepSeek 分析失败: ${message}`);
    }
    return String(content || "").trim();
  }

  function buildMergerCompanyQuestionPrompt(company, rows, date) {
    const first = rows[0] || {};
    const dealType = pickText(first.dealType || first.type, "--");
    const sourceHints = rows
      .slice(0, 5)
      .map((row) => pickText(row.announcementUrl || row.url || row.link, ""))
      .filter(Boolean)
      .join("；");

    return [
      `模板代码:${promptTemplateCode}。`,
      "你是并购事实核验分析师。请先联网搜索并交叉验证（公司公告、交易所、主流财经媒体），不得臆测或编造。",
      `公司:${pickText(company.name)}(${pickText(company.code)}) 截止日期:${date} 交易类型:${dealType}`,
      "只做两件事：介绍这笔交易 + 说明交易对价。",
      `线索链接:${sourceHints || "无"}`,
      "按固定字段输出：",
      "【交易介绍】收购方、被收购方、交易对象、交易方式（如要约收购/资产收购等）、当前交易状态。",
      "【交易对价】总对价、单价、现金与换股安排（含换股比例）、支付安排与生效条件；未披露项明确写“未披露”。",
      "【信息来源】列出1-2条可核验链接。",
      `必须中文，信息完整，回答总长度不超过${reportMaxChars}字。`,
    ].join(" ");
  }

  function buildMergerCompanySnapshot(rows) {
    return JSON.stringify(
      rows.map((row) => ({
        t: pickText(row.title || row.announcementTitle, ""),
        d: mergerAnnouncementDate(row),
        p: Number(row.stockPrice || row.price),
        o: Number(row.offerPrice || row.bidPrice),
        u: pickText(row.announcementUrl || row.url || row.link, ""),
      }))
    );
  }

  async function buildMergerCompanyReportMarkdown(company, rows, date) {
    const questionPrompt = buildMergerCompanyQuestionPrompt(company, rows, date);
    let content = await callDeepSeekChatCompletion({
      systemPrompt: `你是严谨的并购信息分析师。严格按用户给定模板代码与字段顺序作答，只输出“交易介绍”和“交易对价”相关信息，不要扩展到套利、风险或公告解读。最终回答必须为中文，且总长度不超过${reportMaxChars}字。`,
      userPrompt: questionPrompt,
      temperature: 0.2,
    });

    let conciseContent = String(content || "").trim();
    if (Array.from(conciseContent).length > reportMaxChars) {
      content = await callDeepSeekChatCompletion({
        systemPrompt: "你是金融编辑，负责在不丢失关键信息的前提下做压缩改写。",
        userPrompt: `请将以下内容压缩改写为中文，仅保留“交易介绍”和“交易对价”核心信息，不要新增事实，严格控制在${reportMaxChars}字以内：\n${conciseContent}`,
        temperature: 0.1,
      });
      conciseContent = String(content || "").trim();
    }

    return {
      markdown: `# 并购公司报告：${pickText(company.name)}(${pickText(company.code)})\n> ${new Date().toLocaleString("zh-CN", { hour12: false })}\n\n${conciseContent}`,
      questionPrompt,
    };
  }

  async function ensureMergerCompanyReport({ date, code, name, force = false }) {
    const { date: today, groups } = await getTodayMergerGroups();
    const reportDate = normalizeDateText(date || today) || today;
    const company = { code: pickText(code, "--"), name: pickText(name, "--") };
    const groupKey = `${reportDate}|${pickText(company.code, "--")}|${pickText(company.name, "--")}`;
    let rows = groups.get(groupKey) || [];

    if (!rows.length) {
      const wantedCode = String(company.code || "").trim().toLowerCase();
      const wantedName = String(company.name || "").trim().toLowerCase();
      for (const list of groups.values()) {
        const first = list[0] || {};
        const currentCode = String(mergerCompanyCode(first) || "").trim().toLowerCase();
        const currentName = String(mergerCompanyName(first) || "").trim().toLowerCase();
        if ((wantedCode && currentCode === wantedCode) || (wantedName && currentName === wantedName)) {
          rows = list;
          break;
        }
      }
    }

    if (!rows.length) {
      throw new Error("未找到该公司当日merger，无法生成报告");
    }

    const canonical = rows[0] || {};
    company.code = mergerCompanyCode(canonical) || company.code;
    company.name = mergerCompanyName(canonical) || company.name;

    const snapshot = buildMergerCompanySnapshot(rows);
    const existing = getMergerReportByCompany({ date: reportDate, code: company.code, name: company.name });
    if (!force && existing && existing.reportMarkdown && existing.snapshot === snapshot) {
      return existing;
    }

    const built = await buildMergerCompanyReportMarkdown(company, rows, reportDate);
    return upsertMergerReportByCompany({
      date: reportDate,
      code: company.code,
      name: company.name,
      reportMarkdown: built.markdown_style,
      questionPrompt: built.questionPrompt,
      announcements: rows.map((row) => ({
        title: pickText(row.title || row.announcementTitle),
        date: mergerAnnouncementDate(row),
        url: pickText(row.announcementUrl || row.url || row.link, ""),
      })),
      snapshot,
      createdAt: existing?.createdAt || nowIso(),
    });
  }

  async function pushMergerReportsByCompanyToWeCom(optionsInput = {}) {
    const { date, groups } = await getTodayMergerGroups();
    const entries = Array.from(groups.entries());
    if (!entries.length) {
      return { date, totalCompanies: 0, sentCount: 0, failedCount: 0, items: [], failedItems: [] };
    }

    const items = [];
    const failedItems = [];

    for (const [key, rows] of entries) {
      const first = rows[0] || {};
      const code = mergerCompanyCode(first);
      const name = mergerCompanyName(first);
      try {
        const report = await ensureMergerCompanyReport({
          date,
          code,
          name,
          force: Boolean(optionsInput.force),
        });
        const payload = await sendMarkdown(report.reportMarkdown);
        items.push({
          key,
          date,
          code,
          name,
          errcode: payload.errcode,
          errmsg: payload.errmsg,
          sentAt: nowIso(),
          fallbackUsed: false,
        });
      } catch (error) {
        const fallback = getMergerReportByCompany({ date, code, name });
        if (fallback?.reportMarkdown) {
          try {
            const payload = await sendMarkdown(fallback.reportMarkdown);
            items.push({
              key,
              date,
              code,
              name,
              errcode: payload.errcode,
              errmsg: payload.errmsg,
              sentAt: nowIso(),
              fallbackUsed: true,
              fallbackReason: normalizeError(error),
            });
            continue;
          } catch (fallbackError) {
            failedItems.push({
              key,
              date,
              code,
              name,
              error: `生成失败：${normalizeError(error)}；兜底推送失败：${normalizeError(fallbackError)}`,
            });
            continue;
          }
        }

        failedItems.push({
          key,
          date,
          code,
          name,
          error: normalizeError(error),
        });
      }
    }

    return {
      date,
      totalCompanies: entries.length,
      sentCount: items.length,
      failedCount: failedItems.length,
      items,
      failedItems,
      latestSentAt: items[items.length - 1]?.sentAt || null,
    };
  }

  return {
    callDeepSeekChatCompletion,
    buildMergerCompanyQuestionPrompt,
    buildMergerCompanySnapshot,
    buildMergerCompanyReportMarkdown,
    ensureMergerCompanyReport,
    pushMergerReportsByCompanyToWeCom,
  };
}

module.exports = {
  createMergerReportService,
};


