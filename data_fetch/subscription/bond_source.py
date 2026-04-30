# AI-SUMMARY: subscription 上游 API：实时行情与数据抓取
# 对应 INDEX.md §9 文件摘要索引

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Convertible-bond subscription snapshot loader backed by SQLite history."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, Iterable, Optional

import akshare as ak
import pandas as pd

from shared.config.script_config import get_config
from shared.db import subscription_history_db as db

_CONFIG = get_config()
_SUBSCRIPTION_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("subscription") or {})
HISTORY_RETENTION_DAYS = max(30, int(_SUBSCRIPTION_CONFIG.get("history_retention_days") or 1095))


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in {"", "nan", "NaN", "nat", "NaT", "None"}:
        return True
    return bool(pd.isna(value))


def _parse_date(value: Any) -> Optional[date]:
    if _is_null(value):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        parsed = pd.to_datetime(str(value).strip(), errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date()
    except Exception:
        return None


def _date_str(value: Any) -> Optional[str]:
    parsed = _parse_date(value)
    return parsed.isoformat() if parsed else None


def _add_business_days(base: Optional[date], days: int) -> Optional[date]:
    if base is None:
        return None
    try:
        ts = pd.Timestamp(base) + pd.tseries.offsets.BDay(days)
        return ts.date()
    except Exception:
        return base


def _to_float(value: Any) -> Optional[float]:
    if _is_null(value):
        return None
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def _to_int(value: Any) -> Optional[int]:
    parsed = _to_float(value)
    if parsed is None:
        return None
    try:
        return int(parsed)
    except Exception:
        return None


def _first(row: pd.Series, keys: Iterable[str]) -> Any:
    for key in keys:
        if key in row and not _is_null(row[key]):
            return row[key]
    return None


def _status(
    subscribe_date: Optional[date],
    listing_date: Optional[date],
    payment_date: Optional[date],
    today: date,
) -> Dict[str, Any]:
    if subscribe_date and subscribe_date > today:
        return {"status": "upcoming", "daysUntilSubscribe": (subscribe_date - today).days}
    if subscribe_date and subscribe_date == today:
        return {"status": "subscribing", "daysUntilSubscribe": 0}
    if listing_date and listing_date <= today:
        return {"status": "listed", "daysUntilSubscribe": None}
    if payment_date and payment_date >= today:
        return {"status": "waiting_payment", "daysUntilSubscribe": None}
    if listing_date and listing_date > today:
        return {"status": "waiting_listing", "daysUntilSubscribe": None}
    return {"status": "subscribed", "daysUntilSubscribe": None}


def get_bond_data() -> Dict[str, Any]:
    now = datetime.now()
    today = now.date()
    db.init_db()

    fetched_rows = []
    sync_source = "subscription_db"
    fetch_error = None
    prune_stats = {"removedRows": 0, "removedSyncLogs": 0, "cutoffDate": ""}

    try:
        df = ak.bond_zh_cov()
        for _, row in df.iterrows():
            code = str(_first(row, ["债券代码", "代码"]) or "").strip()
            name = str(_first(row, ["债券简称", "名称"]) or "").strip()
            subscribe_date = _parse_date(_first(row, ["申购日期"]))
            if not code or not subscribe_date:
                continue

            lottery_date = _parse_date(_first(row, ["中签号发布日"]))
            listing_date = _parse_date(_first(row, ["上市时间", "上市日期"]))
            payment_date = _add_business_days(lottery_date, 1) if lottery_date else None

            fetched_rows.append(
                {
                    "code": code,
                    "name": name,
                    "subscribeDate": subscribe_date.isoformat(),
                    "subscribeCode": str(_first(row, ["申购代码"]) or code),
                    "listingDate": _date_str(listing_date),
                    "lotteryDate": _date_str(lottery_date),
                    "paymentDate": _date_str(payment_date),
                    "subscribeLimit": _to_int(_first(row, ["申购上限"])),
                    "stockCode": str(_first(row, ["正股代码"]) or "") or None,
                    "stockName": str(_first(row, ["正股简称"]) or "") or None,
                    "stockPrice": _to_float(_first(row, ["正股价", "正股价格"])),
                    "convertPrice": _to_float(_first(row, ["转股价"])),
                    "convertValue": _to_float(_first(row, ["转股价值"])),
                    "bondPrice": _to_float(_first(row, ["债现价", "现价"])),
                    "premiumRate": _to_float(_first(row, ["转股溢价率"])),
                    "lotteryRate": _to_float(_first(row, ["中签率"])),
                    "issueSizeYi": _to_float(_first(row, ["发行规模"])),
                    "creditRating": str(_first(row, ["信用评级"]) or "") or None,
                }
            )

        db.upsert_rows("bond", fetched_rows, "akshare")
        prune_stats = db.prune_old_rows(HISTORY_RETENTION_DAYS)
        db.record_sync("bond", len(fetched_rows), True, "akshare")
        sync_source = "akshare+sqlite"
    except Exception as exc:
        fetch_error = str(exc)
        db.record_sync("bond", 0, False, "akshare", fetch_error)

    stored_rows = db.load_rows("bond")
    if not stored_rows:
        return {
            "success": False,
            "data": [],
            "upcoming": [],
            "updateTime": now.isoformat(),
            "error": fetch_error or "Convertible-bond subscription history is empty.",
        }

    rows = []
    upcoming = []
    for item in stored_rows:
        subscribe_date = _parse_date(item.get("subscribeDate"))
        if not subscribe_date:
            continue
        listing_date = _parse_date(item.get("listingDate"))
        payment_date = _parse_date(item.get("paymentDate"))
        status_info = _status(subscribe_date, listing_date, payment_date, today)
        normalized = {
            **item,
            "status": status_info["status"],
            "daysUntilSubscribe": status_info["daysUntilSubscribe"],
        }
        if normalized["status"] == "upcoming":
            upcoming.append(normalized)
        else:
            rows.append(normalized)

    upcoming.sort(key=lambda x: x.get("daysUntilSubscribe") if x.get("daysUntilSubscribe") is not None else 10**9)
    rows.sort(key=lambda x: x.get("subscribeDate") or "", reverse=True)

    return {
        "success": True,
        "data": rows,
        "upcoming": upcoming,
        "updateTime": now.isoformat(),
        "source": sync_source,
        "historyCount": len(stored_rows),
        "prunedRows": int(prune_stats.get("removedRows") or 0),
        "prunedSyncLogs": int(prune_stats.get("removedSyncLogs") or 0),
    }


if __name__ == "__main__":
    print(json.dumps(get_bond_data(), ensure_ascii=False))
