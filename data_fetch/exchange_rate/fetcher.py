"""exchange_ratefetcher。"""

from __future__ import annotations

from shared.market_service import get_exchange_rates


def fetch_exchange_rate_snapshot() -> dict:
    """抓取港币、美元兑人民币exchange_rate。"""

    return get_exchange_rates()


