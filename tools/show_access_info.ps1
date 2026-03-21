$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

function Get-AlphaMonitorConfig {
  $json = @'
const { getConfig } = require('./shared/config/node_config');
const config = getConfig();
const port = Number(config?.app?.port || 5000);
const host = String(config?.app?.host || '0.0.0.0').trim() || '0.0.0.0';
const healthPath = String(
  config?.deployment?.healthcheck?.public_path ||
  config?.app?.healthcheck_path ||
  '/api/health'
).trim();
const normalizedHealthPath = healthPath.startsWith('/') ? healthPath : `/${healthPath}`;
const serverBaseUrl = String(config?.app?.server_base_url || `http://127.0.0.1:${port}`).trim() || `http://127.0.0.1:${port}`;
const publicBaseUrl = String(config?.deployment?.public_base_url || serverBaseUrl).trim() || serverBaseUrl;
const reverseProxyEnabled = Boolean(config?.deployment?.reverse_proxy?.enabled);
const reverseProxyType = String(config?.deployment?.reverse_proxy?.type || 'none').trim() || 'none';

process.stdout.write(JSON.stringify({
  port,
  host,
  serverBaseUrl,
  publicBaseUrl,
  healthPath: normalizedHealthPath,
  publicHealthUrl: `${publicBaseUrl.replace(/\/+$/, '')}${normalizedHealthPath}`,
  reverseProxyEnabled,
  reverseProxyType
}));
'@ | node -

  return $json | ConvertFrom-Json
}

$cfg = Get-AlphaMonitorConfig
$port = [int]$cfg.port
$localBaseUrl = "http://127.0.0.1:$port"
$localHealthUrl = "$localBaseUrl$($cfg.healthPath)"

$addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
  Where-Object { $_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown' } |
  Select-Object -ExpandProperty IPAddress -Unique

Write-Output 'Alpha Monitor access information:'
Write-Output "Project root        : $projectRoot"
Write-Output "Configured host     : $($cfg.host)"
Write-Output "Configured port     : $port"
Write-Output "Local homepage      : $localBaseUrl/"
Write-Output "Local health        : $localHealthUrl"
Write-Output "Configured app URL  : $($cfg.serverBaseUrl)"
Write-Output "Public homepage     : $($cfg.publicBaseUrl)"
Write-Output "Public health       : $($cfg.publicHealthUrl)"
Write-Output "Reverse proxy       : enabled=$($cfg.reverseProxyEnabled) type=$($cfg.reverseProxyType)"

if (-not $addresses) {
  Write-Output 'LAN homepage        : not detected'
  exit 0
}

foreach ($ip in $addresses) {
  Write-Output "LAN homepage        : http://$ip`:$port/"
}
