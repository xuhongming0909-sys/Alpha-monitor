# AI-SUMMARY: AB 溢价上游 API：腾讯行情 + 配对库 + 历史数据库
# 对应 INDEX.md §9 文件摘要索引

"""AB 溢价数据抓取源。

职责：
1. 从配对库加载 AB 股配对列表
2. 调用腾讯行情获取 A 股和 B 股实时价格
3. 计算溢价率并同步历史数据库
4. 返回标准化数据结构供 fetcher 使用
"""

from __future__ import annotations

from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from shared.db.market_pairs import load_dynamic_pairs
from shared.db import premium_history_db as premium_db
from shared.market_service import clean_name, get_fx_rates, get_quotes
from shared.models.service_result import build_error as shared_build_error, build_success as shared_build_success

SHANGHAI_TZ = timezone(timedelta(hours=8))


def _build_success(data: Any, **extra: Any) -> dict[str, Any]:
    payload = shared_build_success(data, **extra)
    payload.pop("error", None)
    return payload


def _calc_empirical_percentile(current: float, premiums: list[float] | None) -> float | None:
    if not premiums:
        return None
    values = sorted(float(value) for value in premiums if value is not None)
    if len(values) < 2:
        return None
    position = bisect_right(values, float(current))
    return max(0.0, min(100.0, (position / len(values)) * 100))


def _summarize_premium(summary: dict[str, Any], premium: float, premium_samples: list[float] | None = None) -> dict[str, Any]:
    min_premium = summary.get("minPremium3Y")
    max_premium = summary.get("maxPremium3Y")
    percentile = _calc_empirical_percentile(premium, premium_samples)
    return {
        "percentile": round(percentile, 2) if percentile is not None else None,
        "premiumMin": round(float(min_premium), 4) if min_premium is not None else None,
        "premiumMax": round(float(max_premium), 4) if max_premium is not None else None,
        "historyCount": int(summary.get("sampleCount3Y") or 0),
        "historyStartDate": summary.get("startDate3Y"),
        "historyEndDate": summary.get("endDate3Y"),
        "aReturn5Y": summary.get("aReturn5Y"),
        "pairReturn5Y": summary.get("pairReturn5Y"),
        "returnStartDate": summary.get("returnStartDate"),
        "returnEndDate": summary.get("returnEndDate"),
    }


def _shanghai_trade_date() -> str:
    return datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")


def _sync_snapshot_history(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"success": True, "updatedRows": 0}
    try:
        return {"success": True, "updatedRows": int(premium_db.upsert_premium_rows(rows) or 0)}
    except Exception as error:
        return {"success": False, "updatedRows": 0, "error": str(error)}


def build_ab_snapshot(force_pairs: bool = False) -> dict[str, Any]:
    pair_data = load_dynamic_pairs(force_refresh=force_pairs)
    pairs = pair_data.get("ab", [])
    if not pairs:
        raise RuntimeError("AB 动态名单为空")

    fx_rates = get_fx_rates(["HKD", "USD"])
    normalized = []
    query_codes: List[str] = []
    for item in pairs:
        a_code = str(item.get("aCode") or "").strip()
        b_code = str(item.get("bCode") or "").strip()
        b_market = str(item.get("bMarket") or "").strip().lower()
        currency = str(item.get("currency") or "").strip().upper()
        if len(a_code) != 6 or len(b_code) != 6 or b_market not in {"sh", "sz"} or currency not in {"USD", "HKD"}:
            continue

        a_query = f"{'sh' if a_code.startswith('6') else 'sz'}{a_code}"
        b_query = f"{b_market}{b_code}"
        normalized.append(
            {
                "aCode": a_code,
                "aName": clean_name(item.get("aName") or ""),
                "bCode": b_code,
                "bName": clean_name(item.get("bName") or ""),
                "market": str(item.get("market") or ("SH-B" if b_market == "sh" else "SZ-B")),
                "currency": currency,
                "bMarket": b_market,
                "aQuery": a_query,
                "bQuery": b_query,
            }
        )
        query_codes.extend([a_query, b_query])

    premium_db.init_db()
    quote_map = get_quotes(query_codes)
    trade_date = _shanghai_trade_date()
    rows_base = []
    history_rows = []

    for item in normalized:
        a_data = quote_map.get(item["aQuery"])
        b_data = quote_map.get(item["bQuery"])
        if not a_data or not b_data:
            continue
        a_price = float(a_data["price"])
        b_price = float(b_data["price"])
        if a_price <= 0 or b_price <= 0:
            continue

        fx = float(fx_rates[item["currency"]])
        b_price_cny = b_price * fx
        premium = (b_price_cny / a_price - 1) * 100
        rows_base.append(
            {
                "id": f"ab-{item['aCode']}",
                "aCode": item["aCode"],
                "aName": clean_name(a_data.get("name") or item["aName"]),
                "aPrice": round(a_price, 4),
                "bCode": item["bCode"],
                "bName": clean_name(b_data.get("name") or item["bName"]),
                "bPrice": round(b_price, 4),
                "bPriceCny": round(b_price_cny, 4),
                "market": item["market"],
                "currency": item["currency"],
                "exchangeRate": round(fx, 6),
                "premium": round(premium, 4),
                "premiumRaw": premium,
                "source": "tencent",
            }
        )
        history_rows.append(
            {
                "type": "AB",
                "aCode": item["aCode"],
                "pairCode": item["bCode"],
                "date": trade_date,
                "aPrice": round(a_price, 4),
                "pairPrice": round(b_price, 4),
                "pairPriceCny": round(b_price_cny, 4),
                "exchangeRate": round(fx, 6),
                "premium": round(premium, 4),
                "currency": item["currency"],
                "pairMarket": item["bMarket"],
            }
        )

    history_sync = _sync_snapshot_history(history_rows)
    codes = [item["aCode"] for item in rows_base]
    summary_map = premium_db.load_premium_summaries("AB", codes)
    distribution_map = premium_db.load_premium_distributions("AB", codes, days=365 * 3)
    rows = []
    for item in rows_base:
        summary = _summarize_premium(summary_map.get(item["aCode"], {}), item["premiumRaw"], distribution_map.get(item["aCode"]))
        rows.append({**{k: v for k, v in item.items() if k != "premiumRaw"}, **summary})

    rows.sort(key=lambda row: row["premium"], reverse=True)
    return _build_success(
        rows,
        total=len(rows),
        hkdExchangeRate=round(fx_rates["HKD"], 6),
        usdExchangeRate=round(fx_rates["USD"], 6),
        source="tencent+akshare_pairs+sqlite_history",
        tradeDate=trade_date,
        historySync=history_sync,
    )
