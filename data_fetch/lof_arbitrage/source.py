#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""LOF 套利固定来源抓取。

职责：
1. 读取集思录 LOF / QDII 页面家族对应的真实列表接口；
2. 做最小标准化、样本过滤与辅助字段补全；
3. 在抓取层补充统一的实时指数/汇率辅助输入；
4. 不在这里做业务排序、监控入池或推送判断。
"""

from __future__ import annotations

import math
import re
from csv import DictReader
from datetime import datetime
from io import StringIO
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote

import requests

from shared.config.script_config import get_config
from shared.market_service import get_quotes

_CONFIG = get_config()
_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("lof_arbitrage") or {})
_EXTERNAL_MARKET_CONFIG = dict((_FETCH_CONFIG.get("external_market_api") or {}))

REQUEST_TIMEOUT_MS = max(5000, int(_FETCH_CONFIG.get("request_timeout_ms") or 20000))
FIRECRAWL_TIMEOUT_MS = max(5000, int(_FETCH_CONFIG.get("firecrawl_timeout_ms") or REQUEST_TIMEOUT_MS))
SOURCE_REFERER = str(_FETCH_CONFIG.get("source_referer") or "https://www.jisilu.cn/").strip()
JISILU_COOKIE = str(_FETCH_CONFIG.get("jisilu_cookie") or "").strip()
FIRECRAWL_ENABLED = bool(_FETCH_CONFIG.get("firecrawl_enabled"))
FIRECRAWL_API_URL = str(_FETCH_CONFIG.get("firecrawl_api_url") or "").strip()
FIRECRAWL_API_KEY = str(_FETCH_CONFIG.get("firecrawl_api_key") or "").strip()
DEFAULT_GROUP = str(_FETCH_CONFIG.get("default_group") or "europe_us").strip() or "europe_us"
SOURCE_PAGE_URLS = dict((_FETCH_CONFIG.get("source_page_urls") or {}))
SOURCE_API_URLS = dict((_FETCH_CONFIG.get("source_api_urls") or {}))
EXTERNAL_MARKET_ENABLED = bool(_EXTERNAL_MARKET_CONFIG.get("enabled"))
EXTERNAL_MARKET_PROVIDER = str(_EXTERNAL_MARKET_CONFIG.get("provider") or "").strip().lower()
EXTERNAL_MARKET_TIMEOUT_MS = max(3000, int(_EXTERNAL_MARKET_CONFIG.get("request_timeout_ms") or REQUEST_TIMEOUT_MS))
EXTERNAL_CURRENT_QUOTE_URL = str(_EXTERNAL_MARKET_CONFIG.get("current_quote_url") or "").strip()
EXTERNAL_HISTORY_QUOTE_URL = str(_EXTERNAL_MARKET_CONFIG.get("history_quote_url") or "").strip()
_EXTERNAL_INDEX_SYMBOL_MAP = dict((_EXTERNAL_MARKET_CONFIG.get("index_symbol_map") or {}))
EXTERNAL_INDEX_SYMBOL_MAP_BY_CAL_ID = {
    str(key or "").strip().upper(): str(value or "").strip()
    for key, value in dict((_EXTERNAL_INDEX_SYMBOL_MAP.get("cal_index_id") or {})).items()
    if str(key or "").strip() and str(value or "").strip()
}
EXTERNAL_INDEX_SYMBOL_MAP_BY_NAME = {
    str(key or "").strip(): str(value or "").strip()
    for key, value in dict((_EXTERNAL_INDEX_SYMBOL_MAP.get("index_name") or {})).items()
    if str(key or "").strip() and str(value or "").strip()
}
EXTERNAL_INDEX_SYMBOL_MAP_BY_LIVE_TOKEN = {
    str(key or "").strip().upper(): str(value or "").strip()
    for key, value in dict((_EXTERNAL_INDEX_SYMBOL_MAP.get("live_token") or {})).items()
    if str(key or "").strip() and str(value or "").strip()
}
EXTERNAL_FX_SYMBOL_MAP = {
    str(key or "").strip().upper(): str(value or "").strip()
    for key, value in dict((_EXTERNAL_MARKET_CONFIG.get("fx_symbol_map") or {})).items()
    if str(key or "").strip() and str(value or "").strip()
}

GROUP_META = {
    "index": {
        "label": "指数LOF",
        "pageUrl": str(SOURCE_PAGE_URLS.get("index") or "https://www.jisilu.cn/data/lof/#index").strip(),
        "apiUrl": str(SOURCE_API_URLS.get("index") or "https://www.jisilu.cn/data/lof/index_lof_list/").strip(),
    },
    "europe_us": {
        "label": "QDII欧美",
        "pageUrl": str(SOURCE_PAGE_URLS.get("europe_us") or "https://www.jisilu.cn/data/qdii/#qdiie").strip(),
        "apiUrl": str(SOURCE_API_URLS.get("europe_us") or "https://www.jisilu.cn/data/qdii/qdii_list/E").strip(),
    },
    "commodity": {
        "label": "商品LOF",
        "pageUrl": str(SOURCE_PAGE_URLS.get("commodity") or "https://www.jisilu.cn/data/qdii/#qdiic").strip(),
        "apiUrl": str(SOURCE_API_URLS.get("commodity") or "https://www.jisilu.cn/data/qdii/qdii_list/C").strip(),
    },
    "asia": {
        "label": "QDII亚洲",
        "pageUrl": str(SOURCE_PAGE_URLS.get("asia") or "https://www.jisilu.cn/data/qdii/#qdiia").strip(),
        "apiUrl": str(SOURCE_API_URLS.get("asia") or "https://www.jisilu.cn/data/qdii/qdii_list/A").strip(),
    },
}

SOURCE_GROUP_SPECS = (
    {"fetchKey": "index", "outputGroup": "index"},
    {"fetchKey": "europe_us", "outputGroup": "europe_us"},
    {"fetchKey": "commodity", "outputGroup": "europe_us"},
    {"fetchKey": "asia", "outputGroup": "asia"},
)

FX_QUOTE_MAP = {
    "USD": "whUSDCNY",
    "HKD": "whHKDCNY",
    "EUR": "whEURCNY",
    "GBP": "whGBPCNY",
    "AUD": "whAUDCNY",
    "SGD": "whSGDCNY",
    "CAD": "whCADCNY",
    "CNY": "",
}

INDEX_QUOTE_MAP = {
    "NDX.GI": "usNDX",
    "SPX.GI": "usINX",
    "DJI.GI": "usDJI",
    "IXIC.GI": "usIXIC",
    "HSI.GI": "hkHSI",
    "HSI": "hkHSI",
    "HSTECH.GI": "hkHSTECH",
    "HSTECH": "hkHSTECH",
}


def now_iso() -> str:
    return datetime.now().isoformat()


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def to_float(value: Any) -> Optional[float]:
    text = clean_text(value).replace(",", "").replace("%", "")
    if text in {"", "-", "--", "null", "None"}:
        return None
    try:
        parsed = float(text)
    except Exception:
        return None
    return parsed if math.isfinite(parsed) else None


def infer_market(code: str) -> str:
    text = clean_text(code)
    return "sh" if text.startswith("5") else "sz"


def infer_market_label(code: str) -> str:
    return "沪市" if infer_market(code) == "sh" else "深市"


def is_lof_sample(name: str) -> bool:
    text = clean_text(name)
    if not text or "ETF" in text.upper():
        return False
    return "LOF" in text.upper()


def resolve_output_group_key(fetch_group_key: str) -> str:
    # 商品 LOF 当前不单独做页面标签，真实来源仍保留，但展示统一并入 QDII欧美。
    return "europe_us" if fetch_group_key == "commodity" else fetch_group_key


def to_rate_percent(value: Any) -> Optional[float]:
    return to_float(value)


def parse_fee_percent(value: Any) -> Optional[float]:
    return to_float(value)


def parse_custodian_fee(value: Any, fee_tips: Any) -> Optional[float]:
    direct = to_float(value)
    if direct is not None:
        return direct
    text = clean_text(fee_tips)
    hit = re.search(r"托管费[:：]\s*([0-9.]+)", text)
    return to_float(hit.group(1)) if hit else None


def parse_limit_amount(apply_status: Any, min_amount_text: Any) -> Optional[float]:
    status_text = clean_text(apply_status)
    min_text = clean_text(min_amount_text).replace("\r", "\n")
    if "无限额" in status_text or "无限额" in min_text:
        return None

    def _unit_multiplier(unit_text: str) -> float:
        if unit_text == "亿":
            return 100000000.0
        if unit_text == "万":
            return 10000.0
        if unit_text == "千":
            return 1000.0
        return 1.0

    candidates = [
        status_text,
        min_text,
    ]
    patterns = [
        r"限(?:购)?\s*([0-9]+(?:\.[0-9]+)?)\s*([亿万千]?)",
        r"日累计申购限额[:：]?\s*([0-9]+(?:\.[0-9]+)?)\s*([亿万千]?)",
    ]
    for source_text in candidates:
        for pattern in patterns:
            hit = re.search(pattern, source_text)
            if not hit:
                continue
            amount = to_float(hit.group(1))
            if amount is None:
                continue
            return amount * _unit_multiplier(hit.group(2) or "")
    return None


def is_limited_apply(apply_status: Any, min_amount_text: Any) -> bool:
    status_text = clean_text(apply_status)
    min_text = clean_text(min_amount_text)
    if "无限额" in status_text or "无限额" in min_text:
        return False
    return "限" in status_text or "限额" in min_text


def build_headers(page_url: str) -> Dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": page_url or SOURCE_REFERER,
        "Accept": "application/json,text/plain,*/*",
    }
    if JISILU_COOKIE:
        headers["Cookie"] = JISILU_COOKIE
    return headers


def build_firecrawl_url() -> str:
    text = FIRECRAWL_API_URL.rstrip("/")
    if not text:
        return ""
    if text.endswith("/scrape"):
        return text
    return f"{text}/v1/scrape"


def try_firecrawl_probe(page_url: str) -> Dict[str, Any]:
    """仅做可选页面探测，不把 Firecrawl 变成生产必需路径。"""

    if not (FIRECRAWL_ENABLED and FIRECRAWL_API_KEY and FIRECRAWL_API_URL):
        return {"enabled": False, "attempted": False, "success": False, "reason": "not_configured"}

    try:
        response = requests.post(
            build_firecrawl_url(),
            headers={
                "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"url": page_url, "formats": ["markdown"]},
            timeout=FIRECRAWL_TIMEOUT_MS / 1000.0,
        )
        response.raise_for_status()
        payload = response.json() if response.content else {}
        return {
            "enabled": True,
            "attempted": True,
            "success": True,
            "title": clean_text((payload.get("data") or {}).get("metadata", {}).get("title")),
        }
    except Exception as exc:
        return {
            "enabled": True,
            "attempted": True,
            "success": False,
            "reason": str(exc),
        }


def fetch_source_group(group_key: str) -> Dict[str, Any]:
    meta = GROUP_META[group_key]
    firecrawl_status = try_firecrawl_probe(meta["pageUrl"])
    response = requests.get(
        meta["apiUrl"],
        headers=build_headers(meta["pageUrl"]),
        timeout=REQUEST_TIMEOUT_MS / 1000.0,
    )
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("rows") or payload.get("data") or []
    visible_rows = rows if isinstance(rows, list) else []
    visible_count = len(visible_rows)
    all_count = int(payload.get("all") or 0)
    # 集思录完整可见场景里有时不返回 all，此时回退到真实可见条数，避免页面误显示 0。
    if all_count <= 0:
        all_count = visible_count
    return {
        "groupKey": group_key,
        "groupLabel": meta["label"],
        "pageUrl": meta["pageUrl"],
        "apiUrl": meta["apiUrl"],
        "visibleRows": visible_rows,
        "allCount": all_count,
        "visibleCount": visible_count,
        "warn": clean_text(payload.get("warn")),
        "guestLimited": "游客仅显示前" in clean_text(payload.get("warn")),
        "firecrawl": firecrawl_status,
    }


def resolve_index_quote_code(group_key: str, row: Dict[str, Any]) -> str:
    cal_index_id = clean_text(row.get("calIndexId")).upper()
    if cal_index_id in INDEX_QUOTE_MAP:
        return INDEX_QUOTE_MAP[cal_index_id]
    if group_key == "index":
        index_id = clean_text(row.get("indexId"))
        if re.fullmatch(r"\d{6}", index_id):
            return f"{'sz' if index_id.startswith('399') else 'sh'}{index_id}"
    return ""


def resolve_fx_quote_code(currency: str) -> str:
    return FX_QUOTE_MAP.get(clean_text(currency).upper(), "")


def resolve_external_index_symbol(row: Dict[str, Any]) -> str:
    cal_index_id = clean_text(row.get("calIndexId")).upper()
    if cal_index_id and cal_index_id in EXTERNAL_INDEX_SYMBOL_MAP_BY_CAL_ID:
        return EXTERNAL_INDEX_SYMBOL_MAP_BY_CAL_ID[cal_index_id]
    index_name = clean_text(row.get("indexName"))
    if index_name and index_name in EXTERNAL_INDEX_SYMBOL_MAP_BY_NAME:
        return EXTERNAL_INDEX_SYMBOL_MAP_BY_NAME[index_name]
    live_token = clean_text(row.get("liveIndexToken")).upper()
    if live_token and live_token in EXTERNAL_INDEX_SYMBOL_MAP_BY_LIVE_TOKEN:
        return EXTERNAL_INDEX_SYMBOL_MAP_BY_LIVE_TOKEN[live_token]
    return ""


def resolve_external_fx_symbol(currency: str) -> str:
    return EXTERNAL_FX_SYMBOL_MAP.get(clean_text(currency).upper(), "")


def normalize_trade_date(value: Any) -> str:
    text = clean_text(value)
    return text if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else ""


def parse_stooq_current_price(symbol: str) -> Tuple[Optional[float], str]:
    if not (EXTERNAL_CURRENT_QUOTE_URL and symbol):
        return None, ""
    response = requests.get(
        f"{EXTERNAL_CURRENT_QUOTE_URL}?s={quote(symbol)}&i=d",
        headers={"User-Agent": "Mozilla/5.0", "Referer": SOURCE_REFERER},
        timeout=EXTERNAL_MARKET_TIMEOUT_MS / 1000.0,
    )
    response.raise_for_status()
    line = clean_text(response.text.splitlines()[0] if response.text else "")
    if not line:
        return None, ""
    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 7:
        return None, ""
    trade_date = ""
    if re.fullmatch(r"\d{8}", parts[1]):
        trade_date = f"{parts[1][:4]}-{parts[1][4:6]}-{parts[1][6:8]}"
    return to_float(parts[6]), trade_date


def parse_stooq_history_close(symbol: str, trade_date: str) -> Tuple[Optional[float], str]:
    aligned_date = normalize_trade_date(trade_date)
    if not (EXTERNAL_HISTORY_QUOTE_URL and symbol and aligned_date):
        return None, ""
    compact_date = aligned_date.replace("-", "")
    response = requests.get(
        f"{EXTERNAL_HISTORY_QUOTE_URL}?s={quote(symbol)}&i=d&d1={compact_date}&d2={compact_date}",
        headers={"User-Agent": "Mozilla/5.0", "Referer": SOURCE_REFERER},
        timeout=EXTERNAL_MARKET_TIMEOUT_MS / 1000.0,
    )
    response.raise_for_status()
    text = response.text.replace("\ufeff", "").strip()
    if not text:
        return None, ""
    rows = list(DictReader(StringIO(text)))
    if not rows:
        return None, ""
    row = rows[-1]
    return to_float(row.get("Close")), normalize_trade_date(row.get("Date"))


def fetch_open_er_api_rate(currency: str) -> Optional[float]:
    normalized = clean_text(currency).upper()
    if not normalized or normalized == "CNY":
        return 1.0
    try:
        response = requests.get(
            f"https://open.er-api.com/v6/latest/{normalized}",
            timeout=REQUEST_TIMEOUT_MS / 1000.0,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        response.raise_for_status()
        payload = response.json() if response.content else {}
        if str(payload.get("result") or "").lower() != "success":
            return None
        return to_float((payload.get("rates") or {}).get("CNY"))
    except Exception:
        return None


def parse_cal_tips(tips: Any) -> Dict[str, Any]:
    text = clean_text(tips)
    if not text:
        return {}

    result: Dict[str, Any] = {}
    index_match = re.search(
        r"指数从\s*(\d{4}-\d{2}-\d{2})\s*([0-9.]+)\s*到\s*(\d{4}-\d{2}-\d{2})\s*([0-9.]+)",
        text,
    )
    if index_match:
        result["baseIndexDate"] = index_match.group(1)
        result["baseIndexValue"] = to_float(index_match.group(2))
        result["midIndexDate"] = index_match.group(3)
        result["midIndexValue"] = to_float(index_match.group(4))

    fx_match = re.search(
        r"汇率[^0-9]*从\s*(\d{4}-\d{2}-\d{2})\s*([0-9.]+)\s*到\s*(\d{4}-\d{2}-\d{2})\s*([0-9.]+)",
        text,
    )
    if fx_match:
        result["baseFxDate"] = fx_match.group(1)
        result["baseFxValue"] = to_float(fx_match.group(2))
        result["midFxDate"] = fx_match.group(3)
        result["midFxValue"] = to_float(fx_match.group(4))

    live_match = re.search(r"([A-Z0-9_.-]+)\s+([0-9.]+)\(([+\-]?[0-9.]+)%\)", text)
    if live_match:
        result.setdefault("liveIndexToken", live_match.group(1))
        result.setdefault("liveIndexValueFromTips", to_float(live_match.group(2)))
        result.setdefault("liveIndexIncreaseRateFromTips", to_float(live_match.group(3)))
    return result


def normalize_raw_row(group_key: str, payload_row: Dict[str, Any], page_url: str, api_url: str) -> Optional[Dict[str, Any]]:
    cell = payload_row.get("cell") if isinstance(payload_row, dict) and isinstance(payload_row.get("cell"), dict) else payload_row
    row = dict(cell or {})
    code = clean_text(row.get("fund_id"))
    name = clean_text(row.get("fund_nm"))
    if not code or not is_lof_sample(name):
        return None

    output_group_key = resolve_output_group_key(group_key)
    cal_tips = parse_cal_tips(row.get("cal_tips"))
    currency = clean_text(row.get("money_cd") or "CNY").upper() or "CNY"
    apply_status = clean_text(row.get("apply_status"))
    min_amount_text = clean_text(row.get("min_amt"))
    return {
        "code": code,
        "name": name,
        "market": infer_market(code),
        "marketLabel": infer_market_label(code),
        "marketGroup": output_group_key,
        "groupLabel": GROUP_META[output_group_key]["label"],
        "sourceFetchGroup": group_key,
        "currency": currency,
        "price": to_float(row.get("price")),
        "priceDate": clean_text(row.get("price_dt")),
        "changeRate": to_rate_percent(row.get("increase_rt")),
        "turnoverWan": to_float(row.get("volume")),
        "shareAmountWan": to_float(row.get("amount")),
        "shareAmountIncreaseWan": to_float(row.get("amount_incr")),
        "nav": to_float(row.get("fund_nav")),
        "navDate": clean_text(row.get("nav_dt")),
        "indexIncreaseRate": to_rate_percent(
            row.get("index_increase_rt")
            if group_key == "index"
            else (row.get("ref_increase_rt") or row.get("est_val_increase_rt"))
        ),
        "indexName": clean_text(row.get("index_nm")),
        "indexId": clean_text(row.get("index_id")),
        "calIndexId": clean_text(row.get("cal_index_id")),
        "applyFee": parse_fee_percent(row.get("apply_fee")),
        "applyFeeText": clean_text(row.get("apply_fee")),
        "applyStatus": apply_status,
        "applyStatusText": apply_status,
        "applyLimitAmount": parse_limit_amount(apply_status, min_amount_text),
        "limitedApply": is_limited_apply(apply_status, min_amount_text),
        "redeemFee": parse_fee_percent(row.get("redeem_fee")),
        "redeemFeeText": clean_text(row.get("redeem_fee")),
        "redeemStatus": clean_text(row.get("redeem_status")),
        "custodianFee": parse_custodian_fee(row.get("t_fee"), row.get("mt_fee_tips")),
        "custodianFeeText": clean_text(row.get("t_fee")),
        "sourceIopv": to_float(row.get("iopv")),
        "sourceIopvDate": clean_text(row.get("iopv_dt")),
        "sourceNavDiscountRate": to_rate_percent(row.get("nav_discount_rt")),
        "sourceIopvDiscountRate": to_rate_percent(row.get("iopv_discount_rt")),
        "sourceEstimateValue": to_float(row.get("estimate_value")),
        "sourceEstimateValueText": clean_text(row.get("estimate_value")),
        "sourceEstimateIncreaseRate": to_rate_percent(row.get("est_val_increase_rt")),
        "referenceIndexValue": to_float(row.get("ref_price")),
        "referenceIndexIncreaseRate": to_rate_percent(row.get("ref_increase_rt")),
        "hasIopv": clean_text(row.get("has_iopv")).upper() == "Y",
        "hasUsRef": clean_text(row.get("has_us_ref")).upper() == "Y",
        "t0": clean_text(row.get("t0")).upper() == "Y",
        "baseIndexDate": cal_tips.get("baseIndexDate"),
        "baseIndexValue": cal_tips.get("baseIndexValue"),
        "midIndexDate": cal_tips.get("midIndexDate"),
        "midIndexValue": cal_tips.get("midIndexValue"),
        "baseFxDate": cal_tips.get("baseFxDate"),
        "baseFxValue": cal_tips.get("baseFxValue"),
        "midFxDate": cal_tips.get("midFxDate"),
        "midFxValue": cal_tips.get("midFxValue"),
        "liveIndexToken": cal_tips.get("liveIndexToken"),
        "liveIndexValueFromTips": cal_tips.get("liveIndexValueFromTips"),
        "liveIndexIncreaseRateFromTips": cal_tips.get("liveIndexIncreaseRateFromTips"),
        "calTips": clean_text(row.get("cal_tips")),
        "urls": clean_text(row.get("urls")),
        "sourcePageUrl": page_url,
        "sourceApiUrl": api_url,
        "raw": row,
    }


def build_group_summary(group_snapshots: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    summary_groups: Dict[str, Dict[str, Any]] = {}
    for output_group in ("index", "europe_us", "asia"):
        meta = GROUP_META[output_group]
        summary_groups[output_group] = {
            "label": meta["label"],
            "pageUrl": meta["pageUrl"],
            "apiUrl": meta["apiUrl"],
            "pageUrls": [],
            "apiUrls": [],
            "visibleCount": 0,
            "allCount": 0,
            "guestLimited": False,
            "warn": "",
            "firecrawl": {"enabled": False, "attempted": False, "success": False, "reason": "not_configured"},
        }

    for fetch_group_key, snapshot in group_snapshots.items():
        output_group = resolve_output_group_key(fetch_group_key)
        group_summary = summary_groups[output_group]
        group_summary["visibleCount"] += int(snapshot.get("visibleCount") or 0)
        group_summary["allCount"] += int(snapshot.get("allCount") or 0)
        group_summary["guestLimited"] = bool(group_summary["guestLimited"] or snapshot.get("guestLimited"))

        page_url = clean_text(snapshot.get("pageUrl"))
        api_url = clean_text(snapshot.get("apiUrl"))
        if page_url and page_url not in group_summary["pageUrls"]:
            group_summary["pageUrls"].append(page_url)
        if api_url and api_url not in group_summary["apiUrls"]:
            group_summary["apiUrls"].append(api_url)

        warn_text = clean_text(snapshot.get("warn"))
        if warn_text:
            label = clean_text(snapshot.get("groupLabel")) or fetch_group_key
            existing_warn = clean_text(group_summary.get("warn"))
            next_warn = f"{label}: {warn_text}"
            group_summary["warn"] = f"{existing_warn} | {next_warn}".strip(" |") if existing_warn else next_warn

        firecrawl = snapshot.get("firecrawl") if isinstance(snapshot.get("firecrawl"), dict) else {}
        existing_firecrawl = group_summary["firecrawl"]
        group_summary["firecrawl"] = {
            "enabled": bool(existing_firecrawl.get("enabled") or firecrawl.get("enabled")),
            "attempted": bool(existing_firecrawl.get("attempted") or firecrawl.get("attempted")),
            "success": bool(existing_firecrawl.get("success") or firecrawl.get("success")),
            "reason": clean_text(existing_firecrawl.get("reason") or firecrawl.get("reason")),
        }

    return summary_groups


def hydrate_quotes(rows: List[Dict[str, Any]]) -> Tuple[Dict[str, float], Dict[str, float]]:
    index_codes = sorted({code for code in (resolve_index_quote_code(item["marketGroup"], item) for item in rows) if code})
    fx_codes = sorted({code for code in (resolve_fx_quote_code(item.get("currency")) for item in rows) if code})
    quote_map = get_quotes([*index_codes, *fx_codes], timeout=max(8, int(REQUEST_TIMEOUT_MS / 1000.0)))

    index_values = {
        code: to_float((quote_map.get(code) or {}).get("price"))
        for code in index_codes
    }
    fx_values: Dict[str, Optional[float]] = {}
    for currency in sorted({clean_text(item.get("currency")).upper() or "CNY" for item in rows}):
        if currency == "CNY":
            fx_values[currency] = 1.0
            continue
        quote_code = resolve_fx_quote_code(currency)
        fx_value = to_float((quote_map.get(quote_code) or {}).get("price")) if quote_code else None
        if fx_value is None or fx_value <= 0:
            fx_value = fetch_open_er_api_rate(currency)
        fx_values[currency] = fx_value
    return index_values, fx_values


def hydrate_external_market_data(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    """只为 QDII 欧美样本补缺失的指数/汇率输入。"""

    usage = {
        "externalIndexCurrentFilled": 0,
        "externalIndexBaseFilled": 0,
        "externalFxCurrentFilled": 0,
        "externalFxBaseFilled": 0,
    }
    if not (EXTERNAL_MARKET_ENABLED and EXTERNAL_MARKET_PROVIDER == "stooq"):
        return usage

    current_cache: Dict[str, Tuple[Optional[float], str]] = {}
    history_cache: Dict[Tuple[str, str], Tuple[Optional[float], str]] = {}

    def _get_current(symbol: str) -> Tuple[Optional[float], str]:
        if symbol not in current_cache:
            try:
                current_cache[symbol] = parse_stooq_current_price(symbol)
            except Exception:
                current_cache[symbol] = (None, "")
        return current_cache[symbol]

    def _get_history(symbol: str, trade_date: str) -> Tuple[Optional[float], str]:
        cache_key = (symbol, trade_date)
        if cache_key not in history_cache:
            try:
                history_cache[cache_key] = parse_stooq_history_close(symbol, trade_date)
            except Exception:
                history_cache[cache_key] = (None, "")
        return history_cache[cache_key]

    for row in rows:
        if clean_text(row.get("marketGroup")) != "europe_us":
            continue

        nav_date = normalize_trade_date(row.get("navDate") or row.get("baseIndexDate") or row.get("baseFxDate"))
        external_index_symbol = resolve_external_index_symbol(row)
        external_fx_symbol = resolve_external_fx_symbol(clean_text(row.get("currency")).upper() or "CNY")

        if external_index_symbol:
            row["externalIndexSymbol"] = external_index_symbol
        if external_fx_symbol:
            row["externalFxSymbol"] = external_fx_symbol

        if external_index_symbol and (row.get("currentIndexValue") is None or row.get("baseIndexValue") is None):
            current_value, current_date = _get_current(external_index_symbol)
            if row.get("currentIndexValue") is None and current_value is not None:
                row["currentIndexValue"] = current_value
                row["currentIndexValueDate"] = current_date or row.get("priceDate")
                row["currentIndexValueSource"] = "external_stooq"
                usage["externalIndexCurrentFilled"] += 1
            if row.get("baseIndexValue") is None and nav_date:
                base_value, resolved_date = _get_history(external_index_symbol, nav_date)
                if base_value is not None:
                    row["baseIndexValue"] = base_value
                    row["baseIndexDate"] = resolved_date or nav_date
                    row["baseIndexValueSource"] = "external_stooq"
                    usage["externalIndexBaseFilled"] += 1

        if external_fx_symbol and (row.get("currentFxRate") is None or row.get("baseFxValue") is None):
            current_fx_value, current_fx_date = _get_current(external_fx_symbol)
            if row.get("currentFxRate") is None and current_fx_value is not None:
                row["currentFxRate"] = current_fx_value
                row["currentFxRateDate"] = current_fx_date or row.get("priceDate")
                row["currentFxRateSource"] = "external_stooq"
                usage["externalFxCurrentFilled"] += 1
            if row.get("baseFxValue") is None and nav_date:
                base_fx_value, resolved_fx_date = _get_history(external_fx_symbol, nav_date)
                if base_fx_value is not None:
                    row["baseFxValue"] = base_fx_value
                    row["baseFxDate"] = resolved_fx_date or nav_date
                    row["baseFxValueSource"] = "external_stooq"
                    usage["externalFxBaseFilled"] += 1

    return usage


def get_lof_arbitrage_source_snapshot() -> Dict[str, Any]:
    """抓取 LOF 套利来源并补充统一辅助输入。"""

    group_snapshots: Dict[str, Dict[str, Any]] = {}
    source_rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    for source_group in SOURCE_GROUP_SPECS:
        group_key = source_group["fetchKey"]
        try:
            group_snapshot = fetch_source_group(group_key)
            group_snapshots[group_key] = group_snapshot
            for item in group_snapshot["visibleRows"]:
                normalized = normalize_raw_row(group_key, item, group_snapshot["pageUrl"], group_snapshot["apiUrl"])
                if normalized:
                    source_rows.append(normalized)
        except Exception as exc:
            errors.append(f"{group_key}: {exc}")
            group_snapshots[group_key] = {
                "groupKey": group_key,
                "groupLabel": GROUP_META[group_key]["label"],
                "pageUrl": GROUP_META[group_key]["pageUrl"],
                "apiUrl": GROUP_META[group_key]["apiUrl"],
                "visibleRows": [],
                "visibleCount": 0,
                "allCount": 0,
                "warn": str(exc),
                "guestLimited": False,
                "firecrawl": {"enabled": FIRECRAWL_ENABLED, "attempted": False, "success": False, "reason": "group_failed"},
            }

    if not source_rows and errors:
        return {
            "success": False,
            "error": "; ".join(errors),
            "updateTime": now_iso(),
            "source": "jisilu",
        }

    index_values, fx_values = hydrate_quotes(source_rows)
    for row in source_rows:
        current_index_quote_code = resolve_index_quote_code(row["marketGroup"], row)
        row["currentIndexQuoteCode"] = current_index_quote_code
        row["currentIndexValue"] = index_values.get(current_index_quote_code) or to_float(row.get("liveIndexValueFromTips"))
        if index_values.get(current_index_quote_code) is not None:
            row["currentIndexValueSource"] = "tencent"
        elif to_float(row.get("liveIndexValueFromTips")) is not None:
            row["currentIndexValueSource"] = "source_cal_tips"
        row["currentFxRate"] = fx_values.get(clean_text(row.get("currency")).upper() or "CNY")
        if row["currentFxRate"] is not None:
            row["currentFxRateSource"] = "tencent_or_open_er"

    external_usage = hydrate_external_market_data(source_rows)

    aggregated_groups = build_group_summary(group_snapshots)
    source_summary = {
        "groups": aggregated_groups,
        "cookieConfigured": bool(JISILU_COOKIE),
        "firecrawlConfigured": bool(FIRECRAWL_ENABLED and FIRECRAWL_API_URL and FIRECRAWL_API_KEY),
        "externalMarketConfigured": bool(EXTERNAL_MARKET_ENABLED and EXTERNAL_MARKET_PROVIDER and EXTERNAL_CURRENT_QUOTE_URL and EXTERNAL_HISTORY_QUOTE_URL),
        "externalMarketProvider": EXTERNAL_MARKET_PROVIDER or None,
        "externalUsage": external_usage,
        "totalVisibleRows": len(source_rows),
        "defaultGroup": DEFAULT_GROUP,
    }

    return {
        "success": True,
        "data": source_rows,
        "updateTime": now_iso(),
        "source": "jisilu+tencent+stooq" if EXTERNAL_MARKET_ENABLED and EXTERNAL_MARKET_PROVIDER == "stooq" else "jisilu+tencent",
        "sourceSummary": source_summary,
        "defaultGroup": DEFAULT_GROUP,
    }
