#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# AI-SUMMARY: 可转债指标计算：波动率/ATR/理论定价/纯债价值/期权价值
# 对应 INDEX.md §9 文件摘要索引

"""Convertible bond metrics calculation: volatility, ATR, theoretical pricing, option values."""

from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from shared.db import stock_price_history_db as price_db

_CONFIG_GLOBAL: Dict[str, Any] = {}
_VOL_WINDOWS_GLOBAL: tuple[int, ...] = (250,)
_PRIMARY_VOL_WINDOW_GLOBAL: int = 250
_TRADING_DAYS_PER_YEAR_GLOBAL: int = 252
_ATR_WINDOW_GLOBAL: int = 20
_REQUIRED_CLOSE_ROWS_GLOBAL: int = 251
_REQUIRED_HISTORY_BAR_ROWS_GLOBAL: int = 420


def init_metrics_config(
    vol_windows: tuple[int, ...],
    primary_vol_window: int,
    trading_days_per_year: int,
    atr_window: int,
) -> None:
    global _VOL_WINDOWS_GLOBAL, _PRIMARY_VOL_WINDOW_GLOBAL, _TRADING_DAYS_PER_YEAR_GLOBAL, _ATR_WINDOW_GLOBAL
    global _REQUIRED_CLOSE_ROWS_GLOBAL, _REQUIRED_HISTORY_BAR_ROWS_GLOBAL
    _VOL_WINDOWS_GLOBAL = vol_windows
    _PRIMARY_VOL_WINDOW_GLOBAL = primary_vol_window
    _TRADING_DAYS_PER_YEAR_GLOBAL = trading_days_per_year
    _ATR_WINDOW_GLOBAL = atr_window
    _REQUIRED_CLOSE_ROWS_GLOBAL = max(vol_windows) + 1
    _REQUIRED_HISTORY_BAR_ROWS_GLOBAL = max(
        _REQUIRED_CLOSE_ROWS_GLOBAL, atr_window + 1, 20
    )


PRIMARY_VOLATILITY_FIELD = f"volatility{_PRIMARY_VOL_WINDOW_GLOBAL}"
LEGACY_PRIMARY_VOL_FIELD = "volatility60"
VOLATILITY_METRIC_FIELDS = tuple(
    dict.fromkeys([*(f"volatility{w}" for w in _VOL_WINDOWS_GLOBAL), LEGACY_PRIMARY_VOL_FIELD])
)


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in {"", "nan", "NaN", "nat", "NaT", "None"}:
        return True
    try:
        return bool(pd.isna(value))
    except Exception:
        return False


def _to_float(value: Any) -> Optional[float]:
    if _is_null(value):
        return None
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def _to_positive_float(value: Any) -> Optional[float]:
    num = _to_float(value)
    if num is None or num <= 0:
        return None
    return num


def _to_percent_ratio(value: Any) -> Optional[float]:
    if _is_null(value):
        return None
    text = str(value).strip().replace("%", "").replace(",", "")
    if not text:
        return None
    try:
        val = float(text)
    except Exception:
        return None
    if val <= 0:
        return None
    return val / 100.0 if val > 1.0 else val


def _to_date_str(value: Any) -> Optional[str]:
    if _is_null(value):
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    try:
        parsed = pd.to_datetime(str(value).strip(), errors="coerce")
        if pd.isna(parsed):
            return None
        return parsed.date().isoformat()
    except Exception:
        return None


def _blank_volatility_metrics() -> Dict[str, Optional[float]]:
    return {field: None for field in VOLATILITY_METRIC_FIELDS}


def _with_primary_volatility_aliases(
    metrics: Dict[str, Optional[float]] | None,
) -> Dict[str, Optional[float]]:
    normalized = _blank_volatility_metrics()
    if isinstance(metrics, dict):
        normalized.update(metrics)
    primary_value = _to_float(normalized.get(PRIMARY_VOLATILITY_FIELD))
    if (
        LEGACY_PRIMARY_VOL_FIELD != PRIMARY_VOLATILITY_FIELD
        and LEGACY_PRIMARY_VOL_FIELD not in {f"volatility{w}" for w in _VOL_WINDOWS_GLOBAL}
    ):
        normalized[LEGACY_PRIMARY_VOL_FIELD] = primary_value
    return normalized


def _normalize_putback_price_int(value: Any) -> Optional[float]:
    num = _to_float(value)
    if num is None or num <= 0:
        return None
    return float(int(round(num)))


def _extract_percent_values(text: Any) -> list[float]:
    import re
    payload = str(text or "")
    values: list[float] = []
    for hit in re.finditer(r"(\d+(?:\.\d+)?)\s*%", payload):
        try:
            value = float(hit.group(1))
        except Exception:
            continue
        if value > 0:
            values.append(value)
    return values


def _derive_resale_trigger_ratio(row: Dict[str, Any]) -> Optional[float]:
    import re
    ratio = _to_percent_ratio(row.get("putbackTriggerRatio"))
    if ratio is not None:
        return ratio

    clause = str(row.get("resaleClause") or "")
    if not clause:
        return None

    targeted_patterns = [
        r"低于[^。；\n]{0,50}?(\d+(?:\.\d+)?)\s*%",
        r"不足[^。；\n]{0,50}?(\d+(?:\.\d+)?)\s*%",
    ]
    for pattern in targeted_patterns:
        hit = re.search(pattern, clause)
        if not hit:
            continue
        value = _to_float(hit.group(1))
        if value is not None and 20.0 <= value <= 95.0:
            return value / 100.0

    percent_values = [value for value in _extract_percent_values(clause) if 20.0 <= value <= 95.0]
    if not percent_values:
        return None
    return min(percent_values) / 100.0


def _resolve_putback_trigger_price(row: Dict[str, Any]) -> tuple[Optional[float], str]:
    direct = _to_positive_float(row.get("putbackTriggerPrice"))
    if direct is not None:
        return direct, "direct_resale_trigger_price"

    ratio = _derive_resale_trigger_ratio(row)
    row["putbackTriggerRatio"] = (ratio * 100.0) if ratio is not None else None
    if ratio is None:
        return None, "missing"

    base_price = (
        _to_positive_float(row.get("currentTransferPrice"))
        or _to_positive_float(row.get("downFixPrice"))
        or _to_positive_float(row.get("convertPrice"))
        or _to_positive_float(row.get("initialTransferPrice"))
    )
    if base_price is None:
        return None, "missing_base_transfer_price"

    return base_price * ratio, "derived_from_resale_clause_ratio"


def _extract_maturity_redeem_price(redeem_clause: Any) -> Optional[float]:
    import re
    text = str(redeem_clause or "")
    if not text:
        return None

    patterns = [
        r"到期[^。；\n]{0,100}?面值[^0-9]{0,15}(\d+(?:\.\d+)?)\s*%",
        r"期满[^。；\n]{0,100}?面值[^0-9]{0,15}(\d+(?:\.\d+)?)\s*%",
    ]
    for pattern in patterns:
        hit = re.search(pattern, text)
        if not hit:
            continue
        value = _to_float(hit.group(1))
        if value is not None and 80 <= value <= 200:
            return value

    values = [value for value in _extract_percent_values(text) if 80 <= value <= 200]
    if not values:
        return None
    return max(values)


def _should_exclude_by_delist_or_expiry(row: Dict[str, Any], as_of_date: date) -> bool:
    for key in ("delistDate", "ceaseDate"):
        dt = _to_date_str(row.get(key))
        if not dt:
            continue
        try:
            if datetime.fromisoformat(dt).date() <= as_of_date:
                return True
        except Exception:
            continue
    return False


def _american_option_binomial(
    spot: float,
    strike: float,
    years: float,
    risk_free_rate: float,
    volatility: float,
    option_type: str,
    steps: int = 120,
) -> float:
    if spot <= 0 or strike <= 0 or years <= 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
    if volatility <= 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)

    dt = years / max(steps, 1)
    if dt <= 0:
        return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)

    up = math.exp(volatility * math.sqrt(dt))
    down = 1.0 / up
    disc = math.exp(-risk_free_rate * dt)
    growth = math.exp(risk_free_rate * dt)
    prob = (growth - down) / (up - down)
    prob = min(max(prob, 0.0), 1.0)

    values = []
    for i in range(steps + 1):
        stock_t = spot * (up ** (steps - i)) * (down ** i)
        if option_type == "call":
            values.append(max(stock_t - strike, 0.0))
        else:
            values.append(max(strike - stock_t, 0.0))

    for step in range(steps - 1, -1, -1):
        next_values = []
        for i in range(step + 1):
            hold = disc * (prob * values[i] + (1.0 - prob) * values[i + 1])
            stock_t = spot * (up ** (step - i)) * (down ** i)
            if option_type == "call":
                exercise = max(stock_t - strike, 0.0)
            else:
                exercise = max(strike - stock_t, 0.0)
            next_values.append(max(hold, exercise))
        values = next_values

    return float(values[0]) if values else 0.0


def _bond_floor_value(risk_free_rate: float, years: Optional[float]) -> float:
    if years is None or years <= 0:
        return 100.0
    base = max(1.0 + risk_free_rate, 1e-6)
    return 100.0 / (base ** years)


def _calc_volatility_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    symbol = str(stock_code or "").strip()
    if not symbol:
        return _blank_volatility_metrics()

    close_series = pd.Series(
        price_db.load_recent_closes(symbol, _REQUIRED_CLOSE_ROWS_GLOBAL), dtype="float64"
    )

    if len(close_series) < 2:
        return _blank_volatility_metrics()

    returns = np.log(close_series / close_series.shift(1)).dropna()
    metrics: Dict[str, Optional[float]] = {}
    for window in _VOL_WINDOWS_GLOBAL:
        key = f"volatility{window}"
        required_returns = max(2, window)
        if len(returns) < required_returns:
            metrics[key] = None
            continue
        sample = returns.tail(required_returns)
        std = float(sample.std(ddof=1)) if len(sample) > 1 else 0.0
        metrics[key] = std * math.sqrt(_TRADING_DAYS_PER_YEAR_GLOBAL)
    return _with_primary_volatility_aliases(metrics)


def _volatility_metrics_ready(metrics: Dict[str, Any]) -> bool:
    if not isinstance(metrics, dict):
        return False
    return _to_float(metrics.get(f"volatility{_PRIMARY_VOL_WINDOW_GLOBAL}")) is not None


def _calc_stock_history_metrics(stock_code: str) -> Dict[str, Optional[float]]:
    symbol = str(stock_code or "").strip()
    metrics: Dict[str, Optional[float]] = {
        **_blank_volatility_metrics(),
        "stockAtr20": None,
        "stockAvgTurnoverAmount20Yi": None,
        "stockAvgTurnoverAmount5Yi": None,
    }

    if not symbol:
        return metrics

    bars = price_db.load_recent_bars(symbol, _REQUIRED_HISTORY_BAR_ROWS_GLOBAL)
    close_series = pd.Series(
        [item.get("close") for item in bars if _to_float(item.get("close")) is not None],
        dtype="float64",
    )

    if len(close_series) >= 2:
        returns = np.log(close_series / close_series.shift(1)).dropna()
        for window in _VOL_WINDOWS_GLOBAL:
            key = f"volatility{window}"
            required_returns = max(2, window)
            if len(returns) < required_returns:
                continue
            sample = returns.tail(required_returns)
            std = float(sample.std(ddof=1)) if len(sample) > 1 else 0.0
            metrics[key] = std * math.sqrt(_TRADING_DAYS_PER_YEAR_GLOBAL)

    rich_bars = [
        {
            "close": _to_float(item.get("close")),
            "high": _to_float(item.get("high")),
            "low": _to_float(item.get("low")),
            "amount": _to_float(item.get("amount")),
        }
        for item in bars
        if _to_float(item.get("close")) is not None
    ]

    true_ranges: list[float] = []
    prev_close: Optional[float] = None
    for item in rich_bars:
        close = item["close"]
        high = item["high"]
        low = item["low"]
        if high is not None and low is not None:
            if prev_close is None:
                true_ranges.append(high - low)
            else:
                true_ranges.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
        prev_close = close
    if len(true_ranges) >= _ATR_WINDOW_GLOBAL:
        metrics["stockAtr20"] = float(sum(true_ranges[-_ATR_WINDOW_GLOBAL:]) / _ATR_WINDOW_GLOBAL)

    valid_amounts = [item["amount"] for item in rich_bars if item["amount"] is not None]
    if len(valid_amounts) >= 20:
        metrics["stockAvgTurnoverAmount20Yi"] = float(sum(valid_amounts[-20:]) / 20 / 1e8)
    if len(valid_amounts) >= 5:
        metrics["stockAvgTurnoverAmount5Yi"] = float(sum(valid_amounts[-5:]) / 5 / 1e8)
    return _with_primary_volatility_aliases(metrics)


def _stock_history_metrics_ready(metrics: Dict[str, Any]) -> bool:
    if not isinstance(metrics, dict):
        return False
    if _to_float(metrics.get(f"volatility{_PRIMARY_VOL_WINDOW_GLOBAL}")) is None:
        return False
    if _to_float(metrics.get("stockAtr20")) is None:
        return False
    if _to_float(metrics.get("stockAvgTurnoverAmount20Yi")) is None:
        return False
    if _to_float(metrics.get("stockAvgTurnoverAmount5Yi")) is None:
        return False
    return True


def _build_theoretical_metrics(
    row: Dict[str, Any], risk_free_rate: float
) -> Dict[str, Optional[float]]:
    spot = _to_float(row.get("stockPrice"))
    market_price = _to_float(row.get("price"))
    convert_price = _to_float(row.get("convertPrice"))
    remaining_years = _to_float(row.get("remainingYears"))

    market_pure_bond = _to_positive_float(row.get("pureBondValue"))
    bond_value = market_pure_bond
    option_qty = None
    if convert_price and convert_price > 0:
        option_qty = 100.0 / convert_price
    redeem_trigger_price = _to_float(row.get("redeemTriggerPrice"))
    is_below_redeem_trigger = (
        spot is not None
        and redeem_trigger_price is not None
        and redeem_trigger_price > 0
        and spot < redeem_trigger_price
    )
    pricing_bucket = (
        "below_redeem_trigger"
        if is_below_redeem_trigger
        else "at_or_above_redeem_trigger"
        if (spot is not None and redeem_trigger_price is not None and redeem_trigger_price > 0)
        else "unknown"
    )
    pricing_formula = "bond+callspread"

    result: Dict[str, Optional[float]] = {
        "bondValue": round(bond_value, 4) if bond_value is not None else None,
        "optionQty": round(option_qty, 6) if option_qty else None,
        "isStockBelowRedeemTrigger": bool(is_below_redeem_trigger),
        "pricingBucket": pricing_bucket,
        "pricingFormula": pricing_formula,
    }

    for window in _VOL_WINDOWS_GLOBAL:
        vol = _to_float(row.get(f"volatility{window}"))
        call_strike = None
        redeem_call_strike = None
        theoretical = None
        call_value = None
        put_value = None
        long_call_value = None
        short_call_value = None
        call_spread_value = None
        gap = None
        premium_rate = None

        if option_qty and option_qty > 0 and convert_price and convert_price > 0:
            bond_floor_strike = (bond_value / option_qty) if bond_value is not None and option_qty > 0 else None
            strike_candidates = [value for value in [convert_price, bond_floor_strike] if value is not None and value > 0]
            call_strike = max(strike_candidates) if strike_candidates else None
            redeem_call_strike = (
                redeem_trigger_price if redeem_trigger_price and redeem_trigger_price > 0 else None
            )
            if (
                bond_value is not None
                and spot is not None
                and vol is not None
                and remaining_years is not None
                and call_strike is not None
                and redeem_call_strike is not None
            ):
                long_call_unit = _american_option_binomial(
                    spot, call_strike, remaining_years, risk_free_rate, vol, "call"
                )
                short_call_unit = _american_option_binomial(
                    spot, redeem_call_strike, remaining_years, risk_free_rate, vol, "call"
                )
                long_call_value = long_call_unit * option_qty
                short_call_value = short_call_unit * option_qty
                call_spread_value = max(long_call_value - short_call_value, 0.0)
                call_value = call_spread_value
                put_value = None

                theoretical = bond_value + call_spread_value
                if market_price is not None:
                    gap = theoretical - market_price
                    if market_price != 0:
                        premium_rate = (gap / market_price) * 100.0

        suffix = str(window)
        result[f"callStrike{suffix}"] = round(call_strike, 4) if call_strike is not None else None
        result[f"redeemCallStrike{suffix}"] = (
            round(redeem_call_strike, 4) if redeem_call_strike is not None else None
        )
        result[f"putStrike{suffix}"] = None
        result[f"longCallOptionValue{suffix}"] = round(long_call_value, 4) if long_call_value is not None else None
        result[f"shortCallOptionValue{suffix}"] = round(short_call_value, 4) if short_call_value is not None else None
        result[f"callSpreadOptionValue{suffix}"] = (
            round(call_spread_value, 4) if call_spread_value is not None else None
        )
        result[f"callOptionValue{suffix}"] = round(call_value, 4) if call_value is not None else None
        result[f"putOptionValue{suffix}"] = None
        result[f"theoreticalPrice{suffix}"] = round(theoretical, 4) if theoretical is not None else None
        result[f"theoreticalGap{suffix}"] = round(gap, 4) if gap is not None else None
        result[f"theoreticalPremiumRate{suffix}"] = round(premium_rate, 4) if premium_rate is not None else None

    return result


def _build_small_redemption_option_metrics(
    row: Dict[str, Any], risk_free_rate: float
) -> Dict[str, Optional[float]]:
    spot = _to_float(row.get("stockPrice"))
    convert_price = _to_positive_float(row.get("convertPrice"))
    remaining_years = _to_positive_float(row.get("remainingYears"))
    redeem_trigger_price = _to_positive_float(row.get("redeemTriggerPrice"))
    option_qty = (100.0 / convert_price) if convert_price else None
    bond_value = 100.0
    call_strike = None
    long_call_value = None
    short_call_value = None
    option_value = None
    option_yield = None
    option_annualized_yield = None
    total_annualized_yield = None
    volatility = _to_float(row.get(f"volatility{_PRIMARY_VOL_WINDOW_GLOBAL}")) or _to_float(
        row.get("annualizedVolatility")
    )

    if option_qty and option_qty > 0:
        bond_floor_strike = bond_value / option_qty
        call_strike = max(convert_price, bond_floor_strike)

    if (
        option_qty
        and option_qty > 0
        and spot is not None
        and remaining_years is not None
        and call_strike is not None
        and redeem_trigger_price is not None
        and volatility is not None
    ):
        long_call_unit = _american_option_binomial(
            spot, call_strike, remaining_years, risk_free_rate, volatility, "call"
        )
        short_call_unit = _american_option_binomial(
            spot, redeem_trigger_price, remaining_years, risk_free_rate, volatility, "call"
        )
        long_call_value = long_call_unit * option_qty
        short_call_value = short_call_unit * option_qty
        option_value = max(long_call_value - short_call_value, 0.0)

        if market_price := _to_positive_float(row.get("price")):
            option_yield = (option_value / market_price) if option_value is not None else None
            if option_yield is not None and remaining_years and remaining_years > 0:
                option_annualized_yield = (1.0 + option_yield) ** (1.0 / remaining_years) - 1.0
            small_redemption_annualized = _to_float(row.get("smallRedemptionAnnualizedYield"))
            if small_redemption_annualized is not None and option_annualized_yield is not None:
                total_annualized_yield = small_redemption_annualized + option_annualized_yield

    return {
        "smallRedemptionBondValue": bond_value,
        "smallRedemptionCallStrike": round(call_strike, 4) if call_strike is not None else None,
        "smallRedemptionOptionValue": round(option_value, 4) if option_value is not None else None,
        "smallRedemptionOptionYield": round(option_yield, 4) if option_yield is not None else None,
        "smallRedemptionOptionAnnualizedYield": (
            round(option_annualized_yield, 4) if option_annualized_yield is not None else None
        ),
        "smallRedemptionTotalAnnualizedYield": (
            round(total_annualized_yield, 4) if total_annualized_yield is not None else None
        ),
    }