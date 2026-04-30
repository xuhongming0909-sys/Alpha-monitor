# AI-SUMMARY: 股息业务计算：登记日跟踪、股息率计算
# 对应 INDEX.md §9 文件摘要索引

"""dividend策略服务。"""

from __future__ import annotations


def build_dividend_response(fetch_payload: dict) -> dict:
    """当前dividend接口直接沿用抓取结果，策略层保留为独立边界。"""

    return fetch_payload

