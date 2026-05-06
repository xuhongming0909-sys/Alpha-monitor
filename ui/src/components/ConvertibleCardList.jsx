// AI-SUMMARY: 转债套利简洁模块表格，尽量还原旧网页端的干净表格风格
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';
import SimpleDataTable from './SimpleDataTable.jsx';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function formatRatioPercent(value) {
  const number = toNumber(value);
  return number === null ? '--' : `${(number * 100).toFixed(2)}%`;
}

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

function renderVolatility(row) {
  const value = toNumber(row.volatility250) ?? toNumber(row.volatility60);
  return value === null ? '--' : formatPercent(value * 100);
}

function renderPureBondPremium(row) {
  const price = toNumber(row.price);
  const pureBond = toNumber(row.pureBondValue);
  if (price === null || pureBond === null || pureBond === 0) return '--';
  return formatPercent(((price - pureBond) / pureBond) * 100);
}

const SEARCH_FIELDS = ['bondName', 'name', 'code', 'bondCode', 'stockName', 'aName', 'stockCode'];

function homeColumns() {
  return [
    { key: 'bondName', label: '转债', render: (row) => pickText(row.bondName, row.name) },
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code, row.bondCode)}</span> },
    { key: 'price', label: '转债价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'changePercent', label: '涨跌', numeric: true, className: (row) => signedClass(row.changePercent), render: (row) => formatPercent(row.changePercent) },
    { key: 'stockName', label: '正股', render: (row) => pickText(row.stockName, row.aName) },
    { key: 'stockPrice', label: '正股价', numeric: true, render: (row) => formatNumber(row.stockPrice) },
    { key: 'convertPrice', label: '转股价', numeric: true, render: (row) => formatNumber(row.convertPrice) },
    { key: 'convertValue', label: '转股价值', numeric: true, render: (row) => formatNumber(row.convertValue) },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'doubleLow', label: '双低', numeric: true, render: (row) => formatNumber(row.doubleLow) },
    { key: 'remainingSizeYi', label: '规模', numeric: true, render: (row) => formatNumber(row.remainingSizeYi, '亿') },
    { key: 'bondToStockMarketValueRatio', label: '转债市值比', numeric: true, render: (row) => {
      const ratio = toNumber(row.bondToStockMarketValueRatio);
      return ratio === null ? renderMarketValueRatio(row) : formatRatioPercent(ratio);
    } },
    { key: 'pureBondPremium', label: '纯债溢价', numeric: true, render: (row) => renderPureBondPremium(row) },
    { key: 'theoreticalPremiumRate', label: '理论溢价', numeric: true, className: (row) => signedClass(row.theoreticalPremiumRate), render: (row) => formatPercent(row.theoreticalPremiumRate) },
    { key: 'optionValue', label: '隐含期权', numeric: true, render: (row) => formatNumber(row.optionValue) },
    { key: 'volatility250', label: '波动率', numeric: true, render: (row) => renderVolatility(row) },
    { key: 'remainingYears', label: '剩余期限', numeric: true, render: (row) => {
      const value = toNumber(row.remainingYears);
      return value === null ? '--' : `${value.toFixed(1)}年`;
    } },
    { key: 'status', label: '状态', render: (row) => getConvertibleStatus(row) },
  ];
}

function discountColumns() {
  return [
    { key: 'bondName', label: '转债', render: (row) => pickText(row.bondName, row.name) },
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code, row.bondCode)}</span> },
    { key: 'stockName', label: '正股', render: (row) => pickText(row.stockName, row.aName) },
    { key: 'price', label: '转债价', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'stockPrice', label: '正股价', numeric: true, render: (row) => formatNumber(row.stockPrice) },
    { key: 'convertValue', label: '转股价值', numeric: true, render: (row) => formatNumber(row.convertValue) },
    { key: 'premiumRate', label: '转股溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'theoreticalPrice', label: '理论价值', numeric: true, render: (row) => formatNumber(row.theoreticalPrice) },
    { key: 'theoreticalPremiumRate', label: '理论套利空间', numeric: true, className: (row) => signedClass(row.theoreticalPremiumRate), render: (row) => formatPercent(row.theoreticalPremiumRate) },
    { key: 'maturityDate', label: '到期日', render: (row) => formatDate(row.maturityDate) },
    { key: 'rating', label: '评级', render: (row) => pickText(row.rating) },
    { key: 'forceRedeemStatus', label: '强赎状态', render: (row) => pickText(row.forceRedeemStatus) },
  ];
}

function smallColumns() {
  return [
    { key: 'bondName', label: '转债', render: (row) => pickText(row.bondName, row.name) },
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code, row.bondCode)}</span> },
    { key: 'stockName', label: '正股', render: (row) => pickText(row.stockName) },
    { key: 'remainingSizeYi', label: '剩余规模', numeric: true, render: (row) => formatNumber(row.remainingSizeYi, '亿') },
    { key: 'smallRedemptionAnnualizedYield', label: '刚兑年化', numeric: true, className: (row) => signedClass(row.smallRedemptionAnnualizedYield), render: (row) => formatPercent(row.smallRedemptionAnnualizedYield) },
    { key: 'smallRedemptionOptionAnnualizedYield', label: '期权年化', numeric: true, className: (row) => signedClass(row.smallRedemptionOptionAnnualizedYield), render: (row) => formatPercent(row.smallRedemptionOptionAnnualizedYield) },
    { key: 'smallRedemptionTotalAnnualizedYield', label: '总年化收益率', numeric: true, className: (row) => signedClass(row.smallRedemptionTotalAnnualizedYield), render: (row) => formatPercent(row.smallRedemptionTotalAnnualizedYield) },
  ];
}

const CONFIG = {
  home: { eyebrow: 'CONVERTIBLE ARB', title: '转债套利', columns: homeColumns() },
  discount: { eyebrow: 'CB DISCOUNT', title: '折价套利', columns: discountColumns() },
  theoretical: { eyebrow: 'THEORETICAL DISCOUNT', title: '理论折价套利', columns: discountColumns() },
  small_redemption: { eyebrow: 'SMALL REDEMPTION', title: '小额刚兑', columns: smallColumns() },
};

export default function ConvertibleCardList({ rows = [], searchQuery = '', variant = 'home', title, eyebrow }) {
  const mode = CONFIG[variant] ? variant : 'home';
  const filtered = rows.filter((row) => rowMatchesQuery(row, searchQuery, SEARCH_FIELDS));
  return (
    <SimpleDataTable
      eyebrow={eyebrow || CONFIG[mode].eyebrow}
      title={title || CONFIG[mode].title}
      count={`${filtered.length} 条`}
      columns={CONFIG[mode].columns}
      rows={filtered}
      emptyText="暂无数据"
    />
  );
}
