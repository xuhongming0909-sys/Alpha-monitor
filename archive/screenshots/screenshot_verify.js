const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  await page.goto('http://localhost:5001/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Overview tab - check MetricMatrix
  const cards = await page.locator('.metric-card').count();
  console.log('Overview metric cards:', cards);
  
  // Click convertible tab
  await page.click('.tab-button:has-text("转债")');
  await page.waitForTimeout(2000);
  
  // Check tab sub-buttons
  const subTabs = await page.locator('.tab-nav .tab-button').allTextContents();
  console.log('Convertible sub-tabs:', subTabs);
  
  // Check table rows
  const rows = await page.locator('.dense-table tbody tr').count();
  console.log('Convertible table rows:', rows);
  
  // Check for data
  const tds = await page.locator('.dense-table tbody td').count();
  console.log('Convertible table cells:', tds);
  
  await page.screenshot({ path: '/tmp/verify_convertible.png', fullPage: true });
  console.log('Screenshot saved');
  
  // Also check the small redemption tab
  await page.click('.tab-nav .tab-button:has-text("小额")');
  await page.waitForTimeout(1500);
  const smallRows = await page.locator('.dense-table tbody tr').count();
  console.log('Small redemption rows:', smallRows);
  
  await browser.close();
})();
