const API_ENDPOINTS = {
  health: '/api/health',
  uiConfig: '/api/dashboard/ui-config',
  resourceStatus: '/api/dashboard/resource-status',
  cbArb: '/api/market/convertible-bond-arbitrage',
  ah: '/api/market/ah',
  ab: '/api/market/ab',
  lofArb: '/api/market/lof-arbitrage',
  monitor: '/api/monitors',
};

const NUMBER_FORMAT = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 });
const PERCENT_FORMAT = new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function unwrap(payload, fallback) {
  if (!payload || typeof payload !== 'object') return fallback;
  if ('data' in payload) return payload.data ?? fallback;
  return payload;
}

async function fetchJson(url) {
  const response = await fetch(url, { headers: { Accept: 'application/json' } });
  const text = await response.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = { raw: text };
  }
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return payload;
}

function toArray(value) {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.data)) return value.data;
  if (Array.isArray(value?.rows)) return value.rows;
  return [];
}

function toNumber(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatNumber(value, suffix = '') {
  const number = toNumber(value);
  return number === null ? '--' : `${NUMBER_FORMAT.format(number)}${suffix}`;
}

function formatPercent(value) {
  const number = toNumber(value);
  return number === null ? '--' : `${PERCENT_FORMAT.format(number)}%`;
}

function formatTime(value) {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleTimeString('zh-CN', { hour12: false });
}

function signedClass(value) {
  const number = toNumber(value);
  if (number === null || number === 0) return 'is-flat';
  return number > 0 ? 'is-up' : 'is-down';
}

function pickText(...values) {
  for (const value of values) {
    const text = String(value ?? '').trim();
    if (text) return text;
  }
  return '--';
}

function buildOpportunityRows(resources) {
  const rows = [];
  const cbPayload = resources.cbArb.data || {};
  const cbRows = [
    ...toArray(cbPayload.data),
    ...toArray(cbPayload.smallRedemption?.rows),
  ];
  cbRows
    .filter((row) => toNumber(row.premiumRate) !== null || toNumber(row.doubleLow) !== null)
    .sort((a, b) => (toNumber(a.premiumRate) ?? 999) - (toNumber(b.premiumRate) ?? 999))
    .slice(0, 8)
    .forEach((row) => rows.push({
      source: '转债',
      name: pickText(row.bondName, row.name),
      code: pickText(row.code, row.bondCode),
      metric: '溢价率',
      value: formatPercent(row.premiumRate),
      rawValue: toNumber(row.premiumRate),
      risk: `双低 ${formatNumber(row.doubleLow)}`,
      quote: formatNumber(row.price),
    }));

  toArray(resources.ah.data)
    .filter((row) => toNumber(row.premium) !== null)
    .sort((a, b) => Math.abs(toNumber(b.premium) ?? 0) - Math.abs(toNumber(a.premium) ?? 0))
    .slice(0, 5)
    .forEach((row) => rows.push({
      source: 'AH',
      name: pickText(row.aName, row.name),
      code: pickText(row.aCode, row.code),
      metric: '溢价',
      value: formatPercent(row.premium),
      rawValue: toNumber(row.premium),
      risk: pickText(row.hName, row.hCode),
      quote: formatNumber(row.aPrice),
    }));

  toArray(resources.ab.data)
    .filter((row) => toNumber(row.premium) !== null)
    .sort((a, b) => Math.abs(toNumber(b.premium) ?? 0) - Math.abs(toNumber(a.premium) ?? 0))
    .slice(0, 5)
    .forEach((row) => rows.push({
      source: 'AB',
      name: pickText(row.aName, row.name),
      code: pickText(row.aCode, row.code),
      metric: '溢价',
      value: formatPercent(row.premium),
      rawValue: toNumber(row.premium),
      risk: pickText(row.bName, row.bCode),
      quote: formatNumber(row.aPrice),
    }));

  toArray(resources.lofArb.data)
    .filter((row) => toNumber(row.premiumRate) !== null)
    .sort((a, b) => Math.abs(toNumber(b.premiumRate) ?? 0) - Math.abs(toNumber(a.premiumRate) ?? 0))
    .slice(0, 5)
    .forEach((row) => rows.push({
      source: 'LOF',
      name: pickText(row.name, row.fundName),
      code: pickText(row.code, row.fundCode),
      metric: '溢价率',
      value: formatPercent(row.premiumRate),
      rawValue: toNumber(row.premiumRate),
      risk: pickText(row.indexName, row.market),
      quote: formatNumber(row.price, ''),
    }));

  return rows.slice(0, 18);
}

function useDashboardData() {
  const [state, setState] = React.useState({ loading: true, error: '', resources: null, updatedAt: '' });

  const load = React.useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: '' }));
    try {
      const [health, uiConfig, resourceStatus, cbArb, ah, ab, lofArb, monitor] = await Promise.all([
        fetchJson(API_ENDPOINTS.health),
        fetchJson(API_ENDPOINTS.uiConfig),
        fetchJson(`${API_ENDPOINTS.resourceStatus}?keys=exchangeRate,cbArb,ah,ab,lofArb`),
        fetchJson(API_ENDPOINTS.cbArb),
        fetchJson(API_ENDPOINTS.ah),
        fetchJson(API_ENDPOINTS.ab),
        fetchJson(API_ENDPOINTS.lofArb),
        fetchJson(API_ENDPOINTS.monitor),
      ]);
      setState({
        loading: false,
        error: '',
        updatedAt: new Date().toISOString(),
        resources: {
          health: { data: unwrap(health, {}) },
          uiConfig: { data: unwrap(uiConfig, {}) },
          resourceStatus: { data: unwrap(resourceStatus, {}) },
          cbArb: { data: unwrap(cbArb, {}) },
          ah: { data: unwrap(ah, []) },
          ab: { data: unwrap(ab, []) },
          lofArb: { data: unwrap(lofArb, []) },
          monitor: { data: unwrap(monitor, []) },
        },
      });
    } catch (error) {
      setState((current) => ({ ...current, loading: false, error: error.message || '加载失败' }));
    }
  }, []);

  React.useEffect(() => {
    load();
    const timer = window.setInterval(load, 60000);
    return () => window.clearInterval(timer);
  }, [load]);

  return { ...state, reload: load };
}

function StatusStrip({ state }) {
  const health = state.resources?.health?.data || {};
  const sections = health.sections || {};
  const resourceStatus = state.resources?.resourceStatus?.data || {};
  const failedResources = Object.entries(resourceStatus).filter(([, item]) => item?.status && item.status !== 'ok');
  return (
    <header className="terminal-status">
      <div className="brand-block">
        <span className="brand-mark">ALPHA</span>
        <span className="brand-subtitle">Opportunity Terminal</span>
      </div>
      <div className="status-grid">
        <StatusCell label="系统" value={health.status || 'loading'} tone={health.status === 'ok' ? 'good' : 'warn'} />
        <StatusCell label="Web" value={sections.web?.status || '--'} tone={sections.web?.status === 'ok' ? 'good' : 'warn'} />
        <StatusCell label="数据异常" value={failedResources.length} tone={failedResources.length ? 'bad' : 'good'} />
        <StatusCell label="刷新" value={state.loading ? 'loading' : formatTime(state.updatedAt)} tone="neutral" />
      </div>
      <button className="terminal-action" type="button" onClick={state.reload}>刷新</button>
      <a className="terminal-link" href="/legacy">旧版</a>
    </header>
  );
}

function StatusCell({ label, value, tone }) {
  return (
    <div className={`status-cell tone-${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function MetricMatrix({ resources, opportunities }) {
  const cbRows = toArray(resources.cbArb.data?.data);
  const smallRows = toArray(resources.cbArb.data?.smallRedemption?.rows);
  const ahRows = toArray(resources.ah.data);
  const abRows = toArray(resources.ab.data);
  const lofRows = toArray(resources.lofArb.data);
  const monitors = toArray(resources.monitor.data);
  return (
    <section className="metric-matrix" aria-label="核心数据矩阵">
      <MetricCard label="机会总数" value={opportunities.length} hint="跨策略候选" />
      <MetricCard label="转债样本" value={cbRows.length + smallRows.length} hint="含小额刚兑" />
      <MetricCard label="AH / AB" value={`${ahRows.length}/${abRows.length}`} hint="溢价监控" />
      <MetricCard label="LOF" value={lofRows.length} hint="套利候选" />
      <MetricCard label="自定义监控" value={monitors.length} hint="跟踪规则" />
    </section>
  );
}

function MetricCard({ label, value, hint }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <em>{hint}</em>
    </div>
  );
}

function OpportunityCommandCenter({ opportunities }) {
  return (
    <section className="terminal-panel command-center">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Opportunity Command Center</p>
          <h1>机会排序</h1>
        </div>
        <span className="panel-count">{opportunities.length} rows</span>
      </div>
      <div className="dense-table-wrap">
        <table className="dense-table">
          <thead>
            <tr>
              <th>策略</th>
              <th>标的</th>
              <th>代码</th>
              <th>指标</th>
              <th className="num">数值</th>
              <th>约束/风险</th>
              <th className="num">报价</th>
            </tr>
          </thead>
          <tbody>
            {opportunities.length ? opportunities.map((row, index) => (
              <tr key={`${row.source}-${row.code}-${index}`}>
                <td><span className="source-pill">{row.source}</span></td>
                <td>{row.name}</td>
                <td className="mono">{row.code}</td>
                <td>{row.metric}</td>
                <td className={`num mono ${signedClass(row.rawValue)}`}>{row.value}</td>
                <td className="muted">{row.risk}</td>
                <td className="num mono">{row.quote}</td>
              </tr>
            )) : (
              <tr><td colSpan="7" className="empty-cell">暂无真实接口返回的候选机会</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function ConvertibleTable({ rows }) {
  const visibleRows = rows.slice(0, 30);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Convertible Bond Arbitrage</p>
          <h2>转债核心表</h2>
        </div>
        <span className="panel-count">{rows.length} rows</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th>转债</th>
              <th>代码</th>
              <th className="num">转债价</th>
              <th className="num">涨跌</th>
              <th>正股</th>
              <th className="num">正股价</th>
              <th className="num">溢价率</th>
              <th className="num">双低</th>
              <th className="num">规模</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row, index) => (
              <tr key={`${row.code || row.bondCode || index}`}>
                <td>{pickText(row.bondName, row.name)}</td>
                <td className="mono">{pickText(row.code, row.bondCode)}</td>
                <td className="num mono">{formatNumber(row.price)}</td>
                <td className={`num mono ${signedClass(row.changePercent)}`}>{formatPercent(row.changePercent)}</td>
                <td>{pickText(row.stockName, row.aName)}</td>
                <td className="num mono">{formatNumber(row.stockPrice)}</td>
                <td className={`num mono ${signedClass(row.premiumRate)}`}>{formatPercent(row.premiumRate)}</td>
                <td className="num mono">{formatNumber(row.doubleLow)}</td>
                <td className="num mono">{formatNumber(row.remainingSizeYi, '亿')}</td>
                <td className="muted">{pickText(row.forceRedeemStatus, row.status, row.rating)}</td>
              </tr>
            )) : (
              <tr><td colSpan="10" className="empty-cell">转债接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const state = useDashboardData();
  const resources = state.resources;
  const opportunities = resources ? buildOpportunityRows(resources) : [];
  const cbRows = resources ? toArray(resources.cbArb.data?.data) : [];

  return (
    <main className="terminal-shell">
      <StatusStrip state={state} />
      {state.error ? <div className="error-strip">接口加载失败：{state.error}</div> : null}
      {resources ? (
        <>
          <MetricMatrix resources={resources} opportunities={opportunities} />
          <div className="terminal-grid">
            <OpportunityCommandCenter opportunities={opportunities} />
            <ConvertibleTable rows={cbRows} />
          </div>
        </>
      ) : (
        <section className="terminal-panel loading-panel">正在连接真实市场接口...</section>
      )}
    </main>
  );
}

export default App;
