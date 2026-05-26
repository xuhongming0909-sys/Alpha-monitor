# -*- coding: utf-8 -*-
"""LOF IOPV 数据获取层。

从集思录、东财、腾讯获取 LOF 基金原始数据。
不依赖任何旧 lof_arbitrage 代码。
"""

from __future__ import annotations

import math
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from shared.config.script_config import get_config
from shared.market_service import get_fx_rates, get_quotes
from shared.time.shanghai_time import now_iso

_CONFIG = get_config()
_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("lof_iopv") or {})

REQUEST_TIMEOUT = max(5, int(_FETCH_CONFIG.get("request_timeout_ms") or 20000) / 1000)
JISILU_COOKIE = str(_FETCH_CONFIG.get("jisilu_cookie") or "").strip()
SOURCE_REFERER = "https://www.jisilu.cn/"

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": SOURCE_REFERER,
})

# 集思录分组配置
GROUP_CONFIG = {
    "qdii": {
        "label": "QDII",
        "api_url": "https://www.jisilu.cn/data/qdii/qdii_list/A",
        "page_url": "https://www.jisilu.cn/data/qdii/#qdiia",
    },
}


def _to_float(value: Any) -> Optional[float]:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _fetch_jisilu_group(group_key: str) -> List[dict]:
    """从集思录 API 获取一组 LOF 数据。"""
    cfg = GROUP_CONFIG[group_key]
    url = cfg["api_url"]
    params = {"___jsl": "L3z1f8", "rp": "50", "page": "1"}

    if JISILU_COOKIE:
        SESSION.cookies.set("jisilu_session_ticket", JISILU_COOKIE, domain="www.jisilu.cn")

    try:
        resp = SESSION.get(url, params=params, timeout=REQUEST_TIMEOUT)
        data = resp.json()
        raw_rows = data.get("rows", [])
        result = []
        for row in raw_rows:
            cell = row.get("cell") or row
            code = _clean_text(cell.get("fund_id") or cell.get("id"))
            currency = _clean_text(cell.get("currency")).upper() or "CNY"
            if currency not in ("CNY", "USD", "HKD"):
                currency = "USD"
            market = "sz" if code.startswith(("16", "15")) else "sh"

            result.append({
                "code": code,
                "name": _clean_text(cell.get("fund_nm") or cell.get("name")),
                "market": market,
                "marketGroup": group_key,
                "currency": currency,
                "price": _to_float(cell.get("price")),
                "nav": _to_float(cell.get("nav")),
                "navDate": _clean_text(cell.get("nav_dt") or "")[:10],
                "changeRate": _to_float(cell.get("change_rt")),
                "turnoverWan": _to_float(cell.get("volume")),
                "shareAmountWan": _to_float(cell.get("amount")),
                "shareAmountIncreaseWan": _to_float(cell.get("amount_increase")),
                "indexName": _clean_text(cell.get("index_nm")),
                "indexId": _clean_text(cell.get("index_id")),
                "indexIncreaseRate": _to_float(cell.get("index_increase_rt")),
                "applyFee": _to_float(cell.get("apply_fee")),
                "applyStatus": _clean_text(cell.get("apply_status")),
                "redeemFee": _to_float(cell.get("redeem_fee")),
                "redeemStatus": _clean_text(cell.get("redeem_status")),
                "custodianFee": _to_float(cell.get("fee")),
                "fundCompany": _clean_text(cell.get("issuer_nm")),
                "currentFxRate": None,
                "holdings": None,
                "stockPosition": None,
            })
        return result
    except Exception:
        return []


def _fetch_holdings(code: str) -> List[dict]:
    """从东财 F10 获取前十大持仓。"""
    url = f"http://fund.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10"
    try:
        import json
        resp = SESSION.get(url, timeout=REQUEST_TIMEOUT)
        text = resp.content.decode("utf-8", errors="ignore")
        json_match = re.search(r'var\s+jjcc\s*=\s*(\[.*?\]);', text, re.DOTALL)
        if not json_match:
            return []
        data = json.loads(json_match.group(1))
        holdings = []
        for item in data[:10]:
            ticker = _clean_text(item.get("gpdm") or item.get("stockCode"))
            name = _clean_text(item.get("gpjc") or item.get("stockName"))
            weight = _to_float(item.get("zjzbl") or item.get("ratio"))
            market = "us"
            if ticker.startswith(("0", "2", "3")):
                market = "sz"
            elif ticker.startswith(("5", "6", "9")):
                market = "sh"
            elif len(ticker) == 5:
                market = "hk"
            holdings.append({"ticker": ticker, "name": name, "weight": weight, "market": market})
        return holdings
    except Exception:
        return []


def _fetch_stock_position(code: str) -> Optional[float]:
    """从东财 pingzhongdata 获取仓位比。"""
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    try:
        import json
        resp = SESSION.get(url, timeout=REQUEST_TIMEOUT)
        text = resp.content.decode("utf-8", errors="ignore")
        for var_name in ("stockPositionNew", "stockPosition"):
            match = re.search(rf'var\s+{var_name}[^=]*=\s*(\[.*?\]);', text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                if data and isinstance(data[-1], list) and len(data[-1]) >= 2:
                    return _to_float(data[-1][1])
        return None
    except Exception:
        return None


def fetch_lof_iopv_snapshot() -> dict:
    """获取 LOF IOPV 估值所需的全部原始数据。"""
    now = now_iso()

    # 1. 获取实时汇率
    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}

    # 2. 从集思录获取 QDII 数据
    all_rows = []
    all_rows.extend(_fetch_jisilu_group("qdii"))

    # 3. 补充持仓和仓位数据
    for row in all_rows:
        row["holdings"] = _fetch_holdings(row["code"])
        row["stockPosition"] = _fetch_stock_position(row["code"])

    # 4. 补充汇率
    for row in all_rows:
        currency = row.get("currency", "CNY")
        row["currentFxRate"] = fx_rates.get(currency, 1.0)

    source_summary = {
        "totalRows": len(all_rows),
        "qdiiCount": sum(1 for r in all_rows if r["marketGroup"] == "qdii"),
        "fxRates": fx_rates,
        "cookieConfigured": bool(JISILU_COOKIE),
    }

    return {
        "success": True,
        "data": all_rows,
        "updateTime": now,
        "source": "jisilu+eastmoney+tencent",
        "sourceSummary": source_summary,
    }