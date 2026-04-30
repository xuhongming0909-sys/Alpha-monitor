#!/usr/bin/env bash
set -euo pipefail

# 用模板生成并安装 Nginx 站点配置，让公网 80 端口转发到应用内部端口。

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMPLATE_PATH="$PROJECT_ROOT/tools/deploy/nginx-alpha-monitor.conf"
SERVICE_NAME="${1:-alpha-monitor}"
SERVER_NAME="${2:-_}"
UPSTREAM_PORT="${3:-5000}"
SITE_PATH="/etc/nginx/sites-available/${SERVICE_NAME}"
ENABLED_PATH="/etc/nginx/sites-enabled/${SERVICE_NAME}"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Template not found: $TEMPLATE_PATH" >&2
  exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
  echo "nginx is not installed. Please install nginx first." >&2
  exit 1
fi

sed \
  -e "s|YOUR_DOMAIN_OR_IP|${SERVER_NAME}|g" \
  -e "s|127.0.0.1:5000|127.0.0.1:${UPSTREAM_PORT}|g" \
  "$TEMPLATE_PATH" > "$SITE_PATH"

ln -sf "$SITE_PATH" "$ENABLED_PATH"
nginx -t
systemctl reload nginx

echo "Installed nginx site: $SERVICE_NAME"
echo "Server name        : $SERVER_NAME"
echo "Upstream           : 127.0.0.1:${UPSTREAM_PORT}"
echo "Config path        : $SITE_PATH"
