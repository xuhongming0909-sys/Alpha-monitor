import sys, traceback
sys.path.insert(0, r'C:\Users\93724\Desktop\Alpha monitor')

# 1. calc.py
try:
    from strategy.lof_iopv.calc import to_float, calc_a_iopv, calc_b_iopv
    print('[OK] calc.py import')
except Exception as e:
    print('[FAIL] calc.py:', e)
    traceback.print_exc()

# 2. service.py
try:
    from strategy.lof_iopv.service import build_lof_iopv_response
    print('[OK] service.py import')
except Exception as e:
    print('[FAIL] service.py:', e)
    traceback.print_exc()

# 3. source.py + config
try:
    from data_fetch.lof_iopv.source import _load_fund_list, _fetch_nav, _fetch_holdings
    funds = _load_fund_list()
    print('[OK] source.py import, funds=' + str(len(funds)))
except Exception as e:
    print('[FAIL] source.py:', e)
    traceback.print_exc()

# 4. fetcher.py
try:
    from data_fetch.lof_iopv.fetcher import fetch_lof_iopv_snapshot
    print('[OK] fetcher.py import')
except Exception as e:
    print('[FAIL] fetcher.py:', e)
    traceback.print_exc()

# 5. Test single fund NAV fetch
try:
    nav_data = _fetch_nav('161130')
    print('[OK] fetch_nav(161130): nav=' + str(nav_data.get('nav')) + ' date=' + str(nav_data.get('navDate')))
except Exception as e:
    print('[FAIL] fetch_nav:', e)
    traceback.print_exc()

# 6. Test single fund holdings fetch
try:
    holdings = _fetch_holdings('161130')
    print('[OK] fetch_holdings(161130): ' + str(len(holdings)) + ' items')
    if holdings:
        print('  first: ' + str(holdings[0]))
except Exception as e:
    print('[FAIL] fetch_holdings:', e)
    traceback.print_exc()

# 7. Test _fetch_us_realtime
try:
    from data_fetch.lof_iopv.source import _fetch_us_realtime
    us = _fetch_us_realtime(['AAPL', 'QQQ'])
    print('[OK] fetch_us_realtime: ' + str(len(us)) + ' results')
    for k, v in us.items():
        print('  ' + k + ': ' + str(v.get('price')))
except Exception as e:
    print('[FAIL] fetch_us_realtime:', e)
    traceback.print_exc()

# 8. Test _fetch_etf_changes
try:
    from data_fetch.lof_iopv.source import _fetch_etf_changes
    ch = _fetch_etf_changes(['QQQ', 'SPY'])
    print('[OK] fetch_etf_changes: ' + str(ch))
except Exception as e:
    print('[FAIL] fetch_etf_changes:', e)
    traceback.print_exc()

# 9. Test _fetch_purchase_status
try:
    from data_fetch.lof_iopv.source import _fetch_purchase_status
    ps = _fetch_purchase_status()
    print('[OK] fetch_purchase_status: ' + str(len(ps)) + ' funds')
    if '161130' in ps:
        print('  161130: ' + str(ps['161130']))
except Exception as e:
    print('[FAIL] fetch_purchase_status:', e)
    traceback.print_exc()

# 10. Test service.py with mock data
try:
    mock_payload = {
        'success': True,
        'data': [{
            'code': '161130', 'name': '纳指LOF', 'currency': 'USD',
            'nav': 1.5, 'navDate': '2026-05-27', 'price': 1.52,
            'estimation': 'A', 'etf': 'QQQ',
            'holdings': [], 'currentPrices': {}, 'stockPosition': 90.0,
            'holdingsPrevClose': {}, 'navDatePrices': {},
            'currentFxRate': 7.2, 'applyFee': '1.5',
            'applyStatus': '开放申购', 'dailyLimit': None,
            'etfChange': 1.5,
        }],
        'updateTime': '2026-05-28T10:00:00', 'source': 'test',
        'sourceSummary': {'totalRows': 1, 'fxRates': {'USD': 7.2}},
    }
    result = build_lof_iopv_response(mock_payload, [])
    rows = result.get('data', {}).get('rows', [])
    print('[OK] service response: ' + str(len(rows)) + ' rows')
    if rows:
        r = rows[0]
        print('  iopv=' + str(r.get('iopv')) + ' premium=' + str(r.get('premiumRate')) + ' status=' + str(r.get('applyStatus')))
except Exception as e:
    print('[FAIL] service response:', e)
    traceback.print_exc()
