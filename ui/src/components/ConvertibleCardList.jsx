// AI-SUMMARY: 转债套利手机端密集卡片列表，支持多字段组和多场景渲染
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import {
  DenseCardList,
  formatDate,
  formatNumber,
  formatPercent,
  formatRatioPercent,
  pickText,
  signedClass,
  toNumber,
} from './cardListHelpers.jsx';

function getConvertibleStatus(row) {
  const today = new Date().toISOString().slice(0, 10);
  if (row.isUnlisted || (row.delistDate && row.delistDate <= today)) return '已退市';
  if (row.isBeforeConvertStart || (row.convertStartDate && row.convertStartDate > today)) return '未到转股期';
  if (row.forceRedeemStatus && String(row.forceRedeemStatus).includes('强赎')) return '强赎中';
  if (row.maturityDate && row.maturityDate <= today) return '已到期';
  return '正常';
}

function renderMarketValueRatio(row) {
  const remainingSizeYi = toNumber(row.remainingSizeYi);
  const stockMarketValueYi = toNumber(row.stockMarketValueYi);
  if (remainingSizeYi === null || stockMarketValueYi === null || stockMarketValueYi <= 0) return '--';
  return formatRatioPercent(remainingSizeYi / stockMarketValueYi);
}

function renderPureBondPremium(row) {
  const price = toNumber(row.price);
  const pureBond = toNumber(row.pureBondValue);
  if (price === null || pureBond === null || pureBond === 0) return '--';
  return formatPercent(((price - pureBond) / pureBond) * 100);
}

function renderVolatility(row) {
  const value = toNumber(row.volatility250) ?? toNumber(row.volatility60);
  return value === null ? '--' : formatPercent(value * 100);
}

function renderYears(value) {
  const number = toNumber(value);
  return number === null ? '--' : `${number.toFixed(1)}年`;
}

function renderPrimaryHeader(row) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>
          {pickText(row.bondName, row.name)}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--terminal-muted)', fontFamily: 'var(--terminal-mono)', marginTop: '2px' }}>
          {pickText(row.code, row.bondCode)} · {pickText(row.stockName, row.aName, row.stockCode)}
        </div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div className="mono" style={{ fontSize: '16px', fontWeight: 700 }}>{formatNumber(row.price)}</div>
        <div className={`mono ${signedClass(row.changePercent)}`} style={{ fontSize: '12px', marginTop: '2px' }}>
          {formatPercent(row.changePercent)}
        </div>
      </div>
    </div>
  );
}

function renderRightsHeader(row) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '12px', alignItems: 'flex-start', marginBottom: '8px' }}>
      <div style={{ minWidth: 0 }}>
        <div style={{ fontSize: '15px', fontWeight: 700, lineHeight: 1.3 }}>
          {pickText(row.stockName)}
        </div>
        <div style={{ fontSize: '12px', color: 'var(--terminal-muted)', fontFamily: 'var(--terminal-mono)', marginTop: '2px' }}>
          {pickText(row.stockCode)} · {pickText(row.progressName)}
        </div>
      </div>
      <div style={{ textAlign: 'right', flexShrink: 0 }}>
        <div className={`mono ${signedClass(row.expectedReturnRate)}`} style={{ fontSize: '16px', fontWeight: 700 }}>
          {formatPercent(row.expectedReturnRate)}
        </div>
        <div style={{ fontSize: '11px', color: 'var(--terminal-faint)', marginTop: '2px' }}>
          预期收益率
        </div>
      </div>
    </div>
  );
}

const CONVERTIBLE_SEARCH_FIELDS = ['bondName', 'name', 'code', 'bondCode', 'stockName', 'aName', 'stockCode'];
const RIGHTS_SEARCH_FIELDS = ['stockCode', 'stockName', 'progressName', 'recordDate'];

const CONVERTIBLE_META_FIELDS = [
  { key: 'premiumRate', label: '转股溢价率', type: 'signedPercent' },
  { key: 'convertValue', label: '转股价值', type: 'number' },
  { key: 'doubleLow', label: '双低', type: 'number' },
];

const SMALL_META_FIELDS = [
  { key: 'smallRedemptionYield', label: '刚兑收益率', type: 'signedPercent' },
  { key: 'smallRedemptionAnnualizedYield', label: '刚兑年化', type: 'signedPercent' },
  { key: 'smallRedemptionTotalAnnualizedYield', label: '总年化', type: 'signedPercent' },
];

const RIGHTS_META_FIELDS = [
  { key: 'issueRatio', label: '发行比例', type: 'ratioPercent' },
  { key: 'requiredFunds', label: '所需资金', type: 'number' },
  { key: 'optionValue', label: '期权价值', type: 'number' },
];

const HOME_FIELD_GROUPS = [
  {
    fields: [
      { key: 'code', label: '转债代码' },
      { key: 'stockCode', label: '正股代码' },
      { key: 'stockPrice', label: '正股价', type: 'number' },
      { key: 'stockAvgTurnoverAmount20Yi', label: '正股成交(万)', format: (value) => {
        const number = toNumber(value);
        return number === null ? '--' : formatNumber(number * 10000);
      } },
      { key: 'convertPrice', label: '转股价', type: 'number' },
      { key: 'convertValue', label: '转股价值', type: 'number' },
      { key: 'premiumRate', label: '溢价率', type: 'signedPercent' },
      { key: 'remainingSizeYi', label: '规模', type: 'number', suffix: '亿' },
      { key: 'stockMarketValueYi', label: '正股流通市值', type: 'number', suffix: '亿' },
      { key: 'bondToStockMarketValueRatio', label: '转债市值比', format: (_, row) => {
        const ratio = toNumber(row.bondToStockMarketValueRatio);
        return ratio === null ? renderMarketValueRatio(row) : formatRatioPercent(ratio);
      } },
      { key: 'discountAtrRatio', label: '折价ATR', format: (value) => {
        const number = toNumber(value);
        return number === null ? '--' : formatRatioPercent(number);
      } },
      { key: 'market', label: '市场', format: (value, row) => pickText(value, row.marketType, row.boardType) },
      { key: 'doubleLow', label: '双低', type: 'number' },
      { key: 'pureBondValue', label: '纯债价值', type: 'number' },
      { key: 'pureBondPremium', label: '纯债溢价', format: (_, row) => renderPureBondPremium(row) },
      { key: 'theoreticalPrice', label: '理论价值', type: 'number' },
      { key: 'theoreticalPremiumRate', label: '理论溢价', type: 'signedPercent' },
      { key: 'theoreticalOptionValue', label: '理论期权', format: (value, row) => formatNumber(value ?? row.optionValue) },
      { key: 'optionValue', label: '隐含期权', type: 'number' },
      { key: 'volatility250', label: '波动率', format: (_, row) => renderVolatility(row) },
      { key: 'remainingYears', label: '剩余期限', format: (value) => renderYears(value) },
      { key: 'forceRedeemStatus', label: '状态', format: (value, row) => `${pickText(value, '无')}\n${getConvertibleStatus(row)}` },
    ],
  },
];

const DISCOUNT_FIELD_GROUPS = [
  {
    fields: [
      { key: 'code', label: '转债代码' },
      { key: 'stockCode', label: '正股代码' },
      { key: 'stockPrice', label: '正股价', type: 'number' },
      { key: 'convertValue', label: '转股价值', type: 'number' },
      { key: 'premiumRate', label: '转股溢价率', type: 'signedPercent' },
      { key: 'remainingSizeYi', label: '剩余规模', type: 'number', suffix: '亿' },
      { key: 'pureBondValue', label: '纯债价值', type: 'number' },
      { key: 'theoreticalPrice', label: '理论价值', type: 'number' },
      { key: 'theoreticalPremiumRate', label: '理论套利空间', type: 'signedPercent' },
      { key: 'maturityDate', label: '到期日', type: 'date' },
      { key: 'rating', label: '评级' },
      { key: 'forceRedeemStatus', label: '强赎状态' },
      { key: 'convertStatus', label: '转股状态', format: (_, row) => getConvertibleStatus(row) },
    ],
  },
];

const SMALL_FIELD_GROUPS = [
  {
    fields: [
      { key: 'code', label: '转债代码' },
      { key: 'stockCode', label: '正股代码' },
      { key: 'stockPrice', label: '正股价', type: 'number' },
      { key: 'holderCount', label: '持有人数', type: 'number' },
      { key: 'remainingSizeYi', label: '剩余规模', type: 'number', suffix: '亿' },
      { key: 'smallRedemptionAmount', label: '刚兑金额', type: 'number' },
      { key: 'smallRedemptionYield', label: '刚兑收益率', type: 'signedPercent' },
      { key: 'smallRedemptionExpectedYears', label: '预期耗时', format: (value, row) => {
        const base = renderYears(value);
        const remain = renderYears(row.remainingYears);
        return base === '--' && remain === '--' ? '--' : `${base}\n剩余期限 ${remain}`;
      } },
      { key: 'smallRedemptionAnnualizedYield', label: '刚兑年化', type: 'signedPercent' },
      { key: 'smallRedemptionTotalAmount', label: '刚兑总额', type: 'number' },
      { key: 'stockNetDebtExposureYi', label: '负债敞口', format: (value, row) => {
        const exposure = formatNumber(value, '亿');
        const debt = formatNumber(row.stockInterestBearingDebtYi, '亿');
        const cash = formatNumber(row.stockBroadCashYi, '亿');
        return `${exposure}\n有息负债 ${debt}\n广义现金 ${cash}`;
      } },
      { key: 'stockNetAssetsYi', label: '净资产', type: 'number', suffix: '亿' },
      { key: 'smallRedemptionOptionValue', label: '期权价值', type: 'number' },
      { key: 'smallRedemptionOptionAnnualizedYield', label: '期权年化', type: 'signedPercent' },
      { key: 'smallRedemptionTotalAnnualizedYield', label: '总年化收益率', type: 'signedPercent' },
    ],
  },
];

const RIGHTS_FIELD_GROUPS = [
  {
    fields: [
      { key: 'stockCode', label: '正股代码' },
      { key: 'progressName', label: '方案进展' },
      { key: 'progressDate', label: '进展公告日', type: 'date' },
      { key: 'issueScaleYi', label: '发行规模', type: 'number', suffix: '亿' },
      { key: 'stockMarketValueYi', label: '总市值', type: 'number', suffix: '亿' },
      { key: 'issueRatio', label: '发行比例', type: 'ratioPercent' },
      { key: 'rawRequiredShares', label: '原始所需股数', type: 'number' },
      { key: 'placementShares', label: '配售股数', type: 'number' },
      { key: 'marginRequiredShares', label: '两融所需股数', type: 'number' },
      { key: 'convertPrice', label: '转股价', type: 'number' },
      { key: 'volatility250', label: '波动率', format: (_, row) => renderVolatility(row) },
      { key: 'optionUnitValue', label: '单位期权价值', format: (value) => {
        const number = toNumber(value);
        return number === null ? '--' : number.toFixed(4);
      } },
      { key: 'optionValue', label: '期权价值', type: 'number' },
      { key: 'requiredFunds', label: '所需资金', type: 'number' },
      { key: 'recordDate', label: '股权登记日', type: 'date' },
      { key: 'expectedReturnRate', label: '预期收益率', type: 'signedPercent' },
      { key: 'marginReturnRate', label: '两融收益率', type: 'signedPercent' },
      { key: 'expectedPeelReturnRate', label: '预期收益率去皮', type: 'signedPercent' },
      { key: 'marginPeelReturnRate', label: '两融收益率去皮', type: 'signedPercent' },
    ],
  },
];

const FIELD_GROUPS_BY_VARIANT = {
  home: HOME_FIELD_GROUPS,
  discount: DISCOUNT_FIELD_GROUPS,
  theoretical: DISCOUNT_FIELD_GROUPS,
  small_redemption: SMALL_FIELD_GROUPS,
  rights_issue: RIGHTS_FIELD_GROUPS,
};

const META_FIELDS_BY_VARIANT = {
  home: CONVERTIBLE_META_FIELDS,
  discount: CONVERTIBLE_META_FIELDS,
  theoretical: CONVERTIBLE_META_FIELDS,
  small_redemption: SMALL_META_FIELDS,
  rights_issue: RIGHTS_META_FIELDS,
};

const TITLES = {
  home: { eyebrow: 'CONVERTIBLE ARB', title: '转债套利' },
  discount: { eyebrow: 'DISCOUNT ARB', title: '折价套利' },
  theoretical: { eyebrow: 'THEORETICAL DISCOUNT', title: '理论折价套利' },
  small_redemption: { eyebrow: 'SMALL REDEMPTION', title: '小额刚兑' },
  rights_issue: { eyebrow: 'CB RIGHTS ISSUE', title: '抢权配售' },
};

export default function ConvertibleCardList({
  rows = [],
  searchQuery = '',
  variant = 'home',
  eyebrow,
  title,
  fieldGroups,
  searchFields,
  metaFields,
}) {
  const mode = FIELD_GROUPS_BY_VARIANT[variant] ? variant : 'home';
  const headerRenderer = mode === 'rights_issue' ? renderRightsHeader : renderPrimaryHeader;
  const labels = TITLES[mode];

  return (
    <DenseCardList
      title={title || labels.title}
      eyebrow={eyebrow || labels.eyebrow}
      rows={rows}
      searchQuery={searchQuery}
      searchFields={searchFields || (mode === 'rights_issue' ? RIGHTS_SEARCH_FIELDS : CONVERTIBLE_SEARCH_FIELDS)}
      getKey={(row, index) => row.code || row.bondCode || row.stockCode || index}
      renderHeader={headerRenderer}
      metaFields={metaFields || META_FIELDS_BY_VARIANT[mode]}
      fieldGroups={fieldGroups || FIELD_GROUPS_BY_VARIANT[mode]}
      emptyText="暂无数据"
    />
  );
}
