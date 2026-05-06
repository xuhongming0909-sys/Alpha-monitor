const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

assert.ok(!/pushConfig/i.test(app), 'App should not keep push config state');
assert.ok(!/api\/push\/config/i.test(app), 'App should not consume push config API');
assert.ok(!/PushSettings|推送设置/i.test(app), 'App should not keep push settings UI');

console.log('ui push settings ok');
