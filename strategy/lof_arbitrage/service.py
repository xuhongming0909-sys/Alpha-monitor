"""LOF 套利策略输出服务。"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from shared.config.script_config import get_config
from shared.models.service_result import build_success

_CONFIG = get_config()
_STRATEGY_CONFIG = (((_CONFIG.get("strategy") or {}).get("lof_arbitrage") or {}))

DEFAULT_GROUP = str(_STRATEGY_CONFIG.get("default_group") or "europe_us").strip() or "europe_us"
LIMITED_APPLY_CAP_AMOUNT = float(_STRATEGY_CONFIG.get("limited_apply_cap_amount") or 100000)
LIMITED_PREMIUM_RATE_THRESHOLD = float(_STRATEGY_CONFIG.get("limited_premium_rate_threshold") or 1.0)
UNLIMITED_ABS_PREMIUM_RATE_THRESHOLD = float(_STRATEGY_CONFIG.get("unlimited_abs_premium_rate_threshold") or 5.0)
MIN_TURNOVER_WAN = float(_STRATEGY_CONFIG.get("min_turnover_wan") or 100.0)

GROUP_LABELS = {
    "index": "指数LOF",
    "europe_us": "QDII欧美",
    "asia": "QDII亚洲",
}


def _to_float(value: Any) -> Optional[float]:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _round(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), digits)


def _calc_premium_rate(iopv: Optional[float], price: Optional[float]) -> Optional[float]:
    if iopv is None or price is None or price <= 0:
        return None
    return (iopv / price - 1.0) * 100.0


def _resolve_time_note(group_key: str) -> str:
    return "T+2" if group_key == "index" else "T+3"


def _is_unlimited_apply(row: Dict[str, Any]) -> bool:
    return not bool(row.get("limitedApply"))


def _calc_iopv(row: Dict[str, Any]) -> Dict[str, Any]:
    """根据不同分组计算 IOPV，并明确返回真实计算状态。"""

    price = _to_float(row.get("price"))
    nav = _to_float(row.get("nav"))
    group_key = str(row.get("marketGroup") or "").strip()
    currency = str(row.get("currency") or "CNY").strip().upper() or "CNY"
    current_fx_rate = _to_float(row.get("currentFxRate")) or (1.0 if currency == "CNY" else None)
    source_iopv = _to_float(row.get("sourceIopv"))
    source_estimate_value = _to_float(row.get("sourceEstimateValue"))
    source_estimate_increase_rate = _to_float(row.get("sourceEstimateIncreaseRate"))
    index_increase_rate = _to_float(row.get("indexIncreaseRate"))

    if source_iopv is not None and source_iopv > 0:
        return {
            "iopv": source_iopv,
            "calcMode": "source_iopv",
            "calcStatus": "源页直接返回 IOPV",
            "premiumRate": _calc_premium_rate(source_iopv, price),
        }

    if group_key in {"index", "asia"}:
        base_fx_rate = _to_float(row.get("baseFxValue"))
        fx_ratio = 1.0
        if currency != "CNY":
            if current_fx_rate and base_fx_rate and base_fx_rate > 0:
                fx_ratio = current_fx_rate / base_fx_rate
            elif current_fx_rate and row.get("navDate") == row.get("raw", {}).get("price_dt"):
                fx_ratio = 1.0
            else:
                fx_ratio = None

        if nav is not None and index_increase_rate is not None and fx_ratio is not None:
            iopv = nav * (1.0 + index_increase_rate / 100.0) * fx_ratio
            return {
                "iopv": iopv,
                "calcMode": "t1_nav_index_fx",
                "calcStatus": "按 T-1 净值与指数涨幅修正",
                "premiumRate": _calc_premium_rate(iopv, price),
            }

    if group_key == "europe_us":
        current_index_value = _to_float(row.get("currentIndexValue"))
        base_index_value = _to_float(row.get("baseIndexValue"))
        base_fx_value = _to_float(row.get("baseFxValue")) or (1.0 if currency == "CNY" else None)
        if (
            nav is not None and nav > 0 and
            current_index_value is not None and current_index_value > 0 and
            base_index_value is not None and base_index_value > 0 and
            current_fx_rate is not None and current_fx_rate > 0 and
            base_fx_value is not None and base_fx_value > 0
        ):
            iopv = nav * (current_index_value / base_index_value) * (current_fx_rate / base_fx_value)
            return {
                "iopv": iopv,
                "calcMode": "t2_live_index_fx",
                "calcStatus": "按 T-2 基准与实时指数/汇率修正",
                "premiumRate": _calc_premium_rate(iopv, price),
            }

    if source_estimate_value is not None and source_estimate_value > 0:
        return {
            "iopv": source_estimate_value,
            "calcMode": "source_estimate_value",
            "calcStatus": "源页直接返回估算净值",
            "premiumRate": _calc_premium_rate(source_estimate_value, price),
        }

    if nav is not None and source_estimate_increase_rate is not None:
        iopv = nav * (1.0 + source_estimate_increase_rate / 100.0)
        return {
            "iopv": iopv,
            "calcMode": "source_estimated_change",
            "calcStatus": "按源页估算涨幅回推",
            "premiumRate": _calc_premium_rate(iopv, price),
        }

    return {
        "iopv": None,
        "calcMode": "missing_inputs",
        "calcStatus": "真实输入不足，未计算 IOPV",
        "premiumRate": None,
    }


def _build_row(row: Dict[str, Any]) -> Dict[str, Any]:
    calc = _calc_iopv(row)
    premium_rate = _to_float(calc.get("premiumRate"))
    turnover_wan = _to_float(row.get("turnoverWan"))
    limited_apply = bool(row.get("limitedApply"))
    apply_limit_amount = _to_float(row.get("applyLimitAmount"))

    limited_monitor_eligible = bool(
        limited_apply and
        apply_limit_amount is not None and
        apply_limit_amount < LIMITED_APPLY_CAP_AMOUNT and
        turnover_wan is not None and turnover_wan > MIN_TURNOVER_WAN and
        premium_rate is not None and premium_rate > LIMITED_PREMIUM_RATE_THRESHOLD
    )
    unlimited_monitor_eligible = bool(
        _is_unlimited_apply(row) and
        turnover_wan is not None and turnover_wan > MIN_TURNOVER_WAN and
        premium_rate is not None and abs(premium_rate) > UNLIMITED_ABS_PREMIUM_RATE_THRESHOLD
    )

    return {
        **dict(row),
        "groupLabel": GROUP_LABELS.get(str(row.get("marketGroup") or "").strip(), str(row.get("marketGroup") or "--")),
        "iopv": _round(_to_float(calc.get("iopv")), 4),
        "premiumRate": _round(premium_rate, 4),
        "calcMode": calc.get("calcMode"),
        "calcStatus": calc.get("calcStatus"),
        "timeNote": _resolve_time_note(str(row.get("marketGroup") or "").strip()),
        "limitedMonitorEligible": limited_monitor_eligible,
        "unlimitedMonitorEligible": unlimited_monitor_eligible,
        "turnoverWan": _round(turnover_wan, 4),
        "shareAmountWan": _round(_to_float(row.get("shareAmountWan")), 4),
        "shareAmountIncreaseWan": _round(_to_float(row.get("shareAmountIncreaseWan")), 4),
        "nav": _round(_to_float(row.get("nav")), 4),
        "price": _round(_to_float(row.get("price")), 4),
        "changeRate": _round(_to_float(row.get("changeRate")), 4),
        "indexIncreaseRate": _round(_to_float(row.get("indexIncreaseRate")), 4),
        "applyFee": _round(_to_float(row.get("applyFee")), 4),
        "redeemFee": _round(_to_float(row.get("redeemFee")), 4),
        "custodianFee": _round(_to_float(row.get("custodianFee")), 4),
        "applyLimitAmount": _round(apply_limit_amount, 4),
    }


def _sort_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        rows,
        key=lambda item: (
            {"europe_us": 0, "asia": 1, "index": 2}.get(str(item.get("marketGroup") or ""), 9),
            999999.0 if item.get("premiumRate") is None else -abs(float(item.get("premiumRate"))),
            str(item.get("code") or ""),
        ),
    )


def build_lof_arbitrage_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """把抓取快照转换成页面/API 直接可消费的数据。"""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    rows = [
        _build_row(dict(record.get("raw") or {}))
        for record in bus_records
        if record.get("status") == "ok"
    ]
    rows = _sort_rows(rows)
    limited_rows = sorted(
        [item for item in rows if item.get("limitedMonitorEligible")],
        key=lambda item: (999999.0 if item.get("premiumRate") is None else -float(item.get("premiumRate"))),
    )
    unlimited_rows = sorted(
        [item for item in rows if item.get("unlimitedMonitorEligible")],
        key=lambda item: (999999.0 if item.get("premiumRate") is None else -abs(float(item.get("premiumRate")))),
    )

    source_summary = dict(fetch_payload.get("sourceSummary") or {})
    source_summary.setdefault("totalRows", len(rows))
    source_summary["computedRows"] = sum(1 for item in rows if item.get("iopv") is not None)
    source_summary["limitedMonitorCount"] = len(limited_rows)
    source_summary["unlimitedMonitorCount"] = len(unlimited_rows)

    return build_success(
        {
            "groups": [
                {"key": "index", "label": "指数LOF"},
                {"key": "europe_us", "label": "QDII欧美"},
                {"key": "asia", "label": "QDII亚洲"},
            ],
            "defaultGroup": fetch_payload.get("defaultGroup") or DEFAULT_GROUP,
            "rows": rows,
            "limitedMonitorRows": limited_rows,
            "unlimitedMonitorRows": unlimited_rows,
            "sourceSummary": source_summary,
            "rebuildStatus": {
                "success": True,
                "lastRebuildAt": fetch_payload.get("updateTime"),
                "lastRebuildError": None,
            },
        },
        updateTime=fetch_payload.get("updateTime"),
        source=fetch_payload.get("source"),
    )
