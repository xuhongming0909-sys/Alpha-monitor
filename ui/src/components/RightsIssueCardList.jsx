// AI-SUMMARY: 抢权配售简洁模块表格与市场阶段切换，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, signedClass, toNumber } from './cardHelpers.jsx';

function riMatchesQuery(row, query) {
  if (!query) return true;
  const lower = query.toLowerCase();
  return ['stockCode', 'stockName', 'progressName'].some((field) => String(row?.[field] || '').toLowerCase().includes(lower));
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
  const sourceRows = (stage === 'apply' ? riApply : stage === 'ambush' ? riAmbush : riWait).filter((row) => riMatchesQuery(row, searchQuery));

  const columns = [
    { key: 'stockName', label: '正股名称', render: (row) => pickText(row.stockName) },
    { key: 'stockCode', label: '正股代码', render: (row) => <span className="mono">{pickText(row.stockCode)}</span> },
    { key: 'progressName', label: '方案进展', render: (row) => pickText(row.progressName) },
    { key: 'recordDate', label: '股权登记日', render: (row) => formatDate(row.recordDate) },
    { key: 'issueScaleYi', label: '发行规模', numeric: true, render: (row) => formatNumber(row.issueScaleYi, '亿') },
    { key: 'requiredFunds', label: '所需资金', numeric: true, render: (row) => formatNumber(row.requiredFunds) },
    { key: 'expectedReturnRate', label: '预期收益率', numeric: true, className: (row) => signedClass(row.expectedReturnRate), render: (row) => formatPercent(row.expectedReturnRate) },
    { key: 'marginReturnRate', label: '两融收益率', numeric: true, className: (row) => signedClass(row.marginReturnRate), render: (row) => formatPercent(row.marginReturnRate) },
    { key: 'marginPeelReturnRate', label: '两融去皮收益率', numeric: true, className: (row) => signedClass(row.marginPeelReturnRate), render: (row) => formatPercent(row.marginPeelReturnRate) },
  ];

  return (
    <section className="terminal-panel main-table-panel">
      <div className="panel-head compact-head">
        <div>
          <p className="eyebrow">CB RIGHTS ISSUE</p>
          <h2>抢权配售</h2>
        </div>
        <span className="panel-count">{sourceRows.length} 条</span>
      </div>
      <div className="subtab-row">
        {[{ key: 'sh', label: `沪市 (${shRows.length})` }, { key: 'sz', label: `深市 (${szRows.length})` }].map((tab) => (
          <button key={tab.key} type="button" className={`tab-button ${riMarket === tab.key ? 'active' : ''}`} onClick={() => setRiMarket(tab.key)}>{tab.label}</button>
        ))}
      </div>
      <div className="subtab-row">
        {[{ key: 'apply', label: `申购阶段 (${riApply.length})` }, { key: 'ambush', label: `埋伏阶段 (${riAmbush.length})` }, { key: 'wait', label: `等待阶段 (${riWait.length})` }].map((tab) => (
          <button key={tab.key} type="button" className={`tab-button ${stage === tab.key ? 'active' : ''}`} onClick={() => setStage(tab.key)}>{tab.label}</button>
        ))}
      </div>
      <SimpleDataTable eyebrow="" title="" columns={columns} rows={sourceRows} emptyText="暂无抢权配售数据" tableClassName="rights-table" />
    </section>
  );
}
