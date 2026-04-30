"""dividend策略服务。"""

from __future__ import annotations


def build_dividend_response(fetch_payload: dict) -> dict:
    """当前dividend接口直接沿用抓取结果，策略层保留为独立边界。"""

    return fetch_payload

