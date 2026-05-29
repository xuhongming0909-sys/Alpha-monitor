import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import get_fund_holdings, store_holdings_to_db
for code in ['501225', '160416', '501018']:
    valid, excluded, err = get_fund_holdings(code)
    if err:
        print(f'{code} FAIL: {err}')
    else:
        store_holdings_to_db(code, valid)
        print(f'{code} OK: {len(valid)} holdings')
        for t, w, m in valid:
            print(f'  {t:10s} {w:6.2f}% {m}')
    print()