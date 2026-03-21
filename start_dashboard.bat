@echo off
setlocal
cd /d "%~dp0"

echo [Alpha Monitor] Project root: %cd%
echo [Alpha Monitor] Official start entry: start_dashboard.bat
echo [Alpha Monitor] Starting watcher...
powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\start_stable.ps1"

if errorlevel 1 (
  echo.
  echo Alpha Monitor failed to start.
  echo Please review runtime_logs and try again.
  pause >nul
  exit /b 1
)

echo Alpha Monitor is ready.
powershell -NoProfile -ExecutionPolicy Bypass -File ".\tools\show_access_info.ps1"
for /f "usebackq delims=" %%i in (`node -e "const { getConfig } = require('./shared/config/node_config'); const port = Number(getConfig()?.app?.port || 5000); process.stdout.write('http://127.0.0.1:' + port + '/');"`) do set "ALPHA_MONITOR_LOCAL_URL=%%i"
start "" "%ALPHA_MONITOR_LOCAL_URL%"
exit /b 0
