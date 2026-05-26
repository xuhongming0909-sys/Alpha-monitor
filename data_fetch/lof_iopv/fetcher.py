# -*- coding: utf-8 -*-
"""LOF IOPV 数据获取层。

复用旧 lof_arbitrage 的集思录抓取逻辑，额外补充东财持仓和仓位数据。
不做任何估值计算（由 strategy 层负责）。
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional

import requests

from shared.config.script_config import get_config
from shared.market_service import get_fx_rates
from shared.time.shanghai_time import now_iso

# 复用旧的集思录抓取逻辑
from data_fetch.lof_arbitrage.source import get_lof_arbitrage_source_snapshot

_CONFIG = get_config()
_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("lof_iopv") or {})
REQUEST_TIMEOUT = max(5, int(_FETCH_CONFIG.get("request_timeout_ms") or 20000) / 1000)

_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
})


def _to_float(value: Any) -> Optional[float]:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _safe_text(resp: requests.Response) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return resp.content.decode(enc)
        except Exception:
            continue
    return resp.text


def _fetch_holdings(code: str) -> List[dict]:
    """从东财 F10 获取前十大持仓。"""
    url = f"http://fund.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={code}&topline=10&year=&month=&rt=0.{code}"
    try:
        resp = _SESSION.get(url, timeout=REQUEST_TIMEOUT)
        text = _safe_text(resp)
        holdings = []
        # 解析 JSON 格式的持仓数据
        import json
        json_match = re.search(r'var\s+jjcc\s*=\s*(\[.*?\]);', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                for item in data[:10]:
                    ticker = str(item.get("gpdm") or item.get("stockCode") or "").strip()
                    name = str(item.get("gpjc") or item.get("stockName") or "").strip()
                    weight = _to_float(item.get("zjzbl") or item.get("ratio"))
                    market = "us"
                    if ticker.startswith(("0", "2", "3")):
                        market = "sz"
                    elif ticker.startswith(("5", "6", "9")):
                        market = "sh"
                    elif len(ticker) == 5:
                        market = "hk"
                    elif not ticker.startswith(("I", "US")):
                        market = "us"
                    holdings.append({
                        "ticker": ticker,
                        "name": name,
                        "weight": weight,
                        "market": market,
                    })
            except (json.JSONDecodeError, TypeError):
                pass
        return holdings
    except Exception:
        return []


def _fetch_stock_position(code: str) -> Optional[float]:
    """从东财 pingzhongdata 获取仓位比。"""
    url = f"http://fund.eastmoney.com/pingzhongdata/{code}.js"
    try:
        resp = _SESSION.get(url, timeout=REQUEST_TIMEOUT)
        text = _safe_text(resp)
        import json
        for var_name in ("stockPositionNew", "stockPosition"):
            match = re.search(rf'var\s+{var_name}[^=]*=\s*(\[.*?\]);', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    if data and isinstance(data[-1], list) and len(data[-1]) >= 2:
                        return _to_float(data[-1][1])
                except (json.JSONDecodeError, TypeError):
                    pass
        return None
    except Exception:
        return None


def _fetch_fund_company(code: str) -> Optional[str]:
    """从东财 jbgk 获取基金公司名称。"""
    url = f"http://fund.eastmoney.com/jbgk_{code}.html"
    try:
        resp = _SESSION.get(url, timeout=REQUEST_TIMEOUT)
        text = _safe_text(resp)
        # 查找基金管理人
        match = re.search(r'基金管理人[^\d]*?>(.*?)<', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    except Exception:
        return None


def fetch_lof_iopv_snapshot() -> dict:
    """获取 LOF IOPV 估值所需的全部原始数据。"""
    now = now_iso()

    # 1. 复用旧的集思录抓取（已处理 Cookie、Firecrawl、字段映射）
    old_result = get_lof_arbitrage_source_snapshot()
    if not old_result.get("success"):
        return old_result

    old_rows = old_result.get("data", [])

    # 2. 获取汇率
    try:
        fx_rates = get_fx_rates(["USD", "HKD"])
    except Exception:
        fx_rates = {}

    # 3. 标记 QDII 行并补充持仓数据
    all_rows = []
    for row in old_rows:
        group = str(row.get("marketGroup") or "").strip().lower()
        code = str(row.get("code") or "").strip()

        # 统一 marketGroup: asia → qdii
        if group == "asia":
            row["marketGroup"] = "qdii"

        currency = str(row.get("currency") or "CNY").upper()

        # 对非指数（QDII）补充持仓
        new_row = dict(row)
        if group != "index":
            new_row["holdings"] = _fetch_holdings(code)
            new_row["stockPosition"] = _fetch_stock_position(code)

        # 补充基金公司
        company = row.get("fundCompany") or row.get("raw", {}).get("issuer_nm")
        if not company:
            company = _fetch_fund_company(code)
        new_row["fundCompany"] = str(company or "").strip()

        # 补充当前汇率
        new_row["currentFxRate"] = fx_rates.get(currency, 1.0)

        all_rows.append(new_row)

    source_summary = dict(old_result.get("sourceSummary") or {})
    source_summary["totalRows"] = len(all_rows)
    source_summary["indexCount"] = sum(1 for r in all_rows if r.get("marketGroup") == "index")
    source_summary["qdiiCount"] = sum(1 for r in all_rows if r.get("marketGroup") == "qdii")

    return {
        "success": True,
        "data": all_rows,
        "updateTime": now,
        "source": old_result.get("source", "jisilu+tencent") + "+eastmoney",
        "sourceSummary": source_summary,
    }