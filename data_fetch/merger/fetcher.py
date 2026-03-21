"""mergerfetcher。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.merger.source import MergerArbitrageScraper


def fetch_merger_snapshot() -> dict:
    """抓取merger套利数据。"""

    return MergerArbitrageScraper().run()

