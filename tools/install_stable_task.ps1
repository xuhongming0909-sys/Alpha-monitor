$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$taskName = 'AlphaMonitorStable'
$startScript = Join-Path $PSScriptRoot 'start_stable.ps1'
$powerShell = (Get-Command powershell.exe -ErrorAction Stop).Source
$workingCommand = "& '$startScript'"

$action = New-ScheduledTaskAction `
  -Execute $powerShell `
  -Argument "-NoProfile -ExecutionPolicy Bypass -Command $workingCommand"

$triggers = @(
  (New-ScheduledTaskTrigger -AtLogOn),
  (New-ScheduledTaskTrigger -AtStartup)
)

$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -MultipleInstances IgnoreNew `
  -RestartCount 3 `
  -RestartInterval (New-TimeSpan -Minutes 1) `
  -StartWhenAvailable

Register-ScheduledTask `
  -TaskName $taskName `
  -Action $action `
  -Trigger $triggers `
  -Settings $settings `
  -Description 'Alpha Monitor stable watcher bootstrapper' `
  -Force | Out-Null

Write-Output "Installed scheduled task: $taskName"
Write-Output "Project root: $projectRoot"
