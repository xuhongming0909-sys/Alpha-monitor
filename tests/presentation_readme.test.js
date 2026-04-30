// AI-SUMMARY: presentation README 存在性测试
const fs = require('fs');
const path = require('path');

const readmePath = path.resolve(__dirname, '..', 'presentation', 'README.md');

if (!fs.existsSync(readmePath)) {
  console.error('✗ presentation/README.md 不存在');
  process.exit(1);
}

const text = fs.readFileSync(readmePath, 'utf8');

const requiredSections = ['# presentation', '## 职责', 'API', '路由', 'React'];
for (const section of requiredSections) {
  if (!text.includes(section)) {
    console.error(`✗ presentation/README.md 缺少章节: ${section}`);
    process.exit(1);
  }
}

console.log('✓ presentation/README.md 存在且章节完整');
process.exit(0);
