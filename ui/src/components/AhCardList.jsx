// AI-SUMMARY: AH溢价手机端密集全字段行表列表
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import {
  DenseCardList,
  formatDate,
  formatNumber,
  formatPercent,
  pickText,
  signedClass,
  toNumber,
} from './cardListHelpers.jsx';

function renderGap(row) {
  const aPrice = toNumber(row.aPrice);
  const hPriceCny = toNumber(row.hPriceCny);
  if (aPrice === null || hPriceCny === null) return '--';
  const gap = aPrice - hPriceCny;
  return `${gap > 0 ? '+' : ''}${gap.toFixed(2)}`;
}

function renderHeader(row) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>
          {pickText(row.aName, row.name)}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--terminal-muted)', fontFamily: 'var(--terminal-mono)', marginTop: '2px' }}>
          A:{pickText(row.aCode, row.code)} · H:{pickText(row.hCode)} · {pickText(row.hName)}
        </div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div className={`mono ${signedClass(row.premium)}`} style={{ fontSize: '16px', fontWeight: 700 }}>
          {formatPercent(row.premium)}
        </div>
        <div style={{ fontSize: '11px', color: 'var(--terminal-faint)', marginTop: '2px' }}>溢价率</div>
      </div>
    </div>
  );
}

export default function AhCardList({ rows = [], searchQuery = '' }) {
  return (
    <DenseCardList
      title="AH 溢价"
      eyebrow="AH PREMIUM"
      rows={rows}
      searchQuery={searchQuery}
      searchFields={['aName', 'name', 'aCode', 'code', 'hName', 'hCode']}
      getKey={(row, index) => row.aCode || row.code || index}
      renderHeader={renderHeader}
      metaFields={[
        { key: 'aPrice', label: 'A股价格', type: 'number' },
        { key: 'hPriceCny', label: 'H股人民币价', type: 'number' },
        { key: 'percentile', label: '近三年分位', type: 'number' },
      ]}
      fieldGroups={[
        {
          fields: [
            { key: 'aCode', label: 'A股代码' },
            { key: 'hCode', label: 'H股代码' },
            { key: 'hName', label: 'H股名称' },
            { key: 'aPrice', label: 'A股价格', type: 'number' },
            { key: 'hPrice', label: 'H股价格', type: 'number' },
            { key: 'hPriceCny', label: 'H股人民币价', type: 'number' },
            { key: 'gap', label: '价差', format: (_, row) => renderGap(row), tone: (_, row) => signedClass((toNumber(row.aPrice) ?? 0) - (toNumber(row.hPriceCny) ?? 0)) },
            { key: 'premium', label: '溢价率', type: 'signedPercent' },
            { key: 'percentile', label: '近三年分位', type: 'number' },
            { key: 'historyCount', label: '样本数', type: 'number' },
            { key: 'historyRange', label: '样本区间', format: (_, row) => {
              const start = row.historyStartDate ? formatDate(row.historyStartDate) : '--';
              const end = row.historyEndDate ? formatDate(row.historyEndDate) : '--';
              return start === '--' && end === '--' ? '--' : `${start} ~ ${end}`;
            } },
          ],
        },
      ]}
      emptyText="AH 接口暂无数据"
    />
  );
}
