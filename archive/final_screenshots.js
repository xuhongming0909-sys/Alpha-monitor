const { chromium } = require('playwright');

const TABS = [
  { label: '概览', name: 'overview' },
  { label: '转债', name: 'convertible' },
  { label: 'AH溢价', name: 'ah' },
  { label: 'AB溢价', name: 'ab' },
  { label: 'LOF套利', name: 'lof' },
  { label: '打新/申购', name: 'subscription' },
  { label: '自定义监控', name: 'monitor' },
  { label: '分红提醒', name: 'dividend' },
  { label: '抢权配售', name: 'cbRightsIssue' },
  { label: '事件套利', name: 'merger' },
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  for (const tab of TABS) {
    await page.goto('http://localhost:5001/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);
    
    if (tab.label !== '概览') {
      await page.click(`.tab-button:has-text("${tab.label}")`);
      await page.waitForTimeout(2000);
    }
    
    await page.screenshot({ 
      path: `/tmp/final_${tab.name}.png`, 
      fullPage: true 
    });
    
    // Check data count
    const rows = await page.locator('.dense-table tbody tr:not(.empty-row)').count();
    const hasEmpty = await page.locator('.empty-cell').count();
    console.log(`${tab.name}: ${rows} data rows, empty=${hasEmpty > 0}`);
  }
  
  await browser.close();
  console.log('All screenshots taken');
})();
