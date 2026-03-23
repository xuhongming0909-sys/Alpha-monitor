"""Build outward-facing event-arbitrage responses from normalized records."""

from __future__ import annotations

from shared.models.service_result import build_success


EVENT_CATEGORY_KEYS = (
    "hk_private",
    "cn_private",
    "a_event",
    "rights_issue",
    "announcement_pool",
)


def _empty_categories() -> dict[str, list[dict]]:
    return {key: [] for key in EVENT_CATEGORY_KEYS}


def _build_overview(categories: dict[str, list[dict]]) -> dict:
    hk_rows = categories.get("hk_private") or []
    cn_rows = categories.get("cn_private") or []
    a_rows = categories.get("a_event") or []
    announcement_rows = categories.get("announcement_pool") or []
    all_rows = [*hk_rows, *cn_rows, *a_rows]
    positive_count = sum(1 for row in all_rows if isinstance(row, dict) and (row.get("spreadRate") or 0) > 0)
    return {
        "totalCount": len(all_rows),
        "positiveCount": positive_count,
        "hkPrivateCount": len(hk_rows),
        "cnPrivateCount": len(cn_rows),
        "aEventCount": len(a_rows),
        "announcementPoolCount": len(announcement_rows),
    }


def build_event_arbitrage_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """Convert normalized bus records into the event-arbitrage API contract."""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    categories = _empty_categories()
    for record in bus_records:
        if record.get("status") != "ok":
            continue
        row = dict(record.get("raw") or {})
        category = str(row.get("category") or "").strip()
        if category in categories:
            categories[category].append(row)

    data = fetch_payload.get("data") if isinstance(fetch_payload.get("data"), dict) else {}
    source_status = data.get("sourceStatus") if isinstance(data.get("sourceStatus"), dict) else {}
    for key in EVENT_CATEGORY_KEYS:
        categories.setdefault(key, [])
        source_status.setdefault(key, {"status": "pending", "itemCount": len(categories[key])})

    payload = {
        "overview": _build_overview(categories),
        "categories": categories,
        "sourceStatus": source_status,
        "updateTime": fetch_payload.get("updateTime"),
        "cacheTime": fetch_payload.get("cacheTime"),
        "servedFromCache": False,
    }
    return build_success(payload, updateTime=fetch_payload.get("updateTime"), source=fetch_payload.get("source"))
