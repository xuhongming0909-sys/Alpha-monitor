# -*- coding: utf-8 -*-
"""已知基金持仓数据（从2026Q1季报提取，已合并重复ticker）。
用于PDF解析失败时的fallback。
"""
from __future__ import annotations
from typing import Dict, List, Tuple

# 每只基金的前20大持仓: [(ticker, weight%, market), ...]
# 重复ticker已合并权重
KNOWN_HOLDINGS: Dict[str, List[Tuple[str, float, str]]] = {
    # ========== 海外科技 ==========
    "501312": [
        ("ARKK", 18.74, "US"),   # ARK Innovation ETF
        ("ARKG", 15.35, "US"),   # ARK Genomic Revolution ETF
        ("ARKQ", 11.59, "US"),   # ARK Autonomous Technology & Robotics ETF
        ("SOXX",  9.51, "US"),   # iShares Semiconductor ETF
        ("AIQ",   7.85, "US"),   # Global X AI & Technology ETF
        ("QQQ",   7.45, "US"),   # Invesco QQQ Trust
        ("BOTZ",  7.44, "US"),   # Global X Robotics & AI ETF
        ("XLK",   6.44, "US"),   # State Street Technology Select Sector
        ("SMH",   4.29, "US"),   # VanEck Semiconductor ETF
        ("FINX",  1.20, "US"),   # Global X FinTech ETF
    ],
    # ========== 南方原油 (合并重复ticker) ==========
    "501018": [
        ("USO",  38.86, "US"),   # WisdomTree WTI(19.80) + USO(19.06)
        ("BNO",  35.08, "US"),   # WisdomTree Brent(19.20) + BNO(15.88)
        # Simplex WTI ETF (日本) - 剔除
        # Nomura Crude Oil ETF (日本) - 剔除
        # UBS CMCI Oil SF ETF (瑞士) - 剔除
    ],
    # ========== 嘉实原油 (合并重复ticker) ==========
    "160723": [
        ("USO",  28.91, "US"),   # WisdomTree WTI(19.35) + USO(9.56)
        ("BNO",  24.45, "US"),   # WisdomTree Brent(16.28) + BNO(8.17)
        ("OILK", 14.48, "US"),   # ProShares K-1 Free Crude Oil ETF
    ],
    # ========== 原油LOF (合并重复ticker) ==========
    "161129": [
        ("USO",  32.56, "US"),   # WisdomTree WTI(19.70) + USO(12.86)
        ("BNO",  32.77, "US"),   # WisdomTree Brent(19.53) + BNO(13.24)
        ("DBO",  16.72, "US"),   # Invesco DB Oil Fund
    ],
    # ========== 全球油气 ==========
    "163208": [
        ("XOP",  16.04, "US"),   # SPDR S&P Oil & Gas Exploration & Production
        ("VDE",  16.02, "US"),   # Vanguard Energy ETF
        ("IYE",  15.82, "US"),   # iShares US Energy ETF
        ("IXC",  15.81, "US"),   # iShares Global Energy ETF
        ("XLE",  15.60, "US"),   # SPDR Energy Select Sector
        ("USO",   7.60, "US"),   # United States Oil Fund LP
        ("BNO",   7.31, "US"),   # United States Brent Oil Fund LP
    ],
    # ========== 全球芯片 ==========
    "501225": [
        ("PSI",  18.32, "US"),   # Invesco Dynamic Semiconductors ETF
        ("SOXQ", 18.25, "US"),   # Invesco PHLX Semiconductor ETF
        ("SOXX", 18.23, "US"),   # iShares Semiconductor ETF
        ("SMH",  18.17, "US"),   # VanEck Semiconductor ETF
        # A股芯片ETF (~20%) - 暂无数据
        # Global X Semiconductor Japan (日本) - 剔除
    ],
    # ========== 标普信息科技 ==========
    "161128": [("XLK", 100, "US")],
    # ========== 纳指 ==========
    "161130": [("QQQ", 100, "US")],
    # ========== 标普500 ==========
    "161125": [("SPY", 100, "US")],
    # ========== 标普医疗保健 ==========
    "161126": [("XLV", 100, "US")],
    # ========== 标普生物科技 ==========
    "161127": [("XBI", 100, "US")],
    # ========== 美国消费 ==========
    "162415": [("XLY", 100, "US")],
    # ========== 美国REIT ==========
    "160140": [("VNQ", 100, "US")],
    # ========== 美元债 ==========
    "501300": [("AGG", 100, "US")],
    # ========== 印度基金 ==========
    "164824": [("INDA", 100, "US")],
    # ========== 华宝油气 ==========
    "162411": [("XOP", 100, "US")],
    # ========== 嘉实黄金 ==========
    "160719": [("GLD", 100, "US")],
    # ========== 黄金LOF ==========
    "164701": [("GLD", 100, "US")],
    # ========== 黄金主题 ==========
    "161116": [("GLD", 100, "US")],
    # ========== 石油基金(已B类) ==========
    "160416": [],  # 从DB获取
    # ========== 石油LOF(已B类) ==========
    "162719": [],  # 从DB获取
    # ========== 南方香港(已B类) ==========
    "160125": [],  # 从DB获取
    # ========== 港美互联网(已B类) ==========
    "160644": [],  # 从DB获取
    # ========== 中概互联网(已B类) ==========
    "164906": [],  # 从DB获取
}


def get_hardcoded_holdings(code: str) -> List[Tuple[str, float, str]]:
    return KNOWN_HOLDINGS.get(code, [])
