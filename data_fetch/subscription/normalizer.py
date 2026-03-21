"""subscriptionnormalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def _build_error_record(plugin_name: str, message: str, source: str | None = None) -> dict:
    return create_market_record(
        plugin=plugin_name,
        market="CN",
        symbol="*",
        name="申购快照",
        event_type="subscription_item",
        quote_time=now_iso(),
        metrics={},
        raw={"error": message},
        status="error",
        source=source,
        message=message,
    )


def _rows_from_payload(payload: dict, plugin_name: str, kind: str) -> list[dict]:
    if not payload or payload.get("success") is False:
        return [_build_error_record(plugin_name, (payload or {}).get("error", "申购抓取失败"), (payload or {}).get("source"))]

    rows = []
    merged_rows = [*(payload.get("upcoming") or []), *(payload.get("data") or [])]
    for item in merged_rows:
        rows.append(
            create_market_record(
                plugin=plugin_name,
                market="CN",
                symbol=str(item.get("code") or item.get("stockCode") or item.get("bondCode") or ""),
                name=str(item.get("name") or item.get("stockName") or item.get("bondName") or ""),
                event_type="subscription_item",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "kind": kind,
                    "status": item.get("status"),
                    "subscribe_date": item.get("subscribeDate"),
                    "lottery_date": item.get("lotteryDate"),
                    "payment_date": item.get("paymentDate"),
                    "listing_date": item.get("listingDate"),
                    "days_until_subscribe": item.get("daysUntilSubscribe"),
                    "issue_price": item.get("issuePrice"),
                    "latest_price": item.get("latestPrice"),
                    "lottery_rate": item.get("lotteryRate"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(payload.get("source") or ""),
                date=str(item.get("subscribeDate") or ""),
                tags=["subscription", kind],
            )
        )
    return rows


def normalize_ipo_snapshot(payload: dict) -> list[dict]:
    return _rows_from_payload(payload, "subscription", "ipo")


def normalize_bond_subscription_snapshot(payload: dict) -> list[dict]:
    return _rows_from_payload(payload, "subscription", "bond")

