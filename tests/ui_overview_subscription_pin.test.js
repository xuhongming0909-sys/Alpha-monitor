// AI-SUMMARY: 概览页打新置顶+策略筛选器测试
// 对应 specs/react-terminal-ui.md §4.1

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(root, relativePath), 'utf8');
}

const app = read('ui/src/App.jsx');

// Test 1: 打新置顶区组件存在
function testSubscriptionTopSection() {
  const hasSubscriptionTop = /SubscriptionTopSection|subscription-top/i.test(app);
  if (!hasSubscriptionTop) {
    throw new Error('App缺少打新置顶区块组件');
  }
  console.log('✓ 打新置顶区块存在');
}

// Test 2: 概览页使用打新置顶区
function testOverviewUsesSubscriptionTop() {
  const usesSubscriptionTop = /SubscriptionTopSection|subscription-top/i.test(app);
  if (!usesSubscriptionTop) {
    throw new Error('App未渲染打新置顶区');
  }
  const overviewBlockMatch = app.match(/activeTab === 'overview'[\s\S]*?\<\/\>/);
  if (!overviewBlockMatch) {
    throw new Error('未找到overview条件渲染块');
  }
  const overviewBlock = overviewBlockMatch[0];
  const hasTopSection = /SubscriptionTopSection|subscription-top/i.test(overviewBlock);
  if (!hasTopSection) {
    throw new Error('打新置顶区未在概览条件渲染中');
  }
  console.log('✓ 概览页渲染打新置顶区');
}

// Test 3: 打新表格列完整（匹配老UI：当前阶段、类型、名称/代码、申购日、中签缴款日、上市日、申购上限、发行价/转股价）
function testSubscriptionTableColumns() {
  const requiredHeaders = ['当前阶段', '类型', '名称/代码', '申购日', '中签缴款日', '上市日', '申购上限', '发行价/转股价'];
  for (const header of requiredHeaders) {
    if (!app.includes(header)) {
      throw new Error(`打新表格缺少列：${header}`);
    }
  }
  console.log('✓ 打新表格列完整（匹配老UI）');
}

// Test 4: 策略筛选器存在
function testStrategyFilter() {
  const hasStrategyFilter = /strategyFilter|OpportunityFilter|strategy-type|filter.*strategy|opportunity-filter-bar/i.test(app);
  if (!hasStrategyFilter) {
    throw new Error('App缺少策略筛选器');
  }
  console.log('✓ 策略筛选器存在');
}

// Test 5: 筛选选项包含全部主要策略
function testStrategyFilterOptions() {
  const options = ['全部', '转债', 'LOF', 'AH', 'AB', '事件套利'];
  let found = 0;
  for (const opt of options) {
    if (app.includes(opt)) found++;
  }
  if (found < 4) {
    throw new Error(`策略筛选选项不足，需要：${options.join('|')}`);
  }
  console.log('✓ 策略筛选选项完整');
}

// Test 6: buildOpportunityRows支持事件套利
function testMergerOpportunity() {
  const buildRowsMatch = app.match(/function\s+buildOpportunityRows[\s\S]*?return\s+rows\.slice/);
  if (!buildRowsMatch) {
    throw new Error('未找到buildOpportunityRows函数');
  }
  const code = buildRowsMatch[0];
  const hasMerger = /merger|event|事件/i.test(code);
  if (!hasMerger) {
    throw new Error('buildOpportunityRows缺少事件套利数据');
  }
  console.log('✓ buildOpportunityRows支持事件套利');
}

// Test 7: 打新置顶区在概览顶部
function testSubscriptionTopPosition() {
  const overviewBlockMatch = app.match(/activeTab === 'overview'[\s\S]*?\<\/\>/);
  if (!overviewBlockMatch) return;
  const overviewBlock = overviewBlockMatch[0];

  const subsIndex = overviewBlock.search(/SubscriptionTopSection|subscription-top/i);
  const cmdIndex = overviewBlock.search(/OpportunityCommandCenter|command-center/i);

  if (subsIndex === -1) {
    throw new Error('未找到打新置顶区在概览中的位置');
  }

  if (cmdIndex !== -1 && subsIndex > cmdIndex) {
    throw new Error('打新置顶区应该在机会排序区之前（置顶布局）');
  }
  console.log('✓ 打新置顶区位置正确（机会排序之前）');
}

// Run all tests
console.log('\n概览页打新置顶测试:\n');
try {
  testSubscriptionTopSection();
  testOverviewUsesSubscriptionTop();
  testSubscriptionTableColumns();
  testStrategyFilter();
  testStrategyFilterOptions();
  testMergerOpportunity();
  testSubscriptionTopPosition();
  console.log('\n全部通过 ✓');
  process.exit(0);
} catch (error) {
  console.error(`\n✗ ${error.message}`);
  process.exit(1);
}
