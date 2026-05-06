// AI-SUMMARY: AB溢价简洁模块表格，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function renderGap(row) {
  const aPrice = toNumber(row.aPrice);
  const bPriceCny = toNumber(row.bPriceCny);
  if (aPrice === null || bPriceCny === null) return '--';
  const gap = aPrice - bPriceCny;
  return `${gap > 0 ? '+' : ''}${gap.toFixed(2)}`;
}

export default function AbCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, ['aName', 'name', 'aCode', 'code', 'bName', 'bCode']));

  const columns = [
    { key: 'index', label: '#', numeric: true, render: (_, index) => index + 1 },
    { key: 'aName', label: 'A股名称', render: (row) => pickText(row.aName, row.name) },
    { key: 'aCode', label: 'A股代码', render: (row) => <span className="mono">{pickText(row.aCode, row.code)}</span> },
    { key: 'bName', label: 'B股名称', render: (row) => pickText(row.bName) },
    { key: 'bCode', label: 'B股代码', render: (row) => <span className="mono">{pickText(row.bCode)}</span> },
    { key: 'aPrice', label: 'A股价格', numeric: true, render: (row) => formatNumber(row.aPrice) },
    { key: 'bPriceCny', label: 'B股人民币价', numeric: true, render: (row) => formatNumber(row.bPriceCny) },
    { key: 'gap', label: '价差', numeric: true, className: (row) => signedClass((toNumber(row.aPrice) ?? 0) - (toNumber(row.bPriceCny) ?? 0)), render: (row) => renderGap(row) },
    { key: 'premium', label: '溢价率', numeric: true, className: (row) => signedClass(row.premium), render: (row) => formatPercent(row.premium) },
    { key: 'percentile', label: '近三年分位', numeric: true, render: (row) => formatNumber(row.percentile) },
    { key: 'historyCount', label: '样本数', numeric: true, render: (row) => formatNumber(row.historyCount) },
    { key: 'historyRange', label: '样本区间', render: (row) => `${row.historyStartDate ? formatDate(row.historyStartDate) : '--'} ~ ${row.historyEndDate ? formatDate(row.historyEndDate) : '--'}` },
  ];

  return <SimpleDataTable eyebrow="AB PREMIUM" title="AB 溢价" count={`${filtered.length} 条`} columns={columns} rows={filtered} emptyText="AB 接口暂无数据" />;
}
