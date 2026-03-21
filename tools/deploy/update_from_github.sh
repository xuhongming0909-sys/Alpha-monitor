#!/usr/bin/env bash
set -euo pipefail

# 服务器统一更新入口：同步 GitHub 最新代码、安装依赖、重启服务并做健康检查。

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TARGET_BRANCH="${TARGET_BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-alpha-monitor}"
PROJECT_OWNER="${PROJECT_OWNER:-$(id -un)}"
APP_PORT="${APP_PORT:-}"
HEALTH_PATH="${HEALTH_PATH:-/api/health}"
SKIP_GIT_SYNC="${SKIP_GIT_SYNC:-0}"
GIT_RETRY_COUNT="${GIT_RETRY_COUNT:-5}"
GIT_RETRY_DELAY_SECONDS="${GIT_RETRY_DELAY_SECONDS:-8}"

log() {
  printf '[deploy] %s\n' "$1"
}

warn() {
  printf '[deploy][warn] %s\n' "$1" >&2
}

fail() {
  printf '[deploy][error] %s\n' "$1" >&2
  exit 1
}

retry_command() {
  local description="$1"
  shift

  local attempt=1
  while (( attempt <= GIT_RETRY_COUNT )); do
    log "${description} (attempt ${attempt}/${GIT_RETRY_COUNT})"
    if "$@"; then
      return 0
    fi

    if (( attempt == GIT_RETRY_COUNT )); then
      fail "${description} failed after ${GIT_RETRY_COUNT} attempts"
    fi

    warn "${description} failed, retrying in ${GIT_RETRY_DELAY_SECONDS}s"
    sleep "$GIT_RETRY_DELAY_SECONDS"
    attempt=$((attempt + 1))
  done
}

run_systemctl() {
  if sudo -n true >/dev/null 2>&1; then
    sudo -n systemctl "$@"
  else
    systemctl "$@"
  fi
}

service_exists() {
  if sudo -n true >/dev/null 2>&1; then
    sudo -n systemctl list-unit-files "${SERVICE_NAME}.service" --no-legend 2>/dev/null | grep -q "${SERVICE_NAME}\.service"
  else
    systemctl list-unit-files "${SERVICE_NAME}.service" --no-legend 2>/dev/null | grep -q "${SERVICE_NAME}\.service"
  fi
}

repair_project_permissions() {
  log "repairing file ownership for deploy user: ${PROJECT_OWNER}"

  if sudo -n true >/dev/null 2>&1; then
    sudo -n chown -R "${PROJECT_OWNER}:${PROJECT_OWNER}" "$PROJECT_ROOT"
  else
    chown -R "${PROJECT_OWNER}:${PROJECT_OWNER}" "$PROJECT_ROOT"
  fi
}

detect_app_port() {
  if [[ -n "$APP_PORT" ]]; then
    printf '%s' "$APP_PORT"
    return 0
  fi

  if [[ ! -f "$PROJECT_ROOT/config.yaml" ]]; then
    printf '5000'
    return 0
  fi

  node <<'EOF'
const fs = require('fs');
const path = require('path');

try {
  const yaml = require('yaml');
  const configPath = path.join(process.cwd(), 'config.yaml');
  const raw = fs.readFileSync(configPath, 'utf8');
  const config = yaml.parse(raw) || {};
  const port = config?.app?.port;
  process.stdout.write(String(port || 5000));
} catch (error) {
  process.stdout.write('5000');
}
EOF
}

cd "$PROJECT_ROOT"

log "project root: $PROJECT_ROOT"
log "target branch: $TARGET_BRANCH"
log "project owner: $PROJECT_OWNER"

repair_project_permissions

if [[ "$SKIP_GIT_SYNC" != "1" ]]; then
  retry_command "fetching latest code from origin" git fetch --all --prune

  retry_command "resetting worktree to origin/${TARGET_BRANCH}" git reset --hard "origin/${TARGET_BRANCH}"
else
  log "skipping git sync because SKIP_GIT_SYNC=1"
fi

if [[ -f package-lock.json ]]; then
  log "installing Node dependencies with npm ci"
  npm ci
else
  log "package-lock.json not found, using npm install"
  npm install
fi

log "ensuring Linux entrypoint is executable"
chmod +x "$PROJECT_ROOT/tools/deploy/start_linux.sh"

if service_exists; then
  log "restarting system service: ${SERVICE_NAME}"
  run_systemctl restart "$SERVICE_NAME"
  run_systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,12p'
else
  warn "system service ${SERVICE_NAME}.service not found; code was updated but service is not managed yet"
fi

RESOLVED_PORT="$(detect_app_port)"
HEALTH_URL="http://127.0.0.1:${RESOLVED_PORT}${HEALTH_PATH}"

log "checking health: ${HEALTH_URL}"

if ! curl --fail --silent --show-error "$HEALTH_URL"; then
  fail "health check failed after deployment"
fi

printf '\n'
log "deployment finished successfully"
