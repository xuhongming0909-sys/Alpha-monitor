# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF二分类(指数型/主动型)基金分类器 + 持仓获取
# 对应 INDEX.md 9.3 文件摘要索引
"""LOF基金二分类体系。

指数型: ETF映射, 基于业绩基准, 回测MAE<0.5%
主动型: 先API再PDF, 持仓合计<25%时fallback到PDF解析
"""
from __future__ import annotations
from typing import Dict, List, Optional, Tuple


# ============================================================
# 指数型ETF映射: 基金代码 -> [(etf_ticker, weight), ...]
# 映射依据: 业绩比较基准中明确指定的指数, 回测MAE<0.5%
# ============================================================
INDEX_ETF: Dict[str, List[Tuple[str, float]]] = {
    "161125": [("SPY", 100.0)],   # 标普500
    "161130": [("QQQ", 100.0)],   # 纳指100
    "161128": [("XLK", 100.0)],   # 标普信息科技
    "161126": [("RYH", 100.0)],   # 标普医疗保健
    "161127": [("XBI", 100.0)],   # 标普生物科技
    "162415": [("XLY", 100.0)],   # 美国消费
    "160416": [("IXC", 100.0)],   # 石油基金
    "162719": [("IEO", 100.0)],   # 石油LOF
    "162411": [("XOP", 100.0)],   # 华宝油气
    "160719": [("GLD", 100.0)],   # 嘉实黄金
    "164824": [("INDA", 100.0)],  # 印度基金
    "160140": [("IYR", 100.0)],   # 美国REIT
    "164701": [("GLD", 100.0)],   # 黄金LOF
    "501300": [("AGG", 100.0)],   # 美元债
}


def is_index_fund(code: str) -> bool:
    """判断是否为指数型基金"""
    return code in INDEX_ETF


def get_fund_class(code: str) -> str:
    """返回基金分类: 'index' / 'active'"""
    return "index" if code in INDEX_ETF else "active"


def get_index_etf_ticker(code: str) -> str:
    """返回指数型基金的主ETF ticker(第一个)"""
    etfs = INDEX_ETF.get(code, [])
    return etfs[0][0] if etfs else ""


def get_index_holdings(code: str) -> List[Dict]:
    """指数型持仓: 从ETF映射构建"""
    etfs = INDEX_ETF.get(code, [])
    if not etfs:
        return []
    return [{"ticker": t, "weight": w, "market": "US"} for t, w in etfs]


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
        "160644": [
            ("TSM", 9.09, "US"), ("NVDA", 9.05, "US"), ("SNDK", 8.57, "US"),
            ("MU", 7.49, "US"), ("00700", 6.58, "HK"), ("GOOGL", 5.69, "US"),
            ("09988", 4.69, "HK"), ("00883", 3.96, "HK"), ("AVGO", 3.49, "US"),
            ("ASML", 2.85, "US"),
        ],
        "164906": [
            ("00700", 9.54, "HK"), ("PDD", 8.04, "US"), ("09988", 8.0, "HK"),
            ("03690", 6.62, "HK"), ("09999", 5.37, "HK"), ("09618", 4.25, "HK"),
            ("09888", 3.92, "HK"), ("02423", 3.88, "HK"), ("06618", 3.55, "HK"),
            ("YMM", 3.41, "US"),
        ],
        "163208": [
            ("00916", 3.21, "HK"), ("00836", 2.46, "HK"), ("00135", 1.97, "HK"),
            ("01798", 1.87, "HK"), ("06865", 1.43, "HK"), ("00968", 1.16, "HK"),
            ("01811", 1.14, "HK"), ("01171", 1.13, "HK"), ("00857", 0.90, "HK"),
            ("00386", 0.72, "HK"),
        ],
        "160125": [
            ("00288", 4.78, "HK"), ("09911", 4.27, "HK"), ("00700", 4.12, "HK"),
            ("00883", 4.11, "HK"), ("06869", 4.0, "HK"), ("01519", 3.87, "HK"),
            ("02590", 3.45, "HK"), ("06082", 3.34, "HK"), ("09988", 3.28, "HK"),
            ("06181", 2.9, "HK"),
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
    """实时服务用: 指数型用ETF映射, 主动型用DB+hardcoded"""
    if is_index_fund(code):
        return get_index_holdings(code)
    holdings = get_active_holdings(code)
    if holdings:
        return holdings
    return get_active_holdings_hardcoded(code)


def get_holdings_for_backtest(code: str) -> List[Dict]:
    """回测用: 指数型用ETF映射, 主动型用hardcoded"""
    if is_index_fund(code):
        return get_index_holdings(code)
    return get_active_holdings_hardcoded(code)