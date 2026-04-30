"""AH 溢价normalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_ah_snapshot(payload: dict) -> list[dict]:
    """把 AH 快照转换为 The Bus 记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="ah_premium",
                market="AH",
                symbol="*",
                name="AH 溢价",
                event_type="premium_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "AH 抓取失败") if isinstance(payload, dict) else "AH 抓取失败",
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="ah_premium",
                market="AH",
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
                    "pair_price": item.get("hPrice"),
                    "pair_price_cny": item.get("hPriceCny"),
                    "exchange_rate": item.get("exchangeRate"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(item.get("source") or payload.get("source") or ""),
                date=str(payload.get("tradeDate") or ""),
                tags=["premium", "ah"],
            )
        )
    return rows

