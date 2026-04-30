const { chromium } = require('playwright');

const TABS = [
  { label: '概览', name: 'overview', check: '套利核心池' },
  { label: '转债套利', name: 'cbArb', check: '转债代码' },
  { label: 'AH溢价', name: 'ahPremium', check: 'A股代码' },
  { label: 'AB溢价', name: 'abPremium', check: 'B股代码' },
  { label: 'LOF套利', name: 'lofArb', check: 'LOF代码' },
  { label: '打新申购', name: 'subscription', check: '新股名称' },
  { label: '自定义监控', name: 'monitor', check: '监控名称' },
  { label: '分红提醒', name: 'dividend', check: '股票名称' },
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
    
    // verify tab content
    const hasContent = await page.locator('text=' + tab.check).first().isVisible().catch(() => false);
    console.log(`${tab.name}: ${hasContent ? 'OK' : 'MISSING'} (${tab.check})`);
    
    await page.screenshot({ 
      path: `/tmp/tab_${tab.name}.png`, 
      fullPage: true 
    });
  }
  
  await browser.close();
})();
