import React from 'react';

const API_ENDPOINTS = {
  health: '/api/health',
  uiConfig: '/api/dashboard/ui-config',
  resourceStatus: '/api/dashboard/resource-status',
  cbArb: '/api/market/convertible-bond-arbitrage',
  ah: '/api/market/ah',
  ab: '/api/market/ab',
  lofArb: '/api/market/lof-arbitrage',
  monitor: '/api/monitors',
  subscriptions: '/api/market/subscriptions',
  dividend: '/api/dividend?action=portfolio',
  cbRightsIssue: '/api/market/cb-rights-issue',
  merger: '/api/market/event-arbitrage',
  pushConfig: '/api/push/config',
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
  if (value === null || value === undefined) return null;
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

function formatDate(value) {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString('zh-CN');
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

function rowMatchesQuery(row, query, fields) {
  if (!query) return true;
  const lower = query.toLowerCase();
  return fields.some((f) => String(row[f] || '').toLowerCase().includes(lower));
}

function useSort() {
  const [sortConfig, setSortConfig] = React.useState({ key: null, direction: 'asc' });
  const handleSort = React.useCallback((key) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  }, []);
  const sorted = React.useCallback((rows, keyFn) => {
    if (!sortConfig.key || !rows.length) return rows;
    const { key, direction } = sortConfig;
    return [...rows].sort((a, b) => {
      const av = keyFn(a, key);
      const bv = keyFn(b, key);
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      if (typeof av === 'number' && typeof bv === 'number') {
        return direction === 'asc' ? av - bv : bv - av;
      }
      return direction === 'asc' ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
    });
  }, [sortConfig]);
  return { sortConfig, handleSort, sorted };
}

function usePagination({ pageSize = 50 } = {}) {
  const [page, setPage] = React.useState(1);
  const paginate = React.useCallback((rows) => {
    const total = rows.length;
    const totalPages = Math.max(1, Math.ceil(total / pageSize));
    const safePage = Math.min(Math.max(page, 1), totalPages);
    if (safePage !== page) setPage(safePage);
    const start = (safePage - 1) * pageSize;
    return { rows: rows.slice(start, start + pageSize), total, totalPages, page: safePage };
  }, [page, pageSize]);
  return { page, setPage, paginate };
}

function Pagination({ page, totalPages, total, onChange }) {
  if (totalPages <= 1) return null;
  const go = (p) => { if (p >= 1 && p <= totalPages) onChange(p); };
  return (
    <div className="pagination-bar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', borderTop: '1px solid rgba(255,255,255,0.06)', fontSize: '13px' }}>
      <span style={{ color: 'var(--text-faint)' }}>{total} 条</span>
      <div style={{ display: 'flex', gap: '4px' }}>
        <button className="tab-button" onClick={() => go(1)} disabled={page <= 1}>首页</button>
        <button className="tab-button" onClick={() => go(page - 1)} disabled={page <= 1}>上一页</button>
        <span style={{ padding: '4px 10px', color: 'var(--text-soft)' }}>第 {page} / {totalPages} 页</span>
        <button className="tab-button" onClick={() => go(page + 1)} disabled={page >= totalPages}>下一页</button>
        <button className="tab-button" onClick={() => go(totalPages)} disabled={page >= totalPages}>末页</button>
      </div>
    </div>
  );
}

function ExpandableRow({ children, detail, defaultExpanded = false }) {
  const [expanded, setExpanded] = React.useState(defaultExpanded);
  return (
    <>
      <tr onClick={() => setExpanded((v) => !v)} style={{ cursor: 'pointer' }}>
        {children}
        <td className="num muted" style={{ width: '40px', textAlign: 'center' }}>{expanded ? '▼' : '▶'}</td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={React.Children.count(children) + 1} style={{ padding: 0, border: 'none' }}>
            <div style={{ padding: '12px 16px', background: 'rgba(255,255,255,0.02)', fontSize: '13px', lineHeight: 1.8 }}>
              {detail}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

function SortableTh({ label, sortKey, sortConfig, onSort, className }) {
  const isActive = sortConfig.key === sortKey;
  const arrow = isActive ? (sortConfig.direction === 'asc' ? ' ▲' : ' ▼') : '';
  const classes = [className, isActive ? 'sort-active' : ''].filter(Boolean).join(' ');
  return (
    <th
      className={classes || undefined}
      onClick={() => onSort(sortKey)}
      style={{ cursor: 'pointer' }}
    >
      {label}{arrow}
    </th>
  );
}

function buildOpportunityRows(resources) {
  const rows = [];
  const cbRows = [
    ...toArray(resources.cbArb.data),
    ...toArray(resources.cbArb.smallRedemption?.rows),
  ];
  cbRows
    .filter((row) => toNumber(row.premiumRate) !== null || toNumber(row.doubleLow) !== null)
    .sort((a, b) => (toNumber(a.premiumRate) ?? 999) - (toNumber(b.premiumRate) ?? 999))
    .slice(0, 8)
    .forEach((row) => rows.push({
      source: '转债套利',
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

  // 事件套利机会
  const mergerCategories = resources.merger?.data?.categories || {};
  const aEventRows = toArray(mergerCategories.a_event).filter((r) => toNumber(r.spreadRate) !== null || toNumber(r.safeDiscountRate) !== null);
  const hkPrivateRows = toArray(mergerCategories.hk_private).filter((r) => toNumber(r.spreadRate) !== null);
  const allMergerRows = [...aEventRows, ...hkPrivateRows]
    .sort((a, b) => Math.abs(toNumber(b.spreadRate ?? b.safeDiscountRate) ?? 0) - Math.abs(toNumber(a.spreadRate ?? a.safeDiscountRate) ?? 0))
    .slice(0, 3);
  allMergerRows.forEach((row) => rows.push({
    source: '事件套利',
    name: pickText(row.name, row.secName),
    code: pickText(row.symbol, row.secCode),
    metric: '套利空间',
    value: formatPercent(row.spreadRate ?? row.safeDiscountRate),
    rawValue: toNumber(row.spreadRate ?? row.safeDiscountRate),
    risk: pickText(row.eventType, row.eventStage, row.dealType),
    quote: formatNumber(row.currentPrice),
  }));

  return rows.slice(0, 18);
}

function useDashboardData() {
  const [state, setState] = React.useState({ loading: true, error: '', resources: null, updatedAt: '' });

  const load = React.useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: '' }));

    const criticalEndpoints = [
      { key: 'health', url: API_ENDPOINTS.health, fallback: {} },
      { key: 'uiConfig', url: API_ENDPOINTS.uiConfig, fallback: {} },
      { key: 'resourceStatus', url: `${API_ENDPOINTS.resourceStatus}?keys=exchangeRate,cbArb,ah,ab,lofArb`, fallback: {} },
      { key: 'cbArb', url: API_ENDPOINTS.cbArb, fallback: {} },
      { key: 'ah', url: API_ENDPOINTS.ah, fallback: [] },
      { key: 'ab', url: API_ENDPOINTS.ab, fallback: [] },
      { key: 'lofArb', url: API_ENDPOINTS.lofArb, fallback: [] },
      { key: 'monitor', url: API_ENDPOINTS.monitor, fallback: [] },
      { key: 'dividend', url: API_ENDPOINTS.dividend, fallback: [] },
      { key: 'cbRightsIssue', url: API_ENDPOINTS.cbRightsIssue, fallback: {} },
      { key: 'merger', url: API_ENDPOINTS.merger, fallback: {} },
      { key: 'pushConfig', url: API_ENDPOINTS.pushConfig, fallback: {} },
    ];

    const mergeResult = (resources, result, i, endpoints) => {
      const { key, fallback } = endpoints[i];
      if (result.status === 'fulfilled') {
        if (key === 'cbArb') {
          const raw = result.value || fallback;
          resources[key] = {
            data: unwrap(raw, fallback),
            smallRedemption: raw?.smallRedemption || null,
          };
        } else {
          resources[key] = { data: unwrap(result.value, fallback) };
        }
      } else {
        resources[key] = { data: fallback, error: result.reason?.message || 'failed' };
      }
    };

    const criticalResults = await Promise.allSettled(criticalEndpoints.map((e) => fetchJson(e.url)));
    const resources = {};
    const errors = [];
    criticalResults.forEach((result, i) => {
      mergeResult(resources, result, i, criticalEndpoints);
      if (result.status === 'rejected') {
        errors.push(`${criticalEndpoints[i].key}: ${result.reason?.message || 'failed'}`);
      }
    });

    setState({
      loading: false,
      error: errors.length > 0 ? `${errors.length} 个接口异常（${errors.slice(0, 2).join('；')}）` : '',
      updatedAt: new Date().toISOString(),
      resources,
    });

    fetchJson(API_ENDPOINTS.subscriptions).then(
      (value) => {
        setState((current) => ({
          ...current,
          resources: { ...current.resources, subscriptions: { data: unwrap(value, {}) } },
          updatedAt: new Date().toISOString(),
        }));
      },
      (reason) => {
        setState((current) => ({
          ...current,
          resources: { ...current.resources, subscriptions: { data: {}, error: reason?.message || 'failed' } },
          updatedAt: new Date().toISOString(),
        }));
      }
    );
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
  const status = health.status || 'loading';
  const isOk = status === 'ok';
  return (
    <header className="terminal-status minimal">
      <div className="brand-block">
        <span className="brand-mark">ALPHA</span>
        <span className="brand-subtitle">Opportunity Terminal</span>
      </div>
      <div className="status-line">
        <span className={isOk ? 'status-ok' : 'status-warn'}>
          {isOk ? '系统正常' : `系统异常: ${status}`}
        </span>
        {state.loading && <span className="status-loading">刷新中...</span>}
      </div>
      <button className="terminal-action" type="button" onClick={state.reload}>刷新</button>
    </header>
  );
}

function SearchBar({ value, onChange, count }) {
  return (
    <div className="search-bar">
      <input
        className="search-input"
        type="text"
        placeholder="搜索代码或名称..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {count !== undefined && <span className="search-count">{count} 条结果</span>}
    </div>
  );
}

function TabNav({ activeTab, onChange }) {
  const tabs = [
    { key: 'overview', label: '概览' },
    { key: 'convertible', label: '转债套利' },
    { key: 'ah', label: 'AH溢价' },
    { key: 'ab', label: 'AB溢价' },
    { key: 'lof', label: 'LOF套利' },
    { key: 'subscription', label: '打新/申购' },
    { key: 'monitor', label: '自定义监控' },
    { key: 'dividend', label: '分红提醒' },
    { key: 'merger', label: '事件套利' },
    { key: 'push', label: '推送设置' },
  ];
  return (
    <nav className="tab-nav" role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          className={`tab-button ${activeTab === tab.key ? 'active' : ''}`}
          onClick={() => onChange(tab.key)}
          role="tab"
          aria-selected={activeTab === tab.key}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}

function getSubscriptionStage(row, today) {
  if (row.subscribeDate && row.subscribeDate.startsWith(today)) return { label: '今日申购', tone: 'is-up' };
  if (row.paymentDate && row.paymentDate.startsWith(today)) return { label: '今日中签缴款', tone: 'is-down' };
  if (row.listingDate && row.listingDate.startsWith(today)) return { label: '今日上市', tone: 'is-flat' };
  return null;
}

function TodayActions({ data }) {
  if (!data) return null;
  const ipoRows = toArray(data.ipo?.data);
  const bondRows = toArray(data.bonds?.data);
  const allRows = [...ipoRows, ...bondRows];
  const today = new Date().toISOString().slice(0, 10);

  // 过滤：还没申购、还没上市；无上市日认为未上市
  const futureRows = allRows.filter((r) => {
    const notSubscribed = !r.subscribeDate || r.subscribeDate >= today;
    const notListed = !r.listingDate || r.listingDate >= today;
    return notSubscribed && notListed;
  });

  // 排序：今日申购置顶，其他按申购日升序
  const sorted = futureRows.sort((a, b) => {
    const aTodaySub = a.subscribeDate && a.subscribeDate.startsWith(today) ? 1 : 0;
    const bTodaySub = b.subscribeDate && b.subscribeDate.startsWith(today) ? 1 : 0;
    if (aTodaySub !== bTodaySub) return bTodaySub - aTodaySub;
    const aSub = a.subscribeDate || '9999-99-99';
    const bSub = b.subscribeDate || '9999-99-99';
    return aSub.localeCompare(bSub);
  });

  if (sorted.length === 0) {
    return (
      <section className="terminal-panel today-actions">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">TODAY</p><h2>今日行动</h2></div>
        </div>
        <div className="today-empty">近期无申购/上市事项</div>
      </section>
    );
  }

  return (
    <section className="terminal-panel today-actions">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">TODAY</p><h2>今日行动</h2></div>
        <span className="panel-count">{sorted.length} 项</span>
      </div>
      <div className="today-list">
        {sorted.map((row, i) => {
          const isIpo = ipoRows.includes(row);
          const isTodaySub = row.subscribeDate && row.subscribeDate.startsWith(today);
          const stage = isTodaySub ? '今日申购' : (row.subscribeDate ? `申购 ${formatDate(row.subscribeDate)}` : '待申购');
          const tone = isTodaySub ? 'is-up' : 'is-flat';
          return (
            <div key={`${row.code || i}`} className="today-item">
              <span className={`today-stage ${tone}`}>{stage}</span>
              <span className="today-name">{pickText(row.name, row.stockName)}</span>
              <span className="mono muted">{pickText(row.code, row.stockCode)}</span>
              <span className="today-type">{isIpo ? '新股' : '债券'}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function BestOpportunities({ opportunities, onNavigate, pushConfig }) {
  const modules = pushConfig?.modules || {};
  const moduleToSource = {
    cbArb: ['转债套利'],
    ahab: ['AH', 'AB'],
    lofArb: ['LOF'],
    eventArb: ['事件套利'],
  };
  const enabledSources = new Set();
  Object.entries(moduleToSource).forEach(([modKey, sources]) => {
    if (modules[modKey] !== false) {
      sources.forEach((s) => enabledSources.add(s));
    }
  });
  const filtered = opportunities.filter((o) => enabledSources.has(o.source));
  const top5 = filtered.slice(0, 5);
  const sourceTabMap = {
    '转债套利': 'convertible',
    'AH': 'ah',
    'AB': 'ab',
    'LOF': 'lof',
    '事件套利': 'merger',
  };

  return (
    <section className="terminal-panel best-opportunities">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">TOP 5</p><h2>最佳机会</h2></div>
        <span className="panel-count">{opportunities.length} 候选</span>
      </div>
      <div className="best-list">
        {top5.length ? top5.map((row, i) => (
          <div
            key={`${row.source}-${row.code}-${i}`}
            className="best-item"
            onClick={() => onNavigate(sourceTabMap[row.source] || 'overview')}
            role="button"
            tabIndex={0}
          >
            <span className="best-rank">{i + 1}</span>
            <span className="source-pill">{row.source}</span>
            <span className="best-name">{row.name}</span>
            <span className="mono muted">{row.code}</span>
            <span className="best-metric">{row.metric}</span>
            <span className={`best-value mono ${signedClass(row.rawValue)}`}>{row.value}</span>
          </div>
        )) : (
          <div className="today-empty">暂无候选机会</div>
        )}
      </div>
    </section>
  );
}

function MonitorAlerts({ rows, onNavigate }) {
  if (!rows || rows.length === 0) return null;
  const alerts = rows.slice(0, 3);
  return (
    <section className="terminal-panel monitor-alerts">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">ALERT</p><h2>监控提醒</h2></div>
        <span className="panel-count">{rows.length} 条</span>
      </div>
      <div className="alert-list">
        {alerts.map((row, i) => {
          const best = Math.max(toNumber(row.stockYieldRate) ?? -Infinity, toNumber(row.cashYieldRate) ?? -Infinity);
          return (
            <div key={row.id || i} className="alert-item" onClick={() => onNavigate('monitor')} role="button" tabIndex={0}>
              <span className="alert-name">{pickText(row.name)}</span>
              <span className="mono muted">{pickText(row.acquirerName)}&rarr;{pickText(row.targetName)}</span>
              <span className={`alert-yield mono ${signedClass(best === -Infinity ? null : best)}`}>
                {best === -Infinity ? '--' : `${PERCENT_FORMAT.format(best)}%`}
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function OpportunityCommandCenter({ opportunities, filter, onFilterChange }) {
  const filters = [
    { key: 'all', label: '全部' },
    { key: '转债套利', label: '转债套利' },
    { key: 'LOF', label: 'LOF' },
    { key: 'AH', label: 'AH' },
    { key: 'AB', label: 'AB' },
    { key: '事件套利', label: '事件套利' },
  ];

  const filtered = filter === 'all' ? opportunities : opportunities.filter((o) => o.source === filter);

  return (
    <section className="terminal-panel command-center">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Opportunity Command Center</p>
          <h1>机会排序</h1>
        </div>
        <span className="panel-count">{filtered.length} / {opportunities.length} rows</span>
      </div>
      <div className="opportunity-filter-bar">
        {filters.map((f) => (
          <button
            key={f.key}
            className={`filter-chip ${filter === f.key ? 'active' : ''}`}
            onClick={() => onFilterChange(f.key)}
          >
            {f.label}
          </button>
        ))}
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
            {filtered.length ? filtered.map((row, index) => (
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

function ConvertibleTable({ rows, smallRows, rightsIssueData, searchQuery }) {
  const [subTab, setSubTab] = React.useState('main');
  const { sortConfig, handleSort, sorted } = useSort();
  const { page, setPage, paginate } = usePagination({ pageSize: 50 });

  function sortRows(list) {
    return sorted(list, (row, key) => {
      if (key === 'stockAvgTurnoverAmount20Yi') return toNumber(row.stockAvgTurnoverAmount20Yi);
      if (key === 'convertValue') return toNumber(row.convertValue);
      if (key === 'pureBondValue') return toNumber(row.pureBondValue);
      if (key === 'theoreticalPremiumRate') return toNumber(row.theoreticalPremiumRate);
      if (key === 'optionValue') return toNumber(row.optionValue);
      if (key === 'discountAtrRatio') return toNumber(row.discountAtrRatio);
      if (key === 'volatility250') return toNumber(row.volatility250);
      if (key === 'remainingYears') return toNumber(row.remainingYears);
      if (key === 'stockMarketValueYi') return toNumber(row.stockMarketValueYi);
      if (key === 'bondToStockMarketValueRatio') return toNumber(row.bondToStockMarketValueRatio);
      return toNumber(row[key]) ?? row[key];
    });
  }

  const baseFields = ['bondName', 'name', 'code', 'bondCode', 'stockName', 'aName', 'stockCode'];
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, baseFields));
  const { rows: visibleRows, total, totalPages } = paginate(sortRows(filtered));

  const smallFiltered = (smallRows || []).filter((r) => rowMatchesQuery(r, searchQuery, baseFields));
  const smallVisible = sortRows(smallFiltered).slice(0, 50);

  // 折价套利：溢价率 < 0（转债价格 < 转股价值）
  const discountRows = rows.filter((r) => {
    if (!rowMatchesQuery(r, searchQuery, baseFields)) return false;
    const pr = toNumber(r.premiumRate);
    return pr !== null && pr < 0;
  });
  const discountVisible = sortRows(discountRows).slice(0, 50);

  // 理论折价套利：市场价 < BSM理论价
  const theoreticalDiscountRows = rows.filter((r) => {
    if (!rowMatchesQuery(r, searchQuery, baseFields)) return false;
    const price = toNumber(r.price);
    const tp = toNumber(r.theoreticalPrice);
    return price !== null && tp !== null && price < tp;
  });
  const theoreticalDiscountVisible = sortRows(theoreticalDiscountRows).slice(0, 50);

  // 抢权配售数据
  const riRows = toArray(rightsIssueData?.sourceRows);
  const riShRows = riRows.filter((r) => String(r.market || '').toLowerCase() === 'sh' || String(r.stockCode || '').startsWith('6'));
  const riSzRows = riRows.filter((r) => String(r.market || '').toLowerCase() === 'sz' || String(r.stockCode || '').match(/^[03]/));
  const riApply = riRows.filter((r) => r.inApplyStage === true);
  const riAmbush = riRows.filter((r) => {
    if (r.inApplyStage === true) return false;
    const pn = String(r.progressName || '');
    return (pn.includes('上市委通过') || pn.includes('同意注册') || pn.includes('注册生效')) && toNumber(r.expectedReturnRate) > 6;
  });
  const riWait = riRows.filter((r) => {
    if (r.inApplyStage === true) return false;
    const pn = String(r.progressName || '');
    return !((pn.includes('上市委通过') || pn.includes('同意注册') || pn.includes('注册生效')) && toNumber(r.expectedReturnRate) > 6);
  });

  function getConvertStatus(row) {
    const today = new Date().toISOString().slice(0, 10);
    if (row.isUnlisted || (row.delistDate && row.delistDate <= today)) return '已退市';
    if (row.isBeforeConvertStart || (row.convertStartDate && row.convertStartDate > today)) return '未到转股期';
    if (row.forceRedeemStatus && row.forceRedeemStatus.includes('强赎')) return '强赎中';
    if (row.maturityDate && row.maturityDate <= today) return '已到期';
    return '正常';
  }

  // 主页表格 — 完整20列
  function renderHomeTable(dataRows) {
    const sortedData = sortRows(dataRows);
    const safePage = page || 1;
    const safeTotalPages = Math.max(1, Math.ceil(sortedData.length / 50));
    const start = (safePage - 1) * 50;
    const paginatedVis = sortedData.slice(start, start + 50);
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">CONVERTIBLE ARB</p><h2>转债套利</h2></div>
          <span className="panel-count">{dataRows.length} 条</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th>转债名称</th>
                <th className="mono">代码</th>
                <SortableTh label="转债价格" sortKey="price" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="涨跌幅" sortKey="changePercent" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>正股名称</th>
                <SortableTh label="正股价格" sortKey="stockPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="转股价格" sortKey="convertPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="转股价值" sortKey="convertValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="转股溢价率" sortKey="premiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="剩余规模" sortKey="remainingSizeYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="正股流通市值" sortKey="stockMarketValueYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th className="num muted" style={{ fontSize: '10px' }}>转债占比</th>
                <SortableTh label="纯债价值" sortKey="pureBondValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="波动率" sortKey="volatility250" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="期权价值" sortKey="optionValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="理论价值" sortKey="theoreticalPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="理论套利空间" sortKey="theoreticalPremiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="到期日" sortKey="maturityDate" sortConfig={sortConfig} onSort={handleSort} />
                <th>评级</th>
                <th>强赎状态</th>
                <th>转股状态</th>
              </tr>
            </thead>
            <tbody>
              {paginatedVis.length ? paginatedVis.map((row, index) => {
                const stockMarketValueYi = toNumber(row.stockMarketValueYi);
                const remainingSizeYi = toNumber(row.remainingSizeYi);
                const bondToStockRatio = stockMarketValueYi > 0 && remainingSizeYi !== null ? remainingSizeYi / stockMarketValueYi : null;
                const volatility = toNumber(row.volatility250) ?? toNumber(row.volatility60);
                return (
                  <tr key={`${row.code || row.bondCode || index}`}>
                    <td>{pickText(row.bondName, row.name)}</td>
                    <td className="mono">{pickText(row.code, row.bondCode)}</td>
                    <td className="num mono">{formatNumber(row.price)}</td>
                    <td className={`num mono ${signedClass(row.changePercent)}`}>{formatPercent(row.changePercent)}</td>
                    <td>{pickText(row.stockName, row.aName)}</td>
                    <td className="num mono">{formatNumber(row.stockPrice)}</td>
                    <td className="num mono">{formatNumber(row.convertPrice)}</td>
                    <td className={`num mono ${signedClass(row.convertValue)}`}>{formatNumber(row.convertValue)}</td>
                    <td className={`num mono ${signedClass(row.premiumRate)}`}>{formatPercent(row.premiumRate)}</td>
                    <td className="num mono">{formatNumber(row.remainingSizeYi, '亿')}</td>
                    <td className="num mono">{stockMarketValueYi !== null ? formatNumber(stockMarketValueYi, '亿') : '--'}</td>
                    <td className="num mono muted">{bondToStockRatio !== null ? `${(bondToStockRatio * 100).toFixed(1)}%` : '--'}</td>
                    <td className="num mono">{row.pureBondValue != null ? Number(row.pureBondValue).toFixed(2) : '--'}</td>
                    <td className="num mono">{volatility !== null ? `${(volatility * 100).toFixed(2)}%` : '--'}</td>
                    <td className="num mono">{row.optionValue != null ? Number(row.optionValue).toFixed(2) : '--'}</td>
                    <td className="num mono">{row.theoreticalPrice != null ? Number(row.theoreticalPrice).toFixed(2) : '--'}</td>
                    <td className={`num mono ${signedClass(row.theoreticalPremiumRate)}`}>{formatPercent(row.theoreticalPremiumRate)}</td>
                    <td className="mono">{row.maturityDate || '--'}</td>
                    <td className="muted">{pickText(row.rating)}</td>
                    <td className="muted">{pickText(row.forceRedeemStatus)}</td>
                    <td className="muted">{getConvertStatus(row)}</td>
                  </tr>
                );
              }) : (
                <tr><td colSpan="21" className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination page={safePage} totalPages={safeTotalPages} total={sortedData.length} onChange={setPage} />
      </section>
    );
  }

  // 折价套利表格 — 聚焦套利核心字段
  function renderDiscountTable(dataRows, title, eyebrow) {
    const sortedData = sortRows(dataRows);
    const safePage = page || 1;
    const safeTotalPages = Math.max(1, Math.ceil(sortedData.length / 50));
    const start = (safePage - 1) * 50;
    const paginatedVis = sortedData.slice(start, start + 50);
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div>
          <span className="panel-count">{dataRows.length} 条</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th>转债名称</th>
                <th className="mono">代码</th>
                <SortableTh label="转债价格" sortKey="price" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="涨跌幅" sortKey="changePercent" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>正股名称</th>
                <SortableTh label="正股价格" sortKey="stockPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="转股价值" sortKey="convertValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="转股溢价率" sortKey="premiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="剩余规模" sortKey="remainingSizeYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="纯债价值" sortKey="pureBondValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="理论价值" sortKey="theoreticalPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="理论套利空间" sortKey="theoreticalPremiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="到期日" sortKey="maturityDate" sortConfig={sortConfig} onSort={handleSort} />
                <th>评级</th>
                <th>强赎状态</th>
                <th>转股状态</th>
              </tr>
            </thead>
            <tbody>
              {paginatedVis.length ? paginatedVis.map((row, index) => {
                return (
                  <tr key={`${row.code || row.bondCode || index}`}>
                    <td>{pickText(row.bondName, row.name)}</td>
                    <td className="mono">{pickText(row.code, row.bondCode)}</td>
                    <td className="num mono">{formatNumber(row.price)}</td>
                    <td className={`num mono ${signedClass(row.changePercent)}`}>{formatPercent(row.changePercent)}</td>
                    <td>{pickText(row.stockName, row.aName)}</td>
                    <td className="num mono">{formatNumber(row.stockPrice)}</td>
                    <td className={`num mono ${signedClass(row.convertValue)}`}>{formatNumber(row.convertValue)}</td>
                    <td className={`num mono ${signedClass(row.premiumRate)}`}>{formatPercent(row.premiumRate)}</td>
                    <td className="num mono">{formatNumber(row.remainingSizeYi, '亿')}</td>
                    <td className="num mono">{row.pureBondValue != null ? Number(row.pureBondValue).toFixed(2) : '--'}</td>
                    <td className="num mono">{row.theoreticalPrice != null ? Number(row.theoreticalPrice).toFixed(2) : '--'}</td>
                    <td className={`num mono ${signedClass(row.theoreticalPremiumRate)}`}>{formatPercent(row.theoreticalPremiumRate)}</td>
                    <td className="mono">{row.maturityDate || '--'}</td>
                    <td className="muted">{pickText(row.rating)}</td>
                    <td className="muted">{pickText(row.forceRedeemStatus)}</td>
                    <td className="muted">{getConvertStatus(row)}</td>
                  </tr>
                );
              }) : (
                <tr><td colSpan="16" className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <Pagination page={safePage} totalPages={safeTotalPages} total={sortedData.length} onChange={setPage} />
      </section>
    );
  }

  function renderSmallTable() {
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">SMALL REDEMPTION</p><h2>小额刚兑</h2></div>
          <span className="panel-count">{smallFiltered.length} / {smallRows?.length || 0}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th>转债</th>
                <th className="mono">代码</th>
                <th className="num">价格</th>
                <th className="num">涨跌幅</th>
                <th>正股</th>
                <th className="num">正股价</th>
                <th className="num">期权价值</th>
                <th className="num">持有人数</th>
                <SortableTh label="剩余规模" sortKey="remainingSizeYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="刚兑金额" sortKey="smallRedemptionAmount" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="刚兑收益率" sortKey="smallRedemptionYield" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="预期耗时" sortKey="smallRedemptionExpectedYears" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="刚兑年化" sortKey="smallRedemptionAnnualizedYield" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="刚兑总额" sortKey="smallRedemptionTotalAmount" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="负债敞口" sortKey="stockNetDebtExposureYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="净资产" sortKey="stockNetAssetsYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="期权年化" sortKey="smallRedemptionOptionAnnualizedYield" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="总年化" sortKey="smallRedemptionTotalAnnualizedYield" sortConfig={sortConfig} onSort={handleSort} className="num" />
              </tr>
            </thead>
            <tbody>
              {smallVisible.length ? smallVisible.map((row) => (
                <tr key={row.code}>
                  <td>{pickText(row.bondName, row.name)}</td>
                  <td className="mono">{pickText(row.code, row.bondCode)}</td>
                  <td className="num mono">{formatNumber(row.price)}</td>
                  <td className={`num mono ${signedClass(row.changePercent)}`}>{formatPercent(row.changePercent)}</td>
                  <td className="mono">{pickText(row.stockName)} {row.stockCode ? `(${row.stockCode})` : ''}</td>
                  <td className="num mono">{formatNumber(row.stockPrice)}</td>
                  <td className="num mono">{formatNumber(row.optionValue)}</td>
                  <td className="num mono muted">{formatNumber(row.holderCount)}</td>
                  <td className="num mono">{formatNumber(row.remainingSizeYi, '亿')}</td>
                  <td className="num mono">{formatNumber(row.smallRedemptionAmount)}</td>
                  <td className={`num mono ${signedClass(row.smallRedemptionYield)}`}>{formatPercent(row.smallRedemptionYield)}</td>
                  <td className="num mono">{toNumber(row.smallRedemptionExpectedYears) !== null ? row.smallRedemptionExpectedYears.toFixed(1) + '年' : '--'}</td>
                  <td className={`num mono ${signedClass(row.smallRedemptionAnnualizedYield)}`}>{formatPercent(row.smallRedemptionAnnualizedYield)}</td>
                  <td className="num mono">{formatNumber(row.smallRedemptionTotalAmount)}</td>
                  <td className="num mono muted">{formatNumber(row.stockNetDebtExposureYi, '亿')}</td>
                  <td className="num mono muted">{formatNumber(row.stockNetAssetsYi, '亿')}</td>
                  <td className={`num mono ${signedClass(row.smallRedemptionOptionAnnualizedYield)}`}>{formatPercent(row.smallRedemptionOptionAnnualizedYield)}</td>
                  <td className={`num mono ${signedClass(row.smallRedemptionTotalAnnualizedYield)}`}>{formatPercent(row.smallRedemptionTotalAnnualizedYield)}</td>
                </tr>
              )) : (
                <tr><td colSpan="18" className="empty-cell">小额刚兑暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  return (
    <>
      <div className="tab-nav" style={{ marginTop: '8px' }}>
        <button className={`tab-button ${subTab === 'main' ? 'active' : ''}`} onClick={() => setSubTab('main')}>主页 ({rows.length})</button>
        <button className={`tab-button ${subTab === 'discount' ? 'active' : ''}`} onClick={() => setSubTab('discount')}>折价套利 ({discountRows.length})</button>
        <button className={`tab-button ${subTab === 'theoretical' ? 'active' : ''}`} onClick={() => setSubTab('theoretical')}>理论折价 ({theoreticalDiscountRows.length})</button>
        <button className={`tab-button ${subTab === 'small' ? 'active' : ''}`} onClick={() => setSubTab('small')}>小额刚兑 ({smallRows?.length || 0})</button>
        <button className={`tab-button ${subTab === 'rights' ? 'active' : ''}`} onClick={() => setSubTab('rights')}>抢权配售 ({riRows.length})</button>
      </div>

      {subTab === 'main' && renderHomeTable(rows)}
      {subTab === 'discount' && renderDiscountTable(discountRows, '折价套利', 'DISCOUNT ARB')}
      {subTab === 'theoretical' && renderDiscountTable(theoreticalDiscountRows, '理论折价套利', 'THEORETICAL DISCOUNT')}
      {subTab === 'small' && renderSmallTable()}
      {subTab === 'rights' && <RightsIssuePanel riRows={riRows} searchQuery={searchQuery} />}
    </>
  );
}

function RightsIssuePanel({ riRows, searchQuery }) {
  const [riMarket, setRiMarket] = React.useState('sh');
  const riShRows = riRows.filter((r) => String(r.market || '').toLowerCase() === 'sh' || String(r.stockCode || '').startsWith('6'));
  const riSzRows = riRows.filter((r) => String(r.market || '').toLowerCase() === 'sz' || String(r.stockCode || '').match(/^[03]/));
  const marketRows = riMarket === 'sh' ? riShRows : riSzRows;
  const applyRows = marketRows.filter((r) => r.inApplyStage === true);
  const ambushRows = marketRows.filter((r) => {
    if (r.inApplyStage === true) return false;
    const pn = String(r.progressName || '');
    return (pn.includes('上市委通过') || pn.includes('同意注册') || pn.includes('注册生效')) && toNumber(r.expectedReturnRate) > 6;
  });
  const waitRows = marketRows.filter((r) => {
    if (r.inApplyStage === true) return false;
    const pn = String(r.progressName || '');
    return !((pn.includes('上市委通过') || pn.includes('同意注册') || pn.includes('注册生效')) && toNumber(r.expectedReturnRate) > 6);
  });
  const isSz = riMarket === 'sz';
  const q = searchQuery.toLowerCase();
  function riFilter(list) {
    if (!q) return list;
    return list.filter((r) =>
      String(r.stockCode || '').toLowerCase().includes(q) ||
      String(r.stockName || '').toLowerCase().includes(q) ||
      String(r.progressName || '').toLowerCase().includes(q)
    );
  }
  function renderRiSection(title, list, showRecordDate, includeMargin, includePeel) {
    const filtered = riFilter(list).slice(0, 50);
    const cols = [];
    cols.push(<th className="mono">正股代码</th>);
    cols.push(<th>正股名称</th>);
    cols.push(<th>方案进展</th>);
    cols.push(<th>进展公告日</th>);
    cols.push(<th className="num">发行规模</th>);
    cols.push(<th className="num">流通市值</th>);
    cols.push(<th className="num">发行比例</th>);
    cols.push(<th className="num">原始所需股数</th>);
    cols.push(<th className="num">配售股数</th>);
    cols.push(<th className="num">转股价</th>);
    cols.push(<th className="num">波动率</th>);
    cols.push(<th className="num">单位期权价值</th>);
    cols.push(<th className="num">期权价值</th>);
    cols.push(<th className="num">所需资金</th>);
    if (includeMargin) { cols.push(<th className="num">两融所需股数</th>); cols.push(<th className="num">两融所需资金</th>); }
    if (showRecordDate) cols.push(<th>股权登记日</th>);
    cols.push(<th className="num">预期收益率</th>);
    if (includeMargin) cols.push(<th className="num">两融收益率</th>);
    if (includePeel) { cols.push(<th className="num">预期收益率去皮</th>); if (includeMargin) cols.push(<th className="num">两融收益率去皮</th>); }
    return (
      <div style={{ marginTop: '6px' }}>
        <div className="panel-head compact-head" style={{ background: 'var(--terminal-panel-2)', padding: '4px 10px' }}>
          <span style={{ color: 'var(--terminal-blue)', fontFamily: 'var(--terminal-mono)', fontSize: '10px' }}>{title}</span>
          <span className="panel-count">{filtered.length} / {list.length}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead><tr>{cols}</tr></thead>
            <tbody>
              {filtered.length ? filtered.map((row, i) => {
                const cells = [];
                cells.push(<td className="mono">{pickText(row.stockCode)}</td>);
                cells.push(<td>{pickText(row.stockName)}</td>);
                cells.push(<td>{pickText(row.progressName)}</td>);
                cells.push(<td>{formatDate(row.progressDate)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.issueScaleYi)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.stockMarketValueYi)}</td>);
                cells.push(<td className="num mono">{formatPercent(row.issueRatio)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.rawRequiredShares)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.placementShares)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.convertPrice)}</td>);
                cells.push(<td className="num mono">{formatPercent(row.volatility250 ?? row.volatility60)}</td>);
                cells.push(<td className="num mono">{toNumber(row.optionUnitValue) !== null ? Number(row.optionUnitValue).toFixed(4) : '--'}</td>);
                cells.push(<td className="num mono">{formatNumber(row.optionValue)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.requiredFunds)}</td>);
                if (includeMargin) { cells.push(<td className="num mono">{formatNumber(row.marginRequiredShares)}</td>); cells.push(<td className="num mono">{formatNumber(row.marginRequiredFunds)}</td>); }
                if (showRecordDate) cells.push(<td>{formatDate(row.recordDate)}</td>);
                cells.push(<td className={`num mono ${signedClass(row.expectedReturnRate)}`}>{formatPercent(row.expectedReturnRate)}</td>);
                if (includeMargin) cells.push(<td className={`num mono ${signedClass(row.marginReturnRate)}`}>{formatPercent(row.marginReturnRate)}</td>);
                if (includePeel) { cells.push(<td className={`num mono ${signedClass(row.expectedPeelReturnRate)}`}>{formatPercent(row.expectedPeelReturnRate)}</td>); if (includeMargin) cells.push(<td className={`num mono ${signedClass(row.marginPeelReturnRate)}`}>{formatPercent(row.marginPeelReturnRate)}</td>); }
                return <tr key={`${row.stockCode || i}`}>{cells}</tr>;
              }) : (
                <tr><td colSpan={cols.length} className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    );
  }
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">CB RIGHTS ISSUE</p><h2>抢权配售</h2></div>
        <span className="panel-count">{riRows.length} 条记录</span>
      </div>
      <div style={{ padding: '6px 10px', borderBottom: '1px solid var(--terminal-line)' }}>
        {[{ key: 'sh', label: `沪市 (${riShRows.length})` }, { key: 'sz', label: `深市 (${riSzRows.length})` }].map((t) => (
          <button key={t.key} className={`tab-button ${riMarket === t.key ? 'active' : ''}`} onClick={() => setRiMarket(t.key)}>{t.label}</button>
        ))}
      </div>
      {renderRiSection('申购阶段', applyRows, true, !isSz, !isSz)}
      {renderRiSection('埋伏阶段', ambushRows, false, !isSz, !isSz)}
      {renderRiSection('等待阶段', waitRows, false, !isSz, !isSz)}
    </section>
  );
}

function AhTable({ rows, searchQuery }) {
  const { sortConfig, handleSort, sorted } = useSort();
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, ['aName', 'name', 'aCode', 'code', 'hName', 'hCode']));
  const visibleRows = sorted(filtered, (row, key) => toNumber(row[key]) ?? row[key]).slice(0, 50);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">AH Premium</p>
          <h2>AH 溢价</h2>
        </div>
        <span className="panel-count">{filtered.length} / {rows.length}</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th className="num muted" style={{ fontSize: '10px' }}>序号</th>
              <th>A股名称</th>
              <th className="mono">A股代码</th>
              <th>H股名称</th>
              <th className="mono">H股代码</th>
              <SortableTh label="A股价格" sortKey="aPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="H股价格" sortKey="hPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="H股人民币价" sortKey="hPriceCny" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="num muted" style={{ fontSize: '10px' }}>价差</th>
              <SortableTh label="溢价率" sortKey="premium" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="近三年分位" sortKey="percentile" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="样本数" sortKey="historyCount" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="muted" style={{ fontSize: '10px' }}>样本区间</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row, index) => {
              const aPrice = toNumber(row.aPrice);
              const hPriceCny = toNumber(row.hPriceCny);
              const gap = (aPrice !== null && hPriceCny !== null) ? (aPrice - hPriceCny).toFixed(2) : null;
              return (
                <tr key={`${row.aCode || row.code || index}`}>
                  <td className="num mono muted">{index + 1}</td>
                  <td>{pickText(row.aName, row.name)}</td>
                  <td className="mono">{pickText(row.aCode, row.code)}</td>
                  <td>{pickText(row.hName)}</td>
                  <td className="mono">{pickText(row.hCode)}</td>
                  <td className="num mono">{formatNumber(row.aPrice)}</td>
                  <td className="num mono">{formatNumber(row.hPrice)}</td>
                  <td className="num mono">{formatNumber(row.hPriceCny)}</td>
                  <td className="num mono muted">{gap !== null ? (Number(gap) > 0 ? '+' : '') + gap : '--'}</td>
                  <td className={`num mono ${signedClass(row.premium)}`}>{formatPercent(row.premium)}</td>
                  <td className="num mono">{formatNumber(row.percentile)}</td>
                  <td className="num mono">{formatNumber(row.historyCount)}</td>
                  <td className="muted" style={{ fontSize: '10px' }}>{pickText(row.historyStartDate, row.historyEndDate) ? `${row.historyStartDate?.slice(0,10) || ''}~${row.historyEndDate?.slice(0,10) || ''}` : '--'}</td>
                </tr>
              );
            }) : (
              <tr><td colSpan="13" className="empty-cell">AH 接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function AbTable({ rows, searchQuery }) {
  const { sortConfig, handleSort, sorted } = useSort();
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, ['aName', 'name', 'aCode', 'code', 'bName', 'bCode']));
  const visibleRows = sorted(filtered, (row, key) => toNumber(row[key]) ?? row[key]).slice(0, 50);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">AB Premium</p>
          <h2>AB 溢价</h2>
        </div>
        <span className="panel-count">{filtered.length} / {rows.length}</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th className="num muted" style={{ fontSize: '10px' }}>序号</th>
              <th>A股名称</th>
              <th className="mono">A股代码</th>
              <th>B股名称</th>
              <th className="mono">B股代码</th>
              <SortableTh label="A股价格" sortKey="aPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="B股价格" sortKey="bPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="B股人民币价" sortKey="bPriceCny" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="num muted" style={{ fontSize: '10px' }}>价差</th>
              <SortableTh label="溢价率" sortKey="premium" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="近三年分位" sortKey="percentile" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="样本数" sortKey="historyCount" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="muted" style={{ fontSize: '10px' }}>样本区间</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row, index) => {
              const aPrice = toNumber(row.aPrice);
              const bPriceCny = toNumber(row.bPriceCny);
              const gap = (aPrice !== null && bPriceCny !== null) ? (aPrice - bPriceCny).toFixed(2) : null;
              return (
                <tr key={`${row.aCode || row.code || index}`}>
                  <td className="num mono muted">{index + 1}</td>
                  <td>{pickText(row.aName, row.name)}</td>
                  <td className="mono">{pickText(row.aCode, row.code)}</td>
                  <td>{pickText(row.bName)}</td>
                  <td className="mono">{pickText(row.bCode)}</td>
                  <td className="num mono">{formatNumber(row.aPrice)}</td>
                  <td className="num mono">{formatNumber(row.bPrice)}</td>
                  <td className="num mono">{formatNumber(row.bPriceCny)}</td>
                  <td className="num mono muted">{gap !== null ? (Number(gap) > 0 ? '+' : '') + gap : '--'}</td>
                  <td className={`num mono ${signedClass(row.premium)}`}>{formatPercent(row.premium)}</td>
                  <td className="num mono">{formatNumber(row.percentile)}</td>
                  <td className="num mono">{formatNumber(row.historyCount)}</td>
                  <td className="muted" style={{ fontSize: '10px' }}>{pickText(row.historyStartDate, row.historyEndDate) ? `${row.historyStartDate?.slice(0,10) || ''}~${row.historyEndDate?.slice(0,10) || ''}` : '--'}</td>
                </tr>
              );
            }) : (
              <tr><td colSpan="13" className="empty-cell">AB 接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function LofTable({ rows, searchQuery }) {
  const { sortConfig, handleSort, sorted } = useSort();
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, ['name', 'fundName', 'code', 'fundCode', 'indexName']));
  const visibleRows = sorted(filtered, (row, key) => toNumber(row[key]) ?? row[key]).slice(0, 50);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">LOF Arbitrage</p>
          <h2>LOF 套利</h2>
        </div>
        <span className="panel-count">{filtered.length} / {rows.length}</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th>名称</th>
              <th className="mono">代码</th>
              <SortableTh label="现价" sortKey="price" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="涨幅" sortKey="changeRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="成交额(万)" sortKey="turnoverWan" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="净值" sortKey="nav" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="muted" style={{ fontSize: '10px' }}>净值日期</th>
              <th>相关指数</th>
              <th className="muted" style={{ fontSize: '10px' }}>申购状态</th>
              <SortableTh label="申购费" sortKey="applyFee" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="muted" style={{ fontSize: '10px' }}>赎回状态</th>
              <SortableTh label="赎回费" sortKey="redeemFee" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th className="num muted" style={{ fontSize: '10px' }}>托管费</th>
              <SortableTh label="IOPV" sortKey="iopv" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="溢价率" sortKey="premiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row, index) => (
              <tr key={`${row.code || row.fundCode || index}`}>
                <td>{pickText(row.name, row.fundName)}</td>
                <td className="mono">{pickText(row.code, row.fundCode)}</td>
                <td className="num mono">{formatNumber(row.price)}</td>
                <td className={`num mono ${signedClass(row.changeRate)}`}>{formatPercent(row.changeRate)}</td>
                <td className="num mono">{formatNumber(row.turnoverWan)}</td>
                <td className="num mono">{formatNumber(row.nav)}</td>
                <td className="mono muted" style={{ fontSize: '10px' }}>{row.navDate ? formatDate(row.navDate) : '--'}</td>
                <td className="muted">{pickText(row.indexName)}</td>
                <td className="muted" style={{ fontSize: '10px' }}>{pickText(row.applyStatus)}</td>
                <td className="num mono">{formatPercent(row.applyFee)}</td>
                <td className="muted" style={{ fontSize: '10px' }}>{pickText(row.redeemStatus)}</td>
                <td className="num mono">{formatPercent(row.redeemFee)}</td>
                <td className="num mono muted">{formatPercent(row.custodianFee)}</td>
                <td className="num mono">{formatNumber(row.iopv)}</td>
                <td className={`num mono ${signedClass(row.premiumRate)}`}>{formatPercent(row.premiumRate)}</td>
              </tr>
            )) : (
              <tr><td colSpan="15" className="empty-cell">LOF 接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function SubscriptionTable({ data, searchQuery }) {
  const ipoRows = toArray(data?.ipo?.data);
  const bondRows = toArray(data?.bonds?.data);
  const allRows = [...ipoRows, ...bondRows];
  const filtered = allRows.filter((r) => rowMatchesQuery(r, searchQuery, ['name', 'stockName', 'bondName', 'code', 'stockCode', 'bondCode']));
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Subscriptions</p>
          <h2>打新/申购</h2>
        </div>
        <span className="panel-count">{filtered.length} / {allRows.length}</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th>名称</th>
              <th className="mono">代码</th>
              <th>类型</th>
              <th>申购日</th>
              <th>中签缴款日</th>
              <th>上市日</th>
              <th className="num">申购上限</th>
              <th className="num">发行价</th>
              <th className="num">转股价</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length ? filtered.map((row, index) => (
              <tr key={`${row.code || row.stockCode || row.bondCode || index}`}>
                <td>{pickText(row.name, row.stockName, row.bondName)}</td>
                <td className="mono">{pickText(row.code, row.stockCode, row.bondCode)}</td>
                <td>{pickText(row.type)}</td>
                <td>{formatDate(row.subscribeDate)}</td>
                <td>{formatDate(row.paymentDate)}</td>
                <td>{formatDate(row.listingDate)}</td>
                <td className="num mono">{formatNumber(row.subscribeLimit)}</td>
                <td className="num mono">{formatNumber(row.issuePrice)}</td>
                <td className="num mono">{formatNumber(row.convertPrice)}</td>
              </tr>
            )) : (
              <tr><td colSpan="9" className="empty-cell">打新接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

const MONITOR_CURRENCIES = ['CNY', 'HKD', 'USD'];

function buildMonitorDetail(row) {
  const stockLeg = toNumber(row.stockRatio) !== 0 || toNumber(row.cashDistribution) !== 0;
  const cashLeg = toNumber(row.cashOptionPrice) !== 0;
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px 16px' }}>
      <div><span style={{ color: 'var(--text-faint)' }}>收购方股价: </span>{formatNumber(row.acquirerPrice)}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>目标方股价: </span>{formatNumber(row.targetPrice)}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>换股比例: </span>{formatNumber(row.stockRatio)}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>安全系数: </span>{formatNumber(row.safetyFactor)}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>现金对价: </span>{formatNumber(row.cashDistributionCny)}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>股票腿理论对价: </span>{stockLeg ? formatNumber(row.stockPayout) : '未配置'}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>股票腿价差: </span>{stockLeg ? formatNumber(row.stockSpread) : '未配置'}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>现金选择权: </span>{cashLeg ? formatNumber(row.cashPayout) : '未配置'}</div>
      <div><span style={{ color: 'var(--text-faint)' }}>现金腿价差: </span>{cashLeg ? formatNumber(row.cashSpread) : '未配置'}</div>
      <div style={{ gridColumn: '1 / -1' }}><span style={{ color: 'var(--text-faint)' }}>备注: </span>{pickText(row.note) || '无'}</div>
    </div>
  );
}

function MonitorTable({ rows, searchQuery, onRefresh }) {
  const { sortConfig, handleSort, sorted } = useSort();
  const [editing, setEditing] = React.useState(null);
  const [saving, setSaving] = React.useState(false);
  const [editorOpen, setEditorOpen] = React.useState(false);

  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, ['name', 'acquirerName', 'targetName', 'code']));
  const visibleRows = sorted(filtered, (row, key) => toNumber(row[key]) ?? row[key]).slice(0, 50);

  const openCreate = () => {
    setEditing({
      id: '', name: '', acquirerName: '', acquirerCode: '', acquirerMarket: 'A', targetName: '', targetCode: '', targetMarket: 'A',
      stockRatio: '', safetyFactor: 1, cashDistribution: '', cashDistributionCurrency: 'CNY',
      cashOptionPrice: '', cashOptionCurrency: 'CNY', note: '',
    });
    setEditorOpen(true);
  };

  const openEdit = (row) => {
    setEditing({
      id: row.id || '', name: row.name || '',
      acquirerName: row.acquirerName || '', acquirerCode: row.acquirerCode || '', acquirerMarket: row.acquirerMarket || 'A',
      targetName: row.targetName || '', targetCode: row.targetCode || '', targetMarket: row.targetMarket || 'A',
      stockRatio: row.stockRatio ?? '', safetyFactor: row.safetyFactor ?? 1,
      cashDistribution: row.cashDistribution ?? '', cashDistributionCurrency: row.cashDistributionCurrency || 'CNY',
      cashOptionPrice: row.cashOptionPrice ?? '', cashOptionCurrency: row.cashOptionCurrency || 'CNY',
      note: row.note || '',
    });
    setEditorOpen(true);
  };

  const closeEditor = () => { setEditorOpen(false); setEditing(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!editing.acquirerName || !editing.targetName) return;
    setSaving(true);
    try {
      await fetch(API_ENDPOINTS.monitor, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editing),
      });
      closeEditor();
      if (onRefresh) onRefresh();
    } catch (err) {
      alert('保存失败: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('确认删除这个监控项目吗？')) return;
    setSaving(true);
    try {
      await fetch(`${API_ENDPOINTS.monitor}/${encodeURIComponent(id)}`, { method: 'DELETE' });
      if (onRefresh) onRefresh();
    } catch (err) {
      alert('删除失败: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const updateField = (field, value) => setEditing((prev) => ({ ...prev, [field]: value }));

  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Custom Monitor</p>
          <h2>自定义监控</h2>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span className="panel-count">{filtered.length} / {rows.length}</span>
          <button className="tab-button" onClick={openCreate} disabled={saving}>新增监控</button>
        </div>
      </div>

      {editorOpen && editing && (
        <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.06)', background: 'rgba(255,255,255,0.02)' }}>
          <form onSubmit={handleSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px', marginBottom: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>监控名称</label>
                <input type="text" value={editing.name} onChange={(e) => updateField('name', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>收购方名称</label>
                <input type="text" value={editing.acquirerName} onChange={(e) => updateField('acquirerName', e.target.value)} required style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>收购方代码</label>
                <input type="text" value={editing.acquirerCode} onChange={(e) => updateField('acquirerCode', e.target.value)} required style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>收购方市场</label>
                <select value={editing.acquirerMarket} onChange={(e) => updateField('acquirerMarket', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }}>
                  <option value="A">A股</option><option value="H">港股</option><option value="B">B股</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>目标方名称</label>
                <input type="text" value={editing.targetName} onChange={(e) => updateField('targetName', e.target.value)} required style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>目标方代码</label>
                <input type="text" value={editing.targetCode} onChange={(e) => updateField('targetCode', e.target.value)} required style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>目标方市场</label>
                <select value={editing.targetMarket} onChange={(e) => updateField('targetMarket', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }}>
                  <option value="A">A股</option><option value="H">港股</option><option value="B">B股</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>换股比例</label>
                <input type="number" step="0.0001" value={editing.stockRatio} onChange={(e) => updateField('stockRatio', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>安全系数</label>
                <input type="number" min="0" max="1" step="0.0001" value={editing.safetyFactor} onChange={(e) => updateField('safetyFactor', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>现金对价</label>
                <input type="number" step="0.0001" value={editing.cashDistribution} onChange={(e) => updateField('cashDistribution', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>现金对价币种</label>
                <select value={editing.cashDistributionCurrency} onChange={(e) => updateField('cashDistributionCurrency', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }}>
                  {MONITOR_CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>现金选择权</label>
                <input type="number" step="0.0001" value={editing.cashOptionPrice} onChange={(e) => updateField('cashOptionPrice', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>现金选择权币种</label>
                <select value={editing.cashOptionCurrency} onChange={(e) => updateField('cashOptionCurrency', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }}>
                  {MONITOR_CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-faint)', marginBottom: '4px' }}>备注</label>
                <input type="text" value={editing.note} onChange={(e) => updateField('note', e.target.value)} style={{ width: '100%', background: 'var(--terminal-bg)', border: '1px solid var(--terminal-line)', color: 'var(--text)', padding: '4px 8px', fontSize: '13px' }} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button type="submit" className="tab-button active" disabled={saving}>{editing.id ? '保存修改' : '新增监控'}</button>
              <button type="button" className="tab-button" onClick={closeEditor} disabled={saving}>取消</button>
            </div>
          </form>
        </div>
      )}

      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th>监控名称</th>
              <th className="mono">收购方→目标方</th>
              <SortableTh label="目标现价" sortKey="targetPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="股票腿收益率" sortKey="stockYieldRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="现金腿收益率" sortKey="cashYieldRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="最优收益率" sortKey="bestYield" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th>备注</th>
              <th style={{ width: '100px' }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row, index) => {
              const bestYield = Math.max(
                toNumber(row.stockYieldRate) ?? -Infinity,
                toNumber(row.cashYieldRate) ?? -Infinity
              );
              return (
                <ExpandableRow key={`${row.id || row.code || index}`} detail={buildMonitorDetail(row)}>
                  <td>{pickText(row.name)}</td>
                  <td className="mono">{pickText(row.acquirerName)}→{pickText(row.targetName)}</td>
                  <td className="num mono">{formatNumber(row.targetPrice)}</td>
                  <td className={`num mono ${signedClass(row.stockYieldRate)}`}>{formatPercent(row.stockYieldRate)}</td>
                  <td className={`num mono ${signedClass(row.cashYieldRate)}`}>{formatPercent(row.cashYieldRate)}</td>
                  <td className={`num mono ${signedClass(bestYield === -Infinity ? null : bestYield)}`}>
                    {bestYield === -Infinity ? '--' : `${PERCENT_FORMAT.format(bestYield)}%`}
                  </td>
                  <td className="muted">{pickText(row.note)}</td>
                  <td>
                    <button className="tab-button" style={{ padding: '2px 8px', fontSize: '11px' }} onClick={(e) => { e.stopPropagation(); openEdit(row); }} disabled={saving}>编辑</button>
                    <button className="tab-button" style={{ padding: '2px 8px', fontSize: '11px', marginLeft: '4px' }} onClick={(e) => { e.stopPropagation(); handleDelete(row.id); }} disabled={saving}>删除</button>
                  </td>
                </ExpandableRow>
              );
            }) : (
              <tr><td colSpan="8" className="empty-cell">监控接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DividendTable({ rows, searchQuery }) {
  const { sortConfig, handleSort, sorted } = useSort();
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, ['code', 'name']));
  const visibleRows = sorted(filtered, (row, key) => {
    if (key === 'dividendYield') return toNumber(row.dividendData?.dividendYield);
    if (key === 'dividendPerShare') return toNumber(row.dividendData?.dividendPerShare);
    if (key === 'currentPrice') return toNumber(row.dividendData?.currentPrice);
    return toNumber(row[key]) ?? row[key];
  }).slice(0, 50);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Dividend Reminder</p>
          <h2>分红提醒</h2>
        </div>
        <span className="panel-count">{filtered.length} / {rows.length}</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th className="mono">代码</th>
              <th>名称</th>
              <th>登记日</th>
              <th>除权日</th>
              <th>派息日</th>
              <SortableTh label="每股分红" sortKey="dividendPerShare" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="股息率" sortKey="dividendYield" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="当前价" sortKey="currentPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
            </tr>
          </thead>
          <tbody>
            {visibleRows.length ? visibleRows.map((row, index) => {
              const dd = row.dividendData || {};
              return (
                <tr key={`${row.code || index}`}>
                  <td className="mono">{pickText(row.code)}</td>
                  <td>{pickText(row.name, dd.name)}</td>
                  <td>{formatDate(dd.recordDate)}</td>
                  <td>{formatDate(dd.exDividendDate)}</td>
                  <td>{formatDate(dd.payDate)}</td>
                  <td className="num mono">{formatNumber(dd.dividendPerShare)}</td>
                  <td className={`num mono ${signedClass(dd.dividendYield)}`}>{formatPercent(dd.dividendYield)}</td>
                  <td className="num mono">{formatNumber(dd.currentPrice)}</td>
                </tr>
              );
            }) : (
              <tr><td colSpan="8" className="empty-cell">分红接口暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function CbRightsIssueTable({ data, searchQuery }) {
  const [marketTab, setMarketTab] = React.useState('sh');
  const { sortConfig, handleSort, sorted } = useSort();
  const rows = toArray(data.sourceRows);

  const shRows = rows.filter((r) => String(r.market || '').toLowerCase() === 'sh' || String(r.stockCode || '').startsWith('6'));
  const szRows = rows.filter((r) => String(r.market || '').toLowerCase() === 'sz' || String(r.stockCode || '').match(/^[03]/));

  const marketRows = marketTab === 'sh' ? shRows : szRows;
  const isShenzhen = marketTab === 'sz';

  const applyRows = marketRows.filter((r) => r.inApplyStage === true);
  const ambushRows = marketRows.filter((r) => {
    if (r.inApplyStage === true) return false;
    const pn = String(r.progressName || '');
    const isAmbushProgress = pn.includes('上市委通过') || pn.includes('同意注册') || pn.includes('注册生效');
    return isAmbushProgress && toNumber(r.expectedReturnRate) > 6;
  });
  const waitRows = marketRows.filter((r) => {
    if (r.inApplyStage === true) return false;
    const pn = String(r.progressName || '');
    const isAmbushProgress = pn.includes('上市委通过') || pn.includes('同意注册') || pn.includes('注册生效');
    return !(isAmbushProgress && toNumber(r.expectedReturnRate) > 6);
  });

  function filterRows(list) {
    if (!searchQuery) return list;
    const q = searchQuery.toLowerCase();
    return list.filter((r) =>
      String(r.stockCode || '').toLowerCase().includes(q) ||
      String(r.stockName || '').toLowerCase().includes(q) ||
      String(r.progressName || '').toLowerCase().includes(q)
    );
  }

  function sortRows(list) {
    return sorted(list, (row, key) => {
      if (key === 'issueScaleYi') return toNumber(row.issueScaleYi);
      if (key === 'stockMarketValueYi') return toNumber(row.stockMarketValueYi);
      if (key === 'issueRatio') return toNumber(row.issueRatio);
      if (key === 'rawRequiredShares') return toNumber(row.rawRequiredShares);
      if (key === 'placementShares') return toNumber(row.placementShares);
      if (key === 'convertPrice') return toNumber(row.convertPrice);
      if (key === 'volatility250') return toNumber(row.volatility250 ?? row.volatility60);
      if (key === 'optionUnitValue') return toNumber(row.optionUnitValue);
      if (key === 'optionValue') return toNumber(row.optionValue);
      if (key === 'requiredFunds') return toNumber(row.requiredFunds);
      if (key === 'marginRequiredShares') return toNumber(row.marginRequiredShares);
      if (key === 'marginRequiredFunds') return toNumber(row.marginRequiredFunds);
      if (key === 'recordDate') return row.recordDate || '';
      if (key === 'expectedReturnRate') return toNumber(row.expectedReturnRate);
      if (key === 'marginReturnRate') return toNumber(row.marginReturnRate);
      if (key === 'expectedPeelReturnRate') return toNumber(row.expectedPeelReturnRate);
      if (key === 'marginPeelReturnRate') return toNumber(row.marginPeelReturnRate);
      if (key === 'progressDate') return row.progressDate || '';
      return toNumber(row[key]) ?? row[key];
    });
  }

  function renderSection(title, list, showRecordDate, includeMargin, includePeel) {
    const filtered = filterRows(list);
    const visible = sortRows(filtered).slice(0, 50);
    const cols = [];
    cols.push(<th className="mono">正股代码</th>);
    cols.push(<th>正股名称</th>);
    cols.push(<th>方案进展</th>);
    cols.push(<th>进展公告日</th>);
    cols.push(<th className="num">发行规模</th>);
    cols.push(<th className="num">流通市值</th>);
    cols.push(<th className="num">发行比例</th>);
    cols.push(<th className="num">原始所需股数</th>);
    cols.push(<th className="num">配售股数</th>);
    cols.push(<th className="num">转股价</th>);
    cols.push(<th className="num">波动率</th>);
    cols.push(<th className="num">单位期权价值</th>);
    cols.push(<th className="num">期权价值</th>);
    cols.push(<th className="num">所需资金</th>);
    if (includeMargin) {
      cols.push(<th className="num">两融所需股数</th>);
      cols.push(<th className="num">两融所需资金</th>);
    }
    if (showRecordDate) cols.push(<th>股权登记日</th>);
    cols.push(<th className="num">预期收益率</th>);
    if (includeMargin) cols.push(<th className="num">两融收益率</th>);
    if (includePeel) {
      cols.push(<th className="num">预期收益率去皮</th>);
      if (includeMargin) cols.push(<th className="num">两融收益率去皮</th>);
    }

    return (
      <section className="terminal-panel" style={{ marginTop: '8px' }}>
        <div className="panel-head compact-head">
          <div><p className="eyebrow">{marketTab.toUpperCase()}</p><h2>{title}</h2></div>
          <span className="panel-count">{filtered.length} / {list.length}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead><tr>{cols}</tr></thead>
            <tbody>
              {visible.length ? visible.map((row, i) => {
                const cells = [];
                cells.push(<td className="mono">{pickText(row.stockCode)}</td>);
                cells.push(<td>{pickText(row.stockName)}</td>);
                cells.push(<td>{pickText(row.progressName)}</td>);
                cells.push(<td>{formatDate(row.progressDate)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.issueScaleYi)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.stockMarketValueYi)}</td>);
                cells.push(<td className="num mono">{formatPercent(row.issueRatio)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.rawRequiredShares)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.placementShares)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.convertPrice)}</td>);
                cells.push(<td className="num mono">{formatPercent(row.volatility250 ?? row.volatility60)}</td>);
                cells.push(<td className="num mono">{toNumber(row.optionUnitValue) !== null ? Number(row.optionUnitValue).toFixed(4) : '--'}</td>);
                cells.push(<td className="num mono">{formatNumber(row.optionValue)}</td>);
                cells.push(<td className="num mono">{formatNumber(row.requiredFunds)}</td>);
                if (includeMargin) {
                  cells.push(<td className="num mono">{formatNumber(row.marginRequiredShares)}</td>);
                  cells.push(<td className="num mono">{formatNumber(row.marginRequiredFunds)}</td>);
                }
                if (showRecordDate) cells.push(<td>{formatDate(row.recordDate)}</td>);
                cells.push(<td className={`num mono ${signedClass(row.expectedReturnRate)}`}>{formatPercent(row.expectedReturnRate)}</td>);
                if (includeMargin) cells.push(<td className={`num mono ${signedClass(row.marginReturnRate)}`}>{formatPercent(row.marginReturnRate)}</td>);
                if (includePeel) {
                  cells.push(<td className={`num mono ${signedClass(row.expectedPeelReturnRate)}`}>{formatPercent(row.expectedPeelReturnRate)}</td>);
                  if (includeMargin) cells.push(<td className={`num mono ${signedClass(row.marginPeelReturnRate)}`}>{formatPercent(row.marginPeelReturnRate)}</td>);
                }
                return <tr key={`${row.stockCode || i}`}>{cells}</tr>;
              }) : (
                <tr><td colSpan={cols.length} className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  return (
    <>
      <div className="tab-nav" style={{ marginTop: '8px' }}>
        {[
          { key: 'sh', label: `沪市 (${shRows.length})` },
          { key: 'sz', label: `深市 (${szRows.length})` },
        ].map((t) => (
          <button
            key={t.key}
            className={`tab-button ${marketTab === t.key ? 'active' : ''}`}
            onClick={() => setMarketTab(t.key)}
          >{t.label}</button>
        ))}
      </div>
      {renderSection('申购阶段', applyRows, true, !isShenzhen, !isShenzhen)}
      {renderSection('埋伏阶段', ambushRows, false, !isShenzhen, !isShenzhen)}
      {renderSection('等待阶段', waitRows, false, !isShenzhen, !isShenzhen)}
    </>
  );
}

function MergerTable({ data, searchQuery }) {
  const [subTab, setSubTab] = React.useState('a_event');
  const { sortConfig, handleSort, sorted } = useSort();
  const categories = data.categories || {};

  const tabs = [
    { key: 'a_event', label: 'A股套利' },
    { key: 'hk_private', label: '港股套利' },
    { key: 'cn_private', label: '中概私有' },
    { key: 'announcement_pool', label: '最新公告' },
  ];

  const rows = toArray(categories[subTab]);

  function filterRows(list) {
    if (!searchQuery) return list;
    const q = searchQuery.toLowerCase();
    return list.filter((r) =>
      String(r.symbol || '').toLowerCase().includes(q) ||
      String(r.name || '').toLowerCase().includes(q) ||
      String(r.eventType || '').toLowerCase().includes(q) ||
      String(r.dealType || '').toLowerCase().includes(q) ||
      String(r.secName || '').toLowerCase().includes(q)
    );
  }

  function sortList(list, keyFn) {
    return sorted(list, keyFn).slice(0, 50);
  }

  function renderAEvent() {
    const filtered = filterRows(rows);
    const visible = sortList(filtered, (row, key) => {
      if (key === 'currentPrice') return toNumber(row.currentPrice);
      if (key === 'changeRate') return toNumber(row.changeRate);
      if (key === 'safeDiscountRate') return toNumber(row.safeDiscountRate);
      if (key === 'chooseDiscountRate') return toNumber(row.chooseDiscountRate);
      return toNumber(row[key]) ?? row[key];
    });
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">A-EVENT</p><h2>A股套利</h2></div>
          <span className="panel-count">{filtered.length} / {rows.length}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th className="mono">代码</th>
                <th>名称</th>
                <SortableTh label="现价" sortKey="currentPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="涨跌幅" sortKey="changeRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th className="num">安全边际价</th>
                <SortableTh label="安全边际折价" sortKey="safeDiscountRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th className="num">现金选择权价格</th>
                <SortableTh label="现金选择权折价" sortKey="chooseDiscountRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>币种</th>
                <th>事件类型</th>
                <th>官方公告</th>
              </tr>
            </thead>
            <tbody>
              {visible.length ? visible.map((row) => (
                <tr key={row.id}>
                  <td className="mono">{pickText(row.symbol)}</td>
                  <td>{pickText(row.name)}</td>
                  <td className="num mono">{formatNumber(row.currentPrice)}</td>
                  <td className={`num mono ${signedClass(row.changeRate)}`}>{formatPercent(row.changeRate)}</td>
                  <td className="num mono">{pickText(row.safePriceText, row.safePrice)}</td>
                  <td className={`num mono ${signedClass(row.safeDiscountRate)}`}>{formatPercent(row.safeDiscountRate)}</td>
                  <td className="num mono">{pickText(row.choosePriceText, row.choosePrice)}</td>
                  <td className={`num mono ${signedClass(row.chooseDiscountRate)}`}>{formatPercent(row.chooseDiscountRate)}</td>
                  <td>{pickText(row.currency)}</td>
                  <td>{pickText(row.eventType)}</td>
                  <td>{row.announcementUrl || row.detailUrl ? <a href={row.announcementUrl || row.detailUrl} target="_blank" rel="noopener noreferrer" className="terminal-link" style={{ minWidth: 'auto', padding: '2px 6px', fontSize: '11px' }}>查看</a> : '--'}</td>
                </tr>
              )) : (
                <tr><td colSpan="11" className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  function renderHkPrivate() {
    const filtered = filterRows(rows);
    const visible = sortList(filtered, (row, key) => {
      if (key === 'currentPrice') return toNumber(row.currentPrice);
      if (key === 'changeRate') return toNumber(row.changeRate);
      if (key === 'marketValue') return toNumber(row.marketValue);
      if (key === 'spreadRate') return toNumber(row.spreadRate);
      return toNumber(row[key]) ?? row[key];
    });
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">HK-PRIVATE</p><h2>港股套利</h2></div>
          <span className="panel-count">{filtered.length} / {rows.length}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th className="mono">代码</th>
                <th>名称</th>
                <SortableTh label="现价" sortKey="currentPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="涨跌幅" sortKey="changeRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="市值" sortKey="marketValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>私有化价格</th>
                <SortableTh label="套利空间" sortKey="spreadRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>私有化进程</th>
                <th>要约方</th>
                <th>要约方持股</th>
                <th>注册地</th>
                <th>收购方式</th>
                <th>可反套</th>
                <th>可卖空</th>
                <th>核心公告</th>
              </tr>
            </thead>
            <tbody>
              {visible.length ? visible.map((row) => (
                <tr key={row.id}>
                  <td className="mono">{pickText(row.symbol)}</td>
                  <td>{pickText(row.name)}</td>
                  <td className="num mono">{formatNumber(row.currentPrice)}</td>
                  <td className={`num mono ${signedClass(row.changeRate)}`}>{formatPercent(row.changeRate)}</td>
                  <td className="num mono">{pickText(row.marketValueText, row.marketValue)}</td>
                  <td className="num mono">{pickText(row.offerPriceText, row.offerPrice)}</td>
                  <td className={`num mono ${signedClass(row.spreadRate)}`}>{formatPercent(row.spreadRate)}</td>
                  <td>{pickText(row.eventStage)}</td>
                  <td>{pickText(row.offeror)}</td>
                  <td>{pickText(row.offerorHoldingText, row.offerorHolding)}</td>
                  <td>{pickText(row.registryPlace)}</td>
                  <td>{pickText(row.dealMethod)}</td>
                  <td>{row.canCounter ? '是' : '否'}</td>
                  <td>{row.canShort ? '是' : '否'}</td>
                  <td>{row.detailUrl ? <a href={row.detailUrl} target="_blank" rel="noopener noreferrer" className="terminal-link" style={{ minWidth: 'auto', padding: '2px 6px', fontSize: '11px' }}>查看</a> : '--'}</td>
                </tr>
              )) : (
                <tr><td colSpan="15" className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  function renderCnPrivate() {
    const filtered = filterRows(rows);
    const visible = sortList(filtered, (row, key) => {
      if (key === 'currentPrice') return toNumber(row.currentPrice);
      if (key === 'changeRate') return toNumber(row.changeRate);
      if (key === 'marketValue') return toNumber(row.marketValue);
      if (key === 'spreadRate') return toNumber(row.spreadRate);
      return toNumber(row[key]) ?? row[key];
    });
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">CN-PRIVATE</p><h2>中概私有</h2></div>
          <span className="panel-count">{filtered.length} / {rows.length}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th className="mono">代码</th>
                <th>名称</th>
                <SortableTh label="现价" sortKey="currentPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="涨跌幅" sortKey="changeRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="市值" sortKey="marketValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>私有化价格</th>
                <SortableTh label="套利空间" sortKey="spreadRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>进程</th>
                <th>要约方</th>
                <th>收购方式</th>
                <th>详情链接</th>
              </tr>
            </thead>
            <tbody>
              {visible.length ? visible.map((row) => (
                <tr key={row.id}>
                  <td className="mono">{pickText(row.symbol)}</td>
                  <td>{pickText(row.name)}</td>
                  <td className="num mono">{formatNumber(row.currentPrice)}</td>
                  <td className={`num mono ${signedClass(row.changeRate)}`}>{formatPercent(row.changeRate)}</td>
                  <td className="num mono">{pickText(row.marketValueText, row.marketValue)}</td>
                  <td className="num mono">{pickText(row.offerPriceText, row.offerPrice)}</td>
                  <td className={`num mono ${signedClass(row.spreadRate)}`}>{formatPercent(row.spreadRate)}</td>
                  <td>{pickText(row.eventStage)}</td>
                  <td>{pickText(row.offeror)}</td>
                  <td>{pickText(row.dealMethod)}</td>
                  <td>{row.detailUrl ? <a href={row.detailUrl} target="_blank" rel="noopener noreferrer" className="terminal-link" style={{ minWidth: 'auto', padding: '2px 6px', fontSize: '11px' }}>查看</a> : '--'}</td>
                </tr>
              )) : (
                <tr><td colSpan="11" className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  function renderAnnouncementPool() {
    const filtered = filterRows(rows);
    const visible = sortList(filtered, (row, key) => {
      if (key === 'offerPrice') return toNumber(row.offerPrice);
      if (key === 'latestPrice') return toNumber(row.latestPrice ?? row.stockPrice ?? row.price);
      if (key === 'premiumRate') return toNumber(row.premiumRate);
      return toNumber(row[key]) ?? row[key];
    });
    return (
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div><p className="eyebrow">ANNOUNCEMENT</p><h2>最新公告</h2></div>
          <span className="panel-count">{filtered.length} / {rows.length}</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table">
            <thead>
              <tr>
                <th>公告时间</th>
                <th>公司/代码</th>
                <th>交易类型</th>
                <SortableTh label="报价" sortKey="offerPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="目标现价" sortKey="latestPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <SortableTh label="报价溢价" sortKey="premiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
                <th>链接</th>
              </tr>
            </thead>
            <tbody>
              {visible.length ? visible.map((row) => {
                const lp = toNumber(row.latestPrice ?? row.stockPrice ?? row.price);
                const op = toNumber(row.offerPrice);
                const premium = lp && op ? ((op - lp) / lp) * 100 : null;
                return (
                  <tr key={row.announcementId || row.id}>
                    <td>{formatDate(row.announcementDate || row.announcementTime)} {formatTime(row.announcementTime)}</td>
                    <td>{pickText(row.secName, row.stockName)} <span className="mono muted">{pickText(row.secCode)}</span></td>
                    <td>{row.isCore ? <span className="source-pill">核心</span> : null} {pickText(row.dealType)}</td>
                    <td className="num mono">{formatNumber(row.offerPrice)}</td>
                    <td className="num mono">{formatNumber(lp)}</td>
                    <td className={`num mono ${signedClass(premium)}`}>{formatPercent(premium)}</td>
                    <td>{row.announcementUrl || row.pdfUrl ? <a href={row.announcementUrl || row.pdfUrl} target="_blank" rel="noopener noreferrer" className="terminal-link" style={{ minWidth: 'auto', padding: '2px 6px', fontSize: '11px' }}>查看</a> : '--'}</td>
                  </tr>
                );
              }) : (
                <tr><td colSpan="7" className="empty-cell">暂无数据</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    );
  }

  return (
    <>
      <div className="tab-nav" style={{ marginTop: '8px' }}>
        {tabs.map((t) => (
          <button
            key={t.key}
            className={`tab-button ${subTab === t.key ? 'active' : ''}`}
            onClick={() => setSubTab(t.key)}
          >{t.label}</button>
        ))}
      </div>
      {subTab === 'a_event' && renderAEvent()}
      {subTab === 'hk_private' && renderHkPrivate()}
      {subTab === 'cn_private' && renderCnPrivate()}
      {subTab === 'announcement_pool' && renderAnnouncementPool()}
    </>
  );
}

// ─── 概览页补充组件 ───

function OverviewConvertibleGrid({ rows }) {
  const { sortConfig, handleSort, sorted } = useSort();
  const { page, setPage, paginate } = usePagination({ pageSize: 20 });
  const filtered = rows.filter((r) => toNumber(r.premiumRate) !== null || toNumber(r.price) !== null);
  const sortedRows = sorted(filtered, (row, key) => {
    if (key === 'stockAvgTurnoverAmount20Yi') return toNumber(row.stockAvgTurnoverAmount20Yi);
    if (key === 'convertValue') return toNumber(row.convertValue);
    if (key === 'pureBondValue') return toNumber(row.pureBondValue);
    if (key === 'theoreticalPremiumRate') return toNumber(row.theoreticalPremiumRate);
    return toNumber(row[key]) ?? row[key];
  });
  const { rows: pageRows, total, totalPages } = paginate(sortedRows);

  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">CONVERTIBLE BONDS</p><h2>转债套利完整数据</h2></div>
        <span className="panel-count">{filtered.length} 条</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th>转债</th>
              <th className="mono">代码</th>
              <SortableTh label="转债价" sortKey="price" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="涨跌" sortKey="changePercent" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th>正股</th>
              <SortableTh label="正股价" sortKey="stockPrice" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="转股价值" sortKey="convertValue" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="溢价率" sortKey="premiumRate" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="双低" sortKey="doubleLow" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="剩余期限" sortKey="remainingYears" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <SortableTh label="剩余规模" sortKey="remainingSizeYi" sortConfig={sortConfig} onSort={handleSort} className="num" />
              <th>状态</th>
              <th className="num muted" style={{ width: '40px' }}></th>
            </tr>
          </thead>
          <tbody>
            {pageRows.length ? pageRows.map((row, i) => (
              <ExpandableRow
                key={`${row.code || row.bondCode || i}`}
                detail={(() => {
                  const price = toNumber(row.price);
                  const pureBond = toNumber(row.pureBondValue);
                  const pureBondPremium = (price !== null && pureBond !== null && pureBond !== 0) ? ((price - pureBond) / pureBond * 100) : null;
                  return (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px 16px' }}>
                      <div><span style={{ color: 'var(--text-faint)' }}>转股价: </span>{formatNumber(row.convertPrice)}</div>
                      <div><span style={{ color: 'var(--text-faint)' }}>转债市值比: </span>{toNumber(row.bondToStockMarketValueRatio) !== null ? (row.bondToStockMarketValueRatio * 100).toFixed(1) + '%' : '--'}</div>
                      <div><span style={{ color: 'var(--text-faint)' }}>折价ATR比: </span>{toNumber(row.discountAtrRatio) !== null ? (row.discountAtrRatio * 100).toFixed(1) + '%' : '--'}</div>
                      <div><span style={{ color: 'var(--text-faint)' }}>波动率: </span>{formatPercent(row.volatility250 ?? row.volatility60)}</div>
                      <div><span style={{ color: 'var(--text-faint)' }}>纯债溢价: </span>{pureBondPremium !== null ? pureBondPremium.toFixed(2) + '%' : '--'}</div>
                      <div><span style={{ color: 'var(--text-faint)' }}>理论溢价: </span>{formatPercent(row.theoreticalPremiumRate)}</div>
                      <div><span style={{ color: 'var(--text-faint)' }}>期权价值: </span>{formatNumber(row.optionValue)}</div>
                    </div>
                  );
                })()}
              >
                <td>{pickText(row.bondName, row.name)}</td>
                <td className="mono">{pickText(row.code, row.bondCode)}</td>
                <td className="num mono">{formatNumber(row.price)}</td>
                <td className={`num mono ${signedClass(row.changePercent)}`}>{formatPercent(row.changePercent)}</td>
                <td>{pickText(row.stockName, row.aName)}</td>
                <td className="num mono">{formatNumber(row.stockPrice)}</td>
                <td className="num mono">{formatNumber(row.convertValue)}</td>
                <td className={`num mono ${signedClass(row.premiumRate)}`}>{formatPercent(row.premiumRate)}</td>
                <td className="num mono">{formatNumber(row.doubleLow)}</td>
                <td className="num mono">{toNumber(row.remainingYears) !== null ? row.remainingYears.toFixed(1) + '年' : '--'}</td>
                <td className="num mono">{formatNumber(row.remainingSizeYi, '亿')}</td>
                <td className="muted">{pickText(row.forceRedeemStatus, row.rating)}</td>
              </ExpandableRow>
            )) : (
              <tr><td colSpan="13" className="empty-cell">暂无数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
      <Pagination page={page} totalPages={totalPages} total={total} onChange={setPage} />
    </section>
  );
}

function OverviewMonitorSummary({ rows }) {
  const topRows = rows.slice(0, 5);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">CUSTOM MONITOR</p><h2>自定义监控 TOP 5</h2></div>
        <span className="panel-count">{rows.length} 条</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th>监控名称</th>
              <th className="mono">收购方→目标方</th>
              <th className="num">目标现价</th>
              <th className="num">股票腿收益率</th>
              <th className="num">现金腿收益率</th>
              <th className="num">最优收益率</th>
            </tr>
          </thead>
          <tbody>
            {topRows.length ? topRows.map((row, i) => {
              const best = Math.max(toNumber(row.stockYieldRate) ?? -Infinity, toNumber(row.cashYieldRate) ?? -Infinity);
              return (
                <tr key={row.id || i}>
                  <td>{pickText(row.name)}</td>
                  <td className="mono">{pickText(row.acquirerName)}→{pickText(row.targetName)}</td>
                  <td className="num mono">{formatNumber(row.targetPrice)}</td>
                  <td className={`num mono ${signedClass(row.stockYieldRate)}`}>{formatPercent(row.stockYieldRate)}</td>
                  <td className={`num mono ${signedClass(row.cashYieldRate)}`}>{formatPercent(row.cashYieldRate)}</td>
                  <td className={`num mono ${signedClass(best === -Infinity ? null : best)}`}>{best === -Infinity ? '--' : `${PERCENT_FORMAT.format(best)}%`}</td>
                </tr>
              );
            }) : (
              <tr><td colSpan="6" className="empty-cell">暂无监控数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function OverviewDividendSummary({ rows }) {
  const upcoming = rows.filter((r) => {
    const dd = r.dividendData || {};
    if (!dd.recordDate) return false;
    const rd = new Date(dd.recordDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return rd >= today;
  }).slice(0, 5);
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">DIVIDEND</p><h2>分红提醒（ upcoming ）</h2></div>
        <span className="panel-count">{rows.length} 条</span>
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className="dense-table wide-table">
          <thead>
            <tr>
              <th className="mono">代码</th>
              <th>名称</th>
              <th>登记日</th>
              <th>除权日</th>
              <th className="num">每股分红</th>
              <th className="num">股息率</th>
              <th className="num">当前价</th>
            </tr>
          </thead>
          <tbody>
            {upcoming.length ? upcoming.map((row, i) => {
              const dd = row.dividendData || {};
              return (
                <tr key={row.code || i}>
                  <td className="mono">{pickText(row.code)}</td>
                  <td>{pickText(row.name, dd.name)}</td>
                  <td>{formatDate(dd.recordDate)}</td>
                  <td>{formatDate(dd.exDividendDate)}</td>
                  <td className="num mono">{formatNumber(dd.dividendPerShare)}</td>
                  <td className={`num mono ${signedClass(dd.dividendYield)}`}>{formatPercent(dd.dividendYield)}</td>
                  <td className="num mono">{formatNumber(dd.currentPrice)}</td>
                </tr>
              );
            }) : (
              <tr><td colSpan="7" className="empty-cell">暂无 upcoming 分红数据</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function App() {
  const [activeTab, setActiveTab] = React.useState('overview');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [oppFilter, setOppFilter] = React.useState('all');
  const state = useDashboardData();
  const resources = state.resources;
  const opportunities = resources ? buildOpportunityRows(resources) : [];
  const cbRows = resources ? toArray(resources.cbArb.data) : [];
  const smallRedemptionRows = resources ? toArray(resources.cbArb.smallRedemption?.rows) : [];
  const ahRows = resources ? toArray(resources.ah.data) : [];
  const abRows = resources ? toArray(resources.ab.data) : [];
  const lofRows = resources ? toArray(resources.lofArb.data?.rows) : [];
  const monitorRows = resources ? toArray(resources.monitor.data) : [];
  const subscriptionData = resources ? resources.subscriptions?.data : null;
  const dividendRows = resources ? toArray(resources.dividend?.data) : [];
  const cbRightsIssueData = resources ? (resources.cbRightsIssue?.data || {}) : {};
  const mergerData = resources ? (resources.merger?.data || {}) : {};

  const filteredOpportunities = searchQuery
    ? opportunities.filter((r) => String(r.name).toLowerCase().includes(searchQuery.toLowerCase()) || String(r.code).toLowerCase().includes(searchQuery.toLowerCase()))
    : opportunities;

  return (
    <main className="terminal-shell">
      <StatusStrip state={state} />
      {state.error ? <div className="error-strip">接口加载失败：{state.error}</div> : null}
      {resources ? (
        <>
          <TabNav activeTab={activeTab} onChange={setActiveTab} />
          {activeTab !== 'overview' && activeTab !== 'push' && (
            <SearchBar value={searchQuery} onChange={setSearchQuery} />
          )}
          {activeTab === 'overview' && (
            <>
              <div className="dashboard-grid">
                <TodayActions data={subscriptionData} />
                <BestOpportunities opportunities={opportunities} onNavigate={setActiveTab} pushConfig={resources?.pushConfig?.data} />
              </div>
              <MonitorAlerts rows={monitorRows} onNavigate={setActiveTab} />
            </>
          )}
          {activeTab === 'convertible' && <ConvertibleTable rows={cbRows} smallRows={smallRedemptionRows} rightsIssueData={cbRightsIssueData} searchQuery={searchQuery} />}
          {activeTab === 'ah' && <AhTable rows={ahRows} searchQuery={searchQuery} />}
          {activeTab === 'ab' && <AbTable rows={abRows} searchQuery={searchQuery} />}
          {activeTab === 'lof' && <LofTable rows={lofRows} searchQuery={searchQuery} />}
          {activeTab === 'subscription' && <SubscriptionTable data={subscriptionData} searchQuery={searchQuery} />}
          {activeTab === 'monitor' && <MonitorTable rows={monitorRows} searchQuery={searchQuery} onRefresh={state.reload} />}
          {activeTab === 'dividend' && <DividendTable rows={dividendRows} searchQuery={searchQuery} />}
          {activeTab === 'merger' && <MergerTable data={mergerData} searchQuery={searchQuery} />}
          {activeTab === 'push' && <PushSettingsPage config={resources?.pushConfig?.data} />}
        </>
      ) : (
        <section className="terminal-panel loading-panel">正在连接真实市场接口...</section>
      )}
    </main>
  );
}

function PushSettings({ config }) {
  if (!config) return null;
  const ds = config.deliveryStatus || {};
  const modules = config.modules || {};
  const times = Array.isArray(config.times) ? config.times : (config.time ? [config.time] : []);
  return (
    <section className="terminal-panel" style={{ marginTop: '8px' }}>
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">Push Settings</p>
          <h2>推送设置</h2>
        </div>
        <span className="panel-count">{config.enabled ? '已启用' : '已禁用'}</span>
      </div>
      <div className="dense-table-wrap">
        <table className="dense-table">
          <tbody>
            <tr>
              <td style={{ color: 'var(--terminal-muted)' }}>推送时间</td>
              <td className="mono">{times.join(', ') || '--'}</td>
            </tr>
            <tr>
              <td style={{ color: 'var(--terminal-muted)' }}>模块开关</td>
              <td>
                {Object.entries(modules).map(([key, val]) => (
                  <span key={key} className="source-pill" style={{ marginRight: '4px' }}>
                    {key}: {val ? '开' : '关'}
                  </span>
                ))}
              </td>
            </tr>
            <tr>
              <td style={{ color: 'var(--terminal-muted)' }}>Webhook</td>
              <td className="mono">{ds.webhookConfigured ? '已配置' : '未配置'}</td>
            </tr>
            <tr>
              <td style={{ color: 'var(--terminal-muted)' }}>调度器</td>
              <td className="mono">{ds.schedulerEnabled ? '运行中' : ds.schedulerDisabledReason || '已停用'}</td>
            </tr>
            <tr>
              <td style={{ color: 'var(--terminal-muted)' }}>上次推送</td>
              <td className="mono">{formatTime(ds.lastMainPushSuccessAt) || '--'}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}

function PushSettingsPage({ config }) {
  const ds = config?.deliveryStatus || {};
  const modules = config?.modules || {};
  const times = Array.isArray(config?.times) ? config.times : (config?.time ? [config.time] : []);

  const moduleLabels = {
    ahab: 'AH/AB',
    subscription: '打新',
    cbArb: '转债',
    monitor: '监控',
    dividend: '分红',
    eventArb: '事件套利',
    cbRightsIssue: '抢权配售',
    lofArb: 'LOF套利',
  };

  const moduleEntries = Object.entries(modules);

  const rc = {
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,95,106,0.12)',
    borderRadius: '12px',
    padding: '16px 20px',
    marginBottom: '12px',
  };
  const rt = {
    fontSize: '15px',
    fontWeight: 600,
    margin: '0 0 10px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };
  const badge = (c) => ({
    fontSize: '11px',
    padding: '2px 8px',
    borderRadius: '20px',
    background: c === 'g' ? 'rgba(55,208,154,0.12)' : c === 'y' ? 'rgba(255,184,94,0.12)' : 'rgba(255,85,102,0.12)',
    color: c === 'g' ? '#37d09a' : c === 'y' ? '#ffb85e' : '#ff5566',
    fontWeight: 500,
  });

  return (
    <div>
      <section className="terminal-panel" style={{ marginTop: '8px' }}>
        <div className="panel-head compact-head">
          <div><p className="eyebrow">Push Settings</p><h2>推送规则</h2></div>
          <span className="panel-count">{config?.enabled ? '已启用' : '已禁用'}</span>
        </div>
        <div className="dense-table-wrap">
          <table className="dense-table">
            <tbody>
              <tr>
                <td style={{ color: 'var(--terminal-muted)', width: '140px' }}>推送时间</td>
                <td>
                  {times.length > 0 ? (
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {times.map((t, i) => <span key={i} className="source-pill">{t}</span>)}
                    </div>
                  ) : <span className="muted">未配置</span>}
                </td>
              </tr>
              <tr>
                <td style={{ color: 'var(--terminal-muted)' }}>模块开关</td>
                <td>
                  {moduleEntries.length > 0 ? (
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {moduleEntries.map(([key, enabled]) => (
                        <span key={key} className={`source-pill ${enabled ? 'is-up' : 'muted'}`}>
                          {moduleLabels[key] || key}: {enabled ? '开' : '关'}
                        </span>
                      ))}
                    </div>
                  ) : <span className="muted">无模块配置</span>}
                </td>
              </tr>
              <tr>
                <td style={{ color: 'var(--terminal-muted)' }}>Webhook</td>
                <td className="mono">{ds.webhookConfigured ? <span className="is-up">已配置</span> : <span className="is-down">未配置</span>}</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--terminal-muted)' }}>调度器</td>
                <td className="mono">{ds.schedulerEnabled ? <span className="is-up">运行中</span> : <span className="is-down">{ds.schedulerDisabledReason || '已停用'}</span>}</td>
              </tr>
              <tr>
                <td style={{ color: 'var(--terminal-muted)' }}>上次推送</td>
                <td className="mono">{ds.lastMainPushSuccessAt ? formatTime(ds.lastMainPushSuccessAt) : <span className="muted">从未推送</span>}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="terminal-panel" style={{ marginTop: '16px' }}>
        <div className="panel-head compact-head">
          <div><p className="eyebrow">Push Rules</p><h2>规则详解</h2></div>
        </div>
        <div style={{ padding: '12px 16px' }}>
          <div style={rc}>
            <div style={rt}>主摘要定时推送 <span style={badge('g')}>定时</span></div>
            <div style={{ display: 'grid', gridTemplateColumns: '90px 1fr', gap: '6px 14px', fontSize: '13px' }}>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送内容</span><span>聚合所有模块摘要：打新、转债套利、AH溢价、AB溢价、自定义监控</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送时间</span><span><code>08:00</code> / <code>20:18</code></span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>触发条件</span><span>定时触发，非交易日也推送（可配置）</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送格式</span><span>Markdown，企业微信 Webhook</span>
            </div>
            <div style={{ marginTop: '10px', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', fontSize: '12px', color: 'var(--terminal-muted)', lineHeight: 1.6 }}>
              <strong style={{ color: 'var(--terminal-text)' }}>包含字段：</strong>各模块 TOP N 排名、套利空间、溢价率
            </div>
          </div>

          <div style={rc}>
            <div style={rt}>转债套利折价策略提醒 <span style={badge('y')}>实时</span></div>
            <div style={{ display: 'grid', gridTemplateColumns: '90px 1fr', gap: '6px 14px', fontSize: '13px' }}>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送内容</span><span>买入提醒 / 卖出提醒 / 监控名单定时推送</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送时间</span><span>交易时段内 <code>09:30 ~ 14:50</code>，每 10 分钟一档</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>触发条件</span><span>买入：<code>premiumRate &lt; -2%</code>（且已过转股日）<br/>卖出：<code>premiumRate &gt; -0.5%</code>（且该标的在监控名单中）</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>状态机</span><span>首次启动仅初始化监控名单；后续只在状态变化时触发推送</span>
            </div>
            <div style={{ marginTop: '10px', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', fontSize: '12px', color: 'var(--terminal-muted)', lineHeight: 1.6 }}>
              <strong style={{ color: 'var(--terminal-text)' }}>推送格式：</strong>代码 名称 | 价格 X.XX | 溢价率 X% | 正股 X.XX(±X%) | 转股价值 X.XX | 强赎状态
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '8px' }}>
              {['价格','溢价率','正股价格','正股涨跌幅','转股价值','强赎状态'].map(f => (
                <span key={f} style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: 'rgba(255,255,255,0.04)', color: 'var(--terminal-muted)', border: '1px solid rgba(255,255,255,0.06)' }}>{f}</span>
              ))}
            </div>
          </div>

          <div style={rc}>
            <div style={rt}>转债抢权配售独立推送 <span style={badge('g')}>定时</span></div>
            <div style={{ display: 'grid', gridTemplateColumns: '90px 1fr', gap: '6px 14px', fontSize: '13px' }}>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送内容</span><span>抢权配售正式入池项目列表</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送时间</span><span><code>08:00</code> / <code>14:30</code></span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>触发条件</span><span>交易日才推送；监控名单为空则跳过</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送格式</span><span>Markdown，独立推送不并入主摘要</span>
            </div>
          </div>

          <div style={rc}>
            <div style={rt}>LOF 套利独立推送 <span style={badge('y')}>定时+即时</span></div>
            <div style={{ display: 'grid', gridTemplateColumns: '90px 1fr', gap: '6px 14px', fontSize: '13px' }}>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送内容</span><span>LOF 限购池 / 非限购池项目</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送时间</span><span>定时：<code>13:30</code> / <code>14:00</code> / <code>14:30</code>；即时：新入池时触发</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>触发条件</span><span>定时按时间表；即时使用 seenEntryMap 去重</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送格式</span><span>Markdown，独立推送不并入主摘要</span>
            </div>
          </div>

          <div style={rc}>
            <div style={rt}>并购报告推送 <span style={badge('g')}>定时</span></div>
            <div style={{ display: 'grid', gridTemplateColumns: '90px 1fr', gap: '6px 14px', fontSize: '13px' }}>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送内容</span><span>DeepSeek AI 生成的单家公司并购简报</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送时间</span><span>每日 <code>00:00</code> 抓取后触发</span>
              <span style={{ color: 'var(--terminal-muted)', fontWeight: 500 }}>推送格式</span><span>Markdown，逐家公司推送</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default App;
