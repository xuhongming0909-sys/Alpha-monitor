// AI-SUMMARY: 路径解析（JS）：运行时目录、数据库路径
// 对应 INDEX.md §9 文件摘要索引

"use strict";

/**
 * Node 侧统一路径策略。
 * 这里只负责把配置合同转换成稳定路径，不再承担旧目录回退。
 */

const fs = require("fs");
const path = require("path");
const { getConfig, ROOT_DIR } = require("../config/node_config");

function slugify(value, fallback = "local") {
  const normalized = String(value || "")
    .trim()
    .replace(/[^A-Za-z0-9._-]+/g, "-")
    .replace(/^[.-]+|[.-]+$/g, "");
  return normalized || fallback;
}

function resolveFromRoot(relativePath, fallbackRelativePath) {
  const candidate = String(relativePath || "").trim();
  const target = candidate || fallbackRelativePath;
  return path.resolve(ROOT_DIR, target);
}

function getPathPolicy() {
  const config = getConfig();
  const storage = config.storage || {};
  const dataRootDir = resolveFromRoot(storage.data_root_dir, "runtime_data");
  const sharedDataDir = resolveFromRoot(storage.shared_data_dir, "runtime_data/shared");
  const runtimeProfileDir = resolveFromRoot(storage.runtime_profile_dir, "runtime_data/profiles");
  const dbProfile = slugify(storage.db_profile || "shared");
  const runtimeDataDir = dbProfile === "shared"
    ? sharedDataDir
    : path.join(runtimeProfileDir, dbProfile);

  return {
    rootDir: ROOT_DIR,
    dataRootDir,
    sharedDataDir,
    runtimeProfileDir,
    dbProfile,
    runtimeDataDir,
    runtimeFiles: storage.runtime_files || {},
  };
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
  return dirPath;
}

function runtimeFilePath(filename, options = {}) {
  void options;
  const policy = getPathPolicy();
  const targetPath = path.join(policy.runtimeDataDir, filename);
  ensureDir(path.dirname(targetPath));
  return targetPath;
}

function sharedDbPath(filename) {
  const policy = getPathPolicy();
  const targetPath = path.join(policy.sharedDataDir, filename);
  ensureDir(path.dirname(targetPath));
  return targetPath;
}

module.exports = {
  slugify,
  getPathPolicy,
  ensureDir,
  runtimeFilePath,
  sharedDbPath,
};


