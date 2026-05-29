import sys, traceback; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import deepseek_parse_holdings, _deepseek_parse_full_text
try:
    h1 = deepseek_parse_holdings('runtime_data/qreport/501018_2026Q1.pdf', '501018')
    print(f'section: {len(h1) if h1 else "None"}')
except Exception as e:
    print(f'section error: {e}')
    traceback.print_exc()
try:
    h2 = _deepseek_parse_full_text('runtime_data/qreport/501018_2026Q1.pdf', '501018')
    print(f'fulltext: {len(h2) if h2 else "None"}')
except Exception as e:
    print(f'fulltext error: {e}')
    traceback.print_exc()