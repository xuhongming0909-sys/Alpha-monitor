#!/usr/bin/env bash
set -euo pipefail

# Install the bundled Caddy reverse-proxy template for Alpha Monitor.
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMPLATE_PATH="$PROJECT_ROOT/tools/deploy/Caddyfile"
SERVER_NAME="${1:-YOUR_DOMAIN_OR_IP}"
UPSTREAM_PORT="${2:-5000}"
TARGET_PATH="/etc/caddy/Caddyfile"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Template not found: $TEMPLATE_PATH" >&2
  exit 1
fi

if ! command -v caddy >/dev/null 2>&1; then
  echo "caddy is not installed. Please install caddy first." >&2
  exit 1
fi

sed \
  -e "s|YOUR_DOMAIN_OR_IP|${SERVER_NAME}|g" \
  -e "s|127.0.0.1:5000|127.0.0.1:${UPSTREAM_PORT}|g" \
  "$TEMPLATE_PATH" > "$TARGET_PATH"

caddy validate --config "$TARGET_PATH"
systemctl reload caddy

echo "Installed Caddy config"
echo "Server name        : $SERVER_NAME"
echo "Upstream           : 127.0.0.1:${UPSTREAM_PORT}"
echo "Config path        : $TARGET_PATH"
