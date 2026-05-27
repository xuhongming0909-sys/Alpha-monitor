# -*- coding: utf-8 -*-
# AI-SUMMARY: QDII LOF A类指数法回测，全部使用国内API（东财NAV + akshare美股ETF）
# 对应 INDEX.md §9.3 文件摘要索引
"""A类回测 - 基金净值日收益率 vs ETF日收益率，计算R2/MAE/MaxErr"""
import os, sys, json, time, numpy as np
sys.stdout.reconfigure(encoding='utf-8')

BACKTEST_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest'))

# ============================================================
# 数据获取：全部国内API
# ============================================================

# 基金净值 - 东财 lsjz API
import requests
NAV_SESSION = requests.Session()
NAV_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://fundf10.eastmoney.com/',
})


def get_nav_all(code, pages=3):
    """基金净值 - 东财 lsjz API"""
    nav = {}
    for p in range(1, pages + 1):
        url = f'http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={p}&pageSize=20&callback='
        try:
            r = NAV_SESSION.get(url, timeout=10)
            items = r.json()['Data']['LSJZList']
            if not items:
                break
            for i in items:
                nav[i['FSRQ']] = float(i['DWJZ'])
        except Exception as e:
            print(f'  {code} page {p}: {e}')
            break
    return nav


# ETF价格 - 东财 secid 反查 + akshare stock_us_hist
_secid_cache = {}


def _resolve_secid(ticker):
    """通过 stock_us_spot_em 反查secid"""
    if ticker in _secid_cache:
        return _secid_cache[ticker]
    import akshare as ak
    try:
        df = ak.stock_us_spot_em()
        for _, row in df.iterrows():
            code = str(row.get('代码', ''))
            if '.' in code:
                parts = code.split('.', 1)
                sym = parts[1].upper()
                if sym == ticker:
                    _secid_cache[ticker] = code
                    return code
    except Exception as e:
        print(f'  secid反查 {ticker} 失败: {e}')
    _secid_cache[ticker] = None
    return None


def get_etf_prices(ticker):
    """ETF价格 - akshare stock_us_hist (东财数据源)"""
    secid = _resolve_secid(ticker)
    if not secid:
        print(f'  {ticker}: 无secid映射')
        return {}
    import akshare as ak
    try:
        df = ak.stock_us_hist(
            symbol=secid, period="daily",
            start_date='20260101', end_date='20261231',
            adjust=""
        )
        if df is None or df.empty:
            return {}
        return {str(row['日期']): float(row['收盘']) for _, row in df.iterrows()}
    except Exception as e:
        print(f'  {ticker} ({secid}): {e}')
        return {}


# ============================================================
# 回测逻辑
# ============================================================

def daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


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

# 先预加载所有ETF价格（去重）
etf_tickers = sorted(set(etf for _, etf in A_FUNDS.values()))
print(f'预加载 {len(etf_tickers)} 个ETF价格...')
all_etf = {}
for t in etf_tickers:
    all_etf[t] = get_etf_prices(t)
    time.sleep(0.3)

print(f'\nA类回测 | 2026-03-01 ~ 2026-05-26 | {len(A_FUNDS)}只')
print('=' * 90)

all_results = {}
for code in sorted(A_FUNDS.keys()):
    name, etf = A_FUNDS[code]
    fund_nav = get_nav_all(code)
    fund_ret = daily_ret(fund_nav)
    etf_prices = all_etf.get(etf, {})
    etf_ret = daily_ret(etf_prices)

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

    all_results[code] = {
        'r2': r2_val,
        'mae': round(mae, 4),
        'maxErr': round(max_err, 4),
        'samplePeriod': period
    }
    print(f'  {code} {name:<10} -> {etf:<5} N={n:>2} R2={r2_val:.4f} MAE={mae:.4f}% MaxErr={max_err:.4f}% {tag}')

os.makedirs(BACKTEST_DIR, exist_ok=True)
out_path = os.path.join(BACKTEST_DIR, 'a_results.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)

print(f'\n结果已保存: {out_path}')
print(f'共 {len(all_results)} 只基金完成回测')