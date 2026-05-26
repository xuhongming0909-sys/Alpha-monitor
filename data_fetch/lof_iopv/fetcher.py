# -*- coding: utf-8 -*-
"""QDII LOF IOPV 数据获取层。

从东财获取基金净值和持仓，从腾讯获取股价和汇率。
不依赖任何外部第三方数据源。
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

# QDII LOF 基金列表（可扩展）
QDII_FUNDS = [
    {"code": "160644", "name": "南方香港优选FOF", "currency": "HKD", "estimation": "T10"},
    {"code": "164906", "name": "交银中证海外中国互联网", "currency": "USD", "estimation": "T10"},
    {"code": "161128", "name": "汇添富恒生指数", "currency": "HKD", "estimation": "ETF"},
    {"code": "160125", "name": "南方香港优选", "currency": "HKD", "estimation": "T10"},
    {"code": "501225", "name": "全球芯片LOF", "currency": "USD", "estimation": "ETF", "etf": "SMH"},
    {"code": "501312", "name": "汇添富全球互联", "currency": "USD", "estimation": "FOF"},
    {"code": "159202", "name": "华夏恒生科技ETF联接", "currency": "HKD", "estimation": "ETF", "etf": "HSTECH"},
    {"code": "513660", "name": "恒生科技ETF", "currency": "HKD", "estimation": "ETF", "etf": "HSTECH"},
    {"code": "513690", "name": "恒生高股息ETF", "currency": "HKD", "estimation": "ETF", "etf": "HSHKLI"},
    {"code": "520600", "name": "沪港深科技ETF", "currency": "HKD", "estimation": "ETF"},
    {"code": "161130", "name": "纳指LOF", "currency": "USD", "estimation": "ETF", "etf": "QQQ"},
    {"code": "161125", "name": "标普500LOF", "currency": "USD", "estimation": "ETF", "etf": "SPY"},
    {"code": "161126", "name": "标普医疗保健LOF", "currency": "USD", "estimation": "ETF", "etf": "RSPH"},
    {"code": "161127", "name": "标普生物LOF", "currency": "USD", "estimation": "ETF", "etf": "XBI"},
    {"code": "162415", "name": "标普可选消费LOF", "currency": "USD", "estimation": "ETF", "etf": "XLY"},
    {"code": "160140", "name": "标普地产LOF", "currency": "USD", "estimation": "ETF", "etf": "VNQ"},
    {"code": "501300", "name": "广发美国国债LOF", "currency": "USD", "estimation": "ETF", "etf": "AGG"},
    {"code": "164824", "name": "工银印度基金LOF", "currency": "USD", "estimation": "ETF", "etf": "INDA"},
]

_FUND_MAP = {f["code"]: f for f in QDII_FUNDS}


def _to_float(value: Any) -> Optional[float]:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _clean_text(text: Any) -> str:
    if text is None:
        return ""
    text = str(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip() if text else ""


def _fetch_eastmoney_nav(code: str) -> tuple:
    """从东财获取最新净值。返回 (nav, navDate)。"""
    url = f"http://api.fund.eastmoney.com/f10/lsjz?fundCode={code}&pageIndex=1&pageSize=3&callback="
    try:
        resp = SESSION.get(url, timeout=_REQUEST_TIMEOUT)
        data = resp.json()
        items = (data.get("Data") or {}).get("LSJZList") or []
        if items:
            item = items[0]
            nav = _to_float(item.get("DWJZ"))
            nav_date = _clean_text(item.get("FSRQ") or "")[:10]
            return nav, nav_date
    except Exception:
        pass
    return None, None


def _fetch_eastmoney_holdings(code: str) -> List[dict]:
    """从东财获取前十大持仓（解析HTML表格）。"""
    url = f"https://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        resp = SESSION.get(url, timeout=_REQUEST_TIMEOUT)
        text = resp.content.decode("utf-8", errors="ignore")

        # 解析 var apidata={content:"..."}
        m = re.search(r'content\s*:\s*"(.+)"', text, re.DOTALL)
        if not m:
            return []
        html = m.group(1).replace('\\"', '"').replace("\\'", "'")

        # 从HTML表格提取持仓
        holdings = []
        # 匹配 <tr> 行
        rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
        for row_html in rows[1:]:  # skip header
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if len(cells) < 7:
                continue
            # cells: 序号, 股票代码, 股票名称, 最新价, 涨跌幅, 相关资讯, 占净值比例, 持股数, 持仓市值
            ticker = _clean_text(cells[1])
            name = _clean_text(cells[2])
            weight = _to_float(cells[6].replace('%', ''))
            if not ticker or not name:
                continue

            # 判断市场
            if ticker.startswith(("0", "2", "3")):
                market = "sz"
            elif ticker.startswith(("5", "6", "9")):
                market = "sh"
            elif len(ticker) == 5:
                market = "hk"
            else:
                market = "us"

            holdings.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
        return holdings[:10]
    except Exception:
        return []


def _build_tencent_code(ticker: str, market: str) -> str:
    """将持仓股票代码转为腾讯行情代码。"""
    if market == "hk":
        return f"hk{ticker.zfill(5)}"
    elif market == "us":
        return f"us{ticker.upper()}"
    elif market == "sh":
        return f"sh{ticker}"
    elif market == "sz":
        return f"sz{ticker}"
    return ticker


def _fetch_current_prices(holdings: List[dict]) -> dict:
    """批量获取持仓股票当前价格。"""
    if not holdings:
        return {}
    codes = [_build_tencent_code(h["ticker"], h["market"]) for h in holdings]
    try:
        quotes = get_quotes(codes)
        return quotes
    except Exception:
        return {}



def _calc_stock_position(holdings: List[dict]) -> float:
    """从持仓权重推算股票仓位比（Top10持仓占比）。"""
    if not holdings:
        return 0.0
    total = sum(h.get("weight", 0) or 0 for h in holdings)
    return round(total, 2)

def fetch_lof_iopv_snapshot() -> dict:
    """获取 QDII LOF IOPV 估值所需的全部原始数据。"""
    now = now_iso()

    # 1. 获取汇率
    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}

    # 2. 获取各基金净值和持仓
    all_rows = []
    for fund in QDII_FUNDS:
        code = fund["code"]
        nav, nav_date = _fetch_eastmoney_nav(code)
        holdings = _fetch_eastmoney_holdings(code)

        # 获取持仓股票价格
        current_prices = {}
        if holdings:
            quotes = _fetch_current_prices(holdings)
            for h in holdings:
                tc = _build_tencent_code(h["ticker"], h["market"])
                if tc in quotes:
                    current_prices[h["ticker"]] = quotes[tc].get("last") or quotes[tc].get("price")

        # 获取LOF场内价格
        market = "sh" if code.startswith(("5", "6")) else "sz"
        lof_code = f"{market}{code}"
        try:
            lof_quotes = get_quotes([lof_code])
            price_data = lof_quotes.get(lof_code, {})
            price = _to_float(price_data.get("last")) or _to_float(price_data.get("price"))
        except Exception:
            price = None

        # 获取股票仓位比
        stock_position = _calc_stock_position(holdings)

        all_rows.append({
            "code": code,
            "name": fund["name"],
            "currency": fund["currency"],
            "nav": nav,
            "navDate": nav_date,
            "price": price,
            "estimationMethod": fund["estimation"],
            "etf": fund.get("etf"),
            "holdings": holdings,
            "currentPrices": current_prices,
            "stockPosition": stock_position,
            "currentFxRate": fx_rates.get(fund["currency"], 1.0),
        })

    source_summary = {
        "totalRows": len(all_rows),
        "fxRates": fx_rates,
    }

    return {
        "success": True,
        "data": all_rows,
        "updateTime": now,
        "source": "eastmoney+tencent",
        "sourceSummary": source_summary,
    }