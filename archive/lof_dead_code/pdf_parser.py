# -*- coding: utf-8 -*-
"""PDF持仓提取器 - 简洁版。
从季报PDF提取前20大持仓。
策略: 找权重百分比，在其前方文本中匹配已知ETF关键词。
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

import pdfplumber

# 关键词 -> (ticker, market)
_KW: Dict[str, Tuple[str, str]] = {
    # ARK
    "ARK Innovation": ("ARKK", "US"), "ARK Genomic": ("ARKG", "US"),
    "ARK Autonomous": ("ARKQ", "US"), "ARK Next": ("ARKW", "US"),
    "ARK Fintech": ("ARKF", "US"),
    # 科技
    "Invesco QQQ": ("QQQ", "US"), "QQQ Trust": ("QQQ", "US"),
    "Dynamic Semiconductor": ("PSI", "US"), "PHLX Semiconductor": ("SOXQ", "US"),
    "iShares Semiconductor": ("SOXX", "US"), "VanEck Semiconductor": ("SMH", "US"),
    "Global X Robotics": ("BOTZ", "US"), "Global X Artificial": ("AIQ", "US"),
    "Technology Select": ("XLK", "US"), "State Street Technology": ("XLK", "US"),
    # 能源
    "United States Oil": ("USO", "US"), "United States Brent": ("BNO", "US"),
    "WisdomTree WTI": ("CRUD", "US"), "WisdomTree Brent": ("BRNT", "US"),
    "ProShares K-1": ("OILK", "US"), "Invesco DB Oil": ("DBO", "US"),
    "iShares US Energy": ("IYE", "US"), "iShares Global Energy": ("IXC", "US"),
    "Vanguard Energy": ("VDE", "US"), "SPDR S&P Oil": ("XOP", "US"),
    "SPDR Energy": ("XLE", "US"), "Oil & Gas Exploration": ("XOP", "US"),
    # 医疗
    "Health Care Select": ("XLV", "US"), "iShares Biotechnology": ("IBB", "US"),
    "SPDR S&P Biotech": ("XBI", "US"),
    # 消费/REIT
    "Consumer Discretionary": ("XLY", "US"), "Vanguard Real Estate": ("VNQ", "US"),
    # 债券
    "Aggregate Bond": ("AGG", "US"), "iShares Core U.S. Aggregate": ("AGG", "US"),
    "iShares TIPS": ("TIP", "US"), "iBoxx Investment": ("LQD", "US"),
    "iBoxx High Yield": ("HYG", "US"),
    # 宽基
    "SPDR S&P 500": ("SPY", "US"), "iShares Core S&P 500": ("IVV", "US"),
    "iShares MSCI India": ("INDA", "US"), "iShares MSCI Emerging": ("EEM", "US"),
    "Vanguard FTSE Emerging": ("VWO", "US"),
    # 黄金
    "SPDR Gold": ("GLD", "US"), "iShares Gold": ("IAU", "US"),
    "VanEck Gold": ("GDX", "US"),
    # 港股
    "腾讯": ("00700", "HK"), "阿里巴巴": ("09988", "HK"),
    "美团": ("03690", "HK"), "京东": ("09618", "HK"),
    "小米": ("01810", "HK"), "百度": ("09888", "HK"),
    "网易": ("09999", "HK"), "快手": ("01024", "HK"),
    "中国海洋石油": ("00883", "HK"),
}

_HK_CODES = {"00700", "09988", "03690", "09618", "01810", "09888", "09999", "01024", "00883"}


def extract_holdings_from_pdf(pdf_path: str) -> List[Dict]:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join([p.extract_text() or "" for p in pdf.pages])

    # 合并空白
    text = re.sub(r'\s+', ' ', full_text)

    holdings = []

    # 找基金投资明细段落
    for section_kw in ["前十名基金投资明细", "前二十名基金投资明细", "基金投资明细"]:
        idx = text.find(section_kw)
        if idx < 0:
            continue
        # 段落结束
        end = len(text)
        for m in ["5.10 ", "§6 ", "投资组合报告附注"]:
            ei = text.find(m, idx + 100)
            if 0 < ei < end:
                end = ei
        section = text[idx:end]
        _extract_from_section(section, "fund", holdings)
        break

    # 找股票投资明细
    for section_kw in ["前十名股票投资明细", "前二十名股票投资明细", "股票投资明细"]:
        idx = text.find(section_kw)
        if idx < 0:
            continue
        end = len(text)
        for m in ["5.10 ", "§6 ", "投资组合报告附注"]:
            ei = text.find(m, idx + 100)
            if 0 < ei < end:
                end = ei
        section = text[idx:end]
        _extract_from_section(section, "stock", holdings)
        break

    # 去重+排序
    seen = set()
    unique = []
    for h in holdings:
        if h["ticker"] not in seen:
            seen.add(h["ticker"])
            unique.append(h)
    unique.sort(key=lambda x: x["weight"], reverse=True)
    return unique[:20]


def _extract_from_section(section: str, section_type: str, holdings: list):
    """从段落中提取持仓"""
    # 找所有权重百分比
    for m in re.finditer(r'([\d,]+\.\d{2})\s*(%|％)?', section):
        val_str = m.group(1).replace(",", "")
        try:
            val = float(val_str)
        except ValueError:
            continue
        if not (0.1 <= val <= 100):
            continue

        # 在权重前方2000字符中找关键词
        ctx = section[max(0, m.start() - 2000):m.start()]
        ticker, market = _match_keyword(ctx)
        if ticker:
            holdings.append({
                "name": ticker, "ticker": ticker,
                "weight": val, "market": market, "type": section_type,
            })


def _match_keyword(ctx: str) -> Tuple[str, str]:
    """在上下文中匹配关键词"""
    # 1) 精确匹配
    for kw, (ticker, market) in _KW.items():
        if kw in ctx:
            return (ticker, market)
    # 2) 港股代码
    for code in _HK_CODES:
        if code in ctx:
            return (code, "HK")
    # 3) 部分匹配（所有单词都在上下文中）
    for kw, (ticker, market) in _KW.items():
        parts = kw.split()
        if len(parts) >= 2 and all(p in ctx for p in parts):
            return (ticker, market)
    return ("", "other")
