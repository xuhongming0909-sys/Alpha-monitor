// AI-SUMMARY: React 简洁模块表格公共组件，复用旧网页端风格的表头和数据行
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

function renderCell(column, row, index) {
  const raw = typeof column.render === 'function' ? column.render(row, index) : row?.[column.key];
  const className = [
    column.numeric ? 'num' : '',
    typeof column.className === 'function' ? column.className(row, index) : (column.className || ''),
  ].filter(Boolean).join(' ');

  return <td key={column.key || column.label} className={className}>{raw ?? '--'}</td>;
}

export default function SimpleDataTable({
  eyebrow,
  title,
  count,
  columns = [],
  rows = [],
  emptyText = '暂无数据',
  tableClassName = '',
}) {
  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h2>{title}</h2>
        </div>
        {count !== undefined ? <span className="panel-count">{count}</span> : null}
      </div>
      <div className="dense-table-wrap table-scroll">
        <table className={`dense-table wide-table ${tableClassName}`.trim()}>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key || column.label} className={column.numeric ? 'num' : ''}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.length ? rows.map((row, index) => (
              <tr key={row.id || row.code || row.aCode || row.stockCode || row.bondCode || index}>
                {columns.map((column) => renderCell(column, row, index))}
              </tr>
            )) : (
              <tr>
                <td colSpan={columns.length || 1} className="empty-cell">{emptyText}</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
