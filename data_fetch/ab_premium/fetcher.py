"""AB 溢价fetcher。"""

from __future__ import annotations

from shared.market_service import build_ab_snapshot


def fetch_ab_snapshot(*, force_pairs: bool = False) -> dict:
    """抓取 AB 溢价快照，保持旧输出结构兼容。"""

    return build_ab_snapshot(force_pairs=force_pairs)


