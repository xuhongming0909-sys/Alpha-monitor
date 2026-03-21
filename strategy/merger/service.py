"""merger策略服务。"""

from __future__ import annotations

from shared.models.service_result import build_success


def build_merger_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """把总线记录整理成merger模块对外使用的统一结果。"""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    rows = [dict(record.get("raw") or {}) for record in bus_records if record.get("status") == "ok"]
    return build_success(
        rows,
        updateTime=fetch_payload.get("updateTime"),
        total=fetch_payload.get("total", len(rows)),
        source=fetch_payload.get("source"),
    )

