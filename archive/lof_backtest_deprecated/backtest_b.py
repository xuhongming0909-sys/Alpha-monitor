import os, sys, json, requests, numpy as np, re, time
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': None, 'https': None}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

# ============================================================
# 数据源函数 - 全部从国内API获取
# ============================================================

def get_nav_all(code, pages=3):
    """基金净值 - 东财API"""
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

def get_stock_ratio(code):
    """股票仓位比 - 东财pingzhongdata API"""
    url = f'http://fund.eastmoney.com/pingzhongdata/{code}.js'
    r = SESSION.get(url, timeout=15)
    m = re.search(r'var\s+Data_assetAllocation\s*=\s*(\{.*?\});', r.text, re.DOTALL)
    if not m: return None
    data = json.loads(m.group(1))
    for s in data.get('series', []):
        if '股票' in s.get('name', ''):
            if s.get('data'): return s['data'][-1] if s['data'][-1] > 0 else None
    return None

def fetch_holdings(code, year=2026, month=3):
    """前十大持仓 - 东财F10 API"""
    url = f'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year={year}&month={month}'
    r = SESSION.get(url, timeout=15)
    m = re.search(r'content:"(.*?)",arryear', r.text, re.DOTALL)
    if not m: return []
    html = m.group(1)
    rows = re.findall(
        r'<tr><td>(\d+)</td>.*?<a href=[^>]+>([A-Z0-9]+)</a>.*?<a href=[^>]+>([^<]+)</a>.*?<td[^>]*>([\d.]+)%</td>',
        html, re.DOTALL
    )
    result = []
    for seq, stk_code, stk_name, pct in rows:
        if int(seq) > 10: continue
        mkt = 'HK' if stk_code.isdigit() else 'US'
        # Tencent kline ticker format
        if mkt == 'HK':
            tc_ticker = f'hk{stk_code}'
        else:
            tc_ticker = f'us{stk_code}'
        result.append({'code': stk_code, 'name': stk_name, 'ratio': float(pct),
                        'mkt': mkt, 'tc_ticker': tc_ticker})
    return result

_tencent_cache = {}
def tencent_kline(tc_ticker):
    """股票日K线 - 腾讯财经API"""
    if tc_ticker in _tencent_cache: return _tencent_cache[tc_ticker]
    # US stocks need exchange suffix for proper data
    actual_ticker = tc_ticker
    if tc_ticker.startswith('us'):
        code = tc_ticker[2:]
        # Try .OQ first (NASDAQ), then .N (NYSE)
        for suffix in ['.OQ', '.N', '']:
            test = f'us{code}{suffix}'
            url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={test},day,,,100,'
            try:
                r = SESSION.get(url, timeout=10)
                data = r.json()
                klines = data['data'].get(test, {}).get('day', [])
                if klines and len(klines) > 5:
                    actual_ticker = test
                    result = {k[0]: float(k[2]) for k in klines if k[0] >= '2026-03-10'}
                    _tencent_cache[tc_ticker] = result
                    return result
            except:
                pass
            time.sleep(0.1)
        # Fallback: no suffix
        url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={tc_ticker},day,,,100,'
        try:
            r = SESSION.get(url, timeout=10)
            data = r.json()
            klines = data['data'].get(tc_ticker, {}).get('day', [])
            result = {k[0]: float(k[2]) for k in klines if k[0] >= '2026-03-10'}
            _tencent_cache[tc_ticker] = result
            return result
        except:
            pass
    else:
        # HK stocks
        url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={tc_ticker},day,,,100,'
        try:
            r = SESSION.get(url, timeout=10)
            data = r.json()
            klines = data['data'].get(tc_ticker, {}).get('day', [])
            result = {k[0]: float(k[2]) for k in klines if k[0] >= '2026-03-10'}
            _tencent_cache[tc_ticker] = result
            return result
        except:
            pass
    _tencent_cache[tc_ticker] = {}
    return {}

def get_fx_history():
    """汇率历史 - akshare央行中间价 (中国外汇交易中心)"""
    import akshare as ak
    fx = {}
    # USD/CNY
    try:
        df_usd = ak.currency_boc_sina(symbol="美元", start_date="20260301", end_date="20260526")
        for _, row in df_usd.iterrows():
            fx[str(row['日期'])] = {'usd': float(row['央行中间价']) / 100}
    except Exception as e:
        print(f'  [!] USD FX error: {e}')
    # HKD/CNY
    try:
        df_hkd = ak.currency_boc_sina(symbol="港币", start_date="20260301", end_date="20260526")
        for _, row in df_hkd.iterrows():
            d = str(row['日期'])
            if d not in fx:
                fx[d] = {}
            fx[d]['hkd'] = float(row['央行中间价']) / 100
    except Exception as e:
        print(f'  [!] HKD FX error: {e}')
    return fx

# ============================================================
# B类基金定义
# ============================================================
B_FUNDS = {
    '160125': '南方香港',
    '160644': '港美互联',
    '164906': '中概互联',
}

output_lines = []
all_results = []

def log(s=''):
    print(s)
    output_lines.append(s)

log('=' * 95)
log('B类: 前十大持仓估值 (3只, 全部数据从国内API获取)')
log('持仓: 东财F10 API | 仓位: 东财pingzhongdata API | 净值: 东财API')
log('股价: 腾讯财经K线API | 汇率: akshare央行中间价')
log('公式: est = (stock_ratio/100) * Σ(ret_local × (1+fx) × weight) / Σ(weight)')
log('对齐: fund_prev == all tickers prev == FX date')
log('=' * 95)

# 1. Fetch FX data
print('\n获取汇率数据...')
fx_data = get_fx_history()
log(f'汇率数据: {len(fx_data)} 天')
fx_dates = sorted(fx_data.keys())
if fx_dates:
    log(f'  区间: {fx_dates[0]} ~ {fx_dates[-1]}')
    # Show a sample
    sample_d = fx_dates[0]
    fx_sample = fx_data[sample_d]
    log(f'  样例 {sample_d}: USD/CNY={fx_sample.get("usd","N/A")}, HKD/CNY={fx_sample.get("hkd","N/A")}')

# Compute FX returns
fx_ret = {}
fx_dates_sorted = sorted(fx_data.keys())
for i in range(1, len(fx_dates_sorted)):
    d, dp = fx_dates_sorted[i], fx_dates_sorted[i-1]
    r = {}
    if 'usd' in fx_data[d] and 'usd' in fx_data[dp] and fx_data[dp]['usd'] > 0:
        r['usd'] = fx_data[d]['usd'] / fx_data[dp]['usd'] - 1
    if 'hkd' in fx_data[d] and 'hkd' in fx_data[dp] and fx_data[dp]['hkd'] > 0:
        r['hkd'] = fx_data[d]['hkd'] / fx_data[dp]['hkd'] - 1
    if r:
        fx_ret[d] = (r, dp)

log(f'FX收益率: {len(fx_ret)} 天')

for code in sorted(B_FUNDS.keys()):
    name = B_FUNDS[code]

    # 2. Fetch holdings
    holdings = fetch_holdings(code)
    if not holdings:
        log(f'\n  {code} {name}: 无持仓数据')
        continue
    total_w = sum(h['ratio'] for h in holdings)

    # 3. Fetch stock_ratio
    sr = get_stock_ratio(code)
    sr_label = f'{sr:.1f}%' if sr else 'N/A'

    # 4. Fetch fund NAV
    nav = get_nav_all(code)
    if len(nav) < 3:
        log(f'\n  {code} {name}: NAV不足')
        continue
    fund_ret = daily_ret_with_prev(nav)

    # 5. Fetch all ticker prices from Tencent
    ticker_prices = {}
    for h in holdings:
        prices = tencent_kline(h['tc_ticker'])
        if prices:
            ticker_prices[h['tc_ticker']] = prices

    # 6. Alignment
    # Common dates: fund_ret ∩ all ticker prices ∩ fx_ret
    common = set(fund_ret.keys())
    common &= set(fx_ret.keys())
    for h in holdings:
        tp = ticker_prices.get(h['tc_ticker'], {})
        common &= set(tp.keys())
    if code == '160644':
        print(f'  DEBUG: fund_ret={len(fund_ret)}, fx_ret={len(fx_ret)}, ticker_prices keys={list(ticker_prices.keys())}')
        print(f'  DEBUG: common={len(common)} days, sample={sorted(common)[:5]}')
        for h in holdings:
            tp = ticker_prices.get(h['tc_ticker'], {})
            print(f'  DEBUG: {h["tc_ticker"]} -> {len(tp)} prices, dates={sorted(tp.keys())[:3]}')

    aligned = []
    for d in sorted(common):
        fp = fund_ret[d][1]
        # Check all tickers have both d and fp
        ok = True
        for h in holdings:
            tp = ticker_prices.get(h['tc_ticker'], {})
            if d not in tp or fp not in tp:
                ok = False
                break
        if not ok: continue
        # Check FX prev matches fund prev
        if fx_ret[d][1] != fp:
            continue
        aligned.append(d)

    if len(aligned) < 5:
        log(f'\n  {code} {name}: 对齐不足 ({len(aligned)})')
        continue

    # 7. Compute
    y_list, x_list = [], []
    detail_rows = []
    for d in aligned:
        actual = fund_ret[d][0]
        fp = fund_ret[d][1]
        fx_r = fx_ret[d][0]
        fx_usd = fx_r.get('usd', 0)
        fx_hkd = fx_r.get('hkd', 0)

        weighted_cny_ret = 0
        for h in holdings:
            tp = ticker_prices.get(h['tc_ticker'], {})
            if d not in tp or fp not in tp:
                continue
            local_ret = tp[d] / tp[fp] - 1
            w_norm = h['ratio'] / total_w
            if h['mkt'] == 'US':
                cny_ret = (1 + local_ret) * (1 + fx_usd) - 1
            elif h['mkt'] == 'HK':
                cny_ret = (1 + local_ret) * (1 + fx_hkd) - 1
            else:
                cny_ret = local_ret
            weighted_cny_ret += cny_ret * w_norm

        est = weighted_cny_ret
        if sr:
            est *= (sr / 100)

        y_list.append(actual)
        x_list.append(est)
        detail_rows.append((d, actual, est, fx_usd, fx_hkd))

    y = np.array(y_list)
    x = np.array(x_list)
    ss_tot = np.sum((y - y.mean())**2)
    ss_res = np.sum((y - x)**2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    errors = y - x
    mae = np.mean(np.abs(errors)) * 100
    max_err = np.max(np.abs(errors)) * 100
    over05 = int(np.sum(np.abs(errors) > 0.005))
    dir_ok = int(np.sum((y > 0) & (x > 0) | (y < 0) & (x < 0)))
    dir_pct = dir_ok / len(y) * 100
    tag = 'OK' if r2 >= 0.95 and over05 <= 5 else ('WARN' if r2 >= 0.85 else 'BAD')

    # Print
    log(f'\n  {code} {name} (stock_ratio={sr_label}, N={len(aligned)})')
    log(f'  Top10持仓 (来源: 东财F10 API):')
    log(f'  {"#":<3} {"ticker":<10} {"name":<15} {"ratio%":>7} {"mkt":>4} {"tc_ticker":<12} {"price":>4}')
    log(f'  {"-"*58}')
    for idx, h in enumerate(holdings):
        has = 'Y' if h['tc_ticker'] in ticker_prices and ticker_prices[h['tc_ticker']] else 'N'
        log(f'  {idx+1:<3} {h["code"]:<10} {h["name"]:<15} {h["ratio"]:>6.2f}% {h["mkt"]:>4} {h["tc_ticker"]:<12} {has:>4}')
    log(f'  Top10合计: {total_w:.2f}%')

    log(f'\n  {"date":<12} {"actual%":>10} {"est%":>10} {"err%":>10} {"fx_usd%":>8} {"fx_hkd%":>8} dir')
    log(f'  {"-"*68}')
    for d, actual, est, fx_u, fx_h in detail_rows:
        dm = 'OK' if (actual>0 and est>0) or (actual<0 and est<0) else 'X'
        log(f'  {d:<12} {actual*100:>+10.4f} {est*100:>+10.4f} {(actual-est)*100:>+10.4f} {fx_u*100:>+8.4f} {fx_h*100:>+8.4f} {dm}')

    log(f'  R2={r2:.4f} MAE={mae:.4f}% MaxErr={max_err:.4f}% >0.5%={over05} dir={dir_pct:.1f}% {tag}')

    all_results.append({'code': code, 'name': name, 'sr': sr, 'n': len(aligned),
                        'r2': r2, 'mae': mae, 'max_err': max_err,
                        'over05': over05, 'dir': dir_pct, 'tag': tag,
                        'total_w': total_w})

# Summary
log(f'\n{"=" * 100}')
log('B类汇总')
log(f'{"=" * 100}')
log(f'{"code":<8} {"name":<10} {"N":>3} {"ratio%":>7} {"top10%":>7} {"R2":>8} {"MAE%":>8} {"MaxErr%":>9} {">0.5%":>6} {"dir%":>7} {"tag":>5}')
log('-' * 100)
for r in all_results:
    sr_str = f"{r['sr']:.1f}" if r['sr'] else 'N/A'
    log(f"{r['code']:<8} {r['name']:<10} {r['n']:>3} {sr_str:>7} {r['total_w']:>6.2f}% {r['r2']:>8.4f} {r['mae']:>8.4f} {r['max_err']:>9.4f} {r['over05']:>6} {r['dir']:>6.1f}% {r['tag']:>5}")

log(f'\n数据源: 净值=东财API, 持仓=东财F10, 仓位=东财pingzhongdata, 股价=腾讯K线, 汇率=akshare央行中间价')
log(f'Done. {datetime.now():%Y-%m-%d %H:%M:%S}')

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qdii_backtest_B_output.txt')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))
print(f'\nSaved to {out_path}')