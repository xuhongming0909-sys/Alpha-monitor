// AI-SUMMARY: 全设备统一手机端的两行底部标签导航
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

const NAV_TABS = [
  { key: 'overview', label: '概览' },
  { key: 'convertible', label: '转债' },
  { key: 'ah', label: 'AH' },
  { key: 'ab', label: 'AB' },
  { key: 'lof', label: 'LOF' },
  { key: 'subscription', label: '打新' },
  { key: 'monitor', label: '监控' },
];

export default function BottomNav({ activeTab, onChange }) {
  return (
    <nav className="bottom-nav" aria-label="主导航">
      <div className="bottom-nav-grid">
        {NAV_TABS.map((tab) => (
          <button
            key={tab.key}
            className={`bottom-nav-item ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => onChange(tab.key)}
            type="button"
          >
            {tab.label}
          </button>
        ))}
        <span className="bottom-nav-item bottom-nav-item-placeholder" aria-hidden="true" />
      </div>
    </nav>
  );
}
