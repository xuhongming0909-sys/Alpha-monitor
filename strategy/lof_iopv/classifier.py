# -*- coding: utf-8 -*-
"""QDII LOF 分类器: A(指数跟踪) / B(T10持仓)。"""

def get_calc_mode(estimation: str) -> str:
    return {"A": "指数跟踪法", "B": "T10持仓加权法"}.get(estimation, "未知")
