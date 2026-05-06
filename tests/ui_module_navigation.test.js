const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');
const nav = read('ui/src/components/BottomNav.jsx');

// Tab state management
assert.ok(/useState.*activeTab|const\s*\[\s*activeTab\s*,/i.test(app), 'App should have activeTab state');

// Required tab labels
const tabs = ['概览', '转债', 'AH', 'AB', 'LOF', '打新', '监控'];
for (const tab of tabs) {
  assert.ok(app.includes(tab) || nav.includes(tab), `App should include ${tab} tab`);
}

// Removed tabs should not exist
for (const removed of ['分红提醒', '事件套利', '推送设置']) {
  assert.ok(!app.includes(removed), `App should not include removed tab ${removed}`);
}

// Card/list components should back the modules
assert.ok(/AhCardList|AbCardList|LofCardList|SubscriptionCardList|MonitorCardList|ConvertibleCardList|RightsIssueCardList/i.test(app), 'App should use card/list components for modules');

console.log('ui module navigation ok');
