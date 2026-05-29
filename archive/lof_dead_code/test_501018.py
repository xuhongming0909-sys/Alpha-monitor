import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import get_fund_holdings

code = '501018'
valid, excluded, err = get_fund_holdings(code)
if err:
    print(f'FAIL: {err}')
else:
    print(f'OK: {len(valid)} holdings')
    for t, w, m in valid:
        print(f'  {t:10s} {w:6.2f}% {m}')