# AI-SUMMARY: LOF 13只A类指数法回测脚本
# 对应 INDEX.md §9.3 文件摘要索引
# -*- coding: utf-8 -*-
"""LOF 13只 A类指数法回测 - 使用东方财富美股K线API"""
import os, sys, json, numpy as np
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(BASE, 'lof13_nav.json'), encoding='utf-8') as f:
    ALL_NAV = json.load(f)
with open(os.path.join(BASE, 'lof13_etf_prices.json'), encoding='utf-8') as f:
    ALL_ETF = json.load(f)

START = '2026-03-10'
END = '2026-05-26'


def daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i - 1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


INDEX_FUNDS = {
    '160416': ('华安石油', {'XLE': 1.0}),
    '162719': ('广发石油', {'XOP': 1.0}),
    '162411': ('华宝油气', {'XOP': 1.0}),
    '160719': ('嘉实黄金', {'GLD': 1.0}),
    '164701': ('汇添富黄金', {'GLD': 1.0}),
    '160723': ('嘉实原油', {'USO': 1.0}),
    '161116': ('易方达黄金', {'GLD': 0.5, 'GDX': 0.5}),
}

FOF_FUNDS = {
    '160216': ('国泰商品', [('GSG', {'GSG': 1.0}), ('DJP', {'DJP': 1.0}), ('GSG50+GLD50', {'GSG': 0.5, 'GLD': 0.5})]),
    '163208': ('诺安油气', [('XLE', {'XLE': 1.0}), ('XLE50+XOP50', {'XLE': 0.5, 'XOP': 0.5}), ('XLE60+XOP30+GDX10', {'XLE': 0.6, 'XOP': 0.3, 'GDX': 0.1})]),
    '161815': ('银华抗通胀', [('GLD50+USO50', {'GLD': 0.5, 'USO': 0.5}), ('GLD50+GSG50', {'GLD': 0.5, 'GSG': 0.5}), ('GLD40+USO30+GSG30', {'GLD': 0.4, 'USO': 0.3, 'GSG': 0.3})]),
    '165513': ('中信保诚商品', [('GSG', {'GSG': 1.0}), ('USO50+GDX50', {'USO': 0.5, 'GDX': 0.5}), ('GSG50+GLD50', {'GSG': 0.5, 'GLD': 0.5})]),
    '161129': ('易方达原油', [('USO', {'USO': 1.0}), ('USO90+BNO10', {'USO': 0.9, 'BNO': 0.1})]),
    '501018': ('南方原油', [('USO60+BNO40', {'USO': 0.6, 'BNO': 0.4}), ('USO', {'USO': 1.0})]),
}


def backtest(code, name, label, weights):
    nav = ALL_NAV.get(code, {})
    fund_ret = daily_ret(nav)
    if not fund_ret:
        return None

    etf_rets = {}
    for ticker, w in weights.items():
        prices = ALL_ETF.get(ticker, {})
        if not prices:
            continue
        total_w = sum(weights.values())
        etf_rets[ticker] = (daily_ret(prices), w / total_w)

    if not etf_rets:
        return None

    common = set(fund_ret.keys())
    for er, _ in etf_rets.values():
        common &= set(er.keys())

    aligned = []
    for d in sorted(common):
        fp = fund_ret[d][1]
        if all(er[d][1] == fp for er, _ in etf_rets.values()):
            aligned.append(d)

    if len(aligned) < 10:
        return None

    y = np.array([fund_ret[d][0] for d in aligned])
    x = np.array([sum(er[d][0] * w for er, w in etf_rets.values()) for d in aligned])

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
        'code': code, 'name': name, 'label': label, 'n': n,
        'r2': round(r2, 4), 'beta': round(beta, 4), 'mae': round(mae, 4),
        'max_err': round(max_err, 4), 'over05': over05, 'over03': over03,
        'dir': round(dir_pct, 1), 'tag': tag,
        'aligned_dates': aligned, 'y': y.tolist(), 'x': x.tolist(),
    }


if __name__ == '__main__':
    print(f'LOF 13 A-index backtest | {START} ~ {END}')
    print(f'Data: NAV=eastmoney, ETF=eastmoney US kline via proxy')
    print()

    all_results = []

    print('=' * 90)
    print('I. Pure Index (7)')
    print('=' * 90)
    for code, (name, weights) in INDEX_FUNDS.items():
        label = '+'.join(f'{t}{int(w*100)}' for t, w in weights.items()) if len(weights) > 1 else list(weights.keys())[0]
        r = backtest(code, name, label, weights)
        if r:
            all_results.append(r)
            print(f'  {code} {name} -> {label} N={r["n"]} R2={r["r2"]:.4f} MAE={r["mae"]:.4f}% {r["tag"]}')
        else:
            print(f'  {code} {name} -> SKIP')

    print()
    print('=' * 90)
    print('II. FOF/Active (6, multi-combo)')
    print('=' * 90)
    for code, (name, combos) in FOF_FUNDS.items():
        print(f'\n--- {code} {name} ---')
        for label, weights in combos:
            r = backtest(code, name, label, weights)
            if r:
                all_results.append(r)
                print(f'  {label} N={r["n"]} R2={r["r2"]:.4f} MAE={r["mae"]:.4f}% {r["tag"]}')

    # Summary table
    print()
    print('=' * 130)
    print(f'{"code":<8}{"name":<12}{"method":<22}{"N":>3}{"R2":>8}{"beta":>8}{"MAE%":>8}{"dir%":>7}{"maxErr%":>9}{">0.5%":>6}{">0.3%":>6}{"tag":>5}')
    print('-' * 130)
    for r in all_results:
        print(f"{r['code']:<8}{r['name']:<12}{r['label']:<22}{r['n']:>3}{r['r2']:>8.4f}{r['beta']:>8.4f}{r['mae']:>8.4f}{r['dir']:>7.1f}{r['max_err']:>9.4f}{r['over05']:>6}{r['over03']:>6}{r['tag']:>5}")

    # Best per fund
    print()
    print('=' * 130)
    print('Best method per fund')
    print('=' * 130)
    by_code = defaultdict(list)
    for r in all_results:
        by_code[r['code']].append(r)

    for code in sorted(by_code.keys()):
        candidates = by_code[code]
        best = max(candidates, key=lambda x: x['r2'])
        print(f"  {code} {best['name']}: {best['label']}  R2={best['r2']:.4f} beta={best['beta']:.4f} MAE={best['mae']:.4f}% dir={best['dir']:.1f}% {best['tag']}")

    print(f"\nDone. {__import__('datetime').datetime.now():%Y-%m-%d %H:%M:%S}")