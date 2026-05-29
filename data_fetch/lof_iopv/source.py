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
        # 解析持仓表格
        holdings = []
        # 每行数据：序号、股票代码、股票名称、占净值比例、持仓股数、持仓市值
        stock_blocks = re.findall(
            r'<td[^>]*>.*?</td>.*?<td[^>]*>.*?</td>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>.*?<td[^>]*>(.*?)</td>',
            html, re.DOTALL
        )
        for code_td, name_td, weight_td in stock_blocks:
            ticker = _clean(code_td)
            name = _clean(name_td)
            weight = _to_float(weight_td.replace("%", ""))
            if ticker and weight is not None:
                # 港股:5位数字(00700) 美股:纯字母(NVDA) A股:6位数字
                market = "hk" if ticker.isdigit() and len(ticker) >= 4 else \
                         "us" if ticker.isalpha() and len(ticker) <= 5 else \
                         "sz" if ticker.startswith(("0", "3")) and ticker.isdigit() else "sh"
                holdings.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
        return holdings[:10]
    except Exception:
        return []


def _fetch_stock_position(code):
    """Fetch actual stock position % from xueqiu."""
    try:
        url = f"https://stock.xueqiu.com/v5/fund/portfolio/stock.json?symbol={code}&size=10"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        items = data.get("data", {}).get("list", [])
        if items:
            total = sum(i.get("percent", 0) or 0 for i in items)
            return round(total, 2)
    except Exception:
        pass
    return None


def _fetch_fund_info(code):
    """Fetch fund info: applyFee, redeemFee, custodianFee, fundCompany, applyStatus, redeemStatus."""
    info = {}
    try:
        url = f"https://fundf10.eastmoney.com/jbgk_{code}.html"
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r"管理费率.*?(\d+\.\d+%)", text)
        if m:
            info["custodianFee"] = m.group(1)
        m = re.search(r"申购费率.*?(\d+\.\d+%)", text)
        if m:
            info["applyFee"] = m.group(1)
        m = re.search(r"赎回费率.*?(\d+\.\d+%)", text)
        if m:
            info["redeemFee"] = m.group(1)
        # 基金公司
        for key in ["基金公司", "基金管理人"]:
            m = re.search(key + r".*?<a[^>]*>(.*?)</a>", text, re.DOTALL)
            if m:
                val = _clean(m.group(1))
                if val:
                    info["fundCompany"] = val
                    break
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


def _fetch_purchase_status():
    """批量获取基金申购状态（东方财富批量API）"""
    result = {}
    try:
        url = "https://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=8"
        text = SESSION.get(url, timeout=_REQUEST_TIMEOUT).content.decode("utf-8", errors="ignore")
        m = re.search(r"var r = (\[.*?\]);", text, re.DOTALL)
        if not m:
            return result
        arr = _json.loads(m.group(1))
        for item in arr:
            code = str(item.get("code", ""))
            if not code:
                continue
            status = item.get("applyStatus", "")
            limit = item.get("applyLimit")
            result[code] = {
                "applyStatus": status,
                "dailyLimit": _to_float(limit),
            }
    except Exception:
        pass
    return result


def _build_tc_code(ticker, market):
    """构建腾讯行情代码"""
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
        code = fund["code"]
        nav_data = _fetch_nav(code)
        nav, nav_date = nav_data["nav"], nav_data["navDate"]
        # 持仓获取: 指数型用ETF映射, 主动型用API/PDF
        fund_class = get_fund_class(code)
        # 统一使用 get_holdings_for_service（含 hardcoded fallback），不再仅限 index
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
            # 港股实时行情
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
            # 美股实时行情
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

        # 净值披露日股价（用于IOPV计算的基准价格）
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

        # LOF场内价格
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
            "dailyLimit": purchase_status_data.get(code, {}).get("dailyLimit"),
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
