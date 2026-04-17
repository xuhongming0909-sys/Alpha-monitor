#!/usr/bin/env bash
set -euo pipefail

# 统一服务器部署入口：
# 1. 预检查
# 2. Git 同步
# 3. 按改动自动决定是否安装依赖 / 刷新 systemd / 重启服务
# 4. 健康检查与首页标记校验

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
TARGET_BRANCH="${TARGET_BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-alpha-monitor}"
PROJECT_OWNER="${PROJECT_OWNER:-$(id -un)}"
APP_PORT="${APP_PORT:-}"
HEALTH_PATH="${HEALTH_PATH:-/api/health}"
SKIP_GIT_SYNC="${SKIP_GIT_SYNC:-0}"
DEPLOY_REEXEC="${DEPLOY_REEXEC:-0}"
DEPLOY_MODE="${DEPLOY_MODE:-auto}"
GIT_RETRY_COUNT="${GIT_RETRY_COUNT:-8}"
GIT_RETRY_DELAY_SECONDS="${GIT_RETRY_DELAY_SECONDS:-8}"
SERVICE_RETRY_COUNT="${SERVICE_RETRY_COUNT:-8}"
SERVICE_RETRY_DELAY_SECONDS="${SERVICE_RETRY_DELAY_SECONDS:-2}"
HEALTHCHECK_RETRY_COUNT="${HEALTHCHECK_RETRY_COUNT:-20}"
HEALTHCHECK_RETRY_DELAY_SECONDS="${HEALTHCHECK_RETRY_DELAY_SECONDS:-2}"
VERIFY_CONFIG_YAML="${VERIFY_CONFIG_YAML:-1}"
FORCE_RELEASE_APP_PORT="${FORCE_RELEASE_APP_PORT:-1}"
VERIFY_HOMEPAGE_MARKER="${VERIFY_HOMEPAGE_MARKER:-1}"
EXPECTED_HOME_MARKER="${EXPECTED_HOME_MARKER:-dashboard_page.js}"
FORBIDDEN_HOME_MARKERS="${FORBIDDEN_HOME_MARKERS:-app.js|message-form}"
INSTALL_NODE_MODULES="${INSTALL_NODE_MODULES:-}"
INSTALL_PYTHON_REQUIREMENTS="${INSTALL_PYTHON_REQUIREMENTS:-}"
VERIFY_PYTHON_IMPORTS="${VERIFY_PYTHON_IMPORTS:-}"
REFRESH_SYSTEMD_UNIT="${REFRESH_SYSTEMD_UNIT:-}"
RESTART_SERVICE="${RESTART_SERVICE:-}"
PYTHON_BIN_CANDIDATES="${PYTHON_BIN_CANDIDATES:-python3 python}"
RUNTIME_PRESERVE_DIR="${RUNTIME_PRESERVE_DIR:-}"
CHANGED_FILES_FILE="${CHANGED_FILES_FILE:-}"

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

require_command() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1 || die "required command not found: ${cmd}"
}

normalize_toggle() {
  local name="$1"
  local value="$2"
  case "$value" in
    ""|0|1) ;;
    *) die "invalid ${name}: ${value} (expected 0 or 1)" ;;
  esac
}

normalize_deploy_mode() {
  case "$DEPLOY_MODE" in
    auto|fast|full) ;;
    *) die "invalid DEPLOY_MODE: ${DEPLOY_MODE} (expected auto|fast|full)" ;;
  esac
}

preflight_checks() {
  [[ -d "$PROJECT_ROOT" ]] || die "project root not found: $PROJECT_ROOT"
  if [[ "$SKIP_GIT_SYNC" != "1" ]]; then
    [[ -d "$PROJECT_ROOT/.git" ]] || die "not a git repository: $PROJECT_ROOT"
  fi
  [[ -f "$PROJECT_ROOT/package.json" ]] || die "package.json not found in project root"

  if [[ "$SKIP_GIT_SYNC" != "1" ]]; then
    require_command git
  fi
  require_command npm
  require_command node
  require_command curl
  require_command systemctl
  require_command sed
}

detect_python_bin() {
  local candidate
  for candidate in $PYTHON_BIN_CANDIDATES; do
    if command -v "$candidate" >/dev/null 2>&1; then
      printf '%s' "$candidate"
      return 0
    fi
  done
  return 1
}

ensure_changed_files_file() {
  if [[ -n "$CHANGED_FILES_FILE" ]]; then
    return 0
  fi
  CHANGED_FILES_FILE="$(mktemp)"
}

cleanup_changed_files_file() {
  [[ -n "$CHANGED_FILES_FILE" ]] || return 0
  [[ -f "$CHANGED_FILES_FILE" ]] || return 0
  rm -f "$CHANGED_FILES_FILE"
}

changed_files_count() {
  [[ -n "$CHANGED_FILES_FILE" && -s "$CHANGED_FILES_FILE" ]] || {
    printf '0'
    return 0
  }
  grep -c . "$CHANGED_FILES_FILE" || true
}

changed_files_match() {
  local pattern="$1"
  [[ -n "$CHANGED_FILES_FILE" && -s "$CHANGED_FILES_FILE" ]] || return 1
  grep -Eq "$pattern" "$CHANGED_FILES_FILE"
}

log_changed_files_summary() {
  local count
  count="$(changed_files_count)"
  log "detected changed files between deployed revision and target revision: ${count}"
  if (( count > 0 )); then
    sed -n '1,40p' "$CHANGED_FILES_FILE" | sed 's/^/[deploy][changed] /'
    if (( count > 40 )); then
      log "changed file list truncated at 40 lines"
    fi
  fi
}

write_changed_files_between_revisions() {
  local current_rev="${1:-}"
  local target_rev="${2:-}"

  ensure_changed_files_file
  : > "$CHANGED_FILES_FILE"

  if [[ -z "$target_rev" ]]; then
    return 0
  fi

  if [[ -n "$current_rev" && "$current_rev" != "$target_rev" ]] && git cat-file -e "${current_rev}^{commit}" >/dev/null 2>&1; then
    git diff --name-only --no-renames "$current_rev" "$target_rev" | sed '/^$/d' > "$CHANGED_FILES_FILE"
    return 0
  fi

  if [[ -z "$current_rev" ]]; then
    git diff-tree --no-commit-id --name-only -r "$target_rev" | sed '/^$/d' > "$CHANGED_FILES_FILE"
  fi
}

install_python_requirements() {
  local python_bin="${1:-}"
  local pip_log
  local pip_rc
  [[ "$INSTALL_PYTHON_REQUIREMENTS" == "1" ]] || {
    log "skip Python dependency install because INSTALL_PYTHON_REQUIREMENTS=${INSTALL_PYTHON_REQUIREMENTS}"
    return 0
  }

  if [[ ! -f "$PROJECT_ROOT/requirements.txt" ]]; then
    warn "requirements.txt not found, skip Python dependency install"
    return 0
  fi

  [[ -n "$python_bin" ]] || die "python runtime not found; cannot install requirements"
  log "installing Python dependencies with ${python_bin} -m pip install -r requirements.txt"
  pip_log="$(mktemp)"
  if "$python_bin" -m pip install --disable-pip-version-check -r "$PROJECT_ROOT/requirements.txt" > >(tee "$pip_log") 2> >(tee -a "$pip_log" >&2); then
    rm -f "$pip_log"
    return 0
  fi

  pip_rc=$?
  if grep -qi "externally-managed-environment" "$pip_log"; then
    warn "system Python is externally managed; retrying pip install with --break-system-packages"
    "$python_bin" -m pip install --disable-pip-version-check --break-system-packages -r "$PROJECT_ROOT/requirements.txt"
    rm -f "$pip_log"
    return 0
  fi

  rm -f "$pip_log"
  return "$pip_rc"
}

verify_python_imports() {
  local python_bin="${1:-}"
  [[ "$VERIFY_PYTHON_IMPORTS" == "1" ]] || {
    log "skip Python import verification because VERIFY_PYTHON_IMPORTS=${VERIFY_PYTHON_IMPORTS}"
    return 0
  }

  [[ -n "$python_bin" ]] || die "python runtime not found; cannot verify imports"
  log "verifying Python imports: akshare, pandas, requests"
  "$python_bin" - <<'EOF'
import importlib

required = ["akshare", "pandas", "requests"]
missing = []

for name in required:
    try:
        importlib.import_module(name)
    except Exception:
        missing.append(name)

if missing:
    raise SystemExit("missing python modules: " + ", ".join(missing))
EOF
}

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

repair_path_ownership() {
  local recursive="$1"
  local path="$2"
  [[ -e "$path" ]] || return 0

  if [[ "$recursive" == "1" ]]; then
    sudo -n chown -R "${PROJECT_OWNER}:${PROJECT_OWNER}" "$path" >/dev/null 2>&1 \
      || chown -R "${PROJECT_OWNER}:${PROJECT_OWNER}" "$path" >/dev/null 2>&1 \
      || warn "unable to change ownership recursively for ${path}"
  else
    sudo -n chown "${PROJECT_OWNER}:${PROJECT_OWNER}" "$path" >/dev/null 2>&1 \
      || chown "${PROJECT_OWNER}:${PROJECT_OWNER}" "$path" >/dev/null 2>&1 \
      || warn "unable to change ownership for ${path}"
  fi
}

repair_project_permissions_if_needed() {
  local needs_repair=0
  local check_path
  local direct_targets=("$PROJECT_ROOT" "$PROJECT_ROOT/package.json" "$PROJECT_ROOT/package-lock.json" "$PROJECT_ROOT/requirements.txt")
  local recursive_targets=("$PROJECT_ROOT/.git" "$PROJECT_ROOT/runtime_data" "$PROJECT_ROOT/runtime_logs" "$PROJECT_ROOT/tools/deploy")

  if [[ "$INSTALL_NODE_MODULES" == "1" ]]; then
    recursive_targets+=("$PROJECT_ROOT/node_modules")
  fi

  for check_path in "${direct_targets[@]}" "${recursive_targets[@]}"; do
    [[ -e "$check_path" ]] || continue
    if [[ ! -w "$check_path" ]]; then
      needs_repair=1
      break
    fi
  done

  if (( needs_repair == 0 )); then
    log "skip ownership repair because deployment-critical paths are already writable"
    return 0
  fi

  log "repairing file ownership for deploy user on deployment-critical paths"
  for check_path in "${direct_targets[@]}"; do
    repair_path_ownership 0 "$check_path"
  done
  for check_path in "${recursive_targets[@]}"; do
    repair_path_ownership 1 "$check_path"
  done
}

preserve_tracked_runtime_files() {
  local backup_dir
  local tracked_count=0
  local rel_path

  [[ -d "$PROJECT_ROOT/.git" ]] || return 0

  backup_dir="$(mktemp -d)"
  while IFS= read -r -d '' rel_path; do
    tracked_count=$((tracked_count + 1))
    [[ -f "$PROJECT_ROOT/$rel_path" ]] || continue
    mkdir -p "$backup_dir/$(dirname "$rel_path")"
    cp -p "$PROJECT_ROOT/$rel_path" "$backup_dir/$rel_path"
  done < <(git -C "$PROJECT_ROOT" ls-files -z -- runtime_data)

  if (( tracked_count == 0 )); then
    rm -rf "$backup_dir"
    return 0
  fi

  log "preserved ${tracked_count} tracked runtime_data file(s) before git sync"
  printf '%s' "$backup_dir"
}

restore_preserved_runtime_files() {
  local backup_dir="${1:-}"
  local preserved_path
  local rel_path

  [[ -n "$backup_dir" ]] || return 0
  [[ -d "$backup_dir" ]] || return 0

  log "restoring preserved runtime_data files after code sync"
  while IFS= read -r -d '' preserved_path; do
    rel_path="${preserved_path#${backup_dir}/}"
    mkdir -p "$PROJECT_ROOT/$(dirname "$rel_path")"
    cp -p "$preserved_path" "$PROJECT_ROOT/$rel_path"
  done < <(find "$backup_dir" -type f -print0)
}

cleanup_preserved_runtime_files() {
  local backup_dir="${1:-}"
  [[ -n "$backup_dir" ]] || return 0
  [[ -d "$backup_dir" ]] || return 0
  rm -rf "$backup_dir"
}

git_sync() {
  local current_rev
  local target_rev

  export GIT_TERMINAL_PROMPT=0
  ensure_changed_files_file
  current_rev="$(git rev-parse HEAD 2>/dev/null || true)"

  retry_hard \
    "fetching latest code from origin/${TARGET_BRANCH} with resilient HTTP settings" \
    git -c http.version=HTTP/1.1 -c http.maxRequests=2 -c http.lowSpeedLimit=1000 -c http.lowSpeedTime=60 \
    fetch --prune origin "$TARGET_BRANCH"

  if git show-ref --quiet "refs/remotes/origin/${TARGET_BRANCH}"; then
    target_rev="$(git rev-parse "refs/remotes/origin/${TARGET_BRANCH}")"
  else
    target_rev="$(git rev-parse FETCH_HEAD)"
  fi

  write_changed_files_between_revisions "$current_rev" "$target_rev"
  log_changed_files_summary

  if [[ -n "$current_rev" && "$current_rev" == "$target_rev" ]]; then
    log "worktree revision already matches target revision ${target_rev}; resetting anyway to clean local drift"
  fi
  retry_hard "resetting worktree to ${target_rev}" git reset --hard "$target_rev"
}

apply_deploy_mode() {
  local auto_install_node=""
  local auto_install_python=""
  local auto_verify_python=""
  local auto_refresh_systemd=""
  local auto_restart_service=""

  normalize_deploy_mode
  normalize_toggle "INSTALL_NODE_MODULES" "$INSTALL_NODE_MODULES"
  normalize_toggle "INSTALL_PYTHON_REQUIREMENTS" "$INSTALL_PYTHON_REQUIREMENTS"
  normalize_toggle "VERIFY_PYTHON_IMPORTS" "$VERIFY_PYTHON_IMPORTS"
  normalize_toggle "REFRESH_SYSTEMD_UNIT" "$REFRESH_SYSTEMD_UNIT"
  normalize_toggle "RESTART_SERVICE" "$RESTART_SERVICE"

  case "$DEPLOY_MODE" in
    full)
      auto_install_node="1"
      auto_install_python="1"
      auto_verify_python="1"
      auto_refresh_systemd="1"
      auto_restart_service="1"
      ;;
    fast)
      auto_install_node="0"
      auto_install_python="0"
      auto_verify_python="0"
      auto_refresh_systemd="0"
      auto_restart_service="1"
      ;;
    auto)
      if [[ -z "$CHANGED_FILES_FILE" || ! -f "$CHANGED_FILES_FILE" ]]; then
        warn "changed file list is unavailable in auto mode; falling back to full deploy decisions"
        auto_install_node="1"
        auto_install_python="1"
        auto_verify_python="1"
        auto_refresh_systemd="1"
        auto_restart_service="1"
      else
        changed_files_match '^(package\.json|package-lock\.json)$' && auto_install_node="1" || auto_install_node="0"
        changed_files_match '^requirements\.txt$' && auto_install_python="1" || auto_install_python="0"
        auto_verify_python="$auto_install_python"
        changed_files_match '^tools/deploy/(alpha-monitor\.service|start_linux\.sh)$' && auto_refresh_systemd="1" || auto_refresh_systemd="0"
        if changed_files_match '^(data_fetch/|strategy/|presentation/|notification/|shared/|start_server\.js$|config\.yaml$|package\.json$|package-lock\.json$|requirements\.txt$|data_dispatch\.py$|db_paths\.py$|tools/deploy/(start_linux\.sh|alpha-monitor\.service)$)'; then
          auto_restart_service="1"
        else
          auto_restart_service="0"
        fi
      fi
      ;;
  esac

  [[ -n "$INSTALL_NODE_MODULES" ]] || INSTALL_NODE_MODULES="$auto_install_node"
  [[ -n "$INSTALL_PYTHON_REQUIREMENTS" ]] || INSTALL_PYTHON_REQUIREMENTS="$auto_install_python"
  [[ -n "$VERIFY_PYTHON_IMPORTS" ]] || VERIFY_PYTHON_IMPORTS="$auto_verify_python"
  [[ -n "$REFRESH_SYSTEMD_UNIT" ]] || REFRESH_SYSTEMD_UNIT="$auto_refresh_systemd"
  [[ -n "$RESTART_SERVICE" ]] || RESTART_SERVICE="$auto_restart_service"

  log "deploy mode: ${DEPLOY_MODE}"
  log "effective steps: install_node=${INSTALL_NODE_MODULES} install_python=${INSTALL_PYTHON_REQUIREMENTS} verify_python=${VERIFY_PYTHON_IMPORTS} refresh_systemd=${REFRESH_SYSTEMD_UNIT} restart_service=${RESTART_SERVICE}"
}

refresh_systemd_unit() {
  local template_path="$PROJECT_ROOT/tools/deploy/alpha-monitor.service"
  local target_path="/etc/systemd/system/${SERVICE_NAME}.service"
  local rendered_unit
  local unit_written=0

  [[ "$REFRESH_SYSTEMD_UNIT" == "1" ]] || {
    log "skip systemd unit refresh because REFRESH_SYSTEMD_UNIT=${REFRESH_SYSTEMD_UNIT}"
    return 0
  }

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

validate_config_yaml() {
  if [[ "$VERIFY_CONFIG_YAML" != "1" ]]; then
    log "skip config.yaml syntax validation because VERIFY_CONFIG_YAML=${VERIFY_CONFIG_YAML}"
    return 0
  fi

  if [[ ! -f "$PROJECT_ROOT/config.yaml" ]]; then
    warn "config.yaml not found, skip syntax validation"
    return 0
  fi

  log "validating config.yaml syntax"
  node <<'EOF'
const fs = require('fs');
const path = require('path');
const yaml = require('yaml');

const configPath = path.join(process.cwd(), 'config.yaml');
const text = fs.readFileSync(configPath, 'utf8');
yaml.parse(text);
EOF
}

release_stale_port_owner() {
  local port="$1"
  [[ "$FORCE_RELEASE_APP_PORT" == "1" ]] || return 0
  [[ -n "$port" ]] || return 0

  warn "releasing stale owner on port ${port} after restart failure"

  if command -v fuser >/dev/null 2>&1; then
    if sudo -n fuser -k "${port}/tcp" >/dev/null 2>&1; then
      return 0
    fi
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
    return 0
  fi

  if command -v ss >/dev/null 2>&1; then
    local pids
    pids="$(
      ss -ltnp 2>/dev/null \
        | awk -v port=":${port}" '
            index($4, port) {
              if (match($0, /pid=[0-9]+/)) {
                pid = substr($0, RSTART + 4, RLENGTH - 4);
                print pid;
              }
            }
          ' \
        | sort -u
    )"
    if [[ -n "$pids" ]]; then
      while IFS= read -r pid; do
        [[ -n "$pid" ]] || continue
        kill -9 "$pid" >/dev/null 2>&1 || sudo -n kill -9 "$pid" >/dev/null 2>&1 || true
      done <<< "$pids"
    fi
  fi
}

stop_conflicting_pm2_process() {
  [[ -n "$SERVICE_NAME" ]] || return 0
  command -v pm2 >/dev/null 2>&1 || return 0

  if ! pm2 jlist 2>/dev/null | grep -q "\"name\":\"${SERVICE_NAME}\""; then
    return 0
  fi

  warn "detected legacy PM2 process '${SERVICE_NAME}', removing it to avoid port conflicts"
  pm2 delete "$SERVICE_NAME" >/dev/null 2>&1 || pm2 stop "$SERVICE_NAME" >/dev/null 2>&1 || true
  pm2 save >/dev/null 2>&1 || true
}

restart_service_if_needed() {
  local resolved_port="$1"

  if ! service_exists; then
    warn "system service ${SERVICE_NAME}.service not found; code was updated but service is not managed yet"
    return 0
  fi

  refresh_systemd_unit

  [[ "$RESTART_SERVICE" == "1" ]] || {
    log "skip service restart because RESTART_SERVICE=${RESTART_SERVICE}"
    return 0
  }

  stop_conflicting_pm2_process
  log "restarting system service: ${SERVICE_NAME}"
  if ! run_systemctl restart "$SERVICE_NAME"; then
    warn "first restart attempt failed; trying stale-port cleanup before retry"
    release_stale_port_owner "$resolved_port"
    run_systemctl restart "$SERVICE_NAME"
  fi
  wait_service_active
  run_systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,12p'
}

run_health_check() {
  local resolved_port="${1:-}"
  local health_url
  local attempt=1

  if [[ -z "$resolved_port" ]]; then
    resolved_port="$(detect_app_port)"
  fi
  health_url="http://127.0.0.1:${resolved_port}${HEALTH_PATH}"

  log "checking health: ${health_url}"
  while (( attempt <= HEALTHCHECK_RETRY_COUNT )); do
    if curl --fail --silent --show-error "$health_url" >/dev/null; then
      return 0
    fi

    if (( attempt == HEALTHCHECK_RETRY_COUNT )); then
      warn "health check failed after ${HEALTHCHECK_RETRY_COUNT} attempts"
      run_systemctl --no-pager --full status "$SERVICE_NAME" | sed -n '1,24p' || true
      sudo -n journalctl -u "${SERVICE_NAME}" -n 80 --no-pager 2>/dev/null || journalctl -u "${SERVICE_NAME}" -n 80 --no-pager || true
      die "health check failed: ${health_url}"
    fi

    warn "health check not ready yet (attempt ${attempt}/${HEALTHCHECK_RETRY_COUNT}), retry in ${HEALTHCHECK_RETRY_DELAY_SECONDS}s"
    sleep "$HEALTHCHECK_RETRY_DELAY_SECONDS"
    attempt=$((attempt + 1))
  done
}

run_homepage_marker_check() {
  local resolved_port="${1:-}"
  local homepage_url
  local homepage_html

  if [[ "$VERIFY_HOMEPAGE_MARKER" != "1" ]]; then
    log "skip homepage marker check because VERIFY_HOMEPAGE_MARKER=${VERIFY_HOMEPAGE_MARKER}"
    return 0
  fi

  if [[ -z "$resolved_port" ]]; then
    resolved_port="$(detect_app_port)"
  fi

  homepage_url="http://127.0.0.1:${resolved_port}/"
  log "checking homepage markers: ${homepage_url}"
  homepage_html="$(curl --fail --silent --show-error "$homepage_url")"

  if [[ -n "$EXPECTED_HOME_MARKER" ]] && ! printf '%s' "$homepage_html" | grep -q "$EXPECTED_HOME_MARKER"; then
    die "homepage marker check failed: missing expected marker '${EXPECTED_HOME_MARKER}'"
  fi

  if [[ -n "$FORBIDDEN_HOME_MARKERS" ]] && printf '%s' "$homepage_html" | grep -Eq "$FORBIDDEN_HOME_MARKERS"; then
    die "homepage marker check failed: found forbidden markers '${FORBIDDEN_HOME_MARKERS}'"
  fi
}

cd "$PROJECT_ROOT"
log "project root: $PROJECT_ROOT"
log "target branch: $TARGET_BRANCH"
log "project owner: $PROJECT_OWNER"

preflight_checks

if [[ "$SKIP_GIT_SYNC" != "1" ]]; then
  if [[ -z "$RUNTIME_PRESERVE_DIR" ]]; then
    RUNTIME_PRESERVE_DIR="$(preserve_tracked_runtime_files || true)"
  fi
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
      DEPLOY_MODE="$DEPLOY_MODE" \
      GIT_RETRY_COUNT="$GIT_RETRY_COUNT" \
      GIT_RETRY_DELAY_SECONDS="$GIT_RETRY_DELAY_SECONDS" \
      SERVICE_RETRY_COUNT="$SERVICE_RETRY_COUNT" \
      SERVICE_RETRY_DELAY_SECONDS="$SERVICE_RETRY_DELAY_SECONDS" \
      VERIFY_CONFIG_YAML="$VERIFY_CONFIG_YAML" \
      FORCE_RELEASE_APP_PORT="$FORCE_RELEASE_APP_PORT" \
      VERIFY_HOMEPAGE_MARKER="$VERIFY_HOMEPAGE_MARKER" \
      EXPECTED_HOME_MARKER="$EXPECTED_HOME_MARKER" \
      FORBIDDEN_HOME_MARKERS="$FORBIDDEN_HOME_MARKERS" \
      INSTALL_NODE_MODULES="$INSTALL_NODE_MODULES" \
      INSTALL_PYTHON_REQUIREMENTS="$INSTALL_PYTHON_REQUIREMENTS" \
      VERIFY_PYTHON_IMPORTS="$VERIFY_PYTHON_IMPORTS" \
      REFRESH_SYSTEMD_UNIT="$REFRESH_SYSTEMD_UNIT" \
      RESTART_SERVICE="$RESTART_SERVICE" \
      PYTHON_BIN_CANDIDATES="$PYTHON_BIN_CANDIDATES" \
      RUNTIME_PRESERVE_DIR="$RUNTIME_PRESERVE_DIR" \
      CHANGED_FILES_FILE="$CHANGED_FILES_FILE" \
      bash "$PROJECT_ROOT/tools/deploy/update_from_github.sh"
  fi
else
  log "skipping git sync because SKIP_GIT_SYNC=1"
fi

apply_deploy_mode
repair_project_permissions_if_needed

restore_preserved_runtime_files "$RUNTIME_PRESERVE_DIR"
cleanup_preserved_runtime_files "$RUNTIME_PRESERVE_DIR"
RUNTIME_PRESERVE_DIR=""

if [[ "$INSTALL_NODE_MODULES" == "1" ]]; then
  if [[ -f package-lock.json ]]; then
    log "installing Node dependencies with npm ci"
    npm ci --no-audit --fund=false
  else
    log "package-lock.json not found, using npm install"
    npm install --no-audit --fund=false
  fi
else
  log "skip Node dependency install because INSTALL_NODE_MODULES=${INSTALL_NODE_MODULES}"
fi

validate_config_yaml
RESOLVED_APP_PORT="$(detect_app_port)"
PYTHON_BIN="$(detect_python_bin || true)"
if [[ -n "$PYTHON_BIN" ]]; then
  log "detected python runtime: ${PYTHON_BIN}"
else
  warn "python runtime not found in candidates: ${PYTHON_BIN_CANDIDATES}"
fi

install_python_requirements "$PYTHON_BIN"
verify_python_imports "$PYTHON_BIN"

log "ensuring Linux entrypoint is executable"
chmod +x "$PROJECT_ROOT/tools/deploy/start_linux.sh"

restart_service_if_needed "$RESOLVED_APP_PORT"
run_health_check "$RESOLVED_APP_PORT"
run_homepage_marker_check "$RESOLVED_APP_PORT"
cleanup_changed_files_file
log "deployment finished successfully"
