#!/usr/bin/env bash
set -euo pipefail

# 安装正式的 systemd 服务，使 Alpha Monitor 在服务器上长期在线。
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVICE_NAME="${1:-alpha-monitor}"
SERVICE_USER="${SUDO_USER:-${USER}}"
TEMPLATE_PATH="$PROJECT_ROOT/tools/deploy/alpha-monitor.service"
TARGET_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

mkdir -p "$PROJECT_ROOT/runtime_logs" "$PROJECT_ROOT/runtime_data"
chown -R "${SERVICE_USER}:${SERVICE_USER}" "$PROJECT_ROOT/runtime_logs" "$PROJECT_ROOT/runtime_data"

sed \
  -e "s|__PROJECT_ROOT__|${PROJECT_ROOT}|g" \
  -e "s|__SERVICE_USER__|${SERVICE_USER}|g" \
  "$TEMPLATE_PATH" > "$TARGET_PATH"

chmod 644 "$TARGET_PATH"
chmod +x "$PROJECT_ROOT/tools/deploy/start_linux.sh"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Installed systemd service: $SERVICE_NAME"
echo "Check status with: sudo systemctl status $SERVICE_NAME"
