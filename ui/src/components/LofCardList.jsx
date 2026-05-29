// AI-SUMMARY: LOF IOPV 估值表格，统一展示
// 对应 INDEX.md 9.3 文件摘要索引
import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function formatFee(value) {
  const n = toNumber(value);
  return n === null ? '--' : `${n}%`;
}

function formatShare(value) {
  const n = toNumber(value);
  if (n === null) return '--';
  return n >= 10000 ? `${(n / 10000).toFixed(1)}亿` : `${n.toFixed(0)}万`;
}

function formatStockPosition(row) {
  const v = toNumber(row.stockPosition);
  if (v === null) return '--';
  return `${v.toFixed(1)}%`;
}

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) =>
    rowMatchesQuery(row, searchQuery, ['name', 'code', 'fundCompany', 'calcTarget'])
  );
  const sorted = [...filtered].sort(
    (a, b) => Math.abs(toNumber(b.premiumRate) ?? 0) - Math.abs(toNumber(a.premiumRate) ?? 0)
  );

  const columns = [
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code)}</span> },
    { key: 'name', label: '名称', render: (row) => pickText(row.name) },
    { key: 'nav', label: 'T-2净值', numeric: true, render: (row) => formatNumber(row.nav) },
    { key: 'navDate', label: '净值日期', render: (row) => formatDate(row.navDate) },
    { key: 'price', label: '现价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'iopv', label: '实时估值', numeric: true, render: (row) => formatNumber(row.iopv) },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'applyStatus', label: '申购状态', render: (row) => pickText(row.applyStatus) },
    { key: 'shareIncrease', label: '新增份额', numeric: true, render: (row) => formatShare(row.shareIncrease) },
    { key: 'shareTotal', label: '原有份额', numeric: true, render: (row) => formatShare(row.shareTotal) },
    { key: 'applyFee', label: '申购费', numeric: true, render: (row) => formatFee(row.applyFee) },
    { key: 'redeemFee', label: '赎回费', numeric: true, render: (row) => formatFee(row.redeemFee) },
    { key: 'custodianFee', label: '托管费', numeric: true, render: (row) => formatFee(row.custodianFee) },
    { key: 'fundCompany', label: '基金公司', render: (row) => pickText(row.fundCompany) },
    { key: 'calcTarget', label: '估值标的', render: (row) => <span className="muted" style={{fontSize: '0.85em'}}>{pickText(row.calcTarget)}</span> },
    { key: 'stockPosition', label: '总仓位', numeric: true, render: (row) => formatStockPosition(row) },
    { key: 'mae', label: '平均误差', numeric: true, render: (row) => row.mae != null ? `${row.mae.toFixed(2)}%` : '--' },
    { key: 'maxErr', label: 'MAX误差', numeric: true, render: (row) => row.maxErr != null ? `${row.maxErr.toFixed(2)}%` : '--' },
    { key: 'samplePeriod', label: '样本区间', render: (row) => pickText(row.samplePeriod) || '--' },
  ];

  return (
    <SimpleDataTable
      eyebrow="LOF IOPV"
      title="QDII LOF 估值"
      count={`${sorted.length} 条`}
      columns={columns}
      rows={sorted}
      emptyText="LOF 接口暂无数据"
    />
  );
}
