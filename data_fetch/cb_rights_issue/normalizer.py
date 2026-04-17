"""cb_rights_issue normalizer。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_cb_rights_issue_snapshot(payload: dict) -> list[dict]:
    """把固定来源快照标准化为总线记录。"""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="cb_rights_issue",
                market="CN",
                symbol="*",
                name="cb_rights_issue快照",
                event_type="cb_rights_issue_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": (payload or {}).get("error", "cb_rights_issue抓取失败")},
                status="error",
                source=(payload or {}).get("source"),
                message=(payload or {}).get("error", "cb_rights_issue抓取失败"),
            )
        ]

    rows = []
    for item in payload.get("data", []) or []:
        rows.append(
            create_market_record(
                plugin="cb_rights_issue",
                market="CN",
                symbol=str(item.get("bondCode") or ""),
                name=str(item.get("bondName") or ""),
                event_type="cb_rights_issue_snapshot",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics={
                    "stock_code": item.get("stockCode"),
                    "stock_price": item.get("stockPrice"),
                    "convert_price": item.get("convertPrice"),
                    "progress_name": item.get("progressName"),
                    "apply_date": item.get("applyDate"),
                    "record_date": item.get("recordDate"),
                    "list_date": item.get("listDate"),
                    "volatility250": item.get("volatility250"),
                    "volatility60": item.get("volatility60"),
                },
                raw=dict(item),
                status="ok",
                currency="CNY",
                source=str(payload.get("source") or ""),
                date=str(payload.get("updateTime") or "")[:10],
                tags=["cb_rights_issue"],
            )
        )
    return rows
