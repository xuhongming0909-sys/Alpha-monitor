"use strict";

const { getConfig } = require("../config/node_config");
const { runtimeFilePath } = require("../paths/node_paths");
const { readJson, writeJson } = require("./json_store");

/**
 * 运行态state_registry。
 * 统一管理运行态 JSON 文件的路径、读取和写入。
 */
function createStateRegistry(options = {}) {
  const config = options.config || getConfig();
  const runtimeFiles = (config?.storage?.runtime_files && typeof config.storage.runtime_files === "object")
    ? config.storage.runtime_files
    : {};

  function resolve(logicalKey, fallbackName) {
    const configured = String(runtimeFiles?.[logicalKey] || "").trim();
    return runtimeFilePath(configured || fallbackName);
  }

  function read(logicalKey, fallbackName, fallbackValue) {
    return readJson(resolve(logicalKey, fallbackName), fallbackValue);
  }

  function write(logicalKey, fallbackName, value) {
    return writeJson(resolve(logicalKey, fallbackName), value);
  }

  return {
    resolve,
    read,
    write,
  };
}

module.exports = {
  createStateRegistry,
};


