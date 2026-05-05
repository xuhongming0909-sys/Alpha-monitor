// AI-SUMMARY: 验证手机端底部导航栏存在且被条件渲染
// 对应 INDEX.md §9.8 测试索引

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

function exists(relativePath) {
  return fs.existsSync(path.join(root, relativePath));
}

// 行为1：存在 BottomNav 组件文件
assert.ok(
  exists('ui/src/components/BottomNav.jsx'),
  '应存在 ui/src/components/BottomNav.jsx 文件'
);

// 行为2：App.jsx 导入了 BottomNav
const app = read('ui/src/App.jsx');
assert.ok(
  /import\s+.*BottomNav/.test(app),
  'App.jsx 应导入 BottomNav 组件'
);

// 行为3：App.jsx 中有条件渲染 BottomNav（在 isMobile 下）
assert.ok(
  /isMobile\s*&&?\s*<BottomNav|BottomNav\s*\{.*isMobile|isMobile.*BottomNav/.test(app),
  'App.jsx 应在手机端条件渲染 BottomNav'
);

console.log('ui mobile bottom nav ok');
