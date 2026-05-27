# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF IOPV data source - fetch NAV, holdings, prices, purchase status from eastmoney/tencent/xueqiu
# INDEX section 9.3 file summary index
"""LOF IOPV data source layer.

Responsibilities: fetch raw data from eastmoney/tencent/xueqiu APIs.
No business calculation - that belongs to strategy/lof_iopv/.
"""

from __future__ import annotations

import json as _json
import math
import re
import urllib.request
from typing import Any, Dict, List, Optional

import requests

from shared.market_service import get_fx_rates, get_quotes
from shared.config.script_config import load_config
from shared.time.shanghai_time import now_iso

_REQUEST_TIMEOUT = 15

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fundf10.eastmoney.com/",
})
_ETF_SESSION = requests.Session()
_ETF_SESSION.trust_env = False
_ETF_SESSION.proxies = {"http": None, "https": None}


def _get_etf_nav_date_prices(etf_codes, nav_date):
    """获取ETF在净值日的价格（用于期间涨跌幅）"""
    if not nav_date or not etf_codes:
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


def _load_fund_list():
    """Load fund list from config.yaml. Raises on failure."""
    cfg = load_config()
    plugins = cfg.get("data_fetch", {}).get("plugins", {})
    lof_cfg = plugins.get("lof_arbitrage", plugins.get("lof_iopv", {}))
    funds = lof_cfg.get("funds")
    if not funds or not isinstance(funds, list) or len(funds) == 0:
        raise RuntimeError("No funds configured in config.yaml under lof_arbitrage.funds")
    return funds


def _to_float(v):
    try:
        r = float(v)
        return r if math.isfinite(r) else None
    except (TypeError, ValueError):
        return None


def _clean(text):
    if text is None:
        return ""
    return re.sub(r"<[^>]+>", "", str(text)).strip()


def _fetch_us_realtime(codes):
    """Batch fetch US stock realtime via tencent (urllib direct, bypass proxy)."""
    if not codes:
        return {}
    query = ",".join("us" + c for c in codes)
    url = "https://qt.gtimg.cn/q=" + query
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("gbk", errors="ignore")
    except Exception:
        return {}
    result = {}
    for line in text.strip().split(";"):
        line = line.strip()
        if len(line) < 20:
            continue
        key = line.split("=")[0].replace("v_", "")
        code = key.replace("us", "")
        data = line.split("\"")[1].split("~") if "\"" in line else []
        if len(data) > 35:
            result[code] = {
                "price": _to_float(data[3]),
                "prev_close": _to_float(data[4]),
                "change_pct": _to_float(data[32]),
            }
    return result


def _fetch_etf_changes(etf_codes):
    """Fetch ETF realtime change%. Eastmoney kline first, tencent fallback."""
    if not etf_codes:
        return {}
    changes = {}
    for ticker in etf_codes:
        try:
            url = (
                f"https://push2his.eastmoney.com/api/qt/stock/kline/get"
                f"?secid=107.{ticker}&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56"
                f"&klt=101&fqt=0&end=20500101&lmt=2"
            )
            resp = _ETF_SESSION.get(url, timeout=10)
            data = resp.json()
            klines = data.get("data", {}).get("klines", [])
            if len(klines) >= 2:
                prev_close = float(klines[-2].split(",")[2])
                cur_close = float(klines[-1].split(",")[2])
                if prev_close > 0:
                    changes[ticker] = (cur_close / prev_close - 1) * 100
                    continue
        except Exception:
            pass
        # tencent fallback
        try:
            qt_codes = [f"us{ticker}"]
            resp = _ETF_SESSION.get(f"https://qt.gtimg.cn/q={','.join(qt_codes)}", timeout=10)
            text = resp.content.decode("gbk", errors="ignore")
            for line in text.strip().split(";"):
                parts = line.split("~")
                if len(parts) > 4:
                    p = _to_float(parts[4])
                    c = _to_float(parts[3])
                    if p and p > 0 and c:
                        changes[ticker] = (c / p - 1) * 100
        except Exception:
            pass
    return changes


def _fetch_nav(code):
    """Fetch NAV from eastmoney. Returns {nav, navDate, shareIncrease, shareTotal}."""
    result = {"nav": None, "navDate": None, "shareIncrease": None, "shareTotal": None}
    url = f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=3&callback="
    try:
        r = SESSION.get(url, timeout=_REQUEST_TIMEOUT)
        items = r.json()["Data"]["LSJZList"]
        if items:
            result["nav"] = _to_float(items[0].get("DWJZ"))
            result["navDate"] = _clean(items[0].get("FSRQ"))[:10]
    except Exception:
        pass
    # shareIncrease/Total from pingzhongdata
    try:
        url2 = f"https://fund.eastmoney.com/pingzhongdata/{code}.js"
        text = SESSION.get(url2, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r"Data_netWorthTrend\s*=\s*(\[.*?\]);", text, re.DOTALL)
        if m:
            arr = _json.loads(m.group(1))
            if arr:
                latest = arr[-1]
                result["shareIncrease"] = _to_float(latest.get("equityReturn"))
        m2 = re.search(r"Data_fluctuationTrend\s*=\s*(\[.*?\]);", text, re.DOTALL)
        if m2:
            arr2 = _json.loads(m2.group(1))
            if arr2:
                result["shareTotal"] = _to_float(arr2[-1].get("total"))
    except Exception:
        pass
    return result


def _fetch_holdings(code):
    """Fetch top 10 holdings from eastmoney."""
    url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r'content:"(.*?)",arryear', text, re.DOTALL)
        if not m:
            return []
        rows = re.findall(
            r"<tr><td>(\d+)</td>.*?<a href=[^>]+>([A-Z0-9]+)</a>.*?<a href=[^>]+>([^<]+)</a>.*?<td[^>]*>([\d.]+)%</td>",
            m.group(1), re.DOTALL,
        )
        holdings = []
        for _, ticker_raw, name_raw, weight_raw in rows:
            ticker = _clean(ticker_raw)
            name = _clean(name_raw)
            weight = _to_float(weight_raw)
            market = "hk" if (ticker.isdigit() and len(ticker) == 5) else "us"
            holdings.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
        return holdings[:10]
    except Exception:
        return []


def _fetch_purchase_status():
    """Fetch purchase status and daily limit from eastmoney for all funds."""
    result = {}
    try:
        url = "https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx"
        params = {"t": "8", "page": "1,50000", "js": "reData", "sort": "fcode,asc"}
        r = SESSION.get(url, params=params, timeout=_REQUEST_TIMEOUT)
        text = r.text.strip().replace("var reData=", "")
        m = re.search(r"datas:\s*(\[.*?\])\s*,\s*\w+:", text, re.DOTALL)
        if not m:
            return result
        arr = _json.loads(m.group(1))
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


def _fetch_stock_position(code):
    """Fetch stock position ratio from xueqiu."""
    try:
        import akshare as ak
        from datetime import datetime
        date = datetime.now().strftime("%Y%m%d")
        df = ak.fund_individual_detail_hold_xq(symbol=code, date=date)
        if df is not None and not df.empty:
            for _, row in df.iterrows():
                if "\u80a1\u7968" in str(row.get("\u8d44\u4ea7\u7c7b\u578b", "")):
                    val = row.get("\\u4ed3\\u4f4d\\u5360\\u6bd4"); return float(val) if val else None
    except Exception:
        pass
    return None


def _fetch_fund_info(code):
    """Fetch fund info from eastmoney fund page."""
    url = f"https://fundf10.eastmoney.com/jbgk_{code}.html"
    info = {}
    try:
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        for label, key in [
            ("\u7ba1\u7406\u8d39\u7387", "managementFee"),
            ("\u6258\u7ba1\u8d39\u7387", "custodianFee"),
            ("\u7533\u8d2d\u8d39\u7387", "applyFee"),
            ("\u8d4e\u56de\u8d39\u7387", "redeemFee"),
        ]:
            m = re.search(r">" + label + r"</th><td>([\d.]+)%", text)
            if not m:
                m = re.search(label + r".*?([\d.]+)%", text, re.DOTALL)
            if m:
                info[key] = m.group(1)
        m = re.search(r"\u7ba1\u7406\u4eba.*?<a[^>]*>(.*?)</a>", text, re.DOTALL)
        if m:
            val = _clean(m.group(1))
            if val:
                info["fundCompany"] = val
        if "\u5f00\u653e\u7533\u8d2d" in text:
            info["applyStatus"] = "\u5f00\u653e\u7533\u8d2d"
        elif "\u6682\u505c\u7533\u8d2d" in text:
            info["applyStatus"] = "\u6682\u505c\u7533\u8d2d"
        if "\u5f00\u653e\u8d4e\u56de" in text:
            info["redeemStatus"] = "\u5f00\u653e\u8d4e\u56de"
        elif "\u6682\u505c\u8d4e\u56de" in text:
            info["redeemStatus"] = "\u6682\u505c\u8d4e\u56de"
    except Exception:
        pass
    return info


def _build_tc_code(ticker, market):
    if market == "hk":
        return "hk" + ticker.zfill(5)
    elif market == "us":
        return "us" + ticker.upper()
    elif market == "sh":
        return "sh" + ticker
    elif market == "sz":
        return "sz" + ticker
    return ticker


def build_lof_snapshot():
    """Fetch all QDII LOF data. Main entry point."""
    now = now_iso()

    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}

    funds = _load_fund_list()
    purchase_status_data = _fetch_purchase_status()

    etf_codes = list({f.get("etf") for f in funds if f.get("etf") and f.get("estimation") == "A"})
    etf_changes = _fetch_etf_changes(etf_codes)

    all_rows = []
    etf_nav_date_prices = {}
    for fund in funds:
        code = fund["code"]
        nav_data = _fetch_nav(code)
        nav, nav_date = nav_data["nav"], nav_data["navDate"]
        holdings = _fetch_holdings(code)
        fund_info = _fetch_fund_info(code)
        # A类ETF净值日价格
        if fund.get("etf") and fund.get("estimation") == "A":
            etf_nav_date_prices[fund["etf"]] = _get_etf_nav_date_prices([fund["etf"]], nav_date).get(fund["etf"])

        market = "sh" if code.startswith(("5", "6")) else "sz"
        try:
            q = get_quotes([f"{market}{code}"])
            price = _to_float(q.get(f"{market}{code}", {}).get("price"))
        except Exception:
            price = None

        current_prices = {}
        if holdings:
            try:
                hk_codes = [_build_tc_code(h["ticker"], h["market"]) for h in holdings if h["market"] == "hk"]
                if hk_codes:
                    hk_q = get_quotes(hk_codes)
                    for h in holdings:
                        if h["market"] != "hk":
                            continue
                        tc = _build_tc_code(h["ticker"], h["market"])
                        if tc in hk_q:
                            cur = hk_q[tc].get("price") or hk_q[tc].get("prev_close")
                            current_prices[h["ticker"]] = cur
                            if hk_q[tc].get("prev_close"):
                                current_prices.setdefault("_prev_close", {})[h["ticker"]] = hk_q[tc]["prev_close"]
            except Exception:
                pass
            try:
                us_tickers = [h["ticker"] for h in holdings if h["market"] == "us"]
                if us_tickers:
                    us_q = _fetch_us_realtime(us_tickers)
                    for h in holdings:
                        if h["market"] != "us":
                            continue
                        tc = h["ticker"].upper()
                        if tc in us_q:
                            current_prices[h["ticker"]] = us_q[tc].get("price")
                            if us_q[tc].get("prev_close"):
                                current_prices.setdefault("_prev_close", {})[h["ticker"]] = us_q[tc]["prev_close"]
            except Exception:
                pass
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

        nav_date_prices = {}
        if holdings and nav_date:
            try:
                from data_fetch.lof_db.schema import get_db as _get_db
                _conn = _get_db()
                for h in holdings:
                    row = _conn.execute(
                        "SELECT close FROM stock_prices WHERE ticker=? AND date<=? ORDER BY date DESC LIMIT 1",
                        (h["ticker"], nav_date),
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
            "currentFxRate": fx_rates.get(fund["currency"]),
            "applyFee": fund_info.get("applyFee"),
            "applyStatus": purchase_status_data.get(code, {}).get("applyStatus") or fund_info.get("applyStatus"),
            "dailyLimit": purchase_status_data.get(code, {}).get("dailyLimit"),
            "redeemFee": fund_info.get("redeemFee"),
            "redeemStatus": fund_info.get("redeemStatus"),
            "custodianFee": fund_info.get("custodianFee"),
            "fundCompany": fund_info.get("fundCompany"),
            "etfChange": etf_changes.get(fund.get("etf")),
            "etfNavDatePrice": etf_nav_date_prices.get(fund.get("etf")) if fund.get("estimation") == "A" else None,
        })

    return {
        "success": True,
        "data": all_rows,
        "updateTime": now,
        "source": "eastmoney+tencent",
        "sourceSummary": {"totalRows": len(all_rows), "fxRates": fx_rates},
    }
