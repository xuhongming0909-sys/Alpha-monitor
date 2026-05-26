# AI-SUMMARY: LOF 13只B类T10持仓法回测脚本
# 对应 INDEX.md §9.3 文件摘要索引
# -*- coding: utf-8 -*-
"""LOF 13只 B类T10持仓法回测 - 覆盖有持仓的FOF基金"""
import os, sys, json, re, time, requests, numpy as np
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

START = '2026-03-10'
END = '2026-05-26'
BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE, 'lof13_nav.json'), encoding='utf-8') as f:
    ALL_NAV = json.load(f)

_tencent_cache = {}
_em_cache = {}


def em_us_kline(ticker):
    if ticker in _em_cache:
        return _em_cache[ticker]
    url = f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=107.{ticker}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58&klt=101&fqt=1&beg=20260301&end=20260527'
    try:
        r = SESSION.get(url, timeout=15)
        data = r.json()
        klines = (data.get('data') or {}).get('klines', [])
        result = {k.split(',')[0]: float(k.split(',')[2]) for k in klines}
        _em_cache[ticker] = result
        return result
    except Exception as e:
        print(f'  em_us {ticker}: {e}')
    _em_cache[ticker] = {}
    return {}


def tencent_kline(tc_ticker):
    if tc_ticker in _tencent_cache:
        return _tencent_cache[tc_ticker]
    url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={tc_ticker},day,,,100,'
    try:
        r = SESSION.get(url, timeout=10)
        data = r.json()
        klines = data['data'].get(tc_ticker, {}).get('day', [])
        if klines:
            result = {k[0]: float(k[2]) for k in klines if k[0] >= '2026-03-01'}
            _tencent_cache[tc_ticker] = result
            return result
    except:
        pass
    _tencent_cache[tc_ticker] = {}
    return {}


def get_price(code, mkt):
    if mkt == 'HK':
        return tencent_kline(f'hk{code}')
    return em_us_kline(code)


def daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


def fetch_holdings(code, year=2025, month=12):
    url = f'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year={year}&month={month}'
    try:
        r = SESSION.get(url, timeout=15)
        m = re.search(r'content:"(.*?)",arryear', r.text, re.DOTALL)
        if not m:
            return []
        html = m.group(1)
        rows = re.findall(
            r'<tr><td>(\d+)</td>.*?<a href=[^>]+>([A-Z0-9]+)</a>.*?<a href=[^>]+>([^<]+)</a>.*?<td[^>]*>([\d.]+)%</td>',
            html, re.DOTALL
        )
        result = []
        for seq, stk_code, stk_name, pct in rows:
            if int(seq) > 10:
                continue
            mkt = 'HK' if stk_code.isdigit() else 'US'
            result.append({'code': stk_code, 'name': stk_name, 'ratio': float(pct), 'mkt': mkt})
        return result
    except:
        pass
    return []


def get_stock_ratio(code):
    url = f'http://fund.eastmoney.com/pingzhongdata/{code}.js'
    try:
        r = SESSION.get(url, timeout=15)
        m = re.search(r'var\s+Data_assetAllocation\s*=\s*(\{.*?\});', r.text, re.DOTALL)
        if not m:
            return None
        data = json.loads(m.group(1))
        for s in data.get('series', []):
            if '\u80a1\u7968' in s.get('name', ''):
                if s.get('data'):
                    v = s['data'][-1]
                    return v if v > 0 else None
    except:
        pass
    return None


def get_fx():
    import akshare as ak
    fx = {}
    for sym, key in [("\u7f8e\u5143", 'usd'), ("\u6e2f\u5e01", 'hkd')]:
        try:
            df = ak.currency_boc_sina(symbol=sym, start_date="20260301", end_date="20260526")
            for _, row in df.iterrows():
                d = str(row.iloc[0])
                if d not in fx:
                    fx[d] = {}
                fx[d][key] = float(row.iloc[4]) / 100
        except Exception as e:
            print(f'  FX {sym}: {e}')
    return fx


def backtest_t10(code, name, holdings, stock_ratio, fx_data):
    nav = ALL_NAV.get(code, {})
    fund_ret = daily_ret(nav)
    if not fund_ret:
        return None

    total_w = sum(h['ratio'] for h in holdings)

    ticker_prices = {}
    for h in holdings:
        prices = get_price(h['code'], h['mkt'])
        if prices:
            ticker_prices[h['code']] = prices

    fx_dates = sorted(fx_data.keys())
    fx_ret = {}
    for i in range(1, len(fx_dates)):
        d, dp = fx_dates[i], fx_dates[i - 1]
        r = {}
        if 'usd' in fx_data.get(d, {}) and 'usd' in fx_data.get(dp, {}) and fx_data[dp]['usd'] > 0:
            r['usd'] = fx_data[d]['usd'] / fx_data[dp]['usd'] - 1
        if 'hkd' in fx_data.get(d, {}) and 'hkd' in fx_data.get(dp, {}) and fx_data[dp]['hkd'] > 0:
            r['hkd'] = fx_data[d]['hkd'] / fx_data[dp]['hkd'] - 1
        if r:
            fx_ret[d] = (r, dp)

    common = set(fund_ret.keys()) & set(fx_ret.keys())
    for h in holdings:
        tp = ticker_prices.get(h['code'], {})
        common &= set(tp.keys())

    aligned = []
    for d in sorted(common):
        fp = fund_ret[d][1]
        fp_fx = fx_ret[d][1]
        if fp != fp_fx:
            continue
        ok = True
        for h in holdings:
            tp = ticker_prices.get(h['code'], {})
            tp_dates = sorted(tp.keys())
            idx = tp_dates.index(d)
            if idx > 0 and tp_dates[idx - 1] != fp:
                ok = False
                break
        if ok:
            aligned.append(d)

    if len(aligned) < 10:
        return None

    y = np.array([fund_ret[d][0] for d in aligned])
    x_vals = []
    for d in aligned:
        wr = 0
        for h in holdings:
            tp = ticker_prices.get(h['code'], {})
            tp_dates = sorted(tp.keys())
            idx = tp_dates.index(d)
            prev = tp_dates[idx - 1]
            local_ret = tp[d] / tp[prev] - 1
            fx_key = 'usd' if h['mkt'] == 'US' else 'hkd'
            fx_r = fx_ret[d][0].get(fx_key, 0)
            wr += h['ratio'] / total_w * local_ret * (1 + fx_r)
        x_vals.append((stock_ratio / 100) * wr)
    x = np.array(x_vals)

    n = len(y)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    beta = np.dot(x, y) / np.dot(x, x) if np.dot(x, x) > 0 else 0

    abs_err = np.abs(y - x)
    mae = np.mean(abs_err) * 100
    max_err = np.max(abs_err) * 100
    over05 = int(np.sum(abs_err > 0.005))
    over03 = int(np.sum(abs_err > 0.003))
    dir_ok = sum(1 for a, b in zip(y, x) if (a > 0 and b > 0) or (a < 0 and b < 0))
    dir_pct = dir_ok / n * 100
    tag = 'OK' if max_err < 0.5 and over05 == 0 else ('WARN' if over05 <= 3 else 'BAD')

    return {
        'code': code, 'name': name, 'label': f'T10({len(holdings)})',
        'n': n, 'r2': round(r2, 4), 'beta': round(beta, 4),
        'mae': round(mae, 4), 'max_err': round(max_err, 4),
        'over05': over05, 'over03': over03, 'dir': round(dir_pct, 1),
        'tag': tag, 'total_w': round(total_w, 2), 'stock_ratio': stock_ratio,
    }


if __name__ == '__main__':
    print(f'LOF 13 B-T10 backtest | {START} ~ {END}')
    print()

    print('Fetching FX...')
    fx_data = get_fx()
    print(f'FX: {len(fx_data)} days')

    target_funds = {
        '160216': '国泰商品', '163208': '诺安油气', '161815': '银华抗通胀',
        '165513': '中信保诚商品', '161129': '易方达原油', '501018': '南方原油',
    }

    all_results = []
    print()
    print('=' * 90)
    print('B-T10 holdings backtest')
    print('=' * 90)

    for code, name in target_funds.items():
        print(f'\n--- {code} {name} ---')
        holdings = None
        for y, m in [(2025, 12), (2024, 12), (2024, 9), (2024, 6)]:
            h = fetch_holdings(code, year=y, month=m)
            if h:
                holdings = h
                print(f'  Found {len(h)} holdings from {y}Q{m//3+1}')
                break
        if not holdings:
            print(f'  No holdings, SKIP')
            continue

        sr = get_stock_ratio(code)
        sr_val = sr if sr else 90.0
        total_w = sum(h['ratio'] for h in holdings)

        print(f'  Top5: {", ".join(f"{h["code"]}" + "(" + str(h["ratio"]) + "%)" for h in holdings[:5])}')
        print(f'  total_w={total_w:.2f}%, stock_ratio={sr_val:.1f}%')

        r = backtest_t10(code, name, holdings, sr_val, fx_data)
        if r:
            all_results.append(r)
            print(f'  => N={r["n"]} R2={r["r2"]:.4f} MAE={r["mae"]:.4f}% MaxErr={r["max_err"]:.4f}% {r["tag"]}')
        else:
            print(f'  => FAILED')

    if all_results:
        print()
        print('=' * 110)
        print(f'{"code":<8}{"name":<12}{"method":<15}{"N":>3}{"R2":>8}{"beta":>8}{"MAE%":>8}{"dir%":>7}{"maxErr%":>9}{">0.5%":>6}{">0.3%":>6}{"tag":>5}')
        print('-' * 110)
        for r in all_results:
            print(f"{r['code']:<8}{r['name']:<12}{r['label']:<15}{r['n']:>3}{r['r2']:>8.4f}{r['beta']:>8.4f}{r['mae']:>8.4f}{r['dir']:>7.1f}{r['max_err']:>9.4f}{r['over05']:>6}{r['over03']:>6}{r['tag']:>5}")

    print(f"\nDone. {__import__('datetime').datetime.now():%Y-%m-%d %H:%M:%S}")