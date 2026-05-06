// AI-SUMMARY: LOF套利手机端密集全字段卡片列表
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

function renderHeader(row) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>
          {pickText(row.name, row.fundName)}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--terminal-muted)', fontFamily: 'var(--terminal-mono)', marginTop: '2px' }}>
          {pickText(row.code, row.fundCode)} · {pickText(row.indexName)}
        </div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div className={`mono ${signedClass(row.premiumRate)}`} style={{ fontSize: '16px', fontWeight: 700 }}>
          {formatPercent(row.premiumRate)}
        </div>
        <div style={{ fontSize: '11px', color: 'var(--terminal-faint)', marginTop: '2px' }}>溢价率</div>
      </div>
    </div>
  );
}

export default function LofCardList({ rows = [], searchQuery = '' }) {
  return (
    <DenseCardList
      title="LOF 套利"
      eyebrow="LOF ARBITRAGE"
      rows={rows}
      searchQuery={searchQuery}
      searchFields={['name', 'fundName', 'code', 'fundCode', 'indexName']}
      getKey={(row, index) => row.code || row.fundCode || index}
      renderHeader={renderHeader}
      metaFields={[
        { key: 'price', label: '现价', type: 'number' },
        { key: 'changeRate', label: '涨幅', type: 'signedPercent' },
        { key: 'iopv', label: 'IOPV', type: 'number' },
      ]}
      fieldGroups={[
        {
          fields: [
            { key: 'code', label: '代码' },
            { key: 'price', label: '现价', type: 'number' },
            { key: 'changeRate', label: '涨幅', type: 'signedPercent' },
            { key: 'turnoverWan', label: '成交额(万)', type: 'number' },
            { key: 'nav', label: '净值', type: 'number' },
            { key: 'navDate', label: '净值日期', type: 'date' },
            { key: 'indexName', label: '相关指数' },
            { key: 'applyStatus', label: '申购状态' },
            { key: 'applyFee', label: '申购费', type: 'percent' },
            { key: 'redeemStatus', label: '赎回状态' },
            { key: 'redeemFee', label: '赎回费', type: 'percent' },
            { key: 'custodianFee', label: '托管费', type: 'percent' },
            { key: 'iopv', label: 'IOPV', type: 'number' },
            { key: 'premiumRate', label: '溢价率', type: 'signedPercent' },
          ],
        },
      ]}
      emptyText="LOF 接口暂无数据"
    />
  );
}
