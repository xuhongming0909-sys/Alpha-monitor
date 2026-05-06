// AI-SUMMARY: React 手机端统一看板主组件，负责真实接口加载、概览摘要流和七标签导航接线
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import ConvertibleCardList from './components/ConvertibleCardList.jsx';
import BottomNav from './components/BottomNav.jsx';
import AhCardList from './components/AhCardList.jsx';
import AbCardList from './components/AbCardList.jsx';
import LofCardList from './components/LofCardList.jsx';
import SubscriptionCardList from './components/SubscriptionCardList.jsx';
import RightsIssueCardList from './components/RightsIssueCardList.jsx';
import MonitorCardList from './components/MonitorCardList.jsx';
import {
  DenseCard,
  EmptyState,
  FieldPair,
  SectionPanel,
  bestYieldValue,
  formatDate,
  formatNumber,
  formatPercent,
  formatTime,
  pickText,
  rowMatchesQuery,
  signedClass,
  toNumber,
} from './components/cardHelpers.jsx';

const API_ENDPOINTS = {
  health: '/api/health',
  resourceStatus: '/api/dashboard/resource-status',
  cbArb: '/api/market/convertible-bond-arbitrage',
  ah: '/api/market/ah',
  ab: '/api/market/ab',
  lofArb: '/api/market/lof-arbitrage',
  monitor: '/api/monitors',
  subscriptions: '/api/market/subscriptions',
  cbRightsIssue: '/api/market/cb-rights-issue',
};

const MONITOR_CURRENCIES = ['CNY', 'HKD', 'USD'];

function unwrap(payload, fallback) {
  if (!payload || typeof payload !== 'object') return fallback;
  if ('data' in payload) return payload.data ?? fallback;
  return payload;
}

function toArray(value) {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.data)) return value.data;
  if (Array.isArray(value?.rows)) return value.rows;
  return [];
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

function useDashboardData() {
  const [state, setState] = React.useState({ loading: true, error: '', resources: null, updatedAt: '' });

  const load = React.useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: '' }));
    const criticalEndpoints = [
      { key: 'health', url: API_ENDPOINTS.health, fallback: {} },
      { key: 'resourceStatus', url: `${API_ENDPOINTS.resourceStatus}?keys=exchangeRate,cbArb,ah,ab,lofArb,cbRightsIssue`, fallback: {} },
      { key: 'cbArb', url: API_ENDPOINTS.cbArb, fallback: {} },
      { key: 'ah', url: API_ENDPOINTS.ah, fallback: [] },
      { key: 'ab', url: API_ENDPOINTS.ab, fallback: [] },
      { key: 'lofArb', url: API_ENDPOINTS.lofArb, fallback: [] },
      { key: 'monitor', url: API_ENDPOINTS.monitor, fallback: [] },
      { key: 'cbRightsIssue', url: API_ENDPOINTS.cbRightsIssue, fallback: {} },
    ];

    const resources = {};
    const errors = [];
    const results = await Promise.allSettled(criticalEndpoints.map((endpoint) => fetchJson(endpoint.url)));
    results.forEach((result, index) => {
      const { key, fallback } = criticalEndpoints[index];
      if (result.status === 'fulfilled') {
        if (key === 'cbArb') {
          const raw = result.value || fallback;
          const rows = unwrap(raw, fallback);
          const normalizeRows = (items) => {
            if (!Array.isArray(items)) return;
            for (const row of items) {
              if (row && row.optionValue == null && row.callOptionValue != null) {
                row.optionValue = row.callOptionValue;
              }
            }
          };
          normalizeRows(rows);
          normalizeRows(raw?.smallRedemption?.rows);
          resources[key] = { data: rows, smallRedemption: raw?.smallRedemption || null };
        } else {
          resources[key] = { data: unwrap(result.value, fallback) };
        }
      } else {
        resources[key] = { data: fallback, error: result.reason?.message || 'failed' };
        errors.push(`${key}: ${result.reason?.message || 'failed'}`);
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

function sortByNumber(rows, getter, direction = 'desc') {
  return [...rows].sort((a, b) => {
    const av = getter(a);
    const bv = getter(b);
    if (av === null && bv === null) return 0;
    if (av === null) return 1;
    if (bv === null) return -1;
    return direction === 'asc' ? av - bv : bv - av;
  });
}

function todayText() {
  return new Date().toISOString().slice(0, 10);
}

function sameDay(value, today) {
  return Boolean(value && String(value).startsWith(today));
}

function theoreticalOpportunity(row) {
  const price = toNumber(row.price);
  const theoreticalPrice = toNumber(row.theoreticalPrice);
  if (price === null || theoreticalPrice === null || price <= 0 || theoreticalPrice <= price) return null;
  return ((theoreticalPrice - price) / price) * 100;
}

function buildSubscriptionRows(data) {
  const ipoRows = toArray(data?.ipo?.data).map((row) => ({ ...row, type: row.type || '新股' }));
  const bondRows = toArray(data?.bonds?.data).map((row) => ({ ...row, type: row.type || '债券' }));
  return [...ipoRows, ...bondRows];
}

function buildOverviewSections(resources, today = todayText()) {
  const subscriptions = buildSubscriptionRows(resources?.subscriptions?.data);
  const todaySubscriptions = subscriptions
    .map((row) => {
      if (sameDay(row.subscribeDate, today)) return { ...row, stage: '今日申购', stageRank: 1, stageDate: row.subscribeDate };
      if (sameDay(row.paymentDate, today)) return { ...row, stage: '今日缴款', stageRank: 2, stageDate: row.paymentDate };
      if (sameDay(row.listingDate, today)) return { ...row, stage: '今日上市', stageRank: 3, stageDate: row.listingDate };
      return null;
    })
    .filter(Boolean)
    .sort((a, b) => a.stageRank - b.stageRank || pickText(a.code, a.stockCode, a.bondCode).localeCompare(pickText(b.code, b.stockCode, b.bondCode)));

  const rightsRows = toArray(resources?.cbRightsIssue?.data?.sourceRows)
    .filter((row) => row.pushEligible === true && sameDay(row.recordDate, today))
    .sort((a, b) => (toNumber(b.marginPeelReturnRate) ?? -Infinity) - (toNumber(a.marginPeelReturnRate) ?? -Infinity));

  const cbRows = toArray(resources?.cbArb?.data);
  const discountRows = sortByNumber(
    cbRows.filter((row) => {
      const premium = toNumber(row.premiumRate);
      return premium !== null && premium < 0;
    }),
    (row) => toNumber(row.premiumRate),
    'asc'
  );

  const smallRows = sortByNumber(
    toArray(resources?.cbArb?.smallRedemption?.rows),
    (row) => toNumber(row.smallRedemptionTotalAnnualizedYield),
    'desc'
  );

  const theoreticalRows = sortByNumber(
    cbRows.filter((row) => {
      const space = theoreticalOpportunity(row);
      return space !== null && space > 10;
    }),
    (row) => theoreticalOpportunity(row),
    'desc'
  );

  function premiumExtremes(rows) {
    const valid = rows.filter((row) => toNumber(row.premium) !== null);
    const top = sortByNumber(valid, (row) => toNumber(row.premium), 'desc').slice(0, 3);
    const used = new Set(top.map((row) => pickText(row.aCode, row.code)));
    const bottom = sortByNumber(valid, (row) => toNumber(row.premium), 'asc')
      .filter((row) => !used.has(pickText(row.aCode, row.code)))
      .slice(0, 3);
    return { top, bottom };
  }

  const monitorRows = sortByNumber(
    toArray(resources?.monitor?.data).filter((row) => {
      const bestYield = bestYieldValue(row);
      return bestYield !== -Infinity && bestYield > 30;
    }),
    (row) => bestYieldValue(row),
    'desc'
  );

  return {
    todaySubscriptions,
    rightsRows,
    discountRows,
    smallRows,
    theoreticalRows,
    ah: premiumExtremes(toArray(resources?.ah?.data)),
    ab: premiumExtremes(toArray(resources?.ab?.data)),
    monitorRows,
  };
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
        {state.loading ? <span className="status-loading">刷新中...</span> : null}
        <span className="mono muted">{formatTime(state.updatedAt)}</span>
      </div>
      <button className="terminal-action" type="button" onClick={state.reload}>刷新</button>
    </header>
  );
}

function SearchBar({ value, onChange }) {
  return (
    <div className="search-bar">
      <input
        className="search-input"
        type="text"
        placeholder="搜索代码或名称..."
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}

function OverviewSection({ eyebrow, title, count, children }) {
  return (
    <SectionPanel eyebrow={eyebrow} title={title} count={count}>
      <div className="overview-card-list">
        {children}
      </div>
    </SectionPanel>
  );
}

function OverviewPage({ resources, onNavigate }) {
  const sections = buildOverviewSections(resources);

  return (
    <div className="overview-flow">
      <OverviewSection eyebrow="TODAY" title="今日打新" count={`${sections.todaySubscriptions.length} 项`}>
        {sections.todaySubscriptions.length ? sections.todaySubscriptions.map((row, index) => (
          <DenseCard
            key={`${pickText(row.code, row.stockCode, row.bondCode)}-${index}`}
            title={pickText(row.name, row.stockName, row.bondName)}
            code={pickText(row.code, row.stockCode, row.bondCode)}
            subtitle={pickText(row.type)}
            metricLabel={row.stage}
            metricValue={formatDate(row.stageDate)}
            metricClassName={row.stage === '今日申购' ? 'is-up' : row.stage === '今日缴款' ? 'is-down' : 'is-flat'}
          >
            <FieldPair label="申购日" value={formatDate(row.subscribeDate)} className="mono" />
            <FieldPair label="缴款日" value={formatDate(row.paymentDate)} className="mono" />
            <FieldPair label="上市日" value={formatDate(row.listingDate)} className="mono" />
            <FieldPair label="申购上限" value={formatNumber(row.subscribeLimit)} className="mono" />
            <FieldPair label="发行价" value={formatNumber(row.issuePrice)} className="mono" />
            <FieldPair label="转股价" value={formatNumber(row.convertPrice)} className="mono" />
          </DenseCard>
        )) : <EmptyState text="今日暂无打新事项" />}
      </OverviewSection>

      <OverviewSection eyebrow="RIGHTS ISSUE" title="配售登记" count={`${sections.rightsRows.length} 项`}>
        {sections.rightsRows.length ? sections.rightsRows.map((row, index) => (
          <DenseCard
            key={`${row.stockCode || index}`}
            title={pickText(row.stockName)}
            code={pickText(row.stockCode)}
            subtitle={pickText(row.progressName)}
            metricLabel="两融去皮收益率"
            metricValue={formatPercent(row.marginPeelReturnRate)}
            metricClassName={signedClass(row.marginPeelReturnRate)}
          >
            <FieldPair label="股权登记日" value={formatDate(row.recordDate)} className="mono" />
            <FieldPair label="两融收益率" value={formatPercent(row.marginReturnRate)} className={`mono ${signedClass(row.marginReturnRate)}`} />
            <FieldPair label="预期收益率" value={formatPercent(row.expectedReturnRate)} className={`mono ${signedClass(row.expectedReturnRate)}`} />
            <FieldPair label="进展状态" value={pickText(row.progressName)} long />
          </DenseCard>
        )) : <EmptyState text="今日暂无入推送名单的配售登记" />}
      </OverviewSection>

      <OverviewSection eyebrow="CB DISCOUNT" title="折价套利" count={`${sections.discountRows.length} 条`}>
        {sections.discountRows.length ? sections.discountRows.map((row, index) => (
          <DenseCard
            key={`${row.code || row.bondCode || index}`}
            title={pickText(row.bondName, row.name)}
            code={pickText(row.code, row.bondCode)}
            subtitle={pickText(row.stockName, row.aName)}
            metricLabel="转股溢价率"
            metricValue={formatPercent(row.premiumRate)}
            metricClassName={signedClass(row.premiumRate)}
          >
            <FieldPair label="转债价格" value={formatNumber(row.price)} className="mono" />
            <FieldPair label="正股" value={pickText(row.stockName, row.aName)} />
            <FieldPair label="正股价格" value={formatNumber(row.stockPrice)} className="mono" />
            <FieldPair label="转股价值" value={formatNumber(row.convertValue)} className="mono" />
            <FieldPair label="转股溢价率" value={formatPercent(row.premiumRate)} className={`mono ${signedClass(row.premiumRate)}`} />
          </DenseCard>
        )) : <EmptyState text="暂无折价套利机会" />}
      </OverviewSection>

      <OverviewSection eyebrow="SMALL REDEMPTION" title="小额刚兑" count={`${sections.smallRows.length} 条`}>
        {sections.smallRows.length ? sections.smallRows.map((row, index) => (
          <DenseCard
            key={`${row.code || row.bondCode || index}`}
            title={pickText(row.bondName, row.name)}
            code={pickText(row.code, row.bondCode)}
            subtitle={pickText(row.stockName)}
            metricLabel="总年化收益率"
            metricValue={formatPercent(row.smallRedemptionTotalAnnualizedYield)}
            metricClassName={signedClass(row.smallRedemptionTotalAnnualizedYield)}
          >
            <FieldPair label="刚兑年化" value={formatPercent(row.smallRedemptionAnnualizedYield)} className={`mono ${signedClass(row.smallRedemptionAnnualizedYield)}`} />
            <FieldPair label="期权年化" value={formatPercent(row.smallRedemptionOptionAnnualizedYield)} className={`mono ${signedClass(row.smallRedemptionOptionAnnualizedYield)}`} />
            <FieldPair label="总年化收益率" value={formatPercent(row.smallRedemptionTotalAnnualizedYield)} className={`mono ${signedClass(row.smallRedemptionTotalAnnualizedYield)}`} />
          </DenseCard>
        )) : <EmptyState text="暂无小额刚兑机会" />}
      </OverviewSection>

      <OverviewSection eyebrow="THEORETICAL" title="理论折价套利" count={`${sections.theoreticalRows.length} 条`}>
        {sections.theoreticalRows.length ? sections.theoreticalRows.map((row, index) => {
          const space = theoreticalOpportunity(row);
          return (
            <DenseCard
              key={`${row.code || row.bondCode || index}`}
              title={pickText(row.bondName, row.name)}
              code={pickText(row.code, row.bondCode)}
              subtitle={pickText(row.stockName, row.aName)}
              metricLabel="套利空间"
              metricValue={space === null ? '--' : `${space.toFixed(2)}%`}
              metricClassName={signedClass(space)}
            >
              <FieldPair label="转债价格" value={formatNumber(row.price)} className="mono" />
              <FieldPair label="理论价值" value={formatNumber(row.theoreticalPrice)} className="mono" />
              <FieldPair label="套利空间" value={space === null ? '--' : `${space.toFixed(2)}%`} className={`mono ${signedClass(space)}`} />
            </DenseCard>
          );
        }) : <EmptyState text="暂无理论套利空间大于 10% 的机会" />}
      </OverviewSection>

      <PremiumOverview title="AH 机会" rows={sections.ah} peerCodeKey="hCode" onClick={() => onNavigate('ah')} />
      <PremiumOverview title="AB 机会" rows={sections.ab} peerCodeKey="bCode" onClick={() => onNavigate('ab')} />

      <OverviewSection eyebrow="CUSTOM MONITOR" title="自定义监控" count={`${sections.monitorRows.length} 条`}>
        {sections.monitorRows.length ? sections.monitorRows.map((row, index) => {
          const bestYield = bestYieldValue(row);
          return (
            <DenseCard
              key={`${row.id || index}`}
              title="自定义"
              code={`${pickText(row.acquirerName)} → ${pickText(row.targetName)}`}
              subtitle={pickText(row.name, row.note)}
              metricLabel="最优收益率"
              metricValue={bestYield === -Infinity ? '--' : `${bestYield.toFixed(3)}%`}
              metricClassName={signedClass(bestYield === -Infinity ? null : bestYield)}
            >
              <FieldPair label="目标现价" value={formatNumber(row.targetPrice)} className="mono" />
              <FieldPair label="换股收益率" value={formatPercent(row.stockYieldRate)} className={`mono ${signedClass(row.stockYieldRate)}`} />
              <FieldPair label="现金收益率" value={formatPercent(row.cashYieldRate)} className={`mono ${signedClass(row.cashYieldRate)}`} />
              <FieldPair label="最优收益率" value={bestYield === -Infinity ? '--' : `${bestYield.toFixed(3)}%`} className={`mono ${signedClass(bestYield === -Infinity ? null : bestYield)}`} />
            </DenseCard>
          );
        }) : <EmptyState text="暂无最优收益率大于 30% 的自定义机会" />}
      </OverviewSection>
    </div>
  );
}

function PremiumOverview({ title, rows, peerCodeKey, onClick }) {
  const items = [
    ...rows.top.map((row) => ({ row, tag: '前三' })),
    ...rows.bottom.map((row) => ({ row, tag: '倒三' })),
  ];

  return (
    <OverviewSection eyebrow="PREMIUM" title={title} count={`${items.length} 条`}>
      {items.length ? items.map(({ row, tag }, index) => (
        <DenseCard
          key={`${title}-${row.aCode || row.code || index}`}
          title={pickText(row.aName, row.name)}
          code={`${pickText(row.aCode, row.code)} / ${pickText(row[peerCodeKey])}`}
          subtitle={tag}
          metricLabel="溢价率"
          metricValue={formatPercent(row.premium)}
          metricClassName={signedClass(row.premium)}
          footer={<button type="button" className="tab-button" onClick={onClick}>查看全部</button>}
        />
      )) : <EmptyState text={`${title} 暂无数据`} />}
    </OverviewSection>
  );
}

function ConvertiblePage({ rows, smallRows, rightsIssueData, searchQuery }) {
  const [subTab, setSubTab] = React.useState('main');
  const riRows = toArray(rightsIssueData?.sourceRows);
  const discountRows = sortByNumber(
    rows.filter((row) => {
      const premium = toNumber(row.premiumRate);
      return premium !== null && premium < 0;
    }),
    (row) => toNumber(row.premiumRate),
    'asc'
  );
  const theoreticalRows = sortByNumber(
    rows.filter((row) => {
      const price = toNumber(row.price);
      const theoreticalPrice = toNumber(row.theoreticalPrice);
      return price !== null && theoreticalPrice !== null && price < theoreticalPrice;
    }),
    (row) => theoreticalOpportunity(row),
    'desc'
  );
  const sortedSmallRows = sortByNumber(smallRows, (row) => toNumber(row.smallRedemptionTotalAnnualizedYield), 'desc');

  return (
    <>
      <div className="subtab-row convertible-subtabs">
        {[
          { key: 'main', label: `主页 (${rows.length})` },
          { key: 'discount', label: `折价套利 (${discountRows.length})` },
          { key: 'theoretical', label: `理论折价 (${theoreticalRows.length})` },
          { key: 'small', label: `小额刚兑 (${smallRows.length})` },
          { key: 'rights', label: `抢权配售 (${riRows.length})` },
        ].map((tab) => (
          <button key={tab.key} type="button" className={`tab-button ${subTab === tab.key ? 'active' : ''}`} onClick={() => setSubTab(tab.key)}>
            {tab.label}
          </button>
        ))}
      </div>
      {subTab === 'main' && <ConvertibleCardList title="转债套利" eyebrow="CONVERTIBLE ARB" rows={rows} searchQuery={searchQuery} variant="home" />}
      {subTab === 'discount' && <ConvertibleCardList title="折价套利" eyebrow="CB DISCOUNT" rows={discountRows} searchQuery={searchQuery} variant="discount" />}
      {subTab === 'theoretical' && <ConvertibleCardList title="理论折价套利" eyebrow="THEORETICAL DISCOUNT" rows={theoreticalRows} searchQuery={searchQuery} variant="theoretical" />}
      {subTab === 'small' && <ConvertibleCardList title="小额刚兑" eyebrow="SMALL REDEMPTION" rows={sortedSmallRows} searchQuery={searchQuery} variant="small_redemption" />}
      {subTab === 'rights' && <RightsIssueCardList rows={riRows} searchQuery={searchQuery} />}
    </>
  );
}

function MonitorEditor({ editing, saving, onClose, onSubmit, onChange }) {
  if (!editing) return null;
  return (
    <section className="terminal-panel monitor-editor">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">CUSTOM EDITOR</p>
          <h2>{editing.id ? '编辑自定义' : '新增自定义'}</h2>
        </div>
      </div>
      <form onSubmit={onSubmit} className="monitor-form">
        <div className="monitor-form-section">
          <h3>收购方</h3>
          <label>名称<input value={editing.acquirerName} onChange={(e) => onChange('acquirerName', e.target.value)} required /></label>
          <label>代码<input value={editing.acquirerCode} onChange={(e) => onChange('acquirerCode', e.target.value)} required /></label>
          <label>市场<select value={editing.acquirerMarket} onChange={(e) => onChange('acquirerMarket', e.target.value)}><option value="A">A股</option><option value="H">港股</option><option value="B">B股</option></select></label>
        </div>
        <div className="monitor-form-section">
          <h3>目标方</h3>
          <label>名称<input value={editing.targetName} onChange={(e) => onChange('targetName', e.target.value)} required /></label>
          <label>代码<input value={editing.targetCode} onChange={(e) => onChange('targetCode', e.target.value)} required /></label>
          <label>市场<select value={editing.targetMarket} onChange={(e) => onChange('targetMarket', e.target.value)}><option value="A">A股</option><option value="H">港股</option><option value="B">B股</option></select></label>
        </div>
        <div className="monitor-form-section">
          <h3>交易条款</h3>
          <label>监控名<input value={editing.name} onChange={(e) => onChange('name', e.target.value)} /></label>
          <label>换股比例<input type="number" step="0.0001" value={editing.stockRatio} onChange={(e) => onChange('stockRatio', e.target.value)} /></label>
          <label>安全系数<input type="number" min="0" max="1" step="0.0001" value={editing.safetyFactor} onChange={(e) => onChange('safetyFactor', e.target.value)} /></label>
          <label>现金对价<input type="number" step="0.0001" value={editing.cashDistribution} onChange={(e) => onChange('cashDistribution', e.target.value)} /></label>
          <label>现金对价币种<select value={editing.cashDistributionCurrency} onChange={(e) => onChange('cashDistributionCurrency', e.target.value)}>{MONITOR_CURRENCIES.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
          <label>现金选择权<input type="number" step="0.0001" value={editing.cashOptionPrice} onChange={(e) => onChange('cashOptionPrice', e.target.value)} /></label>
          <label>现金选择权币种<select value={editing.cashOptionCurrency} onChange={(e) => onChange('cashOptionCurrency', e.target.value)}>{MONITOR_CURRENCIES.map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
          <label>备注<input value={editing.note} onChange={(e) => onChange('note', e.target.value)} /></label>
        </div>
        <div className="card-footer-actions">
          <button type="submit" className="tab-button active" disabled={saving}>{editing.id ? '保存修改' : '新增自定义'}</button>
          <button type="button" className="tab-button" onClick={onClose} disabled={saving}>取消</button>
        </div>
      </form>
    </section>
  );
}

function MonitorPage({ rows, searchQuery, onRefresh }) {
  const [editing, setEditing] = React.useState(null);
  const [saving, setSaving] = React.useState(false);

  const openCreate = () => setEditing({
    id: '',
    name: '',
    acquirerName: '',
    acquirerCode: '',
    acquirerMarket: 'A',
    targetName: '',
    targetCode: '',
    targetMarket: 'A',
    stockRatio: '',
    safetyFactor: 1,
    cashDistribution: '',
    cashDistributionCurrency: 'CNY',
    cashOptionPrice: '',
    cashOptionCurrency: 'CNY',
    note: '',
  });

  const openEdit = (row) => setEditing({
    id: row.id || '',
    name: row.name || '',
    acquirerName: row.acquirerName || '',
    acquirerCode: row.acquirerCode || '',
    acquirerMarket: row.acquirerMarket || 'A',
    targetName: row.targetName || '',
    targetCode: row.targetCode || '',
    targetMarket: row.targetMarket || 'A',
    stockRatio: row.stockRatio ?? '',
    safetyFactor: row.safetyFactor ?? 1,
    cashDistribution: row.cashDistribution ?? '',
    cashDistributionCurrency: row.cashDistributionCurrency || 'CNY',
    cashOptionPrice: row.cashOptionPrice ?? '',
    cashOptionCurrency: row.cashOptionCurrency || 'CNY',
    note: row.note || '',
  });

  const closeEditor = () => setEditing(null);
  const updateField = (field, value) => setEditing((current) => ({ ...current, [field]: value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!editing.acquirerName || !editing.targetName) return;
    setSaving(true);
    try {
      const response = await fetch(API_ENDPOINTS.monitor, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editing),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      closeEditor();
      onRefresh();
    } catch (error) {
      alert(`保存失败: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('确认删除这个监控项目吗？')) return;
    setSaving(true);
    try {
      const response = await fetch(`${API_ENDPOINTS.monitor}/${encodeURIComponent(id)}`, { method: 'DELETE' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      onRefresh();
    } catch (error) {
      alert(`删除失败: ${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const visibleRows = sortByNumber(
    rows.filter((row) => rowMatchesQuery(row, searchQuery, ['name', 'acquirerName', 'targetName', 'acquirerCode', 'targetCode'])),
    (row) => bestYieldValue(row),
    'desc'
  );

  return (
    <div className="monitor-page">
      <div className="page-action-row">
        <button type="button" className="tab-button active" onClick={openCreate} disabled={saving}>新增自定义</button>
      </div>
      {editing ? (
        <MonitorEditor
          editing={editing}
          saving={saving}
          onClose={closeEditor}
          onSubmit={handleSubmit}
          onChange={updateField}
        />
      ) : null}
      <MonitorCardList rows={visibleRows} searchQuery="" onEdit={openEdit} onDelete={handleDelete} saving={saving} />
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = React.useState('overview');
  const [searchQuery, setSearchQuery] = React.useState('');
  const state = useDashboardData();
  const resources = state.resources;

  const cbRows = resources ? toArray(resources.cbArb.data) : [];
  const smallRedemptionRows = resources ? toArray(resources.cbArb.smallRedemption?.rows) : [];
  const ahRows = resources ? toArray(resources.ah.data) : [];
  const abRows = resources ? toArray(resources.ab.data) : [];
  const lofRows = resources ? toArray(resources.lofArb.data?.rows) : [];
  const monitorRows = resources ? toArray(resources.monitor.data) : [];
  const subscriptionRows = resources ? buildSubscriptionRows(resources.subscriptions?.data) : [];
  const cbRightsIssueData = resources ? (resources.cbRightsIssue?.data || {}) : {};

  return (
    <>
      <main className="terminal-shell">
        <StatusStrip state={state} />
        {state.error ? <div className="error-strip">接口加载失败：{state.error}</div> : null}
        {resources ? (
          <>
            {activeTab !== 'overview' ? <SearchBar value={searchQuery} onChange={setSearchQuery} /> : null}
            {activeTab === 'overview' && <OverviewPage resources={resources} onNavigate={setActiveTab} />}
            {activeTab === 'convertible' && <ConvertiblePage rows={cbRows} smallRows={smallRedemptionRows} rightsIssueData={cbRightsIssueData} searchQuery={searchQuery} />}
            {activeTab === 'ah' && <AhCardList rows={ahRows} searchQuery={searchQuery} />}
            {activeTab === 'ab' && <AbCardList rows={abRows} searchQuery={searchQuery} />}
            {activeTab === 'lof' && <LofCardList rows={lofRows} searchQuery={searchQuery} />}
            {activeTab === 'subscription' && <SubscriptionCardList rows={subscriptionRows} searchQuery={searchQuery} />}
            {activeTab === 'monitor' && <MonitorPage rows={monitorRows} searchQuery={searchQuery} onRefresh={state.reload} />}
          </>
        ) : (
          <section className="terminal-panel loading-panel">正在连接真实市场接口...</section>
        )}
      </main>
      <BottomNav activeTab={activeTab} onChange={setActiveTab} />
    </>
  );
}

export default App;
