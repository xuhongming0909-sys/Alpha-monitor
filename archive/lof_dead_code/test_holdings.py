import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import fetch_top10_stocks

for code in ['161128', '501312', '163208', '160644']:
    h = fetch_top10_stocks(code)
    tw = sum(x['weight'] for x in h) if h else 0
    print(f'{code} API: {len(h)} holdings, total={tw:.1f}%')
    for x in h[:5]:
        print(f'  {x["ticker"]} {x["name"]} {x["weight"]}% {x["market"]}')
    print()