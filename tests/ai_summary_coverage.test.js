// AI-SUMMARY: AI-SUMMARY 覆盖率测试：验证核心代码文件都有注释
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

function scan(dir, pattern) {
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      // Skip excluded directories
      if (['node_modules', '.claude', '.git', 'archive', 'runtime_data', 'ui/dist'].includes(entry.name)) continue;
      results.push(...scan(fullPath, pattern));
    } else if (pattern.test(entry.name)) {
      results.push(fullPath);
    }
  }
  return results;
}

const files = scan(root, /\.(py|js|jsx)$/)
  .filter((f) => {
    const rel = path.relative(root, f);
    // 只检查核心代码文件
    const coreDirs = ['data_fetch/', 'strategy/', 'shared/', 'notification/', 'presentation/'];
    return coreDirs.some((d) => rel.startsWith(d));
  });
const missing = [];

for (const file of files) {
  const text = fs.readFileSync(file, 'utf8');
  if (!text.includes('AI-SUMMARY')) {
    missing.push(path.relative(root, file));
  }
}

if (missing.length > 0) {
  console.error(`✗ ${missing.length} 个文件缺少 AI-SUMMARY:`);
  missing.forEach((f) => console.error(`  - ${f}`));
  process.exit(1);
}

console.log(`✓ ${files.length} 个代码文件全部有 AI-SUMMARY`);
process.exit(0);
