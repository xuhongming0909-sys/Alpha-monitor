import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import deepseek_parse_holdings
h = deepseek_parse_holdings('runtime_data/qreport/501018_2026Q1.pdf', '501018')
print(f'Result: {len(h) if h else "None"} holdings')
if h:
    for x in h: print(f'  {x}')