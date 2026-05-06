// AI-SUMMARY: 验证 AH 溢价全局使用简洁表格视图
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

// 行为1：存在 AhCardList 组件文件
assert.ok(
  exists('ui/src/components/AhCardList.jsx'),
  '应存在 ui/src/components/AhCardList.jsx 文件'
);

// 行为2：App.jsx 导入了 AhCardList
const app = read('ui/src/App.jsx');
assert.ok(
  /import\s+.*AhCardList/.test(app),
  'App.jsx 应导入 AhCardList 组件'
);

// 行为3：App.jsx 在 ah tab 渲染 AhCardList
assert.ok(
  /activeTab\s*===\s*['"]ah['"]\s*&&\s*<AhCardList/.test(app),
  'App.jsx 应在 ah tab 渲染 AhCardList'
);

console.log('ui global ah card ok');
