# -*- coding: utf-8 -*-
"""A类回测 - 全国内API（腾讯K线替代Yahoo Finance）"""
import sys, json, requests, re, numpy as np
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

TC_CACHE = {}

def get_nav(code, pages=3):
    nav = {}
    for p in range(1, pages+1):
        url = f'http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={p}&pageSize=20&callback='
        items = SESSION.get(url, timeout=10).json()['Data']['LSJZList']
        if not items: break
        for i in items: nav[i['FSRQ']] = float(i['DWJZ'])
    return nav

def daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i-1]
        if prices[dp] > 0: ret[d] = (prices[d]/prices[dp]-1, dp)
    return ret

def tencent_kline(ticker):
    if ticker in TC_CACHE: return TC_CACHE[ticker]
    # US: usXXX.N, HK: hkXXXXX
    if ticker.endswith('.HK') or len(ticker) == 5:
        tc = f'hk{ticker}'
    elif '.' in ticker:
        tc = f'us{ticker.split(".")[0]}'
    elif len(ticker) <= 5 and ticker.isdigit():
        tc = f'hk{ticker}'
    else:
        tc = f'us{ticker}'
    
    try:
        url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={tc},day,,,60,'
        data = SESSION.get(url, timeout=10).json()
        klines = data['data'].get(tc, {}).get('day', [])
        result = {k[0]: float(k[2]) for k in klines if k[0] >= '2026-03-10'}
        TC_CACHE[ticker] = result
        return result
    except: pass
    
    # Fallback with suffix
    for suf in ['.O', '.N', '']:
        tc2 = f'us{ticker}{suf}'
        try:
            url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={tc2},day,,,60,'
            data = SESSION.get(url, timeout=10).json()
            klines = data['data'].get(tc2, {}).get('day', [])
            if klines:
                result = {k[0]: float(k[2]) for k in klines if k[0] >= '2026-03-10'}
                TC_CACHE[ticker] = result
                return result
        except: pass
    TC_CACHE[ticker] = {}
    return {}

def get_fx_history():
    import akshare as ak
    fx = {}
    for sym, key in [("美元", "usd"), ("港币", "hkd")]:
        try:
            df = ak.currency_boc_sina(symbol=sym, start_date="20260301", end_date="20260526")
            for _, row in df.iterrows():
                d = str(row['日期'])
                if d not in fx: fx[d] = {}
                fx[d][key] = float(row['央行中间价']) / 100
        except: pass
    return fx

# A类基金定义
A_FUNDS = {
    '501225': ('全球芯片', 'SMH'),
    '161128': ('标普信息科技', 'XLK'),
    '161130': ('纳指', 'QQQ'),
    '161125': ('标普500', 'SPY'),
    '161126': ('标普医疗', 'RSPH'),
    '161127': ('标普生物', 'XBI'),
    '162415': ('标普可选消费', 'XLY'),
    '160140': ('标普地产', 'VNQ'),
    '501300': ('美国国债', 'AGG'),
    '164824': ('工银印度', 'INDA'),
}

print('获取汇率...')
fx_data = get_fx_history()
fx_ret = {}
fx_dates = sorted(fx_data.keys())
for i in range(1, len(fx_dates)):
    d, dp = fx_dates[i], fx_dates[i-1]
    r = {}
    for k in ['usd', 'hkd']:
        if k in fx_data[d] and k in fx_data[dp] and fx_data[dp][k] > 0:
            r[k] = fx_data[d][k] / fx_data[dp][k] - 1
    if r: fx_ret[d] = (r, dp)
print(f'汇率: {len(fx_ret)} 天')

results = []
for code, (name, etf) in A_FUNDS.items():
    nav = get_nav(code)
    if len(nav) < 5: print(f'  {code} {name}: NAV不足'); continue
    fund_ret = daily_ret(nav)
    
    etf_prices = tencent_kline(etf)
    if not etf_prices: print(f'  {code} {name}: ETF {etf} 无数据'); continue
    etf_ret = daily_ret(etf_prices)
    
    common = set(fund_ret.keys()) & set(etf_ret.keys()) & set(fx_ret.keys())
    aligned = sorted(common)
    if len(aligned) < 5: print(f'  {code} {name}: 对齐不足 {len(aligned)}'); continue
    
    y_list, x_list = [], []
    for d in aligned:
        actual = fund_ret[d][0]
        er = etf_ret[d][0]
        fr = fx_ret[d][0]
        fx_key = 'usd' if code in ['501300','164824'] else 'hkd'
        if fx_key not in fr: fx_key = 'usd'
        fx_v = fr.get(fx_key, 0)
        est = er * (1 + fx_v)
        y_list.append(actual)
        x_list.append(est)
    
    y = np.array(y_list)
    x = np.array(x_list)
    ss_tot = np.sum((y - y.mean())**2)
    ss_res = np.sum((y - x)**2)
    r2 = 1 - ss_res/ss_tot if ss_tot > 0 else 0
    errors = y - x
    mae = np.mean(np.abs(errors)) * 100
    max_err = np.max(np.abs(errors)) * 100
    over05 = int(np.sum(np.abs(errors) > 0.005))
    dir_ok = int(np.sum((y>0)&(x>0)|(y<0)&(x<0)))
    tag = 'OK' if r2>=0.95 and over05<=5 else ('WARN' if r2>=0.85 else 'BAD')
    
    results.append({'code': code, 'name': name, 'etf': etf, 'n': len(aligned),
                    'r2': r2, 'mae': mae, 'max_err': max_err, 'tag': tag,
                    'sample': f"{aligned[0]}~{aligned[-1]}"})
    print(f'  {code} {name} -> {etf}: R2={r2:.4f} MAE={mae:.4f}% MaxErr={max_err:.4f}% {tag}')

print(f'\nA类汇总')
print(f"{'code':<8} {'name':<10} {'ETF':<6} {'N':>3} {'R2':>8} {'MAE%':>8} {'MaxErr%':>9} {'tag':>5}")
for r in results:
    print(f"{r['code']:<8} {r['name']:<10} {r['etf']:<6} {r['n']:>3} {r['r2']:>8.4f} {r['mae']:>8.4f} {r['max_err']:>9.4f} {r['tag']:>5}")

# Save results
with open('runtime_data/backtest/a_results.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'\nSaved to runtime_data/backtest/a_results.json')