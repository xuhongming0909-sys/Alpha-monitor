# AI-SUMMARY: Windows PowerShell 版服务器同步脚本
# 用法: .\deploy\sync_server.ps1

$ErrorActionPreference = "Stop"

$PROJECT_DIR = "/home/ubuntu/Alpha monitor"
$TARGET_BRANCH = "main"
$SERVICE_NAME = "alpha-monitor"
$REPO_URL = "https://github.com/xuhongming0909-sys/Alpha-monitor.git"
$SSH_HOST = "ubuntu@43.139.35.190"
$SSH_KEY = "$env:USERPROFILE\.ssh\alpha_monitor_deploy_key"

function Log($msg) { Write-Host "[sync] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "[sync][warn] $msg" -ForegroundColor Yellow }
function Die($msg) { Write-Host "[sync][error] $msg" -ForegroundColor Red; exit 1 }

function Invoke-Remote($cmd) {
    ssh -i $SSH_KEY -o StrictHostKeyChecking=no $SSH_HOST $cmd
}

Log "开始同步到服务器..."

# 1. 修复 git 协议
Invoke-Remote "cd '$PROJECT_DIR' && current=`$(git remote get-url origin 2>/dev/null) && if [[ '`$current' == git://* ]]; then git remote set-url origin '$REPO_URL'; echo '协议已修复'; fi"

# 2. 切到目标分支
Invoke-Remote "cd '$PROJECT_DIR' && git checkout '$TARGET_BRANCH' 2>/dev/null || git checkout -b '$TARGET_BRANCH'"

# 3. Stash 本地修改
Invoke-Remote "cd '$PROJECT_DIR' && if ! git diff --quiet HEAD 2>/dev/null; then git stash push -m 'auto-stash-before-sync'; echo 'STASHED'; else echo 'CLEAN'; fi"

# 4. Fetch + Merge
Log "拉取远程..."
$result = Invoke-Remote "cd '$PROJECT_DIR' && git fetch origin '$TARGET_BRANCH' && git merge 'origin/$TARGET_BRANCH' --no-edit -m 'sync: auto-merge' && git log --oneline -3"
Write-Host $result

# 5. 恢复 stash
Invoke-Remote "cd '$PROJECT_DIR' && git stash pop --quiet 2>/dev/null || echo 'stash pop 有冲突'"

# 6. 重启服务
Log "重启服务..."
Invoke-Remote "sudo systemctl restart '$SERVICE_NAME' && sleep 2 && systemctl is-active '$SERVICE_NAME'"

Log "同步完成"