"""convertible_bond正股history_sync器。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.convertible_bond.history_source import sync_cb_stock_history


def sync_convertible_bond_stock_history(*, force_full: bool = False) -> dict:
    """sync_convertible_bond_stock_history价格。"""

    return sync_cb_stock_history(force_full=force_full)


