# -*- coding: utf-8 -*-
# AI-SUMMARY: 基金持仓更新，使用akshare fund_portfolio_hold_em API
"""基金持仓增量更新 - akshare fund_portfolio_hold_em API"""

import os
import datetime
import time

for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
    os.environ[k] = ''

from data_fetch.lof_db.schema import get_db


def _load_b_funds():
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        return [f for f in funds if f.get("estimation") == "B" and f.get("code")]
    except Exception:
        return []


def _fetch_holdings_api(code, year=None):
    import akshare as ak
    if year is None:
        year = str(datetime.datetime.now().year)
    try:
        df = ak.fund_portfolio_hold_em(symbol=code, date=year)
        if df is None or df.empty:
            return []
        holdings = []
        for _, row in df.iterrows():
            code_stock = str(row.get("股票代码", ""))
            name_stock = str(row.get("股票名称", ""))
            weight = float(row.get("占净值比例", 0) or 0)
            quarter = str(row.get("季度", ""))
            if code_stock and weight > 0:
                holdings.append({"ticker": code_stock, "name": name_stock, "weight": weight, "quarter": quarter})
        return holdings
    except Exception as e:
        print(f"  {code}: API失败 - {e}")
        return []


def _fetch_holdings_html(code):
    import re, requests
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://fundf10.eastmoney.com/"})
    url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        r = s.get(url, timeout=15)
        m = re.search(r'content:"(.*?)",arryear', r.text, re.DOTALL)
        if not m: return []
        rows = re.findall(r'<tr><td>(\d+)</td>.*?<a href=[^>]+>([A-Z0-9]+)</a>.*?<a href=[^>]+>([^<]+)</a>.*?<td[^>]*>([\d.]+)%</td>', m.group(1), re.DOTALL)
        return [{"ticker": c, "name": n.strip(), "weight": float(w), "quarter": ""} for _, c, n, w in rows]
    except Exception:
        return []


def update_holdings():
    conn = get_db()
    b_funds = _load_b_funds()
    total = 0
    print(f"B类基金 ({len(b_funds)}):")
    for fund in b_funds:
        code = fund["code"]
        name = fund.get("name", "")
        print(f"\n--- {code} {name} ---")
        holdings = _fetch_holdings_api(code)
        if not holdings:
            print("  API无数据，尝试HTML...")
            holdings = _fetch_holdings_html(code)
        if not holdings:
            print("  无持仓"); continue
        quarter = holdings[0].get("quarter", "latest")
        for h in holdings:
            t = h["ticker"]
            market = "HK" if (t.isdigit() and len(t) == 5) else "US"
            conn.execute("INSERT OR REPLACE INTO holdings (code, report_date, ticker, name, weight, market) VALUES (?,?,?,?,?,?)",
                (code, quarter, t, h["name"], h["weight"], market))
        conn.commit()
        total += len(holdings)
        print(f"  {len(holdings)}条 ({quarter})")
        time.sleep(0.5)
    conn.close()
    print(f"\n完成: {total}条")
    return total


if __name__ == "__main__":
    update_holdings()