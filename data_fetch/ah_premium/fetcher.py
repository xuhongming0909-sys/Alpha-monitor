# AI-SUMMARY: AH 溢价抓取调度：调用腾讯行情 API 并标准化为 Bus 记录
# 对应 INDEX.md §9 文件摘要索引

"""AH 溢价fetcher。"""

from __future__ import annotations

from data_fetch.ah_premium.source import build_ah_snapshot


def fetch_ah_snapshot(*, force_pairs: bool = False) -> dict:
    """抓取 AH 溢价快照，保持旧输出结构兼容。"""

    return build_ah_snapshot(force_pairs=force_pairs)


