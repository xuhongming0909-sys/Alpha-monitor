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
from data_fetch.lof_iopv.fund_classifier import (
    get_fund_class, get_holdings_for_service, get_index_etf_ticker, is_index_fund,
)
from shared.config.script_config import load_config
from shared.time.shanghai_time import now_iso

_REQUEST_TIMEOUT = 15

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fundf10.eastmoney.com/",
})


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
            if arr2 and len(arr2) >= 2:
                result["shareTotal"] = _to_float(arr2[-1])
    except Exception:
        pass
    # fallback: 浠庡熀閲戞鍐甸〉鑾峰彇浠介
    if result["shareTotal"] is None:
        try:
            url3 = f"https://fundf10.eastmoney.com/jbgk_{code}.html"
            text3 = SESSION.get(url3, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
            # 鍖归厤 "浠介瑙勬ā: xxx浜夸唤" 鎴?"xxx涓囦唤"
            for unit, mult in [("浜夸唤", 10000), ("涓囦唤", 1)]:
                m3 = re.search(r"浠介瑙勬ā.*?(\d+[\d,.]*)\s*" + unit, text3)
                if m3:
                    val = _to_float(m3.group(1).replace(",", ""))
                    if val:
                        result["shareTotal"] = val * mult
                        break
        except Exception:
            pass
    return result


def _fetch_holdings(code):
    """Fetch top-10 holdings from eastmoney."""
    url = f"http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        r = SESSION.get(url, timeout=_REQUEST_TIMEOUT)
        text = r.content.decode("utf-8", errors="ignore")
        m = re.search(r'var apidata=\{content:"(.*?)"\}', text, re.DOTALL)
        if not m:
            return []
        html = m.group(1)
        rows = re.findall(r'<td class=\'tor\'>.*?</td>', html, re.DOTALL)
        # 瑙ｆ瀽鎸佷粨琛ㄦ牸
        holdings = []
        # 姣忚鏁版嵁锛氬簭鍙枫€佽偂绁ㄤ唬鐮併€佽偂绁ㄥ悕绉般€佸崰鍑€鍊兼瘮渚嬨€佹寔浠撹偂鏁般€佹寔浠撳競鍊?
        stock_blocks = re.findall(
            r'<td[^>]*>.*?</td>.*?<td[^>]*>.*?</td>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            html, re.DOTALL
        )
        for code_td, name_td, weight_td in stock_blocks:
            ticker = _clean(code_td)
            name = _clean(name_td)
            weight = _to_float(weight_td.replace("%", ""))
            if ticker and weight is not None:
                # 娓偂:5浣嶆暟瀛?00700) 缇庤偂:绾瓧姣?NVDA) A鑲?6浣嶆暟瀛?
                market = "hk" if ticker.isdigit() and len(ticker) >= 4 else \
                         "us" if ticker.isalpha() and len(ticker) <= 5 else \
                         "sz" if ticker.startswith(("0", "3")) and ticker.isdigit() else "sh"
                holdings.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
        return holdings[:10]
    except Exception:
        return []


def _fetch_stock_position(code):
    """Fetch total non-cash position % from akshare (total position = 100% - cash)."""
    try:
        import akshare as ak
        from datetime import datetime
        now = datetime.now()
        q = (now.month - 1) // 3
        q_month = q * 3
        if q_month == 0:
            q_month = 12
            q_year = now.year - 1
        else:
            q_year = now.year
        date_str = f"{q_year}{q_month:02d}31"
        df = ak.fund_individual_detail_hold_xq(symbol=code, date=date_str)
        if df is not None and not df.empty:
            cash_pct = 0.0
            for _, row in df.iterrows():
                asset_type = str(row.iloc[0])
                if "鐜伴噾" in asset_type:
                    cash_pct += float(row.iloc[1])
            return round(100.0 - cash_pct, 2)
    except Exception:
        pass
    return None


def _fetch_fund_info(code):
    """Fetch fund info: applyFee, redeemFee, custodianFee, fundCompany, applyStatus, redeemStatus."""
    info = {}
    try:
        url = f"https://fundf10.eastmoney.com/jbgk_{code}.html"
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r"鎵樼璐圭巼.*?(\d+\.\d+%)", text)
        if m:
            info["custodianFee"] = m.group(1)
        m = re.search(r"鐢宠喘璐圭巼.*?(\d+\.\d+%)", text)
        if m:
            info["applyFee"] = m.group(1)
        m = re.search(r"璧庡洖璐圭巼.*?(\d+\.\d+%)", text)
        if m:
            info["redeemFee"] = m.group(1)
        # 鍩洪噾鍏徃 - 浠庡熀閲戠鐞嗕汉瀛楁鎻愬彇
        m_company = re.search(r"鍩洪噾绠＄悊浜?{0,50}?<a[^>]*>([^<]+)</a>", text)
        if m_company:
            val = _clean(m_company.group(1))
            if val and val != "鍩洪噾浠ｇ爜":
                info["fundCompany"] = val
        # 鐢宠喘鐘舵€侊細闄愬ぇ棰?> 鏆傚仠鐢宠喘 > 寮€鏀剧敵璐?
        m_limit = re.search(r"鍗曟棩绱璐拱涓婇檺([\d,.]+)\s*(涓囧厓?|鍏?", text)
        if "闄愬ぇ棰? in text:
            info["applyStatus"] = "闄愬ぇ棰?
            if m_limit:
                raw = float(m_limit.group(1).replace(",", ""))
                unit = m_limit.group(2)
                info["dailyLimit"] = raw * 10000 if unit in ("涓?, "涓囧厓") else raw
        elif "鏆傚仠鐢宠喘" in text:
            info["applyStatus"] = "鏆傚仠鐢宠喘"
        elif "寮€鏀剧敵璐? in text:
            info["applyStatus"] = "寮€鏀剧敵璐?
        if "寮€鏀捐祹鍥? in text:
            info["redeemStatus"] = "寮€鏀捐祹鍥?
        elif "鏆傚仠璧庡洖" in text:
            info["redeemStatus"] = "鏆傚仠璧庡洖"
    except Exception:
        pass
    return info


def _fetch_purchase_status():
    """鎵归噺鑾峰彇鍩洪噾鐢宠喘鐘舵€侊紙涓滄柟璐㈠瘜鎵归噺API锛?""
    result = {}
    try:
        url = "https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=8"
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        # API杩斿洖 var db={datas:[[code,name,type,nav,date,applyStatus,...,limit,...],...]}
        m = re.search(r"var db=\{datas:(\[.*\]),record:", text, re.DOTALL)
        if not m:
            return result
        arr = _json.loads(m.group(1))
        for item in arr:
            code = str(item[0]) if len(item) > 0 else ""
            if not code:
                continue
            status = str(item[5]) if len(item) > 5 else ""
            limit = item[9] if len(item) > 9 else None
            result[code] = {
                "applyStatus": status,
                "dailyLimit": _to_float(limit),
            }
    except Exception:
        pass
    return result



def _build_tc_code(ticker, market):
    """鏋勫缓鑵捐琛屾儏浠ｇ爜"""
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

    all_rows = []
    for fund in funds:
        # 跳过已删除的基金
        if fund.get('code') == '160125':
            continue
        code = fund["code"]
        nav_data = _fetch_nav(code)
        nav, nav_date = nav_data["nav"], nav_data["navDate"]
        # 鎸佷粨鑾峰彇: 鎸囨暟鍨嬬敤ETF鏄犲皠, 涓诲姩鍨嬬敤API/PDF
        fund_class = get_fund_class(code)
        # 缁熶竴浣跨敤 get_holdings_for_service锛堝惈 hardcoded fallback锛夛紝涓嶅啀浠呴檺 index
        holdings_raw = get_holdings_for_service(code)
        if holdings_raw:
            holdings = [{"ticker": h["ticker"], "name": h.get("name", ""), "weight": h["weight"], "market": h["market"].lower()} for h in holdings_raw]
        else:
            holdings = _fetch_holdings(code)

        fund_info = _fetch_fund_info(code)
        market = "sh" if code.startswith(("5", "6")) else "sz"
        current_prices = {}
        price = None
        if holdings:
            # 娓偂瀹炴椂琛屾儏
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
            # 缇庤偂瀹炴椂琛屾儏
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

        # 鍑€鍊兼姭闇叉棩鑲′环锛堢敤浜嶪OPV璁＄畻鐨勫熀鍑嗕环鏍硷級
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

        # LOF鍦哄唴浠锋牸
        try:
            tc_code = _build_tc_code(code, market)
            q = get_quotes([tc_code])
            if q and tc_code in q:
                price = q[tc_code].get("price")
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
            "holdings": holdings,
            "currentPrices": current_prices,
            "stockPosition": stock_position,
            "holdingsPrevClose": current_prices.get("_prev_close"),
            "navDatePrices": nav_date_prices,
            "navDate": nav_date,
            "currentFxRate": fx_rates.get(fund["currency"]),
            "applyFee": fund_info.get("applyFee"),
            "applyStatus": purchase_status_data.get(code, {}).get("applyStatus") or fund_info.get("applyStatus"),
            "dailyLimit": purchase_status_data.get(code, {}).get("dailyLimit") or fund_info.get("dailyLimit"),
            "redeemFee": fund_info.get("redeemFee"),
            "redeemStatus": fund_info.get("redeemStatus"),
            "custodianFee": fund_info.get("custodianFee"),
            "fundCompany": fund_info.get("fundCompany"),
        })

    return {
        "success": True,
        "data": all_rows,
        "updateTime": now,
        "source": "eastmoney+tencent",
        "sourceSummary": {"totalRows": len(all_rows), "fxRates": fx_rates},
    }

