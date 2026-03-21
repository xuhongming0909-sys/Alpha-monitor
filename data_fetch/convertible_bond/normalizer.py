"""convertible_bondnormalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_convertible_bond_snapshot(payload: dict) -> list[dict]:
    """把convertible_bond实时结果转换成总线记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="convertible_bond",
                market="CN",
                symbol="*",
                name="convertible_bond快照",
                event_type="convertible_bond_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "convertible_bond抓取失败") if isinstance(payload, dict) else "convertible_bond抓取失败",
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="convertible_bond",
                market="CN",
                symbol=str(item.get("code") or ""),
                name=str(item.get("bondName") or ""),
                event_type="convertible_bond_snapshot",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "price": item.get("price"),
                    "stock_price": item.get("stockPrice"),
                    "convert_price": item.get("convertPrice"),
                    "convert_value": item.get("convertValue"),
                    "premium_rate": item.get("premiumRate"),
                    "theoretical_premium_rate": item.get("theoreticalPremiumRate"),
                    "double_low": item.get("doubleLow"),
                    "remaining_years": item.get("remainingYears"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(payload.get("source") or ""),
                date=str(payload.get("tradeDate") or "") or str(payload.get("updateTime") or "")[:10],
                tags=["convertible_bond"],
            )
        )
    return rows

