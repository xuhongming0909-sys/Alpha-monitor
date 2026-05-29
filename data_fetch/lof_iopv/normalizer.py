# -*- coding: utf-8 -*-
"""LOF IOPV 数据标准化器。"""

from __future__ import annotations

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def normalize_lof_iopv_snapshot(payload: dict) -> list[dict]:
    """将 LOF IOPV 快照转换为总线记录。"""
    if not payload or payload.get("success") is False:
        error_message = (payload or {}).get("error", "lof_iopv_fetch_failed")
        return [
            create_market_record(
                plugin="lof_iopv",
                market="CN",
                symbol="*",
                name="lof_iopv_snapshot",
                event_type="lof_iopv_snapshot",
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
        metrics = {
            "price": item.get("price"),
            "nav": item.get("nav"),
            "nav_date": item.get("navDate"),
            "currency": item.get("currency"),
            "group": item.get("marketGroup"),
            "stock_position": item.get("stockPosition"),
        }
        if item.get("indexIncreaseRate") is not None:
            metrics["index_increase_rate"] = item["indexIncreaseRate"]

        rows.append(
            create_market_record(
                plugin="lof_iopv",
                market=str(item.get("market") or "CN"),
                symbol=str(item.get("code") or ""),
                name=str(item.get("name") or ""),
                event_type="lof_iopv_snapshot",
                quote_time=str(payload.get("updateTime") or now_iso()),
                metrics=metrics,
                raw=dict(item),
                status="ok",
                currency=str(item.get("currency") or "CNY"),
                source=str(payload.get("source") or ""),
                date=str(payload.get("updateTime") or "")[:10],
                tags=["lof_iopv", str(item.get("marketGroup") or "")],
            )
        )
    return rows