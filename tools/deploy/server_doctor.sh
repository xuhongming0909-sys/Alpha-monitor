#!/usr/bin/env bash
set -euo pipefail

# 服务器侧快速自检脚本：检查依赖、配置、systemd、反向代理和健康检查。

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

print_section() {
  echo
  echo "== $1 =="
}

print_kv() {
  printf '%-22s %s\n' "$1" "$2"
}

safe_run() {
  local label="$1"
  shift
  if "$@" >/tmp/alpha_monitor_doctor.out 2>/tmp/alpha_monitor_doctor.err; then
    print_kv "$label" "ok"
    cat /tmp/alpha_monitor_doctor.out
  else
    print_kv "$label" "fail"
    cat /tmp/alpha_monitor_doctor.err >&2 || true
  fi
}

CONFIG_JSON="$(
node <<'EOF'
const { getConfig } = require('./shared/config/node_config');
const config = getConfig();
const port = Number(config?.app?.port || 5000);
const host = String(config?.app?.host || '0.0.0.0').trim() || '0.0.0.0';
const serviceName = String(config?.deployment?.systemd?.service_name || 'alpha-monitor').trim() || 'alpha-monitor';
const healthPath = String(
  config?.deployment?.healthcheck?.public_path ||
  config?.app?.healthcheck_path ||
  '/api/health'
).trim();
const normalizedHealthPath = healthPath.startsWith('/') ? healthPath : `/${healthPath}`;
const serverBaseUrl = String(config?.app?.server_base_url || `http://127.0.0.1:${port}`).trim() || `http://127.0.0.1:${port}`;
const publicBaseUrl = String(config?.deployment?.public_base_url || serverBaseUrl).trim() || serverBaseUrl;
const reverseProxyEnabled = Boolean(config?.deployment?.reverse_proxy?.enabled);
const reverseProxyType = String(config?.deployment?.reverse_proxy?.type || 'none').trim() || 'none';
process.stdout.write(JSON.stringify({
  port,
  host,
  serviceName,
  healthPath: normalizedHealthPath,
  serverBaseUrl,
  publicBaseUrl,
  publicHealthUrl: `${publicBaseUrl.replace(/\/+$/, '')}${normalizedHealthPath}`,
  reverseProxyEnabled,
  reverseProxyType
}));
EOF
)"

PORT="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.port));")"
HOST="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.host));")"
SERVICE_NAME="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.serviceName));")"
LOCAL_HEALTH_URL="http://127.0.0.1:${PORT}$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.healthPath));")"
PUBLIC_BASE_URL="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.publicBaseUrl));")"
PUBLIC_HEALTH_URL="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.publicHealthUrl));")"
REVERSE_PROXY_ENABLED="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.reverseProxyEnabled));")"
REVERSE_PROXY_TYPE="$(printf '%s' "$CONFIG_JSON" | node -e "const data = JSON.parse(require('fs').readFileSync(0,'utf8')); process.stdout.write(String(data.reverseProxyType));")"

print_section "Project"
print_kv "Project root" "$PROJECT_ROOT"
print_kv "Configured host" "$HOST"
print_kv "Configured port" "$PORT"
print_kv "Service name" "$SERVICE_NAME"
print_kv "Public URL" "$PUBLIC_BASE_URL"
print_kv "Public health" "$PUBLIC_HEALTH_URL"
print_kv "Reverse proxy" "enabled=${REVERSE_PROXY_ENABLED} type=${REVERSE_PROXY_TYPE}"

print_section "Runtime Dependencies"
for bin in node npm python; do
  if command -v "$bin" >/dev/null 2>&1; then
    print_kv "$bin" "$(command -v "$bin")"
  else
    print_kv "$bin" "missing"
  fi
done

print_section "systemd"
if command -v systemctl >/dev/null 2>&1; then
  safe_run "systemctl is-enabled" systemctl is-enabled "$SERVICE_NAME"
  safe_run "systemctl is-active" systemctl is-active "$SERVICE_NAME"
  echo "-- recent journal --"
  journalctl -u "$SERVICE_NAME" -n 20 --no-pager || true
else
  print_kv "systemctl" "missing"
fi

print_section "Reverse Proxy"
if command -v nginx >/dev/null 2>&1; then
  safe_run "nginx -t" nginx -t
  safe_run "nginx active" systemctl is-active nginx
fi
if command -v caddy >/dev/null 2>&1; then
  safe_run "caddy active" systemctl is-active caddy
fi

print_section "Health Checks"
safe_run "local health" curl -fsS "$LOCAL_HEALTH_URL"

if [[ "$PUBLIC_BASE_URL" != http://127.0.0.1:* ]] && [[ "$PUBLIC_BASE_URL" != http://localhost:* ]] && [[ "$PUBLIC_BASE_URL" != https://localhost:* ]]; then
  safe_run "public health" curl -fsS "$PUBLIC_HEALTH_URL"
else
  print_kv "public health" "skipped (public URL not configured yet)"
fi

print_section "Listening Ports"
if command -v ss >/dev/null 2>&1; then
  ss -ltnp | grep -E "(:80|:443|:${PORT})" || true
elif command -v netstat >/dev/null 2>&1; then
  netstat -ltnp 2>/dev/null | grep -E "(:80|:443|:${PORT})" || true
else
  print_kv "port inspection" "ss/netstat missing"
fi

print_section "Done"
echo "Doctor check finished."
