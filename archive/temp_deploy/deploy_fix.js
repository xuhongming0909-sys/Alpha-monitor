const { execSync } = require('child_process');
const host = '43.139.35.190', user = 'ubuntu', pass = 'DellG77588';
const proj = '/home/ubuntu/Alpha monitor';
function ssh(cmd) {
  try {
    return execSync("sshpass -p '" + pass + "' ssh -o StrictHostKeyChecking=no " + user + "@" + host + " " + JSON.stringify(cmd), { timeout: 30000 }).toString();
  } catch(e) { return 'ERR: ' + (e.stderr ? e.stderr.toString().slice(0,500) : e.message); }
}
async function run() {
  console.log('1. Fix fetcher...');
  const fixPy = `cd "${proj}" && python3 -c "
with open('data_fetch/lof_iopv/fetcher.py','r',encoding='utf-8-sig') as f:
    c=f.read()
old='QDII_FUNDS = [\\ndef _load_funds_from_config'
if old in c:
    c=c.replace(old,'def _load_funds_from_config')
    open('data_fetch/lof_iopv/fetcher.py','w',encoding='utf-8').write(c)
    print('FIXED')
else:
    print('NO_ORPHAN')
compile(c,'f','exec')
print('SYNTAX_OK')
"`;
  console.log(ssh(fixPy));
  console.log('2. Restart...');
  console.log(ssh("sudo systemctl restart alpha-monitor"));
  console.log('3. Wait 6s...');
  await new Promise(r => setTimeout(r, 6000));
  console.log('4. Verify...');
  const v = ssh(`cd "${proj}" && curl -s http://127.0.0.1:5001/api/market/lof-arbitrage | python3 -c "
import sys,json
d=json.load(sys.stdin)
rows=d.get('data',{}).get('rows',[])
print('rows:',len(rows))
codes=[r.get('code') for r in rows]
print('codes:',sorted(codes))
r=rows[0] if rows else {}
print('calcTarget:',r.get('calcTarget'))
print('r2:',r.get('r2'))
has_old=any(c in codes for c in ['159202','513660','513690','520600'])
print('has_old:',has_old)
"`);
  console.log(v);
}
run().catch(e => console.error(e));