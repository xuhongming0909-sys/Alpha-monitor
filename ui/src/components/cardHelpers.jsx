// AI-SUMMARY: React 手机端卡片视图公共格式化与展示积木
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

const NUMBER_FORMAT = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 });
const PERCENT_FORMAT = new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function toNumber(value) {
  if (value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

export function formatNumber(value, suffix = '') {
  const number = toNumber(value);
  return number === null ? '--' : `${NUMBER_FORMAT.format(number)}${suffix}`;
}

export function formatPercent(value) {
  const number = toNumber(value);
  return number === null ? '--' : `${PERCENT_FORMAT.format(number)}%`;
}

export function formatDate(value) {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString('zh-CN');
}

export function formatTime(value) {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleTimeString('zh-CN', { hour12: false });
}

export function pickText(...values) {
  for (const value of values) {
    const text = String(value ?? '').trim();
    if (text) return text;
  }
  return '--';
}

export function signedClass(value) {
  const number = toNumber(value);
  if (number === null || number === 0) return 'is-flat';
  return number > 0 ? 'is-up' : 'is-down';
}

export function rowMatchesQuery(row, query, fields) {
  if (!query) return true;
  const lower = query.toLowerCase();
  return fields.some((field) => String(row?.[field] || '').toLowerCase().includes(lower));
}

export function bestYieldValue(row) {
  return Math.max(
    toNumber(row?.maxYieldRate) ?? -Infinity,
    toNumber(row?.stockYieldRate) ?? -Infinity,
    toNumber(row?.cashYieldRate) ?? -Infinity
  );
}

export function SectionPanel({ eyebrow, title, count, children, className = '' }) {
  return (
    <section className={`terminal-panel main-table-panel ${className}`.trim()}>
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{title}</h2>
        </div>
        {count !== undefined ? <span className="panel-count">{count}</span> : null}
      </div>
      {children}
    </section>
  );
}

export function DenseCard({ title, code, metricLabel, metricValue, metricClassName = '', subtitle, children, footer }) {
  return (
    <article
      className="dense-card"
      style={{
        padding: '12px',
        borderBottom: '1px solid var(--terminal-line-soft)',
        background: 'var(--terminal-panel)',
      }}
    >
      <div className="dense-card-head" style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
        <div className="dense-card-title-wrap" style={{ minWidth: 0 }}>
          <div className="dense-card-title" style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>{title}</div>
          <div className="dense-card-code mono" style={{ fontSize: '12px', color: 'var(--terminal-muted)', marginTop: '2px', wordBreak: 'break-all' }}>{code}</div>
          {subtitle ? <div className="dense-card-subtitle" style={{ fontSize: '11px', color: 'var(--terminal-faint)', marginTop: '2px', wordBreak: 'break-all' }}>{subtitle}</div> : null}
        </div>
        {metricLabel ? (
          <div className="dense-card-metric" style={{ textAlign: 'right', flexShrink: 0 }}>
            <div className="dense-card-metric-label" style={{ fontSize: '11px', color: 'var(--terminal-faint)' }}>{metricLabel}</div>
            <div className={`dense-card-metric-value mono ${metricClassName}`.trim()} style={{ fontSize: '16px', fontWeight: 700, marginTop: '2px' }}>{metricValue}</div>
          </div>
        ) : null}
      </div>
      <div className="dense-card-fields" style={{ borderTop: '1px solid var(--terminal-line-soft)' }}>{children}</div>
      {footer ? <div className="dense-card-footer" style={{ paddingTop: '8px', marginTop: '4px' }}>{footer}</div> : null}
    </article>
  );
}

export function FieldPair({ label, value, className = '', long = false }) {
  return (
    <div
      className={`card-field ${long ? 'card-field-long' : ''}`.trim()}
      style={{
        display: 'grid',
        gridTemplateColumns: '88px 1fr',
        gap: '8px',
        alignItems: 'start',
        padding: '5px 0',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
      }}
    >
      <span className="field-label" style={{ fontSize: '11px', color: 'var(--terminal-faint)', lineHeight: 1.5 }}>{label}</span>
      <span className={`field-value ${className}`.trim()} style={{ fontSize: '12px', lineHeight: 1.5, whiteSpace: 'pre-line', wordBreak: 'break-all' }}>{value}</span>
    </div>
  );
}

export function EmptyState({ text = '暂无数据' }) {
  return <div className="empty-cell card-empty">{text}</div>;
}
