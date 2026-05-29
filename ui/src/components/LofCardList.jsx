// AI-SUMMARY: LOF IOPV 估值表格，按三分类展示（指数型/持仓型/报表型），支持展开查看持仓
// 对应 INDEX.md 9.3 文件摘要索引
import React from 'react';
import { formatDate, formatNumber, formatPercent, pickText, rowMatchesQuery, signedClass, toNumber } from './cardHelpers.jsx';

function formatFee(value) {
  const n = toNumber(value);
  return n === null ? '--' : `${n}%`;
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

function marketLabel(market) {
  const map = { us: '美股', hk: '港股', sh: '沪A', sz: '深A', a: 'A股' };
  return map[market] || market || '--';
}

function FundClassBadge({ fundClass }) {
  if (!fundClass) return <span className="badge badge-muted">--</span>;
  const config = {
    index: { label: '指数型', cls: 'badge-blue' },
    active_api: { label: '持仓型', cls: 'badge-green' },
    active_pdf: { label: '报表型', cls: 'badge-orange' },
  };
  const c = config[fundClass] || { label: fundClass, cls: 'badge-muted' };
  return <span className={`badge ${c.cls}`}>{c.label}</span>;
}

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) =>
    rowMatchesQuery(row, searchQuery, ['name', 'code', 'fundCompany', 'calcTarget'])
  );

  const sorted = [...filtered].sort(
    (a, b) => Math.abs(toNumber(b.premiumRate) ?? 0) - Math.abs(toNumber(a.premiumRate) ?? 0)
  );

  const columns = [
    { key: 'code', label: '代码', render: (row) => <span className="mono">{pickText(row.code)}</span> },
    { key: 'name', label: '名称', render: (row) => pickText(row.name) },
    { key: 'fundClass', label: '分类', render: (row) => <FundClassBadge fundClass={row.fundClass} /> },
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'nav', label: '净值', numeric: true, render: (row) => formatNumber(row.nav) },
    { key: 'iopv', label: 'IOPV', numeric: true, render: (row) => formatNumber(row.iopv) },
    { key: 'price', label: '价格', numeric: true, render: (row) => formatNumber(row.price) },
    { key: 'calcTarget', label: '估值标的', render: (row) => <span className="muted" style={{ fontSize: '0.85em' }}>{pickText(row.calcTarget)}</span> },
    { key: 'backtestMae', label: 'MAE', numeric: true, render: (row) => row.backtestMae != null ? `${row.backtestMae.toFixed(3)}%` : '--' },
    { key: 'stockPosition', label: '仓位', numeric: true, render: (row) => formatStockPosition(row) },
    { key: 'applyStatus', label: '申购', render: (row) => pickText(row.applyStatus) || '--' },
  ];

  return (
    <>
      <LofTable rows={sorted} columns={columns} />
    </>
  );
}

function LofTable({ rows, columns }) {
  const [expandedCode, setExpanded] = React.useState(null);
  const toggle = (code) => setExpanded(prev => prev === code ? null : code);

  return (
    <section className="card card-table">
      <div className="card-header">
        <div className="card-eyebrow">LOF IOPV</div>
        <div className="card-title">QDII LOF 估值</div>
        <div className="card-count">{rows.length} 条</div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th style={{ width: 28 }}></th>
              {columns.map(col => <th key={col.key}>{col.label}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr><td colSpan={columns.length + 1} className="empty">LOF 接口暂无数据</td></tr>
            ) : (
              rows.map((row) => {
                const code = row.code;
                const isOpen = expandedCode === code;
                const holdings = row.holdings || [];
                return (
                  <React.Fragment key={code}>
                    <tr
                      className={`clickable${isOpen ? ' expanded' : ''}`}
                      onClick={() => toggle(code)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td style={{ fontSize: '10px', textAlign: 'center' }}>{isOpen ? '▼' : '▶'}</td>
                      {columns.map(col => (
                        <td
                          key={col.key}
                          className={col.className ? (typeof col.className === 'function' ? col.className(row) : col.className) : (col.numeric ? 'num' : '')}
                        >
                          {col.render ? col.render(row) : pickText(row[col.key])}
                        </td>
                      ))}
                    </tr>
                    {isOpen && (
                      <tr className="sub-row">
                        <td colSpan={columns.length + 1} className="sub-cell">
                          <div className="holdings-panel">
                            <div className="holdings-info">
                              <span>NAV日期: {row.navDate || '--'}</span>
                              <span>规模: {formatShare(row.shareTotal)}</span>
                              <span>基金公司: {row.fundCompany || '--'}</span>
                              <span>托管费: {formatFee(row.custodianFee)}</span>
                              <span>赎回费率: {formatFee(row.redeemFee)}</span>
                            </div>
                            <div className="holdings-info">
                              <span>申购状态: {pickText(row.applyStatus) || '--'} {row.dailyLimit ? `(限额${row.dailyLimit}万)` : ''}</span>
                              <span>汇率: {row.currentFxRate != null ? row.currentFxRate.toFixed(4) : '--'}</span>
                              <span>持仓数: {holdings.length}</span>
                            </div>
                            {holdings.length > 0 && (
                              <table className="holdings-table">
                                <thead>
                                  <tr>
                                    <th>#</th>
                                    <th>代码</th>
                                    <th>名称</th>
                                    <th>占比</th>
                                    <th>市场</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {holdings.map((h, i) => (
                                    <tr key={h.ticker || i}>
                                      <td>{i + 1}</td>
                                      <td>{h.ticker || '--'}</td>
                                      <td>{h.name || '--'}</td>
                                      <td className="num">{h.weight != null ? `${h.weight.toFixed(2)}%` : '--'}</td>
                                      <td>{marketLabel(h.market)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
