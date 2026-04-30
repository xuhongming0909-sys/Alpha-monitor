#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Historical premium (AH/AB) backed by local SQLite cache (5Y, A-share HFQ when available)."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import akshare as ak
import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import premium_history_db as db
from market_pairs import find_ab_pair, find_ah_pair, load_dynamic_pairs

WINDOW_DAYS = 365 * 5
MIN_DEGRADED_SAMPLE_COUNT = 1
MAX_DEGRADED_RANGE_DAYS = 7
REQUEST_HEADERS = {
    "Referer": "https://gu.qq.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}


class PremiumDataError(Exception):
    pass


def _parse_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def _safe_day_span(start_date: str, end_date: str) -> Optional[int]:
    try:
        return (_parse_date(end_date) - _parse_date(start_date)).days
    except Exception:
        return None


def _safe_date_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "strftime"):
        try:
            return value.strftime("%Y-%m-%d")
        except Exception:
            return None
    text = str(value).strip()
    return text[:10] if text else None


def _extract_latest_date(frame: Any, date_col: str = "date") -> Optional[str]:
    if frame is None or getattr(frame, "empty", True):
        return None
    if date_col not in frame.columns:
        return None

    try:
        series = frame[date_col].dropna()
    except Exception:
        return None

    if getattr(series, "empty", True):
        return None
    return _safe_date_text(series.iloc[-1])


def _fetch_latest_market_date(market: str, code: str) -> Optional[str]:
    try:
        if market in {"sh", "sz"}:
            frame = ak.stock_zh_a_hist_tx(symbol=f"{market}{code}")
        elif market == "hk":
            frame = ak.stock_hk_daily(symbol=str(code).zfill(5))
        elif market == "us":
            frame = ak.stock_us_daily(symbol=str(code).upper())
        elif market in {"shb", "szb"}:
            frame = ak.stock_zh_b_daily(symbol=f"{market[:2]}{code}")
        else:
            return None
    except Exception:
        return None

    return _extract_latest_date(frame)


def _pick_market_samples(pair_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
    samples: Dict[str, str] = {
        "sh": "",
        "sz": "",
        "hk": "",
        "us": "",
        "shb": "",
        "szb": "",
    }

    for item in pair_data.get("ah", []):
        a_code = str(item.get("aCode") or "").strip()
        h_code = str(item.get("hCode") or "").strip()
        if a_code.startswith("6") and not samples["sh"]:
            samples["sh"] = a_code
        if a_code and not a_code.startswith("6") and not samples["sz"]:
            samples["sz"] = a_code
        if h_code and not samples["hk"]:
            samples["hk"] = h_code

    for item in pair_data.get("ab", []):
        a_code = str(item.get("aCode") or "").strip()
        b_code = str(item.get("bCode") or "").strip()
        b_market = str(item.get("bMarket") or "").strip().lower()
        if a_code.startswith("6") and not samples["sh"]:
            samples["sh"] = a_code
        if a_code and not a_code.startswith("6") and not samples["sz"]:
            samples["sz"] = a_code
        if b_market == "sh" and b_code and not samples["shb"]:
            samples["shb"] = b_code
        if b_market == "sz" and b_code and not samples["szb"]:
            samples["szb"] = b_code

    fallbacks = {
        "sh": "600000",
        "sz": "000001",
        "hk": "00005",
        "shb": "900901",
        "szb": "200002",
    }
    for market, fallback in fallbacks.items():
        if not samples[market]:
            samples[market] = fallback

    return samples


def load_market_latest_dates(pair_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
    samples = _pick_market_samples(pair_data)
    result: Dict[str, str] = {}

    for market, code in samples.items():
        latest_date = _fetch_latest_market_date(market, code)
        if latest_date:
            result[market] = latest_date

    return result


def resolve_pair_for_code(stock_type: str, a_code: str, pair_data: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    if stock_type == "AH":
        return find_ah_pair(a_code, pair_data.get("ah", []))
    if stock_type == "AB":
        return find_ab_pair(a_code, pair_data.get("ab", []))
    return None


def get_pair_code(stock_type: str, pair: Dict[str, Any]) -> str:
    if stock_type == "AH":
        return str(pair.get("hCode") or "").strip()
    return str(pair.get("bCode") or "").strip()


def expected_end_date_for_pair(stock_type: str, pair: Dict[str, Any], market_dates: Dict[str, str]) -> Optional[str]:
    if not pair:
        return None

    a_code = str(pair.get("aCode") or "").strip()
    a_market = str(pair.get("aMarket") or ("sh" if a_code.startswith("6") else "sz")).strip().lower()

    if stock_type == "AH":
        pair_market = "hk"
    else:
        raw_b_market = str(pair.get("bMarket") or ("sh" if str(pair.get("bCode") or "").startswith("9") else "sz")).strip().lower()
        pair_market = f"{raw_b_market}b"

    candidates = [market_dates.get(a_market), market_dates.get(pair_market)]
    available = [item for item in candidates if item]
    if not available:
        return None
    return min(available)


def history_needs_sync(
    stock_type: str,
    a_code: str,
    pair_code: Optional[str] = None,
    expected_end_date: Optional[str] = None,
    summary: Optional[Dict[str, Any]] = None,
) -> bool:
    cached_summary = summary
    if cached_summary is None:
        cached_summary = premium_history_summary(stock_type, a_code)

    if not cached_summary:
        return True

    sample_count = int(cached_summary.get("sampleCount") or 0)
    if sample_count <= 0:
        return True

    summary_pair_code = str(cached_summary.get("pairCode") or "").strip()
    if pair_code and summary_pair_code and summary_pair_code != str(pair_code).strip():
        return True

    summary_end_date = str(cached_summary.get("endDate") or "").strip()
    if expected_end_date and (not summary_end_date or summary_end_date < expected_end_date):
        return True

    if summary_requires_full_backfill(cached_summary):
        return True

    return False


def summary_requires_full_backfill(summary: Optional[Dict[str, Any]]) -> bool:
    if not summary:
        return False

    sample_count = int(summary.get("sampleCount") or 0)
    sample_count_3y = int(summary.get("sampleCount3Y") or 0)
    start_date = str(summary.get("startDate") or "").strip()
    end_date = str(summary.get("endDate") or "").strip()
    start_date_3y = str(summary.get("startDate3Y") or "").strip()
    end_date_3y = str(summary.get("endDate3Y") or "").strip()

    if sample_count <= MIN_DEGRADED_SAMPLE_COUNT or sample_count_3y <= MIN_DEGRADED_SAMPLE_COUNT:
        return True

    if sample_count > 0 and (not start_date or not end_date):
        return True

    if sample_count_3y > 0 and (not start_date_3y or not end_date_3y):
        return True

    if 0 < sample_count_3y <= 5 and start_date_3y and end_date_3y:
        span_days = _safe_day_span(start_date_3y, end_date_3y)
        if span_days is None or span_days <= MAX_DEGRADED_RANGE_DAYS:
            return True

    return False


def premium_history_summary(stock_type: str, a_code: str) -> Optional[Dict[str, Any]]:
    return premium_history_summaries(stock_type, [a_code]).get(a_code)


def premium_history_summaries(stock_type: str, codes: List[str]) -> Dict[str, Dict[str, Any]]:
    return db.load_premium_summaries(stock_type, codes)


def _fetch_price_series(code: str, market: str, days: int) -> List[Dict[str, Any]]:
    cutoff = db.cutoff_date(days)
    result: List[Dict[str, Any]] = []
    start_date = cutoff.replace("-", "")
    end_date = datetime.now().strftime("%Y%m%d")

    try:
        if market in {"sh", "sz"}:
            # A 股历史分位优先使用后复权收盘价，减少分红送转对长期百分位的扭曲
            df = ak.stock_zh_a_hist(symbol=str(code), period="daily", start_date=start_date, end_date=end_date, adjust="hfq")
            date_col = "date"
            close_col = "close"
        elif market == "hk":
            df = ak.stock_hk_daily(symbol=str(code).zfill(5))
            date_col = "date"
            close_col = "close"
        elif market == "us":
            df = ak.stock_us_daily(symbol=str(code).upper())
            date_col = "date"
            close_col = "close"
        elif market in {"shb", "szb"}:
            symbol = f"{market[:2]}{code}"
            df = ak.stock_zh_b_daily(symbol=symbol)
            date_col = "date"
            close_col = "close"
        else:
            raise PremiumDataError(f"Unsupported market: {market}")
    except Exception as exc:
        raise PremiumDataError(f"AkShare daily request failed ({market}{code}): {exc}") from exc

    if df is None or df.empty:
        raise PremiumDataError(f"AkShare daily has no usable rows ({market}{code})")

    for _, row in df.iterrows():
        date = str(row[date_col])[:10]
        if date < cutoff:
            continue
        try:
            close_price = float(row[close_col])
        except (TypeError, ValueError):
            continue
        if close_price <= 0:
            continue
        result.append({"date": date, "price": close_price})

    result.sort(key=lambda x: x["date"])
    if not result:
        raise PremiumDataError(f"No price rows in range ({market}{code}, days={days})")
    return result


def _fetch_fx_series(currency: str, days: int) -> List[Dict[str, Any]]:
    cutoff = db.cutoff_date(days)
    result: List[Dict[str, Any]] = []
    if currency not in {"HKD", "USD"}:
        raise PremiumDataError(f"Unsupported FX currency: {currency}")

    start_date = cutoff
    end_date = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.frankfurter.app/{start_date}..{end_date}"
    try:
        response = requests.get(url, params={"from": currency, "to": "CNY"}, timeout=20, headers=REQUEST_HEADERS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise PremiumDataError(f"Historical FX request failed ({currency}): {exc}") from exc
    except ValueError as exc:
        raise PremiumDataError(f"Historical FX parse failed ({currency})") from exc

    rates = payload.get("rates") or {}
    for date, value in rates.items():
        if date < cutoff:
            continue
        try:
            close_rate = float((value or {}).get("CNY"))
        except (TypeError, ValueError):
            continue
        if close_rate <= 0:
            continue
        result.append({"date": str(date), "rate": close_rate})

    result.sort(key=lambda x: x["date"])
    if not result:
        raise PremiumDataError(f"No FX rows in range ({currency}, days={days})")
    return result


def _carry_forward_rate(target_date: str, sorted_rates: List[Dict[str, Any]], idx: int, current_rate: Optional[float]) -> tuple[Optional[float], int]:
    i = idx
    rate = current_rate
    while i < len(sorted_rates) and str(sorted_rates[i]["date"]) <= target_date:
        rate = float(sorted_rates[i]["rate"])
        i += 1
    return rate, i


def _build_premium_rows(
    stock_type: str,
    a_code: str,
    pair_code: str,
    pair_market: str,
    currency: str,
    a_prices: List[Dict[str, Any]],
    pair_prices: List[Dict[str, Any]],
    fx_rates: List[Dict[str, Any]],
    compare_ratio: float = 1.0,
) -> List[Dict[str, Any]]:
    a_map = {str(item["date"]): float(item["price"]) for item in a_prices}
    p_map = {str(item["date"]): float(item["price"]) for item in pair_prices}
    common_dates = sorted(set(a_map.keys()) & set(p_map.keys()))

    rows: List[Dict[str, Any]] = []
    rate_idx = 0
    fx_rate: Optional[float] = None

    for date in common_dates:
        fx_rate, rate_idx = _carry_forward_rate(date, fx_rates, rate_idx, fx_rate)
        if fx_rate is None or fx_rate <= 0:
            continue

        a_price = a_map.get(date)
        pair_price = p_map.get(date)
        if a_price is None or pair_price is None or a_price <= 0:
            continue

        pair_price_cny = pair_price * fx_rate * compare_ratio
        premium = (pair_price_cny / a_price - 1) * 100

        rows.append(
            {
                "type": stock_type,
                "aCode": a_code,
                "pairCode": pair_code,
                "date": date,
                "aPrice": round(a_price, 4),
                "pairPrice": round(pair_price, 4),
                "pairPriceCny": round(pair_price_cny, 4),
                "exchangeRate": round(fx_rate, 6),
                "premium": round(premium, 4),
                "currency": currency,
                "pairMarket": pair_market,
            }
        )

    return rows


def sync_history_for_code(
    stock_type: str,
    a_code: str,
    days: int = WINDOW_DAYS,
    force_full: bool = False,
    pair_data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    stock_type = str(stock_type or "").upper()
    a_code = str(a_code or "").strip()

    if stock_type not in {"AH", "AB"}:
        return {"success": False, "error": f"Unsupported type: {stock_type}"}
    if not a_code:
        return {"success": False, "error": "a_code is required"}

    db.init_db()

    if pair_data is None:
        try:
            pair_data = load_dynamic_pairs(force_refresh=False)
        except Exception as exc:
            return {"success": False, "error": f"Failed to load dynamic pairs: {exc}"}

    compare_ratio = 1.0
    if stock_type == "AH":
        pair = find_ah_pair(a_code, pair_data.get("ah", []))
        if not pair:
            return {"success": False, "error": f"AH pair not found for aCode={a_code}"}
        pair_code = str(pair["hCode"])
        pair_market = "hk"
        currency = "HKD"
        a_market = str(pair.get("aMarket") or ("sh" if a_code.startswith("6") else "sz"))
    else:
        pair = find_ab_pair(a_code, pair_data.get("ab", []))
        if not pair:
            return {"success": False, "error": f"AB pair not found for aCode={a_code}"}
        pair_code = str(pair["bCode"])
        pair_market = str(pair.get("bMarket") or ("sh" if pair_code.startswith("9") else "sz"))
        currency = str(pair.get("currency") or ("USD" if pair_market == "sh" else "HKD"))
        a_market = str(pair.get("aMarket") or ("sh" if a_code.startswith("6") else "sz"))
        pair_market = f"{pair_market}b"

    existing = db.load_premium_history(stock_type, a_code, WINDOW_DAYS)
    if existing:
        existing_pair = str(existing[-1].get("pairCode") or "")
        if existing_pair and existing_pair != pair_code:
            db.delete_premium_history(stock_type, a_code)
            existing = []

    fetch_days = max(days, WINDOW_DAYS) + 30
    if existing and not force_full:
        last_date = db.get_last_trade_date(stock_type, a_code)
        if last_date:
            lag_days = max(0, (datetime.now() - _parse_date(last_date)).days)
            fetch_days = max(120, lag_days + 45)
    else:
        db.delete_premium_history(stock_type, a_code)

    try:
        a_prices = _fetch_price_series(a_code, a_market, fetch_days)
        pair_prices = _fetch_price_series(pair_code, pair_market, fetch_days)
    except PremiumDataError as exc:
        return {"success": False, "error": str(exc)}

    cached_fx = db.load_fx_chain(currency, db.cutoff_date(fetch_days))
    fx_rows = [{"date": key, "rate": value} for key, value in sorted(cached_fx.items())]
    if not fx_rows or force_full:
        try:
            fx_rows = _fetch_fx_series(currency, fetch_days)
        except PremiumDataError as exc:
            return {"success": False, "error": str(exc)}
        db.upsert_fx_rows(currency, fx_rows)

    premium_rows = _build_premium_rows(
        stock_type,
        a_code,
        pair_code,
        pair_market,
        currency,
        a_prices,
        pair_prices,
        fx_rows,
        compare_ratio=compare_ratio,
    )
    db.upsert_premium_rows(premium_rows)
    db.prune_old_rows(WINDOW_DAYS)

    history = db.load_premium_history(stock_type, a_code, max(1, days))
    if not history:
        return {"success": False, "error": f"No cached premium history for {stock_type}:{a_code}"}

    payload = {
        "aCode": a_code,
        "type": stock_type,
        "history": history,
        "count": len(history),
        "startDate": history[0]["date"],
        "endDate": history[-1]["date"],
        "source": "sqlite_cache",
        "updateTime": datetime.now().isoformat(),
        "currency": currency,
    }

    if stock_type == "AH":
        payload["hCode"] = pair_code
    else:
        payload["bCode"] = pair_code
        payload["market"] = str(pair.get("market") or "")

    return {"success": True, "data": payload}


def load_cached_history_for_code(stock_type: str, a_code: str, days: int = WINDOW_DAYS) -> Dict[str, Any]:
    stock_type = str(stock_type or "").upper()
    a_code = str(a_code or "").strip()
    if stock_type not in {"AH", "AB"}:
        return {"success": False, "error": f"Unsupported type: {stock_type}"}
    if not a_code:
        return {"success": False, "error": "a_code is required"}

    db.init_db()
    history = db.load_premium_history(stock_type, a_code, max(1, days))
    if not history:
        return {"success": False, "error": f"No cached premium history for {stock_type}:{a_code}"}

    payload = {
        "aCode": a_code,
        "type": stock_type,
        "history": history,
        "count": len(history),
        "startDate": history[0]["date"],
        "endDate": history[-1]["date"],
        "source": "sqlite_cache",
        "updateTime": datetime.now().isoformat(),
        "currency": history[-1].get("currency"),
    }
    if stock_type == "AH":
        payload["hCode"] = history[-1].get("pairCode")
    else:
        payload["bCode"] = history[-1].get("pairCode")

    return {"success": True, "data": payload}


def ensure_history_for_code(stock_type: str, a_code: str, days: int = WINDOW_DAYS, force_full: bool = False) -> Dict[str, Any]:
    stock_type = str(stock_type or "").upper()
    a_code = str(a_code or "").strip()

    if stock_type not in {"AH", "AB"}:
        return {"success": False, "error": f"Unsupported type: {stock_type}"}
    if not a_code:
        return {"success": False, "error": "a_code is required"}

    db.init_db()

    try:
        pair_data = load_dynamic_pairs(force_refresh=False)
    except Exception as exc:
        return {"success": False, "error": f"Failed to load dynamic pairs: {exc}"}
    pair = resolve_pair_for_code(stock_type, a_code, pair_data)
    if not pair:
        return {"success": False, "error": f"{stock_type} pair not found for aCode={a_code}"}

    market_dates = load_market_latest_dates(pair_data)
    expected_end_date = expected_end_date_for_pair(stock_type, pair, market_dates)
    pair_code = get_pair_code(stock_type, pair)
    cached_result = load_cached_history_for_code(stock_type, a_code, max(1, days))
    summary = premium_history_summary(stock_type, a_code)

    degraded_summary = summary_requires_full_backfill(summary)
    if force_full or not cached_result.get("success") or history_needs_sync(
        stock_type,
        a_code,
        pair_code=pair_code,
        expected_end_date=expected_end_date,
        summary=summary,
    ):
        return sync_history_for_code(
            stock_type,
            a_code,
            days=days,
            force_full=(force_full or degraded_summary),
            pair_data=pair_data,
        )

    return cached_result


def main() -> None:
    if len(sys.argv) < 3:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "usage: python fetch_historical_premium.py <AH|AB> <code> [days] [--force-full]",
                },
                ensure_ascii=False,
            )
        )
        return

    stock_type = str(sys.argv[1] or "").upper()
    stock_code = str(sys.argv[2] or "").strip()

    force_full = any(str(arg).strip().lower() == "--force-full" for arg in sys.argv[3:])

    days = WINDOW_DAYS
    for arg in sys.argv[3:]:
        if str(arg).startswith("--"):
            continue
        try:
            days = int(arg)
            break
        except Exception:
            pass

    if days <= 0:
        print(json.dumps({"success": False, "error": "days must be > 0"}, ensure_ascii=False))
        return

    result = ensure_history_for_code(stock_type, stock_code, days=days, force_full=force_full)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

