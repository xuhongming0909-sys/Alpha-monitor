// AI-SUMMARY: AB 溢价密集全字段行表列表
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import {
  DenseCard,
  EmptyState,
  FieldPair,
  SectionPanel,
  formatNumber,
  formatPercent,
  pickText,
  rowMatchesQuery,
  signedClass,
  toNumber,
} from './cardHelpers.jsx';

function AbCard({ row }) {
  const aPrice = toNumber(row.aPrice);
  const bPriceCny = toNumber(row.bPriceCny);
  const gap = aPrice !== null && bPriceCny !== null ? aPrice - bPriceCny : null;
  const range = row.historyStartDate || row.historyEndDate
    ? `${row.historyStartDate?.slice(0, 10) || '--'} ~ ${row.historyEndDate?.slice(0, 10) || '--'}`
    : '--';

  return (
    <DenseCard
      title={pickText(row.aName, row.name)}
      code={`A:${pickText(row.aCode, row.code)} / B:${pickText(row.bCode)}`}
      subtitle={pickText(row.bName)}
      metricLabel="溢价率"
      metricValue={formatPercent(row.premium)}
      metricClassName={signedClass(row.premium)}
    >
      <FieldPair label="A股价格" value={formatNumber(row.aPrice)} className="mono" />
      <FieldPair label="B股价格" value={formatNumber(row.bPrice)} className="mono" />
      <FieldPair label="B股人民币" value={formatNumber(row.bPriceCny)} className="mono" />
      <FieldPair
        label="价差"
        value={gap === null ? '--' : formatNumber(gap)}
        className={`mono ${signedClass(gap)}`}
      />
      <FieldPair label="近三年分位" value={formatNumber(row.percentile)} className="mono" />
      <FieldPair label="样本数" value={formatNumber(row.historyCount)} className="mono" />
      <FieldPair label="样本区间" value={range} className="mono" long />
    </DenseCard>
  );
}

export default function AbCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, ['aName', 'name', 'aCode', 'code', 'bName', 'bCode']));

  return (
    <SectionPanel eyebrow="AB PREMIUM" title="AB 溢价" count={`${filtered.length} 条`}>
      <div className="card-list">
        {filtered.length ? filtered.map((row, index) => (
          <AbCard key={`${row.aCode || row.code || index}`} row={row} />
        )) : <EmptyState text="AB 接口暂无数据" />}
      </div>
    </SectionPanel>
  );
}
