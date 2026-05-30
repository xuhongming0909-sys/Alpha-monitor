# -*- coding: utf-8 -*-
# AI-SUMMARY: 鍩洪噾鎸佷粨 - A绫籈TF鏄犲皠(100%鏉冮噸,鍩轰簬涓氱哗鍩哄噯) + B绫诲疄闄呮寔浠?2026Q1瀛ｆ姤)
# 瀵瑰簲 INDEX.md 9.3 鏂囦欢鎽樿绱㈠紩
"""宸茬煡鍩洪噾鎸佷粨鏁版嵁銆?

A绫?鎸囨暟璺熻釜): 鍗旹TF鏄犲皠, weight鍥哄畾100%, 鎬讳粨浣嶇敱API鎶撳彇銆?
B绫?涓诲姩/娣峰悎): 瀹為檯鎸佷粨浠庡鎶? 鎬讳粨浣嶇敱API鎶撳彇銆?
"""
from __future__ import annotations
from typing import Dict, List, Tuple


# A绫? 鍩洪噾浠ｇ爜 -> (etf_ticker, etf_name)
ETF_MAPPING: Dict[str, Tuple[str, str]] = {
    "161128": ("XLK", "鏍囨櫘500淇℃伅绉戞妧 -> XLK"),
    "161130": ("QQQ", "绾虫柉杈惧厠100 -> QQQ"),
    "161125": ("SPY", "鏍囨櫘500 -> SPY"),
    "161126": ("RYH", "鏍囨櫘500鍖荤枟淇濆仴绛夋潈閲?-> RYH"),
    "161127": ("XBI", "鏍囨櫘鐢熺墿绉戞妧绮鹃€夎涓?-> XBI"),
    "162415": ("XLY", "鏍囨櫘缇庡浗鍝佽川娑堣垂 -> XLY"),
    "160416": ("IXC", "鏍囨櫘鍏ㄧ悆鐭虫补 -> IXC"),
    "162719": ("IEO", "閬撶惣鏂編鍥界煶娌瑰紑鍙戠敓浜?-> IEO"),
    "162411": ("XOP", "鏍囨櫘鐭虫补澶╃劧姘斾笂娓?-> XOP"),
    "160719": ("GLD", "浼︽暒閲戜环鏍?-> GLD"),
    "164824": ("INDA", "涓俊璇佸埜鍗板害ETP(MSCI India) -> INDA"),
    "160723": ("USO", "WTI鍘熸补浠锋牸 -> USO"),
    "161129": ("USO", "S&P GSCI鍘熸补鎸囨暟 -> USO"),
    "501018": ("USO", "60%WTI+40%Brent -> USO+BNO"),
    "160140": ("IYR", "閬撶惣鏂編鍥界簿閫塕EIT -> IYR"),
    "164701": ("GLD", "浼︽暒閲戜环鏍?-> GLD(ETF鑱旀帴)"),
    "161116": ("GLD", "50%浼︽暒閲?50%MSCI閲戠熆鑲?-> GLD+GDX"),
    "501300": ("AGG", "宸村厠鑾辩編鍥界患鍚堝€哄埜 -> AGG"),
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


# B绫? 鍩洪噾浠ｇ爜 -> 瀹為檯鎸佷粨 [(ticker, weight, market), ...]
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
    "164906": [("KWEB", 100.0, "US")],
}


def get_b_holdings(code: str) -> List[Dict]:
    raw = B_HOLDINGS.get(code, [])
    return [{"ticker": t, "weight": w, "market": m} for t, w, m in raw]


def get_holdings_for_backtest(code: str) -> List[Dict]:
    if is_class_a(code):
        return get_a_holdings(code)
    return get_b_holdings(code)
