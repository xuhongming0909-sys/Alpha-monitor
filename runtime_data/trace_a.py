import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\93724\Desktop\Alpha monitor')
sys.path.insert(0, r'C:\Users\93724\Desktop\Alpha monitor')

from strategy.lof_iopv.backtest_v2 import _get_nav_dates, _get_fx_rates
from strategy.lof_iopv.calc import calc_a_iopv
from data_fetch.lof_db.schema import get_db

code = '161130'
etf = 'QQQ'

nav_dict = _get_nav_dates(code, '2026-02-01', '2026-05-28')
fx_rates = _get_fx_rates('2026-02-01', '2026-05-28')

# Get ETF prices from stock_prices table
conn = get_db()
etf_rows = conn.execute('SELECT date, close FROM stock_prices WHERE ticker=? ORDER BY date', (etf,)).fetchall()
etf_prices = {r[0]: r[1] for r in etf_rows}
conn.close()

# Get stock position
from data_fetch.lof_iopv.source import _fetch_stock_position
stock_position = _fetch_stock_position(code) or 90.0

nav_dates = sorted(nav_dict.keys())
print(f'stock_position={stock_position}%, etf={etf}, nav_dates={len(nav_dates)}, etf_prices={len(etf_prices)}')
print()

max_err = 0
max_day = None
all_rows = []

for i in range(1, len(nav_dates)):
    d_prev, d_curr = nav_dates[i-1], nav_dates[i]
    if d_prev not in fx_rates or d_curr not in fx_rates:
        continue
    nav_prev = nav_dict[d_prev]
    nav_curr = nav_dict[d_curr]
    if nav_prev <= 0:
        continue

    etf_nav_date = etf_prices.get(d_prev)
    etf_curr = etf_prices.get(d_curr)

    if not etf_nav_date or not etf_curr or etf_nav_date <= 0:
        continue

    etf_change_pct = (etf_curr / etf_nav_date - 1) * 100

    predicted, status, details = calc_a_iopv(
        nav=nav_prev,
        etf_change_pct=etf_change_pct,
        fx_now=fx_rates.get(d_curr),
        fx_base=fx_rates.get(d_prev),
        stock_position=stock_position,
        etf_nav_date_price=etf_nav_date,
    )

    if predicted is None or predicted <= 0:
        continue

    err_pct = abs(predicted - nav_curr) / nav_prev * 100
    all_rows.append((d_prev, d_curr, nav_prev, nav_curr, predicted, etf_nav_date, etf_curr, etf_change_pct, fx_rates.get(d_prev), fx_rates.get(d_curr), err_pct, details))

    if err_pct > max_err:
        max_err = err_pct
        max_day = len(all_rows) - 1

print(f'All {len(all_rows)} days computed, max_err={max_err:.3f}%')
print()

# Print the max error day
r = all_rows[max_day]
d_prev, d_curr = r[0], r[1]
print(f'=== MAX ERROR DAY: {d_prev} -> {d_curr} ===')
print(f'NAV prev: {r[2]}')
print(f'NAV curr: {r[3]}')
print(f'predicted: {r[4]:.6f}')
print(f'error: {abs(r[4]-r[3]):.6f} ({r[10]:.3f}%)')
print()
print(f'ETF({etf}) prev({d_prev}): {r[5]:.4f}')
print(f'ETF({etf}) curr({d_curr}): {r[6]:.4f}')
print(f'ETF change: {r[7]:.4f}%')
print(f'fx_base({d_prev}): {r[8]}')
print(f'fx_now({d_curr}): {r[9]}')
print(f'stock_position: {stock_position}%')
print()
print(f'status: {r[11]}')
print(f'details: {r[12]}')
