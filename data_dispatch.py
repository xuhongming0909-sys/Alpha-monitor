from __future__ import annotations

import json
import sys

from data_fetch.ab_premium.fetcher import fetch_ab_snapshot
from data_fetch.ab_premium.normalizer import normalize_ab_snapshot
from data_fetch.ah_premium.fetcher import fetch_ah_snapshot
from data_fetch.ah_premium.normalizer import normalize_ah_snapshot
from data_fetch.convertible_bond.fetcher import fetch_convertible_bond_snapshot
from data_fetch.convertible_bond.history_sync import sync_convertible_bond_stock_history
from data_fetch.convertible_bond.normalizer import normalize_convertible_bond_snapshot
from data_fetch.cb_rights_issue.fetcher import (
    fetch_cb_rights_issue_snapshot,
    sync_cb_rights_issue_stock_history_snapshot,
)
from data_fetch.cb_rights_issue.normalizer import normalize_cb_rights_issue_snapshot
from data_fetch.dividend.fetcher import fetch_dividend_snapshot, fetch_upcoming_dividend_snapshot
from data_fetch.event_arbitrage.fetcher import fetch_event_arbitrage_snapshot
from data_fetch.event_arbitrage.normalizer import normalize_event_arbitrage_snapshot
from data_fetch.exchange_rate.fetcher import fetch_exchange_rate_snapshot
from data_fetch.exchange_rate.normalizer import normalize_exchange_rate_snapshot
from data_fetch.lof_arbitrage.fetcher import fetch_lof_arbitrage_snapshot
from data_fetch.lof_arbitrage.normalizer import normalize_lof_arbitrage_snapshot
from data_fetch.merger.fetcher import fetch_merger_snapshot
from data_fetch.merger.normalizer import normalize_merger_snapshot
from data_fetch.subscription.fetcher import fetch_bond_subscription_snapshot, fetch_ipo_snapshot
from data_fetch.subscription.normalizer import normalize_bond_subscription_snapshot, normalize_ipo_snapshot
from shared.market_service import get_single_price, search_stock
from shared.models.service_result import build_error as shared_build_error, build_success as shared_build_success
from shared.paths.tool_paths import ensure_scripts_on_path
from strategy.ab_premium.service import build_ab_response
from strategy.ah_premium.service import build_ah_response
from strategy.convertible_bond.service import build_convertible_bond_response
from strategy.cb_rights_issue.service import build_cb_rights_issue_response
from strategy.dividend.service import build_dividend_response
from strategy.event_arbitrage.service import build_event_arbitrage_response
from strategy.lof_arbitrage.service import build_lof_arbitrage_response
from strategy.merger.service import build_merger_response
from strategy.subscription.service import build_subscription_response

ensure_scripts_on_path()
from fetch_historical_premium import ensure_history_for_code


def build_success(data, **extra):
    payload = shared_build_success(data, **extra)
    payload.pop("error", None)
    return payload


def build_error(message, data=None, **extra):
    return shared_build_error(message, [] if data is None else data, **extra)


def dump(payload):
    text = json.dumps(payload, ensure_ascii=False, default=str)
    try:
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
    except Exception:
        print(text)


def action_ah(force_pairs: bool = False) -> dict:
    payload = fetch_ah_snapshot(force_pairs=force_pairs)
    records = normalize_ah_snapshot(payload)
    return build_ah_response(payload, records)


def action_ab(force_pairs: bool = False) -> dict:
    payload = fetch_ab_snapshot(force_pairs=force_pairs)
    records = normalize_ab_snapshot(payload)
    return build_ab_response(payload, records)


def action_exchange_rate() -> dict:
    payload = fetch_exchange_rate_snapshot()
    normalize_exchange_rate_snapshot(payload)
    return payload


def action_ipo() -> dict:
    payload = fetch_ipo_snapshot()
    records = normalize_ipo_snapshot(payload)
    return build_subscription_response(payload, records)


def action_bonds() -> dict:
    payload = fetch_bond_subscription_snapshot()
    records = normalize_bond_subscription_snapshot(payload)
    return build_subscription_response(payload, records)


def action_convertible_bond() -> dict:
    payload = fetch_convertible_bond_snapshot()
    records = normalize_convertible_bond_snapshot(payload)
    return build_convertible_bond_response(payload, records)


def action_sync_cb_stock_history(force_full: bool = False) -> dict:
    return sync_convertible_bond_stock_history(force_full=force_full)


def action_cb_rights_issue() -> dict:
    payload = fetch_cb_rights_issue_snapshot()
    records = normalize_cb_rights_issue_snapshot(payload)
    return build_cb_rights_issue_response(payload, records)


def action_lof_arbitrage() -> dict:
    payload = fetch_lof_arbitrage_snapshot()
    records = normalize_lof_arbitrage_snapshot(payload)
    return build_lof_arbitrage_response(payload, records)


def action_sync_cb_rights_issue_stock_history(force_full: bool = False) -> dict:
    return sync_cb_rights_issue_stock_history_snapshot(force_full=force_full)


def action_merger() -> dict:
    payload = fetch_merger_snapshot()
    records = normalize_merger_snapshot(payload)
    return build_merger_response(payload, records)


def action_event_arbitrage() -> dict:
    payload = fetch_event_arbitrage_snapshot()
    records = normalize_event_arbitrage_snapshot(payload)
    return build_event_arbitrage_response(payload, records)


def action_dividend(code: str) -> dict:
    payload = fetch_dividend_snapshot(code)
    return build_dividend_response(payload)


def action_dividend_upcoming(days: int = 3) -> dict:
    payload = fetch_upcoming_dividend_snapshot(days)
    return build_dividend_response(payload)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        dump(build_error("缺少 action"))
        sys.exit(1)

    action = str(args[0]).strip().lower()

    try:
        if action == "ah":
            dump(action_ah(force_pairs="--force-pairs" in args[1:]))
        elif action == "ab":
            dump(action_ab(force_pairs="--force-pairs" in args[1:]))
        elif action == "exchange-rate":
            dump(action_exchange_rate())
        elif action == "search":
            dump(search_stock(str(args[1] if len(args) > 1 else "").strip(), int(args[2]) if len(args) > 2 else 20))
        elif action == "price":
            dump(
                get_single_price(
                    str(args[1] if len(args) > 1 else "").strip(),
                    str(args[2] if len(args) > 2 else "a").strip().lower(),
                    str(args[3] if len(args) > 3 else "sh").strip().lower(),
                )
            )
        elif action == "ipo":
            dump(action_ipo())
        elif action == "bonds":
            dump(action_bonds())
        elif action == "cb-arb":
            dump(action_convertible_bond())
        elif action == "sync-cb-stock-history":
            dump(action_sync_cb_stock_history(force_full="--force-full" in args[1:]))
        elif action == "cb-rights-issue":
            dump(action_cb_rights_issue())
        elif action == "lof-arbitrage":
            dump(action_lof_arbitrage())
        elif action == "sync-cb-rights-issue-stock-history":
            dump(action_sync_cb_rights_issue_stock_history(force_full="--force-full" in args[1:]))
        elif action == "merger":
            dump(action_merger())
        elif action == "event-arbitrage":
            dump(action_event_arbitrage())
        elif action == "historical-premium":
            dump(
                ensure_history_for_code(
                    str(args[1] if len(args) > 1 else "AH").upper(),
                    str(args[2] if len(args) > 2 else "").strip(),
                    days=int(args[3]) if len(args) > 3 else 1825,
                    force_full="--force-full" in args[4:],
                )
            )
        elif action == "dividend" and len(args) > 1:
            dump(action_dividend(str(args[1]).strip()))
        elif action == "dividend-upcoming":
            dump(action_dividend_upcoming(int(args[1]) if len(args) > 1 else 3))
        else:
            dump(build_error(f"未知 action: {action}"))
            sys.exit(1)
    except Exception as exc:
        dump(build_error(str(exc)))
        sys.exit(1)


if __name__ == "__main__":
    main()
