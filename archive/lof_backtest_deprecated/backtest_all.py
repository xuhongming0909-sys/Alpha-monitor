# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF 27只基金统一回测，计算R²并分级标记
# 对应 INDEX.md §9.3 文件摘要索引
"""LOF回测 - A类(ETF跟踪) + B类(T10持仓)"""

import os, sys, json, requests, re, time
import numpy as np
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

SESSION = requests.Session()
SESSION.trust_env = False
SESSION.proxies = {'http': None, 'https': None}
SESSION.headers.update({'User-Agent': 'Mozilla/5.0', 'Referer': 'https://fundf10.eastmoney.com/'})

DB_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'lof_db', 'lof.db'))

import sqlite3
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# 27只目标基金
# ============================================================
TARGET_FUNDS = {
    '163208': '全球油气能源LOF',
    '161815': '银华抗通胀LOF',
    '162719': '广发石油LOF',
    '162411': '华宝油气LOF',
    '160416': '华安石油LOF',
    '160719': '嘉实黄金LOF',
    '164701': '汇添富黄金LOF',
    '160723': '嘉实原油LOF',
    '161129': '易方达原油LOF',
    '160216': '国泰商品LOF',
    '161116': '易方达黄金LOF',
    '165513': '中信保诚商品LOF',
    '501018': '南方原油LOF',
    '162415': '美国消费LOF',
    '501300': '美国国债LOF',
    '161127': '标普生物科技LOF',
    '164824': '印度基金LOF',
    '160125': '南方香港LOF',
    '164906': '中概互联网LOF',
    '160140': '美国REIT精选LOF',
    '161126': '标普医疗保健LOF',
    '501312': '海外科技LOF',
    '160644': '港美互联网LOF',
    '161128': '标普信息科技LOF',
    '161130': '纳斯达克100LOF',
    '161125': '标普500LOF',
    '501225': '全球芯片LOF',
}


# ============================================================
# 数据获取
# ============================================================

def get_nav_series(code):
    conn = get_db()
    rows = conn.execute('SELECT date, nav FROM fund_nav WHERE code=? ORDER BY date', (code,)).fetchall()
    conn.close()
    return {r['date']: r['nav'] for r in rows}


def get_fx_from_db():
    conn = get_db()
    rows = conn.execute('SELECT currency, date, rate FROM fx_rates ORDER BY date').fetchall()
    conn.close()
    fx = {}
    for r in rows:
        d = r['date']
        if d not in fx:
            fx[d] = {}
        fx[d][r['currency']] = r['rate']
    return fx


def daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i-1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


_tc_cache = {}

def tencent_kline_raw(tc_code, start='2026-03-01'):
    if tc_code in _tc_cache:
        return _tc_cache[tc_code]
    try:
        url = f'http://web.ifzq.gtimg.cn/appstock/app/kline/kline?param={tc_code},day,,,120,'
        data = SESSION.get(url, timeout=10).json()
        klines = data.get('data', {}).get(tc_code, {}).get('day', [])
        if not klines:
            for k in data.get('data', {}):
                if k != 'qt' and isinstance(data['data'][k], dict):
                    klines = data['data'][k].get('day', [])
                    if klines:
                        break
        result = {k[0]: float(k[2]) for k in klines if k[0] >= start}
        _tc_cache[tc_code] = result
        return result
    except:
        _tc_cache[tc_code] = {}
        return {}


def akshare_us_stock(ticker, start='2026-03-01'):
    """akshare获取美股个股K线"""
    try:
        import akshare as ak
        df = ak.stock_us_daily(symbol=ticker, adjust='')
        prices = {}
        for _, row in df.iterrows():
            d = str(row['date'])[:10]
            if d >= start:
                prices[d] = float(row['close'])
        return prices
    except:
        return {}


def akshare_etf(ticker, start='2026-03-01'):
    try:
        import akshare as ak
        df = ak.stock_us_daily(symbol=ticker, adjust='')
        prices = {}
        for _, row in df.iterrows():
            d = str(row['date'])[:10]
            if d >= start:
                prices[d] = float(row['close'])
        return prices
    except:
        return {}


def tencent_etf(ticker, start='2026-03-01'):
    for suffix in ['.OQ', '.N', '']:
        r = tencent_kline_raw(f'us{ticker}{suffix}', start)
        if len(r) >= 5:
            return r
    return tencent_kline_raw(f'hk{ticker}', start)


def get_etf_series(ticker):
    conn = get_db()
    rows = conn.execute('SELECT date, close FROM etf_prices WHERE ticker=? ORDER BY date', (ticker,)).fetchall()
    conn.close()
    db_data = {r['date']: r['close'] for r in rows}
    if len(db_data) >= 20:
        return db_data
    online = tencent_etf(ticker)
    if len(online) >= 10:
        return online
    ak_data = akshare_etf(ticker)
    if len(ak_data) >= 10:
        return ak_data
    return db_data if db_data else online


def get_stock_ratio(code):
    url = f'http://fund.eastmoney.com/pingzhongdata/{code}.js'
    r = SESSION.get(url, timeout=15)
    m = re.search(r'var\s+Data_assetAllocation\s*=\s*(\{.*?\});', r.text, re.DOTALL)
    if not m:
        return None
    data = json.loads(m.group(1))
    for s in data.get('series', []):
        if '股票' in s.get('name', ''):
            if s.get('data'):
                return s['data'][-1] if s['data'][-1] > 0 else None
    return None


def fetch_holdings_online(code, year=2026, month=3):
    url = f'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year={year}&month={month}'
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
        tc_ticker = f'hk{stk_code}' if mkt == 'HK' else f'us{stk_code}'
        result.append({'code': stk_code, 'name': stk_name, 'ratio': float(pct),
                       'mkt': mkt, 'tc_ticker': tc_ticker})
    return result


def get_holdings_from_db(code):
    conn = get_db()
    rows = conn.execute(
        'SELECT ticker, weight, market FROM holdings WHERE code=? '
        'ORDER BY report_date DESC, weight DESC LIMIT 10',
        (code,)
    ).fetchall()
    conn.close()
    if not rows:
        return []
    result = []
    for r in rows:
        mkt = r['market'] or 'US'
        tc_ticker = f'hk{r["ticker"]}' if mkt == 'HK' else f'us{r["ticker"]}'
        result.append({'code': r['ticker'], 'ratio': r['weight'], 'mkt': mkt, 'tc_ticker': tc_ticker})
    return result


# ============================================================
# 回测核心
# ============================================================

def calc_metrics(y, x):
    n = len(y)
    if n < 5:
        return None
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    abs_err = np.abs(y - x)
    mae = float(np.mean(abs_err)) * 100
    max_err = float(np.max(abs_err)) * 100
    over05 = int(np.sum(abs_err > 0.005))
    dir_ok = int(np.sum(((y > 0) & (x > 0)) | ((y < 0) & (x < 0))))
    dir_pct = dir_ok / n * 100
    return {
        'n': n, 'r2': round(float(r2), 4),
        'mae': round(mae, 4), 'max_err': round(max_err, 4),
        'over05': over05, 'dir': round(dir_pct, 1),
    }


def classify_r2(r2):
    if r2 >= 0.9:
        return 'OK'
    elif r2 >= 0.8:
        return 'WARN'
    else:
        return 'BAD'


def backtest_a_fund(code, name, etf_ticker, currency, fx_ret):
    nav = get_nav_series(code)
    if len(nav) < 10:
        return None
    fund_ret = daily_ret(nav)

    etf_prices = get_etf_series(etf_ticker)
    if len(etf_prices) < 10:
        return None
    etf_ret = daily_ret(etf_prices)

    common = set(fund_ret.keys()) & set(etf_ret.keys()) & set(fx_ret.keys())
    aligned = sorted(common)
    if len(aligned) < 5:
        return None

    y_list, x_list = [], []
    for d in aligned:
        actual = fund_ret[d][0]
        er = etf_ret[d][0]
        fr = fx_ret[d][0]
        fx_key = currency.lower()
        if fx_key not in fr:
            fx_key = 'usd'
        fx_v = fr.get(fx_key, 0)
        est = er * (1 + fx_v)
        y_list.append(actual)
        x_list.append(est)

    y = np.array(y_list)
    x = np.array(x_list)
    m = calc_metrics(y, x)
    if m:
        m['code'] = code
        m['name'] = name
        m['etf'] = etf_ticker
        m['type'] = 'A'
        m['sample'] = f"{aligned[0]}~{aligned[-1]}"
        m['tag'] = classify_r2(m['r2'])
    return m


def backtest_b_fund(code, name, currency, fx_ret):
    holdings = get_holdings_from_db(code)
    if len(holdings) < 5:
        holdings = fetch_holdings_online(code)
    if len(holdings) < 3:
        return None

    total_w = sum(h['ratio'] for h in holdings)
    sr = get_stock_ratio(code)

    nav = get_nav_series(code)
    if len(nav) < 10:
        return None
    fund_ret = daily_ret(nav)

    ticker_prices = {}
    for h in holdings:
        # 港股走腾讯，美股走akshare
        if h['mkt'] == 'HK':
            tp = tencent_kline_raw(h['tc_ticker'])
        else:
            tp = akshare_us_stock(h['code'])
            if len(tp) < 10:
                tp = tencent_kline_raw(h['tc_ticker'])
        if tp:
            ticker_prices[h['tc_ticker']] = tp

    common = set(fund_ret.keys()) & set(fx_ret.keys())
    for h in holdings:
        tp = ticker_prices.get(h['tc_ticker'], {})
        common &= set(tp.keys())

    aligned = []
    for d in sorted(common):
        fp = fund_ret[d][1]
        ok = True
        for h in holdings:
            tp = ticker_prices.get(h['tc_ticker'], {})
            if d not in tp or fp not in tp:
                ok = False
                break
        if not ok:
            continue
        if fx_ret[d][1] != fp:
            continue
        aligned.append(d)

    if len(aligned) < 5:
        return None

    y_list, x_list = [], []
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

    y = np.array(y_list)
    x = np.array(x_list)
    m = calc_metrics(y, x)
    if m:
        m['code'] = code
        m['name'] = name
        m['etf'] = f'T10({len(holdings)})'
        m['type'] = 'B'
        m['sample'] = f"{aligned[0]}~{aligned[-1]}"
        m['tag'] = classify_r2(m['r2'])
    return m


# ============================================================
# 主流程
# ============================================================

def main():
    print('加载汇率...')
    fx_data = get_fx_from_db()
    for d in list(fx_data.keys()):
        fx_data[d] = {k: v for k, v in fx_data[d].items() if v is not None}
    fx_ret = {}
    fx_dates = sorted(fx_data.keys())
    for i in range(1, len(fx_dates)):
        d, dp = fx_dates[i], fx_dates[i-1]
        r = {}
        for k in ['usd', 'hkd']:
            vd = fx_data[d].get(k)
            vdp = fx_data[dp].get(k)
            if vd is not None and vdp is not None and vdp > 0:
                r[k] = vd / vdp - 1
        if r:
            fx_ret[d] = (r, dp)
    print(f'汇率: {len(fx_ret)} 天')

    # 从DB读取基金元数据
    conn = get_db()
    funds = conn.execute('SELECT code, name, estimation, etf, currency FROM funds').fetchall()
    conn.close()
    fund_map = {f['code']: f for f in funds}

    results = []
    errors = []

    for i, (code, name) in enumerate(TARGET_FUNDS.items()):
        f = fund_map.get(code)
        if not f:
            errors.append(f'{code} {name}: 不在DB中')
            continue
        est_type = f['estimation']
        etf = f['etf']
        ccy = f['currency'] or 'USD'

        print(f'[{i+1}/27] {code} {name} ({est_type}, etf={etf})')

        try:
            if est_type == 'A':
                if not etf:
                    errors.append(f'{code} {name}: 无ETF基准')
                    continue
                r = backtest_a_fund(code, name, etf, ccy, fx_ret)
            else:
                r = backtest_b_fund(code, name, ccy, fx_ret)

            if r:
                results.append(r)
                print(f'  R²={r["r2"]:.4f} MAE={r["mae"]:.4f}% MaxErr={r["max_err"]:.4f}% N={r["n"]} tag={r["tag"]}')
            else:
                errors.append(f'{code} {name}: 数据不足')
                print(f'  数据不足')
        except Exception as e:
            errors.append(f'{code} {name}: {e}')
            print(f'  错误: {e}')

        time.sleep(0.3)

    results.sort(key=lambda x: -x['r2'])

    # ============================================================
    # 标准输出
    # ============================================================
    ok_list = [r for r in results if r['tag'] == 'OK']
    warn_list = [r for r in results if r['tag'] == 'WARN']
    bad_list = [r for r in results if r['tag'] == 'BAD']

    print(f'\n{"="*105}')
    print(f'LOF回测结果 (27只, R²≥0.9=OK | 0.8~0.9=WARN | <0.8=BAD)')
    print(f'{"="*105}')
    print(f'{"#":>3} {"code":<8} {"name":<20} {"type":<5} {"etf":<10} {"N":>3} {"R2":>8} {"MAE%":>8} {"MaxErr%":>9} {">0.5%":>6} {"dir%":>7} {"tag":>5}')
    print('-' * 105)
    for idx, r in enumerate(results, 1):
        print(f'{idx:>3} {r["code"]:<8} {r["name"]:<20} {r["type"]:<5} {r["etf"]:<10} {r["n"]:>3} {r["r2"]:>8.4f} {r["mae"]:>8.4f} {r["max_err"]:>9.4f} {r["over05"]:>6} {r["dir"]:>6.1f}% {r["tag"]:>5}')

    print(f'\nOK: {len(ok_list)} | WARN: {len(warn_list)} | BAD: {len(bad_list)} | 失败: {len(errors)}')

    if errors:
        print(f'\n无法回测:')
        for e in errors:
            print(f'  - {e}')

    # 保存JSON
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest')
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, 'lof27_r2_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n已保存: {json_path}')


if __name__ == '__main__':
    main()
