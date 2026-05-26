# -*- coding: utf-8 -*-
# AI-SUMMARY: QDII LOF 分类器: A(指数跟踪) / B(T10持仓)
# 对应 INDEX.md §9.3 文件摘要索引
"""QDII LOF 分类器: A(指数跟踪) / B(T10持仓)

分类依据:
- A类: 有明确ETF标的，用指数跟踪法估值
- B类: 有前十大持仓数据，用T10持仓加权法估值

分类结果来源: tools/backtest/lof13_backtest_report.md
"""


def get_calc_mode(estimation: str) -> str:
    """返回估值方法的中文标签"""
    return {
        "A": "指数跟踪法",
        "B": "T10持仓加权法",
    }.get(estimation, "未知")