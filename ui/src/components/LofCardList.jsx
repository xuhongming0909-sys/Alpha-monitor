// AI-SUMMARY: LOF IOPV 估值表格，按 R² 精度分页展示，支持展开查看持仓
// 对应 INDEX.md §9.3 文件摘要索引
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

export default function LofCardList({ rows = [], searchQuery = '' }) {
  const filtered = rows.filter((row) =>
    rowMatchesQuery(row, searchQuery, ['name', 'code', 'fundCompany', 'calcTarget'])
  );

  const sorted = [...filtered].sort(
    (a, b) => Math.abs(toNumber(b.premiumRate) ?? 0) - Math.abs(toNumber(a.premiumRate) ?? 0)
  );

  const columns = [
    { key: 'name', label: '基金名称', render: (row) => (
      <div>
        <div className="cell-primary">{row.name || '--'}</div>
        <div className="cell-secondary">{row.code}</div>
      </div>
    )},
    { key: 'premiumRate', label: '溢价率', numeric: true, className: (row) => signedClass(row.premiumRate), render: (row) => formatPercent(row.premiumRate) },
    { key: 'iopv', label: 'IOPV', numeric: true, render: (row) => formatNumber(row.iopv, 3) },
    { key: 'price', label: '现价', numeric: true, render: (row) => formatNumber(row.price, 3) },
    { key: 'nav', label: 'NAV', numeric: true, render: (row) => formatNumber(row.nav, 4) },
    { key: 'applyFee', label: '申购费', render: (row) => formatFee(row.applyFee) },
    { key: 'dailyLimit', label: '日限', render: (row) => formatShare(row.dailyLimit) },
    { key: 'stockPosition', label: '仓位', render: (row) => formatStockPosition(row) },
    { key: 'r2', label: 'R²', numeric: true, render: (row) => row.r2 != null ? row.r2.toFixed(3) : '--' },
    { key: 'maxErr', label: 'MaxErr', numeric: true, render: (row) => row.maxErr != null ? `${row.maxErr.toFixed(2)}%` : '--' },
  ];

  const accurate = sorted.filter((r) => toNumber(r.r2) >= 0.8);
  const inaccurate = sorted.filter((r) => toNumber(r.r2) < 0.8);

  return <LofSubTabs accurate={accurate} inaccurate={inaccurate} columns={columns} />;
}

function LofSubTabs({ accurate, inaccurate, columns }) {
  const [subTab, setSubTab] = React.useState('accurate');
  const [expandedCode, setExpandedCode] = React.useState(null);
  const activeRows = subTab === 'accurate' ? accurate : inaccurate;

  const toggleExpand = (code) => {
    setExpandedCode((prev) => (prev === code ? null : code));
  };

  const switchTab = (tab) => {
    setSubTab(tab);
    setExpandedCode(null);
  };

  const renderCell = (col, row, idx) => {
    const raw = typeof col.render === 'function' ? col.render(row, idx) : row?.[col.key];
    const cls = [
      col.numeric ? 'num' : '',
      typeof col.className === 'function' ? col.className(row, idx) : (col.className || ''),
    ].filter(Boolean).join(' ');
    return <td key={col.key || col.label} className={cls}>{raw ?? '--'}</td>;
  };

  return (
    <>
      <div className="subtab-row">
        <button className={`tab-button${subTab === 'accurate' ? ' active' : ''}`} onClick={() => switchTab('accurate')}>准确 ({accurate.length})</button>
        <button className={`tab-button${subTab === 'inaccurate' ? ' active' : ''}`} onClick={() => switchTab('inaccurate')}>不准确 ({inaccurate.length})</button>
      </div>
      <section className="terminal-panel main-table-panel">
        <div className="panel-head compact-head">
          <div>
            <p className="eyebrow">LOF IOPV</p>
            <h2>QDII LOF 估值</h2>
          </div>
          <span className="panel-count">{activeRows.length} 条</span>
        </div>
        <div className="dense-table-wrap table-scroll">
          <table className="dense-table wide-table lof-expandable-table">
            <thead>
              <tr>
                <th className="lof-expand-col"></th>
                {columns.map((col) => (
                  <th key={col.key || col.label} className={col.numeric ? 'num' : ''}>
                    {col.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {activeRows.length === 0 ? (
                <tr><td colSpan={columns.length + 1} className="empty-cell">LOF 接口暂无数据</td></tr>
              ) : (
                activeRows.map((row, idx) => {
                  const code = row.code;
                  const isExpanded = expandedCode === code;
                  const holdings = row.holdings || [];
                  return (
                    <React.Fragment key={code || idx}>
                      <tr
                        className={`lof-data-row${isExpanded ? ' expanded' : ''}`}
                        onClick={() => toggleExpand(code)}
                        title="点击展开持仓"
                      >
                        <td className="lof-expand-col">
                          <span className={`lof-expand-icon${isExpanded ? ' open' : ''}`}>&#9654;</span>
                        </td>
                        {columns.map((col) => renderCell(col, row, idx))}
                      </tr>
                      {isExpanded && (
                        <tr className="lof-holdings-row">
                          <td colSpan={columns.length + 1}>
                            <div className="lof-holdings-panel">
                              <div className="lof-holdings-title">
                                持仓明细{holdings.length > 0 ? ` (${holdings.length}只)` : ''}
                              </div>
                              {holdings.length === 0 ? (
                                <div className="lof-holdings-empty">暂无持仓数据</div>
                              ) : (
                                <table className="lof-holdings-inner">
                                  <thead>
                                    <tr>
                                      <th>#</th>
                                      <th>股票代码</th>
                                      <th>股票名称</th>
                                      <th className="num">占净值比例</th>
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
    </>
  );
}