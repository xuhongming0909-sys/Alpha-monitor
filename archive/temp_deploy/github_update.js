const https = require('https');
const fs = require('fs');
const path = require('path');

const REPO = 'xuhongming0909-sys/Alpha-monitor';
const BRANCH = 'main';

function apiRequest(options, body) {
  return new Promise((resolve, reject) => {
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
        catch(e) { resolve({ status: res.statusCode, data }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(body);
    req.end();
  });
}

async function getFileSha(filePath) {
  const options = {
    hostname: 'api.github.com',
    path: `/repos/${REPO}/contents/${filePath}?ref=${BRANCH}`,
    method: 'GET',
    headers: { 'User-Agent': 'Node.js', 'Accept': 'application/vnd.github.v3+json' }
  };
  return apiRequest(options);
}

async function updateFile(filePath, content, sha, message) {
  const body = JSON.stringify({
    message,
    content: Buffer.from(content).toString('base64'),
    sha,
    branch: BRANCH
  });
  const options = {
    hostname: 'api.github.com',
    path: `/repos/${REPO}/contents/${filePath}`,
    method: 'PUT',
    headers: {
      'User-Agent': 'Node.js',
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json'
    }
  };
  return apiRequest(options, body);
}

async function main() {
  const files = [
    { path: 'data_fetch/lof_iopv/fetcher.py', local: 'data_fetch/lof_iopv/fetcher.py', msg: 'fix(lof): restore fetcher with 27 funds + _load_from_config' },
    { path: 'strategy/lof_iopv/service.py', local: 'strategy/lof_iopv/service.py', msg: 'fix(lof): calcCore to calcTarget, B-type shows top10' },
    { path: 'runtime_data/backtest/a_results.json', local: 'runtime_data/backtest/a_results.json', msg: 'feat(lof): add A-type backtest results for 23 funds' },
  ];

  for (const f of files) {
    console.log(`Getting SHA for ${f.path}...`);
    const resp = await getFileSha(f.path);
    if (resp.status !== 200) {
      console.log(`  SKIP ${f.path}: ${resp.status}`);
      continue;
    }
    const sha = resp.data.sha;
    const content = fs.readFileSync(f.local, 'utf-8');
    console.log(`  Updating ${f.path} (sha: ${sha.slice(0,8)}...)`);
    const updateResp = await updateFile(f.path, content, sha, f.msg);
    console.log(`  Result: ${updateResp.status}`);
    if (updateResp.status !== 200) {
      console.log(`  Error: ${JSON.stringify(updateResp.data).slice(0, 200)}`);
    }
  }
  console.log('Done!');
}

main().catch(e => console.error(e));