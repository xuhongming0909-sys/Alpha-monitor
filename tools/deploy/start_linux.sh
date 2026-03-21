#!/usr/bin/env bash
set -euo pipefail

# 统一的 Linux 启动入口，只负责切换到项目根目录并启动正式 Node 服务。
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

mkdir -p runtime_logs runtime_data

NODE_BIN="${NODE_BIN:-$(command -v node)}"
export NODE_ENV="${NODE_ENV:-production}"

exec "$NODE_BIN" start_server.js
