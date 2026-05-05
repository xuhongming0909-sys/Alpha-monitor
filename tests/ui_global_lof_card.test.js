// AI-SUMMARY: 验证 LOF 套利全局使用卡片视图
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

assert.ok(exists('ui/src/components/LofCardList.jsx'), '应存在 LofCardList 组件文件');

const app = read('ui/src/App.jsx');
assert.ok(/import\s+.*LofCardList/.test(app), 'App.jsx 应导入 LofCardList');
assert.ok(/activeTab\s*===\s*['"]lof['"]\s*&&\s*<LofCardList/.test(app), 'App.jsx 应在 lof tab 渲染 LofCardList');

console.log('ui global lof card ok');
