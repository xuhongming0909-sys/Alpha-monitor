"""AH 溢价fetcher。"""

from __future__ import annotations

from shared.market_service import build_ah_snapshot


def fetch_ah_snapshot(*, force_pairs: bool = False) -> dict:
    """抓取 AH 溢价快照，保持旧输出结构兼容。"""

    return build_ah_snapshot(force_pairs=force_pairs)


