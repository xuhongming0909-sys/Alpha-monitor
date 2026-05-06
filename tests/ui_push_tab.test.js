const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

assert.ok(!/推送设置/.test(app), 'App should remove 推送设置 tab');
assert.ok(!/activeTab\s*===\s*['"]push['"]/.test(app), 'App should not render push tab content');
assert.ok(!/PushSettings|PushSettingsPage/.test(app), 'App should remove push settings UI');

console.log('ui push tab ok');
