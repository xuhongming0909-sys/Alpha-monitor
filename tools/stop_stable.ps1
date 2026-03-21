$ErrorActionPreference = 'Stop'

$targetPort = 5000
$projectRoot = Split-Path -Parent $PSScriptRoot
$logDir = Join-Path $projectRoot 'runtime_logs'
$runnerPidFile = Join-Path $logDir 'watcher.pid'
$appPidFile = Join-Path $logDir 'server.pid'

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

function Stop-TrackedProcess {
  param(
    [string]$Label,
    [string]$PidFile
  )

  $pidValue = Get-PidFromFile $PidFile
  if (-not $pidValue) {
    return 0
  }

  $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
  if (-not $proc) {
    Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
    return 0
  }

  Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
  Write-Host "Stopped $Label PID=$pidValue"
  Start-Sleep -Milliseconds 300
  Remove-Item -Path $PidFile -Force -ErrorAction SilentlyContinue
  return 1
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

[int]$stopped = 0
$stopped += Stop-TrackedProcess 'Alpha Monitor watcher' $runnerPidFile
$stopped += Stop-TrackedProcess 'Alpha Monitor' $appPidFile

$managedWatcherIds = @(Get-ManagedNodeProcessIds '*keep_running.js*')
foreach ($procId in $managedWatcherIds) {
  Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
  Write-Output "Stopped Alpha Monitor watcher PID=$procId"
  $stopped++
}

$managedServerIds = @(Get-ManagedNodeProcessIds '*start_server.js*')
foreach ($procId in $managedServerIds) {
  Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
  Write-Output "Stopped Alpha Monitor server PID=$procId"
  $stopped++
}

 $listenerProcIds = Get-ListeningProcessIds $targetPort
if ($listenerProcIds) {
  foreach ($procId in $listenerProcIds) {
    $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
    if ($proc -and $proc.ProcessName -eq 'node') {
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
      Write-Output "Stopped Alpha Monitor PID=$procId"
      $stopped++
    } else {
      $name = if ($proc) { $proc.ProcessName } else { 'unknown' }
      Write-Output "Skipped PID=$procId ($name)."
    }
  }
}

if ($stopped -eq 0) {
  Write-Output "No listener on port $targetPort."
}

