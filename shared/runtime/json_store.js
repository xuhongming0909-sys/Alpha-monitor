"use strict";

/**
 * 统一的 JSON 运行态读写层。
 * 这里专门处理“运行态状态文件”的读取、写入与更新，避免各入口重复实现。
 */

const fs = require("fs");
const path = require("path");
const { ensureDir } = require("../paths/node_paths");

function cloneFallback(value) {
  if (Array.isArray(value)) return value.map(cloneFallback);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, cloneFallback(item)]));
  }
  return value;
}

function readJson(filePath, fallbackValue = null) {
  try {
    if (!fs.existsSync(filePath)) return cloneFallback(fallbackValue);
    const text = fs.readFileSync(filePath, "utf8");
    return text.trim() ? JSON.parse(text) : cloneFallback(fallbackValue);
  } catch {
    return cloneFallback(fallbackValue);
  }
}

function writeJson(filePath, data, options = {}) {
  const spaces = Number.isFinite(Number(options.spaces)) ? Number(options.spaces) : 2;
  const dirPath = path.dirname(filePath);
  ensureDir(dirPath);
  const payload = JSON.stringify(data, null, spaces);
  const tempPath = path.join(dirPath, `.${path.basename(filePath)}.${process.pid}.${Date.now()}.tmp`);
  fs.writeFileSync(tempPath, payload, "utf8");
  fs.renameSync(tempPath, filePath);
  return data;
}

function updateJson(filePath, fallbackValue, updater, options = {}) {
  const current = readJson(filePath, fallbackValue);
  const next = typeof updater === "function" ? updater(current) : current;
  writeJson(filePath, next, options);
  return next;
}

module.exports = {
  cloneFallback,
  readJson,
  writeJson,
  updateJson,
};


