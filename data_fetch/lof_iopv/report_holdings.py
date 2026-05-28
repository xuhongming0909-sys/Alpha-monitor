# -*- coding: utf-8 -*-
"""从季报PDF提取前20大持仓，映射到ticker+market，存入DB。
数据拉取后存入SQLite，回测/实时计算从DB读取。"""
from __future__ import annotations

import os
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests

# ============================================================
# 已知 US ETF 映射字典 (name关键词 -> ticker)
# ============================================================
_KNOWN_US_ETFS: Dict[str, str] = {
    # ARK系列
    "ARK Innovation": "ARKK",
    "ARK Genomic": "ARKG",
    "ARK Autonomous": "ARKQ",
    "ARK Next Generation": "ARKW",
    "ARK Fintech": "ARKF",
    # 科技/半导体
    "Invesco QQQ": "QQQ",
    "Invesco Dynamic Semiconductor": "PSI",
    "Invesco PHLX Semiconductor": "SOXQ",
    "iShares Semiconductor": "SOXX",
    "iShares PHLX Semiconductor": "SOXX",
    "VanEck Semiconductor": "SMH",
    "Global X Robotics": "BOTZ",
    "Global X Artificial Intelligence": "AIQ",
    "Global X Autonomous": "AIQ",
    "Technology Select Sector": "XLK",
    "State Street Technology": "XLK",
    "SPDR Technology": "XLK",
    "SPDR S&P Technology": "XLK",
    # 能源/原油
    "United States Oil Fund": "USO",
    "United States Brent Oil": "BNO",
    "WisdomTree WTI Crude": "CRUD",
    "WisdomTree Brent Crude": "BRNT",
    "ProShares K-1 Free Crude": "OILK",
    "Invesco DB Oil": "DBO",
    "iShares US Energy": "IYE",
    "iShares Global Energy": "IXC",
    "Vanguard Energy": "VDE",
    "SPDR S&P Oil": "XOP",
    "SPDR Energy Select": "XLE",
    "Oil & Gas Exploration": "XOP",
    "Energy Select Sector": "XLE",
    # 医疗/生物科技
    "Health Care Select": "XLV",
    "SPDR Health Care": "XLV",
    "iShares Biotechnology": "IBB",
    "SPDR S&P Biotech": "XBI",
    # 消费/REIT
    "Consumer Discretionary Select": "XLY",
    "SPDR Consumer": "XLY",
    "Vanguard Real Estate": "VNQ",
    "iShares Cohen & Steers REIT": "ICF",
    # 债券
    "iShares Core U.S. Aggregate": "AGG",
    "iShares TIPS Bond": "TIP",
    "iShares iBoxx Investment Grade": "LQD",
    "iShares iBoxx High Yield": "HYG",
    # 宽基
    "SPDR S&P 500": "SPY",
    "iShares Core S&P 500": "IVV",
    "iShares MSCI India": "INDA",
    "iShares MSCI Emerging": "EEM",
    "Vanguard FTSE Emerging": "VWO",
    "SPDR Dow Jones": "DIA",
    # 黄金
    "SPDR Gold": "GLD",
    "iShares Gold Trust": "IAU",
    "VanEck Gold Miners": "GDX",
    # 其他
    "iShares Core S&P Mid-Cap": "IJH",
    "iShares Core S&P Small-Cap": "IJR",
    "iShares Edge MSCI USA Value": "VLUE",
    "iShares Edge MSCI USA Momentum": "MTUM",
    "iShares Edge MSCI USA Quality": "QUAL",
    "iShares Edge MSCI Min Vol": "USMV",
    "WisdomTree India Earnings": "EPI",
    "iShares MSCI Brazil": "EWZ",
    "iShares MSCI Japan": "EWJ",
    "iShares MSCI South Korea": "EWY",
    "iShares MSCI Taiwan": "EWT",
    "Samsung S&P GSCI": "USO",
    "NEXT FUNDS NOMURA Crude": "USO",
    "UBS CMCI Oil": "BNO",
    "Simplex WTI": "USO",
    "Simplex Brent": "BNO",
}

_A_SHARE_PREFIXES = {"51": "sh", "15": "sz", "60": "sh", "00": "sz", "30": "sz", "68": "sh"}

HK_SESSION = requests.Session()
HK_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://fundf10.eastmoney.com/",
})


# ============================================================
# 1. 季报获取 + PDF下载
# ============================================================
def fetch_latest_report_id(code: str) -> Optional[str]:
    import akshare as ak
    try:
        df = ak.fund_announcement_report_em(symbol=code)
        if df is None or df.empty:
            return None
        for _, row in df.iloc[::-1].iterrows():
            title = str(row.get("公告标题", ""))
            if "季度报告" in title and "摘要" not in title and "年度" not in title:
                return str(row.get("报告ID", ""))
        return str(df.iloc[-1].get("报告ID", ""))
    except Exception:
        return None


def download_report_pdf(report_id: str, save_dir: str) -> Optional[str]:
    os.makedirs(save_dir, exist_ok=True)
    pdf_path = os.path.join(save_dir, f"{report_id}.pdf")
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 10000:
        return pdf_path
    # HTTP优先(HTTPS被拦截)
    for url in [
        f"http://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf",
        f"https://pdf.dfcfw.com/pdf/H2_{report_id}_1.pdf",
    ]:
        try:
            r = HK_SESSION.get(url, timeout=60, verify=(not url.startswith("http://")))
            if r.content[:4] == b"%PDF" and len(r.content) > 10000:
                with open(pdf_path, "wb") as f:
                    f.write(r.content)
                return pdf_path
        except Exception:
            continue
    return None


# ============================================================
# 2. PDF解析 - 提取持仓
# ============================================================
def extract_holdings_from_pdf(pdf_path: str) -> List[Dict]:
    import pdfplumber
    all_holdings = []
    with pdfplumber.open(pdf_path) as pdf:
        all_holdings.extend(_extract_fund_holdings(pdf))
        all_holdings.extend(_extract_stock_holdings(pdf))
        all_holdings.extend(_extract_bond_holdings(pdf))
    seen = set()
    unique = []
    for h in all_holdings:
        key = h.get("ticker") or h.get("name", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(h)
    unique.sort(key=lambda x: x.get("weight", 0), reverse=True)
    return unique[:20]


def _extract_fund_holdings(pdf) -> List[Dict]:
    holdings = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2:
                continue
            header = " ".join([str(c) for c in table[0] if c])
            if ("基金名称" not in header and "基金简称" not in header):
                continue
            if "占净值" not in header and "比例" not in header and "净值比" not in header:
                continue
            name_col = weight_col = None
            for ci, cell in enumerate(table[0]):
                c = str(cell) if cell else ""
                if "名称" in c or "基金" in c:
                    name_col = ci
                if "比例" in c or "净值" in c:
                    weight_col = ci
            if name_col is None or weight_col is None:
                continue
            for row in table[1:]:
                if len(row) <= max(name_col, weight_col):
                    continue
                name = _clean(row[name_col])
                weight = _parse_weight(row[weight_col])
                if name and weight is not None and weight > 0:
                    ticker, market = map_to_ticker_and_market(name, "")
                    holdings.append({"name": name, "ticker": ticker, "weight": weight, "market": market, "type": "fund"})
    return holdings


def _extract_stock_holdings(pdf) -> List[Dict]:
    holdings = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2:
                continue
            header = " ".join([str(c) for c in table[0] if c])
            if "股票代码" not in header and "股票名称" not in header:
                continue
            if "占净值" not in header and "比例" not in header:
                continue
            name_col = code_col = weight_col = None
            for ci, cell in enumerate(table[0]):
                c = str(cell) if cell else ""
                if "名称" in c:
                    name_col = ci
                if "代码" in c:
                    code_col = ci
                if "比例" in c or "净值" in c:
                    weight_col = ci
            if name_col is None or weight_col is None:
                continue
            for row in table[1:]:
                if len(row) <= max(name_col, weight_col):
                    continue
                name = _clean(row[name_col])
                code_str = _clean(row[code_col]) if code_col is not None and len(row) > code_col else ""
                weight = _parse_weight(row[weight_col])
                if name and weight is not None and weight > 0:
                    ticker, market = map_to_ticker_and_market(name, code_str)
                    holdings.append({"name": name, "ticker": ticker, "weight": weight, "market": market, "type": "stock"})
    return holdings


def _extract_bond_holdings(pdf) -> List[Dict]:
    holdings = []
    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2:
                continue
            header = " ".join([str(c) for c in table[0] if c])
            if "债券" not in header:
                continue
            if "占净值" not in header and "比例" not in header:
                continue
            name_col = weight_col = None
            for ci, cell in enumerate(table[0]):
                c = str(cell) if cell else ""
                if "名称" in c:
                    name_col = ci
                if "比例" in c or "净值" in c:
                    weight_col = ci
            if name_col is None or weight_col is None:
                continue
            for row in table[1:]:
                if len(row) <= max(name_col, weight_col):
                    continue
                name = _clean(row[name_col])
                weight = _parse_weight(row[weight_col])
                if name and weight is not None and weight > 0:
                    holdings.append({"name": name, "ticker": "", "weight": weight, "market": "bond", "type": "bond"})
    return holdings


# ============================================================
# 3. Ticker映射 + 市场识别
# ============================================================
def map_to_ticker_and_market(name: str, code_str: str) -> Tuple[str, str]:
    if not name:
        return ("", "other")
    name_upper = name.upper().strip()

    # 1) 已知US ETF字典
    for keyword, ticker in _KNOWN_US_ETFS.items():
        if keyword.upper() in name_upper:
            return (ticker, "US")

    # 2) 名称含US关键词
    us_kws = ["ETF", "FUND", "TRUST", "SPDR", "ISHARES", "VANGUARD",
               "INVESCO", "PROSHARES", "GLOBAL X", "WISDOMTREE",
               "VANECK", "DIREXION", "ARK ", "ETC"]
    for kw in us_kws:
        if kw in name_upper:
            m = re.search(r'\b([A-Z]{2,5})\b', name_upper)
            if m:
                return (m.group(1), "US")
            return ("", "US")

    # 3) 代码识别
    if code_str:
        code_clean = re.sub(r'[^0-9]', '', code_str)
        if len(code_clean) == 5:
            return (code_clean.zfill(5), "HK")
        elif len(code_clean) == 6 and code_clean[:2] in _A_SHARE_PREFIXES:
            return (code_clean, "A")

    # 4) 名称中嵌入的代码
    hk_m = re.search(r'\b(\d{5})\b', name)
    if hk_m:
        return (hk_m.group(1).zfill(5), "HK")
    a_m = re.search(r'\b(\d{6})\b', name)
    if a_m and a_m.group(1)[:2] in _A_SHARE_PREFIXES:
        return (a_m.group(1), "A")

    return ("", "other")


def filter_and_normalize(holdings: List[Dict]) -> Tuple[List[Tuple[str, float, str]], List[Dict]]:
    valid, excluded = [], []
    for h in holdings:
        ticker = h.get("ticker", "")
        market = h.get("market", "other")
        weight = h.get("weight", 0)
        name = h.get("name", "")
        if market in ("US", "HK", "A") and ticker:
            valid.append((ticker, weight, market))
        else:
            excluded.append({"name": name, "market": market, "weight": weight,
                             "reason": f"market={market}" if not ticker else "no_ticker"})
    total_w = sum(w for _, w, _ in valid)
    if total_w <= 0:
        return [], excluded
    normalized = [(t, w / total_w * 100, m) for t, w, m in valid]
    return normalized, excluded


def _clean(val) -> str:
    if val is None:
        return ""
    return re.sub(r'\s+', ' ', str(val)).strip()


def _parse_weight(val) -> Optional[float]:
    if val is None:
        return None
    s = str(val).strip().replace("%", "").replace("％", "")
    if not s or s in ("-", "--", ""):
        return None
    try:
        v = float(s)
        return v if v > 0 else None
    except (ValueError, TypeError):
        return None


# ============================================================
# 4. 便捷入口：获取持仓
# ============================================================
def get_fund_holdings(code: str, pdf_cache_dir: str = None) -> Tuple[List[Tuple[str, float, str]], List[Dict], Optional[str]]:
    """获取基金前20大持仓（归一化后）。

    Returns:
        (valid_holdings, excluded, error_msg)
        valid_holdings: [(ticker, weight_pct, market), ...]
        excluded: [{"name", "reason", ...}, ...]
        error_msg: None on success
    """
    if pdf_cache_dir is None:
        pdf_cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "runtime_data", "qreport")

    report_id = fetch_latest_report_id(code)
    if not report_id:
        return [], [], f"{code}: 无法获取季报ID"

    pdf_path = download_report_pdf(report_id, pdf_cache_dir)
    if not pdf_path:
        return [], [], f"{code}: PDF下载失败 (report_id={report_id})"

    raw = extract_holdings_from_pdf(pdf_path)
    if not raw:
        return [], [], f"{code}: PDF解析无持仓数据"

    valid, excluded = filter_and_normalize(raw)
    return valid, excluded, None


# ============================================================
# 5. DB写入
# ============================================================
def store_holdings_to_db(code: str, holdings: List[Tuple[str, float, str]],
                         report_date: str = None, db_path: str = None):
    """将持仓写入DB holdings表。

    Args:
        code: 基金代码
        holdings: [(ticker, weight, market), ...]
        report_date: 报告日期，默认今天
        db_path: DB路径，默认 runtime_data/lof_db/lof.db
    """
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "runtime_data", "lof_db", "lof.db")
    if report_date is None:
        report_date = datetime.now().strftime("%Y-%m-%d")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    # 先删除该基金旧持仓
    conn.execute("DELETE FROM holdings WHERE code = ?", (code,))
    # 写入新持仓
    for ticker, weight, market in holdings:
        conn.execute(
            "INSERT OR REPLACE INTO holdings (code, report_date, ticker, name, weight, market) VALUES (?, ?, ?, ?, ?, ?)",
            (code, report_date, ticker, "", weight, market)
        )
    conn.commit()
    conn.close()


def update_all_holdings(fund_codes: List[str], pdf_cache_dir: str = None, db_path: str = None):
    """批量更新所有基金持仓到DB。

    Returns:
        results: {code: {"ok": bool, "holdings": int, "excluded": int, "error": str|None}}
    """
    results = {}
    for code in fund_codes:
        valid, excluded, err = get_fund_holdings(code, pdf_cache_dir)
        if err:
            results[code] = {"ok": False, "holdings": 0, "excluded": 0, "error": err}
            print(f"  {code} FAIL: {err}")
            continue
        store_holdings_to_db(code, valid, db_path=db_path)
        results[code] = {"ok": True, "holdings": len(valid), "excluded": len(excluded), "error": None}
        excl_names = [e["name"] for e in excluded]
        print(f"  {code} OK: {len(valid)} holdings, {len(excluded)} excluded {excl_names}")
    return results
