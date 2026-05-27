import sys, os
sys.path.insert(0, r'C:\Users\93724\Desktop\Alpha monitor')
os.chdir(r'C:\Users\93724\Desktop\Alpha monitor')

# Monkey-patch _load_fund_list to return only 3 funds
import data_fetch.lof_iopv.source as src
original_load = src._load_fund_list
def patched_load():
    funds = original_load()
    return [f for f in funds if f['code'] in ('161130', '161128', '161125')]
src._load_fund_list = patched_load

from data_fetch.lof_iopv.source import build_lof_snapshot
from strategy.lof_iopv.service import build_lof_iopv_response
import time, json

t0 = time.time()
payload = build_lof_snapshot()
t1 = time.time()
print('[snapshot] rows=' + str(len(payload.get('data', []))) + ' time=' + str(round(t1 - t0, 1)) + 's')

for row in payload.get('data', []):
    code = row.get('code')
    nav = row.get('nav')
    price = row.get('price')
    etf = row.get('etf')
    est = row.get('estimation')
    ec = row.get('etfChange')
    hc = len(row.get('holdings', []) or [])
    edp = row.get('etfNavDatePrice')
    print('  ' + code + ': nav=' + str(nav) + ' price=' + str(price) + ' etf=' + str(etf) + ' est=' + est + ' hc=' + str(hc) + ' etfChg=' + str(ec) + ' etfNavDP=' + str(edp))

result = build_lof_iopv_response(payload, [])
rows = result.get('data', {}).get('rows', [])
print('[response] rows=' + str(len(rows)))
for r in rows:
    print('  ' + r.get('code') + ' ' + r.get('name') + ': iopv=' + str(r.get('iopv')) + ' premium=' + str(r.get('premiumRate')) + ' status=' + str(r.get('applyStatus')) + ' calc=' + str(r.get('calcTarget')))
