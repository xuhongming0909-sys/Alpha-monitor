const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

// Tab state management
assert.ok(/useState.*activeTab|const\s*\[\s*activeTab\s*,/i.test(app), 'App should have activeTab state');

// Required tab labels
const tabs = ['转债', 'AH', 'AB', 'LOF', '打新', '监控', '分红', '抢权', '事件'];
for (const tab of tabs) {
  assert.ok(app.includes(tab), `App should include ${tab} tab`);
}

// Module table components
assert.ok(/AhTable|AbTable|LofTable|SubscriptionTable|MonitorTable|DividendTable|CbRightsIssueTable|MergerTable/i.test(app), 'App should have module table components');

console.log('ui module navigation ok');
