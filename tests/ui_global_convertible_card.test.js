// AI-SUMMARY: 验证转债套利全局使用卡片视图，不区分设备
// 对应 INDEX.md §9.8 测试索引

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

// 行为1：ConvertibleCardList 被无条件渲染在主页
assert.ok(
  /<ConvertibleCardList/.test(app),
  'App.jsx 应渲染 ConvertibleCardList'
);
assert.ok(
  !/isMobile\s*\?\s*<ConvertibleCardList/.test(app),
  'ConvertibleCardList 不应被 isMobile 条件包裹'
);

console.log('ui global convertible card ok');
