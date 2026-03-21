"""AH 溢价策略服务。"""

from __future__ import annotations

from shared.models.service_result import build_success


def build_ah_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """消费总线记录并恢复旧接口兼容结构。"""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    rows = [dict(record.get("raw") or {}) for record in bus_records if record.get("status") == "ok"]
    rows.sort(key=lambda item: float(item.get("premium") or -10**9), reverse=True)
    return build_success(
        rows,
        updateTime=fetch_payload.get("updateTime"),
        total=fetch_payload.get("total", len(rows)),
        exchangeRate=fetch_payload.get("exchangeRate"),
        source=fetch_payload.get("source"),
        tradeDate=fetch_payload.get("tradeDate"),
        historySync=fetch_payload.get("historySync"),
    )

