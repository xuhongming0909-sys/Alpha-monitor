#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""IPO subscription snapshot loader backed by SQLite history."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Dict, Iterable, Optional

import akshare as ak
import pandas as pd

import subscription_history_db as db


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


def _normalize_schedule_dates(
    subscribe_date: Optional[date],
    lottery_date: Optional[date],
    payment_date: Optional[date],
) -> tuple[Optional[date], Optional[date]]:
    if subscribe_date is None:
        return lottery_date, payment_date

    min_lottery = _add_business_days(subscribe_date, 1)
    min_payment = _add_business_days(subscribe_date, 2)

    if lottery_date is None or (min_lottery and lottery_date < min_lottery):
        lottery_date = min_lottery

    min_payment_by_lottery = _add_business_days(lottery_date, 1) if lottery_date else None
    hard_floor = min_payment
    if min_payment_by_lottery and hard_floor:
        hard_floor = max(min_payment_by_lottery, hard_floor)
    elif min_payment_by_lottery:
        hard_floor = min_payment_by_lottery

    if payment_date is None or (hard_floor and payment_date < hard_floor):
        payment_date = hard_floor

    return lottery_date, payment_date


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


def _market_from_code(code: str) -> str:
    code = str(code or "")
    if code.startswith("6"):
        return "SH"
    if code.startswith(("0", "3")):
        return "SZ"
    if code.startswith(("4", "8")):
        return "BJ"
    return "UNKNOWN"


def _normalize_code(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text.zfill(6) if text.isdigit() else text


def _build_dxsyl_map() -> Dict[str, Dict[str, Any]]:
    try:
        df = ak.stock_dxsyl_em()
    except Exception:
        return {}

    result: Dict[str, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        code = _normalize_code(_first(row, ["股票代码", "代码"]))
        if not code:
            continue

        result[code] = {
            "issuePrice": _to_float(_first(row, ["发行价", "发行价格"])),
            "latestPrice": _to_float(_first(row, ["最新价"])),
            "openPremium": _to_float(_first(row, ["开盘溢价", "开盘溢价率"])),
            "firstDayChange": _to_float(_first(row, ["首日涨幅"])),
            "listingDate": _date_str(_first(row, ["上市日期"])),
            "lotteryRateOnline": _to_float(_first(row, ["网上-发行中签率", "网上发行中签率"])),
        }

    return result


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


def get_ipo_data() -> Dict[str, Any]:
    now = datetime.now()
    today = now.date()
    db.init_db()

    fetched_rows = []
    sync_source = "subscription_db"
    fetch_error = None

    try:
        dxsyl_map = _build_dxsyl_map()
        df = ak.stock_new_ipo_cninfo()
        for _, row in df.iterrows():
            code = _normalize_code(_first(row, ["证券代码", "证券代号", "股票代码"]))
            name = str(_first(row, ["证券简称", "名称"]) or "").strip()
            subscribe_date = _parse_date(_first(row, ["申购日期", "发行日期"]))
            if not code or not subscribe_date:
                continue

            dxsyl_item = dxsyl_map.get(code, {})
            listing_date = _parse_date(_first(row, ["上市日期"])) or _parse_date(dxsyl_item.get("listingDate"))
            lottery_date = _parse_date(_first(row, ["中签公告日", "摇号结果公告日"]))
            payment_date = _parse_date(_first(row, ["中签缴款日", "缴款日期"]))
            lottery_date, payment_date = _normalize_schedule_dates(subscribe_date, lottery_date, payment_date)

            fetched_rows.append(
                {
                    "code": code,
                    "name": name,
                    "subscribeDate": subscribe_date.isoformat(),
                    "subscribeCode": code,
                    "listingDate": _date_str(listing_date),
                    "lotteryDate": _date_str(lottery_date),
                    "paymentDate": _date_str(payment_date),
                    "issuePrice": _to_float(_first(row, ["发行价格", "发行价"])) or dxsyl_item.get("issuePrice"),
                    "latestPrice": dxsyl_item.get("latestPrice"),
                    "openPremium": dxsyl_item.get("openPremium"),
                    "firstDayChange": dxsyl_item.get("firstDayChange"),
                    "dxsylYield": (
                        dxsyl_item.get("firstDayChange")
                        if dxsyl_item.get("firstDayChange") is not None
                        else dxsyl_item.get("openPremium")
                    ),
                    "peRatio": _to_float(_first(row, ["发行市盈率"])),
                    "lotteryRate": _to_float(_first(row, ["网上发行中签率"])) or dxsyl_item.get("lotteryRateOnline"),
                    "subscribeLimit": _to_int(_first(row, ["网上申购上限"])),
                    "totalSharesWan": _to_float(_first(row, ["总发行数量"])),
                    "onlineSharesWan": _to_float(_first(row, ["网上发行数量"])),
                    "market": _market_from_code(code),
                }
            )

        db.upsert_rows("ipo", fetched_rows, "akshare")
        db.record_sync("ipo", len(fetched_rows), True, "akshare")
        sync_source = "akshare+sqlite"
    except Exception as exc:
        fetch_error = str(exc)
        db.record_sync("ipo", 0, False, "akshare", fetch_error)

    stored_rows = db.load_rows("ipo")
    if not stored_rows:
        return {
            "success": False,
            "data": [],
            "upcoming": [],
            "updateTime": now.isoformat(),
            "error": fetch_error or "IPO subscription history is empty.",
        }

    rows = []
    upcoming = []
    for item in stored_rows:
        subscribe_date = _parse_date(item.get("subscribeDate"))
        if not subscribe_date:
            continue
        listing_date = _parse_date(item.get("listingDate"))
        lottery_date = _parse_date(item.get("lotteryDate"))
        payment_date = _parse_date(item.get("paymentDate"))
        lottery_date, payment_date = _normalize_schedule_dates(subscribe_date, lottery_date, payment_date)
        status_info = _status(subscribe_date, listing_date, payment_date, today)
        normalized = {
            **item,
            "lotteryDate": _date_str(lottery_date),
            "paymentDate": _date_str(payment_date),
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
    }


if __name__ == "__main__":
    print(json.dumps(get_ipo_data(), ensure_ascii=False))
