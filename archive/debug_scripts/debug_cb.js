const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  page.on('console', msg => {
    if (msg.type() === 'error') console.log('BROWSER ERROR:', msg.text());
  });
  page.on('pageerror', err => console.log('PAGE ERROR:', err.message));
  
  await page.goto('http://localhost:5001/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  // Click the convertible tab
  await page.click('.tab-button:has-text("转债")');
  await page.waitForTimeout(2000);
  
  const html = await page.content();
  
  // Check if the table has data
  const rows = await page.locator('.dense-table tbody tr').count();
  console.log('Table rows:', rows);
  
  // Check for error messages
  const errors = await page.locator('.empty-cell').allTextContents();
  console.log('Empty cells:', errors);
  
  await browser.close();
})();
