// AI-SUMMARY: 企业微信客户端：发送 Markdown 到 Webhook
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * wecom发送client。
 * 这里只负责把已经准备好的 Markdown 推送出去。
 */

const { appendHtmlLinkForPush, trimMarkdownForWeCom } = require("../styles/markdown_style");

function createWeComClient(options = {}) {
  const fetchImpl = options.fetchImpl || globalThis.fetch;

  if (typeof fetchImpl !== "function") {
    throw new Error("当前环境缺少 fetch，无法发送wecom消息");
  }

  async function sendMarkdown(markdown) {
    const webhookUrl = String(options.webhookUrl || "").trim();
    if (!webhookUrl) {
      throw new Error("未配置 WECOM_WEBHOOK_URL");
    }

    const markdownWithLink = appendHtmlLinkForPush(markdown, options.pushHtmlUrl);
    const safeMarkdown = trimMarkdownForWeCom(markdownWithLink, options.maxLength || 3900);
    const response = await fetchImpl(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        msgtype: "markdown",
        markdown: { content: safeMarkdown },
      }),
    });

    let payload = null;
    try {
      payload = await response.json();
    } catch {
      payload = { errcode: -1, errmsg: "Webhook response is not JSON" };
    }

    if (!response.ok || Number(payload?.errcode) !== 0) {
      throw new Error(
        `wecom推送失败: HTTP ${response.status}, errcode=${payload?.errcode}, errmsg=${payload?.errmsg || ""}`
      );
    }
    return payload;
  }

  return {
    sendMarkdown,
    trimMarkdownForWeCom,
    appendHtmlLinkForPush,
  };
}

module.exports = {
  createWeComClient,
};


