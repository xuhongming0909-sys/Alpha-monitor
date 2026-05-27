#!/usr/bin/env bash
set -euo pipefail

# AI-SUMMARY: 服务器 git 同步脚本，处理协议修复/stash/冲突/重启全流程
# 由 Codex skill sync-alpha-server 调用

PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/Alpha monitor}"
TARGET_BRANCH="${TARGET_BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-alpha-monitor}"
REPO_URL="https://github.com/xuhongming0909-sys/Alpha-monitor.git"
BACKUP_DIR="/tmp/server_backup_$(date +%s)"

log()  { printf '[sync] %s\n' "$1"; }
warn() { printf '[sync][warn] %s\n' "$1" >&2; }
die()  { printf '[sync][error] %s\n' "$1" >&2; exit 1; }

cd "$PROJECT_DIR" || die "项目目录不存在: $PROJECT_DIR"

# 1. 修复 git:// 协议（GitHub 已废弃）
current_url=$(git remote get-url origin 2>/dev/null || echo "")
if [[ "$current_url" == git://* ]]; then
  log "修复协议: git:// -> https://"
  git remote set-url origin "$REPO_URL"
fi

# 2. 切到目标分支
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "$TARGET_BRANCH" ]]; then
  log "切换分支: $current_branch -> $TARGET_BRANCH"
  git checkout "$TARGET_BRANCH" 2>/dev/null || git checkout -b "$TARGET_BRANCH" "origin/$TARGET_BRANCH"
fi

# 3. Stash 本地修改
if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet HEAD 2>/dev/null; then
  log "暂存本地修改..."
  git stash push -m "auto-stash before sync $(date +%Y%m%d_%H%M%S)"
  STASHED=1
else
  STASHED=0
fi

# 4. 处理未跟踪文件冲突
CONFLICT_FILES=$(git ls-files --others --exclude-standard 2>/dev/null || true)
if [[ -n "$CONFLICT_FILES" ]]; then
  mkdir -p "$BACKUP_DIR"
  while IFS= read -r f; do
    if git cat-file -e HEAD:"$f" 2>/dev/null; then
      mv "$f" "$BACKUP_DIR/"
      warn "冲突文件已备份: $f -> $BACKUP_DIR/"
    fi
  done <<< "$CONFLICT_FILES"
fi

# 5. Fetch + Merge
log "拉取远程..."
git fetch origin "$TARGET_BRANCH"
BEFORE=$(git rev-parse HEAD)
git merge "origin/$TARGET_BRANCH" --no-edit -m "sync: auto-merge from origin/$TARGET_BRANCH"
AFTER=$(git rev-parse HEAD)

if [[ "$BEFORE" == "$AFTER" ]]; then
  log "已是最新，无新提交"
else
  NEW_COMMITS=$(git rev-list "$BEFORE".."$AFTER" --count)
  log "合并完成，新增 $NEW_COMMITS 个提交"
fi

# 6. 恢复 stash
if [[ "$STASHED" -eq 1 ]]; then
  log "恢复暂存修改..."
  git stash pop --quiet 2>/dev/null || warn "stash pop 有冲突，手动处理"
fi

# 7. 重启服务（如果在运行）
if systemctl is-active "$SERVICE_NAME" &>/dev/null; then
  log "重启服务: $SERVICE_NAME"
  systemctl restart "$SERVICE_NAME"
  sleep 2
  if systemctl is-active "$SERVICE_NAME" &>/dev/null; then
    log "服务运行正常"
  else
    die "服务重启失败"
  fi
fi

# 8. 输出最终状态
echo "---STATUS---"
git log --oneline -3
echo "---BRANCH---"
git branch -vv | head -3
log "同步完成"