# -*- coding: utf-8 -*-
# AI-SUMMARY: ETF价格增量更新，通过akshare反查secid后从东财拉取美股ETF日线
# 对应 INDEX.md §9.3 文件摘要索引
"""ETF价格增量更新 - 两步走：stock_us_spot_em反查secid + stock_us_hist拉历史"""

import time
from data_fetch.lof_db.schema import get_db


def _load_etf_list() -> list[str]:
    """从 config.yaml 提取去重的 ETF 代码列表。"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        etfs = {f["etf"] for f in funds if f.get("etf") and f.get("estimation") == "A"}
        if etfs:
            return sorted(etfs)
    except Exception:
        pass
    return ['QQQ', 'SPY', 'GLD', 'XLK']


def _resolve_secids(tickers: list[str]) -> dict[str, str]:
    """通过 stock_us_spot_em 反查每个ETF的东财secid（105/106/107）。

    返回 {ticker: "105.QQQ", ...} 映射。
    """
    import akshare as ak
    try:
        df = ak.stock_us_spot_em()
    except Exception as e:
        print(f'  stock_us_spot_em 失败: {e}')
        return {}

    # df 里有 代码 列，格式如 "105.QQQ" 或 "106.SPY"
    result = {}
    code_to_ticker = {}
    for _, row in df.iterrows():
        code = str(row.get('代码', ''))
        if '.' in code:
            parts = code.split('.', 1)
            secid = parts[0]
            sym = parts[1].upper()
            code_to_ticker[sym] = f'{secid}.{sym}'

    for t in tickers:
        t_upper = t.upper()
        if t_upper in code_to_ticker:
            result[t] = code_to_ticker[t_upper]
        else:
            print(f'  {t}: 未在stock_us_spot_em中找到')

    return result


def fetch_etf_hist(secid: str, start: str = '20250101', end: str = '20261231') -> dict:
    """通过 akshare stock_us_hist 拉取ETF历史日线收盘价。

    secid: 东财内部编码，如 "105.QQQ"
    返回 {date_str: close_price}
    """
    import akshare as ak
    try:
        df = ak.stock_us_hist(
            symbol=secid,
            period="daily",
            start_date=start,
            end_date=end,
            adjust=""
        )
    except Exception as e:
        print(f'  {secid}: stock_us_hist 失败 - {e}')
        return {}

    if df is None or df.empty:
        return {}

    prices = {}
    for _, row in df.iterrows():
        date_str = str(row['日期']).replace('-', '')
        close = float(row['收盘'])
        if close > 0:
            prices[date_str] = close
    return prices


def update_etf():
    """增量更新所有ETF价格。"""
    conn = get_db()
    total_inserted = 0

    etf_list = _load_etf_list()
    print(f'ETF列表 ({len(etf_list)}): {", ".join(etf_list)}')

    # 步骤1: 反查secid
    secid_map = _resolve_secids(etf_list)
    if not secid_map:
        print('secid反查失败，跳过更新')
        conn.close()
        return 0

    print(f'secid映射: {secid_map}')

    # 步骤2: 逐个拉取历史数据
    for ticker in etf_list:
        secid = secid_map.get(ticker)
        if not secid:
            continue

        prices = fetch_etf_hist(secid)
        if not prices:
            continue

        for date, close in prices.items():
            conn.execute(
                'INSERT OR REPLACE INTO etf_prices (ticker, date, close) VALUES (?, ?, ?)',
                (ticker, date, close)
            )
        conn.commit()
        total_inserted += len(prices)
        print(f'  {ticker} ({secid}): {len(prices)} days')
        time.sleep(0.5)

    conn.close()
    return total_inserted


if __name__ == '__main__':
    total = update_etf()
    print(f'\n更新完成: 共 {total} 条记录')