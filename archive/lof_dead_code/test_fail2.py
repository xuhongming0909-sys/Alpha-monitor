import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import get_fund_holdings

for code in ['501300', '164824', '160723', '501018', '160719']:
    valid, excluded, err = get_fund_holdings(code)
    if err:
        print(f'{code} FAIL: {err}')
    else:
        print(f'{code} OK: {len(valid)} holdings')
        for t, w, m in valid:
            print(f'  {t:10s} {w:6.2f}% {m}')
    print()