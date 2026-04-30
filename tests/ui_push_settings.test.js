const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

// Push config state
assert.ok(/pushConfig|push.*State/i.test(app), 'App should have push config state');

// Push config API endpoint
assert.ok(/api\/push\/config/i.test(app), 'App should consume push config API');

// Push settings component or panel
assert.ok(/PushSettings|push.*panel|推送设置/i.test(app), 'App should have push settings UI');

console.log('ui push settings ok');
