// AI-SUMMARY: 验证转债套利在手机端渲染卡片列表替代宽表格
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

// 行为1：存在 ConvertibleCardList 组件文件
assert.ok(
  exists('ui/src/components/ConvertibleCardList.jsx'),
  '应存在 ui/src/components/ConvertibleCardList.jsx 文件'
);

// 行为2：App.jsx 导入了 ConvertibleCardList
const app = read('ui/src/App.jsx');
assert.ok(
  /import\s+.*ConvertibleCardList/.test(app),
  'App.jsx 应导入 ConvertibleCardList 组件'
);

// 行为3：ConvertibleTable 内部有条件渲染逻辑
assert.ok(
  /isMobile\s*\?\s*<ConvertibleCardList|<ConvertibleCardList.*\{.*isMobile|isMobile.*ConvertibleCardList/.test(app),
  'ConvertibleTable 应在手机端条件渲染 ConvertibleCardList'
);

console.log('ui mobile convertible card ok');
