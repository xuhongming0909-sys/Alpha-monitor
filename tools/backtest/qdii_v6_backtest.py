# AI-SUMMARY: QDII v6回测脚本（日期对齐版）
# 对应 INDEX.md §9.3 文件摘要索引
# -*- coding: utf-8 -*-
"""QDII LOF v6 backtest - date-aligned, ~40 trading days
Alignment rule: keep date D only when fund_prev_date == etf_prev_date
This ensures both returns cover the exact same calendar period.
"""
import os, sys, json, time
from datetime import datetime
import requests
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': None, 'https': None}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

PROXY = 'http://127.0.0.1:7890'
START, END = '2026-03-10', '2026-05-26'
_cache = {}

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

def get_prices(ticker):
    if ticker in _cache: return _cache[ticker]
    old_h, old_s = os.environ.get('HTTP_PROXY'), os.environ.get('HTTPS_PROXY')
    try:
        os.environ['HTTP_PROXY'] = PROXY
        os.environ['HTTPS_PROXY'] = PROXY
        import yfinance as yf
        h = yf.Ticker(ticker).history(start=START, end=END)
    finally:
        if old_h: os.environ['HTTP_PROXY'] = old_h
        else: os.environ.pop('HTTP_PROXY', None)
        if old_s: os.environ['HTTPS_PROXY'] = old_s
        else: os.environ.pop('HTTPS_PROXY', None)
    if h.empty: return {}
    result = {idx.strftime('%Y-%m-%d'): float(row['Close']) for idx, row in h.iterrows()}
    _cache[ticker] = result
    return result

def daily_ret_with_prev(prices):
    """Return {D: (ret, prev_date)} where ret = prices[D]/prices[prev]-1
    prev is the immediately preceding date in the sorted series."""
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i-1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret

def backtest(code, label, est_weights):
    nav = get_nav_all(code)
    fund_ret = daily_ret_with_prev(nav)

    total_w = sum(est_weights.values())
    ticker_rets = {}
    for ticker, w in est_weights.items():
        p = get_prices(ticker)
        if not p: continue
        ticker_rets[ticker] = (daily_ret_with_prev(p), w / total_w)

    if not ticker_rets: return None

    # Align: keep D only when ALL tickers have data on D AND fund_prev == etf_prev
    common = set(fund_ret.keys())
    for tr, _ in ticker_rets.values():
        common &= set(tr.keys())

    # Filter by prev_date match
    aligned = []
    for d in sorted(common):
        fund_prev = fund_ret[d][1]
        all_match = all(tr[d][1] == fund_prev for tr, _ in ticker_rets.values())
        if all_match:
            aligned.append(d)

    if len(aligned) < 10:
        print(f"  [WARN] {code} aligned days={len(aligned)}, too few")
        return None

    y = np.array([fund_ret[d][0] for d in aligned])
    x = np.array([sum(tr[d][0] * w for tr, w in ticker_rets.values()) for d in aligned])

    n = len(y)
    ss_res = np.sum((y - x) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    beta = np.dot(x, y) / np.dot(x, x) if np.dot(x, x) > 0 else 0

    abs_err = np.abs(y - x)
    mae = np.mean(abs_err) * 100
    max_err = np.max(abs_err) * 100
    over05 = int(np.sum(abs_err > 0.005))
    dir_ok = sum(1 for a, b in zip(y, x) if (a > 0 and b > 0) or (a < 0 and b < 0))
    dir_pct = dir_ok / n * 100
    tag = 'OK' if max_err < 0.5 and over05 == 0 else ('WARN' if over05 <= 3 else 'BAD')

    # Show excluded days
    excluded = len(common) - len(aligned)
    print(f"  {code} {label}: common={len(common)} aligned={len(aligned)} excluded_holiday_mismatch={excluded}")

    return {'code': code, 'label': label, 'n': n, 'r2': r2, 'beta': beta,
            'mae': mae, 'max_err': max_err, 'over05': over05, 'dir': dir_pct, 'tag': tag}

def hk(raw):
    return raw.lstrip('0').zfill(4) + '.HK'

def load_holdings():
    with open(r'C:\Users\93724\Desktop\qdii_holdings.json', 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == '__main__':
    print(f"QDII LOF v6 backtest | {START}~{END} | date-aligned")
    print(f"Rule: keep D only when fund_prev_date == etf_prev_date (same calendar period)")
    print()
    holdings = load_holdings()
    results = []
    names = {
        '161130':'??100','161125':'??500','161126':'????','161127':'????',
        '162415':'????','160140':'REIT??','501300':'???','164824':'????',
        '501312':'????','161128':'??????','164906':'????',
        '501225':'????','160125':'????','160644':'????',
    }

    def run(code, weights, label):
        print(f"  {code} {names.get(code,'')} -> {label} ...", end=' ', flush=True)
        r = backtest(code, label, weights)
        if r:
            results.append(r)
            print(f"OK N={r['n']}")
        else:
            print("FAIL")
        return r

    # A: single ETF
    for code, etf in [('161130','QQQ'),('161125','SPY'),('161126','RSPH'),('161127','XBI'),
                       ('162415','XLY'),('160140','VNQ'),('501300','AGG'),('164824','INDA')]:
        run(code, {etf: 1.0}, etf)

    # 501312: FOF holdings
    run('501312', {'ARKK':18.74,'ARKG':15.35,'ARKQ':11.59,'SOXX':9.51,
        'AIQ':7.85,'QQQ':7.45,'BOTZ':7.44,'XLK':6.44,'SMH':4.29,'FINX':1.20}, 'FOF-10')

    # Holdings-based
    for code in ['161128','164906','160125','160644']:
        h = holdings.get(code, [])
        w = {}
        for item in h:
            mkt = item.get('mkt', 'US')
            if mkt == 'HK': w[hk(item['code'])] = item['ratio']
            elif mkt == 'US': w[item['code']] = item['ratio']
        if w:
            run(code, w, f'Top10({len(w)})')

    # 501225: SMH
    run('501225', {'SMH': 1.0}, 'SMH')

    # Summary
    print(f"\n{'='*120}")
    print(f"{'code':<8}{'name':<10}{'method':<20}{'N':>3}{'R2':>8}{'beta':>8}{'MAE%':>8}{'dir%':>7}{'MaxErr%':>9}{'>0.5%':>6}{'tag':>5}")
    print('-'*120)
    for r in results:
        print(f"{r['code']:<8}{names.get(r['code'],''):<10}{r['label']:<20}{r['n']:>3}{r['r2']:>8.4f}{r['beta']:>8.4f}{r['mae']:>8.4f}{r['dir']:>7.1f}{r['max_err']:>9.4f}{r['over05']:>6}{r['tag']:>5}")
    print(f"\nDone. {datetime.now():%Y-%m-%d %H:%M:%S}")