"""AB 溢价normalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_ab_snapshot(payload: dict) -> list[dict]:
    """把 AB 快照转换为 The Bus 记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="ab_premium",
                market="AB",
                symbol="*",
                name="AB 溢价",
                event_type="premium_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "AB 抓取失败") if isinstance(payload, dict) else "AB 抓取失败",
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="ab_premium",
                market="AB",
                symbol=str(item.get("aCode") or ""),
                name=str(item.get("aName") or ""),
                event_type="premium_snapshot",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "premium": item.get("premium"),
                    "percentile": item.get("percentile"),
                    "premium_min": item.get("premiumMin"),
                    "premium_max": item.get("premiumMax"),
                    "history_count": item.get("historyCount"),
                    "a_price": item.get("aPrice"),
                    "pair_price": item.get("bPrice"),
                    "pair_price_cny": item.get("bPriceCny"),
                    "exchange_rate": item.get("exchangeRate"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(item.get("source") or payload.get("source") or ""),
                date=str(payload.get("tradeDate") or ""),
                tags=["premium", "ab"],
            )
        )
    return rows

