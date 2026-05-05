// AI-SUMMARY: LOF套利全局卡片列表视图
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

const PERCENT_FORMAT = new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

function toNumber(value) {
  if (value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function formatNumber(value, suffix = '') {
  const number = toNumber(value);
  return number === null ? '--' : `${number.toLocaleString('zh-CN', { maximumFractionDigits: 2 })}${suffix}`;
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

function LofCard({ row }) {
  const [expanded, setExpanded] = React.useState(false);

  return (
    <div className="lof-card" style={{
      padding: '12px',
      borderBottom: '1px solid var(--terminal-line-soft)',
      background: 'var(--terminal-panel)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>
            {pickText(row.name, row.fundName)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--terminal-muted)', fontFamily: 'var(--terminal-mono)', marginTop: '2px' }}>
            {pickText(row.code, row.fundCode)}
          </div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: '12px', color: 'var(--terminal-faint)' }}>溢价率</div>
          <div className={`mono ${signedClass(row.premiumRate)}`} style={{ fontSize: '18px', fontWeight: 700 }}>
            {formatPercent(row.premiumRate)}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '8px' }}>
        <div>
          <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>现价</div>
          <div className="mono" style={{ fontSize: '14px', fontWeight: 700 }}>{formatNumber(row.price)}</div>
          <div className={`mono ${signedClass(row.changeRate)}`} style={{ fontSize: '11px' }}>{formatPercent(row.changeRate)}</div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>净值</div>
          <div className="mono" style={{ fontSize: '14px', fontWeight: 700 }}>{formatNumber(row.nav)}</div>
          <div className="mono muted" style={{ fontSize: '11px' }}>{row.navDate ? new Date(row.navDate).toLocaleDateString('zh-CN') : '--'}</div>
        </div>
        <div>
          <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>相关指数</div>
          <div style={{ fontSize: '13px' }}>{pickText(row.indexName)}</div>
        </div>
      </div>

      {expanded && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 12px', padding: '8px 0', borderTop: '1px solid var(--terminal-line-soft)', fontSize: '12px' }}>
          <div><span style={{ color: 'var(--terminal-faint)' }}>IOPV: </span><span className="mono">{formatNumber(row.iopv)}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>成交额: </span><span className="mono">{formatNumber(row.turnoverWan)}万</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>申购: </span>{pickText(row.applyStatus)}</div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>赎回: </span>{pickText(row.redeemStatus)}</div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>申购费: </span><span className="mono">{formatPercent(row.applyFee)}</span></div>
          <div><span style={{ color: 'var(--terminal-faint)' }}>赎回费: </span><span className="mono">{formatPercent(row.redeemFee)}</span></div>
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

export default function LofCardList({ rows, searchQuery }) {
  const filtered = rows.filter((r) => rowMatchesQuery(r, searchQuery, ['name', 'fundName', 'code', 'fundCode', 'indexName']));

  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div><p className="eyebrow">LOF ARBITRAGE</p><h2>LOF 套利</h2></div>
        <span className="panel-count">{filtered.length} 条</span>
      </div>
      <div style={{ maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
        {filtered.length ? filtered.map((row, index) => (
          <LofCard key={`${row.code || row.fundCode || index}`} row={row} />
        )) : (
          <div className="empty-cell" style={{ padding: '24px 12px' }}>暂无数据</div>
        )}
      </div>
    </section>
  );
}
