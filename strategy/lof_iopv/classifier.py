# -*- coding: utf-8 -*-
"""LOF 基金分类器。"""

from __future__ import annotations


def classify_fund(row: dict) -> str:
    """判定基金分类。
    1. marketGroup == "index" → A类
    2. 有 holdings 且非空 → B类
    3. currency == "CNY" 且无境外资产 → D类
    4. 默认 → B类
    """
    group = str(row.get("marketGroup") or "").strip().lower()
    if group == "index":
        return "A"
    holdings = row.get("holdings") or []
    if isinstance(holdings, list) and len(holdings) > 0:
        return "B"
    currency = str(row.get("currency") or "CNY").upper()
    if currency == "CNY":
        return "D"
    return "B"


CALC_MODE_LABELS = {
    "A": "指数跟踪法",
    "B": "T10持仓加权法",
    "C": "多ETF拟合法(预留)",
    "D": "直接NAV法",
}


def get_calc_mode(fund_type: str) -> str:
    return CALC_MODE_LABELS.get(fund_type, "未知")


def get_group_key(fund_type: str) -> str:
    return "index" if fund_type == "A" else "qdii"