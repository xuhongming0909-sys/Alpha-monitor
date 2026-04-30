# AI-SUMMARY: event_arbitrage 数据标准化：原始数据转为 Bus 记录
# 对应 INDEX.md §9 文件摘要索引

"""Normalize event-arbitrage source rows into The Bus records."""

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
    text = _clean_text(value)
    if not text:
        return None
    if text.endswith("%"):
        text = text[:-1]
    return _to_float(text)


def _to_bool(value: Any) -> bool | None:
    text = _clean_text(value).lower()
    if text in {"是", "y", "yes", "true", "1"}:
        return True
    if text in {"否", "n", "no", "false", "0"}:
        return False
    return None


def _with_scheme(url: Any) -> str:
    text = _clean_text(url)
    if not text:
        return ""
    if text.startswith("http://") or text.startswith("https://"):
        return text
    return f"https://{text.lstrip('/')}"


def _build_id(category: str, symbol: str, detail_url: str, fallback: str) -> str:
    key = detail_url or fallback or symbol or now_iso()
    return f"{category}:{symbol}:{key}"


def _build_standardized_row(category: str, item: dict[str, Any], source_name: str) -> dict[str, Any]:
    if category == "hk_private":
        symbol = _clean_text(item.get("stock_code"))
        detail_url = _with_scheme(item.get("process_url"))
        offer_price_text = _clean_text(item.get("redeem_price")) or _clean_text(item.get("descr"))
        return {
            "id": _build_id(category, symbol, detail_url, _clean_text(item.get("release_date"))),
            "source": source_name,
            "category": category,
            "market": "HK",
            "symbol": symbol,
            "name": _clean_text(item.get("stock_nm")),
            "currentPrice": _to_float(item.get("price")),
            "currentPriceText": _clean_text(item.get("price")),
            "changeRate": _to_percent(item.get("increase_rt")),
            "changeRateText": _clean_text(item.get("increase_rt")),
            "marketValue": _to_float(item.get("market_value")),
            "marketValueText": _clean_text(item.get("market_value")),
            "offerPrice": _to_float(item.get("redeem_price")),
            "offerPriceText": offer_price_text,
            "spreadRate": _to_percent(item.get("arbitrage_space")),
            "spreadText": _clean_text(item.get("arbitrage_space")),
            "eventType": "港股私有化",
            "eventStage": _clean_text(item.get("process")),
            "offeror": _clean_text(item.get("offeror")),
            "offerorHolding": _to_percent(item.get("offeror_right")),
            "offerorHoldingText": _clean_text(item.get("offeror_right")),
            "registryPlace": _clean_text(item.get("registrar")),
            "dealMethod": _clean_text(item.get("way")),
            "canShort": _to_bool(item.get("short_flag")),
            "canCounter": _to_bool(item.get("counter_flag")),
            "summary": _clean_text(item.get("descr")),
            "detailUrl": detail_url,
            "officialMatch": None,
            "releaseDate": _clean_text(item.get("release_date")),
            "raw": dict(item),
        }

    if category == "cn_private":
        symbol = _clean_text(item.get("stock_code"))
        detail_url = _with_scheme(item.get("process_url"))
        offer_price_text = _clean_text(item.get("redeem_price")) or _clean_text(item.get("descr"))
        return {
            "id": _build_id(category, symbol, detail_url, _clean_text(item.get("release_date"))),
            "source": source_name,
            "category": category,
            "market": "US",
            "symbol": symbol,
            "name": _clean_text(item.get("stock_nm")),
            "currentPrice": _to_float(item.get("price")),
            "currentPriceText": _clean_text(item.get("price")),
            "changeRate": _to_percent(item.get("increase_rt")),
            "changeRateText": _clean_text(item.get("increase_rt")),
            "marketValue": _to_float(item.get("market_value")),
            "marketValueText": _clean_text(item.get("market_value")),
            "offerPrice": _to_float(item.get("redeem_price")),
            "offerPriceText": offer_price_text,
            "spreadRate": _to_percent(item.get("arbitrage_space")),
            "spreadText": _clean_text(item.get("arbitrage_space")),
            "eventType": "中概股私有化",
            "eventStage": _clean_text(item.get("process")),
            "offeror": _clean_text(item.get("offeror")),
            "offerorHolding": _to_percent(item.get("offeror_right")),
            "offerorHoldingText": _clean_text(item.get("offeror_right")),
            "registryPlace": "",
            "dealMethod": _clean_text(item.get("way")),
            "canShort": None,
            "canCounter": None,
            "summary": _clean_text(item.get("descr")),
            "detailUrl": detail_url,
            "officialMatch": None,
            "releaseDate": _clean_text(item.get("release_date")),
            "feesHint": _clean_text(item.get("descr")),
            "raw": dict(item),
        }

    symbol = _clean_text(item.get("stock_id"))
    announcement_url = _with_scheme(item.get("yaoyue_url"))
    question_id = _clean_text(item.get("question_id"))
    forum_url = "" if not question_id else f"https://www.jisilu.cn/question/{question_id}"
    return {
        "id": _build_id(category, symbol, announcement_url, question_id),
        "source": source_name,
        "category": category,
        "market": "CN",
        "symbol": symbol,
        "name": _clean_text(item.get("stock_nm")),
        "currentPrice": _to_float(item.get("price")),
        "currentPriceText": _clean_text(item.get("price")),
        "changeRate": _to_percent(item.get("increase_rt")),
        "changeRateText": _clean_text(item.get("increase_rt")),
        "marketValue": None,
        "marketValueText": "",
        "offerPrice": _to_float(item.get("choose_price")),
        "offerPriceText": _clean_text(item.get("choose_price")),
        "spreadRate": _to_percent(item.get("choose_discount_rt")),
        "spreadText": _clean_text(item.get("choose_discount_rt")),
        "eventType": _clean_text(item.get("type_cd")),
        "eventStage": "进行中" if _clean_text(item.get("active_flg")).upper() == "Y" else "",
        "offeror": "",
        "offerorHolding": None,
        "offerorHoldingText": "",
        "registryPlace": "",
        "dealMethod": _clean_text(item.get("type_cd")),
        "canShort": None,
        "canCounter": None,
        "summary": _clean_text(item.get("descr")),
        "detailUrl": announcement_url or forum_url,
        "officialMatch": None,
        "currency": _clean_text(item.get("money_type")),
        "safePrice": _to_float(item.get("safe_price")),
        "safePriceText": _clean_text(item.get("safe_price")),
        "safeDiscountRate": _to_percent(item.get("discount_rt")),
        "safeDiscountRateText": _clean_text(item.get("discount_rt")),
        "choosePrice": _to_float(item.get("choose_price")),
        "choosePriceText": _clean_text(item.get("choose_price")),
        "chooseDiscountRate": _to_percent(item.get("choose_discount_rt")),
        "chooseDiscountRateText": _clean_text(item.get("choose_discount_rt")),
        "announcementUrl": announcement_url,
        "forumUrl": forum_url,
        "raw": dict(item),
    }


def normalize_event_arbitrage_snapshot(payload: dict) -> list[dict]:
    """Convert fetched event-arbitrage categories into normalized bus records."""

    if not payload or payload.get("success") is False:
        return [
            create_market_record(
                plugin="event_arbitrage",
                market="MULTI",
                symbol="*",
                name="event_arbitrage",
                event_type="event_arbitrage_snapshot",
                quote_time=now_iso(),
                metrics={},
                raw={"error": payload.get("error") if isinstance(payload, dict) else "unknown"},
                status="error",
                source=(payload or {}).get("source") if isinstance(payload, dict) else None,
                message=(payload or {}).get("error", "event_arbitrage fetch failed") if isinstance(payload, dict) else "event_arbitrage fetch failed",
            )
        ]

    data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
    categories = data.get("categories") if isinstance(data.get("categories"), dict) else {}
    source_status = data.get("sourceStatus") if isinstance(data.get("sourceStatus"), dict) else {}
    quote_time = str(payload.get("updateTime") or now_iso())
    source_name = str(payload.get("source") or "jisilu")
    records = []

    for category, items in categories.items():
        if category == "rights_issue":
            continue
        for item in items or []:
            if not isinstance(item, dict):
                continue
            standardized = _build_standardized_row(category, item, source_name)
            metrics = {
                "category": category,
                "spread_rate": standardized.get("spreadRate"),
                "event_stage": standardized.get("eventStage"),
                "source_status": source_status.get(category, {}).get("status"),
            }
            records.append(
                create_market_record(
                    plugin="event_arbitrage",
                    market=str(standardized.get("market") or ""),
                    symbol=str(standardized.get("symbol") or ""),
                    name=str(standardized.get("name") or ""),
                    event_type=str(standardized.get("eventType") or category),
                    quote_time=quote_time,
                    metrics=metrics,
                    raw=standardized,
                    status="ok",
                    currency=standardized.get("currency"),
                    source=source_name,
                    date=str(standardized.get("releaseDate") or ""),
                    tags=["event_arbitrage", category],
                )
            )
    return records

