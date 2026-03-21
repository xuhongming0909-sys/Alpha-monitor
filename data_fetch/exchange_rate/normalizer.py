"""exchange_ratenormalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_exchange_rate_snapshot(payload: dict) -> list[dict]:
    """把exchange_rate快照转换为 The Bus 记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="exchange_rate",
                market="FX",
                symbol="CNY",
                name="exchange_rate快照",
                event_type="exchange_rate",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "exchange_rate抓取失败") if isinstance(payload, dict) else "exchange_rate抓取失败",
            )
        ]

    data = payload.get("data") or {}
    return [
        create_market_record(
            plugin="exchange_rate",
            market="FX",
            symbol="CNY",
            name="人民币exchange_rate",
            event_type="exchange_rate",
            quote_time=str(payload.get("updateTime") or now_iso()),
            metrics={
                "hkd_to_cny": data.get("hkdToCny"),
                "usd_to_cny": data.get("usdToCny"),
            },
            raw=dict(data),
            status="ok",
            currency="CNY",
            source=str(data.get("source") or payload.get("source") or ""),
            date=str(data.get("updateTime") or "")[:10],
            tags=["fx"],
        )
    ]

