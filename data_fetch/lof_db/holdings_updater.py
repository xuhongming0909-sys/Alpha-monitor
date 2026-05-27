# -*- coding: utf-8 -*-
# AI-SUMMARY: 持仓数据增量更新，从东方财富F10 API获取
# 对应 INDEX.md §9.3 文件摘要索引
"""持仓数据增量更新"""

import re
import requests
from data_fetch.lof_db.schema import get_db

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://fundf10.eastmoney.com/',
})

# B类基金（需要持仓数据）
def _load_b_fund_codes() -> list[str]:
    """从 config 读取B类基金代码。"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        return [f["code"] for f in funds if f.get("estimation") == "B" and f.get("code")]
    except Exception:
        pass
    return ['160644', '164906', '160125', '501312']

B_FUNDS = _load_b_fund_codes()


def fetch_holdings(code, year=2025, month=12):
    """获取基金持仓"""
    url = f'https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year={year}&month={month}'
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
            result.append({
                'code': stk_code,
                'name': stk_name,
                'weight': float(pct),
                'market': mkt,
            })
        return result
    except Exception as e:
        print(f'  {code}: {e}')
    return []


def update_holdings():
    """增量更新持仓数据"""
    conn = get_db()
    total = 0

    for code in B_FUNDS:
        for year, month in [(2025, 12), (2024, 12), (2024, 9)]:
            holdings = fetch_holdings(code, year=year, month=month)
            if holdings:
                report_date = f'{year}-{month:02d}-31'
                for h in holdings:
                    conn.execute(
                        'INSERT OR REPLACE INTO holdings (code, report_date, ticker, name, weight, market) VALUES (?, ?, ?, ?, ?, ?)',
                        (code, report_date, h['code'], h['name'], h['weight'], h['market'])
                    )
                conn.commit()
                total += len(holdings)
                print(f'  {code}: {len(holdings)} holdings from {year}Q{month//3+1}')
                break

    conn.close()
    return total