"""上海时区时间工具。"""

from __future__ import annotations

import re
from datetime import datetime, timezone, timedelta
from typing import Any, Dict


SHANGHAI_TIMEZONE = timezone(timedelta(hours=8))


def now_iso() -> str:
    """返回当前 UTC ISO 时间。"""

    return datetime.now().isoformat()


def shanghai_now() -> datetime:
    """返回上海时区当前时间。"""

    return datetime.now(SHANGHAI_TIMEZONE)


def get_shanghai_parts(dt: datetime | None = None) -> Dict[str, Any]:
    """把shanghai_time拆成统一的日期与时分秒结构。"""

    current = dt.astimezone(SHANGHAI_TIMEZONE) if dt else shanghai_now()
    weekday = current.weekday() + 1
    if weekday == 7:
        weekday = 0
    return {
        "date": current.strftime("%Y-%m-%d"),
        "hour": current.hour,
        "minute": current.minute,
        "second": current.second,
        "weekday": weekday,
    }


def normalize_date_text(value: Any) -> str:
    """提取 YYYY-MM-DD 格式，兼容含时间的字符串。"""

    text = str(value or "").strip()
    if not text:
        return ""
    hit = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return hit.group(0) if hit else text[:10]


def parse_time_to_minutes(time_text: str | None) -> int | None:
    """把 HH:MM 文本转换成分钟数。"""

    hit = re.match(r"^(\d{2}):(\d{2})$", str(time_text or "").strip())
    if not hit:
        return None
    hour = int(hit.group(1))
    minute = int(hit.group(2))
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None
    return hour * 60 + minute


def is_trading_weekday(dt: datetime | None = None) -> bool:
    """判断是否为交易日周一到周五。"""

    weekday = get_shanghai_parts(dt)["weekday"]
    return 1 <= weekday <= 5


def is_trading_session(dt: datetime | None = None) -> bool:
    """判断当前是否处于 A/H 常用盘中时段。"""

    parts = get_shanghai_parts(dt)
    if parts["weekday"] < 1 or parts["weekday"] > 5:
        return False
    minutes = parts["hour"] * 60 + parts["minute"]
    return (
        9 * 60 + 30 <= minutes <= 11 * 60 + 30
        or 13 * 60 <= minutes <= 15 * 60
        or 9 * 60 + 30 <= minutes <= 12 * 60
        or 13 * 60 <= minutes <= 16 * 60
    )


def is_after_cutoff(dt: datetime | None = None, cutoff_time: str = "16:10") -> bool:
    """判断当前是否已过某个上海时区截止时间。"""

    parts = get_shanghai_parts(dt)
    if parts["weekday"] < 1 or parts["weekday"] > 5:
        return False
    cutoff_minutes = parse_time_to_minutes(cutoff_time)
    if cutoff_minutes is None:
        return False
    return parts["hour"] * 60 + parts["minute"] >= cutoff_minutes

