# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF浜屽垎绫?鎸囨暟鍨?涓诲姩鍨?鍩洪噾鍒嗙被鍣?+ 鎸佷粨鑾峰彇
# 瀵瑰簲 INDEX.md 9.3 鏂囦欢鎽樿绱㈠紩
"""LOF鍩洪噾浜屽垎绫讳綋绯汇€?
鎸囨暟鍨? ETF/鎸囨暟/鏈熻揣鏄犲皠, 鍩轰簬涓氱哗鍩哄噯, 鍥炴祴MAE<0.5%
涓诲姩鍨? 鍏圓PI鍐峆DF, 鎸佷粨鍚堣<25%鏃秄allback鍒癙DF瑙ｆ瀽
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ============================================================
# 鎸囨暟鍨嬫爣鐨勬槧灏? 鍩洪噾浠ｇ爜 -> [(ticker, weight), ...]
# 涓夌ticker绫诲瀷:
#   - 鎸囨暟: ^NDX, ^GSPC, ^SP500-45, ^SP500-30, ^HSI (^寮€澶?
#   - 鏈熻揣: CL=F, BZ=F, GC=F 绛?(=F缁撳熬)
#   - ETF:  KWEB, AGG, GLD, RYH, XBI, IYR, XOP 绛?(绾瓧姣?
# Yahoo Deno浠ｇ悊闄愬埗: ^SP500EW-35/^SPBIO/^DJUSRE/^SPSIOP 鍙繑鍥?澶?#   鈫?鐢‥TF鏇夸唬: RYH/XBI/IYR/XOP
# 鏄犲皠渚濇嵁: 涓氱哗姣旇緝鍩哄噯, 鍥炴祴楠岃瘉
# ============================================================
INDEX_ETF: Dict[str, List[Tuple[str, float]]] = {
    # --- 缇庤偂鎸囨暟 (^ticker, Yahoo鏈夊畬鏁村巻鍙? ---
    "161125": [("^GSPC", 100.0)],          # 鏍囨櫘500
    "161130": [("^NDX", 100.0)],           # 绾虫柉杈惧厠100
    "161128": [("^SP500-45", 100.0)],      # 鏍囨櫘500淇℃伅绉戞妧
    "162415": [("XLY", 100.0)],            # 鏍囨櫘缇庡浗鍝佽川娑堣垂(=Consumer Discretionary)
    # --- 鏈熻揣 (=F) ---
    # --- ETF (鎸囨暟ticker浠ｇ悊涓嶅彲鐢ㄦ椂鐨勬浛浠? ---
    "161126": [("RYH", 100.0)],            # 鏍囨櫘500鍖荤枟淇濆仴绛夋潈閲?(^SP500EW-35鏃犲巻鍙?
    "161127": [("XBI", 100.0)],            # 鏍囨櫘鐢熺墿绉戞妧 (^SPBIO鏃犲巻鍙?
    "160140": [("IYR", 100.0)],            # 閬撶惣鏂編鍥絉EIT (^DJUSRE鏃犲巻鍙?
    "162719": [("IEO", 100.0)],            # 鐭虫补LOF: iShares US Oil & Gas E&P
    "162411": [("XOP", 100.0)],            # 鏍囨櫘鐭虫补澶╃劧姘斾笂娓?(^SPSIOP鏃犲巻鍙?
    # --- ETF (鏈韩鏃犲搴旀寚鏁皌icker) ---
    "160719": [("GC=F", 100.0)],           # 嘉实黄金: 黄金期货→伦敦金
    "160416": [("IXC", 100.0)],            # 鐭虫补鍩洪噾: iShares Global Energy
    "164824": [("INDA", 100.0)],           # 鍗板害鍩洪噾: iShares MSCI India
    "164701": [("GLD", 100.0)],            # 榛勯噾LOF: SPDR Gold Shares
    "164906": [("KWEB", 100.0)],           # 涓浜掕仈缃? KraneShares CSI China Internet
    "501300": [("AGG", 100.0)],            # 缇庡厓鍊? iShares Core US Aggregate Bond
}


def is_index_fund(code: str) -> bool:
    """鍒ゆ柇鏄惁涓烘寚鏁板瀷鍩洪噾"""
    return code in INDEX_ETF


def get_fund_class(code: str) -> str:
    """杩斿洖鍩洪噾鍒嗙被: 'index' / 'active'"""
    return "index" if code in INDEX_ETF else "active"


def get_index_etf_ticker(code: str) -> str:
    """杩斿洖鎸囨暟鍨嬪熀閲戠殑涓绘爣鐨則icker(绗竴涓?"""
    etfs = INDEX_ETF.get(code, [])
    return etfs[0][0] if etfs else ""


def is_futures_ticker(ticker: str) -> bool:
    """鍒ゆ柇鏄惁涓烘湡璐icker (濡?CL=F, BZ=F, GC=F)"""
    return "=F" in ticker


def is_index_ticker(ticker: str) -> bool:
    """鍒ゆ柇鏄惁涓烘寚鏁皌icker (濡?^NDX, ^GSPC)"""
    return ticker.startswith("^")


def get_index_holdings(code: str) -> List[Dict]:
    """鎸囨暟鍨嬫寔浠? 浠庢爣鐨勬槧灏勬瀯寤? market鏍规嵁ticker绫诲瀷鍒ゆ柇"""
    etfs = INDEX_ETF.get(code, [])
    if not etfs:
        return []
    result = []
    for t, w in etfs:
        if is_index_ticker(t):
            market = "INDEX"
        elif is_futures_ticker(t):
            market = "FUTURES"
        else:
            market = "US"
        result.append({"ticker": t, "weight": w, "market": market})
    return result


def get_active_holdings(code: str) -> List[Dict]:
    """涓诲姩鍨嬫寔浠? 浠嶥B璇诲彇(鐢県oldings_updater缁存姢)"""
    from data_fetch.lof_db.schema import get_db
    conn = get_db()
    latest = conn.execute(
        "SELECT report_date FROM holdings WHERE code = ? ORDER BY report_date DESC LIMIT 1",
        (code,)
    ).fetchone()
    if not latest:
        conn.close()
        return []
    rows = conn.execute(
        "SELECT ticker, name, weight, market FROM holdings WHERE code = ? AND report_date = ? ORDER BY weight DESC",
        (code, latest[0])
    ).fetchall()
    conn.close()
    return [{"ticker": r[0], "name": r[1], "weight": r[2], "market": r[3]} for r in rows]


def get_active_holdings_hardcoded(code: str) -> List[Dict]:
    """涓诲姩鍨嬪厹搴? 浣跨敤hardcoded鎸佷粨(浠庝笂瀛ｅ害瀛ｆ姤)"""
    _HARDCODED: Dict[str, List[Tuple[str, float, str]]] = {
        "163208": [
            ("02015", 9.8, "HK"), ("09888", 9.5, "HK"),
            ("00981", 7.6, "HK"), ("01810", 6.8, "HK"),
            ("03690", 5.7, "HK"), ("09999", 5.2, "HK"),
            ("00285", 4.8, "HK"), ("01024", 3.9, "HK"),
            ("02518", 3.5, "HK"), ("06181", 2.9, "HK"),
        ],
        "501312": [
            ("ARKK", 18.74, "US"), ("ARKG", 15.35, "US"),
            ("ARKQ", 11.59, "US"), ("SOXX", 9.51, "US"),
            ("AIQ", 7.85, "US"),   ("QQQ", 7.45, "US"),
            ("BOTZ", 7.44, "US"),  ("XLK", 6.44, "US"),
            ("SMH", 4.29, "US"),   ("FINX", 1.20, "US"),
        ],
        "501225": [("PSI", 18.32, "US"), ("SOXQ", 18.25, "US"),
                   ("SOXX", 18.23, "US"), ("SMH", 18.17, "US")],
    }
    raw = _HARDCODED.get(code, [])
    return [{"ticker": t, "weight": w, "market": m} for t, w, m in raw]


def get_holdings_for_service(code: str) -> List[Dict]:
    """瀹炴椂鏈嶅姟鐢? 鎸囨暟鍨嬬敤鏍囩殑鏄犲皠, 涓诲姩鍨嬬敤DB+hardcoded"""
    if is_index_fund(code):
        return get_index_holdings(code)
    holdings = get_active_holdings(code)
    if holdings:
        return holdings
    return get_active_holdings_hardcoded(code)


def get_holdings_for_backtest(code: str) -> List[Dict]:
    """鍥炴祴鐢? 鎸囨暟鍨嬬敤鏍囩殑鏄犲皠, 涓诲姩鍨嬬敤DB浼樺厛+hardcoded鍏滃簳"""
    if is_index_fund(code):
        return get_index_holdings(code)
    holdings = get_active_holdings(code)
    if holdings:
        return holdings
    return get_active_holdings_hardcoded(code)