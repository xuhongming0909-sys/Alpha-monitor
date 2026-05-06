// AI-SUMMARY: React 手机端密集行表公共格式化与展示积木
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
    <article className="dense-row">
      <div className="dense-row-main">
        <div className="dense-row-id">
          <div className="dense-row-title">{title}</div>
          <div className="dense-row-code mono">{code}</div>
          {subtitle ? <div className="dense-row-subtitle">{subtitle}</div> : null}
        </div>
        {metricLabel ? (
          <div className="dense-row-metric">
            <div className="dense-row-metric-label">{metricLabel}</div>
            <div className={`dense-row-metric-value mono ${metricClassName}`.trim()}>{metricValue}</div>
          </div>
        ) : null}
      </div>
      <div className="dense-row-fields">{children}</div>
      {footer ? <div className="dense-row-footer">{footer}</div> : null}
    </article>
  );
}

export function FieldPair({ label, value, className = '', long = false }) {
  return (
    <div className={`row-field ${long ? 'row-field-long' : ''}`.trim()}>
      <span className="field-label">{label}</span>
      <span className={`field-value ${className}`.trim()}>{value}</span>
    </div>
  );
}

export function EmptyState({ text = '暂无数据' }) {
  return <div className="empty-cell card-empty">{text}</div>;
}
