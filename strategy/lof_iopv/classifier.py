# -*- coding: utf-8 -*-
"""QDII LOF 基金分类器。"""

from __future__ import annotations


def classify_fund(row: dict) -> str:
    """判定 QDII 基金估值分类。
    1. 有 holdings 且非空 → B类（T10持仓加权法）
    2. 默认 → A类（指数跟踪法）
    """
    holdings = row.get("holdings") or []
    if isinstance(holdings, list) and len(holdings) > 0:
        return "B"
    return "A"


CALC_MODE_LABELS = {
    "A": "指数跟踪法",
    "B": "T10持仓加权法",
    "C": "多ETF拟合法(预留)",
}


def get_calc_mode(fund_type: str) -> str:
    return CALC_MODE_LABELS.get(fund_type, "未知")


def get_group_key(fund_type: str) -> str:
    return "qdii"