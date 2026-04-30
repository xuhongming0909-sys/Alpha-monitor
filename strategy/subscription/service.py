"""subscription策略服务。"""

from __future__ import annotations

from shared.models.service_result import build_success


def build_subscription_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """按旧接口格式恢复 upcoming/data 结构。"""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    rows = [dict(record.get("raw") or {}) for record in bus_records if record.get("status") == "ok"]
    upcoming = [item for item in rows if str(item.get("status") or "") == "upcoming"]
    history = [item for item in rows if str(item.get("status") or "") != "upcoming"]
    upcoming.sort(key=lambda item: item.get("daysUntilSubscribe") if item.get("daysUntilSubscribe") is not None else 10**9)
    history.sort(key=lambda item: str(item.get("subscribeDate") or ""), reverse=True)
    return build_success(
        history,
        updateTime=fetch_payload.get("updateTime"),
        upcoming=upcoming,
        source=fetch_payload.get("source"),
        historyCount=fetch_payload.get("historyCount", len(rows)),
    )

