// AI-SUMMARY: 打新申购简洁模块表格，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, pickText, rowMatchesQuery } from './cardHelpers.jsx';

function flattenRows(data) {
  const ipoRows = Array.isArray(data?.ipo?.data) ? data.ipo.data : [];
  const bondRows = Array.isArray(data?.bonds?.data) ? data.bonds.data : [];
  return [...ipoRows, ...bondRows];
}

export default function SubscriptionCardList({ rows, data, searchQuery = '' }) {
  const sourceRows = Array.isArray(rows) ? rows : flattenRows(data);
  const filtered = sourceRows.filter((row) => rowMatchesQuery(row, searchQuery, ['name', 'stockName', 'bondName', 'code', 'stockCode', 'bondCode']));

  const columns = [
    { key: 'name', label: '名称', render: (row) => pickText(row.name, row.stockName, row.bondName) },
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code, row.stockCode, row.bondCode)}</span> },
    { key: 'type', label: '类型', render: (row) => pickText(row.type) },
    { key: 'subscribeDate', label: '申购日', render: (row) => formatDate(row.subscribeDate) },
    { key: 'paymentDate', label: '中签缴款日', render: (row) => formatDate(row.paymentDate) },
    { key: 'listingDate', label: '上市日', render: (row) => formatDate(row.listingDate) },
    { key: 'subscribeLimit', label: '申购上限', numeric: true, render: (row) => formatNumber(row.subscribeLimit) },
    { key: 'issuePrice', label: '发行价', numeric: true, render: (row) => formatNumber(row.issuePrice) },
    { key: 'convertPrice', label: '转股价', numeric: true, render: (row) => formatNumber(row.convertPrice) },
  ];

  return <SimpleDataTable eyebrow="SUBSCRIPTIONS" title="打新申购" count={`${filtered.length} 条`} columns={columns} rows={filtered} emptyText="打新接口暂无数据" />;
}
