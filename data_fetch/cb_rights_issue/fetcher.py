"""cb_rights_issue fetcher。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.cb_rights_issue.history_source import sync_cb_rights_issue_stock_history
from data_fetch.cb_rights_issue.source import get_cb_rights_issue_source_snapshot


def fetch_cb_rights_issue_snapshot() -> dict:
    """抓取可转债抢权配售固定来源快照。"""

    return get_cb_rights_issue_source_snapshot(allow_inline_history_hydrate=False)


def sync_cb_rights_issue_stock_history_snapshot(*, force_full: bool = False) -> dict:
    """同步可转债抢权配售专用正股历史库。"""

    return sync_cb_rights_issue_stock_history(force_full=force_full)
