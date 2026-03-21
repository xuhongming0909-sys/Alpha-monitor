const DEFAULT_BASE_URL = process.env.ALPHA_MONITOR_BASE_URL || `http://127.0.0.1:${process.env.PORT || 5000}`;

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
