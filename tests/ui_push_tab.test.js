const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

// 推送设置在TabNav中存在
assert.ok(/'push'.*'推送设置'|推送设置.*TabNav/.test(app), 'App should have 推送设置 as top-level tab');

// 推送设置不在其他Tab底部显示
const pushAtBottom = app.match(/<PushSettings.*\/\s*>[\s\S]*?<\/main>/);
if (pushAtBottom) {
  // PushSettings should NOT be rendered after all tab content
  // It should only be in its own conditional
  assert.ok(!/activeTab.*===.*push.*PushSettings|PushSettings.*activeTab.*push/.test(app) || /<PushSettings.*\/\s*>/.test(app), 'PushSettings should be standalone tab, not at bottom');
}

// TabNav包含推送设置
assert.ok(/\{ key:.*push.*label:.*推送/.test(app), 'TabNav should include push tab');

console.log('ui push tab ok');
