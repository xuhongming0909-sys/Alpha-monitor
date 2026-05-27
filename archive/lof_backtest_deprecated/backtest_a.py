import os, sys, json, requests, numpy as np
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': None, 'https': None}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

PROXY = 'http://127.0.0.1:7890'
_cache = {}

def yf_prices(ticker):
    if ticker in _cache: return _cache[ticker]
    old_h, old_s = os.environ.get('HTTP_PROXY'), os.environ.get('HTTPS_PROXY')
    try:
        os.environ['HTTP_PROXY'] = PROXY
        os.environ['HTTPS_PROXY'] = PROXY
        import yfinance as yf
        h = yf.Ticker(ticker).history(start='2026-03-10', end='2026-05-26')
    finally:
        if old_h: os.environ['HTTP_PROXY'] = old_h
        else: os.environ.pop('HTTP_PROXY', None)
        if old_s: os.environ['HTTPS_PROXY'] = old_s
        else: os.environ.pop('HTTPS_PROXY', None)
    if h.empty: return {}
    result = {idx.strftime('%Y-%m-%d'): float(row['Close']) for idx, row in h.iterrows()}
    _cache[ticker] = result
    return result

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

names = {
    '161130':'纳指100','161125':'标普500','161126':'标普医疗','161127':'标普生物',
    '162415':'美国消费','160140':'REIT精选','501300':'美元债','164824':'印度基金',
    '161128':'标普信息科技','501225':'全球芯片',
}

etf_map = {
    '161130':'QQQ','161125':'SPY','161126':'RSPH','161127':'XBI',
    '162415':'XLY','160140':'VNQ','501300':'AGG','164824':'INDA',
    '161128':'VGT','501225':'SMH',
}

print("=" * 90)
print("A类: 指数/ETF估值 (10只)")
print("公式: est_ret = etf_ret (不做仓位修正)")
print("区间: 2026-03-10 ~ 2026-05-26, 对齐: fund_prev == etf_prev")
print("=" * 90)

all_results = []

for code in sorted(etf_map.keys()):
    etf = etf_map[code]
    name = names[code]
    
    fund_nav = get_nav_all(code)
    fund_ret = daily_ret_with_prev(fund_nav)
    etf_prices = yf_prices(etf)
    etf_ret = daily_ret_with_prev(etf_prices)
    
    common = sorted(set(fund_ret.keys()) & set(etf_ret.keys()))
    aligned = [d for d in common if etf_ret[d][1] == fund_ret[d][1]]
    
    if len(aligned) < 10:
        print(f"  {code} {name} -> {etf}: only {len(aligned)} days, SKIP")
        continue
    
    y = np.array([fund_ret[d][0] for d in aligned])
    x = np.array([etf_ret[d][0] for d in aligned])
    
    n = len(y)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    
    abs_err = np.abs(y - x)
    mae = np.mean(abs_err) * 100
    max_err = np.max(abs_err) * 100
    over05 = int(np.sum(abs_err > 0.005))
    dir_ok = sum(1 for a, b in zip(y, x) if (a > 0 and b > 0) or (a < 0 and b < 0))
    dir_pct = dir_ok / n * 100
    tag = 'OK' if max_err < 0.5 and over05 == 0 else ('WARN' if over05 <= 3 else 'BAD')
    
    print(f"\n  {code} {name} -> {etf} (N={n})")
    print(f"  {'date':<12} {'actual%':>10} {'est%':>10} {'err%':>10} dir")
    print(f"  {'-'*50}")
    for i, d in enumerate(aligned):
        dir_mark = "OK" if (y[i]>0 and x[i]>0) or (y[i]<0 and x[i]<0) else "X"
        print(f"  {d:<12} {y[i]*100:>+10.4f} {x[i]*100:>+10.4f} {(y[i]-x[i])*100:>+10.4f} {dir_mark}")
    
    print(f"  R2={r2:.4f} MAE={mae:.4f}% MaxErr={max_err:.4f}% >0.5%={over05} dir={dir_pct:.1f}% {tag}")
    
    all_results.append({'code': code, 'name': name, 'label': etf, 'n': n,
                        'r2': r2, 'mae': mae, 'max_err': max_err,
                        'over05': over05, 'dir': dir_pct, 'tag': tag, 'sr': '-'})

# Summary
print(f"\n{'=' * 110}")
print("A类汇总")
print(f"{'=' * 110}")
print(f"{'code':<8} {'name':<10} {'ETF':<8} {'N':>3} {'R2':>8} {'MAE%':>8} {'MaxErr%':>9} {'>0.5%':>6} {'dir%':>7} {'tag':>5}")
print("-" * 110)
for r in all_results:
    print(f"{r['code']:<8} {r['name']:<10} {r['label']:<8} {r['n']:>3} {r['r2']:>8.4f} {r['mae']:>8.4f} {r['max_err']:>9.4f} {r['over05']:>6} {r['dir']:>6.1f}% {r['tag']:>5}")

print(f"\nDone. {__import__('datetime').datetime.now():%Y-%m-%d %H:%M:%S}")