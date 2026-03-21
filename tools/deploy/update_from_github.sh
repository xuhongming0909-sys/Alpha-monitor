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
DEPLOY_REEXEC="${DEPLOY_REEXEC:-0}"
SERVICE_RETRY_COUNT="${SERVICE_RETRY_COUNT:-8}"
SERVICE_RETRY_DELAY_SECONDS="${SERVICE_RETRY_DELAY_SECONDS:-2}"

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

retry_soft_command() {
  local description="$1"
  shift

  local attempt=1
  while (( attempt <= GIT_RETRY_COUNT )); do
    log "${description} (attempt ${attempt}/${GIT_RETRY_COUNT})"
    if "$@"; then
      return 0
    fi

    if (( attempt == GIT_RETRY_COUNT )); then
      return 1
    fi

    warn "${description} failed, retrying in ${GIT_RETRY_DELAY_SECONDS}s"
    sleep "$GIT_RETRY_DELAY_SECONDS"
    attempt=$((attempt + 1))
  done

  return 1
}

require_command() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || fail "required command not found: ${cmd}"
}

preflight_checks() {
  [[ -d "$PROJECT_ROOT" ]] || fail "project root not found: $PROJECT_ROOT"
  [[ -d "$PROJECT_ROOT/.git" ]] || fail "not a git repository: $PROJECT_ROOT"
  [[ -f "$PROJECT_ROOT/package.json" ]] || fail "package.json not found in project root"

  require_command git
  require_command npm
  require_command node
  require_command curl
  require_command sed
  require_command mktemp
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

git_sync() {
  export GIT_TERMINAL_PROMPT=0

  if ! retry_soft_command "fetching latest code from origin" git fetch --all --prune; then
    warn "default git fetch failed, trying resilient fetch mode"
    retry_command \
      "fetching target branch with resilient HTTP settings" \
      git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 \
      fetch --prune origin "$TARGET_BRANCH"
    retry_command "resetting worktree to fetched HEAD" git reset --hard FETCH_HEAD
    return 0
  fi

  retry_command "resetting worktree to origin/${TARGET_BRANCH}" git reset --hard "origin/${TARGET_BRANCH}"
}

refresh_systemd_unit() {
  local template_path="$PROJECT_ROOT/tools/deploy/alpha-monitor.service"
  local target_path="/etc/systemd/system/${SERVICE_NAME}.service"
  local rendered_unit

  if [[ ! -f "$template_path" ]]; then
    warn "systemd template not found: $template_path"
    return 0
  fi

  log "refreshing systemd unit: ${SERVICE_NAME}.service"
  rendered_unit="$(mktemp)"

  sed \
    -e "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
    -e "s|__SERVICE_USER__|${PROJECT_OWNER}|g" \
    "$template_path" > "$rendered_unit"

  if sudo -n true >/dev/null 2>&1; then
    sudo -n tee "$target_path" < "$rendered_unit" >/dev/null
    sudo -n chmod 644 "$target_path"
    sudo -n systemctl daemon-reload
  else
    cat "$rendered_unit" > "$target_path"
    chmod 644 "$target_path"
    systemctl daemon-reload
  fi

  rm -f "$rendered_unit"
}

wait_service_active() {
  local attempt=1
  while (( attempt <= SERVICE_RETRY_COUNT )); do
    if run_systemctl is-active --quiet "$SERVICE_NAME"; then
      log "service ${SERVICE_NAME} is active"
      return 0
    fi

    warn "service ${SERVICE_NAME} not active yet (attempt ${attempt}/${SERVICE_RETRY_COUNT})"
    sleep "$SERVICE_RETRY_DELAY_SECONDS"
    attempt=$((attempt + 1))
  done

  warn "service ${SERVICE_NAME} failed to become active"
  run_systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,20p' || true
  if sudo -n true >/dev/null 2>&1; then
    sudo -n journalctl -u "${SERVICE_NAME}" -n 60 --no-pager || true
  else
    journalctl -u "${SERVICE_NAME}" -n 60 --no-pager || true
  fi
  fail "service restart check failed"
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

preflight_checks
repair_project_permissions

if [[ "$SKIP_GIT_SYNC" != "1" ]]; then
  git_sync

  if [[ "$DEPLOY_REEXEC" != "1" ]]; then
    log "reloading deployment script from latest synced revision"
    exec env \
      PROJECT_ROOT="$PROJECT_ROOT" \
      TARGET_BRANCH="$TARGET_BRANCH" \
      SERVICE_NAME="$SERVICE_NAME" \
      PROJECT_OWNER="$PROJECT_OWNER" \
      APP_PORT="$APP_PORT" \
      HEALTH_PATH="$HEALTH_PATH" \
      SKIP_GIT_SYNC=1 \
      DEPLOY_REEXEC=1 \
      GIT_RETRY_COUNT="$GIT_RETRY_COUNT" \
      GIT_RETRY_DELAY_SECONDS="$GIT_RETRY_DELAY_SECONDS" \
      bash "$PROJECT_ROOT/tools/deploy/update_from_github.sh"
  fi
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
  refresh_systemd_unit
  log "restarting system service: ${SERVICE_NAME}"
  run_systemctl restart "$SERVICE_NAME"
  wait_service_active
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
