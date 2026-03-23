#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Rebuild or update 5-year AH/AB premium history database."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import premium_history_db as db
from fetch_historical_premium import (
    WINDOW_DAYS,
    expected_end_date_for_pair,
    history_needs_sync,
    load_market_latest_dates,
    premium_history_summaries,
    sync_history_for_code,
)
from market_pairs import load_dynamic_pairs


def _is_tolerated_update_error(message: object) -> bool:
    text = str(message or "").strip()
    if not text:
        return False

    # Incremental sync should stay available when only a few symbols hit
    # upstream provider edge cases and existing local cache can still serve.
    tolerated_patterns = (
        "AkShare daily request failed",
        "AkShare daily has no usable rows",
        "No price rows in range",
    )
    return any(pattern in text for pattern in tolerated_patterns)


def _select_pairs(pair_data: dict, stock_type: str, resume_from: str, limit: int | None) -> list[tuple[str, dict]]:
    selected: list[tuple[str, dict]] = []
    normalized_type = str(stock_type or "ALL").upper()
    resume_code = str(resume_from or "").strip()

    if normalized_type in {"ALL", "AH"}:
        for item in pair_data.get("ah", []):
            a_code = str(item.get("aCode") or "").strip()
            if not a_code:
                continue
            if resume_code and a_code < resume_code:
                continue
            selected.append(("AH", item))

    if normalized_type in {"ALL", "AB"}:
        for item in pair_data.get("ab", []):
            a_code = str(item.get("aCode") or "").strip()
            if not a_code:
                continue
            if resume_code and a_code < resume_code:
                continue
            selected.append(("AB", item))

    selected.sort(key=lambda item: (item[0], str(item[1].get("aCode") or "")))
    if isinstance(limit, int) and limit > 0:
        selected = selected[:limit]
    return selected


def run(mode: str, stock_type: str = "ALL", limit: int | None = None, resume_from: str = "", only_missing: bool = False) -> dict:
    db.init_db()
    db.prune_old_rows(WINDOW_DAYS)

    pair_data = load_dynamic_pairs(force_refresh=True)
    market_dates = load_market_latest_dates(pair_data)
    selected_pairs = _select_pairs(pair_data, stock_type, resume_from, limit)

    force_full = mode == "rebuild"

    total = len(selected_pairs)
    done = 0
    ok = 0
    skipped = 0
    failed = []
    warnings = []
    summary_cache = {
        "AH": premium_history_summaries("AH", [str(item.get("aCode") or "").strip() for _, item in selected_pairs if _ == "AH"]),
        "AB": premium_history_summaries("AB", [str(item.get("aCode") or "").strip() for _, item in selected_pairs if _ == "AB"]),
    }

    for index, (current_type, item) in enumerate(selected_pairs, start=1):
        a_code = str(item.get("aCode") or "")
        if not a_code:
            continue
        current_pair_code = str(item.get("hCode") or item.get("bCode") or "").strip()
        expected_end_date = expected_end_date_for_pair(current_type, item, market_dates)
        summary = summary_cache[current_type].get(a_code)

        if mode == "update":
            if only_missing and summary:
                skipped += 1
                continue
            if not only_missing and not history_needs_sync(
                current_type,
                a_code,
                pair_code=current_pair_code,
                expected_end_date=expected_end_date,
                summary=summary,
            ):
                skipped += 1
                continue

        print(f"[{index}/{total}] syncing {current_type}:{a_code}", file=sys.stderr, flush=True)
        result = sync_history_for_code(
            current_type,
            a_code,
            days=WINDOW_DAYS,
            force_full=force_full,
            pair_data=pair_data,
        )
        done += 1
        if result.get("success"):
            ok += 1
        elif mode == "update" and _is_tolerated_update_error(result.get("error")):
            warnings.append({"type": current_type, "code": a_code, "error": result.get("error")})
        else:
            failed.append({"type": current_type, "code": a_code, "error": result.get("error")})

    return {
        "success": len(failed) == 0,
        "mode": mode,
        "stockType": str(stock_type or "ALL").upper(),
        "total": total,
        "processed": done,
        "skipped": skipped,
        "successCount": ok,
        "warningCount": len(warnings),
        "failedCount": len(failed),
        "warnings": warnings[:30],
        "failed": failed[:30],
        "marketDates": market_dates,
        "updateTime": datetime.now().isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["rebuild", "update"], default="update")
    parser.add_argument("--type", choices=["ALL", "AH", "AB"], default="ALL")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--resume-from", default="")
    parser.add_argument("--only-missing", action="store_true")
    args = parser.parse_args()

    result = run(
        args.mode,
        stock_type=args.type,
        limit=args.limit if args.limit > 0 else None,
        resume_from=args.resume_from,
        only_missing=bool(args.only_missing),
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

