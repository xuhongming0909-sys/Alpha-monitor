"""Normalize LOF/QDII source rows into The Bus records."""

from __future__ import annotations

from typing import Any

from shared.bus.market_record import create_market_record
from shared.time.shanghai_time import now_iso


def _clean_text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text in {"-", "--", "None", "null"} else text


def _to_float(value: Any) -> float | None:
    text = _clean_text(value).replace(",", "")
    if not text:
        return None
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text)
    except Exception:
        return None


def _to_percent(value: Any) -> float | None:
    return _to_float(value)


def _to_bool(value: Any) -> bool | None:
    text = _clean_text(value).upper()
    if text == "Y":
        return True
    if text == "N":
        return False
    return None


def _build_id(category: str, symbol: str, last_time: str) -> str:
    return f"{category}:{symbol}:{last_time or now_iso()}"


def _build_standardized_row(category: str, item: dict[str, Any], source_name: str) -> dict[str, Any]:
    symbol = _clean_text(item.get("fund_id"))
    detail_url = f"https://www.jisilu.cn/data/qdii/detail/{symbol}" if symbol else "https://www.jisilu.cn/data/qdii/"
    return {
        "id": _build_id(category, symbol, _clean_text(item.get("last_time"))),
        "source": source_name,
        "category": category,
        "market": "CN",
        "symbol": symbol,
        "name": _clean_text(item.get("fund_nm")),
        "issuer": _clean_text(item.get("issuer_nm")),
        "currentPrice": _to_float(item.get("price")),
        "changeRate": _to_percent(item.get("increase_rt")),
        "volumeWan": _to_float(item.get("volume")),
        "amountWanShares": _to_float(item.get("amount")),
        "amountIncreaseWanShares": _to_float(item.get("amount_incr")),
        "navValue": _to_float(item.get("fund_nav")),
        "navDate": _clean_text(item.get("nav_dt")),
        "navPremiumRate": _to_percent(item.get("nav_discount_rt")),
        "iopv": _to_float(item.get("iopv")),
        "iopvTime": _clean_text(item.get("iopv_dt")),
        "iopvPremiumRate": _to_percent(item.get("iopv_discount_rt")),
        "estimatedValue": _to_float(item.get("estimate_value")),
        "estimatedTime": _clean_text(item.get("last_est_datetime")) or _clean_text(item.get("est_val_dt")),
        "estimatedPremiumRate": _to_percent(item.get("discount_rt")),
        "referenceIndex": _clean_text(item.get("index_nm")),
        "referenceIndexChangeRate": _to_percent(item.get("ref_increase_rt")),
        "applyStatus": _clean_text(item.get("apply_status")),
        "applyFeeRate": _to_percent(item.get("apply_fee")),
        "tradeFeeRate": _to_percent(item.get("t_fee")),
        "redeemStatus": _clean_text(item.get("redeem_status")),
        "redeemFeeRate": _to_percent(item.get("redeem_fee")),
        "managementFeeRate": _to_percent(item.get("mt_fee")),
        "minAmountText": _clean_text(item.get("min_amt")),
        "currency": _clean_text(item.get("money_cd")),
        "t0": _to_bool(item.get("t0")),
        "notes": _clean_text(item.get("notes")),
        "detailUrl": detail_url,
        "quoteTimeText": _clean_text(item.get("last_time")),
        "raw": dict(item),
    }


def normalize_lof_arbitrage_snapshot(payload: dict) -> list[dict]:
    """Convert fetched LOF snapshot categories into normalized bus records."""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="lof_arbitrage",
                market="CN",
                symbol="*",
                name="lof_arbitrage",
                event_type="lof_arbitrage_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "lof_arbitrage fetch failed") if isinstance(payload, dict) else "lof_arbitrage fetch failed",
            )
        ]

    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    categories = data.get("categories") if isinstance(data.get("categories"), dict) else {}
    source_status = data.get("sourceStatus") if isinstance(data.get("sourceStatus"), dict) else {}
    quote_time = str(payload.get("updateTime") or now_iso())
    source_name = str(payload.get("source") or "jisilu_qdii")
    records = []

    for category, items in categories.items():
        for item in items or []:
            if not isinstance(item, dict):
                continue
            standardized = _build_standardized_row(category, item, source_name)
            metrics = {
                "category": category,
                "nav_premium_rate": standardized.get("navPremiumRate"),
                "iopv_premium_rate": standardized.get("iopvPremiumRate"),
                "estimate_premium_rate": standardized.get("estimatedPremiumRate"),
                "apply_status": standardized.get("applyStatus"),
                "source_status": source_status.get(category, {}).get("status"),
            }
            records.append(
                create_market_record(
                    plugin="lof_arbitrage",
                    market="CN",
                    symbol=str(standardized.get("symbol") or ""),
                    name=str(standardized.get("name") or ""),
                    event_type="lof_premium_arbitrage",
                    quote_time=quote_time,
                    metrics=metrics,
                    raw=standardized,
                    status="ok",
                    currency=standardized.get("currency"),
                    source=source_name,
                    date=str(standardized.get("navDate") or ""),
                    tags=["lof_arbitrage", category],
                )
            )
    return records
