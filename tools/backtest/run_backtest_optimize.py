# -*- coding: utf-8 -*-
# AI-SUMMARY: A类全面回测+映射优化，尝试所有候选ETF组合，选出每只基金最优映射
# 对应 INDEX.md §9.3 文件摘要索引
"""
A类回测+映射优化：
1. 通过 stock_us_spot_em 反查所有候选ETF的secid
2. 通过 stock_us_hist 拉取历史日线
3. 对每只基金尝试所有单ETF + 双ETF组合
4. 输出最优映射方案
"""
import os, sys, json, time, itertools, numpy as np
import requests
sys.stdout.reconfigure(encoding='utf-8')

BACKTEST_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'runtime_data', 'backtest'))

# ============================================================
# 数据获取
# ============================================================

NAV_SESSION = requests.Session()
NAV_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://fundf10.eastmoney.com/',
})


def get_nav_all(code, pages=5):
    """基金净值 - 东财 lsjz API"""
    nav = {}
    for p in range(1, pages + 1):
        url = f'http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex={p}&pageSize=40&callback='
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


def resolve_all_secids():
    """通过 stock_us_spot_em 获取全部美股secid映射"""
    import akshare as ak
    print('正在获取美股列表 (stock_us_spot_em)...')
    df = ak.stock_us_spot_em()
    mapping = {}
    for _, row in df.iterrows():
        code = str(row.get('代码', ''))
        name = str(row.get('名称', ''))
        if '.' in code:
            parts = code.split('.', 1)
            secid = parts[0]
            sym = parts[1].upper()
            mapping[sym] = {'secid': code, 'name': name, 'market': secid}
    print(f'共获取 {len(mapping)} 只美股证券')
    return mapping


def fetch_etf_hist(secid, start='20260101', end='20261231'):
    """通过 akshare stock_us_hist 拉取ETF历史日线"""
    import akshare as ak
    try:
        df = ak.stock_us_hist(symbol=secid, period="daily",
                              start_date=start, end_date=end, adjust="")
        if df is None or df.empty:
            return {}
        return {str(row['日期']): float(row['收盘']) for _, row in df.iterrows()}
    except Exception as e:
        print(f'  {secid}: {e}')
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


def calc_r2_single(nav, etf_prices):
    """单ETF回测: y = x (无截距，与backtest_a.py一致)"""
    fr = daily_ret(nav)
    er = daily_ret(etf_prices)
    common = sorted(set(fr.keys()) & set(er.keys()))
    if len(common) < 10:
        return None
    y = np.array([fr[d][0] for d in common])
    x = np.array([er[d][0] for d in common])
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    ss_res = np.sum((y - x) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    abs_err = np.abs(y - x)
    mae = float(np.mean(abs_err)) * 100
    max_err = float(np.max(abs_err)) * 100
    return {
        'r2': round(r2, 4), 'mae': round(mae, 4),
        'maxErr': round(max_err, 4),
        'samples': len(common),
        'period': f'{common[0]}~{common[-1]}'
    }


def calc_r2_dual(nav, p1, p2):
    """双ETF回归: y = b1*x1 + b2*x2 (OLS)"""
    fr = daily_ret(nav)
    r1 = daily_ret(p1)
    r2 = daily_ret(p2)
    common = sorted(set(fr.keys()) & set(r1.keys()) & set(r2.keys()))
    if len(common) < 10:
        return None
    y = np.array([fr[d][0] for d in common])
    x1 = np.array([r1[d][0] for d in common])
    x2 = np.array([r2[d][0] for d in common])
    n = len(y)
    # OLS: y = b0 + b1*x1 + b2*x2
    sx1 = np.sum(x1); sx2 = np.sum(x2); sy = np.sum(y)
    sx1x1 = np.sum(x1*x1); sx2x2 = np.sum(x2*x2); sx1x2 = np.sum(x1*x2)
    sx1y = np.sum(x1*y); sx2y = np.sum(x2*y)
    A = np.array([[n, sx1, sx2], [sx1, sx1x1, sx1x2], [sx2, sx1x2, sx2x2]])
    B = np.array([sy, sx1y, sx2y])
    try:
        beta = np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        return None
    y_mean = sy / n
    ss_tot = np.sum((y - y_mean) ** 2)
    preds = beta[0] + beta[1] * x1 + beta[2] * x2
    ss_res = np.sum((y - preds) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    abs_err = np.abs(y - preds)
    mae = float(np.mean(abs_err)) * 100
    max_err = float(np.max(abs_err)) * 100
    return {
        'r2': round(r2, 4), 'mae': round(mae, 4),
        'maxErr': round(max_err, 4), 'samples': n,
        'period': f'{common[0]}~{common[-1]}',
        'b0': round(float(beta[0]), 6),
        'b1': round(float(beta[1]), 4),
        'b2': round(float(beta[2]), 4),
    }


# ============================================================
# 基金列表 + 候选ETF
# ============================================================

# 当前config映射
A_FUNDS_CURRENT = {
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

# 每只基金的候选ETF池（逻辑相关）
CANDIDATE_POOLS = {
    '161128': ['XLK', 'VGT', 'SMH', 'QQQ'],
    '501225': ['SMH', 'XLK', 'SOXX', 'PHO'],
    '161130': ['QQQ', 'NDX', 'QQQM', 'SPY'],
    '161125': ['SPY', 'IVV', 'VOO', 'VTI'],
    '161126': ['XLV', 'VHT', 'IYH', 'RSPH'],
    '161127': ['XBI', 'IBB', 'IBBQ', 'ARKK'],
    '162415': ['XLY', 'VCR', 'IYC', 'RCD'],
    '160140': ['VNQ', 'IYR', 'XLRE', 'VNQI'],
    '501300': ['AGG', 'BND', 'TLT', 'LQD', 'TIP', 'SHY'],
    '164824': ['INDA', 'SMIN', 'EEM'],
    '160416': ['XLE', 'OIH', 'IEO', 'XOP'],
    '162719': ['XOP', 'XLE', 'OIH', 'IEO'],
    '162411': ['XOP', 'XLE', 'OIH', 'IEO', 'BNO'],
    '160723': ['USO', 'BNO', 'XLE', 'XOP', 'GSG'],
    '161129': ['USO', 'BNO', 'XLE', 'XOP', 'GSG'],
    '501018': ['USO', 'BNO', 'XLE', 'XOP', 'GSG'],
    '163208': ['XLE', 'XOP', 'OIH', 'IEO', 'USO', 'BNO'],
    '160216': ['GSG', 'DJP', 'DBC', 'GLD', 'USO', 'BNO', 'XLE', 'XOP'],
    '161815': ['GLD', 'TIP', 'GSG', 'DJP', 'DBC', 'USO', 'BNO', 'IAU', 'SLV'],
    '165513': ['GSG', 'DJP', 'DBC', 'GLD', 'USO', 'BNO', 'XLE', 'XOP', 'GDX'],
    '160719': ['GLD', 'IAU', 'GDX', 'SLV', 'GLDM'],
    '164701': ['GLD', 'IAU', 'GDX', 'SLV', 'GLDM'],
    '161116': ['GLD', 'IAU', 'GDX', 'SLV', 'GLDM'],
}


# ============================================================
# 主流程
# ============================================================

def main():
    # 1. 反查secid
    secid_map = resolve_all_secids()

    # 2. 收集所有候选ETF（去重）
    all_candidates = set()
    for pool in CANDIDATE_POOLS.values():
        all_candidates.update(pool)
    print(f'\n共需 {len(all_candidates)} 个候选ETF: {sorted(all_candidates)}')

    # 3. 拉取ETF历史数据
    print('\n=== 拉取ETF历史数据 ===')
    all_etf = {}
    for ticker in sorted(all_candidates):
        info = secid_map.get(ticker)
        if not info:
            print(f'  {ticker}: 无secid映射，跳过')
            continue
        prices = fetch_etf_hist(info['secid'])
        if prices:
            all_etf[ticker] = prices
            print(f'  {ticker} ({info["secid"]}): {len(prices)} days')
        else:
            print(f'  {ticker} ({info["secid"]}): 无数据')
        time.sleep(0.3)

    print(f'\n成功获取 {len(all_etf)} 个ETF数据')

    # 4. 拉取基金NAV
    print('\n=== 拉取基金NAV ===')
    all_nav = {}
    for code in sorted(A_FUNDS_CURRENT.keys()):
        nav = get_nav_all(code)
        all_nav[code] = nav
        print(f'  {code} {A_FUNDS_CURRENT[code][0]}: {len(nav)} days')
        time.sleep(0.3)

    # 5. 逐基金回测所有方案
    print('\n=== 回测：单ETF方案 ===')
    results = []

    for code in sorted(A_FUNDS_CURRENT.keys()):
        name, current_etf = A_FUNDS_CURRENT[code]
        nav = all_nav.get(code, {})
        if len(nav) < 15:
            print(f'{code} {name}: NAV不足({len(nav)}天)，跳过')
            continue

        candidates = CANDIDATE_POOLS.get(code, [])
        available = [t for t in candidates if t in all_etf]

        # 单ETF
        singles = []
        for t in available:
            r = calc_r2_single(nav, all_etf[t])
            if r:
                singles.append({'type': 'single', 'etf': t, **r})
        singles.sort(key=lambda x: -x['r2'])

        # 双ETF组合 (取top8单ETF做组合)
        duals = []
        top_etfs = [s['etf'] for s in singles[:8]]
        for i in range(len(top_etfs)):
            for j in range(i+1, len(top_etfs)):
                r = calc_r2_dual(nav, all_etf[top_etfs[i]], all_etf[top_etfs[j]])
                if r:
                    duals.append({'type': 'dual', 'etf1': top_etfs[i], 'etf2': top_etfs[j], **r})
        duals.sort(key=lambda x: -x['r2'])

        # 当前映射R2
        cur_r2 = None
        for s in singles:
            if s['etf'] == current_etf:
                cur_r2 = s['r2']
                break

        # 选最优：双ETF显著优于单ETF才选双
        best = None
        if duals and (not singles or duals[0]['r2'] > singles[0]['r2'] + 0.02):
            best = duals[0]
            best_label = f"{duals[0]['etf1']}+{duals[0]['etf2']}"
        elif singles:
            best = singles[0]
            best_label = singles[0]['etf']
        else:
            best_label = '-'

        improved = best and cur_r2 is not None and best['r2'] > cur_r2 + 0.01

        entry = {
            'code': code, 'name': name,
            'currentEtf': current_etf, 'currentR2': cur_r2,
            'bestType': best['type'] if best else 'none',
            'bestMapping': best_label,
            'bestR2': best['r2'] if best else None,
            'bestMae': best['mae'] if best else None,
            'bestMaxErr': best['maxErr'] if best else None,
            'improved': improved,
            'top3single': [(s['etf'], s['r2']) for s in singles[:3]],
            'top3dual': [(d['etf1']+'+'+d['etf2'], d['r2']) for d in duals[:3]],
        }
        results.append(entry)

        flag = ' ↑' if improved else ''
        print(f'{code} {name:<10} cur:{current_etf}={cur_r2} best:{best["type"]}:{best_label}={best["r2"]}{flag}')

    # 6. 输出
    os.makedirs(BACKTEST_DIR, exist_ok=True)

    # 保存完整结果
    out_path = os.path.join(BACKTEST_DIR, 'explorer_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n完整结果: {out_path}')

    # 生成优化后的a_results.json（用最优映射）
    a_results = {}
    config_updates = []
    for r in results:
        a_results[r['code']] = {
            'r2': r['bestR2'], 'mae': r['bestMae'],
            'maxErr': r['bestMaxErr'], 'samplePeriod': '-'
        }
        if r['improved']:
            config_updates.append({
                'code': r['code'], 'name': r['name'],
                'old': r['currentEtf'], 'new': r['bestMapping'],
                'oldR2': r['currentR2'], 'newR2': r['bestR2']
            })

    a_path = os.path.join(BACKTEST_DIR, 'a_results.json')
    with open(a_path, 'w', encoding='utf-8') as f:
        json.dump(a_results, f, ensure_ascii=False, indent=2)
    print(f'回测结果: {a_path}')

    # 需要更新config的映射
    if config_updates:
        print(f'\n=== 需要更新config的映射 ({len(config_updates)}只) ===')
        for u in config_updates:
            print(f"  {u['code']} {u['name']}: {u['old']} → {u['new']}  (R2: {u['oldR2']} → {u['newR2']})")

    return results, config_updates


if __name__ == '__main__':
    main()