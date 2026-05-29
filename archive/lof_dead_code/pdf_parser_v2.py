# -*- coding: utf-8 -*-
"""PDF持仓提取器 v2 - 支持股票+基金持仓提取。
"""
from __future__ import annotations
import re
from typing import Dict, List, Tuple
import pdfplumber

# 名称 -> (ticker, market)
NAME_MAP: Dict[str, Tuple[str, str]] = {
    # ARK
    "ARK Innovation": ("ARKK", "US"), "ARK Genomic": ("ARKG", "US"),
    "ARK Autonomous": ("ARKQ", "US"), "ARK Next": ("ARKW", "US"),
    # 科技ETF
    "Invesco QQQ": ("QQQ", "US"), "QQQ Trust": ("QQQ", "US"),
    "Dynamic Semiconductor": ("PSI", "US"), "PHLX Semiconductor": ("SOXQ", "US"),
    "iShares Semiconductor": ("SOXX", "US"), "VanEck Semiconductor": ("SMH", "US"),
    "Global X Robotics": ("BOTZ", "US"), "Global X Artificial Intelligence": ("AIQ", "US"),
    "Technology Select": ("XLK", "US"), "State Street Technology": ("XLK", "US"),
    "Global X FinTech": ("FINX", "US"),
    # 能源ETF
    "SPDR S&P Oil": ("XOP", "US"), "VANGUARD ENERGY": ("VDE", "US"),
    "ISHARES US ENERGY": ("IYE", "US"), "ISHARES GLOBAL ENERGY": ("IXC", "US"),
    "SPDR ENERGY SELECT": ("XLE", "US"), "UNITED STATES OIL": ("USO", "US"),
    "UNITED STATES BRENT": ("BNO", "US"), "WisdomTree WTI": ("USO", "US"),
    "WisdomTree Brent": ("BNO", "US"), "ProShares K-1": ("OILK", "US"),
    "Invesco DB Oil": ("DBO", "US"),
    # 其他ETF
    "Health Care Select": ("XLV", "US"), "SPDR S&P Biotech": ("XBI", "US"),
    "Consumer Discretionary": ("XLY", "US"), "Vanguard Real Estate": ("VNQ", "US"),
    "Aggregate Bond": ("AGG", "US"), "SPDR S&P 500": ("SPY", "US"),
    "iShares MSCI India": ("INDA", "US"), "SPDR Gold": ("GLD", "US"),
    "iShares Gold": ("IAU", "US"), "iShares Core S&P 500": ("IVV", "US"),
    "iShares Biotechnology": ("IBB", "US"),
    # 股票
    "NVIDIA": ("NVDA", "US"), "MICRON": ("MU", "US"), "SANDISK": ("SNDK", "US"),
    "ALPHABET": ("GOOGL", "US"), "META PLATFORMS": ("META", "US"),
    "AMAZON": ("AMZN", "US"), "MICROSOFT": ("MSFT", "US"),
    "BROADCOM": ("AVGO", "US"), "ASML HOLDING": ("ASML", "US"),
    "TAIWAN SEMICONDUCTOR": ("TSM", "US"), "TENCENT": ("00700", "HK"),
    "ALIBABA": ("09988", "HK"), "CNOOC": ("00883", "HK"),
    "MEITUAN": ("03690", "HK"), "KUAISHOU": ("01024", "HK"),
    "CHINA MOBILE": ("00941", "HK"), "ZIJIN MINING": ("02899", "HK"),
    "POP MART": ("09992", "HK"), "BAIDU": ("09888", "HK"),
    "JD.COM": ("09618", "HK"), "NETEASE": ("09999", "HK"),
    "CHINA TELECOM": ("00728", "HK"), "APPLE": ("AAPL", "US"),
    "PALANTIR": ("PLTR", "US"), "AMD": ("AMD", "US"),
    "CISCO": ("CSCO", "US"), "INTEL": ("INTC", "US"),
    "QUALCOMM": ("QCOM", "US"), "ADOBE": ("ADBE", "US"),
    "SALESFORCE": ("CRM", "US"), "ORACLE": ("ORCL", "US"),
    "SERVICENOW": ("NOW", "US"), "INTUIT": ("INTU", "US"),
    "AMD": ("AMD", "US"), "DELL": ("DELL", "US"),
    "HP": ("HPQ", "US"), "IBM": ("IBM", "US"),
    "NETFLIX": ("NFLX", "US"), "TESLA": ("TSLA", "US"),
    "NXP": ("NXPI", "US"), "APPLIED MATERIALS": ("AMAT", "US"),
    "LAM RESEARCH": ("LRCX", "US"), "KLA": ("KLAC", "US"),
    "MARVELL": ("MRVL", "US"), "ON SEMICONDUCTOR": ("ON", "US"),
    "MONOLITHIC": ("MPWR", "US"), "WOLFSPEED": ("WOLF", "US"),
    # 港股简称
    "腾讯": ("00700", "HK"), "阿里巴巴": ("09988", "HK"),
    "美团": ("03690", "HK"), "小米": ("01810", "HK"),
    "京东": ("09618", "HK"), "百度": ("09888", "HK"),
    "网易": ("09999", "HK"), "快手": ("01024", "HK"),
    "中国海洋石油": ("00883", "HK"), "中国移动": ("00941", "HK"),
    "中国电信": ("00728", "HK"),
}

# 按长度降序排序
_SORTED_KEYWORDS = sorted(NAME_MAP.keys(), key=len, reverse=True)

# US ticker正则 (2-5个大写字母)
_US_TICKER_RE = re.compile(r'\b([A-Z]{2,5})\b')


def extract_holdings_from_pdf(pdf_path: str) -> List[Dict]:
    with pdfplumber.open(pdf_path) as pdf:
        full_text = "\n".join([p.extract_text() or "" for p in pdf.pages])

    holdings = []

    # 1) 基金投资明细
    fund_section = _find_section(full_text, ["前十名基金投资明细"])
    if fund_section and "未持有基金" not in fund_section:
        holdings.extend(_extract_from_section(fund_section, "fund"))

    # 2) 股票投资明细
    stock_section = _find_section(full_text, ["前十名股票及存托凭证", "前十名股票投资明细", "前十名证券"])
    if stock_section and "未持有股票" not in stock_section:
        holdings.extend(_extract_from_section(stock_section, "stock"))

    # 去重排序
    seen = set()
    unique = []
    for h in holdings:
        if h["ticker"] and h["ticker"] not in seen:
            seen.add(h["ticker"])
            unique.append(h)
    unique.sort(key=lambda x: x["weight"], reverse=True)
    return unique[:20]


def _find_section(text: str, keywords: List[str]) -> str:
    for kw in keywords:
        idx = text.find(kw)
        if idx >= 0:
            end = len(text)
            for m in ["5.5 ", "5.6 ", "5.7 ", "5.8 ", "5.9 ", "5.10 ", "§6 "]:
                ei = text.find(m, idx + 100)
                if 0 < ei < end:
                    end = ei
            return text[idx:end]
    return ""


def _extract_from_section(section: str, holding_type: str) -> List[Dict]:
    holdings = []
    # 合并空白，但保留单词内的空格问题
    text = re.sub(r'\s+', ' ', section)

    # 找所有百分比
    for m in re.finditer(r'(\d+\.\d{2})\s*(%|％)?', text):
        val_str = m.group(1)
        try:
            val = float(val_str)
        except:
            continue
        if not (0.5 <= val <= 50):
            continue

        # 小窗口150字符
        ctx = text[max(0, m.start() - 150):m.start()]
        ticker, market = _match_name(ctx)

        if ticker:
            holdings.append({
                "name": ticker,
                "ticker": ticker,
                "weight": val,
                "market": market,
                "type": holding_type,
            })

    return holdings


def _match_name(ctx: str) -> Tuple[str, str]:
    ctx_upper = ctx.upper()

    # 1) 精确匹配（长关键词优先）
    for keyword in _SORTED_KEYWORDS:
        if keyword.upper() in ctx_upper:
            return NAME_MAP[keyword]

    # 2) 部分匹配（所有单词都在上下文中）
    for keyword in _SORTED_KEYWORDS:
        parts = keyword.upper().split()
        if len(parts) >= 2 and all(p in ctx_upper for p in parts):
            return NAME_MAP[keyword]

    # 3) 去空格匹配（处理PDF换行导致的空格问题）
    ctx_nospace = re.sub(r'\s+', '', ctx_upper)
    for keyword in _SORTED_KEYWORDS:
        kw_nospace = re.sub(r'\s+', '', keyword.upper())
        if len(kw_nospace) >= 4 and kw_nospace in ctx_nospace:
            return NAME_MAP[keyword]

    return ("", "other")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        holdings = extract_holdings_from_pdf(sys.argv[1])
        print(f"提取到 {len(holdings)} 条持仓:")
        for h in holdings:
            print(f"  {h['ticker']:10s} {h['weight']:6.2f}% {h['market']}")
