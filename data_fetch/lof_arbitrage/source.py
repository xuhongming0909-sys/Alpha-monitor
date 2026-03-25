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
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

from shared.config.script_config import get_config
from shared.market_service import get_quotes

_CONFIG = get_config()
_FETCH_CONFIG = (((_CONFIG.get("data_fetch") or {}).get("plugins") or {}).get("lof_arbitrage") or {})

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
    "asia": {
        "label": "QDII亚洲",
        "pageUrl": str(SOURCE_PAGE_URLS.get("asia") or "https://www.jisilu.cn/data/qdii/#qdiia").strip(),
        "apiUrl": str(SOURCE_API_URLS.get("asia") or "https://www.jisilu.cn/data/qdii/qdii_list/A").strip(),
    },
}

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

    cal_tips = parse_cal_tips(row.get("cal_tips"))
    currency = clean_text(row.get("money_cd") or "CNY").upper() or "CNY"
    apply_status = clean_text(row.get("apply_status"))
    min_amount_text = clean_text(row.get("min_amt"))
    return {
        "code": code,
        "name": name,
        "market": infer_market(code),
        "marketLabel": infer_market_label(code),
        "marketGroup": group_key,
        "groupLabel": GROUP_META[group_key]["label"],
        "currency": currency,
        "price": to_float(row.get("price")),
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


def hydrate_quotes(rows: List[Dict[str, Any]]) -> Tuple[Dict[str, float], Dict[str, float]]:
    index_codes = sorted({code for code in (resolve_index_quote_code(item["marketGroup"], item) for item in rows) if code})
    fx_codes = sorted({code for code in (resolve_fx_quote_code(item.get("currency")) for item in rows) if code})
    quote_map = get_quotes([*index_codes, *fx_codes], timeout=max(8, int(REQUEST_TIMEOUT_MS / 1000.0)))

    index_values = {
        code: to_float((quote_map.get(code) or {}).get("price"))
        for code in index_codes
    }
    fx_values = {
        currency: (1.0 if currency == "CNY" else to_float((quote_map.get(resolve_fx_quote_code(currency)) or {}).get("price")))
        for currency in sorted({clean_text(item.get("currency")).upper() or "CNY" for item in rows})
    }
    return index_values, fx_values


def get_lof_arbitrage_source_snapshot() -> Dict[str, Any]:
    """抓取 LOF 套利来源并补充统一辅助输入。"""

    group_snapshots: Dict[str, Dict[str, Any]] = {}
    source_rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    for group_key in ("index", "europe_us", "asia"):
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
        row["currentIndexValue"] = index_values.get(current_index_quote_code)
        row["currentFxRate"] = fx_values.get(clean_text(row.get("currency")).upper() or "CNY")

    source_summary = {
        "groups": {
            key: {
                "label": value["groupLabel"],
                "pageUrl": value["pageUrl"],
                "apiUrl": value["apiUrl"],
                "visibleCount": value["visibleCount"],
                "allCount": value["allCount"],
                "guestLimited": value["guestLimited"],
                "warn": value["warn"],
                "firecrawl": value["firecrawl"],
            }
            for key, value in group_snapshots.items()
        },
        "cookieConfigured": bool(JISILU_COOKIE),
        "firecrawlConfigured": bool(FIRECRAWL_ENABLED and FIRECRAWL_API_URL and FIRECRAWL_API_KEY),
        "totalVisibleRows": len(source_rows),
        "defaultGroup": DEFAULT_GROUP,
    }

    return {
        "success": True,
        "data": source_rows,
        "updateTime": now_iso(),
        "source": "jisilu+tencent",
        "sourceSummary": source_summary,
        "defaultGroup": DEFAULT_GROUP,
    }
