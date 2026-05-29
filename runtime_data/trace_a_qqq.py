import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\93724\Desktop\Alpha monitor')
sys.path.insert(0, r'C:\Users\93724\Desktop\Alpha monitor')

from strategy.lof_iopv.backtest_v2 import _get_nav_dates, _get_fx_rates, _get_etf_prices
from strategy.lof_iopv.calc import calc_a_iopv
from data_fetch.lof_iopv.source import _fetch_stock_position

code = '161130'
etf = 'QQQ'

nav_dict = _get_nav_dates(code, '2026-02-01', '2026-05-28')
etf_prices = _get_etf_prices(etf, '2026-02-01', '2026-05-28')
fx_rates = _get_fx_rates('2026-02-01', '2026-05-28')
stock_position = _fetch_stock_position(code) or 90.0

nav_dates = sorted(nav_dict.keys())
print(f'stock_position={stock_position}%')
print(f'nav_dates={len(nav_dates)}, etf_prices={len(etf_prices)}, fx_dates={len(fx_rates)}')
print()

max_err = 0
max_idx = None
all_rows = []

for i in range(1, len(nav_dates)):
    d_prev, d_curr = nav_dates[i-1], nav_dates[i]
    if d_prev not in etf_prices or d_curr not in etf_prices:
        continue
    if d_prev not in fx_rates or d_curr not in fx_rates:
        continue
    nav_prev = nav_dict[d_prev]
    nav_curr = nav_dict[d_curr]
    if nav_prev <= 0:
        continue

    etf_prev = etf_prices[d_prev]
    etf_curr = etf_prices[d_curr]
    etf_change_pct = (etf_curr / etf_prev - 1) * 100

    predicted, status, details = calc_a_iopv(
        nav=nav_prev, etf_change_pct=etf_change_pct,
        fx_now=fx_rates[d_curr], fx_base=fx_rates[d_prev],
        stock_position=stock_position, etf_nav_date_price=etf_prev,
    )

    if predicted is None or predicted <= 0:
        continue

    err_pct = abs(predicted - nav_curr) / nav_prev * 100
    all_rows.append((d_prev, d_curr, nav_prev, nav_curr, predicted, etf_prev, etf_curr, etf_change_pct, fx_rates[d_prev], fx_rates[d_curr], err_pct, status, details))

    if err_pct > max_err:
        max_err = err_pct
        max_idx = len(all_rows) - 1

print(f'Computed {len(all_rows)} days, max_err={max_err:.3f}%')
print()

# Max error day
r = all_rows[max_idx]
print(f'=== MAX ERROR: {r[0]} -> {r[1]} ===')
print(f'NAV prev: {r[2]}')
print(f'NAV curr: {r[3]}')
print(f'predicted: {r[4]:.6f}')
print(f'error: {abs(r[4]-r[3]):.6f} ({r[10]:.3f}%)')
print(f'status: {r[11]}')
print()
print(f'ETF({etf}) prev({r[0]}): {r[5]:.4f}')
print(f'ETF({etf}) curr({r[1]}): {r[6]:.4f}')
print(f'ETF change: {r[7]:.4f}%')
print(f'fx_base({r[0]}): {r[8]}')
print(f'fx_now({r[1]}): {r[9]}')
print(f'stock_position: {stock_position}%')
print()
print(f'=== Calculation Trace ===')
etf_period_ret = r[7] / 100
fx_ratio = r[9] / r[8] if r[8] and r[8] > 0 else 1.0
stock_frac = stock_position / 100
portfolio_ret = stock_frac * etf_period_ret
est = r[2] * (1 + portfolio_ret) * fx_ratio

print(f'etf_period_ret = etf_change/100 = {r[7]:.4f}% / 100 = {etf_period_ret:.6f}')
print(f'fx_ratio = fx_now/fx_base = {r[9]}/{r[8]} = {fx_ratio:.6f}')
print(f'portfolio_ret = stock_position/100 * etf_period_ret = {stock_frac} * {etf_period_ret:.6f} = {portfolio_ret:.6f}')
print(f'est = NAV * (1 + portfolio_ret) * fx_ratio')
print(f'    = {r[2]} * (1 + {portfolio_ret:.6f}) * {fx_ratio:.6f}')
print(f'    = {r[2]} * {1+portfolio_ret:.6f} * {fx_ratio:.6f}')
print(f'    = {est:.6f}')
print(f'actual NAV = {r[3]}')
print(f'error = |{est:.6f} - {r[3]}| = {abs(est-r[3]):.6f} ({abs(est-r[3])/r[2]*100:.3f}%)')
