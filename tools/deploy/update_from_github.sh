#!/usr/bin/env bash
set -euo pipefail

# 服务器统一部署入口（GitHub Actions 与人工排障共用）：
# 1) 预检查 2) 代码同步 3) 依赖安装 4) service 更新与重启 5) 健康检查

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TARGET_BRANCH="${TARGET_BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-alpha-monitor}"
PROJECT_OWNER="${PROJECT_OWNER:-$(id -un)}"
APP_PORT="${APP_PORT:-}"
HEALTH_PATH="${HEALTH_PATH:-/api/health}"
SKIP_GIT_SYNC="${SKIP_GIT_SYNC:-0}"
DEPLOY_REEXEC="${DEPLOY_REEXEC:-0}"
GIT_RETRY_COUNT="${GIT_RETRY_COUNT:-8}"
GIT_RETRY_DELAY_SECONDS="${GIT_RETRY_DELAY_SECONDS:-8}"
SERVICE_RETRY_COUNT="${SERVICE_RETRY_COUNT:-8}"
SERVICE_RETRY_DELAY_SECONDS="${SERVICE_RETRY_DELAY_SECONDS:-2}"

log() {
  printf '[deploy] %s\n' "$1"
}

warn() {
  printf '[deploy][warn] %s\n' "$1" >&2
}

die() {
  printf '[deploy][error] %s\n' "$1" >&2
  exit 1
}

retry_hard() {
  local description="$1"
  shift

  local attempt=1
  while (( attempt <= GIT_RETRY_COUNT )); do
    log "${description} (attempt ${attempt}/${GIT_RETRY_COUNT})"
    if "$@"; then
      return 0
    fi

    if (( attempt == GIT_RETRY_COUNT )); then
      die "${description} failed after ${GIT_RETRY_COUNT} attempts"
    fi

    warn "${description} failed, retrying in ${GIT_RETRY_DELAY_SECONDS}s"
    sleep "$GIT_RETRY_DELAY_SECONDS"
    attempt=$((attempt + 1))
  done
}

retry_soft() {
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
  command -v "$cmd" >/dev/null 2>&1 || die "required command not found: ${cmd}"
}

preflight_checks() {
  [[ -d "$PROJECT_ROOT" ]] || die "project root not found: $PROJECT_ROOT"
  [[ -d "$PROJECT_ROOT/.git" ]] || die "not a git repository: $PROJECT_ROOT"
  [[ -f "$PROJECT_ROOT/package.json" ]] || die "package.json not found in project root"

  require_command git
  require_command npm
  require_command node
  require_command curl
  require_command systemctl
  require_command sed
}

# 尝试 sudo systemctl；若 sudo 不可用则回退普通 systemctl。
run_systemctl() {
  local err_file
  local rc
  local err_msg

  err_file="$(mktemp)"
  if sudo -n systemctl "$@" 2>"$err_file"; then
    rm -f "$err_file"
    return 0
  fi

  rc=$?
  err_msg="$(cat "$err_file" 2>/dev/null || true)"
  rm -f "$err_file"

  if printf '%s' "$err_msg" | grep -qiE 'a password is required|no tty present|not in the sudoers|may not run sudo|not allowed to execute'; then
    systemctl "$@"
    return $?
  fi

  if [[ -n "$err_msg" ]]; then
    printf '%s\n' "$err_msg" >&2
  fi

  return "$rc"
}

service_exists() {
  local list_output
  if ! list_output="$(run_systemctl list-unit-files "${SERVICE_NAME}.service" --no-legend 2>/dev/null)"; then
    die "unable to query systemd units for ${SERVICE_NAME}.service"
  fi

  printf '%s\n' "$list_output" | grep -q "${SERVICE_NAME}\.service"
}

repair_project_permissions() {
  log "repairing file ownership for deploy user: ${PROJECT_OWNER}"

  if sudo -n chown -R "${PROJECT_OWNER}:${PROJECT_OWNER}" "$PROJECT_ROOT" >/dev/null 2>&1; then
    return 0
  fi

  if ! chown -R "${PROJECT_OWNER}:${PROJECT_OWNER}" "$PROJECT_ROOT" >/dev/null 2>&1; then
    warn "unable to change ownership for ${PROJECT_ROOT}; continuing with existing permissions"
  fi
}

git_sync() {
  export GIT_TERMINAL_PROMPT=0

  if ! retry_soft "fetching latest code from origin" git fetch --all --prune; then
    warn "default git fetch failed, trying resilient fetch mode"
    retry_hard \
      "fetching target branch with resilient HTTP settings" \
      git -c http.version=HTTP/1.1 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 \
      fetch --prune origin "$TARGET_BRANCH"
    retry_hard "resetting worktree to fetched HEAD" git reset --hard FETCH_HEAD
    return 0
  fi

  retry_hard "resetting worktree to origin/${TARGET_BRANCH}" git reset --hard "origin/${TARGET_BRANCH}"
}

refresh_systemd_unit() {
  local template_path="$PROJECT_ROOT/tools/deploy/alpha-monitor.service"
  local target_path="/etc/systemd/system/${SERVICE_NAME}.service"
  local rendered_unit
  local unit_written=0

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

  if sudo -n tee "$target_path" < "$rendered_unit" >/dev/null 2>&1; then
    unit_written=1
    sudo -n chmod 644 "$target_path" || true
  elif [[ -w "$(dirname "$target_path")" ]]; then
    cat "$rendered_unit" > "$target_path"
    chmod 644 "$target_path" || true
    unit_written=1
  else
    warn "skip refreshing systemd unit: no permission to write ${target_path}"
  fi

  rm -f "$rendered_unit"

  if (( unit_written == 0 )); then
    if [[ "$PROJECT_ROOT" == *" "* ]]; then
      die "project root contains spaces; unit refresh is required but permission is missing"
    fi
    return 0
  fi

  run_systemctl daemon-reload
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
  sudo -n journalctl -u "${SERVICE_NAME}" -n 80 --no-pager 2>/dev/null || journalctl -u "${SERVICE_NAME}" -n 80 --no-pager || true
  die "service restart check failed"
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
} catch {
  process.stdout.write('5000');
}
EOF
}

run_health_check() {
  local resolved_port
  local health_url

  resolved_port="$(detect_app_port)"
  health_url="http://127.0.0.1:${resolved_port}${HEALTH_PATH}"

  log "checking health: ${health_url}"
  curl --fail --silent --show-error "$health_url" >/dev/null
}

cd "$PROJECT_ROOT"
log "project root: $PROJECT_ROOT"
log "target branch: $TARGET_BRANCH"
log "project owner: $PROJECT_OWNER"

preflight_checks
repair_project_permissions

if [[ "$SKIP_GIT_SYNC" != "1" ]]; then
  git_sync

  # 代码同步后重新执行新版本脚本，避免“旧脚本跑后半程”。
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
      SERVICE_RETRY_COUNT="$SERVICE_RETRY_COUNT" \
      SERVICE_RETRY_DELAY_SECONDS="$SERVICE_RETRY_DELAY_SECONDS" \
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

run_health_check
log "deployment finished successfully"
