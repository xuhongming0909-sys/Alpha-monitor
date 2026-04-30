#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dividend data loader (AkShare CNINFO + Tencent quote, no Eastmoney)."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
ROOT_TEXT = str(ROOT_DIR)
if ROOT_TEXT not in sys.path:
    sys.path.insert(0, ROOT_TEXT)

import akshare as ak
import requests
from data_fetch.dividend.source import (
    get_dividend_data as plugin_get_dividend_data,
    get_stock_price as plugin_get_stock_price,
    get_upcoming_dividends as plugin_get_upcoming_dividends,
)


def clean_nan(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    return obj


def normalize_code(code: str) -> str:
    return str(code or "").strip()


def get_stock_currency(stock_code: str) -> str:
    code = normalize_code(stock_code)
    if code.startswith("900"):
        return "USD"
    if code.startswith(("200", "201")):
        return "HKD"
    return "CNY"


def get_stock_currency_symbol(currency: str) -> str:
    symbols = {"CNY": "￥", "USD": "$", "HKD": "HK$"}
    return symbols.get(str(currency or "").upper(), "￥")


def _build_query_code(stock_code: str) -> str:
    code = normalize_code(stock_code)
    if code.startswith("900"):
        return f"sh{code}"
    if code.startswith(("200", "201")):
        return f"sz{code}"
    if code.startswith("6"):
        return f"sh{code}"
    return f"sz{code}"


def get_stock_price(stock_code: str) -> Dict[str, Any]:
    code = normalize_code(stock_code)
    if not code:
        return {"price": None, "currency": "CNY", "name": "", "source": "tencent"}

    query_code = _build_query_code(code)
    try:
        resp = requests.get(
            f"https://qt.gtimg.cn/q={query_code}",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"},
            timeout=15,
        )
        text = resp.content.decode("gbk", errors="ignore")
        m = re.match(r'v_([^=]+)="(.*)";?', text.strip())
        if not m:
            return {"price": None, "currency": get_stock_currency(code), "name": "", "source": "tencent"}
        parts = m.group(2).split("~")
        if len(parts) < 4:
            return {"price": None, "currency": get_stock_currency(code), "name": "", "source": "tencent"}
        name = str(parts[1] if len(parts) > 1 else "").strip()
        price = float(parts[3]) if parts[3] else None
        return {
            "price": price if isinstance(price, (int, float)) and price > 0 else None,
            "currency": get_stock_currency(code),
            "name": name,
            "source": "tencent",
        }
    except Exception:
        return {"price": None, "currency": get_stock_currency(code), "name": "", "source": "tencent"}


def _first_existing_col(columns: list, candidates: list[str]) -> Optional[str]:
    for c in candidates:
        if c in columns:
            return c
    return None


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _to_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        text = str(value).strip()
        if not text or text.lower() == "nan":
            return None
        return float(text)
    except Exception:
        return None


def _to_text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text.lower() == "nan" else text


def get_dividend_data(stock_code: str) -> Dict[str, Any]:
    code = normalize_code(stock_code)
    if not code:
        return {"success": False, "error": "股票代码不能为空", "data": None}

    try:
        df = ak.stock_dividend_cninfo(symbol=code)
    except Exception as exc:
        return {"success": False, "error": f"CNINFO dividend数据获取失败: {exc}", "data": None}

    if df is None or df.empty:
        return {"success": False, "error": "未获取到dividend数据", "data": None}

    columns = list(df.columns)
    announce_col = _first_existing_col(columns, ["实施方案公告日期", "公告日期"])
    report_col = _first_existing_col(columns, ["报告时间", "报告期"])
    type_col = _first_existing_col(columns, ["dividend类型"])
    cash_col = _first_existing_col(columns, ["派息比例", "现金dividend比例"])
    send_col = _first_existing_col(columns, ["送股比例"])
    reserve_col = _first_existing_col(columns, ["转增比例"])
    record_col = _first_existing_col(columns, ["股权登记日"])
    ex_col = _first_existing_col(columns, ["除权日", "除权除息日"])
    pay_col = _first_existing_col(columns, ["派息日"])
    desc_col = _first_existing_col(columns, ["实施方案dividend说明", "方案说明"])

    if announce_col:
        try:
            df = df.sort_values(by=announce_col, ascending=False)
        except Exception:
            pass

    latest = df.iloc[0]
    dividend_per_10 = _to_optional_float(latest.get(cash_col)) if cash_col else None
    dividend_per_share = (dividend_per_10 / 10) if dividend_per_10 is not None else None

    price_info = get_stock_price(code)
    current_price = _to_optional_float(price_info.get("price"))
    dividend_yield = (dividend_per_share / current_price * 100) if current_price and current_price > 0 and dividend_per_share and dividend_per_share > 0 else None

    currency = get_stock_currency(code)
    result = {
        "code": code,
        "name": _to_text(price_info.get("name")),
        "announcementDate": _to_text(latest.get(announce_col)) if announce_col else "",
        "reportPeriod": _to_text(latest.get(report_col)) if report_col else "",
        "dividendType": _to_text(latest.get(type_col)) if type_col else "",
        "dividendPer10Shares": dividend_per_10,
        "dividendPerShare": dividend_per_share,
        "stockDividendPer10": _to_optional_float(latest.get(send_col)) if send_col else None,
        "capitalReservePer10": _to_optional_float(latest.get(reserve_col)) if reserve_col else None,
        "recordDate": _to_text(latest.get(record_col)) if record_col else "",
        "exDividendDate": _to_text(latest.get(ex_col)) if ex_col else "",
        "payDate": _to_text(latest.get(pay_col)) if pay_col else "",
        "description": _to_text(latest.get(desc_col)) if desc_col else "",
        "currency": currency,
        "currencySymbol": get_stock_currency_symbol(currency),
        "currentPrice": current_price,
        "dividendYield": round(dividend_yield, 2) if isinstance(dividend_yield, float) else None,
        "source": "cninfo+tencent",
        "updateTime": datetime.now().isoformat(),
    }
    return clean_nan({"success": True, "data": result})


def get_upcoming_dividends(days: int = 3) -> Dict[str, Any]:
    _ = int(days) if days else 3
    # CNINFO interface is symbol-scoped; no stable all-market upcoming endpoint in current pipeline.
    return {
        "success": True,
        "data": [],
        "note": "当前版本仅提供按代码查询dividend；全市场即将dividend榜单未启用。",
        "source": "cninfo",
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "参数不足"}, ensure_ascii=False))
        sys.exit(1)

    action = sys.argv[1]

    if action == "dividend" and len(sys.argv) >= 3:
        stock_code = sys.argv[2]
        print(json.dumps(plugin_get_dividend_data(stock_code), ensure_ascii=False, default=str))
        sys.exit(0)

    if action == "upcoming":
        days = int(sys.argv[2]) if len(sys.argv) >= 3 else 3
        print(json.dumps(plugin_get_upcoming_dividends(days), ensure_ascii=False, default=str))
        sys.exit(0)

    if action == "price" and len(sys.argv) >= 3:
        stock_code = sys.argv[2]
        print(json.dumps(plugin_get_stock_price(stock_code), ensure_ascii=False, default=str))
        sys.exit(0)

    print(json.dumps({"success": False, "error": "未知操作"}, ensure_ascii=False))
    sys.exit(1)

