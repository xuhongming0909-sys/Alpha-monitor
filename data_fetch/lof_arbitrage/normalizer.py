"""LOF 套利标准化器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_lof_arbitrage_snapshot(payload: dict) -> list[dict]:
    """把 LOF 套利快照转换成总线记录。"""

    if not payload or payload.get("success") is False:
        error_message = (payload or {}).get("error", "lof_arbitrage_fetch_failed")
        return [
            create_market_record(
                plugin="lof_arbitrage",
                market="CN",
                symbol="*",
                name="lof_arbitrage_snapshot",
                event_type="lof_arbitrage_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": error_message},
                status="error",
                source=(payload or {}).get("source"),
                message=error_message,
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="lof_arbitrage",
                market=str(item.get("market") or "CN"),
                symbol=str(item.get("code") or ""),
                name=str(item.get("name") or ""),
                event_type="lof_arbitrage_snapshot",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "price": item.get("price"),
                    "change_rate": item.get("changeRate"),
                    "turnover_wan": item.get("turnoverWan"),
                    "nav": item.get("nav"),
                    "nav_date": item.get("navDate"),
                    "index_name": item.get("indexName"),
                    "index_increase_rate": item.get("indexIncreaseRate"),
                    "currency": item.get("currency"),
                    "group": item.get("marketGroup"),
                },
                raw=dict(item),
                status="ok",
                currency=str(item.get("currency") or "CNY"),
                source=str(payload.get("source") or ""),
                date=str(payload.get("updateTime") or "")[:10],
                tags=["lof_arbitrage", str(item.get("marketGroup") or "")],
            )
        )
    return rows

