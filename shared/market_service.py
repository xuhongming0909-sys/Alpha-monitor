"""市场基础服务。

这里集中放置跨插件复用的行情、exchange_rate、搜索与配对辅助能力。
该模块只负责提供基础市场数据能力，不承载业务策略判断。
"""

from __future__ import annotations

import re
import urllib.parse
from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List

import requests

from shared.paths.tool_paths import ensure_scripts_on_path
from shared.models.service_result import build_error as shared_build_error, build_success as shared_build_success
from shared.time.shanghai_time import now_iso

ensure_scripts_on_path()

from market_pairs import load_dynamic_pairs
import premium_history_db as premium_db


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://gu.qq.com/",
}

FX_QUERY_MAP = {
    "HKD": "whHKDCNY",
    "USD": "whUSDCNY",
}

SHANGHAI_TZ = timezone(timedelta(hours=8))


def build_success(data: Any, **extra: Any) -> dict[str, Any]:
    """统一市场服务的成功返回结构。"""

    payload = shared_build_success(data, **extra)
    payload.pop("error", None)
    return payload


def build_error(message: Any, data: Any = None, **extra: Any) -> dict[str, Any]:
    """统一市场服务的失败返回结构。"""

    return shared_build_error(message, [] if data is None else data, **extra)


def clean_name(value: str) -> str:
    return re.sub(r"[\u0000-\u001f\u007f]+", "", str(value or "").strip())


def normalize_company_name(value: str) -> str:
    text = clean_name(value)
    text = text.replace("Ａ", "A").replace("Ｂ", "B")
    text = re.sub(r"[\s\u3000]", "", text)
    text = re.sub(r"[()（）\-·•]", "", text)
    for token in ("股份有限公司", "有限责任公司", "有限公司", "股份", "集团", "控股", "A股", "B股", "H股"):
        text = text.replace(token, "")
    return text.upper().strip()


def is_pair_name_consistent(a_name: str, pair_name: str) -> bool:
    a_norm = normalize_company_name(a_name)
    p_norm = normalize_company_name(pair_name)
    if not a_norm or not p_norm:
        return True
    if a_norm == p_norm or a_norm in p_norm or p_norm in a_norm:
        return True
    return SequenceMatcher(None, a_norm, p_norm).ratio() >= 0.62


def create_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update(REQUEST_HEADERS)
    return session


def get_quotes(codes: Iterable[str], timeout: int = 15) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    normalized_codes = [str(code or "").strip() for code in codes if str(code or "").strip()]
    if not normalized_codes:
        return result

    with create_session() as session:
        for index in range(0, len(normalized_codes), 100):
            batch = normalized_codes[index:index + 100]
            try:
                response = session.get(f"https://qt.gtimg.cn/q={','.join(batch)}", timeout=timeout)
                text = response.content.decode("gbk", errors="ignore")
            except Exception:
                continue

            for line in text.splitlines():
                match = re.match(r'v_([^=]+)="(.*)";?', line.strip())
                if not match:
                    continue
                code = match.group(1)
                parts = match.group(2).split("~")
                if len(parts) < 4:
                    continue
                try:
                    price = float(parts[3]) if parts[3] else 0.0
                except Exception:
                    price = 0.0
                if price <= 0:
                    continue
                result[code] = {
                    "name": clean_name(parts[1] if len(parts) > 1 else ""),
                    "price": price,
                }

    return result


def get_fx_rates(currencies: Iterable[str]) -> Dict[str, float]:
    requested = []
    for currency in currencies:
        normalized = str(currency or "").upper()
        if normalized in FX_QUERY_MAP and normalized not in requested:
            requested.append(normalized)

    quotes = get_quotes([FX_QUERY_MAP[currency] for currency in requested], timeout=12)
    rates: Dict[str, float] = {}
    for currency in requested:
        value = quotes.get(FX_QUERY_MAP[currency], {}).get("price")
        if not isinstance(value, (int, float)) or value <= 0:
            raise RuntimeError(f"exchange_rate接口缺少 {currency}")
        rates[currency] = float(value)
    return rates


def safe_text(response: requests.Response, encoding: str = "utf-8") -> str:
    try:
        return response.content.decode(encoding, errors="ignore")
    except Exception:
        return response.text or ""


def safe_get(url: str, params=None, headers=None, timeout: int = 10):
    merged_headers = dict(REQUEST_HEADERS)
    if headers:
        merged_headers.update(headers)
    return requests.get(url, params=params, headers=merged_headers, timeout=timeout)


def get_exchange_rates() -> dict[str, Any]:
    ts = now_iso()
    try:
        rates = get_fx_rates(["HKD", "USD"])
    except Exception as error:
        return build_error(f"腾讯exchange_rate获取失败: {error}")

    return build_success(
        {
            "hkdToCny": float(rates["HKD"]),
            "usdToCny": float(rates["USD"]),
            "updateTime": ts,
            "source": "tencent",
        },
        updateTime=ts,
    )


def get_single_price(code: str, market: str, b_market: str = "sh") -> dict[str, Any]:
    market = str(market or "a").lower()
    code = str(code or "").strip()
    if not code:
        return build_error("code 不能为空")

    if market == "h":
        q_code = code if code.startswith("hk") else f"hk{code.zfill(5)}"
        currency = "HKD"
        market_label = "H"
    elif market == "b":
        q_code = f"{'sz' if b_market.lower() == 'sz' else 'sh'}{code}"
        currency = "HKD" if b_market.lower() == "sz" else "USD"
        market_label = "B"
    else:
        q_code = f"{'sh' if code.startswith('6') else 'sz'}{code}"
        currency = "CNY"
        market_label = "A"

    row = get_quotes([q_code]).get(q_code)
    if not row:
        return build_error("未获取到实时行情")

    ts = now_iso()
    return build_success(
        {
            "code": code,
            "name": row["name"],
            "price": row["price"],
            "market": market_label,
            "currency": currency,
            "updateTime": ts,
            "source": "tencent",
        },
        updateTime=ts,
    )


def decode_unicode_text(text: str | None) -> str:
    if text is None:
        return ""
    if "\\u" not in text and "\\x" not in text:
        return text
    try:
        return text.encode("utf-8").decode("unicode_escape")
    except Exception:
        return text


def parse_market_from_code(full_code: str):
    full_code = str(full_code or "").strip().lower()
    if len(full_code) < 3:
        return None, None, None, None
    if full_code.startswith("hk"):
        return "hk", full_code[2:], "H", "HKD"
    if full_code.startswith("sh"):
        code = full_code[2:]
        return "sh", code, ("B" if code.startswith("900") else "A"), ("USD" if code.startswith("900") else "CNY")
    if full_code.startswith("sz"):
        code = full_code[2:]
        return "sz", code, ("B" if code.startswith("200") else "A"), ("HKD" if code.startswith("200") else "CNY")
    return None, None, None, None


def normalize_search_item(item: dict[str, Any]):
    market, code, market_type, currency = parse_market_from_code(str(item.get("code") or "").strip())
    if not market or not code:
        return None
    return {
        "code": code,
        "name": str(item.get("name") or "").strip(),
        "pinyin": str(item.get("suggest") or "").strip().lower(),
        "market": market,
        "marketType": market_type,
        "currency": currency,
        "securityType": str(item.get("type") or ""),
    }


def search_stock_proxy(keyword: str) -> list[dict[str, Any]]:
    payload = safe_get(
        "https://proxy.finance.qq.com/cgi/cgi-bin/smartbox/search",
        params={"stockFlag": 1, "fundFlag": 1, "app": "official_website", "query": keyword},
        timeout=8,
    ).json()
    return [row for row in (normalize_search_item(item) for item in payload.get("stock") or []) if row]


def search_stock_s3(keyword: str) -> list[dict[str, Any]]:
    content = safe_text(safe_get(f"https://smartbox.gtimg.cn/s3/?q={urllib.parse.quote(keyword)}&t=all", timeout=8))
    match = re.search(r'v_hint="([^"]*)"', content)
    if not match:
        return []

    rows = []
    for chunk in decode_unicode_text(match.group(1)).split("^"):
        parts = chunk.split("~")
        if len(parts) < 5:
            continue
        market = str(parts[0]).lower()
        code = str(parts[1]).strip()
        if market not in {"sh", "sz", "hk"}:
            continue
        rows.append(
            {
                "code": code,
                "name": str(parts[2]).strip(),
                "pinyin": str(parts[3]).strip().lower(),
                "market": market,
                "marketType": "H" if market == "hk" else ("B" if (market == "sh" and code.startswith("900")) or (market == "sz" and code.startswith("200")) else "A"),
                "currency": "HKD" if market == "hk" or (market == "sz" and code.startswith("200")) else ("USD" if market == "sh" and code.startswith("900") else "CNY"),
                "securityType": str(parts[4]).strip(),
            }
        )
    return rows


def search_stock(keyword: str, limit: int = 20) -> dict[str, Any]:
    keyword = str(keyword or "").strip()
    ts = now_iso()
    if not keyword:
        return build_success([], updateTime=ts)

    source = "tencent_proxy"
    try:
        rows = search_stock_proxy(keyword)
    except Exception:
        rows = []
        source = "tencent_s3_fallback"
    if not rows:
        try:
            rows = search_stock_s3(keyword)
            if rows:
                source = "tencent_s3"
        except Exception:
            rows = []
            source = "tencent_empty"

    uniq = []
    seen = set()
    for item in rows:
        key = (item["market"], item["code"])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(item)
        if len(uniq) >= int(limit):
            break

    result = build_success(uniq, updateTime=ts)
    result["source"] = source
    return result


def calc_empirical_percentile(current: float, premiums: list[float] | None) -> float | None:
    if not premiums:
        return None
    values = sorted(float(value) for value in premiums if value is not None)
    if len(values) < 2:
        return None
    position = bisect_right(values, float(current))
    return max(0.0, min(100.0, (position / len(values)) * 100))


def summarize_premium(summary: dict[str, Any], premium: float, premium_samples: list[float] | None = None) -> dict[str, Any]:
    min_premium = summary.get("minPremium3Y")
    max_premium = summary.get("maxPremium3Y")
    percentile = calc_empirical_percentile(premium, premium_samples)
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


def shanghai_trade_date() -> str:
    return datetime.now(SHANGHAI_TZ).strftime("%Y-%m-%d")


def sync_snapshot_history(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"success": True, "updatedRows": 0}
    try:
        return {"success": True, "updatedRows": int(premium_db.upsert_premium_rows(rows) or 0)}
    except Exception as error:
        return {"success": False, "updatedRows": 0, "error": str(error)}


def build_ah_snapshot(force_pairs: bool = False) -> dict[str, Any]:
    pair_data = load_dynamic_pairs(force_refresh=force_pairs)
    pairs = pair_data.get("ah", [])
    if not pairs:
        raise RuntimeError("AH 动态名单为空")

    exchange_rate = get_fx_rates(["HKD"])["HKD"]
    normalized = []
    query_codes: List[str] = []
    for item in pairs:
        a_code = str(item.get("aCode") or "").strip()
        h_code = str(item.get("hCode") or "").strip().zfill(5)
        if len(a_code) != 6 or len(h_code) != 5:
            continue
        a_query = f"{'sh' if a_code.startswith('6') else 'sz'}{a_code}"
        h_query = f"hk{h_code}"
        normalized.append(
            {
                "aCode": a_code,
                "aName": clean_name(item.get("aName") or ""),
                "hCode": h_code,
                "hName": clean_name(item.get("hName") or ""),
                "aQuery": a_query,
                "hQuery": h_query,
            }
        )
        query_codes.extend([a_query, h_query])

    premium_db.init_db()
    quote_map = get_quotes(query_codes)
    trade_date = shanghai_trade_date()
    rows_base = []
    history_rows = []

    for item in normalized:
        a_data = quote_map.get(item["aQuery"])
        h_data = quote_map.get(item["hQuery"])
        if not a_data or not h_data:
            continue
        a_name = clean_name(a_data.get("name") or item["aName"])
        h_name = clean_name(h_data.get("name") or item["hName"])
        if not is_pair_name_consistent(a_name, h_name):
            continue
        a_price = float(a_data["price"])
        h_price = float(h_data["price"])
        if a_price <= 0 or h_price <= 0:
            continue

        h_price_cny = h_price * exchange_rate
        premium = (h_price_cny / a_price - 1) * 100
        rows_base.append(
            {
                "id": f"ah-{item['aCode']}",
                "aCode": item["aCode"],
                "aName": a_name,
                "aPrice": round(a_price, 4),
                "hCode": item["hCode"],
                "hName": h_name,
                "hPrice": round(h_price, 4),
                "hPriceCny": round(h_price_cny, 4),
                "exchangeRate": round(exchange_rate, 6),
                "premium": round(premium, 4),
                "premiumRaw": premium,
                "source": "tencent",
            }
        )
        history_rows.append(
            {
                "type": "AH",
                "aCode": item["aCode"],
                "pairCode": item["hCode"],
                "date": trade_date,
                "aPrice": round(a_price, 4),
                "pairPrice": round(h_price, 4),
                "pairPriceCny": round(h_price_cny, 4),
                "exchangeRate": round(exchange_rate, 6),
                "premium": round(premium, 4),
                "currency": "HKD",
                "pairMarket": "hk",
            }
        )

    history_sync = sync_snapshot_history(history_rows)
    codes = [item["aCode"] for item in rows_base]
    summary_map = premium_db.load_premium_summaries("AH", codes)
    distribution_map = premium_db.load_premium_distributions("AH", codes, days=365 * 3)
    rows = []
    for item in rows_base:
        summary = summarize_premium(summary_map.get(item["aCode"], {}), item["premiumRaw"], distribution_map.get(item["aCode"]))
        rows.append({**{k: v for k, v in item.items() if k != "premiumRaw"}, **summary})

    rows.sort(key=lambda row: row["premium"], reverse=True)
    return build_success(
        rows,
        total=len(rows),
        exchangeRate=round(exchange_rate, 6),
        source="tencent+akshare_pairs+sqlite_history",
        tradeDate=trade_date,
        historySync=history_sync,
    )


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
    trade_date = shanghai_trade_date()
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

    history_sync = sync_snapshot_history(history_rows)
    codes = [item["aCode"] for item in rows_base]
    summary_map = premium_db.load_premium_summaries("AB", codes)
    distribution_map = premium_db.load_premium_distributions("AB", codes, days=365 * 3)
    rows = []
    for item in rows_base:
        summary = summarize_premium(summary_map.get(item["aCode"], {}), item["premiumRaw"], distribution_map.get(item["aCode"]))
        rows.append({**{k: v for k, v in item.items() if k != "premiumRaw"}, **summary})

    rows.sort(key=lambda row: row["premium"], reverse=True)
    return build_success(
        rows,
        total=len(rows),
        hkdExchangeRate=round(fx_rates["HKD"], 6),
        usdExchangeRate=round(fx_rates["USD"], 6),
        source="tencent+akshare_pairs+sqlite_history",
        tradeDate=trade_date,
        historySync=history_sync,
    )


