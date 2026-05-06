// AI-SUMMARY: 手机端密集卡片列表通用帮助函数与基础卡片壳
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

const NUMBER_FORMAT = new Intl.NumberFormat('zh-CN', { maximumFractionDigits: 2 });
const PERCENT_FORMAT = new Intl.NumberFormat('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

export function toNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

export function pickText(...values) {
  for (const value of values) {
    const text = String(value ?? '').trim();
    if (text) return text;
  }
  return '--';
}

export function rowMatchesQuery(row, query, fields) {
  if (!query) return true;
  const lower = String(query).toLowerCase();
  return fields.some((field) => String(readValue(row, field) ?? '').toLowerCase().includes(lower));
}

export function signedClass(value) {
  const number = toNumber(value);
  if (number === null || number === 0) return 'is-flat';
  return number > 0 ? 'is-up' : 'is-down';
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

export function formatDateTime(value) {
  if (!value) return '--';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return `${date.toLocaleDateString('zh-CN')} ${date.toLocaleTimeString('zh-CN', { hour12: false })}`;
}

export function formatSignedNumber(value, suffix = '') {
  const number = toNumber(value);
  if (number === null) return '--';
  const sign = number > 0 ? '+' : '';
  return `${sign}${NUMBER_FORMAT.format(number)}${suffix}`;
}

export function formatRatioPercent(value) {
  const number = toNumber(value);
  return number === null ? '--' : `${PERCENT_FORMAT.format(number * 100)}%`;
}

export function formatValue(value, type = 'text', suffix = '') {
  if (type === 'number') return formatNumber(value, suffix);
  if (type === 'percent') return formatPercent(value);
  if (type === 'ratioPercent') return formatRatioPercent(value);
  if (type === 'date') return formatDate(value);
  if (type === 'datetime') return formatDateTime(value);
  if (type === 'signedNumber') return formatSignedNumber(value, suffix);
  if (type === 'signedPercent') return formatPercent(value);
  return pickText(value);
}

export function readValue(row, accessor) {
  if (typeof accessor === 'function') return accessor(row);
  return row?.[accessor];
}

function resolveTone(type, value, row) {
  if (typeof type === 'function') return type(value, row);
  if (type === 'signedPercent' || type === 'signedNumber') return signedClass(value);
  return '';
}

function resolveLabel(field, row) {
  if (typeof field.label === 'function') return field.label(row);
  return field.label;
}

function renderMetaValue(field, row) {
  const rawValue = readValue(row, field.key);
  const value = field.format ? field.format(rawValue, row) : formatValue(rawValue, field.type, field.suffix);
  const tone = resolveTone(field.tone || field.type, rawValue, row);

  return (
    <div key={field.id || String(field.key)} style={{ minWidth: 0 }}>
      <div style={{ fontSize: '10px', color: 'var(--terminal-faint)', marginBottom: '2px' }}>
        {resolveLabel(field, row)}
      </div>
      <div className={tone ? `mono ${tone}` : 'mono'} style={{ fontSize: '13px', fontWeight: 700, lineHeight: 1.35, whiteSpace: 'pre-line', wordBreak: 'break-all' }}>
        {value}
      </div>
    </div>
  );
}

function renderFieldRow(field, row) {
  const rawValue = readValue(row, field.key);
  const label = resolveLabel(field, row);
  const value = field.format ? field.format(rawValue, row) : formatValue(rawValue, field.type, field.suffix);
  const tone = resolveTone(field.tone || field.type, rawValue, row);

  return (
    <div
      key={field.id || String(field.key)}
      style={{
        display: 'grid',
        gridTemplateColumns: '88px 1fr',
        gap: '8px',
        alignItems: 'start',
        padding: '5px 0',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
      }}
    >
      <span style={{ fontSize: '11px', color: 'var(--terminal-faint)', lineHeight: 1.5 }}>{label}</span>
      <span className={tone ? `mono ${tone}` : 'mono'} style={{ fontSize: '12px', lineHeight: 1.5, whiteSpace: 'pre-line', wordBreak: 'break-all' }}>
        {value}
      </span>
    </div>
  );
}

export function DenseCardList({
  title,
  eyebrow,
  rows = [],
  searchQuery = '',
  searchFields = [],
  getKey,
  renderHeader,
  metaFields = [],
  fieldGroups = [],
  emptyText = '暂无数据',
}) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, searchFields));

  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{title}</h2>
        </div>
        <span className="panel-count">{filtered.length} 条</span>
      </div>
      <div style={{ maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
        {filtered.length ? filtered.map((row, index) => (
          <article
            key={typeof getKey === 'function' ? getKey(row, index) : index}
            style={{
              padding: '12px',
              borderBottom: '1px solid var(--terminal-line-soft)',
              background: 'var(--terminal-panel)',
            }}
          >
            {renderHeader(row, index)}
            {metaFields.length ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '8px', marginBottom: '8px' }}>
                {metaFields.map((field) => renderMetaValue(field, row))}
              </div>
            ) : null}
            <div style={{ borderTop: '1px solid var(--terminal-line-soft)' }}>
              {fieldGroups.flatMap((group) => {
                const items = typeof group.when === 'function' && !group.when(row) ? [] : group.fields;
                return items.map((field) => renderFieldRow(field, row));
              })}
            </div>
          </article>
        )) : (
          <div className="empty-cell" style={{ padding: '24px 12px' }}>{emptyText}</div>
        )}
      </div>
    </section>
  );
}
