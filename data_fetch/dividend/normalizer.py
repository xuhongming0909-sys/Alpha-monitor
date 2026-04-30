# AI-SUMMARY: dividend 数据标准化：原始数据转为 Bus 记录
# 对应 INDEX.md §9 文件摘要索引

"""dividendnormalizer器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_dividend_payload(payload: dict) -> list[dict]:
    """把dividend查询结果转换成总线记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="dividend",
                market="CN",
                symbol="*",
                name="dividend数据",
                event_type="dividend_item",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "dividend抓取失败") if isinstance(payload, dict) else "dividend抓取失败",
            )
        ]

    data = payload.get("data") or payload
    if not isinstance(data, dict):
        return []
    return [
        create_market_record(
            plugin="dividend",
            market="CN",
            symbol=str(data.get("code") or ""),
            name=str(data.get("name") or ""),
            event_type="dividend_item",
            quote_time=str(payload.get("updateTime") or now_iso()),
            metrics={
                "record_date": data.get("recordDate"),
                "ex_dividend_date": data.get("exDividendDate"),
                "dividend_per_share": data.get("dividendPerShare"),
                "dividend_yield": data.get("dividendYield"),
                "current_price": data.get("currentPrice"),
            },
            raw=dict(data),
            status="ok",
            currency="CNY",
            source=str(payload.get("source") or data.get("source") or ""),
            date=str(data.get("recordDate") or ""),
            tags=["dividend"],
        )
    ]


def normalize_upcoming_dividend_payload(payload: dict) -> list[dict]:
    """把即将到来的dividend列表转换成总线记录。"""

    if not payload or payload.get("success") is False:
        return []
    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="dividend",
                market="CN",
                symbol=str(item.get("code") or ""),
                name=str(item.get("name") or ""),
                event_type="dividend_upcoming",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "record_date": item.get("recordDate"),
                    "days_until_record": item.get("daysUntilRecord"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(payload.get("source") or ""),
                date=str(item.get("recordDate") or ""),
                tags=["dividend", "upcoming"],
            )
        )
    return rows

