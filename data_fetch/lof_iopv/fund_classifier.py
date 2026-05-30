# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF二分类(指数型/主动型)基金分类器 + 持仓获取
# 对应 INDEX.md 9.3 文件摘要索引
"""LOF基金二分类体系。

指数型: ETF/指数/期货映射, 基于业绩基准, 回测MAE<0.5%
主动型: 全API再PDF, 持仓合计<25%时fallback到PDF解析
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ============================================================
# 鎸囨暟鍨嬫爣鐨勬槧灏? 鍩洪噾浠ｇ爜 -> [(ticker, weight), ...]
# 涓夌ticker绫诲瀷:
#   - 鎸囨暟: ^NDX, ^GSPC, ^SP500-45, ^SP500-30, ^HSI (^寮€澶?
#   - 
#   - ETF:  KWEB, AGG, GLD, RYH, XBI, IYR, XOP 绛?(绾瓧姣?
# Yahoo Deno浠ｇ悊闄愬埗: ^SP500EW-35/^SPBIO/^DJUSRE/^SPSIOP 鍙繑鍥?澶?#   鈫?鐢‥TF鏇夸唬: RYH/XBI/IYR/XOP
# 鏄犲皠渚濇嵁: 涓氱哗姣旇緝鍩哄噯, 鍥炴祴楠岃瘉
# ============================================================
INDEX_ETF: Dict[str, List[Tuple[str, float]]] = {
    # --- 美股指数 (^ticker, Yahoo有完整历史) ---
    "161125": [("^GSPC", 100.0)],          # 标普500
    "161130": [("^NDX", 100.0)],           # 纳斯达克100
    "161128": [("^SP500-45", 100.0)],      # 标普500淇℃伅绉戞妧
    "162415": [("XLY", 100.0)],            # 标普美国品质消费(=Consumer Discretionary)
    # --- 
    # --- ? ---
    "161126": [("RYH", 100.0)],            # 标普500鍖荤枟淇濆仴绛夋潈閲?(^SP500EW-35鏃犲巻鍙?
    "161127": [("XBI", 100.0)],            # 标普生物科技 (^SPBIO无历史)
    "160140": [("IYR", 100.0)],            # 道琼斯美国REIT (^DJUSRE无历史)
    "162719": [("IEO", 100.0)],            # 石油LOF: iShares US Oil & Gas E&P
    "162411": [("XOP", 100.0)],            # 鏍囨櫘鐭虫补澶╃劧姘斾笂娓?(^SPSIOP鏃犲巻鍙?
    # --- 
    "160719": [("GC=F", 100.0)],           # 嘉实黄金: 黄金期货→伦敦金
    "161226": [("AG0", 100.0)],            # 白银LOF: 上海白银期货主力合约(akshare)
    "160416": [("IXC", 100.0)],            # 石油基金: iShares Global Energy
    "164824": [("INDA", 100.0)],           # 印度基金: iShares MSCI India
    "164701": [("GLD", 100.0)],            # 黄金LOF: SPDR Gold Shares
    "164906": [("KWEB", 100.0)],           # 中概互联网: KraneShares CSI China Internet
    "501300": [("AGG", 100.0)],            # 美元债: iShares Core US Aggregate Bond
}


def is_index_fund(code: str) -> bool:
    """判断是否为指数型基金"""
    return code in INDEX_ETF


def get_fund_class(code: str) -> str:
    """返回基金分类: index / active"""
    return "index" if code in INDEX_ETF else "active"


def get_index_etf_ticker(code: str) -> str:
    """返回指数型基金的主标的ticker(第一个)"""
    etfs = INDEX_ETF.get(code, [])
    return etfs[0][0] if etfs else ""


# 国内期货主力合约符号集合 (2-3字母 + "0")
_DOMESTIC_FUTURES = {"AG0", "AU0", "CU0", "AL0", "ZN0", "PB0", "NI0", "SN0",
                     "RB0", "HC0", "SS0", "BU0", "RU0", "FU0", "LU0", "NR0",
                     "SC0", "SP0", "EB0", "EG0", "PG0", "LH0", "AP0", "CJ0",
                     "CF0", "SR0", "TA0", "MA0", "OI0", "RM0", "FG0", "SA0"}


def is_futures_ticker(ticker: str) -> bool:
    """判断是否为期货ticker: Yahoo格式(=F结尾) 或 国内主力合约(如AG0)"""
    return "=F" in ticker or ticker in _DOMESTIC_FUTURES


def is_index_ticker(ticker: str) -> bool:
    """判断是否为指数ticker (如 ^NDX)"""
    return ticker.startswith("^")


def get_index_holdings(code: str) -> List[Dict]:
    """指数型持仓: 从标的映射构建, market根据ticker类型判断"""
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
    """主动型持仓: 从DB读取(由holdings_updater维护)"""
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
    """主动型兜底: 使用hardcoded持仓(从上季度季报)"""
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
    """实时服务用: 指数型用标的映射, 主动型用DB+hardcoded"""
    if is_index_fund(code):
        return get_index_holdings(code)
    holdings = get_active_holdings(code)
    if holdings:
        return holdings
    return get_active_holdings_hardcoded(code)


def get_holdings_for_backtest(code: str) -> List[Dict]:
    """回测用: 指数型用标的映射, 主动型用DB优先+hardcoded兜底"""
    if is_index_fund(code):
        return get_index_holdings(code)
    holdings = get_active_holdings(code)
    if holdings:
        return holdings
    return get_active_holdings_hardcoded(code)