#!/usr/bin/env bash
set -euo pipefail

# Fast deploy is only for dependency-unchanged releases.
# It keeps git sync / restart / health / marker checks,
# and delegates all real deploy logic to the full script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec env \
  INSTALL_NODE_MODULES="${INSTALL_NODE_MODULES:-0}" \
  INSTALL_PYTHON_REQUIREMENTS="${INSTALL_PYTHON_REQUIREMENTS:-0}" \
  VERIFY_PYTHON_IMPORTS="${VERIFY_PYTHON_IMPORTS:-0}" \
  bash "$SCRIPT_DIR/update_from_github.sh"
