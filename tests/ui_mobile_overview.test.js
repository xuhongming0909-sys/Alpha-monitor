// AI-SUMMARY: 验证概览页在手机端的关键样式优化
// 对应 INDEX.md §9.8 测试索引

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const css = read('ui/src/styles.css');
const mediaIndex = css.search(/@media\s*\(\s*max-width\s*:\s*768px\s*\)/);
assert.ok(mediaIndex >= 0, '应存在 768px 媒体查询');
const afterMedia = css.slice(mediaIndex);

// 行为1：搜索输入框在手机端不应有 max-width 限制
assert.ok(
  /\.search-input\s*\{[^}]*max-width\s*:\s*none/.test(afterMedia) ||
  /\.search-input\s*\{[^}]*max-width\s*:\s*100%/.test(afterMedia) ||
  /\.search-input\s*\{[^}]*max-width\s*:\s*auto/.test(afterMedia),
  '移动端 .search-input 应取消 max-width 限制，占满可用宽度'
);

// 行为2：品牌副标题在手机端隐藏，节省空间
assert.ok(
  /\.brand-subtitle\s*\{[^}]*display\s*:\s*none/.test(afterMedia),
  '移动端 .brand-subtitle 应隐藏'
);

// 行为3：底部导航两行布局
assert.ok(
  /bottom-nav-grid|grid-template-columns\s*:\s*repeat\(4,\s*1fr\)/.test(css),
  '应存在两行底部导航网格样式'
);

// 行为4：主列表应为密集行表字段流
assert.ok(
  /dense-row|row-field|field-label|field-value/.test(css),
  '应存在密集行表字段流样式'
);

console.log('ui mobile overview ok');
