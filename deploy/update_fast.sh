#!/usr/bin/env bash
set -euo pipefail

# Fast deploy keeps git sync / restart / health / marker checks,
# but skips dependency installation and import verification.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec env \
  DEPLOY_MODE="${DEPLOY_MODE:-fast}" \
  bash "$SCRIPT_DIR/update_from_github.sh"
