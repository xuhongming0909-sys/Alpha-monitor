param(
  [int]$Port = 5000,
  [string]$RuleName = 'Alpha Monitor 5000'
)

$ErrorActionPreference = 'Stop'

$existing = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
if ($existing) {
  Set-NetFirewallRule -DisplayName $RuleName -Enabled True -Direction Inbound -Action Allow | Out-Null
  Write-Output "Firewall rule already exists and is enabled: $RuleName"
  exit 0
}

New-NetFirewallRule `
  -DisplayName $RuleName `
  -Direction Inbound `
  -Action Allow `
  -Enabled True `
  -Protocol TCP `
  -LocalPort $Port | Out-Null

Write-Output "Firewall rule installed: $RuleName (TCP $Port)"
