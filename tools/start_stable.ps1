$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
$runnerScriptArg = '.\tools\keep_running.js'
$logDir = Join-Path $projectRoot 'runtime_logs'
$runnerLog = Join-Path $logDir 'watcher.log'
$stdoutLog = Join-Path $logDir 'server_stdout.log'
$stderrLog = Join-Path $logDir 'server_stderr.log'
$runnerPidFile = Join-Path $logDir 'watcher.pid'
$appPidFile = Join-Path $logDir 'server.pid'
$nodeCommand = Get-Command node -ErrorAction Stop
$nodePath = $nodeCommand.Source

function Get-AlphaMonitorRuntimeConfig {
  $json = @'
const { getConfig } = require('./shared/config/node_config');
const config = getConfig();
const port = Number(config?.app?.port || 5000);
const healthPath = String(
  config?.deployment?.healthcheck?.public_path ||
  config?.app?.healthcheck_path ||
  '/api/health'
).trim();
const normalizedHealthPath = healthPath.startsWith('/') ? healthPath : `/${healthPath}`;
const publicBaseUrl = String(
  config?.deployment?.public_base_url ||
  config?.app?.server_base_url ||
  `http://127.0.0.1:${port}`
).trim() || `http://127.0.0.1:${port}`;

process.stdout.write(JSON.stringify({
  port,
  localBaseUrl: `http://127.0.0.1:${port}`,
  localHealthUrl: `http://127.0.0.1:${port}${normalizedHealthPath}`,
  publicBaseUrl,
  publicHealthUrl: `${publicBaseUrl.replace(/\/+$/, '')}${normalizedHealthPath}`
}));
'@ | node -

  return $json | ConvertFrom-Json
}

$runtimeConfig = Get-AlphaMonitorRuntimeConfig
$targetPort = [int]$runtimeConfig.port
$healthUrl = $runtimeConfig.localHealthUrl
$localBaseUrl = $runtimeConfig.localBaseUrl
$publicBaseUrl = $runtimeConfig.publicBaseUrl
$publicHealthUrl = $runtimeConfig.publicHealthUrl

if (-not (Test-Path (Join-Path $projectRoot 'package.json'))) {
  throw "package.json not found in $projectRoot"
}

New-Item -ItemType Directory -Path $logDir -Force | Out-Null

function Get-PidFromFile {
  param([string]$Path)
  if (-not (Test-Path $Path)) {
    return $null
  }

  $raw = (Get-Content -Path $Path -Raw -ErrorAction SilentlyContinue).Trim()
  if (-not $raw) {
    return $null
  }

  $pidValue = 0
  if ([int]::TryParse($raw, [ref]$pidValue)) {
    return $pidValue
  }

  return $null
}

function Test-ProcessAlive {
  param([int]$ProcessId)
  if (-not $ProcessId) {
    return $false
  }

  return [bool](Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)
}

function Remove-StalePidFile {
  param([string]$Path)
  $pidValue = Get-PidFromFile $Path
  if ($pidValue -and -not (Test-ProcessAlive $pidValue)) {
    Remove-Item -Path $Path -Force -ErrorAction SilentlyContinue
  }
}

function Test-ServiceHealthy {
  try {
    $statusCode = & curl.exe -s -o NUL -w '%{http_code}' $healthUrl
    return $statusCode -eq '200'
  } catch {
    return $false
  }
}

function Write-RecentLog {
  param(
    [string]$Path,
    [string]$Label
  )

  if (-not (Test-Path $Path)) {
    Write-Output "[$Label] log file not found: $Path"
    return
  }

  Write-Output "[$Label] recent log:"
  Get-Content -Path $Path -Tail 20 -ErrorAction SilentlyContinue
}

function Get-ListeningProcessIds {
  param([int]$Port)

  $matches = @()
  $lines = & netstat -ano -p tcp | Select-String -Pattern (":$Port\s+.*LISTENING\s+(\d+)$")
  foreach ($line in $lines) {
    if ($line.Matches.Count -gt 0) {
      $matches += [int]$line.Matches[0].Groups[1].Value
    }
  }

  return $matches | Select-Object -Unique
}

function Get-ManagedNodeProcessIds {
  param([string]$Pattern)

  $items = Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like $Pattern } |
    ForEach-Object { [int]$_.ProcessId }

  return $items | Select-Object -Unique
}

Remove-StalePidFile $runnerPidFile
Remove-StalePidFile $appPidFile

Write-Output "Project root : $projectRoot"
Write-Output "Node path    : $nodePath"
Write-Output "Health URL   : $healthUrl"
Write-Output "Local URL    : $localBaseUrl"
Write-Output "Public URL   : $publicBaseUrl"
Write-Output "Public health: $publicHealthUrl"
Write-Output "Logs         : $logDir"

$watcherProcIds = @(Get-ManagedNodeProcessIds '*keep_running.js*')
if ($watcherProcIds.Count -gt 0 -and (Test-ServiceHealthy)) {
  if ($watcherProcIds.Count -gt 1) {
    $extraWatcherIds = @($watcherProcIds | Select-Object -Skip 1)
    Write-Output "Found duplicate watcher processes: $($watcherProcIds -join ', '). Keeping PID=$($watcherProcIds[0])."
    foreach ($procId in $extraWatcherIds) {
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
  }
  Set-Content -Path $runnerPidFile -Value $watcherProcIds[0]
  Write-Output "Alpha Monitor watcher already running PID=$($watcherProcIds[0])"
  Write-Output "Service is ready: $localBaseUrl/"
  exit 0
}

if ($watcherProcIds.Count -gt 0 -and -not (Test-ServiceHealthy)) {
  Write-Output "Found unhealthy watcher process(es): $($watcherProcIds -join ', '). Restarting them."
  foreach ($procId in $watcherProcIds) {
    Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
  }
  Start-Sleep -Milliseconds 500
  Remove-Item -Path $runnerPidFile -Force -ErrorAction SilentlyContinue
  Remove-Item -Path $appPidFile -Force -ErrorAction SilentlyContinue
}

$runnerPid = Get-PidFromFile $runnerPidFile
if ($runnerPid -and (Test-ProcessAlive $runnerPid) -and (Test-ServiceHealthy)) {
  Write-Output "Alpha Monitor watcher already running PID=$runnerPid"
  Write-Output "Service is ready: $localBaseUrl/"
  exit 0
}

if ($runnerPid -and (Test-ProcessAlive $runnerPid) -and -not (Test-ServiceHealthy)) {
  Write-Output "Watcher PID=$runnerPid exists but health check is failing. Restarting watcher."
  Stop-Process -Id $runnerPid -Force -ErrorAction SilentlyContinue
  Start-Sleep -Milliseconds 500
  Remove-Item -Path $runnerPidFile -Force -ErrorAction SilentlyContinue
  Remove-Item -Path $appPidFile -Force -ErrorAction SilentlyContinue
}

$listenerProcIds = Get-ListeningProcessIds $targetPort
if ($listenerProcIds) {
  foreach ($procId in $listenerProcIds) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc -and $proc.ProcessName -eq 'node') {
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
      Write-Output "Stopped old start_server.js process PID=$procId"
    } else {
      $name = if ($proc) { $proc.ProcessName } else { 'unknown' }
      Write-Output "Port $targetPort is used by PID=$procId ($name)."
      Write-Output "Please free this port manually, then retry."
      exit 1
    }
  }
}

$proc = Start-Process -FilePath $nodePath `
    -ArgumentList @($runnerScriptArg) `
    -WorkingDirectory $projectRoot `
    -WindowStyle Minimized `
    -PassThru
Write-Output "Started Alpha Monitor watcher PID=$($proc.Id)"

$ok = $false
for ($i = 0; $i -lt 60; $i++) {
  Start-Sleep -Milliseconds 500
  if (Test-ServiceHealthy) {
    $ok = $true
    break
  }

  $currentRunnerPid = Get-PidFromFile $runnerPidFile
  if ($currentRunnerPid -and -not (Test-ProcessAlive $currentRunnerPid)) {
    break
  }
}

if (-not $ok) {
  Write-Output 'Service started but health check failed.'
  Write-RecentLog -Path $runnerLog -Label 'watcher'
  Write-RecentLog -Path $stderrLog -Label 'server_stderr'
  Write-RecentLog -Path $stdoutLog -Label 'server_stdout'
  exit 1
}

Write-Output "Service is ready: $localBaseUrl/"
