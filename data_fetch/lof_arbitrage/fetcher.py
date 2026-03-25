"""LOF 套利抓取入口。"""

from __future__ import annotations

from data_fetch.lof_arbitrage.source import get_lof_arbitrage_source_snapshot


def fetch_lof_arbitrage_snapshot() -> dict:
    """抓取 LOF 套利固定来源快照。"""

    return get_lof_arbitrage_source_snapshot()

