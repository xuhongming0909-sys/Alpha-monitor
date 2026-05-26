// AI-SUMMARY: LOF/IOPV 估值卡片，展示实时溢价率、估值核心、持仓明细
// 对应 INDEX.md §9 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function formatFee(value) {
  const n = toNumber(value);
  return n === null ? '--' : `${n}%`;
}

function formatBacktest(bt) {
  if (!bt || bt.r2 == null) return '待回测';
  const parts = [`R²=${bt.r2.toFixed(3)}`];
  if (bt.mae != null) parts.push(`MAE=${bt.mae.toFixed(4)}`);
  if (bt.maxErr != null) parts.push(`MAX=${bt.maxErr.toFixed(4)}`);
  return parts.join(' ');
}

function formatHoldingsSummary(holdings) {
  if (!Array.isArray(holdings) || holdings.length === 0) return '--';
  const ok = holdings.filter(h => h.status === 'ok');
  if (ok.length === 0) return `${holdings.length}只(无有效)`;
  const names = ok.slice(0, 3).map(h => h.name).join(',');
  return ok.length > 3 ? `${names}...等${ok.length}只` : names;
}

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) =>
    rowMatchesQuery(row, searchQuery, ['name', 'fundName', 'code', 'fundCode', 'indexName', 'fundCompany'])
  );

  const sorted = [...filtered].sort(
    (a, b) => Math.abs(toNumber(b.premiumRate) ?? 0) - Math.abs(toNumber(a.premiumRate) ?? 0)
  );

  const columns = [
    { key: 'name', label: '名称', render: (row) => pickText(row.name, row.fundName) },
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code, row.fundCode)}</span> },
    { key: 'fundType', label: '类型', render: (row) => {
      const t = row.fundType;
      if (!t) return '--';
      const labels = { A: 'A指数', B: 'B持仓', C: 'C拟合', D: 'D折价' };
      return <span className="mono">{labels[t] || t}</span>;
    }},
    { key: 'currency', label: '币种', render: (row) => row.currency || 'CNY' },
    { key: 'price', label: '现价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'nav', label: 'T-2净值', numeric: true, render: (row) => formatNumber(row.nav) },
    { key: 'navDate', label: '净值日期', render: (row) => formatDate(row.navDate) },
    { key: 'iopv', label: '实时估值', numeric: true, render: (row) => formatNumber(row.iopv) },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'applyStatus', label: '申购状态', render: (row) => pickText(row.applyStatus) },
    { key: 'shareAmountIncreaseWan', label: '新增份额(万)', numeric: true, render: (row) => formatNumber(row.shareAmountIncreaseWan) },
    { key: 'shareAmountWan', label: '原有份额(万)', numeric: true, render: (row) => formatNumber(row.shareAmountWan) },
    { key: 'applyFee', label: '申购费', numeric: true, render: (row) => formatFee(row.applyFee) },
    { key: 'redeemFee', label: '赎回费', numeric: true, render: (row) => formatFee(row.redeemFee) },
    { key: 'custodianFee', label: '托管费', numeric: true, render: (row) => formatFee(row.custodianFee) },
    { key: 'fundCompany', label: '基金公司', render: (row) => pickText(row.fundCompany) },
    { key: 'calcMode', label: '估值核心', render: (row) => pickText(row.calcMode, row.indexName) },
    { key: 'stockPosition', label: '动态仓位', numeric: true, render: (row) => {
      const v = toNumber(row.stockPosition);
      return v === null ? '--' : `${v}%`;
    }},
    { key: 'backtest', label: '回测', render: (row) => formatBacktest(row.backtest) },
    { key: 'holdings', label: '持仓', render: (row) => formatHoldingsSummary(row.holdings) },
    { key: 'calcStatus', label: '估值状态', render: (row) => <span className="muted">{pickText(row.calcStatus)}</span> },
  ];

  return (
    <SimpleDataTable
      eyebrow="LOF IOPV"
      title="LOF/QDII 估值"
      count={`${sorted.length} 条`}
      columns={columns}
      rows={sorted}
      emptyText="LOF 接口暂无数据"
    />
  );
}