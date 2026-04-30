const fs = require('fs');
const path = require('path');
const assert = require('assert');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

// 转债套利tab有抢权配售子tab
assert.ok(/subTab.*===.*'rights'|tab-button.*抢权配售/.test(app), 'App should have 抢权配售 sub-tab in convertible table');

// ConvertibleTable接收rightsIssueData参数
assert.ok(/ConvertibleTable.*rightsIssueData|rightsIssueData.*ConvertibleTable/.test(app), 'ConvertibleTable should receive rightsIssueData prop');

// 抢权配售表格渲染逻辑存在
assert.ok(/renderRightsIssueTable|renderRiSection/.test(app), 'App should have 抢权配售 table render function');

// 抢权配售市场子Tab存在
assert.ok(/riMarket.*sh.*sz|setRiMarket/.test(app), 'App should have market sub-tab (sh/sz) for 抢权配售');

// 抢权配售三阶段存在
assert.ok(/riApply.*riAmbush.*riWait|inApplyStage/.test(app), 'App should have 3 stages (apply/ambush/wait)');

console.log('ui rights issue tab ok');
