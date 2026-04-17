"""可转债抢权配售策略输出服务。"""

from __future__ import annotations

import math
import re
from bisect import bisect_right
from datetime import datetime
from statistics import median
from typing import Any, Dict, List, Optional

from shared.config.script_config import get_config
from shared.models.service_result import build_success

_CONFIG = get_config()
_STRATEGY_CONFIG = (((_CONFIG.get("strategy") or {}).get("cb_rights_issue") or {}))

MIN_EXPECTED_RETURN_RATE = float(_STRATEGY_CONFIG.get("min_expected_return_rate") or 6.0)
TARGET_BOND_LOTS = max(1, int(_STRATEGY_CONFIG.get("target_bond_lots") or 10))
MARGIN_SHARE_RATIO = float(_STRATEGY_CONFIG.get("margin_share_ratio") or 0.6)
MARGIN_ROUND_LOT_SHARES = max(1, int(_STRATEGY_CONFIG.get("margin_round_lot_shares") or 50))
EXPECTED_ROUND_LOT_SHARES = max(1, int(_STRATEGY_CONFIG.get("expected_round_lot_shares") or 100))
OPTION_TERM_YEARS = float(_STRATEGY_CONFIG.get("option_term_years") or 6.0)
TRADING_DAYS_PER_YEAR = max(1, int(_STRATEGY_CONFIG.get("annualization_trading_days_per_year") or 252))

APPLY_STAGE_KEYWORDS = tuple(
    str(item or "").strip()
    for item in (_STRATEGY_CONFIG.get("apply_stage_keywords") or ["申购", "待发", "发行公告", "网上发行"])
    if str(item or "").strip()
)
REGISTRATION_STAGE_KEYWORDS = ("同意注册", "注册生效")
LISTING_COMMITTEE_STAGE_KEYWORDS = ("上市委通过",)
TIMELINE_LINE_PATTERN = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})\s*(?P<name>.+)")


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


def _normalize_date_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return text[:10]


def _normalize_trade_calendar(values: Any) -> List[str]:
    result = sorted({
        _normalize_date_text(item)
        for item in (values or [])
        if _normalize_date_text(item)
    })
    return result


def _count_trading_days(trade_calendar: List[str], start_date: str, end_date: str) -> Optional[int]:
    start_text = _normalize_date_text(start_date)
    end_text = _normalize_date_text(end_date)
    if not start_text or not end_text or start_text >= end_text or not trade_calendar:
        return None
    left = bisect_right(trade_calendar, start_text)
    right = bisect_right(trade_calendar, end_text)
    count = right - left
    return count if count > 0 else None


def _add_trading_days(trade_calendar: List[str], start_date: str, trading_days: int) -> str:
    start_text = _normalize_date_text(start_date)
    if not start_text or trading_days <= 0 or not trade_calendar:
        return ""
    start_index = bisect_right(trade_calendar, start_text)
    target_index = start_index + trading_days - 1
    if target_index < 0 or target_index >= len(trade_calendar):
        return ""
    return trade_calendar[target_index]


def _clean_progress_text(value: Any) -> str:
    text = str(value or "").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_progress_sample_group(progress_name: str) -> str:
    text = _clean_progress_text(progress_name)
    if any(keyword in text for keyword in LISTING_COMMITTEE_STAGE_KEYWORDS):
        return "listing_committee"
    if any(keyword in text for keyword in REGISTRATION_STAGE_KEYWORDS):
        return "registration"
    return ""


def _is_apply_stage(row: Dict[str, Any]) -> bool:
    if _normalize_date_text(row.get("applyDate")):
        return True
    progress_name = _clean_progress_text(row.get("progressName"))
    return any(keyword in progress_name for keyword in APPLY_STAGE_KEYWORDS)


def _extract_progress_timeline(row: Dict[str, Any]) -> List[tuple[str, str]]:
    result: List[tuple[str, str]] = []
    progress_full = str(row.get("progressFull") or "").replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    for line in progress_full.splitlines():
        cleaned_line = re.sub(r"<[^>]+>", " ", str(line or "")).strip()
        if not cleaned_line:
            continue
        match = TIMELINE_LINE_PATTERN.match(cleaned_line)
        if not match:
            continue
        date_text = _normalize_date_text(match.group("date"))
        stage_name = _clean_progress_text(match.group("name"))
        if date_text and stage_name:
            result.append((date_text, stage_name))

    progress_date = _normalize_date_text(row.get("progressDate"))
    progress_name = _clean_progress_text(row.get("progressName"))
    if progress_date and progress_name and (progress_date, progress_name) not in result:
        result.append((progress_date, progress_name))
    return result


def _extract_stage_dates_from_row(row: Dict[str, Any]) -> Dict[str, str]:
    stage_dates: Dict[str, str] = {}
    for date_text, stage_name in _extract_progress_timeline(row):
        sample_group = _normalize_progress_sample_group(stage_name)
        if not sample_group:
            continue
        previous = stage_dates.get(sample_group)
        if not previous or date_text > previous:
            stage_dates[sample_group] = date_text
    return stage_dates


def _build_stage_lag_median_map(rows: List[Dict[str, Any]], trade_calendar: List[str]) -> Dict[str, int]:
    if not trade_calendar:
        return {}

    samples: Dict[str, List[int]] = {
        "listing_committee": [],
        "registration": [],
    }
    for row in rows:
        apply_date = _normalize_date_text(row.get("applyDate"))
        if not apply_date:
            continue
        for sample_group, progress_date in _extract_stage_dates_from_row(row).items():
            gap = _count_trading_days(trade_calendar, progress_date, apply_date)
            if gap is None or gap <= 0:
                continue
            samples[sample_group].append(gap)

    medians: Dict[str, int] = {}
    for key, values in samples.items():
        if values:
            medians[key] = int(round(float(median(values))))
    return medians


def _resolve_estimated_apply_trading_days(
    row: Dict[str, Any],
    *,
    today_text: str,
    trade_calendar: List[str],
    stage_lag_median_map: Dict[str, int],
) -> tuple[Optional[int], str]:
    apply_date = _normalize_date_text(row.get("applyDate"))
    if apply_date:
        return _count_trading_days(trade_calendar, today_text, apply_date), "apply_date"

    sample_group = _normalize_progress_sample_group(str(row.get("progressName") or ""))
    progress_date = _normalize_date_text(row.get("progressDate"))
    stage_lag = int(stage_lag_median_map.get(sample_group) or 0)
    if not sample_group or not progress_date or stage_lag <= 0:
        return None, ""

    estimated_apply_date = _add_trading_days(trade_calendar, progress_date, stage_lag)
    if not estimated_apply_date:
        return None, ""
    return _count_trading_days(trade_calendar, today_text, estimated_apply_date), f"median:{sample_group}"


def _resolve_expected_required_shares(raw_required_shares: Optional[float]) -> Optional[int]:
    if raw_required_shares is None or raw_required_shares <= 0:
        return None
    adjusted = raw_required_shares * MARGIN_SHARE_RATIO
    return int(math.ceil(adjusted / EXPECTED_ROUND_LOT_SHARES) * EXPECTED_ROUND_LOT_SHARES)


def _resolve_margin_required_shares(raw_required_shares: Optional[float]) -> Optional[int]:
    if raw_required_shares is None or raw_required_shares <= 0:
        return None
    adjusted = raw_required_shares * MARGIN_SHARE_RATIO
    return int(math.ceil(adjusted / MARGIN_ROUND_LOT_SHARES) * MARGIN_ROUND_LOT_SHARES)


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


def _calc_annualized_return_rate(margin_peel_return_rate: Optional[float], trading_days: Optional[int]) -> Optional[float]:
    if margin_peel_return_rate is None or trading_days is None or trading_days <= 0:
        return None
    base_ratio = margin_peel_return_rate / 100.0
    if base_ratio <= -1.0:
        return None
    annualized_ratio = math.pow(1.0 + base_ratio, TRADING_DAYS_PER_YEAR / float(trading_days)) - 1.0
    return annualized_ratio * 100.0


def _build_row(
    row: Dict[str, Any],
    *,
    risk_free_rate: Optional[float],
    treasury_yield_10y: Optional[float],
    trade_calendar: List[str],
    today_text: str,
    stage_lag_median_map: Dict[str, int],
) -> Dict[str, Any]:
    stock_price = _to_float(row.get("stockPrice"))
    convert_price = _to_float(row.get("convertPrice"))
    volatility = _to_float(row.get("volatility250") if row.get("volatility250") is not None else row.get("volatility60"))
    raw_required_shares = _to_float(row.get("rawRequiredShares"))
    placement_shares = _resolve_expected_required_shares(raw_required_shares)
    margin_required_shares = _resolve_margin_required_shares(raw_required_shares)

    issue_scale_yi = _to_float(
        row.get("issueScaleYi")
        if row.get("issueScaleYi") is not None
        else (row.get("amountYi") if row.get("amountYi") is not None else row.get("cbAmountYi"))
    )
    stock_market_value_yi = _to_float(row.get("stockMarketValueYi"))
    issue_ratio = None
    if issue_scale_yi is not None and stock_market_value_yi is not None and stock_market_value_yi > 0:
        issue_ratio = issue_scale_yi / stock_market_value_yi

    required_funds = None
    margin_required_funds = None
    original_funds_baseline = None
    if stock_price is not None and stock_price > 0 and raw_required_shares is not None and raw_required_shares > 0:
        original_funds_baseline = raw_required_shares * stock_price
    if stock_price is not None and stock_price > 0 and placement_shares is not None:
        required_funds = placement_shares * stock_price
    if stock_price is not None and stock_price > 0 and margin_required_shares is not None:
        margin_required_funds = margin_required_shares * stock_price

    option_reference_price = convert_price
    option_strike_price = None
    option_quantity = None
    option_unit_value = None
    option_value = None
    if stock_price and stock_price > 0 and convert_price and convert_price > 0:
        option_strike_price = max(stock_price, convert_price)
        option_quantity = (TARGET_BOND_LOTS * 100.0 / option_strike_price) if option_strike_price > 0 else None

    if (
        stock_price and stock_price > 0
        and option_strike_price and option_strike_price > 0
        and option_quantity and option_quantity > 0
        and risk_free_rate is not None
        and volatility is not None and volatility > 0
    ):
        option_unit_value = _black_scholes_call(
            stock_price,
            option_strike_price,
            OPTION_TERM_YEARS,
            risk_free_rate,
            volatility,
        )
        option_value = option_unit_value * option_quantity

    expected_return_rate = None
    if option_value is not None and required_funds is not None and required_funds > 0:
        expected_return_rate = option_value / required_funds * 100.0

    margin_return_rate = None
    if option_value is not None and margin_required_funds is not None and margin_required_funds > 0:
        margin_return_rate = option_value / margin_required_funds * 100.0

    expected_peel_return_rate = None
    if (
        expected_return_rate is not None
        and original_funds_baseline is not None
        and required_funds is not None
        and required_funds > 0
    ):
        expected_peel_return_rate = expected_return_rate * ((original_funds_baseline - required_funds) / required_funds)

    margin_peel_return_rate = None
    if (
        margin_return_rate is not None
        and original_funds_baseline is not None
        and margin_required_funds is not None
        and margin_required_funds > 0
    ):
        margin_peel_return_rate = margin_return_rate * ((original_funds_baseline - margin_required_funds) / margin_required_funds)

    estimated_apply_trading_days, trading_days_source = _resolve_estimated_apply_trading_days(
        row,
        today_text=today_text,
        trade_calendar=trade_calendar,
        stage_lag_median_map=stage_lag_median_map,
    )
    annualized_return_rate = _calc_annualized_return_rate(margin_peel_return_rate, estimated_apply_trading_days)

    in_apply_stage = _is_apply_stage(row)
    high_return = bool(expected_return_rate is not None and expected_return_rate > MIN_EXPECTED_RETURN_RATE)
    pin_priority = None
    push_eligible = False

    return {
        **dict(row),
        "issueScaleYi": _round(issue_scale_yi, 4),
        "stockMarketValueYi": _round(stock_market_value_yi, 4),
        "issueRatio": _round(issue_ratio, 6),
        "placementShares": _round(placement_shares, 4),
        "marginRequiredShares": margin_required_shares,
        "requiredSharesRaw": _round(raw_required_shares, 4),
        "requiredSharesAdjusted": _round(placement_shares, 4),
        "requiredSharesFinal": _round(placement_shares, 4),
        "marginRequiredFunds": _round(margin_required_funds, 4),
        "requiredFunds": _round(required_funds, 4),
        "originalFundsBaseline": _round(original_funds_baseline, 4),
        "marketRule": f"raw_x_{MARGIN_SHARE_RATIO}_expected_round_{EXPECTED_ROUND_LOT_SHARES}_margin_round_{MARGIN_ROUND_LOT_SHARES}",
        "stageEligible": in_apply_stage or bool(_normalize_progress_sample_group(str(row.get("progressName") or ""))),
        "monitorEligible": False,
        "optionReferencePrice": _round(option_reference_price, 4),
        "optionStrikePrice": _round(option_strike_price, 4),
        "optionQuantity": _round(option_quantity, 6),
        "optionUnitValue": _round(option_unit_value, 6),
        "optionValue": _round(option_value, 4),
        "expectedProfit": _round(option_value, 4),
        "expectedReturnRate": _round(expected_return_rate, 4),
        "marginReturnRate": _round(margin_return_rate, 4),
        "expectedPeelReturnRate": _round(expected_peel_return_rate, 4),
        "marginPeelReturnRate": _round(margin_peel_return_rate, 4),
        "estimatedApplyTradingDays": estimated_apply_trading_days,
        "estimatedApplyTradingDaysSource": trading_days_source,
        "annualizedReturnRate": _round(annualized_return_rate, 4),
        "treasuryYield10y": treasury_yield_10y,
        "pinPriority": pin_priority,
        "inApplyStage": in_apply_stage,
        "pushEligible": False,
        "isHighExpectedReturn": high_return,
    }


def _sort_source_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def sort_key(item: Dict[str, Any]) -> tuple[Any, ...]:
        annualized = _to_float(item.get("annualizedReturnRate"))
        margin_return = _to_float(item.get("marginReturnRate"))
        expected_return = _to_float(item.get("expectedReturnRate"))
        progress_date = _normalize_date_text(item.get("progressDate"))
        record_date = _normalize_date_text(item.get("recordDate"))
        return (
            int(item.get("pinPriority") or 99),
            1 if annualized is None else 0,
            999999.0 if annualized is None else -annualized,
            1 if margin_return is None else 0,
            999999.0 if margin_return is None else -margin_return,
            1 if expected_return is None else 0,
            999999.0 if expected_return is None else -expected_return,
            progress_date or "9999-99-99",
            record_date or "9999-99-99",
            str(item.get("stockCode") or ""),
        )

    return sorted(rows, key=sort_key)


def build_cb_rights_issue_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """把固定来源快照转换为对外页面数据。"""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    risk_free_rate = _to_float(fetch_payload.get("riskFreeRate"))
    treasury_yield_10y = _to_float(fetch_payload.get("treasuryYield10y"))
    trade_calendar = _normalize_trade_calendar(fetch_payload.get("tradeCalendarDates"))
    today_text = datetime.now().date().isoformat()
    base_rows = [
        dict(record.get("raw") or {})
        for record in bus_records
        if record.get("status") == "ok" and isinstance(record.get("raw"), dict)
    ]
    stage_lag_median_map = _build_stage_lag_median_map(base_rows, trade_calendar)
    source_rows = [
        _build_row(
            row,
            risk_free_rate=risk_free_rate,
            treasury_yield_10y=treasury_yield_10y,
            trade_calendar=trade_calendar,
            today_text=today_text,
            stage_lag_median_map=stage_lag_median_map,
        )
        for row in base_rows
    ]
    source_rows = _sort_source_rows(source_rows)
    monitor_list: List[Dict[str, Any]] = []

    source_summary = {
        "totalRows": len(source_rows),
        "applyStageCount": sum(1 for item in source_rows if item.get("inApplyStage")),
        "highReturnCount": sum(1 for item in source_rows if item.get("isHighExpectedReturn")),
        "pushEligibleCount": 0,
        "sourceUrl": fetch_payload.get("sourceUrl"),
        "sourceTitle": fetch_payload.get("sourceTitle"),
        "stageLagMedianMap": stage_lag_median_map,
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
