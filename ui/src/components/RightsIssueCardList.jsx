// AI-SUMMARY: 抢权配售密集卡片列表与市场/阶段切换
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import {
  DenseCard,
  EmptyState,
  FieldPair,
  SectionPanel,
  formatDate,
  formatNumber,
  formatPercent,
  pickText,
  signedClass,
  toNumber,
} from './cardHelpers.jsx';

function riMatchesQuery(row, query) {
  if (!query) return true;
  const lower = query.toLowerCase();
  return ['stockCode', 'stockName', 'progressName'].some((field) => String(row?.[field] || '').toLowerCase().includes(lower));
}

function RightsIssueCard({ row }) {
  const issueRatio = toNumber(row.issueRatio);
  const volatility = toNumber(row.volatility250 ?? row.volatility60);
  return (
    <DenseCard
      title={pickText(row.stockName)}
      code={pickText(row.stockCode)}
      subtitle={pickText(row.progressName)}
      metricLabel="两融去皮收益率"
      metricValue={formatPercent(row.marginPeelReturnRate)}
      metricClassName={signedClass(row.marginPeelReturnRate)}
    >
      <FieldPair label="进展公告日" value={formatDate(row.progressDate)} className="mono" />
      <FieldPair label="股权登记日" value={formatDate(row.recordDate)} className="mono" />
      <FieldPair label="发行规模" value={formatNumber(row.issueScaleYi, '亿')} className="mono" />
      <FieldPair label="流通市值" value={formatNumber(row.stockMarketValueYi, '亿')} className="mono" />
      <FieldPair label="发行比例" value={issueRatio === null ? '--' : formatPercent(issueRatio * 100)} className="mono" />
      <FieldPair label="原始所需股数" value={formatNumber(row.rawRequiredShares)} className="mono" />
      <FieldPair label="配售股数" value={formatNumber(row.placementShares)} className="mono" />
      <FieldPair label="转股价" value={formatNumber(row.convertPrice)} className="mono" />
      <FieldPair label="波动率" value={volatility === null ? '--' : formatPercent(volatility * 100)} className="mono" />
      <FieldPair label="单位期权价值" value={toNumber(row.optionUnitValue) !== null ? Number(row.optionUnitValue).toFixed(4) : '--'} className="mono" />
      <FieldPair label="期权价值" value={formatNumber(row.optionValue)} className="mono" />
      <FieldPair label="所需资金" value={formatNumber(row.requiredFunds)} className="mono" />
      <FieldPair label="两融所需股数" value={formatNumber(row.marginRequiredShares)} className="mono" />
      <FieldPair label="两融所需资金" value={formatNumber(row.marginRequiredFunds)} className="mono" />
      <FieldPair label="预期收益率" value={formatPercent(row.expectedReturnRate)} className={`mono ${signedClass(row.expectedReturnRate)}`} />
      <FieldPair label="两融收益率" value={formatPercent(row.marginReturnRate)} className={`mono ${signedClass(row.marginReturnRate)}`} />
      <FieldPair label="预期去皮" value={formatPercent(row.expectedPeelReturnRate)} className={`mono ${signedClass(row.expectedPeelReturnRate)}`} />
      <FieldPair label="两融去皮" value={formatPercent(row.marginPeelReturnRate)} className={`mono ${signedClass(row.marginPeelReturnRate)}`} />
    </DenseCard>
  );
}

export default function RightsIssueCardList({ rows = [], searchQuery = '' }) {
  const [riMarket, setRiMarket] = React.useState('sh');
  const [stage, setStage] = React.useState('apply');
  const shRows = rows.filter((row) => String(row.market || '').toLowerCase() === 'sh' || String(row.stockCode || '').startsWith('6'));
  const szRows = rows.filter((row) => String(row.market || '').toLowerCase() === 'sz' || String(row.stockCode || '').match(/^[03]/));
  const marketRows = riMarket === 'sh' ? shRows : szRows;
  const riApply = marketRows.filter((row) => row.inApplyStage === true);
  const riAmbush = marketRows.filter((row) => {
    if (row.inApplyStage === true) return false;
    const progress = String(row.progressName || '');
    return (progress.includes('上市委通过') || progress.includes('同意注册') || progress.includes('注册生效')) && toNumber(row.expectedReturnRate) > 6;
  });
  const riWait = marketRows.filter((row) => {
    if (row.inApplyStage === true) return false;
    const progress = String(row.progressName || '');
    return !((progress.includes('上市委通过') || progress.includes('同意注册') || progress.includes('注册生效')) && toNumber(row.expectedReturnRate) > 6);
  });
  const sourceRows = stage === 'apply' ? riApply : stage === 'ambush' ? riAmbush : riWait;
  const filtered = sourceRows.filter((row) => riMatchesQuery(row, searchQuery));

  return (
    <SectionPanel eyebrow="CB RIGHTS ISSUE" title="抢权配售" count={`${filtered.length} 条`}>
      <div className="subtab-row">
        {[{ key: 'sh', label: `沪市 (${shRows.length})` }, { key: 'sz', label: `深市 (${szRows.length})` }].map((tab) => (
          <button key={tab.key} type="button" className={`tab-button ${riMarket === tab.key ? 'active' : ''}`} onClick={() => setRiMarket(tab.key)}>
            {tab.label}
          </button>
        ))}
      </div>
      <div className="subtab-row">
        {[{ key: 'apply', label: `申购阶段 (${riApply.length})` }, { key: 'ambush', label: `埋伏阶段 (${riAmbush.length})` }, { key: 'wait', label: `等待阶段 (${riWait.length})` }].map((tab) => (
          <button key={tab.key} type="button" className={`tab-button ${stage === tab.key ? 'active' : ''}`} onClick={() => setStage(tab.key)}>
            {tab.label}
          </button>
        ))}
      </div>
      <div className="card-list">
        {filtered.length ? filtered.map((row, index) => (
          <RightsIssueCard key={`${row.stockCode || index}`} row={row} />
        )) : <EmptyState text="暂无抢权配售数据" />}
      </div>
    </SectionPanel>
  );
}
