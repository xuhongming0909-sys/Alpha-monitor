# AI-SUMMARY: 可转债抓取调度：调用集思录/东方财富 API
# 对应 INDEX.md §9 文件摘要索引

"""convertible_bondfetcher。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.convertible_bond.source import get_bond_cb_data


def fetch_convertible_bond_snapshot() -> dict:
    """抓取convertible_bond实时套利数据。"""

    return get_bond_cb_data(allow_inline_history_hydrate=False)

