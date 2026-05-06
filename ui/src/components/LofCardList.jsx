// AI-SUMMARY: LOF套利简洁模块表格，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass } from './cardHelpers.jsx';

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, ['name', 'fundName', 'code', 'fundCode', 'indexName']));

  const columns = [
    { key: 'name', label: '名称', render: (row) => pickText(row.name, row.fundName) },
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code, row.fundCode)}</span> },
    { key: 'price', label: '现价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'changeRate', label: '涨幅', numeric: true, className: (row) => signedClass(row.changeRate), render: (row) => formatPercent(row.changeRate) },
    { key: 'turnoverWan', label: '成交额(万)', numeric: true, render: (row) => formatNumber(row.turnoverWan) },
    { key: 'nav', label: '净值', numeric: true, render: (row) => formatNumber(row.nav) },
    { key: 'navDate', label: '净值日期', render: (row) => formatDate(row.navDate) },
    { key: 'indexName', label: '相关指数', render: (row) => pickText(row.indexName) },
    { key: 'applyStatus', label: '申购状态', render: (row) => pickText(row.applyStatus) },
    { key: 'redeemStatus', label: '赎回状态', render: (row) => pickText(row.redeemStatus) },
    { key: 'iopv', label: 'IOPV', numeric: true, render: (row) => formatNumber(row.iopv) },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
  ];

  return <SimpleDataTable eyebrow="LOF ARBITRAGE" title="LOF 套利" count={`${filtered.length} 条`} columns={columns} rows={filtered} emptyText="LOF 接口暂无数据" />;
}
