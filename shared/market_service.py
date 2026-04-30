# AI-SUMMARY: 跨市场工具：价格查询、配对匹配、股票搜索
# 对应 INDEX.md §9 文件摘要索引

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

from shared.models.service_result import build_error as shared_build_error, build_success as shared_build_success
from shared.time.shanghai_time import now_iso


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


