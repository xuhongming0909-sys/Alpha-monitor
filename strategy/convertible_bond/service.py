"""Convertible-bond strategy response service."""

from __future__ import annotations

from shared.models.service_result import build_success


def build_convertible_bond_response(fetch_payload: dict, bus_records: list[dict]) -> dict:
    """Build the outward-facing convertible-bond payload from normalized bus records."""

    if not fetch_payload or fetch_payload.get("success") is False:
        return fetch_payload

    rows = [dict(record.get("raw") or {}) for record in bus_records if record.get("status") == "ok"]
    return build_success(
        rows,
        updateTime=fetch_payload.get("updateTime"),
        source=fetch_payload.get("source"),
        tradeDate=fetch_payload.get("tradeDate"),
        syncStats=fetch_payload.get("syncStats"),
        stats=fetch_payload.get("stats"),
        treasuryYield10y=fetch_payload.get("treasuryYield10y"),
        treasuryYield10yDate=fetch_payload.get("treasuryYield10yDate"),
        treasuryYield10ySource=fetch_payload.get("treasuryYield10ySource"),
        cookieConfigured=fetch_payload.get("cookieConfigured"),
    )
