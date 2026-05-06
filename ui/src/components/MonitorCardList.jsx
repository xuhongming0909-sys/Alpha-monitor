// AI-SUMMARY: 自定义监控密集行表列表与三表明细
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import {
  DenseCard,
  EmptyState,
  FieldPair,
  SectionPanel,
  bestYieldValue,
  formatNumber,
  formatPercent,
  pickText,
  rowMatchesQuery,
  signedClass,
} from './cardHelpers.jsx';

function InfoTable({ title, rows }) {
  return (
    <div className="mini-table-block">
      <div className="mini-table-title">{title}</div>
      <div className="mini-table">
        {rows.map((row) => (
          <div key={row.label} className="mini-table-row">
            <span className="mini-table-label">{row.label}</span>
            <span className={`mini-table-value ${row.className || ''}`.trim()}>{row.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MonitorCard({ row, onEdit, onDelete, saving }) {
  const bestYield = bestYieldValue(row);
  const subtitle = row.name && row.name !== '自定义' ? row.name : pickText(row.note);

  return (
    <DenseCard
      title="自定义"
      code={`${pickText(row.acquirerName)} → ${pickText(row.targetName)}`}
      subtitle={subtitle}
      metricLabel="最优收益率"
      metricValue={bestYield === -Infinity ? '--' : `${bestYield.toFixed(3)}%`}
      metricClassName={signedClass(bestYield === -Infinity ? null : bestYield)}
      footer={(
        <div className="card-footer-actions">
          <button type="button" className="tab-button" onClick={() => onEdit(row)} disabled={saving}>编辑</button>
          <button type="button" className="tab-button" onClick={() => onDelete(row.id)} disabled={saving}>删除</button>
        </div>
      )}
    >
      <FieldPair label="目标现价" value={formatNumber(row.targetPrice)} className="mono" />
      <FieldPair label="换股收益率" value={formatPercent(row.stockYieldRate)} className={`mono ${signedClass(row.stockYieldRate)}`} />
      <FieldPair label="现金收益率" value={formatPercent(row.cashYieldRate)} className={`mono ${signedClass(row.cashYieldRate)}`} />
      <FieldPair label="最优收益率" value={bestYield === -Infinity ? '--' : `${bestYield.toFixed(3)}%`} className={`mono ${signedClass(bestYield === -Infinity ? null : bestYield)}`} />
      <FieldPair label="备注" value={pickText(row.note)} long />
      <div className="row-field row-field-long">
        <InfoTable
          title="收购方表"
          rows={[
            { label: '名称', value: pickText(row.acquirerName) },
            { label: '代码', value: pickText(row.acquirerCode), className: 'mono' },
            { label: '市场', value: pickText(row.acquirerMarket) },
            { label: '币种', value: pickText(row.acquirerCurrency) },
            { label: '现价', value: formatNumber(row.acquirerPrice), className: 'mono' },
          ]}
        />
      </div>
      <div className="row-field row-field-long">
        <InfoTable
          title="目标方表"
          rows={[
            { label: '名称', value: pickText(row.targetName) },
            { label: '代码', value: pickText(row.targetCode), className: 'mono' },
            { label: '市场', value: pickText(row.targetMarket) },
            { label: '币种', value: pickText(row.targetCurrency) },
            { label: '现价', value: formatNumber(row.targetPrice), className: 'mono' },
          ]}
        />
      </div>
      <div className="row-field row-field-long">
        <InfoTable
          title="收益表"
          rows={[
            { label: '换股比例', value: formatNumber(row.stockRatio), className: 'mono' },
            { label: '安全系数', value: formatNumber(row.safetyFactor), className: 'mono' },
            { label: '现金对价', value: formatNumber(row.cashDistributionCny), className: 'mono' },
            { label: '股票腿理论对价', value: formatNumber(row.stockPayout), className: 'mono' },
            { label: '股票腿价差', value: formatNumber(row.stockSpread), className: `mono ${signedClass(row.stockSpread)}` },
            { label: '换股收益率', value: formatPercent(row.stockYieldRate), className: `mono ${signedClass(row.stockYieldRate)}` },
            { label: '现金选择权', value: formatNumber(row.cashPayout), className: 'mono' },
            { label: '现金腿价差', value: formatNumber(row.cashSpread), className: `mono ${signedClass(row.cashSpread)}` },
            { label: '现金收益率', value: formatPercent(row.cashYieldRate), className: `mono ${signedClass(row.cashYieldRate)}` },
          ]}
        />
      </div>
    </DenseCard>
  );
}

export default function MonitorCardList({ rows = [], searchQuery = '', onEdit = () => {}, onDelete = () => {}, saving = false }) {
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, ['name', 'acquirerName', 'targetName', 'acquirerCode', 'targetCode']));

  return (
    <SectionPanel eyebrow="CUSTOM MONITOR" title="自定义监控" count={`${filtered.length} 条`}>
      <div className="card-list">
        {filtered.length ? filtered.map((row, index) => (
          <MonitorCard
            key={`${row.id || index}`}
            row={row}
            onEdit={onEdit}
            onDelete={onDelete}
            saving={saving}
          />
        )) : <EmptyState text="监控接口暂无数据" />}
      </div>
    </SectionPanel>
  );
}
