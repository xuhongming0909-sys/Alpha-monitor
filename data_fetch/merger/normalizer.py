"""mergernormalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_merger_snapshot(payload: dict) -> list[dict]:
    """把merger结果转换成 The Bus 记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="merger",
                market="CN",
                symbol="*",
                name="merger",
                event_type="merger_announcement",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "merger抓取失败") if isinstance(payload, dict) else "merger抓取失败",
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="merger",
                market="CN",
                symbol=str(item.get("secCode") or item.get("code") or item.get("targetCode") or ""),
                name=str(item.get("secName") or item.get("targetName") or item.get("name") or ""),
                event_type="merger_announcement",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "announcement_date": item.get("announcementDate"),
                    "deal_type": item.get("dealType") or item.get("type"),
                    "offer_price": item.get("offerPrice") or item.get("bidPrice"),
                    "stock_price": item.get("stockPrice") or item.get("price"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(payload.get("source") or ""),
                date=str(item.get("announcementDate") or ""),
                tags=["merger"],
            )
        )
    return rows

