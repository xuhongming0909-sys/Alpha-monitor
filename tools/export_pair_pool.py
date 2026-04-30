#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Export active AH/AB pair universes from local SQLite and audit AH completeness."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from market_pairs import DB_PATH, DATA_DIR, fetch_ah_pairs, load_dynamic_pairs

AH_JSON_PATH = DATA_DIR / "AH配对导出.json"
AH_TSV_PATH = DATA_DIR / "AH配对导出.tsv"
AB_JSON_PATH = DATA_DIR / "AB配对导出.json"
AB_TSV_PATH = DATA_DIR / "AB配对导出.tsv"
AH_AUDIT_PATH = DATA_DIR / "AH配对审计.json"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _query_pairs(stock_type: str) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT
                type,
                a_code,
                a_name,
                a_market,
                pair_code,
                pair_name,
                pair_market,
                market_label,
                currency,
                first_seen,
                last_seen,
                updated_at,
                source
            FROM pair_master
            WHERE type = ? AND is_active = 1
            ORDER BY a_code ASC
            """,
            (stock_type,),
        ).fetchall()

    if stock_type == "AH":
        return [
            {
                "type": "AH",
                "aCode": row["a_code"],
                "aName": row["a_name"] or "",
                "aMarket": row["a_market"] or "",
                "hCode": row["pair_code"],
                "hName": row["pair_name"] or "",
                "hMarket": row["pair_market"] or "",
                "currency": row["currency"] or "HKD",
                "firstSeen": row["first_seen"],
                "lastSeen": row["last_seen"],
                "updatedAt": row["updated_at"],
                "source": row["source"] or "",
            }
            for row in rows
        ]

    return [
        {
            "type": "AB",
            "aCode": row["a_code"],
            "aName": row["a_name"] or "",
            "aMarket": row["a_market"] or "",
            "bCode": row["pair_code"],
            "bName": row["pair_name"] or "",
            "bMarket": row["pair_market"] or "",
            "market": row["market_label"] or "",
            "currency": row["currency"] or "",
            "firstSeen": row["first_seen"],
            "lastSeen": row["last_seen"],
            "updatedAt": row["updated_at"],
            "source": row["source"] or "",
        }
        for row in rows
    ]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_tsv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _audit_ah(rows: list[dict[str, Any]]) -> dict[str, Any]:
    # Use the same live pair source logic as market sync to avoid
    # schema drift from third-party dataframe column changes.
    existing_by_h = {str(item.get("hCode") or ""): item for item in rows}
    source_rows = fetch_ah_pairs(existing_by_h)
    source_rows = [
        {
            "aCode": str(item.get("aCode") or "").strip(),
            "aName": str(item.get("aName") or "").strip(),
            "hCode": str(item.get("hCode") or "").strip().zfill(5),
            "hName": str(item.get("hName") or "").strip(),
        }
        for item in source_rows
        if str(item.get("aCode") or "").strip() and str(item.get("hCode") or "").strip()
    ]

    db_keys = {(item["aCode"], item["hCode"]) for item in rows}
    source_keys = {(item["aCode"], item["hCode"]) for item in source_rows}
    missing = sorted(
        [item for item in source_rows if (item["aCode"], item["hCode"]) not in db_keys],
        key=lambda item: (item["aCode"], item["hCode"]),
    )
    extra = sorted(
        [item for item in rows if (item["aCode"], item["hCode"]) not in source_keys],
        key=lambda item: (item["aCode"], item["hCode"]),
    )

    return {
        "success": len(missing) == 0,
        "source": "tencent+akshare.fetch_ah_pairs",
        "sourceTotal": len(source_rows),
        "dbTotal": len(rows),
        "missingInDb": missing,
        "extraInDb": extra,
        "checkedAt": datetime.now().isoformat(),
    }


def export_pairs(force_refresh: bool = False) -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    pair_data = load_dynamic_pairs(force_refresh=force_refresh)

    ah_rows = _query_pairs("AH")
    ab_rows = _query_pairs("AB")

    ah_payload = {
        "success": True,
        "type": "AH",
        "count": len(ah_rows),
        "source": pair_data.get("source"),
        "updateTime": datetime.now().isoformat(),
        "data": ah_rows,
    }
    ab_payload = {
        "success": True,
        "type": "AB",
        "count": len(ab_rows),
        "source": pair_data.get("source"),
        "updateTime": datetime.now().isoformat(),
        "data": ab_rows,
    }
    ah_audit = _audit_ah(ah_rows)

    _write_json(AH_JSON_PATH, ah_payload)
    _write_json(AB_JSON_PATH, ab_payload)
    _write_json(AH_AUDIT_PATH, ah_audit)

    _write_tsv(
        AH_TSV_PATH,
        ah_rows,
        ["aCode", "aName", "aMarket", "hCode", "hName", "hMarket", "currency", "firstSeen", "lastSeen", "updatedAt", "source"],
    )
    _write_tsv(
        AB_TSV_PATH,
        ab_rows,
        ["aCode", "aName", "aMarket", "bCode", "bName", "bMarket", "market", "currency", "firstSeen", "lastSeen", "updatedAt", "source"],
    )

    return {
        "success": True,
        "refresh": bool(force_refresh),
        "pairSource": pair_data.get("source"),
        "ahCount": len(ah_rows),
        "abCount": len(ab_rows),
        "ahAudit": {
            "sourceTotal": ah_audit["sourceTotal"],
            "dbTotal": ah_audit["dbTotal"],
            "missingInDb": len(ah_audit["missingInDb"]),
            "extraInDb": len(ah_audit["extraInDb"]),
        },
        "files": {
            "ahJson": str(AH_JSON_PATH),
            "ahTsv": str(AH_TSV_PATH),
            "abJson": str(AB_JSON_PATH),
            "abTsv": str(AB_TSV_PATH),
            "ahAudit": str(AH_AUDIT_PATH),
        },
        "updateTime": datetime.now().isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    result = export_pairs(force_refresh=bool(args.refresh))
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

