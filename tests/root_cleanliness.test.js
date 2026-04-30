// AI-SUMMARY: 根目录清洁度测试：验证无垃圾文件
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

// 白名单文件
const allowedFiles = new Set([
  'README.md', 'CLAUDE.md', 'INDEX.md', 'MEMORY.md',
  'package.json', 'package-lock.json', 'requirements.txt',
  'start_server.js', 'data_dispatch.py', 'config.yaml',
  '.gitignore', '.env.example', '.env', 'server_config_loader.js',
]);

// 白名单目录
const allowedDirs = new Set([
  '.git', '.github', 'config', 'data_fetch', 'deploy', 'docs', 'presentation',
  'notification', 'scripts', 'shared', 'strategy', 'tests', 'ui', 'specs',
  'missions', 'templates', 'archive', 'runtime_data', 'node_modules',
]);

const entries = fs.readdirSync(root);
const violations = [];

for (const entry of entries) {
  const fullPath = path.join(root, entry);
  const stat = fs.statSync(fullPath);
  if (stat.isDirectory()) {
    if (!allowedDirs.has(entry)) violations.push(`非法目录: ${entry}`);
  } else {
    if (!allowedFiles.has(entry)) violations.push(`非法文件: ${entry}`);
  }
}

// 检查空目录
const strategyPath = path.join(root, 'strategy');
if (fs.existsSync(strategyPath)) {
  const strategyDirs = fs.readdirSync(strategyPath, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name);
  for (const dir of strategyDirs) {
    const dirPath = path.join(strategyPath, dir);
    const files = fs.readdirSync(dirPath);
    if (files.length === 0) violations.push(`空目录: strategy/${dir}`);
  }
}

if (violations.length > 0) {
  console.error('根目录清洁度违规:');
  violations.forEach((v) => console.error(`  ✗ ${v}`));
  process.exit(1);
}

console.log('✓ 根目录清洁');
process.exit(0);
