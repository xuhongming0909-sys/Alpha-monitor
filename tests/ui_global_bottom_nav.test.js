// AI-SUMMARY: 验证底部导航全局显示，不依赖 isMobile
// 对应 INDEX.md §9.8 测试索引

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');
const nav = read('ui/src/components/BottomNav.jsx');

// 行为1：BottomNav 被无条件渲染（不包裹在 isMobile 条件中）
assert.ok(
  /<BottomNav/.test(app),
  'App.jsx 应渲染 BottomNav'
);
assert.ok(
  !/isMobile\s*&&\s*<BottomNav/.test(app) && !/isMobile\s*\?\s*<BottomNav/.test(app),
  'BottomNav 不应被 isMobile 条件包裹，应全局显示'
);

// 行为2：顶部 TabNav 已移除
assert.ok(
  !/<TabNav/.test(app),
  'App.jsx 不应再渲染顶部 TabNav'
);

// 行为3：底部导航为两行 7 标签
const requiredLabels = ['概览', '转债', 'AH', 'AB', 'LOF', '打新', '监控'];
for (const label of requiredLabels) {
  assert.ok(nav.includes(label), `BottomNav 应包含 ${label}`);
}
assert.ok(!nav.includes('更多'), 'BottomNav 不应再保留更多下拉');
assert.ok(/gridTemplateColumns:\s*'repeat\(4,\s*1fr\)'|bottom-nav-grid/.test(nav), 'BottomNav 应为网格两行布局');

console.log('ui global bottom nav ok');
