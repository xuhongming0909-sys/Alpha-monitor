# -*- coding: utf-8 -*-
"""QDII LOF IOPV 数据获取层 - 18字段完整版。

东财净值+持仓+基金档案 | 腾讯行情+汇率。
"""

from __future__ import annotations

import json as _json
import math
import re
from typing import Any, Dict, List, Optional

import requests

from shared.market_service import get_fx_rates, get_quotes
from shared.time.shanghai_time import now_iso

_REQUEST_TIMEOUT = 15

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fundf10.eastmoney.com/",
})

# QDII LOF 基金列表: estimation = "A"(指数跟踪) / "B"(T10持仓)
QDII_FUNDS = [
    {"code": "160644", "name": "港美互联LOF", "currency": "HKD", "estimation": "B"},
    {"code": "164906", "name": "中概互联LOF", "currency": "USD", "estimation": "B"},
    {"code": "161128", "name": "标普信息科技LOF", "currency": "USD", "estimation": "A", "etf": "XLK"},
    {"code": "160125", "name": "南方香港LOF", "currency": "HKD", "estimation": "B"},
    {"code": "501225", "name": "全球芯片LOF", "currency": "USD", "estimation": "A", "etf": "SMH"},
    {"code": "501312", "name": "全球互联LOF", "currency": "USD", "estimation": "B"},
    {"code": "159202", "name": "恒生科技联接", "currency": "HKD", "estimation": "A", "etf": "HSTECH"},
    {"code": "513660", "name": "恒生科技ETF", "currency": "HKD", "estimation": "A", "etf": "HSTECH"},
    {"code": "513690", "name": "恒生高股息ETF", "currency": "HKD", "estimation": "A", "etf": "HSHKLI"},
    {"code": "520600", "name": "沪港深科技ETF", "currency": "HKD", "estimation": "A"},
    {"code": "161130", "name": "纳指LOF", "currency": "USD", "estimation": "A", "etf": "QQQ"},
    {"code": "161125", "name": "标普500LOF", "currency": "USD", "estimation": "A", "etf": "SPY"},
    {"code": "161126", "name": "标普医疗LOF", "currency": "USD", "estimation": "A", "etf": "RSPH"},
    {"code": "161127", "name": "标普生物LOF", "currency": "USD", "estimation": "A", "etf": "XBI"},
    {"code": "162415", "name": "标普可选消费LOF", "currency": "USD", "estimation": "A", "etf": "XLY"},
    {"code": "160140", "name": "标普地产LOF", "currency": "USD", "estimation": "A", "etf": "VNQ"},
    {"code": "501300", "name": "美国国债LOF", "currency": "USD", "estimation": "A", "etf": "AGG"},
    {"code": "164824", "name": "工银印度LOF", "currency": "USD", "estimation": "A", "etf": "INDA"},
]


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


def _fetch_nav(code: str) -> tuple:
    """东财净值API。返回 (nav, navDate)。"""
    url = f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=3&callback="
    try:
        data = SESSION.get(url, timeout=_REQUEST_TIMEOUT).json()
        items = (data.get("Data") or {}).get("LSJZList") or []
        if items:
            return _to_float(items[0].get("DWJZ")), _clean(items[0].get("FSRQ"))[:10]
    except Exception:
        pass
    return None, None


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
        # 基金公司: 搜索 "基金管理人" 后面的公司名
        m = re.search(r'基金管理人.*?<a[^>]*>(.*?)<', text, re.DOTALL)
        if not m:
            m = re.search(r'基金公司.*?<a[^>]*>(.*?)<', text, re.DOTALL)
        if m:
            val = _clean(m.group(1))
            if val and "基金" not in val:
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

    all_rows = []
    for fund in QDII_FUNDS:
        code = fund["code"]
        nav, nav_date = _fetch_nav(code)
        holdings = _fetch_holdings(code)
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
            try:
                codes = [_build_tc_code(h["ticker"], h["market"]) for h in holdings]
                quotes = get_quotes(codes)
                for h in holdings:
                    tc = _build_tc_code(h["ticker"], h["market"])
                    if tc in quotes:
                        current_prices[h["ticker"]] = quotes[tc].get("price")
            except Exception:
                pass

        stock_position = sum(h.get("weight", 0) or 0 for h in holdings)

        all_rows.append({
            "code": code,
            "name": fund["name"],
            "currency": fund["currency"],
            "nav": nav,
            "navDate": nav_date,
            "price": price,
            "estimation": fund["estimation"],
            "etf": fund.get("etf"),
            "holdings": holdings,
            "currentPrices": current_prices,
            "stockPosition": stock_position,
            "currentFxRate": fx_rates.get(fund["currency"], 1.0),
            "applyFee": fund_info.get("applyFee"),
            "applyStatus": fund_info.get("applyStatus"),
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