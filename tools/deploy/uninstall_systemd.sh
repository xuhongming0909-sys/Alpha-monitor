#!/usr/bin/env bash
set -euo pipefail

# 卸载正式的 systemd 服务。
SERVICE_NAME="${1:-alpha-monitor}"
TARGET_PATH="/etc/systemd/system/${SERVICE_NAME}.service"

if [[ "${EUID}" -ne 0 ]]; then
  exec sudo bash "$0" "$@"
fi

systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true
rm -f "$TARGET_PATH"
systemctl daemon-reload

echo "Removed systemd service: $SERVICE_NAME"
