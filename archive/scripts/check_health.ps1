param(
  [string]$Url = '',
  [int]$TimeoutSec = 5
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

function Get-DefaultHealthUrl {
  if ($env:ALPHA_MONITOR_HEALTH_URL) {
    return $env:ALPHA_MONITOR_HEALTH_URL
  }

  $json = @'
const { getConfig } = require('./shared/config/node_config');
const config = getConfig();
const port = Number(config?.app?.port || 5000);
const normalizeBaseUrl = (value) => {
  const text = String(value || '').trim();
  if (/^\$\{.+\}$/.test(text)) return '';
  return text ? text.replace(/\/+$/, '') : '';
};
const healthPath = String(
  config?.deployment?.healthcheck?.public_path ||
  config?.app?.healthcheck_path ||
  '/api/health'
).trim();
const normalizedHealthPath = healthPath.startsWith('/') ? healthPath : `/${healthPath}`;
const publicBaseUrl = normalizeBaseUrl(
  process.env.PUBLIC_BASE_URL ||
  config?.deployment?.public_base_url
);
const serverBaseUrl = normalizeBaseUrl(config?.app?.server_base_url);
const baseUrl = publicBaseUrl || serverBaseUrl || `http://127.0.0.1:${port}`;

process.stdout.write(JSON.stringify({
  url: `${baseUrl}${normalizedHealthPath}`
}));
'@ | node -

  return ($json | ConvertFrom-Json).url
}

if (-not $Url) {
  $Url = Get-DefaultHealthUrl
}

try {
  $response = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec $TimeoutSec
  $payload = if ($null -ne $response.data) { $response.data } else { $response }
  $webStatus = $payload.sections.web.status

  Write-Output "Health URL   : $Url"
  Write-Output "Overall      : $($payload.status)"
  Write-Output "Web          : $webStatus"
  Write-Output "Data Jobs    : $($payload.sections.data_jobs.status)"
  Write-Output "Push         : $($payload.sections.push_scheduler.status)"
  $payload | ConvertTo-Json -Depth 8

  if ($webStatus -eq 'ok') {
    exit 0
  }

  Write-Error "Web health is not ok. Current web status: $webStatus"
  exit 1
} catch {
  Write-Error "Health check failed for $Url : $($_.Exception.Message)"
  Write-Output 'Hint        : check process status, reverse proxy config, firewall, and /api/health exposure.'
  exit 1
}
