@echo off
setlocal
cd /d "%~dp0"

echo Stopping Alpha Monitor...
powershell -ExecutionPolicy Bypass -File ".\tools\stop_stable.ps1"
pause
