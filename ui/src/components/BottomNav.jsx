// AI-SUMMARY: 手机端底部固定导航栏
// 对应 INDEX.md §9.3 文件摘要索引

import React from 'react';

const PRIMARY_TABS = [
  { key: 'overview', label: '概览' },
  { key: 'convertible', label: '转债' },
  { key: 'ah', label: 'AH' },
  { key: 'lof', label: 'LOF' },
];

const MORE_TABS = [
  { key: 'ab', label: 'AB溢价' },
  { key: 'subscription', label: '打新' },
  { key: 'monitor', label: '监控' },
  { key: 'dividend', label: '分红' },
  { key: 'merger', label: '事件' },
  { key: 'push', label: '设置' },
];

export default function BottomNav({ activeTab, onChange }) {
  const [moreOpen, setMoreOpen] = React.useState(false);

  return (
    <>
      <nav className="bottom-nav" style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 100,
        display: 'flex',
        borderTop: '1px solid var(--terminal-line)',
        background: 'var(--terminal-panel)',
      }}>
        {PRIMARY_TABS.map((tab) => (
          <button
            key={tab.key}
            className={`bottom-nav-item ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => { onChange(tab.key); setMoreOpen(false); }}
            style={{
              flex: 1,
              padding: '8px 4px',
              border: 0,
              borderRight: '1px solid var(--terminal-line)',
              background: activeTab === tab.key ? 'rgba(242, 184, 75, .08)' : 'transparent',
              color: activeTab === tab.key ? 'var(--terminal-yellow)' : 'var(--terminal-muted)',
              fontSize: '12px',
              cursor: 'pointer',
              minHeight: '52px',
            }}
          >
            {tab.label}
          </button>
        ))}
        <button
          className={`bottom-nav-item ${moreOpen ? 'active' : ''}`}
          onClick={() => setMoreOpen((v) => !v)}
          style={{
            flex: 1,
            padding: '8px 4px',
            border: 0,
            background: moreOpen ? 'rgba(242, 184, 75, .08)' : 'transparent',
            color: moreOpen ? 'var(--terminal-yellow)' : 'var(--terminal-muted)',
            fontSize: '12px',
            cursor: 'pointer',
            minHeight: '52px',
          }}
        >
          {moreOpen ? '收起' : '更多'}
        </button>
      </nav>

      {moreOpen && (
        <div style={{
          position: 'fixed',
          bottom: '52px',
          left: 0,
          right: 0,
          zIndex: 99,
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '1px',
          borderTop: '1px solid var(--terminal-line)',
          background: 'var(--terminal-line)',
        }}>
          {MORE_TABS.map((tab) => (
            <button
              key={tab.key}
              className={`bottom-nav-item ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => { onChange(tab.key); setMoreOpen(false); }}
              style={{
                padding: '12px 8px',
                border: 0,
                background: activeTab === tab.key ? 'rgba(242, 184, 75, .08)' : 'var(--terminal-panel)',
                color: activeTab === tab.key ? 'var(--terminal-yellow)' : 'var(--terminal-text)',
                fontSize: '13px',
                cursor: 'pointer',
                minHeight: '48px',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}
    </>
  );
}
