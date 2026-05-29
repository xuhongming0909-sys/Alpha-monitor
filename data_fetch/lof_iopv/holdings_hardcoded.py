# -*- coding: utf-8 -*-
# AI-SUMMARY: 基金持仓 - A类ETF映射(100%权重,基于业绩基准) + B类实际持仓(2026Q1季报)
# 对应 INDEX.md 9.3 文件摘要索引
"""已知基金持仓数据。

A类(指数跟踪): 单ETF映射, weight固定100%, 总仓位由API抓取。
B类(主动/混合): 实际持仓从季报, 总仓位由API抓取。
"""
from __future__ import annotations
from typing import Dict, List, Tuple


# A类: 基金代码 -> (etf_ticker, etf_name)
ETF_MAPPING: Dict[str, Tuple[str, str]] = {
    "161128": ("XLK", "标普500信息科技 -> XLK"),
    "161130": ("QQQ", "纳斯达克100 -> QQQ"),
    "161125": ("SPY", "标普500 -> SPY"),
    "161126": ("RYH", "标普500医疗保健等权重 -> RYH"),
    "161127": ("XBI", "标普生物科技精选行业 -> XBI"),
    "162415": ("XLY", "标普美国品质消费 -> XLY"),
    "160416": ("IXC", "标普全球石油 -> IXC"),
    "162719": ("IEO", "道琼斯美国石油开发生产 -> IEO"),
    "162411": ("XOP", "标普石油天然气上游 -> XOP"),
    "160719": ("GLD", "伦敦金价格 -> GLD"),
    "164824": ("INDA", "中信证券印度ETP(MSCI India) -> INDA"),
    "160723": ("USO", "WTI原油价格 -> USO"),
    "161129": ("USO", "S&P GSCI原油指数 -> USO"),
    "501018": ("USO", "60%WTI+40%Brent -> USO+BNO"),
    "160140": ("IYR", "道琼斯美国精选REIT -> IYR"),
    "164701": ("GLD", "伦敦金价格 -> GLD(ETF联接)"),
    "161116": ("GLD", "50%伦敦金+50%MSCI金矿股 -> GLD+GDX"),
    "501300": ("AGG", "巴克莱美国综合债券 -> AGG"),
}


def is_class_a(code: str) -> bool:
    return code in ETF_MAPPING


def get_etf_ticker(code: str) -> str:
    entry = ETF_MAPPING.get(code)
    return entry[0] if entry else ""


def get_a_holdings(code: str) -> List[Dict]:
    entry = ETF_MAPPING.get(code)
    if not entry:
        return []
    if code == "501018":
        return [
            {"ticker": "USO", "weight": 60.0, "market": "US"},
            {"ticker": "BNO", "weight": 40.0, "market": "US"},
        ]
    if code == "161116":
        return [
            {"ticker": "GLD", "weight": 50.0, "market": "US"},
            {"ticker": "GDX", "weight": 50.0, "market": "US"},
        ]
    return [{"ticker": entry[0], "weight": 100.0, "market": "US"}]


# B类: 基金代码 -> 实际持仓 [(ticker, weight, market), ...]
B_HOLDINGS: Dict[str, List[Tuple[str, float, str]]] = {
    "501312": [
        ("ARKK", 18.74, "US"), ("ARKG", 15.35, "US"),
        ("ARKQ", 11.59, "US"), ("SOXX", 9.51, "US"),
        ("AIQ", 7.85, "US"),   ("QQQ", 7.45, "US"),
        ("BOTZ", 7.44, "US"),  ("XLK", 6.44, "US"),
        ("SMH", 4.29, "US"),   ("FINX", 1.20, "US"),
    ],
    "501225": [("PSI", 18.32, "US"), ("SOXQ", 18.25, "US"), ("SOXX", 18.23, "US"), ("SMH", 18.17, "US")],
    "163208": [
        ("XOP", 16.04, "US"), ("VDE", 16.02, "US"), ("IYE", 15.82, "US"),
        ("IXC", 15.81, "US"), ("XLE", 15.60, "US"), ("USO", 7.60, "US"),
        ("BNO", 7.31, "US"),
    ],
    "160644": [
        ("TSM", 9.09, "US"), ("NVDA", 9.05, "US"), ("SNDK", 8.57, "US"),
        ("MU", 7.49, "US"), ("00700", 6.58, "HK"), ("GOOGL", 5.69, "US"),
        ("09988", 4.69, "HK"), ("00883", 3.96, "HK"), ("AVGO", 3.49, "US"),
        ("ASML", 2.85, "US"),
    ],
    "160125": [],
    "164906": [("KWEB", 100.0, "US")],
}


def get_b_holdings(code: str) -> List[Dict]:
    raw = B_HOLDINGS.get(code, [])
    return [{"ticker": t, "weight": w, "market": m} for t, w, m in raw]


def get_holdings_for_backtest(code: str) -> List[Dict]:
    if is_class_a(code):
        return get_a_holdings(code)
    return get_b_holdings(code)