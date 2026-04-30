#!/usr/bin/env bash
set -euo pipefail

# Unified Linux entrypoint for the production Node service.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

mkdir -p runtime_logs runtime_data

if [[ -n "${NODE_BIN:-}" ]]; then
  RESOLVED_NODE_BIN="$NODE_BIN"
else
  RESOLVED_NODE_BIN="$(command -v node || true)"
  if [[ -z "$RESOLVED_NODE_BIN" ]] && [[ -x "/usr/bin/node" ]]; then
    RESOLVED_NODE_BIN="/usr/bin/node"
  fi
  if [[ -z "$RESOLVED_NODE_BIN" ]] && [[ -x "/usr/local/bin/node" ]]; then
    RESOLVED_NODE_BIN="/usr/local/bin/node"
  fi
fi

if [[ -z "${RESOLVED_NODE_BIN:-}" ]]; then
  echo "[start_linux][error] node binary not found in PATH and common locations" >&2
  exit 1
fi

export NODE_ENV="${NODE_ENV:-production}"

exec "$RESOLVED_NODE_BIN" start_server.js
