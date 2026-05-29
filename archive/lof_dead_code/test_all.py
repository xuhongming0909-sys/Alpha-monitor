import sys; sys.path.insert(0, '.')
from data_fetch.lof_iopv.report_holdings import get_fund_holdings, store_holdings_to_db, update_all_holdings

codes = [
    '161128', '501225', '161130', '161125', '161126', '161127',
    '162415', '160140', '501300', '164824', '160416', '162719',
    '162411', '160723', '161129', '501018', '163208', '160719',
    '164701', '161116', '160125', '160644', '164906', '501312',
]

results = update_all_holdings(codes)
ok = sum(1 for v in results.values() if v['ok'])
fail = sum(1 for v in results.values() if not v['ok'])
print(f'\n=== {ok} OK, {fail} FAIL ===')