const { getConfig } = require('../shared/config/node_config');

function normalizeBaseUrl(value) {
  const text = String(value || '').trim();
  if (/^\$\{.+\}$/.test(text)) return '';
  return text ? text.replace(/\/+$/, '') : '';
}

function resolveDefaultBaseUrl() {
  const explicit = normalizeBaseUrl(process.env.ALPHA_MONITOR_BASE_URL || process.env.PUBLIC_BASE_URL);
  if (explicit) return explicit;

  const config = getConfig();
  const port = Number(config?.app?.port || process.env.PORT || 5000);
  const publicBaseUrl = normalizeBaseUrl(config?.deployment?.public_base_url);
  if (publicBaseUrl) return publicBaseUrl;

  const serverBaseUrl = normalizeBaseUrl(config?.app?.server_base_url);
  if (serverBaseUrl) return serverBaseUrl;

  return `http://127.0.0.1:${port}`;
}

const DEFAULT_BASE_URL = resolveDefaultBaseUrl();

async function fetchJson(url) {
  const response = await fetch(url);
  const text = await response.text();
  let payload = null;
  try {
    payload = JSON.parse(text);
  } catch {
    payload = { raw: text };
  }
  return { response, payload };
}

async function main() {
  const baseUrl = DEFAULT_BASE_URL.replace(/\/+$/, '');
  const healthUrl = `${baseUrl}/api/health`;
  const homeUrl = `${baseUrl}/`;

  const homeResponse = await fetch(homeUrl);
  if (!homeResponse.ok) {
    throw new Error(`homepage check failed: HTTP ${homeResponse.status}`);
  }

  const { response, payload } = await fetchJson(healthUrl);
  if (!response.ok) {
    throw new Error(`health check failed: HTTP ${response.status}`);
  }

  const health = payload && typeof payload === 'object' && payload.data ? payload.data : payload;
  const webStatus = health?.sections?.web?.status;
  if (webStatus !== 'ok') {
    throw new Error(`health endpoint reachable but web status is ${webStatus || 'unknown'}`);
  }

  console.log(`homepage ok: ${homeUrl}`);
  console.log(`health ok  : ${healthUrl}`);
  console.log(`overall    : ${health?.status || 'unknown'}`);
  console.log(`web        : ${webStatus}`);
}

main().catch((error) => {
  console.error('smoke failed:', error.message);
  process.exit(1);
});
