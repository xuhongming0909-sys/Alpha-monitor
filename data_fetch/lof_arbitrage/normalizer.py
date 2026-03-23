"""Normalize LOF/QDII source rows into The Bus records."""

from __future__ import annotations

from typing import Any

from shared.bus.market_record import create_market_record
from shared.config.script_config import get_config
from shared.time.shanghai_time import now_iso


def _clean_text(value: Any) -> str:
    text = str(value or "").replace("\xa0", " ").strip()
    return "" if text in {"-", "--", "None", "null"} else text


def _sanitize_raw(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_raw(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_raw(item) for item in value]
    if isinstance(value, str):
        return value.replace("\xa0", " ").strip()
    return value


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


def _format_decimal(value: float | None, digits: int = 4) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def _combine_timestamp(*parts: Any) -> str:
    text_parts = [_clean_text(part) for part in parts]
    text_parts = [part for part in text_parts if part]
    return " ".join(text_parts).strip()


def _build_estimated_fields(item: dict[str, Any], current_price: float | None, nav_value: float | None) -> dict[str, Any]:
    strategy_config = get_config().get("strategy", {}).get("lof_arbitrage", {})
    allow_derivation = bool(strategy_config.get("derive_estimate_from_est_val_increase_rt", True))
    estimated_value = _to_float(item.get("estimate_value"))
    estimated_premium_rate = _to_percent(item.get("discount_rt"))
    estimated_increase_rate = _to_percent(item.get("est_val_increase_rt"))
    estimated_source = "direct_source" if estimated_value is not None or estimated_premium_rate is not None else ""

    if allow_derivation and estimated_value is None and nav_value is not None and estimated_increase_rate is not None:
        estimated_value = nav_value * (1 + estimated_increase_rate / 100.0)
        estimated_source = "derived_from_est_val_increase_rt"

    if allow_derivation and estimated_premium_rate is None and estimated_value not in {None, 0} and current_price is not None:
        estimated_premium_rate = ((current_price / estimated_value) - 1) * 100.0
        if not estimated_source:
            estimated_source = "derived_from_est_val_increase_rt"

    has_estimate_signal = any(
        value is not None and value != ""
        for value in (estimated_value, estimated_premium_rate, estimated_increase_rate)
    )
    estimated_time = ""
    if has_estimate_signal:
        estimated_time = (
            _clean_text(item.get("last_est_datetime"))
            or _combine_timestamp(item.get("last_est_dt"), item.get("last_est_time"))
            or _clean_text(item.get("est_val_dt"))
            or _clean_text(item.get("last_time"))
        )

    label_map = {
        "direct_source": "源直接返回",
        "derived_from_est_val_increase_rt": "Jisilu估值涨幅推导",
    }

    return {
        "estimatedValue": estimated_value,
        "estimatedValueText": _clean_text(item.get("estimate_value")) or _format_decimal(estimated_value, 4),
        "estimatedTime": estimated_time,
        "estimatedPremiumRate": estimated_premium_rate,
        "estimatedPremiumRateText": _clean_text(item.get("discount_rt")) or _format_decimal(estimated_premium_rate, 2),
        "estimatedIncreaseRate": estimated_increase_rate,
        "estimatedIncreaseRateText": _clean_text(item.get("est_val_increase_rt")),
        "estimatedSource": estimated_source,
        "estimatedSourceLabel": label_map.get(estimated_source, ""),
    }


def _build_id(category: str, symbol: str, last_time: str) -> str:
    return f"{category}:{symbol}:{last_time or now_iso()}"


def _build_standardized_row(category: str, item: dict[str, Any], source_name: str) -> dict[str, Any]:
    symbol = _clean_text(item.get("fund_id"))
    detail_url = f"https://www.jisilu.cn/data/qdii/detail/{symbol}" if symbol else "https://www.jisilu.cn/data/qdii/"
    official_url = _clean_text(item.get("urls"))
    current_price = _to_float(item.get("price"))
    nav_value = _to_float(item.get("fund_nav"))
    estimated_fields = _build_estimated_fields(item, current_price, nav_value)
    return {
        "id": _build_id(category, symbol, _clean_text(item.get("last_time"))),
        "source": source_name,
        "category": category,
        "market": "CN",
        "symbol": symbol,
        "name": _clean_text(item.get("fund_nm")),
        "issuer": _clean_text(item.get("issuer_nm")),
        "currentPrice": current_price,
        "changeRate": _to_percent(item.get("increase_rt")),
        "volumeWan": _to_float(item.get("volume")),
        "turnoverRate": _to_percent(item.get("turnover_rt")),
        "priceDate": _clean_text(item.get("price_dt")),
        "quoteTimeText": _clean_text(item.get("last_time")),
        "amountWanShares": _to_float(item.get("amount")),
        "amountIncreaseWanShares": _to_float(item.get("amount_incr")),
        "amountIncreaseRate": _to_percent(item.get("amount_increase_rt")),
        "amountDate": _clean_text(item.get("amount_dt")),
        "amountIncreaseTips": _clean_text(item.get("amount_incr_tips")),
        "navValue": nav_value,
        "navValueText": _clean_text(item.get("fund_nav")),
        "navDate": _clean_text(item.get("nav_dt")),
        "navPremiumRate": _to_percent(item.get("nav_discount_rt")),
        "navPremiumRateText": _clean_text(item.get("nav_discount_rt")),
        "iopv": _to_float(item.get("iopv")),
        "iopvText": _clean_text(item.get("iopv")),
        "iopvTime": _clean_text(item.get("iopv_dt")),
        "iopvPremiumRate": _to_percent(item.get("iopv_discount_rt")),
        "iopvPremiumRateText": _clean_text(item.get("iopv_discount_rt")),
        **estimated_fields,
        "referenceIndex": _clean_text(item.get("index_nm")),
        "referenceIndexChangeRate": _to_percent(item.get("ref_increase_rt")),
        "referencePriceText": _clean_text(item.get("ref_price")),
        "applyStatus": _clean_text(item.get("apply_status")),
        "applyFeeRate": _to_percent(item.get("apply_fee")),
        "applyFeeText": _clean_text(item.get("apply_fee")) or _clean_text(item.get("apply_fee_tips")),
        "tradeFeeRate": _to_percent(item.get("t_fee")),
        "redeemStatus": _clean_text(item.get("redeem_status")),
        "redeemFeeRate": _to_percent(item.get("redeem_fee")),
        "redeemFeeText": _clean_text(item.get("redeem_fee")) or _clean_text(item.get("redeem_fee_tips")),
        "managementFeeRate": _to_percent(item.get("mt_fee")),
        "managementFeeText": _clean_text(item.get("mt_fee")),
        "managementFeeTips": _clean_text(item.get("mt_fee_tips")),
        "minAmountText": _clean_text(item.get("min_amt")),
        "currency": _clean_text(item.get("money_cd")),
        "fundType": _clean_text(item.get("lof_type")),
        "evaluationEnabled": _to_bool(item.get("eval_show")),
        "assetRatioText": _clean_text(item.get("asset_ratio")),
        "calculationTips": _clean_text(item.get("cal_tips")),
        "calculationIndexCode": _clean_text(item.get("cal_index_id")),
        "t0": _to_bool(item.get("t0")),
        "notes": _clean_text(item.get("notes")),
        "officialUrl": official_url,
        "sourceDetailUrl": detail_url,
        "detailUrl": detail_url,
        "raw": _sanitize_raw(dict(item)),
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
