"""可转债抢权配售策略输出服务。"""

from __future__ import annotations

import math
from typing import Any, Dict, Optional

from shared.config.script_config import get_config
from shared.models.service_result import build_success

_CONFIG = get_config()
_STRATEGY_CONFIG = (((_CONFIG.get("strategy") or {}).get("cb_rights_issue") or {}))

MIN_EXPECTED_RETURN_RATE = float(_STRATEGY_CONFIG.get("min_expected_return_rate") or 8.0)
TARGET_BOND_LOTS = max(1, int(_STRATEGY_CONFIG.get("target_bond_lots") or 10))
LOT_SIZE_SHARES = max(1, int(_STRATEGY_CONFIG.get("lot_size_shares") or 100))
SHANGHAI_RATIO_FACTOR = float(_STRATEGY_CONFIG.get("shanghai_ratio_factor") or 0.5)
SHANGHAI_CORRECTION_FACTOR = float(_STRATEGY_CONFIG.get("shanghai_correction_factor") or 0.6)
OPTION_TERM_YEARS = float(_STRATEGY_CONFIG.get("option_term_years") or 6.0)
ELIGIBLE_PROGRESS_KEYWORDS = [str(item or "").strip() for item in (_STRATEGY_CONFIG.get("eligible_progress_keywords") or []) if str(item or "").strip()]


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


def _is_stage_eligible(row: Dict[str, Any]) -> bool:
    progress_name = str(row.get("progressName") or "").strip()
    if any(keyword and keyword in progress_name for keyword in ELIGIBLE_PROGRESS_KEYWORDS):
        return True
    return bool(str(row.get("applyDate") or "").strip())


def _resolve_required_shares(row: Dict[str, Any]) -> Dict[str, Any]:
    raw_required = _to_float(row.get("rawRequiredShares"))
    if raw_required is None or raw_required <= 0:
        return {
            "requiredSharesRaw": None,
            "requiredSharesAdjusted": None,
            "requiredSharesFinal": None,
            "marketRule": "missing_raw_required_shares",
        }

    market = str(row.get("market") or "").strip().lower()
    if market == "sh":
        adjusted = raw_required * SHANGHAI_RATIO_FACTOR * SHANGHAI_CORRECTION_FACTOR
        market_rule = "shanghai_raw_x_0.5_x_0.6_then_round_100"
    else:
        adjusted = raw_required
        market_rule = "shenzhen_raw_then_round_100"

    final_required = int(math.ceil(adjusted / LOT_SIZE_SHARES) * LOT_SIZE_SHARES)
    return {
        "requiredSharesRaw": _round(raw_required, 4),
        "requiredSharesAdjusted": _round(adjusted, 4),
        "requiredSharesFinal": final_required,
        "marketRule": market_rule,
    }


def _norm_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / math.sqrt(2.0)))


def _black_scholes_call(spot: float, strike: float, years: float, risk_free_rate: float, volatility: float) -> float:
    if spot <= 0 or strike <= 0 or years <= 0:
        return max(spot - strike, 0.0)
    if volatility <= 0:
        return max(spot - strike, 0.0)

    sqrt_t = math.sqrt(years)
    numerator = math.log(spot / strike) + (risk_free_rate + 0.5 * volatility * volatility) * years
    denominator = volatility * sqrt_t
    if denominator <= 0:
        return max(spot - strike, 0.0)
    d1 = numerator / denominator
    d2 = d1 - (volatility * sqrt_t)
    return (spot * _norm_cdf(d1)) - (strike * math.exp(-risk_free_rate * years) * _norm_cdf(d2))


def _build_row(row: Dict[str, Any], risk_free_rate: Optional[float], treasury_yield_10y: Optional[float]) -> Dict[str, Any]:
    stock_price = _to_float(row.get("stockPrice"))
    convert_price = _to_float(row.get("convertPrice"))
    ma20_price = _to_float(row.get("ma20CloseDb"))
    if ma20_price is None:
        ma20_price = _to_float(row.get("ma20Price"))
    volatility60 = _to_float(row.get("volatility60"))
    required_share_info = _resolve_required_shares(row)

    option_strike_price = None
    option_quantity = None
    option_unit_value = None
    expected_profit = None
    required_funds = None
    expected_return_rate = None

    if stock_price and stock_price > 0 and required_share_info["requiredSharesFinal"]:
        required_funds = required_share_info["requiredSharesFinal"] * stock_price

    if stock_price and stock_price > 0 and ma20_price and ma20_price > 0:
        option_strike_price = max(stock_price, ma20_price)
        option_quantity = 1000.0 / option_strike_price if option_strike_price > 0 else None

    if (
        stock_price and stock_price > 0 and
        option_strike_price and option_strike_price > 0 and
        option_quantity and option_quantity > 0 and
        risk_free_rate is not None and
        volatility60 is not None and volatility60 > 0
    ):
        option_unit_value = _black_scholes_call(
            stock_price,
            option_strike_price,
            OPTION_TERM_YEARS,
            risk_free_rate,
            volatility60,
        )
        expected_profit = option_unit_value * option_quantity

    if expected_profit is not None and required_funds and required_funds > 0:
        expected_return_rate = (expected_profit / required_funds) * 100.0

    stage_eligible = _is_stage_eligible(row)
    monitor_eligible = bool(
        stage_eligible and
        expected_return_rate is not None and
        expected_return_rate > MIN_EXPECTED_RETURN_RATE
    )

    reason = ""
    if not stage_eligible:
        reason = "stage_not_eligible"
    elif required_funds is None:
        reason = "missing_required_funds"
    elif volatility60 is None:
        reason = "missing_volatility60"
    elif expected_return_rate is None:
        reason = "missing_option_metrics"
    elif expected_return_rate <= MIN_EXPECTED_RETURN_RATE:
        reason = "expected_return_not_enough"

    return {
        **dict(row),
        **required_share_info,
        "stageEligible": stage_eligible,
        "monitorEligible": monitor_eligible,
        "optionStrikePrice": _round(option_strike_price, 4),
        "optionQuantity": _round(option_quantity, 6),
        "optionUnitValue": _round(option_unit_value, 6),
        "requiredFunds": _round(required_funds, 4),
        "expectedProfit": _round(expected_profit, 4),
        "expectedReturnRate": _round(expected_return_rate, 4),
        "treasuryYield10y": treasury_yield_10y,
        "nonEligibleReason": reason,
    }


def build_cb_rights_issue_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """把固定来源快照转换为对外页面数据。"""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    risk_free_rate = _to_float(fetch_payload.get("riskFreeRate"))
    treasury_yield_10y = _to_float(fetch_payload.get("treasuryYield10y"))
    source_rows = [
        _build_row(dict(record.get("raw") or {}), risk_free_rate, treasury_yield_10y)
        for record in bus_records
        if record.get("status") == "ok"
    ]

    source_rows.sort(
        key=lambda item: (
            0 if item.get("monitorEligible") else 1,
            (999999.0 if item.get("expectedReturnRate") is None else -float(item.get("expectedReturnRate"))),
            str(item.get("progressDate") or ""),
        )
    )
    monitor_list = [item for item in source_rows if item.get("monitorEligible")]
    source_summary = {
        "totalRows": len(source_rows),
        "eligibleStageCount": sum(1 for item in source_rows if item.get("stageEligible")),
        "monitorEligibleCount": len(monitor_list),
        "highReturnCount": sum(
            1
            for item in source_rows
            if (_to_float(item.get("expectedReturnRate")) is not None and float(item.get("expectedReturnRate")) > MIN_EXPECTED_RETURN_RATE)
        ),
        "sourceUrl": fetch_payload.get("sourceUrl"),
        "sourceTitle": fetch_payload.get("sourceTitle"),
    }

    return build_success(
        {
            "monitorList": monitor_list,
            "sourceRows": source_rows,
            "sourceSummary": source_summary,
            "rebuildStatus": {
                "success": True,
                "lastRebuildAt": fetch_payload.get("updateTime"),
                "lastRebuildError": None,
                "hydrateStats": fetch_payload.get("hydrateStats"),
            },
        },
        updateTime=fetch_payload.get("updateTime"),
        source=fetch_payload.get("source"),
        sourceUrl=fetch_payload.get("sourceUrl"),
        sourceTitle=fetch_payload.get("sourceTitle"),
        treasuryYield10y=fetch_payload.get("treasuryYield10y"),
        treasuryYield10yDate=fetch_payload.get("treasuryYield10yDate"),
        treasuryYield10ySource=fetch_payload.get("treasuryYield10ySource"),
    )
