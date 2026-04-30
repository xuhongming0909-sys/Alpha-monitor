# AI-SUMMARY: AB 溢价抓取调度：调用腾讯行情 API 并标准化为 Bus 记录
# 对应 INDEX.md §9 文件摘要索引

"""AB 溢价fetcher。"""

from __future__ import annotations

from data_fetch.ab_premium.source import build_ab_snapshot


def fetch_ab_snapshot(*, force_pairs: bool = False) -> dict:
    """抓取 AB 溢价快照，保持旧输出结构兼容。"""

    return build_ab_snapshot(force_pairs=force_pairs)


