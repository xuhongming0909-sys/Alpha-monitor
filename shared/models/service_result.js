// AI-SUMMARY: 标准响应包装（JS）：成功/错误响应格式
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * 统一服务返回模型。
 * 目标是让 Node 侧的服务层都返回相同的 success / data / error 结构。
 */

function nowIso() {
  return new Date().toISOString();
}

function normalizeError(error) {
  if (!error) return "Unknown error";
  if (typeof error === "string") return error;
  return error instanceof Error ? error.message || "Unknown error" : String(error);
}

function buildSuccess(data = null, extra = {}) {
  return {
    success: true,
    data,
    error: null,
    updateTime: extra.updateTime || nowIso(),
    ...extra,
  };
}

function buildError(error, data = null, extra = {}) {
  return {
    success: false,
    data,
    error: normalizeError(error),
    updateTime: extra.updateTime || nowIso(),
    ...extra,
  };
}

function isServiceResult(value) {
  return Boolean(value && typeof value === "object" && Object.prototype.hasOwnProperty.call(value, "success"));
}

module.exports = {
  nowIso,
  normalizeError,
  buildSuccess,
  buildError,
  isServiceResult,
};
