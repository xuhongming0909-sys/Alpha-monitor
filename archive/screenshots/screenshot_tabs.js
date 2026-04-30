const { chromium } = require('playwright');

const TABS = [
  { label: '概览', name: 'overview' },
  { label: '转债套利', name: 'cbArb' },
  { label: 'AH溢价', name: 'ahPremium' },
  { label: 'AB溢价', name: 'abPremium' },
  { label: 'LOF套利', name: 'lofArb' },
  { label: '打新申购', name: 'subscription' },
  { label: '自定义监控', name: 'monitor' },
  { label: '分红提醒', name: 'dividend' },
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  for (const tab of TABS) {
    await page.goto('http://localhost:5001/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    
    if (tab.label !== '概览') {
      const btn = await page.locator('.tab-button', { hasText: tab.label }).first();
      if (await btn.isVisible().catch(() => false)) {
        await btn.click();
        await page.waitForTimeout(1500);
      }
    }
    
    await page.screenshot({ 
      path: `/tmp/tab_${tab.name}.png`, 
      fullPage: true 
    });
    console.log(`screenshot: tab_${tab.name}.png`);
  }
  
  await browser.close();
})();
