param(
  [string]$RuleName = 'Alpha Monitor 5000'
)

$ErrorActionPreference = 'Stop'

$existing = Get-NetFirewallRule -DisplayName $RuleName -ErrorAction SilentlyContinue
if (-not $existing) {
  Write-Output "Firewall rule not found: $RuleName"
  exit 0
}

Remove-NetFirewallRule -DisplayName $RuleName
Write-Output "Firewall rule removed: $RuleName"
