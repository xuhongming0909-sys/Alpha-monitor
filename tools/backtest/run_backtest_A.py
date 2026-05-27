# -*- coding: utf-8 -*-
"""QDII LOF A类回测 - 24只指数跟踪基金，使用东财NAV + Yahoo Finance ETF"""
import os, sys, json, requests, numpy as np
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': None, 'https': None}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

PROXY = 'http://127.0.0.1:7890'
BACKTEST_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest'))

def get_nav_all(code, pages=3):
    nav = {}
    for p in range(1, pages + 1):
        url = f'http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={p}&pageSize=20&callback='
        r = SESSION.get(url, timeout=10)
        items = r.json()['Data']['LSJZList']
        if not items: break
        for i in items:
            nav[i['FSRQ']] = float(i['DWJZ'])
    return nav

def daily_ret_with_prev(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i-1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret

_yf_cache = {}
def yf_prices(ticker):
    if ticker in _yf_cache: return _yf_cache[ticker]
    old_h, old_s = os.environ.get('HTTP_PROXY'), os.environ.get('HTTPS_PROXY')
    try:
        os.environ['HTTP_PROXY'] = PROXY
        os.environ['HTTPS_PROXY'] = PROXY
        import yfinance as yf
        h = yf.Ticker(ticker).history(start='2026-03-01', end='2026-05-27')
    finally:
        if old_h: os.environ['HTTP_PROXY'] = old_h
        else: os.environ.pop('HTTP_PROXY', None)
        if old_s: os.environ['HTTPS_PROXY'] = old_s
        else: os.environ.pop('HTTPS_PROXY', None)
    if h.empty: return {}
    result = {idx.strftime('%Y-%m-%d'): float(row['Close']) for idx, row in h.iterrows()}
    _yf_cache[ticker] = result
    return result

# 24只A类基金 -> ETF映射
A_FUNDS = {
    '161128': ('标普信息科技', 'XLK'),
    '501225': ('全球芯片', 'SMH'),
    '161130': ('纳指100', 'QQQ'),
    '161125': ('标普500', 'SPY'),
    '161126': ('标普医疗保健', 'XLV'),
    '161127': ('标普生物科技', 'XBI'),
    '162415': ('美国消费', 'XLY'),
    '160140': ('美国REIT', 'VNQ'),
    '501300': ('美元债', 'AGG'),
    '164824': ('印度基金', 'INDA'),
    '160416': ('石油基金', 'XLE'),
    '162719': ('石油', 'XOP'),
    '162411': ('华宝油气', 'XOP'),
    '160723': ('嘉实原油', 'USO'),
    '161129': ('原油LOF', 'USO'),
    '501018': ('南方原油', 'USO'),
    '163208': ('全球油气能源', 'XLE'),
    '160216': ('国泰商品', 'GSG'),
    '161815': ('抗通胀', 'GLD'),
    '165513': ('中信保诚商品', 'GSG'),
    '160719': ('嘉实黄金', 'GLD'),
    '164701': ('黄金LOF', 'GLD'),
    '161116': ('黄金主题', 'GLD'),
}

all_results = {}
print(f'A类回测 | 2026-03-10 ~ 2026-05-26 | {len(A_FUNDS)}只')
print('=' * 90)

for code in sorted(A_FUNDS.keys()):
    name, etf = A_FUNDS[code]
    fund_nav = get_nav_all(code)
    fund_ret = daily_ret_with_prev(fund_nav)
    etf_prices = yf_prices(etf)
    etf_ret = daily_ret_with_prev(etf_prices)
    
    common = sorted(set(fund_ret.keys()) & set(etf_ret.keys()))
    
    if len(common) < 5:
        print(f'  {code} {name} -> {etf}: only {len(common)} days, SKIP')
        continue
    
    y = np.array([fund_ret[d][0] for d in common])
    x = np.array([etf_ret[d][0] for d in common])
    
    n = len(y)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    abs_err = np.abs(y - x)
    mae = float(np.mean(abs_err) * 100)
    max_err = float(np.max(abs_err) * 100)
    
    tag = 'OK' if max_err < 2 and r2 > 0.7 else ('WARN' if r2 > 0.5 else 'BAD')
    
    period = f'{common[0]}~{common[-1]}'
    r2_val = round(float(r2), 4)
    max_err_val = round(max_err, 4)
    
    all_results[code] = {
        'r2': r2_val,
        'mae': round(mae, 4),
        'maxErr': max_err_val,
        'samplePeriod': period
    }
    
    print(f'  {code} {name:<10} -> {etf:<5} N={n:>2} R2={r2_val:.4f} MAE={mae:.4f}% MaxErr={max_err_val:.4f}% {tag}')

# Save results
os.makedirs(BACKTEST_DIR, exist_ok=True)
out_path = os.path.join(BACKTEST_DIR, 'a_results.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print()
print(f'结果已保存: {out_path}')
print(f'共 {len(all_results)} 只基金完成回测')