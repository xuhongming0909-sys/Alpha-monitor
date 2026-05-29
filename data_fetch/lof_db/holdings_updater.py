# -*- coding: utf-8 -*-
# AI-SUMMARY: 基金持仓更新 - 指数型跳过, 主动型先API再PDF
"""基金持仓更新流程。

指数型: 跳过(ETF映射在fund_classifier.py硬编码)
主动型: akshare API优先, 持仓合计<25%时fallback到PDF解析
"""
import os
import datetime
import time

from data_fetch.lof_db.schema import get_db, init_db


# API覆盖率阈值: 低于此值触发PDF解析
_API_COVERAGE_THRESHOLD = 25.0


def _load_funds():
    """从config加载所有基金列表"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds", [])
        return [f for f in funds if f.get("code")]
    except Exception:
        return []


def _is_index_fund(code: str) -> bool:
    from data_fetch.lof_iopv.fund_classifier import is_index_fund
    return is_index_fund(code)


def _fetch_holdings_api(code: str, year: str = None) -> list:
    """akshare API获取持仓"""
    import akshare as ak
    if year is None:
        year = str(datetime.datetime.now().year)
    try:
        df = ak.fund_portfolio_hold_em(symbol=code, date=year)
        if df is None or df.empty:
            return []
        holdings = []
        for _, row in df.iterrows():
            ticker = str(row.get("股票代码", ""))
            name = str(row.get("股票名称", ""))
            weight = float(row.get("占净值比例", 0) or 0)
            quarter = str(row.get("季度", ""))
            if ticker and weight > 0:
                holdings.append({"ticker": ticker, "name": name, "weight": weight, "quarter": quarter})
        return holdings
    except Exception as e:
        print(f"  {code}: API失败 - {e}")
        return []


def _fetch_holdings_html(code: str) -> list:
    """东方财富HTML抓取持仓"""
    import re, requests
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://fundf10.eastmoney.com/"})
    url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        r = s.get(url, timeout=15)
        m = re.search(r'content:"(.*?)",arryear', r.text, re.DOTALL)
        if not m:
            return []
        rows = re.findall(
            r'<tr><td>(\d+)</td>.*?<a href=[^>]+>([A-Z0-9]+)</a>.*?<a href=[^>]+>([^<]+)</a>.*?<td[^>]*>([\d.]+)%</td>',
            m.group(1), re.DOTALL
        )
        return [{"ticker": c, "name": n.strip(), "weight": float(w), "quarter": ""} for _, c, n, w in rows]
    except Exception:
        return []


def _fetch_holdings_pdf(code: str) -> list:
    """PDF解析获取持仓(调用report_holdings模块)"""
    try:
        from data_fetch.lof_iopv.report_holdings import update_all_holdings
        results = update_all_holdings([code], concurrency=1)
        result = results.get(code, {})
        if result.get("ok"):
            # 重新从DB读取
            from data_fetch.lof_db.schema import get_db as _get_db
            conn = _get_db()
            latest = conn.execute(
                "SELECT report_date FROM holdings WHERE code = ? ORDER BY report_date DESC LIMIT 1",
                (code,)
            ).fetchone()
            if latest:
                rows = conn.execute(
                    "SELECT ticker, name, weight, market FROM holdings WHERE code = ? AND report_date = ?",
                    (code, latest[0])
                ).fetchall()
                conn.close()
                return [{"ticker": r[0], "name": r[1], "weight": r[2], "quarter": latest[0]} for r in rows]
            conn.close()
        return []
    except Exception as e:
        print(f"  {code}: PDF解析失败 - {e}")
        return []


def _determine_market(ticker: str) -> str:
    """根据ticker判断市场"""
    if ticker.isdigit() and len(ticker) == 5:
        return "HK"
    if ticker.isdigit() and len(ticker) == 6:
        return "A"
    return "US"


def _store_holdings(conn, code: str, holdings: list, quarter: str):
    """写入持仓到DB, 清除旧数据"""
    # 删除该基金旧数据
    conn.execute("DELETE FROM holdings WHERE code = ?", (code,))
    for h in holdings:
        t = h["ticker"]
        market = _determine_market(t)
        conn.execute(
            "INSERT OR REPLACE INTO holdings (code, report_date, ticker, name, weight, market) VALUES (?,?,?,?,?,?)",
            (code, quarter, t, h.get("name", ""), h["weight"], market)
        )
    conn.commit()


def update_holdings():
    """主入口: 更新所有基金持仓"""
    init_db()
    conn = get_db()
    funds = _load_funds()
    stats = {"index": 0, "api_ok": 0, "api_low": 0, "pdf_ok": 0, "fail": 0}
    
    print(f"持仓更新: {len(funds)} 只基金")
    
    for fund in funds:
        code = fund["code"]
        name = fund.get("name", "")
        
        # 指数型: 跳过
        if _is_index_fund(code):
            stats["index"] += 1
            continue
        
        print(f"\n--- {code} {name} ---")
        
        # 主动型: 先API
        holdings = _fetch_holdings_api(code)
        if not holdings:
            print("  API无数据, 尝试HTML...")
            holdings = _fetch_holdings_html(code)
        
        if holdings:
            total_weight = sum(h["weight"] for h in holdings)
            quarter = holdings[0].get("quarter", "latest")
            print(f"  API: {len(holdings)}条, 覆盖率{total_weight:.1f}%")
            
            if total_weight >= _API_COVERAGE_THRESHOLD:
                # API覆盖率足够, 直接用
                _store_holdings(conn, code, holdings, quarter)
                print(f"  -> API数据OK, 已写入DB")
                stats["api_ok"] += 1
                time.sleep(0.5)
                continue
            else:
                print(f"  -> API覆盖率{total_weight:.1f}% < {_API_COVERAGE_THRESHOLD}%, 尝试PDF解析")
                stats["api_low"] += 1
        
        # API失败或覆盖率不足: 尝试PDF解析
        pdf_holdings = _fetch_holdings_pdf(code)
        if pdf_holdings:
            total_weight = sum(h["weight"] for h in pdf_holdings)
            quarter = pdf_holdings[0].get("quarter", "latest")
            _store_holdings(conn, code, pdf_holdings, quarter)
            print(f"  -> PDF解析OK: {len(pdf_holdings)}条, 覆盖率{total_weight:.1f}%")
            stats["pdf_ok"] += 1
        else:
            print(f"  -> 无数据(使用hardcoded兜底)")
            stats["fail"] += 1
        
        time.sleep(0.5)
    
    conn.close()
    print(f"\n完成: 指数型{stats['index']}只跳过, API成功{stats['api_ok']}只, "
          f"API低覆盖{stats['api_low']}只, PDF成功{stats['pdf_ok']}只, 失败{stats['fail']}只")
    return stats


if __name__ == "__main__":
    update_holdings()