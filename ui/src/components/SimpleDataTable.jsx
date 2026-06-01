// AI-SUMMARY: React 简洁模块表格公共组件，复用旧网页端风格的表头和数据行
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import { toNumber } from './cardHelpers.jsx';

function renderCell(column, row, index) {
  const raw = typeof column.render === 'function' ? column.render(row, index) : row?.[column.key];
  const className = [
    column.numeric ? 'num' : '',
    typeof column.className === 'function' ? column.className(row, index) : (column.className || ''),
  ].filter(Boolean).join(' ');

  return <td key={column.key || column.label} className={className}>{raw ?? '--'}</td>;
}

function useSort() {
  const [sortConfig, setSortConfig] = React.useState({ key: null, direction: 'asc' });
  const handleSort = React.useCallback((key) => {
    setSortConfig((current) => ({
      key,
      direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc',
    }));
  }, []);
  const sorted = React.useCallback((rows, columns, isPinned) => {
    const doSort = (list) => {
      if (!sortConfig.key || !list.length) return list;
      const { key, direction } = sortConfig;
      const column = columns.find((c) => (c.sortKey || c.key) === key);
      const getValue = column?.sortValue ? column.sortValue : (row) => toNumber(row[key]) ?? row[key];
      return [...list].sort((a, b) => {
        const av = getValue(a);
        const bv = getValue(b);
        if (av == null && bv == null) return 0;
        if (av == null) return 1;
        if (bv == null) return -1;
        if (typeof av === 'number' && typeof bv === 'number') {
          return direction === 'asc' ? av - bv : bv - av;
        }
        return direction === 'asc' ? String(av).localeCompare(String(bv)) : String(bv).localeCompare(String(av));
      });
    };
    if (!isPinned) return doSort(rows);
    // 始终分离置顶和非置顶，各自独立排序
    const pinned = rows.filter(isPinned);
    const rest = rows.filter((r) => !isPinned(r));
    return [...doSort(pinned), ...doSort(rest)];
  }, [sortConfig]);
  return { sortConfig, handleSort, sorted };
}

export default function SimpleDataTable({
  eyebrow,
  title,
  count,
  columns = [],
  rows = [],
  emptyText = '暂无数据',
  tableClassName = '',
  isPinned,
}) {
  const { sortConfig, handleSort, sorted } = useSort();
  const sortedRows = sorted(rows, columns, isPinned);

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
              {columns.map((column) => {
                const sortKey = column.sortKey || column.key;
                const isActive = sortConfig.key === sortKey;
                const arrow = isActive ? (sortConfig.direction === 'asc' ? ' ▲' : ' ▼') : '';
                return (
                  <th
                    key={column.key || column.label}
                    className={[column.numeric ? 'num' : '', isActive ? 'sort-active' : ''].filter(Boolean).join(' ')}
                    onClick={() => sortKey && handleSort(sortKey)}
                    style={{ cursor: 'pointer' }}
                  >
                    {column.label}{arrow}
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody>
            {sortedRows.length ? sortedRows.map((row, index) => (
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
