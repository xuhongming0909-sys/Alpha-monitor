// AI-SUMMARY: LOF IOPV 估值表格，统一展示，支持置顶筛选和1拖六字段
// 对应 INDEX.md 9.3 文件摘要索引
import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function formatFee(value) {
  if (value == null) return '--';
  const s = String(value).replace('%', '');
  return toNumber(s) === null ? '--' : s + '%';
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

/** 置顶条件：有限额 + 限额<10万 + IOPV溢价率>1% */
function isPinned(row) {
  const premium = toNumber(row.premiumRate);
  const status = (row.applyStatus || '').toString();
  const isPaused = status.includes('暂停');
  // 溢价>2% + 未暂停申购（有明确限额或开放申购），或折价<-3%
  if (premium !== null && premium > 2 && !isPaused) return true;
  if (premium !== null && premium < -3) return true;
  return false;
}

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) =>
    rowMatchesQuery(row, searchQuery, ['name', 'code', 'fundCompany', 'calcTarget'])
  );
// 默认按溢价率降序；列头点击排序时置顶始终隔离在顶部
  const sorted = [...filtered].sort((a, b) => {
    const pa = toNumber(a.premiumRate) ?? -Infinity;
    const pb = toNumber(b.premiumRate) ?? -Infinity;
    return pb - pa;
  });

  const columns = [
    {
      key: 'code', label: '代码',
      render: (row) => (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
          {isPinned(row) && <span title="置顶：溢价>2% 或 折价<-3%" style={{ color: '#e74c3c', fontSize: '0.75em' }}>📌</span>}
          <span className="mono">{pickText(row.code)}</span>
        </span>
      ),
    },
    { key: 'name', label: '名称', render: (row) => pickText(row.name) },
    { key: 'exchange', label: '市场', render: (row) => {
      const ex = row.exchange;
      if (ex === 'SZ') return <span style={{ color: '#e74c3c', fontWeight: 600 }}>深</span>;
      if (ex === 'SH') return <span style={{ color: '#3498db', fontWeight: 600 }}>沪</span>;
      return <span className="muted">--</span>;
    } },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'iopvStatus', label: '持仓覆盖', render: (row) => row.iopvStatus ? <span className="muted" style={{fontSize:'0.8em'}}>{row.iopvStatus}</span> : '--' },
    { key: 'applyStatus', label: '申购状态', render: (row) => {
      const s = (row.applyStatus || '').toString();
      if (s.startsWith('限额')) return <span style={{ color: '#e67e22', fontWeight: 600 }}>{s}</span>;
      if (s === '暂停申购') return <span style={{ color: '#e74c3c' }}>{s}</span>;
      if (s === '开放申购') return <span style={{ color: '#27ae60' }}>{s}</span>;
      return <span className="muted">{s || '--'}</span>;
    } },
    { key: 'supports1to6', label: '1拖六', render: (row) => {
    if (row.code === '161226') return <span style={{ color: '#f39c12', fontSize: '0.85em' }}>身份证</span>;
    return row.supports1to6 ? <span style={{ color: '#27ae60', fontWeight: 600 }}>✓</span> : <span style={{ color: '#bdc3c7' }}>✗</span>;
  } },
    { key: 'nav', label: 'T-2净值', numeric: true, render: (row) => formatNumber(row.nav) },
    { key: 'navDate', label: '净值日期', render: (row) => formatDate(row.navDate) },
    { key: 'price', label: '现价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'iopv', label: '实时估值', numeric: true, render: (row) => formatNumber(row.iopv) },
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

  const pinnedCount = filtered.filter(isPinned).length;

  return (
    <SimpleDataTable
      eyebrow="LOF IOPV"
      title={`QDII LOF 估值${pinnedCount > 0 ? ` · 📌${pinnedCount}` : ''}`}
      count={`${sorted.length} 条`}
      columns={columns}
      rows={sorted}
      isPinned={isPinned}
      emptyText="LOF 接口暂无数据"
    />
  );
}