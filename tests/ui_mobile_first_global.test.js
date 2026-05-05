// AI-SUMMARY: 验证全局 Mobile-First 样式：默认即移动端样式
// 对应 INDEX.md §9.8 测试索引

const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const css = read('ui/src/styles.css');

// 行为1：全局 .terminal-shell 不应有 1920px 最小宽度
const terminalShellMatch = css.match(/\.terminal-shell\s*\{([^}]*)\}/);
assert.ok(terminalShellMatch, '应存在 .terminal-shell 规则');
const terminalShellBody = terminalShellMatch[1];
assert.ok(
  !/min-width\s*:\s*1920px/.test(terminalShellBody),
  '全局 .terminal-shell 不应包含 min-width: 1920px'
);

// 行为2：全局 .wide-table 不应有 1800px 最小宽度
const wideTableMatch = css.match(/\.wide-table\s*\{([^}]*)\}/);
assert.ok(wideTableMatch, '应存在 .wide-table 规则');
const wideTableBody = wideTableMatch[1];
assert.ok(
  !/min-width\s*:\s*1800px/.test(wideTableBody),
  '全局 .wide-table 不应包含 min-width: 1800px'
);

// 行为3：全局 .dashboard-grid 应为单列
const dashGridMatch = css.match(/\.dashboard-grid\s*\{([^}]*)\}/);
assert.ok(dashGridMatch, '应存在 .dashboard-grid 规则');
const dashGridBody = dashGridMatch[1];
assert.ok(
  /grid-template-columns\s*:\s*1fr/.test(dashGridBody),
  '全局 .dashboard-grid 应为单列 1fr'
);

// 行为4：全局 .terminal-grid 应为单列
const termGridMatch = css.match(/\.terminal-grid\s*\{([^}]*)\}/);
assert.ok(termGridMatch, '应存在 .terminal-grid 规则');
const termGridBody = termGridMatch[1];
assert.ok(
  /grid-template-columns\s*:\s*1fr/.test(termGridBody),
  '全局 .terminal-grid 应为单列 1fr'
);

console.log('ui mobile-first global ok');
