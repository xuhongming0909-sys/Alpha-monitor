"""convertible_bondfetcher。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.convertible_bond.source import get_bond_cb_data


def fetch_convertible_bond_snapshot() -> dict:
    """抓取convertible_bond实时套利数据。"""

    return get_bond_cb_data()

