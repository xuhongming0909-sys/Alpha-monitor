import sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\93724\Desktop\Alpha monitor')
sys.path.insert(0, r'C:\Users\93724\Desktop\Alpha monitor')

from strategy.lof_iopv.backtest_v2 import _get_nav_dates, _get_fx_rates, _get_holdings, _get_stock_prices_batch
from strategy.lof_iopv.calc import calc_b_iopv
from data_fetch.lof_iopv.source import _fetch_stock_position

code = '160644'
d_prev = '2026-03-06'
d_curr = '2026-03-09'

nav_dict = _get_nav_dates(code, '2026-02-01', '2026-03-15')
fx_rates = _get_fx_rates('2026-02-01', '2026-03-15')
holdings = _get_holdings(code)
stock_ratio = _fetch_stock_position(code) or sum(h['weight'] for h in holdings)
tickers = list(set(h['ticker'] for h in holdings))
stock_prices = _get_stock_prices_batch(tickers, '2026-02-01', '2026-03-15')

print('=== 160644 2026-03-06->2026-03-09 ===')
print(f'NAV prev: {nav_dict[d_prev]}')
print(f'NAV curr: {nav_dict[d_curr]}')
print(f'stock_ratio: {stock_ratio}%')
print(f'fx({d_prev}): {fx_rates.get(d_prev)}')
print(f'fx({d_curr}): {fx_rates.get(d_curr)}')
print()

total_w = sum(h['weight'] for h in holdings)
print(f'T10 total weight: {total_w}%')
print()

for h in holdings:
    t = h['ticker']
    w = h['weight']
    nw = w / total_w
    pp = stock_prices.get(t, {}).get(d_prev)
    pc = stock_prices.get(t, {}).get(d_curr)
    if pp and pc and pp > 0:
        ret = pc / pp - 1
        contrib = nw * ret
        print(f'  {t:8s} w={w:5.2f}% norm={nw:.4f} price={pp:.4f}->{pc:.4f} ret={ret*100:+.3f}% contrib={contrib*100:.4f}%')
    else:
        print(f'  {t:8s} w={w:5.2f}% MISSING prev={pp} curr={pc}')

print()
weighted_ret = 0.0
for h in holdings:
    t = h['ticker']
    nw = h['weight'] / total_w
    pp = stock_prices.get(t, {}).get(d_prev)
    pc = stock_prices.get(t, {}).get(d_curr)
    if pp and pc and pp > 0:
        weighted_ret += nw * (pc / pp - 1)

fx_now = fx_rates.get(d_curr)
fx_base = fx_rates.get(d_prev)
fx_ratio = fx_now / fx_base if (fx_now and fx_base and fx_base > 0) else 1.0
portfolio_ret = stock_ratio / 100 * weighted_ret
est = nav_dict[d_prev] * (1 + portfolio_ret) * fx_ratio
err = abs(est - nav_dict[d_curr])

print(f'weighted_ret: {weighted_ret*100:.4f}%')
print(f'fx_ratio: {fx_ratio:.6f} (now={fx_now} base={fx_base})')
print(f'portfolio_ret = {stock_ratio}/100 * {weighted_ret*100:.4f}% = {portfolio_ret*100:.4f}%')
print(f'est = {nav_dict[d_prev]} * (1+{portfolio_ret*100:.4f}%) * {fx_ratio:.6f} = {est:.6f}')
print(f'actual: {nav_dict[d_curr]}')
print(f'error: {err:.6f} ({err/nav_dict[d_prev]*100:.3f}%)')
