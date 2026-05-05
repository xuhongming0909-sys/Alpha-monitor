// AI-SUMMARY: 验证移动端基础媒体查询存在且覆盖桌面最小宽度
// 对应 INDEX.md §9.8 测试索引

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const css = read('ui/src/styles.css');

// 行为1：存在移动端媒体查询
assert.ok(
  /@media\s*\(\s*max-width\s*:\s*768px\s*\)/.test(css),
  'styles.css 应包含 @media (max-width: 768px) 媒体查询'
);

// 行为2：媒体查询内部覆盖 .terminal-shell 的最小宽度
const mediaMatch = css.match(/@media\s*\(\s*max-width\s*:\s*768px\s*\)\s*\{([^}]*)\}/);
// 由于CSS可能有嵌套，用更宽松的方式：查找媒体查询后的 .terminal-shell
const mediaIndex = css.search(/@media\s*\(\s*max-width\s*:\s*768px\s*\)/);
assert.ok(mediaIndex >= 0, '应找到媒体查询位置');
const afterMedia = css.slice(mediaIndex);
// 在媒体查询区域内查找 .terminal-shell 的 min-width: 0
assert.ok(
  /\.terminal-shell\s*\{[^}]*min-width\s*:\s*0/.test(afterMedia),
  '移动端媒体查询内应将 .terminal-shell 的 min-width 设为 0'
);

// 行为3：手机端增大 Tab 按钮触控区域
assert.ok(
  /\.tab-button\s*\{[^}]*min-height\s*:\s*40px/.test(afterMedia) ||
  /\.tab-button\s*\{[^}]*padding\s*:\s*8px\s+14px/.test(afterMedia),
  '移动端应将 .tab-button 触控区域增大'
);

console.log('ui mobile media query ok');
