import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("43.139.35.190", port=22, username="ubuntu", password="DellG77588")

# ?????????????BOM???
content = """#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

mkdir -p runtime_logs runtime_data

if [[ -n "${NODE_BIN:-}" ]]; then
  RESOLVED_NODE_BIN="$NODE_BIN"
else
  RESOLVED_NODE_BIN="$(command -v node || true)"
  if [[ -z "$RESOLVED_NODE_BIN" ]] && [[ -x "/usr/bin/node" ]]; then
    RESOLVED_NODE_BIN="/usr/bin/node"
  fi
  if [[ -z "$RESOLVED_NODE_BIN" ]] && [[ -x "/usr/local/bin/node" ]]; then
    RESOLVED_NODE_BIN="/usr/local/bin/node"
  fi
fi

if [[ -z "${RESOLVED_NODE_BIN:-}" ]]; then
  echo "[start_linux][error] node binary not found in PATH and common locations" >&2
  exit 1
fi

export NODE_ENV="${NODE_ENV:-production}"

exec "$RESOLVED_NODE_BIN" start_server.js
"""

sftp = ssh.open_sftp()
with sftp.file("/home/ubuntu/Alpha monitor/tools/deploy/start_linux.sh", "w") as f:
    f.write(content)
sftp.chmod("/home/ubuntu/Alpha monitor/tools/deploy/start_linux.sh", 0o755)
sftp.close()
print("Written start_linux.sh (no BOM)")

# ??
stdin, stdout, stderr = ssh.exec_command("sudo systemctl restart alpha-monitor")
stdout.read()
time.sleep(15)

stdin, stdout, stderr = ssh.exec_command("sudo systemctl is-active alpha-monitor")
status = stdout.read().decode().strip()
print(f"Service: {status}")

ssh.close()
