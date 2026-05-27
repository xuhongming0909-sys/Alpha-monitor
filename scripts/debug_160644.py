# -*- coding: utf-8 -*-
"""160644 按项目代码实际逻辑逐步展示B类计算过程"""
import sqlite3, os, numpy as np
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), '..', 'runtime_data', 'lof_db', 'lof.db')
CODE = '160644'


def get_db():
    return sqlite3.connect(DB)


def get_series(conn, table, key_col, val_col, key_val):
    rows = conn.execute(
        f'SELECT {val_col}, date FROM {table} WHERE {key_col} = ? ORDER BY date',
        (key_val,)
    ).fetchall()
    return {r[1]: r[0] for r in rows if r[0] is not None}


def get_etf_price(conn, ticker, date):
    """对应 iopv_calculator.get_etf_price: WHERE date <= ? ORDER BY date DESC LIMIT 1"""
    row = conn.execute(
        'SELECT close FROM stock_prices WHERE ticker = ? AND date <= ? ORDER BY date DESC LIMIT 1',
        (ticker, date)
    ).fetchone()
    return row[0] if row else None


def get_fx_rate(conn, currency, date):
    """对应 iopv_calculator.get_fx_rate: currency"""
    if currency == 'CNY':
        return 1.0
    row = conn.execute(
        'SELECT rate FROM fx_rates WHERE UPPER(currency) = UPPER(?) AND date <= ? ORDER BY date DESC LIMIT 1',
        (currency, date)
    ).fetchone()
    return row[0] if row else None


def daily_ret(prices):
    ret = {}
    dates = sorted(prices.keys())
    for i in range(1, len(dates)):
        d, dp = dates[i], dates[i-1]
        if prices[dp] > 0:
            ret[d] = (prices[d] / prices[dp] - 1, dp)
    return ret


def main():
    conn = get_db()

    # === 持仓 ===
    holdings = conn.execute(
        'SELECT report_date, ticker, name, weight, market FROM holdings '
        'WHERE code=? ORDER BY report_date DESC LIMIT 10', (CODE,)
    ).fetchall()
    total_w = sum(h[3] for h in holdings)
    usd_w = sum(h[3] for h in holdings if h[4] == 'US')
    hkd_w = sum(h[3] for h in holdings if h[4] == 'HK')

    print('=' * 70)
    print('Part A: 当前项目代码 calc_iopv_b 的计算逻辑')
    print('  公式: IOPV = NAV * (1 + stock_ratio * sum(w_i * cny_ret_i))')
    print('  其中 cny_ret_i = local_ret * fx_ratio')
    print('  fx_ratio = fx_now / fx_base')
    print('  fx_now = fx_hkd_today (因为fund currency=HKD)')
    print('  fx_base = get_fx_rate(fx_key, nav_date)')
    print('  fx_key = "usd" if market=="US" else "hkd"')
    print()

    # 最近一个有完整数据的净值日: 5/22
    nav_date = '2026-05-22'
    today = '2026-05-27'

    nav_row = conn.execute('SELECT nav FROM fund_nav WHERE code=? AND date=?', (CODE, nav_date)).fetchone()
    nav = nav_row[0]
    fx_now = get_fx_rate(conn, 'HKD', today)  # fund currency = HKD
    print(f'  nav_date: {nav_date}  NAV={nav}')
    print(f'  fx_now (HKD/{today}): {fx_now}')
    print()

    print('  项目代码逐股计算:')
    weighted_ret = 0
    valid = 0
    for h in holdings:
        ticker, name, weight, market = h[1], h[2], h[3], h[4]
        price_now = get_etf_price(conn, ticker, today)
        price_prev = get_etf_price(conn, ticker, nav_date)
        if not price_now or not price_prev or price_prev == 0:
            print(f'    {ticker:8s} price缺失, skip')
            continue

        local_ret = price_now / price_prev - 1

        fx_key = 'usd' if market == 'US' else 'hkd'
        fx_base = get_fx_rate(conn, fx_key, nav_date)
        fx_ratio = 1.0
        if fx_now and fx_base and fx_base > 0:
            fx_ratio = fx_now / fx_base

        cny_ret = local_ret * fx_ratio  # <-- 项目代码: local_ret * fx_ratio
        contrib = cny_ret * (weight / total_w)
        weighted_ret += contrib
        valid += 1

        print(f'    {ticker:8s} {market:2s}  local_ret={local_ret*100:+7.4f}%  fx_key={fx_key}  fx_base={fx_base}  fx_ratio={fx_ratio}  cny_ret={cny_ret*100:+7.4f}%  w={weight/total_w*100:.2f}%  contrib={contrib*100:+7.4f}%')

    stock_ratio = total_w  # spec: stock_ratio是百分比值
    est_ret_pct = stock_ratio * weighted_ret  # stock_ratio/100 * weighted_ret, 但total_w已经是百分比
    # 等等, 看代码: est_ret = (stock_ratio / 100) * weighted_ret
    # stock_ratio = total_w = 61.46
    # weighted_ret is the sum of normalized weighted returns
    # 所以 est_ret = (61.46 / 100) * weighted_ret
    # 但weighted_ret已经用了normalized weights (weight/total_w), 所以weighted_ret是一个完整的收益率
    # 再乘以 stock_ratio/100 会缩小
    # 让我重新看代码...

    print()
    print('  关键: 代码中 stock_ratio = total_w = {:.2f}'.format(total_w))
    print('  weighted_ret = sum(cny_ret_i * (weight_i / total_w)) = {:.6f}'.format(weighted_ret))
    print('  est_ret = (stock_ratio / 100) * weighted_ret = ({:.2f} / 100) * {:.6f} = {:.6f}'.format(
        stock_ratio, weighted_ret, (stock_ratio / 100) * weighted_ret))
    print('  IOPV = NAV * (1 + est_ret) = {:.4f} * (1 + {:.6f}) = {:.4f}'.format(
        nav, (stock_ratio / 100) * weighted_ret, nav * (1 + (stock_ratio / 100) * weighted_ret)))
    print()
    print('  问题1: fx_ratio = fx_hkd_today / fx_usd_nav_date (US股) — 跨币种比值, 无意义')
    print('  问题2: cny_ret = local_ret * fx_ratio — 应为 (1+local_ret)*fx_ratio - 1')
    print('  问题3: stock_ratio=61.46, weighted_ret已用归一化权重求和=完整收益率')
    print('         再乘 stock_ratio/100 把收益率缩小到61.46%, 假设38.54%仓位为0收益')
    print('         但这与spec公式一致: IOPV = NAV * (1 + stock_ratio * sum(w_i * ret_i))')

    # === Part B: 按spec正确逻辑重算 ===
    print()
    print('=' * 70)
    print('Part B: 按用户指定的正确逻辑 — 个股收益率 + 个股市场汇率 + 求和T10')
    print('  步骤: 对每只T10持仓:')
    print('    1. 个股涨跌幅(price_d/price_dp - 1)')
    print('    2. 该股市场对应汇率涨跌幅(fx_rate[d]/fx_rate[dp] - 1)')
    print('    3. 人民币收益率 = (1+个股涨跌) * (1+汇率涨跌) - 1')
    print('    4. 乘以归一化权重')
    print('  求和所有T10, 再乘stock_ratio')
    print()

    # 回测模式: 逐日计算
    fx_usd_all = get_series(conn, 'fx_rates', 'currency', 'rate', 'USD')
    fx_hkd_all = get_series(conn, 'fx_rates', 'currency', 'rate', 'HKD')
    nav_all = get_series(conn, 'fund_nav', 'code', 'nav', CODE)
    nav_dates = sorted(nav_all.keys())

    stock_prices_all = {}
    for h in holdings:
        prices = get_series(conn, 'stock_prices', 'ticker', 'close', h[1])
        if prices:
            stock_prices_all[h[1]] = prices

    r40 = nav_dates[-40:] if len(nav_dates) >= 40 else nav_dates

    yv, xv = [], []
    debug = []

    for i in range(1, len(r40)):
        d, dp = r40[i], r40[i-1]

        # NAV return
        if nav_all.get(d) is None or nav_all.get(dp) is None:
            continue
        nav_d = nav_all[d]
        nav_dp = nav_all[dp]
        fund_ret = nav_d / nav_dp - 1

        # 逐股: 累计收益率 + 币种汇率
        stock_parts = []
        wr = 0
        for h in holdings:
            ticker, weight, market = h[1], h[3], h[4]
            if ticker not in stock_prices_all:
                continue
            prices = stock_prices_all[ticker]
            # 取dp和d当天的价格(或最近的)
            p_dp = None
            for dd in reversed(sorted(prices.keys())):
                if dd <= dp:
                    p_dp = prices[dd]
                    break
            p_d = None
            for dd in reversed(sorted(prices.keys())):
                if dd <= d:
                    p_d = prices[dd]
                    break
            if not p_dp or not p_d or p_dp == 0:
                continue

            local_ret = p_d / p_dp - 1

            # 汇率: 根据个股市场取对应币种
            if market == 'US':
                fx_dp = fx_usd_all.get(dp)
                fx_d = fx_usd_all.get(d)
            else:
                fx_dp = fx_hkd_all.get(dp)
                fx_d = fx_hkd_all.get(d)

            fx_chg = 0
            if fx_dp and fx_d and fx_dp > 0:
                fx_chg = fx_d / fx_dp - 1

            cny_ret = (1 + local_ret) * (1 + fx_chg) - 1
            norm_w = weight / total_w
            contrib = cny_ret * norm_w
            wr += contrib
            stock_parts.append((ticker, market, local_ret, fx_chg, cny_ret, norm_w))

        # stock_ratio * weighted_return
        est_ret = (total_w / 100) * wr

        d1 = datetime.strptime(dp, '%Y-%m-%d')
        d2 = datetime.strptime(d, '%Y-%m-%d')
        gap = (d2 - d1).days

        yv.append(fund_ret)
        xv.append(est_ret)
        debug.append({
            'date': d, 'prev': dp, 'gap': gap,
            'fund': fund_ret, 'est': est_ret,
            'parts': stock_parts,
        })

    print(f'  对齐行数: {len(yv)}')
    print()
    print(f'  {"日期":12s} {"前日":12s} {"间隔":>4s} {"基金涨跌":>10s} {"估算涨跌":>10s} {"误差":>10s}')
    print(f'  {"-"*64}')
    for r in debug:
        flag = ' !!!' if r['gap'] > 4 else ''
        print(f'  {r["date"]:12s} {r["prev"]:12s} {r["gap"]:3d}d {r["fund"]*100:9.4f}% {r["est"]*100:9.4f}% {(r["fund"]-r["est"])*100:9.4f}%{flag}')

    # 回归统计
    if len(yv) >= 10:
        y_arr = np.array(yv)
        x_arr = np.array(xv)
        ss_tot = np.sum((y_arr - np.mean(y_arr)) ** 2)
        ss_res = np.sum((y_arr - x_arr) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        abs_err = np.abs(y_arr - x_arr)
        print()
        print(f'  R2: {round(float(r2), 4)}')
        print(f'  MAE: {round(float(np.mean(abs_err)) * 100, 4)}%')
        print(f'  MaxErr: {round(float(np.max(abs_err)) * 100, 4)}%')

    # === Part C: 最新IOPV溢价率(逐股拆解) ===
    print()
    print('=' * 70)
    print('Part C: 最新IOPV溢价率 — 逐股拆解')
    d = nav_dates[-1]
    dp = nav_dates[-2]
    nav_d = nav_all[d]
    nav_dp = nav_all[dp]
    fx_now_val = get_fx_rate(conn, 'HKD', d)

    print(f'  日期: {d}  前日: {dp}')
    print(f'  NAV: {nav_d:.4f}  前日NAV: {nav_dp:.4f}')
    print(f'  fx_hkd_today: {fx_now_val}')
    print()
    print(f'  {"ticker":8s} {"市场":4s} {"前日价":>10s} {"今日价":>10s} {"个股涨跌":>10s} {"币种":4s} {"前日fx":>8s} {"今日fx":>8s} {"汇率涨跌":>10s} {"人民币收益":>10s} {"归一权重":>8s} {"贡献":>10s}')
    print(f'  {"-"*110}')

    wr_total = 0
    for h in holdings:
        ticker, weight, market = h[1], h[3], h[4]
        p_dp = get_etf_price(conn, ticker, dp)
        p_d = get_etf_price(conn, ticker, d)
        if not p_dp or not p_d or p_dp == 0:
            continue

        local_ret = p_d / p_dp - 1
        fx_key = 'USD' if market == 'US' else 'HKD'
        fx_dp_val = get_fx_rate(conn, fx_key, dp)
        fx_d_val = get_fx_rate(conn, fx_key, d)
        fx_chg = 0
        if fx_dp_val and fx_d_val and fx_dp_val > 0:
            fx_chg = fx_d_val / fx_dp_val - 1

        cny_ret = (1 + local_ret) * (1 + fx_chg) - 1
        norm_w = weight / total_w
        contrib = cny_ret * norm_w
        wr_total += contrib

        print(f'  {ticker:8s} {market:4s} {p_dp:10.2f} {p_d:10.2f} {local_ret*100:+9.4f}% {fx_key:4s} {fx_dp_val:8.4f} {fx_d_val:8.4f} {fx_chg*100:+9.4f}% {cny_ret*100:+9.4f}% {norm_w*100:7.2f}% {contrib*100:+9.4f}%')

    est_ret_final = (total_w / 100) * wr_total
    iopv = nav_dp * (1 + est_ret_final)
    premium = (nav_d / iopv - 1) * 100 if iopv > 0 else 0

    print(f'  {"-"*110}')
    print(f'  T10加权人民币收益合计: {wr_total*100:+.4f}%')
    print(f'  stock_ratio: {total_w:.2f}%')
    print(f'  est_ret = stock_ratio * weighted_ret = ({total_w:.2f}/100) * {wr_total:.6f} = {est_ret_final:.6f}')
    print(f'  IOPV = {nav_dp:.4f} * (1 + {est_ret_final:.6f}) = {iopv:.4f}')
    print(f'  真实NAV = {nav_d:.4f}')
    print(f'  溢价率 = ({nav_d:.4f} / {iopv:.4f} - 1) * 100 = {premium:+.4f}%')

    conn.close()


if __name__ == '__main__':
    main()