"""subscriptionfetcher。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.subscription.ipo_source import get_ipo_data
from data_fetch.subscription.bond_source import get_bond_data


def fetch_ipo_snapshot() -> dict:
    """抓取 A 股新股申购数据。"""

    return get_ipo_data()


def fetch_bond_subscription_snapshot() -> dict:
    """抓取convertible_bond申购数据。"""

    return get_bond_data()

