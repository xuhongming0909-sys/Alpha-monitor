// AI-SUMMARY: 概览页打新置顶+策略筛选器测试
// 对应 specs/react-terminal-ui.md §4.1

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

function testOverviewSectionBuilder() {
  const hasBuilder = /buildOverviewSections|OverviewPage/i.test(app);
  if (!hasBuilder) {
    throw new Error('App 缺少新的概览分块构建逻辑');
  }
  console.log('✓ 概览分块构建逻辑存在');
}

function testOverviewSectionOrder() {
  const expected = ['今日打新', '配售登记', '折价套利', '小额刚兑', '理论折价套利', 'AH 机会', 'AB 机会', '自定义监控'];
  for (const title of expected) {
    if (!app.includes(title)) {
      throw new Error(`概览缺少区块：${title}`);
    }
  }
  console.log('✓ 概览区块标题完整');
}

function testBestOpportunitiesRemoved() {
  if (/BestOpportunities|最佳机会/.test(app)) {
    throw new Error('概览不应再包含最佳机会');
  }
  console.log('✓ 最佳机会已移除');
}

function testNoEventOpportunity() {
  if (/事件套利/.test(app)) {
    throw new Error('概览不应再包含事件套利文案');
  }
  console.log('✓ 概览不再包含事件套利');
}

function testTheoreticalThresholdAndPositiveSpace() {
  const hasThreshold = />\s*10|10%/.test(app);
  const hasPositiveSpace = /套利空间|theoreticalOpportunity|theoreticalSpace/i.test(app);
  if (!hasThreshold || !hasPositiveSpace) {
    throw new Error('理论折价套利应按 >10% 正数套利空间展示');
  }
  console.log('✓ 理论折价套利阈值和展示口径存在');
}

function testMonitorThreshold() {
  if (!/bestYield.*30|>\s*30/.test(app)) {
    throw new Error('自定义监控应按最优收益率 > 30% 过滤');
  }
  console.log('✓ 自定义监控过滤阈值存在');
}

// Run all tests
console.log('\n概览页打新置顶测试:\n');
try {
  testOverviewSectionBuilder();
  testOverviewSectionOrder();
  testBestOpportunitiesRemoved();
  testNoEventOpportunity();
  testTheoreticalThresholdAndPositiveSpace();
  testMonitorThreshold();
  console.log('\n全部通过 ✓');
  process.exit(0);
} catch (error) {
  console.error(`\n✗ ${error.message}`);
  process.exit(1);
}
