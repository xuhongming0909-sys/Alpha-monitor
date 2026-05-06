// AI-SUMMARY: 打新申购密集卡片列表
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import {
  DenseCard,
  EmptyState,
  FieldPair,
  SectionPanel,
  formatDate,
  formatNumber,
  pickText,
  rowMatchesQuery,
} from './cardHelpers.jsx';

function SubscriptionCard({ row }) {
  return (
    <DenseCard
      title={pickText(row.name, row.stockName, row.bondName)}
      code={pickText(row.code, row.stockCode, row.bondCode)}
      subtitle={pickText(row.type)}
    >
      <FieldPair label="申购日" value={formatDate(row.subscribeDate)} className="mono" />
      <FieldPair label="缴款日" value={formatDate(row.paymentDate)} className="mono" />
      <FieldPair label="上市日" value={formatDate(row.listingDate)} className="mono" />
      <FieldPair label="申购上限" value={formatNumber(row.subscribeLimit)} className="mono" />
      <FieldPair label="发行价" value={formatNumber(row.issuePrice)} className="mono" />
      <FieldPair label="转股价" value={formatNumber(row.convertPrice)} className="mono" />
    </DenseCard>
  );
}

function flattenRows(data) {
  const ipoRows = Array.isArray(data?.ipo?.data) ? data.ipo.data : [];
  const bondRows = Array.isArray(data?.bonds?.data) ? data.bonds.data : [];
  return [...ipoRows, ...bondRows];
}

export default function SubscriptionCardList({ rows, data, searchQuery = '' }) {
  const sourceRows = Array.isArray(rows) ? rows : flattenRows(data);
  const filtered = sourceRows.filter((row) => rowMatchesQuery(row, searchQuery, ['name', 'stockName', 'bondName', 'code', 'stockCode', 'bondCode']));

  return (
    <SectionPanel eyebrow="SUBSCRIPTIONS" title="打新/申购" count={`${filtered.length} 条`}>
      <div className="card-list">
        {filtered.length ? filtered.map((row, index) => (
          <SubscriptionCard key={`${row.code || row.stockCode || row.bondCode || index}`} row={row} />
        )) : <EmptyState text="打新接口暂无数据" />}
      </div>
    </SectionPanel>
  );
}
