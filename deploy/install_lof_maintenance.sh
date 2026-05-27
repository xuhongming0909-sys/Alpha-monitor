#!/usr/bin/env bash
set -euo pipefail

# AI-SUMMARY: LOF维护定时任务部署脚本
# 对应 INDEX.md §9.3 文件摘要索引

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_FILE="$SCRIPT_DIR/lof_maintenance.service"
TIMER_FILE="$SCRIPT_DIR/lof_maintenance.timer"

echo "[lof-timer] 部署 LOF 维护定时任务..."

# 复制 service 和 timer 到 systemd
sudo cp "$SERVICE_FILE" /etc/systemd/system/alpha-lof-maintenance.service
sudo cp "$TIMER_FILE" /etc/systemd/system/alpha-lof-maintenance.timer

# 重载 systemd
sudo systemctl daemon-reload

# 启用并启动 timer
sudo systemctl enable alpha-lof-maintenance.timer
sudo systemctl start alpha-lof-maintenance.timer

echo "[lof-timer] 定时任务已部署"
echo "  服务: alpha-lof-maintenance.service"
echo "  定时器: alpha-lof-maintenance.timer"
echo "  执行时间: 每天 06:30 (服务器时间)"
echo ""
echo "查看状态: systemctl status alpha-lof-maintenance.timer"
echo "查看日志: journalctl -u alpha-lof-maintenance.service -f"
echo "手动执行: systemctl start alpha-lof-maintenance.service"