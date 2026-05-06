// AI-SUMMARY: 自定义监控简洁模块表格，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { bestYieldValue, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass } from './cardHelpers.jsx';

export default function MonitorCardList({ rows = [], searchQuery = '', onEdit = () => {}, onDelete = () => {}, saving = false }) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, ['name', 'acquirerName', 'targetName', 'acquirerCode', 'targetCode']));

  const columns = [
    { key: 'title', label: '名称', render: () => '自定义' },
    { key: 'pair', label: '收购方 / 目标方', render: (row) => `${pickText(row.acquirerName)} → ${pickText(row.targetName)}` },
    { key: 'targetPrice', label: '目标现价', numeric: true, render: (row) => formatNumber(row.targetPrice) },
    { key: 'stockYieldRate', label: '换股收益率', numeric: true, className: (row) => signedClass(row.stockYieldRate), render: (row) => formatPercent(row.stockYieldRate) },
    { key: 'cashYieldRate', label: '现金收益率', numeric: true, className: (row) => signedClass(row.cashYieldRate), render: (row) => formatPercent(row.cashYieldRate) },
    { key: 'bestYield', label: '最优收益率', numeric: true, className: (row) => signedClass(bestYieldValue(row)), render: (row) => {
      const value = bestYieldValue(row);
      return value === -Infinity ? '--' : `${value.toFixed(3)}%`;
    } },
    { key: 'note', label: '备注', render: (row) => pickText(row.name, row.note) },
    { key: 'actions', label: '操作', render: (row) => (
      <div className="card-footer-actions">
        <button type="button" className="tab-button" onClick={() => onEdit(row)} disabled={saving}>编辑</button>
        <button type="button" className="tab-button" onClick={() => onDelete(row.id)} disabled={saving}>删除</button>
      </div>
    ) },
  ];

  return <SimpleDataTable eyebrow="CUSTOM MONITOR" title="自定义监控" count={`${filtered.length} 条`} columns={columns} rows={filtered} emptyText="监控接口暂无数据" tableClassName="monitor-table" />;
}
