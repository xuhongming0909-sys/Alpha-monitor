const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  
  await page.goto('http://localhost:5001/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  const html = await page.content();
  console.log(html.substring(0, 2000));
  console.log('\n--- TABS ---');
  const tabs = await page.locator('.tab-button').all();
  for (const t of tabs) {
    const text = await t.textContent();
    const cls = await t.getAttribute('class');
    console.log(`  [${text}] class=${cls}`);
  }
  
  await browser.close();
})();
