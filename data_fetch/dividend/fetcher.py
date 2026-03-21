"""dividendfetcher。"""

from __future__ import annotations

from shared.paths.tool_paths import ensure_scripts_on_path

ensure_scripts_on_path()

from data_fetch.dividend.source import get_dividend_data, get_upcoming_dividends


def fetch_dividend_snapshot(code: str) -> dict:
    """抓取单只股票的dividend数据。"""

    return get_dividend_data(code)


def fetch_upcoming_dividend_snapshot(days: int = 3) -> dict:
    """抓取指定天数内的dividend提醒数据。"""

    return get_upcoming_dividends(days)

