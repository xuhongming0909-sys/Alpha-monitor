# -*- coding: utf-8 -*-
"""QDII LOF IOPV 数据获取层 - 31只基金双引擎版。

东财净值+持仓+基金档案 | 腾讯行情+汇率。
"""

from __future__ import annotations

import json as _json
import math
import re
from typing import Any, Dict, List, Optional

import requests
import urllib.request

from shared.market_service import get_fx_rates, get_quotes
from shared.time.shanghai_time import now_iso

_REQUEST_TIMEOUT = 15

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fundf10.eastmoney.com/",
})
# ETF实时涨跌幅获取（东财美股K线 → 腾讯行情 fallback）
_ETF_SESSION = requests.Session()
_ETF_SESSION.trust_env = False
_ETF_SESSION.proxies = {'http': None, 'https': None}



def _fetch_us_realtime(codes):
    """批量获取美股实时行情（urllib直连，绕过代理）"""
    if not codes:
        return {}
    query = ','.join('us' + c for c in codes)
    url = 'https://qt.gtimg.cn/q=' + query
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode('gbk')
    except Exception:
        return {}
    result = {}
    for line in text.strip().split(';'):
        line = line.strip()
        if len(line) < 20:
            continue
        key = line.split('=')[0].replace('v_', '')
        code = key.replace('us', '')
        data = line.split('"')[1].split('~')
        if len(data) < 5:
            continue
        price = float(data[3]) if data[3] else 0
        prev = float(data[4]) if data[4] else 0
        if price > 0:
            result[code] = {'price': price, 'prev_close': prev}
    return result

def _fetch_etf_changes(etf_codes: list) -> dict:
    """获取ETF实时涨跌幅（百分比）。东财K线优先，腾讯fallback。"""
    if not etf_codes:
        return {}
    changes = {}
    for ticker in etf_codes:
        try:
            url = (f'https://push2his.eastmoney.com/api/qt/stock/kline/get'
                   f'?secid=107.{ticker}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54'
                   f'&klt=101&fqt=1&beg=0&end=20500101&lmt=2')
            r = _ETF_SESSION.get(url, timeout=10)
            klines = r.json().get('data', {}).get('klines', [])
            if len(klines) >= 2:
                prev = float(klines[-2].split(',')[2])
                cur = float(klines[-1].split(',')[2])
                if prev > 0:
                    changes[ticker] = (cur / prev - 1) * 100
        except Exception:
            pass
    missing = [t for t in etf_codes if t not in changes]
    if missing:
        try:
            qt_codes = [f"us{t}.us" for t in missing]
            resp = _ETF_SESSION.get(f"https://qt.gtimg.cn/q={','.join(qt_codes)}", timeout=10)
            for i, line in enumerate(resp.content.decode("gbk", errors="ignore").splitlines()):
                if i >= len(missing):
                    break
                parts = line.split("~")
                if len(parts) > 4:
                    p, c = _to_float(parts[4]), _to_float(parts[3])
                    if p and p > 0 and c:
                        changes[missing[i]] = (c / p - 1) * 100
        except Exception:
            pass
    return changes


def _load_funds_from_config() -> list[dict]:
    """从 config.yaml 读取基金列表，fallback 到内置列表。"""
    try:
        from shared.config.script_config import load_config
        cfg = load_config()
        plugins = cfg.get("data_fetch", {}).get("plugins", {})
        lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
        funds = lof_cfg.get("funds")
        if funds and isinstance(funds, list) and len(funds) > 0:
            return funds
    except Exception:
        pass
    # Fallback 内置列表
    return _FALLBACK_FUNDS

# 内置 fallback 列表（config.yaml 不可用时使用）
_FALLBACK_FUNDS = [
    # A类: 美股宽基指数
    {"code": "161128", "name": "标普信息科技LOF", "currency": "USD", "estimation": "A", "etf": "XLK"},
    {"code": "501225", "name": "全球芯片LOF", "currency": "USD", "estimation": "A", "etf": "SMH"},
    {"code": "161130", "name": "纳指LOF", "currency": "USD", "estimation": "A", "etf": "QQQ"},
    {"code": "161125", "name": "标普500LOF", "currency": "USD", "estimation": "A", "etf": "SPY"},
    {"code": "161126", "name": "标普医疗保健LOF", "currency": "USD", "estimation": "A", "etf": "XLV"},
    {"code": "161127", "name": "标普生物科技LOF", "currency": "USD", "estimation": "A", "etf": "XBI"},
    {"code": "162415", "name": "美国消费LOF", "currency": "USD", "estimation": "A", "etf": "XLY"},
    {"code": "160140", "name": "美国REIT精选LOF", "currency": "USD", "estimation": "A", "etf": "VNQ"},
    {"code": "501300", "name": "美元债LOF", "currency": "USD", "estimation": "A", "etf": "AGG"},
    {"code": "164824", "name": "印度基金LOF", "currency": "USD", "estimation": "A", "etf": "INDA"},
    # A类: 石油商品
    {"code": "160416", "name": "石油基金LOF", "currency": "USD", "estimation": "A", "etf": "XLE"},
    {"code": "162719", "name": "石油LOF", "currency": "USD", "estimation": "A", "etf": "XOP"},
    {"code": "162411", "name": "华宝油气LOF", "currency": "USD", "estimation": "A", "etf": "XOP"},
    {"code": "160723", "name": "嘉实原油LOF", "currency": "USD", "estimation": "A", "etf": "USO"},
    {"code": "161129", "name": "原油LOF", "currency": "USD", "estimation": "A", "etf": "USO"},
    {"code": "501018", "name": "南方原油LOF", "currency": "USD", "estimation": "A", "etf": "USO"},
    {"code": "163208", "name": "全球油气能源LOF", "currency": "USD", "estimation": "A", "etf": "XLE"},
    {"code": "160216", "name": "国泰商品LOF", "currency": "USD", "estimation": "A", "etf": "GSG"},
    {"code": "161815", "name": "抗通胀LOF", "currency": "USD", "estimation": "A", "etf": "GLD"},
    {"code": "165513", "name": "中信保诚商品LOF", "currency": "USD", "estimation": "A", "etf": "GSG"},
    # A类: 黄金
    {"code": "160719", "name": "嘉实黄金LOF", "currency": "USD", "estimation": "A", "etf": "GLD"},
    {"code": "164701", "name": "黄金LOF", "currency": "USD", "estimation": "A", "etf": "GLD"},
    {"code": "161116", "name": "黄金主题LOF", "currency": "USD", "estimation": "A", "etf": "GLD"},
    # B类: T10持仓
    {"code": "160125", "name": "南方香港LOF", "currency": "HKD", "estimation": "B"},
    {"code": "160644", "name": "港美互联网LOF", "currency": "HKD", "estimation": "B"},
    {"code": "164906", "name": "中概互联网LOF", "currency": "USD", "estimation": "B"},
    {"code": "501312", "name": "海外科技LOF", "currency": "USD", "estimation": "B"},
]

QDII_FUNDS = _load_funds_from_config()

def _to_float(value: Any) -> Optional[float]:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _clean(text: Any) -> str:
    if text is None:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


def _fetch_nav(code: str) -> dict:
    """东财净值API + pingzhongdata份额。返回 {nav, navDate, shareIncrease, shareTotal}。"""
    result = {"nav": None, "navDate": None, "shareIncrease": None, "shareTotal": None}
    # 1. NAV
    url = f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=3&callback="
    try:
        data = SESSION.get(url, timeout=_REQUEST_TIMEOUT).json()
        items = (data.get("Data") or {}).get("LSJZList") or []
        if items:
            result["nav"] = _to_float(items[0].get("DWJZ"))
            result["navDate"] = _clean(items[0].get("FSRQ"))[:10]
    except Exception:
        pass
    # 2. 份额 from pingzhongdata
    try:
        js_text = SESSION.get(f"http://fund.eastmoney.com/pingzhongdata/{code}.js", timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r'var\s+Data_buySedemption\s*=\s*(\{.*?\});', js_text, re.DOTALL)
        if m:
            bs = _json.loads(m.group(1))
            for series in bs.get("series", []):
                if series.get("name") == "总份额":
                    data_list = series.get("data", [])
                    if data_list:
                        result["shareTotal"] = data_list[-1]
                elif series.get("name") == "期间申购":
                    data_list = series.get("data", [])
                    if data_list:
                        result["shareIncrease"] = data_list[-1]
    except Exception:
        pass
    return result


def _fetch_holdings(code: str) -> List[dict]:
    """东财F10持仓HTML表格。"""
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r'content\s*:\s*"(.+)"', text, re.DOTALL)
        if not m:
            return []
        rows = re.findall(r'<tr>(.*?)</tr>', m.group(1), re.DOTALL)
        holdings = []
        for row_html in rows[1:]:  # skip header
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if len(cells) < 7:
                continue
            ticker = _clean(cells[1])
            name = _clean(cells[2])
            weight = _to_float(cells[6].replace('%', ''))
            if not ticker or not name:
                continue
            market = "hk" if len(ticker) == 5 else ("sh" if ticker.startswith(("5","6","9")) else ("sz" if ticker.startswith(("0","2","3")) else "us"))
            holdings.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
        return holdings[:10]
    except Exception:
        return []


def _fetch_purchase_status() -> dict:
    """从天天基金获取所有基金申购状态和日累计限额。

    返回: {code: {"applyStatus": str, "dailyLimit": float}}
    - applyStatus: "开放申购" / "暂停申购" / "限大额"
    - dailyLimit: 日累计限定金额（元），无限额时为 1e11
    """
    result = {}
    try:
        url = "https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx"
        params = {"t": "8", "page": "1,50000", "js": "reData", "sort": "fcode,asc"}
        r = SESSION.get(url, params=params, timeout=_REQUEST_TIMEOUT)
        text = r.text.strip().replace("var reData=", "")
        # 正则提取datas数组，避免依赖demjson
        m = re.search(r'datas:\s*(\[.*?\])\s*,\s*\w+:', text, re.DOTALL)
        if not m:
            return result
        import json as _json_parse
        arr = _json_parse.loads(m.group(1))
        for item in arr:
            if len(item) >= 11:
                code = item[0]
                status_raw = item[5]
                daily_limit_raw = item[9]
                try:
                    daily_limit = float(daily_limit_raw)
                except (TypeError, ValueError):
                    daily_limit = None
                result[code] = {
                    "applyStatus": status_raw,
                    "dailyLimit": daily_limit,
                }
    except Exception:
        pass
    return result

# A类ETF净值日价格（用于期间涨跌幅）
def _get_etf_nav_date_prices(etf_codes, nav_date):
    """获取ETF在净值日的价格"""
    if not nav_date:
        return {}
    result = {}
    try:
        from data_fetch.lof_db.schema import get_db as _get_db
        _conn = _get_db()
        for ticker in set(etf_codes):
            row = _conn.execute(
                "SELECT close FROM etf_prices WHERE ticker=? AND date<=? ORDER BY date DESC LIMIT 1",
                (ticker, nav_date)
            ).fetchone()
            if row:
                result[ticker] = row[0]
        _conn.close()
    except Exception:
        pass
    return result

def _fetch_jisilu_qdii() -> dict:
    """从集思录获取QDII限额数据。返回 {code: {min_amt, apply_status, ...}}。"""
    result = {}
    try:
        url = "https://www.jisilu.cn/data/qdii/qdii_list/A"
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        import re as _re
        m = _re.search(r'"rows"\s*:\s*(\[.*?\])', text, _re.DOTALL)
        if m:
            rows = _json.loads(m.group(1))
            for row in rows:
                cell = row.get("cell", row)
                code = str(cell.get("fund_id", ""))
                if code:
                    result[code] = {
                        "min_amt": cell.get("min_amt"),
                        "apply_redeem_status": cell.get("apply_redeem_status", ""),
                    }
    except Exception:
        pass
    return result


def _fetch_stock_position(code):
    """从雪球获取最新股票仓位占比（用当天日期）"""
    try:
        import akshare as ak
        from datetime import datetime
        date = datetime.now().strftime('%Y%m%d')
        df = ak.fund_individual_detail_hold_xq(symbol=code, date=date)
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                if '股票' in str(row.get('资产类型', '')):
                    return float(row.get('仓位占比', 0) or 0)
    except Exception:
        pass
    return None

def _fetch_fund_info(code: str) -> dict:
    """东财基金档案页：费用/公司/状态。"""
    url = f"https://fundf10.eastmoney.com/jbgk_{code}.html"
    info = {}
    try:
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        for label, key in [
            ("管理费率", "managementFee"),
            ("托管费率", "custodianFee"),
            ("申购费率", "applyFee"),
            ("赎回费率", "redeemFee"),
        ]:
            m = re.search(r'>' + label + r'</th><td>([\d.]+)%', text)
            if not m:
                m = re.search(label + r'.*?([\d.]+)%', text, re.DOTALL)
            if m:
                info[key] = m.group(1)
        # 基金管理人: ...管理人</label><a href="...">公司名</a>...
        m = re.search(r'管理人.*?<a[^>]*>(.*?)</a>', text, re.DOTALL)
        if m:
            val = _clean(m.group(1))
            if val:
                info["fundCompany"] = val
        # Status: search for known keywords
        if "开放申购" in text:
            info["applyStatus"] = "开放申购"
        elif "暂停申购" in text:
            info["applyStatus"] = "暂停申购"
        if "开放赎回" in text:
            info["redeemStatus"] = "开放赎回"
        elif "暂停赎回" in text:
            info["redeemStatus"] = "暂停赎回"
    except Exception:
        pass
    return info


def _build_tc_code(ticker: str, market: str) -> str:
    if market == "hk":
        return f"hk{ticker.zfill(5)}"
    elif market == "us":
        return f"us{ticker.upper()}"
    elif market == "sh":
        return f"sh{ticker}"
    elif market == "sz":
        return f"sz{ticker}"
    return ticker


def fetch_lof_iopv_snapshot() -> dict:
    """获取全部QDII LOF数据。18字段。"""
    now = now_iso()

    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}


    # 从天天基金获取申购状态和限额
    purchase_status_data = _fetch_purchase_status()

    # A类ETF实时涨跌幅
    etf_codes = list({f.get("etf") for f in QDII_FUNDS if f.get("etf") and f.get("estimation") == "A"})
    etf_changes = _fetch_etf_changes(etf_codes)

    all_rows = []
    for fund in QDII_FUNDS:
        code = fund["code"]
        nav_data = _fetch_nav(code)
        nav, nav_date = nav_data["nav"], nav_data["navDate"]
        holdings = _fetch_holdings(code)
        # 更新该基金ETF的净值日价格
        etf_nav_date_prices[fund.get("etf", "")] = _get_etf_nav_date_prices([fund.get("etf", "")], nav_date).get(fund.get("etf", ""))
        fund_info = _fetch_fund_info(code)

        # LOF场内价格
        market = "sh" if code.startswith(("5", "6")) else "sz"
        try:
            q = get_quotes([f"{market}{code}"])
            price = _to_float(q.get(f"{market}{code}", {}).get("price"))
        except Exception:
            price = None

        # 持仓股票价格
        current_prices = {}
        if holdings:
            # HK via get_quotes
            try:
                hk_codes = [_build_tc_code(h["ticker"], h["market"]) for h in holdings if h["market"] == "hk"]
                if hk_codes:
                    hk_q = get_quotes(hk_codes)
                    for h in holdings:
                        if h["market"] != "hk": continue
                        tc = _build_tc_code(h["ticker"], h["market"])
                        if tc in hk_q:
                            cur = hk_q[tc].get("price") or hk_q[tc].get("prev_close")
                            current_prices[h["ticker"]] = cur
                            if hk_q[tc].get("prev_close"):
                                current_prices.setdefault("_prev_close", {})[h["ticker"]] = hk_q[tc]["prev_close"]
            except Exception:
                pass
            # US via urllib (bypass proxy)
            try:
                us_tickers = [h["ticker"] for h in holdings if h["market"] == "us"]
                if us_tickers:
                    us_q = _fetch_us_realtime(us_tickers)
                    for h in holdings:
                        if h["market"] != "us": continue
                        tc = h["ticker"].upper()
                        if tc in us_q:
                            current_prices[h["ticker"]] = us_q[tc].get("price")
                            if us_q[tc].get("prev_close"):
                                current_prices.setdefault("_prev_close", {})[h["ticker"]] = us_q[tc]["prev_close"]
            except Exception:
                pass
            # DB fallback
            missing = [h for h in holdings if not current_prices.get(h["ticker"])]
            if missing:
                try:
                    from data_fetch.lof_db.schema import get_db as _get_db
                    _conn = _get_db()
                    for h in missing:
                        row = _conn.execute("SELECT close FROM stock_prices WHERE ticker=? ORDER BY date DESC LIMIT 1", (h["ticker"],)).fetchone()
                        if row:
                            current_prices[h["ticker"]] = row[0]
                    _conn.close()
                except Exception:
                    pass

        stock_position = _fetch_stock_position(code) or sum(h.get("weight", 0) or 0 for h in holdings)

        # 净值日各持仓价格（用于期间涨跌幅）
        nav_date_prices = {}
        if holdings and nav_date:
            try:
                from data_fetch.lof_db.schema import get_db as _get_db
                _conn = _get_db()
                for h in holdings:
                    row = _conn.execute(
                        "SELECT close FROM stock_prices WHERE ticker=? AND date<=? ORDER BY date DESC LIMIT 1",
                        (h["ticker"], nav_date)
                    ).fetchone()
                    if row:
                        nav_date_prices[h["ticker"]] = row[0]
                _conn.close()
            except Exception:
                pass

        all_rows.append({
            "code": code,
            "name": fund["name"],
            "currency": fund["currency"],
            "nav": nav,
            "shareIncrease": nav_data.get("shareIncrease"),
            "shareTotal": nav_data.get("shareTotal"),
            "price": price,
            "estimation": fund["estimation"],
            "etf": fund.get("etf"),
            "holdings": holdings,
            "currentPrices": current_prices,
            "stockPosition": stock_position,
            "holdingsPrevClose": current_prices.pop("_prev_close", None),
            "navDatePrices": nav_date_prices,
            "navDate": nav_date,
            "currentFxRate": fx_rates.get(fund["currency"], 1.0),
            "applyFee": fund_info.get("applyFee"),
            "applyStatus": purchase_status_data.get(code, {}).get("applyStatus") or fund_info.get("applyStatus"),
            "dailyLimit": purchase_status_data.get(code, {}).get("dailyLimit"),
            "redeemFee": fund_info.get("redeemFee"),
            "redeemStatus": fund_info.get("redeemStatus"),
            "custodianFee": fund_info.get("custodianFee"),
            "fundCompany": fund_info.get("fundCompany"),
            "etfChange": etf_changes.get(fund.get("etf")),
            "etfNavDatePrice": etf_nav_date_prices.get(fund.get("etf")),
        })

    return {
        "success": True,
        "data": all_rows,
        "updateTime": now,
        "source": "eastmoney+tencent",
        "sourceSummary": {"totalRows": len(all_rows), "fxRates": fx_rates},
    }