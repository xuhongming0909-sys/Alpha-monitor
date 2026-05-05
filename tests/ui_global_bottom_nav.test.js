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

// 行为1：BottomNav 被无条件渲染（不包裹在 isMobile 条件中）
assert.ok(
  /<BottomNav/.test(app),
  'App.jsx 应渲染 BottomNav'
);
assert.ok(
  !/isMobile\s*&&\s*<BottomNav/.test(app) && !/isMobile\s*\?\s*<BottomNav/.test(app),
  'BottomNav 不应被 isMobile 条件包裹，应全局显示'
);

console.log('ui global bottom nav ok');
