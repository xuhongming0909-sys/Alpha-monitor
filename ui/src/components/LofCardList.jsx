// LOF IOPV 估值卡片 - 18字段完整版
import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function formatFee(value) {
  const n = toNumber(value);
  return n === null ? '--' : `${n}%`;
}

function formatStockPosition(row) {
  const v = toNumber(row.stockPosition);
  if (v === null) return '--';
  const method = row.calcMethod || '';
  return method.includes('指数') ? `反推${v.toFixed(1)}%` : `${v.toFixed(1)}%`;
}

function formatPremiumStatus(row) {
  const ps = row.premiumStatus;
  if (!ps) return '--';
  const cls = ps === '溢价' ? 'positive' : ps === '折价' ? 'negative' : '';
  return <span className={cls}>{ps}</span>;
}

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) =>
    rowMatchesQuery(row, searchQuery, ['name', 'code', 'fundCompany', 'calcMethod'])
  );
  const sorted = [...filtered].sort(
    (a, b) => Math.abs(toNumber(b.premiumRate) ?? 0) - Math.abs(toNumber(a.premiumRate) ?? 0)
  );

  // 18字段
  const columns = [
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code)}</span> },
    { key: 'name', label: '名称', render: (row) => pickText(row.name) },
    { key: 'currency', label: '币种', render: (row) => row.currency || 'CNY' },
    { key: 'nav', label: '净值', numeric: true, render: (row) => formatNumber(row.nav) },
    { key: 'navDate', label: '净值日期', render: (row) => formatDate(row.navDate) },
    { key: 'price', label: '现价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'iopv', label: '实时估值', numeric: true, render: (row) => formatNumber(row.iopv) },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'applyFee', label: '申购费', numeric: true, render: (row) => formatFee(row.applyFee) },
    { key: 'applyStatus', label: '申购状态', render: (row) => pickText(row.applyStatus) },
    { key: 'redeemFee', label: '赎回费', numeric: true, render: (row) => formatFee(row.redeemFee) },
    { key: 'custodianFee', label: '托管费', numeric: true, render: (row) => formatFee(row.custodianFee) },
    { key: 'fundCompany', label: '基金公司', render: (row) => pickText(row.fundCompany) },
    { key: 'calcMethod', label: '估值方法', render: (row) => pickText(row.calcMethod) },
    { key: 'calcStatus', label: '估值状态', render: (row) => <span className="muted">{pickText(row.calcStatus)}</span> },
    { key: 'stockPosition', label: '仓位', numeric: true, render: (row) => formatStockPosition(row) },
    { key: 'benchmark', label: '基准指数', render: (row) => pickText(row.benchmark) },
    { key: 'premiumStatus', label: '溢价状态', render: (row) => formatPremiumStatus(row) },
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