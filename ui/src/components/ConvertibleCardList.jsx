// AI-SUMMARY: 转债套利手机端卡片列表视图
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

const NUMBER_FORMAT = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 });
const PERCENT_FORMAT = new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

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

function ConvertibleCard({ row }) {
  const [expanded, setExpanded] = React.useState(false);
  const price = toNumber(row.price);
  const premium = toNumber(row.premiumRate);

  return (
    <div className="cb-card" style={{
      padding: '12px',
      borderBottom: '1px solid var(--terminal-line-soft)',
      background: 'var(--terminal-panel)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>
            {pickText(row.bondName, row.name)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--terminal-muted)', fontFamily: 'var(--terminal-mono)', marginTop: '2px' }}>
            {pickText(row.code, row.bondCode)}
          </div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: '16px', fontWeight: 700, fontFamily: 'var(--terminal-mono)' }}>
            {formatNumber(price)}
          </div>
          <div style={{ fontSize: '12px', marginTop: '2px' }} className={`mono ${signedClass(row.changePercent)}`}>
            {formatPercent(row.changePercent)}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '8px' }}>
        <div>
          <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>转股溢价率</div>
          <div className={`mono ${signedClass(premium)}`} style={{ fontSize: '14px', fontWeight: 700 }}>
            {formatPercent(premium)}
          </div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>正股</div>
          <div style={{ fontSize: '13px' }}>{pickText(row.stockName, row.aName)}</div>
          <div className="mono muted" style={{ fontSize: '11px' }}>{formatNumber(row.stockPrice)}</div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>剩余规模</div>
          <div className="mono" style={{ fontSize: '14px', fontWeight: 700 }}>{formatNumber(row.remainingSizeYi, '亿')}</div>
        </div>
      </div>

      {expanded && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 12px', padding: '8px 0', borderTop: '1px solid var(--terminal-line-soft)', fontSize: '12px' }}>
          <div><span style={{ color: 'var(--terminal-faint)' }}>转股价值: </span><span className="mono">{formatNumber(row.convertValue)}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>纯债价值: </span><span className="mono">{row.pureBondValue != null ? Number(row.pureBondValue).toFixed(2) : '--'}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>理论价值: </span><span className="mono">{row.theoreticalPrice != null ? Number(row.theoreticalPrice).toFixed(2) : '--'}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>理论套利: </span><span className={`mono ${signedClass(row.theoreticalPremiumRate)}`}>{formatPercent(row.theoreticalPremiumRate)}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>到期日: </span><span className="mono">{row.maturityDate || '--'}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>评级: </span>{pickText(row.rating)}</div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>强赎: </span>{pickText(row.forceRedeemStatus)}</div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>转股状态: </span>{row.isUnlisted ? '已退市' : (row.isBeforeConvertStart ? '未到转股期' : (row.forceRedeemStatus && row.forceRedeemStatus.includes('强赎') ? '强赎中' : '正常'))}</div>
        </div>
      )}

      <button
        onClick={() => setExpanded((v) => !v)}
        style={{
          width: '100%',
          padding: '6px',
          border: 0,
          background: 'transparent',
          color: 'var(--terminal-faint)',
          fontSize: '12px',
          cursor: 'pointer',
          marginTop: '4px',
        }}
      >
        {expanded ? '▲ 收起' : '▼ 展开'}
      </button>
    </div>
  );
}

export default function ConvertibleCardList({ rows, searchQuery }) {
  const baseFields = ['bondName', 'name', 'code', 'bondCode', 'stockName', 'aName', 'stockCode'];
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, baseFields));

  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">CONVERTIBLE ARB</p><h2>转债套利</h2></div>
        <span className="panel-count">{filtered.length} 条</span>
      </div>
      <div style={{ maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
        {filtered.length ? filtered.map((row, index) => (
          <ConvertibleCard key={`${row.code || row.bondCode || index}`} row={row} />
        )) : (
          <div className="empty-cell" style={{ padding: '24px 12px' }}>暂无数据</div>
        )}
      </div>
    </section>
  );
}
