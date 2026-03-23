"""Build outward-facing LOF arbitrage responses from normalized records."""

from __future__ import annotations

import re
from typing import Any

from shared.config.script_config import get_config
from shared.models.service_result import build_success


LOF_CATEGORY_KEYS = ("europe_us", "asia", "commodity")


def _strategy_config() -> dict[str, Any]:
    config = get_config().get("strategy", {}).get("lof_arbitrage", {})
    return config if isinstance(config, dict) else {}


def _empty_groups() -> dict[str, list[dict]]:
    return {key: [] for key in LOF_CATEGORY_KEYS}


def _to_float(value: Any) -> float | None:
    try:
        parsed = float(value)
        return parsed
    except Exception:
        return None


def _clean_text(value: Any) -> str:
    text = str(value or "").strip()
    return "" if text in {"-", "--", "None", "null"} else text


def _pick_signal_basis(row: dict[str, Any]) -> tuple[str, float | None, str]:
    if row.get("iopvPremiumRate") is not None:
        return "iopv", _to_float(row.get("iopvPremiumRate")), "high"
    if row.get("estimatedPremiumRate") is not None:
        return "estimate", _to_float(row.get("estimatedPremiumRate")), "medium"
    return "nav", _to_float(row.get("navPremiumRate")), "low"


def _parse_apply_status(status_text: str) -> dict[str, Any]:
    text = _clean_text(status_text)
    lowered = text.lower()
    is_open = bool(text) and ("开放" in text or "限" in text)
    is_limited = "限" in text
    is_paused = "暂停" in text or "关闭" in text or "不可" in text or "停止" in text
    limit_match = re.search(r"限\s*([0-9]+(?:\.[0-9]+)?)\s*([千万元亿万]?)", text)
    limit_value = None
    if limit_match:
        limit_value = limit_match.group(1) + (limit_match.group(2) or "")
    return {
        "raw": text,
        "isOpen": is_open and not is_paused,
        "isLimited": is_limited,
        "isPaused": is_paused or ("pause" in lowered),
        "limitText": limit_value or text,
    }


def _build_risk_flags(row: dict[str, Any], apply_meta: dict[str, Any], confidence: str, low_liquidity_volume_wan: float | None) -> list[str]:
    flags = []
    if confidence == "low":
        flags.append("仅有净值溢价，缺少零登录 IOPV/盘中估值")
    if apply_meta.get("isLimited"):
        flags.append(f"申购受限：{apply_meta.get('raw') or '限购'}")
    if apply_meta.get("isPaused"):
        flags.append("当前暂停申购")
    volume = _to_float(row.get("volumeWan"))
    if low_liquidity_volume_wan is not None and volume is not None and volume < low_liquidity_volume_wan:
        flags.append("场内成交额偏低，卖出冲击需谨慎")
    if _clean_text(row.get("notes")):
        flags.append(row["notes"])
    return flags


def _enrich_row(row: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    premium_threshold_pct = float(config.get("premium_threshold_pct", 1.5))
    min_net_premium_pct = float(config.get("min_net_premium_pct", 0.5))
    nav_only_allows_candidate = bool(config.get("nav_only_allows_candidate", False))
    treat_limited_apply_as_watch_only = bool(config.get("treat_limited_apply_as_watch_only", True))
    low_liquidity_volume_wan = _to_float(config.get("low_liquidity_volume_wan"))

    signal_basis, premium_rate, confidence = _pick_signal_basis(row)
    apply_meta = _parse_apply_status(row.get("applyStatus"))
    cost_rate = sum(
        value for value in (
            _to_float(row.get("applyFeeRate")),
            _to_float(row.get("tradeFeeRate")),
        )
        if value is not None
    )
    net_premium_rate = premium_rate - cost_rate if premium_rate is not None else None

    # 这里把“抓到的溢价”与“能否真正执行”拆开，避免把净值观察信号误报成可套利结论。
    if apply_meta.get("isPaused"):
        action_status = "不可参与"
        action_rank = 0
    elif premium_rate is None or premium_rate <= 0:
        action_status = "无明显溢价"
        action_rank = 1
    elif signal_basis == "nav" and not nav_only_allows_candidate:
        action_status = "仅观察"
        action_rank = 2
    elif treat_limited_apply_as_watch_only and apply_meta.get("isLimited"):
        action_status = "仅观察"
        action_rank = 2
    elif net_premium_rate is not None and premium_rate >= premium_threshold_pct and net_premium_rate >= min_net_premium_pct and apply_meta.get("isOpen"):
        action_status = "套利候选"
        action_rank = 3
    else:
        action_status = "仅观察"
        action_rank = 2

    return {
        **row,
        "premiumBasis": signal_basis,
        "premiumRate": premium_rate,
        "confidence": confidence,
        "estimatedCostRate": cost_rate,
        "netPremiumRate": net_premium_rate,
        "applyMeta": apply_meta,
        "applyOpen": apply_meta.get("isOpen"),
        "actionStatus": action_status,
        "actionRank": action_rank,
        "riskFlags": _build_risk_flags(row, apply_meta, confidence, low_liquidity_volume_wan),
    }


def _build_overview(rows: list[dict], groups: dict[str, list[dict]]) -> dict[str, Any]:
    actionable = [row for row in rows if row.get("actionStatus") == "套利候选"]
    watch_rows = [row for row in rows if row.get("actionStatus") == "仅观察"]
    return {
        "totalCount": len(rows),
        "candidateCount": len(actionable),
        "watchCount": len(watch_rows),
        "applyOpenCount": sum(1 for row in rows if row.get("applyOpen")),
        "iopvAvailableCount": sum(1 for row in rows if row.get("iopv") is not None),
        "estimateAvailableCount": sum(1 for row in rows if row.get("estimatedValue") is not None),
        "navOnlyCount": sum(1 for row in rows if row.get("premiumBasis") == "nav"),
        "europeUsCount": len(groups.get("europe_us") or []),
        "asiaCount": len(groups.get("asia") or []),
        "commodityCount": len(groups.get("commodity") or []),
    }


def build_lof_arbitrage_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """Convert normalized bus records into the outward-facing LOF arbitrage contract."""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    config = _strategy_config()
    groups = _empty_groups()
    rows = []

    for record in bus_records:
        if record.get("status") != "ok":
            continue
        row = _enrich_row(dict(record.get("raw") or {}), config)
        category = str(row.get("category") or "").strip()
        if category in groups:
            groups[category].append(row)
        rows.append(row)

    rows.sort(
        key=lambda item: (
            -(item.get("actionRank") or 0),
            -(_to_float(item.get("premiumRate")) or -9999),
            -(_to_float(item.get("volumeWan")) or -9999),
            str(item.get("symbol") or ""),
        )
    )

    payload = {
        "overview": _build_overview(rows, groups),
        "rows": rows,
        "groups": groups,
        "sourceStatus": (fetch_payload.get("data") or {}).get("sourceStatus", {}),
        "updateTime": fetch_payload.get("updateTime"),
        "cacheTime": fetch_payload.get("cacheTime"),
        "servedFromCache": bool(fetch_payload.get("servedFromCache")),
        "iopvSearch": {
            "publicSourceStatus": "searching",
            "currentZeroLoginAvailability": "partial_schema_but_not_publicly_filled",
        },
    }
    return build_success(
        payload,
        updateTime=fetch_payload.get("updateTime"),
        source=fetch_payload.get("source"),
        cacheTime=fetch_payload.get("cacheTime"),
        servedFromCache=bool(fetch_payload.get("servedFromCache")),
    )
