// AI-SUMMARY: AH溢价简洁模块表格，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function renderGap(row) {
  const aPrice = toNumber(row.aPrice);
  const hPriceCny = toNumber(row.hPriceCny);
  if (aPrice === null || hPriceCny === null) return '--';
  const gap = aPrice - hPriceCny;
  return `${gap > 0 ? '+' : ''}${gap.toFixed(2)}`;
}

export default function AhCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, ['aName', 'name', 'aCode', 'code', 'hName', 'hCode']));

  const columns = [
    { key: 'index', label: '#', numeric: true, render: (_, index) => index + 1 },
    { key: 'aName', label: 'A股名称', render: (row) => pickText(row.aName, row.name) },
    { key: 'aCode', label: 'A股代码', render: (row) => <span className="mono">{pickText(row.aCode, row.code)}</span> },
    { key: 'hName', label: 'H股名称', render: (row) => pickText(row.hName) },
    { key: 'hCode', label: 'H股代码', render: (row) => <span className="mono">{pickText(row.hCode)}</span> },
    { key: 'aPrice', label: 'A股价格', numeric: true, render: (row) => formatNumber(row.aPrice) },
    { key: 'hPriceCny', label: 'H股人民币价', numeric: true, render: (row) => formatNumber(row.hPriceCny) },
    { key: 'gap', label: '价差', numeric: true, className: (row) => signedClass((toNumber(row.aPrice) ?? 0) - (toNumber(row.hPriceCny) ?? 0)), render: (row) => renderGap(row) },
    { key: 'premium', label: '溢价率', numeric: true, className: (row) => signedClass(row.premium), render: (row) => formatPercent(row.premium) },
    { key: 'percentile', label: '近三年分位', numeric: true, render: (row) => formatNumber(row.percentile) },
    { key: 'historyCount', label: '样本数', numeric: true, render: (row) => formatNumber(row.historyCount) },
    { key: 'historyRange', label: '样本区间', render: (row) => `${row.historyStartDate ? formatDate(row.historyStartDate) : '--'} ~ ${row.historyEndDate ? formatDate(row.historyEndDate) : '--'}` },
  ];

  return <SimpleDataTable eyebrow="AH PREMIUM" title="AH 溢价" count={`${filtered.length} 条`} columns={columns} rows={filtered} emptyText="AH 接口暂无数据" />;
}
