# AI-SUMMARY: AH/AB 动态配对库：配对发现 + SQLite 持久化 + 每日对账
# 对应 INDEX.md §9 文件摘要索引

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dynamic AH/AB pair discovery with local SQLite persistence and daily reconciliation (no Eastmoney)."""

from __future__ import annotations

import json
import re
import sqlite3
import time
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import akshare as ak
import requests
from shared.paths.db_paths import ROOT_DATA_DIR, STATIC_DATA_DIR, ensure_dir, shared_db_path

DATA_DIR = ROOT_DATA_DIR
DB_PATH = shared_db_path("market_pairs.db")
AH_CACHE_PATHS = [
    STATIC_DATA_DIR / "ah_pair_export.json",
]

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://gu.qq.com/",
}

AB_SH_FIXED_MAP: Dict[str, Dict[str, str]] = {
    "900901": {"aCode": "600602", "aName": "浜戣禌鏅鸿仈"},
    "900902": {"aCode": "600604", "aName": "甯傚寳楂樻柊"},
    "900903": {"aCode": "600611", "aName": ""},
    "900904": {"aCode": "600613", "aName": "绁炲鍒惰嵂"},
    "900905": {"aCode": "600612", "aName": ""},
    "900906": {"aCode": "600610", "aName": ""},
    "900908": {"aCode": "600618", "aName": "姘⒈鍖栧伐"},
    "900909": {"aCode": "600623", "aName": "鍗庤皧闆嗗洟"},
    "900910": {"aCode": "600619", "aName": "娴风珛鑲′唤"},
    "900911": {"aCode": "600639", "aName": "娴︿笢閲戞ˉ"},
    "900912": {"aCode": "600648", "aName": ""},
    "900913": {"aCode": "600617", "aName": "鍥芥柊鑳芥簮"},
    "900914": {"aCode": "600650", "aName": "閿︽睙鍦ㄧ嚎"},
    "900915": {"aCode": "600818", "aName": "涓矾鑲′唤"},
    "900916": {"aCode": "600679", "aName": "涓婃捣鍑ゅ嚢"},
    "900917": {"aCode": "600851", "aName": "娴锋鑲′唤"},
    "900918": {"aCode": "600819", "aName": ""},
    "900920": {"aCode": "600841", "aName": "鍔ㄥ姏鏂扮"},
    "900921": {"aCode": "600844", "aName": "涓瑰寲绉戞妧"},
    "900922": {"aCode": "600689", "aName": "涓婃捣涓夋瘺"},
    "900923": {"aCode": "600827", "aName": "鐧捐仈鑲′唤"},
    "900924": {"aCode": "600843", "aName": "涓婂伐鐢宠礉"},
    "900925": {"aCode": "600835", "aName": "涓婃捣鏈虹數"},
    "900926": {"aCode": "600845", "aName": "瀹濅俊杞欢"},
    "900927": {"aCode": "600822", "aName": "涓婃捣鐗╄锤"},
    "900928": {"aCode": "600848", "aName": "涓婃捣涓存腐"},
    "900932": {"aCode": "600663", "aName": ""},
    "900934": {"aCode": "600754", "aName": "閿︽睙閰掑簵"},
    "900936": {"aCode": "600295", "aName": "閯傚皵澶氭柉"},
    "900937": {"aCode": "600726", "aName": "鍗庣數鑳芥簮"},
    "900938": {"aCode": "600751", "aName": "娴疯埅绉戞妧"},
    "900940": {"aCode": "600094", "aName": ""},
    "900941": {"aCode": "600776", "aName": "涓滄柟閫氫俊"},
    "900942": {"aCode": "600054", "aName": "榛勫北鏃呮父"},
    "900943": {"aCode": "600272", "aName": "寮€寮€瀹炰笟"},
    "900945": {"aCode": "600221", "aName": "娴疯埅鎺ц偂"},
    "900946": {"aCode": "600698", "aName": "婀栧崡澶╅泚"},
    "900947": {"aCode": "600320", "aName": "鎸崕閲嶅伐"},
}

AH_MANUAL_MAP: Dict[str, Dict[str, str]] = {
    "02039": {"aCode": "000039", "aName": "涓泦闆嗗洟"},
    "01839": {"aCode": "301039", "aName": "涓泦杞﹁締"},
    "01375": {"aCode": "601375", "aName": "涓師璇佸埜"},
    "00338": {"aCode": "600688", "aName": "涓婃捣鐭冲寲"},
    "01528": {"aCode": "601828", "aName": ""},
    "03996": {"aCode": "601868", "aName": "涓浗鑳藉缓"},
    "01033": {"aCode": "600871", "aName": "鐭冲寲娌规湇"},
    "00588": {"aCode": "601588", "aName": "鍖楄景瀹炰笟"},
    "06869": {"aCode": "601869", "aName": "闀块鍏夌氦"},
    "01347": {"aCode": "688347", "aName": "鍗庤櫣鍏徃"},
    "02315": {"aCode": "688796", "aName": "鐧惧ゥ璧涘浘"},
    "02768": {"aCode": "002768", "aName": "鍥芥仼鑲′唤"},
    "01385": {"aCode": "688385", "aName": "澶嶆棪寰數"},
    "06185": {"aCode": "688185", "aName": ""},
    "00883": {"aCode": "600938", "aName": "涓浗娴锋补"},
    "01513": {"aCode": "000513", "aName": "涓界彔闆嗗洟"},
    "06826": {"aCode": "688366", "aName": "鏄婃捣鐢熺"},
    "02218": {"aCode": "605198", "aName": ""},
    "00995": {"aCode": "600012", "aName": ""},
    "06066": {"aCode": "601066", "aName": "涓俊寤烘姇"},
    "00177": {"aCode": "600377", "aName": ""},
    "06865": {"aCode": "601865", "aName": ""},
    "02883": {"aCode": "601808", "aName": "涓捣娌规湇"},
    "00038": {"aCode": "601038", "aName": ""},
    "00548": {"aCode": "600548", "aName": ""},
    "00719": {"aCode": "000756", "aName": "鏂板崕鍒惰嵂"},
    "03618": {"aCode": "601077", "aName": "娓濆啘鍟嗚"},
    "01339": {"aCode": "601319", "aName": "涓浗浜轰繚"},
    "00902": {"aCode": "600011", "aName": "鍗庤兘鍥介檯"},
    "00107": {"aCode": "601107", "aName": "鍥涘窛鎴愭笣"},
    "01330": {"aCode": "601330", "aName": "缁胯壊鍔ㄥ姏"},
    "00553": {"aCode": "600775", "aName": "鍗椾含鐔婄尗"},
    "00187": {"aCode": "600860", "aName": "浜煄鑲′唤"},
    "01800": {"aCode": "601800", "aName": "涓浗浜ゅ缓"},
    "00386": {"aCode": "600028", "aName": "涓浗鐭冲寲"},
    "01055": {"aCode": "600029", "aName": "鍗楁柟鑸┖"},
    "01071": {"aCode": "600027", "aName": "鍗庣數鍥介檯"},
    "01065": {"aCode": "600874", "aName": "鍒涗笟鐜繚"},
    "00956": {"aCode": "600956", "aName": "鏂板ぉ缁胯兘"},
    "00670": {"aCode": "600115", "aName": "涓浗涓滆埅"},
    "02202": {"aCode": "000002", "aName": "涓囩A"},
    "01816": {"aCode": "003816", "aName": "涓浗骞挎牳"},
    "06818": {"aCode": "601818", "aName": "鍏夊ぇ閾惰"},
    "00323": {"aCode": "600808", "aName": "椹挗鑲′唤"},
}


def now_iso() -> str:
    return datetime.now().isoformat()


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    return session


def _connect() -> sqlite3.Connection:
    ensure_dir(DB_PATH.parent)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_pair_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;

            CREATE TABLE IF NOT EXISTS pair_master (
                type TEXT NOT NULL,
                a_code TEXT NOT NULL,
                pair_code TEXT NOT NULL,
                a_name TEXT,
                pair_name TEXT,
                a_market TEXT,
                pair_market TEXT,
                market_label TEXT,
                currency TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                source TEXT,
                PRIMARY KEY (type, a_code, pair_code)
            );

            CREATE INDEX IF NOT EXISTS idx_pair_master_type_active
                ON pair_master(type, is_active);

            CREATE TABLE IF NOT EXISTS pair_sync_log (
                sync_date TEXT NOT NULL,
                type TEXT NOT NULL,
                total_active INTEGER NOT NULL,
                added_count INTEGER NOT NULL,
                removed_count INTEGER NOT NULL,
                updated_count INTEGER NOT NULL,
                source TEXT,
                sync_time TEXT NOT NULL,
                PRIMARY KEY (sync_date, type)
            );
            """
        )


def _normalize_text(value: str) -> str:
    text = str(value or "")
    text = text.replace("Ａ", "A").replace("Ｂ", "B")
    text = re.sub(r"[\s\u3000]", "", text)
    text = re.sub(r"[()（）\\-·•]", "", text)
    for token in ["股份有限公司", "有限责任公司", "有限公司", "股份", "集团", "控股", "B股", "A股", "B", "A", "H股", "H"]:
        text = text.replace(token, "")
    return text.upper().strip()


def _is_name_consistent(left: str, right: str) -> bool:
    left_norm = _normalize_text(left)
    right_norm = _normalize_text(right)
    if not left_norm or not right_norm:
        return True
    if left_norm == right_norm or left_norm in right_norm or right_norm in left_norm:
        return True
    return SequenceMatcher(None, left_norm, right_norm).ratio() >= 0.62


def _get_tencent_quotes(codes: List[str]) -> Dict[str, Dict[str, float]]:
    quote_map: Dict[str, Dict[str, float]] = {}
    if not codes:
        return quote_map

    with _session() as s:
        for i in range(0, len(codes), 100):
            batch = codes[i : i + 100]
            query = ",".join(batch)
            for _ in range(3):
                try:
                    resp = s.get(f"https://qt.gtimg.cn/q={query}", timeout=10)
                    text = resp.content.decode("gbk", errors="ignore")
                    break
                except Exception:
                    text = ""
                    time.sleep(0.3)
            if not text:
                continue

            for line in text.splitlines():
                m = re.match(r'v_([^=]+)="(.*)";?', line.strip())
                if not m:
                    continue
                code = m.group(1)
                parts = m.group(2).split("~")
                if len(parts) < 4:
                    continue
                try:
                    price = float(parts[3]) if parts[3] else 0.0
                except Exception:
                    price = 0.0
                if price <= 0:
                    continue
                quote_map[code] = {
                    "name": str(parts[1] if len(parts) > 1 else "").strip(),
                    "price": price,
                }

    return quote_map


def _get_fx_rates() -> Dict[str, float]:
    quotes = _get_tencent_quotes(["whHKDCNY", "whUSDCNY"])
    hkd = quotes.get("whHKDCNY", {}).get("price")
    usd = quotes.get("whUSDCNY", {}).get("price")
    if not (isinstance(hkd, (float, int)) and hkd > 0 and isinstance(usd, (float, int)) and usd > 0):
        raise RuntimeError("鏃犳硶鑾峰彇鑵捐exchange_rate")
    return {"HKD": float(hkd), "USD": float(usd)}


def _smartbox_search(keyword: str) -> List[dict]:
    q = str(keyword or "").strip()
    if not q:
        return []

    for _ in range(3):
        try:
            response = requests.get(
                "https://proxy.finance.qq.com/cgi/cgi-bin/smartbox/search",
                params={"stockFlag": 1, "fundFlag": 1, "app": "official_website", "query": q},
                timeout=8,
                headers=REQUEST_HEADERS,
            )
            payload = response.json()
            return payload.get("stock") or []
        except Exception:
            time.sleep(0.25)
    return []


def _candidate_a_codes(rows: List[dict]) -> List[Tuple[str, str]]:
    candidates: Dict[str, str] = {}
    for item in rows:
        code = str(item.get("code") or "").strip().lower()
        name = str(item.get("name") or "").strip()
        if code.startswith("sh") and code[2:].isdigit() and not code.startswith("sh900"):
            candidates[code] = name
        elif code.startswith("sz") and code[2:].isdigit() and not (code.startswith("sz200") or code.startswith("sz201")):
            candidates[code] = name
    return sorted(candidates.items(), key=lambda x: x[0])


def _fetch_hk_ah_rows(seed_rows: Optional[List[dict]] = None) -> List[dict]:
    rows: List[dict] = []
    seed_map: Dict[str, dict] = {}

    for item in seed_rows or []:
        h_code = str(item.get("hCode") or "").strip().zfill(5)
        h_name = str(item.get("hName") or "").strip()
        if len(h_code) == 5 and h_name:
            seed_map[h_code] = {"hCode": h_code, "hName": h_name, "hPrice": 0.0, "ratio": 0.0}

    # Primary source: AkShare AH spot API
    try:
        spot_df = ak.stock_zh_ah_spot()
    except Exception:
        spot_df = None

    if spot_df is not None and hasattr(spot_df, "empty") and not spot_df.empty:
        code_col = "浠ｇ爜" if "浠ｇ爜" in spot_df.columns else spot_df.columns[0]
        name_col = "鍚嶇О" if "鍚嶇О" in spot_df.columns else spot_df.columns[1]
        price_col = "鏈€鏂颁环" if "鏈€鏂颁环" in spot_df.columns else spot_df.columns[2]

        for _, row in spot_df.iterrows():
            h_code = str(row.get(code_col) or "").strip().zfill(5)
            h_name = str(row.get(name_col) or "").strip()
            try:
                h_price = float(row.get(price_col) or 0)
            except Exception:
                h_price = 0.0
            if len(h_code) != 5 or not h_name:
                continue
            seed_map[h_code] = {"hCode": h_code, "hName": h_name, "hPrice": max(0.0, h_price), "ratio": 0.0}

    # Supplement source: AkShare AH name list
    try:
        name_df = ak.stock_zh_ah_name()
    except Exception:
        name_df = None

    if name_df is not None and hasattr(name_df, "empty") and not name_df.empty:
        code_col = "浠ｇ爜" if "浠ｇ爜" in name_df.columns else name_df.columns[0]
        name_col = "鍚嶇О" if "鍚嶇О" in name_df.columns else name_df.columns[1]

        for _, row in name_df.iterrows():
            h_code = str(row.get(code_col) or "").strip().zfill(5)
            h_name = str(row.get(name_col) or "").strip()
            if len(h_code) != 5 or not h_name:
                continue
            cached = seed_map.get(h_code) or {"hCode": h_code, "hName": h_name, "hPrice": 0.0, "ratio": 0.0}
            if not cached.get("hName"):
                cached["hName"] = h_name
            seed_map[h_code] = cached

    # Some valid AH pairs are occasionally missing from AkShare's AH list.
    # Force-include known HK codes so we can still try Tencent quote resolution.
    for manual_h_code in AH_MANUAL_MAP.keys():
        h_code = str(manual_h_code or "").strip().zfill(5)
        if len(h_code) != 5 or h_code in seed_map:
            continue
        seed_map[h_code] = {"hCode": h_code, "hName": "", "hPrice": 0.0, "ratio": 0.0}

    if not seed_map:
        return rows

    quote_map = _get_tencent_quotes([f"hk{code}" for code in seed_map.keys()])
    for h_code, item in seed_map.items():
        quote = quote_map.get(f"hk{h_code}") or {}
        try:
            h_price = float(quote.get("price") or item.get("hPrice") or 0)
        except Exception:
            h_price = 0.0
        if h_price <= 0:
            continue
        rows.append(
            {
                "hCode": h_code,
                "hName": str(quote.get("name") or item.get("hName") or "").strip(),
                "hPrice": h_price,
                "ratio": 0.0,
            }
        )

    return rows


def _resolve_ah_a_code(h_name: str, h_code: str, h_price: float, ratio_hint: float, hk_to_cny: float) -> Optional[Tuple[str, str]]:
    queries = [h_name]
    stripped = re.sub(r"(鑲′唤鏈夐檺鍏徃|鑲′唤|闆嗗洟|鎺ц偂|鏈夐檺鍏徃)$", "", h_name).strip()
    if stripped and stripped != h_name:
        queries.append(stripped)

    candidates: Dict[str, str] = {}
    for q in queries:
        for code, name in _candidate_a_codes(_smartbox_search(q)):
            candidates[code] = name

    if not candidates:
        return None

    quotes = _get_tencent_quotes(list(candidates.keys()))
    best = None
    best_score = 10**9
    h_norm = _normalize_text(h_name)

    for code, cand_name in candidates.items():
        quote = quotes.get(code)
        if not quote:
            continue
        a_price = float(quote.get("price") or 0)
        if a_price <= 0:
            continue

        implied = (h_price * hk_to_cny) / a_price
        ratio_gap = abs(implied - ratio_hint) if ratio_hint > 0 else abs(implied - 1.0)
        sim = SequenceMatcher(None, h_norm, _normalize_text(cand_name or quote.get("name") or "")).ratio()
        if sim < 0.55:
            continue
        score = ratio_gap - 0.35 * sim

        if score < best_score:
            best_score = score
            best = (code[2:], str(quote.get("name") or cand_name or "").strip())

    if not best:
        return None
    if best_score > 2.5:
        return None
    return best


def fetch_ah_pairs(existing_by_h: Dict[str, dict]) -> List[dict]:
    seed_rows = list(existing_by_h.values())
    if not seed_rows:
        seed_rows = _load_cached_ah_pairs()

    rows = _fetch_hk_ah_rows(seed_rows=seed_rows)
    hk_to_cny = _get_fx_rates()["HKD"]

    result = []
    for row in rows:
        h_code = row["hCode"]
        h_name = row["hName"]
        existing = existing_by_h.get(h_code)

        manual = AH_MANUAL_MAP.get(h_code)
        if manual:
            a_code = str(manual.get("aCode") or "")
            a_name = str(manual.get("aName") or "")
        elif existing and _is_name_consistent(existing.get("aName") or "", h_name):
            a_code = str(existing.get("aCode") or "")
            a_name = str(existing.get("aName") or "")
        else:
            resolved = _resolve_ah_a_code(h_name, h_code, float(row["hPrice"]), float(row["ratio"]), hk_to_cny)
            if not resolved:
                continue
            a_code, a_name = resolved

        if len(a_code) != 6:
            continue

        result.append(
            {
                "type": "AH",
                "aCode": a_code,
                "aName": a_name,
                "aMarket": "sh" if a_code.startswith("6") else "sz",
                "hCode": h_code,
                "hName": h_name,
                "hMarket": "hk",
                "currency": "HKD",
                "marketLabel": "AH",
            }
        )

    dedup = {}
    for item in result:
        dedup[(item["aCode"], item["hCode"])] = item
    return sorted(dedup.values(), key=lambda x: x["aCode"])


def _resolve_ab_a_code(name_b: str, b_code: str, b_market: str, b_price: float, fx_rate: float) -> Optional[Tuple[str, str]]:
    if b_market == "sz" and b_code.startswith(("200", "201")):
        mapped = f"0{b_code[1:]}"
        if len(mapped) == 6:
            return mapped, ""

    queries = [name_b]
    stripped = re.sub(r"[B锛鑲[B锛$", "", name_b).strip()
    if stripped and stripped != name_b:
        queries.append(stripped)

    candidates: Dict[str, str] = {}
    for q in queries:
        for code, name in _candidate_a_codes(_smartbox_search(q)):
            candidates[code] = name

    if not candidates:
        return None

    quotes = _get_tencent_quotes(list(candidates.keys()))
    target_name = _normalize_text(name_b)

    best = None
    best_score = 10**9

    for code, cand_name in candidates.items():
        q = quotes.get(code)
        if not q:
            continue
        a_price = float(q.get("price") or 0)
        if a_price <= 0:
            continue
        ratio = (b_price * fx_rate) / a_price
        if ratio <= 0:
            continue

        sim = SequenceMatcher(None, target_name, _normalize_text(cand_name or q.get("name") or "")).ratio()
        score = abs(ratio - 1.0) - 0.5 * sim
        if score < best_score:
            best_score = score
            best = (code[2:], str(q.get("name") or cand_name or "").strip())

    if not best:
        return None
    if best_score > 2.2:
        return None
    return best


def _resolve_fixed_ab_pair(b_code: str, b_market: str) -> Optional[Tuple[str, str]]:
    normalized_b_code = str(b_code or "").strip()
    normalized_market = str(b_market or "").strip().lower()

    if normalized_market == "sz" and normalized_b_code.startswith(("200", "201")):
        mapped = f"0{normalized_b_code[1:]}"
        if len(mapped) == 6:
            return mapped, ""

    if normalized_market == "sh":
        fixed = AB_SH_FIXED_MAP.get(normalized_b_code)
        if fixed:
            return str(fixed["aCode"]), str(fixed.get("aName") or "")

    return None


def _load_cached_ah_pairs() -> List[dict]:
    payload = None
    for path in AH_CACHE_PATHS:
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            break
        except Exception:
            continue
    if payload is None:
        return []

    raw_rows = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(raw_rows, list):
        return []

    rows: List[dict] = []
    for item in raw_rows:
        if not isinstance(item, dict):
            continue
        a_code = str(item.get("aCode") or "").strip()
        h_code = str(item.get("hCode") or "").strip().zfill(5)
        if len(a_code) != 6 or len(h_code) != 5:
            continue
        rows.append(
            {
                "type": "AH",
                "aCode": a_code,
                "aName": str(item.get("aName") or "").strip(),
                "aMarket": str(item.get("aMarket") or ("sh" if a_code.startswith("6") else "sz")).strip(),
                "hCode": h_code,
                "hName": str(item.get("hName") or "").strip(),
                "hMarket": str(item.get("hMarket") or "hk").strip(),
                "currency": "HKD",
                "marketLabel": "AH",
            }
        )

    dedup = {}
    for item in rows:
        dedup[(item["aCode"], item["hCode"])] = item
    return sorted(dedup.values(), key=lambda x: x["aCode"])


def fetch_ab_pairs(existing_by_b: Dict[str, dict]) -> List[dict]:
    b_spot = ak.stock_zh_b_spot()

    result = []
    for _, row in b_spot.iterrows():
        full_code = str(row.iloc[0]).strip().lower()
        b_name = str(row.iloc[1]).strip()
        try:
            b_price = float(row.iloc[2])
        except Exception:
            b_price = 0.0
        if b_price <= 0:
            continue

        if not (full_code.startswith("sh") or full_code.startswith("sz")):
            continue

        b_market = full_code[:2]
        b_code = full_code[2:]
        if len(b_code) != 6:
            continue

        if b_market == "sh":
            currency = "USD"
            market_label = "SH-B"
        else:
            currency = "HKD"
            market_label = "SZ-B"

        fixed = _resolve_fixed_ab_pair(b_code, b_market)
        if fixed:
            a_code, a_name = fixed
        else:
            existing = existing_by_b.get(b_code)
            if existing:
                a_code = str(existing.get("aCode") or "")
                a_name = str(existing.get("aName") or "")
            else:
                continue

        if len(a_code) != 6:
            continue

        result.append(
            {
                "type": "AB",
                "aCode": a_code,
                "aName": a_name,
                "aMarket": "sh" if a_code.startswith("6") else "sz",
                "bCode": b_code,
                "bName": b_name,
                "bMarket": b_market,
                "market": market_label,
                "currency": currency,
                "marketLabel": market_label,
            }
        )

    dedup = {}
    for item in result:
        dedup[(item["aCode"], item["bCode"])] = item
    return sorted(dedup.values(), key=lambda x: x["aCode"])


def _load_pairs_from_db(stock_type: str, active_only: bool = True) -> List[dict]:
    where_clause = "WHERE type = ?"
    if active_only:
        where_clause += " AND is_active = 1"

    with _connect() as conn:
        rows = conn.execute(
            f"""
            SELECT
                type,
                a_code,
                pair_code,
                a_name,
                pair_name,
                a_market,
                pair_market,
                market_label,
                currency
            FROM pair_master
            {where_clause}
            ORDER BY a_code ASC
            """,
            (stock_type,),
        ).fetchall()

    result = []
    for row in rows:
        if stock_type == "AH":
            result.append(
                {
                    "type": "AH",
                    "aCode": row["a_code"],
                    "aName": row["a_name"] or "",
                    "aMarket": row["a_market"] or "",
                    "hCode": row["pair_code"],
                    "hName": row["pair_name"] or "",
                    "hMarket": row["pair_market"] or "hk",
                }
            )
        else:
            result.append(
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
                }
            )

    return result


def _load_active_pairs_from_db(stock_type: str) -> List[dict]:
    return _load_pairs_from_db(stock_type=stock_type, active_only=True)


def _has_suspicious_ah_pairs(rows: List[dict]) -> bool:
    for item in rows:
        a_name = str(item.get("aName") or "").strip()
        h_name = str(item.get("hName") or "").strip()
        if not _is_name_consistent(a_name, h_name):
            return True
    return False


def _has_sync_today(stock_type: str) -> bool:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM pair_sync_log
            WHERE sync_date = ? AND type = ?
            LIMIT 1
            """,
            (today_str(), stock_type),
        ).fetchone()
    return bool(row)


def _sync_pairs_to_db(stock_type: str, api_rows: List[dict], source: str) -> Dict[str, int]:
    init_pair_db()

    now = now_iso()
    today = today_str()
    added = 0
    removed = 0
    updated = 0

    normalized_rows = []
    for row in api_rows:
        if stock_type == "AH":
            pair_code = str(row.get("hCode") or row.get("pairCode") or "").strip().zfill(5)
            pair_name = str(row.get("hName") or row.get("pairName") or "").strip()
            pair_market = str(row.get("hMarket") or row.get("pairMarket") or "hk").strip()
            market_label = "AH"
            currency = "HKD"
        else:
            pair_code = str(row.get("bCode") or row.get("pairCode") or "").strip()
            pair_name = str(row.get("bName") or row.get("pairName") or "").strip()
            pair_market = str(row.get("bMarket") or row.get("pairMarket") or "").strip()
            market_label = str(row.get("market") or row.get("marketLabel") or "").strip()
            currency = str(row.get("currency") or "").strip().upper()

        a_code = str(row.get("aCode") or "").strip()
        if not a_code or not pair_code:
            continue

        normalized_rows.append(
            {
                "aCode": a_code,
                "pairCode": pair_code,
                "aName": str(row.get("aName") or "").strip(),
                "pairName": pair_name,
                "aMarket": str(row.get("aMarket") or ("sh" if a_code.startswith("6") else "sz")).strip(),
                "pairMarket": pair_market,
                "marketLabel": market_label,
                "currency": currency,
            }
        )

    api_keys = {(row["aCode"], row["pairCode"]) for row in normalized_rows}

    with _connect() as conn:
        current_rows = conn.execute(
            """
            SELECT a_code, pair_code
            FROM pair_master
            WHERE type = ? AND is_active = 1
            """,
            (stock_type,),
        ).fetchall()
        current_keys = {(row["a_code"], row["pair_code"]) for row in current_rows}

        for row in normalized_rows:
            key = (row["aCode"], row["pairCode"])
            if key not in current_keys:
                added += 1
            else:
                updated += 1

            conn.execute(
                """
                INSERT INTO pair_master(
                    type, a_code, pair_code, a_name, pair_name,
                    a_market, pair_market, market_label, currency,
                    is_active, first_seen, last_seen, updated_at, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
                ON CONFLICT(type, a_code, pair_code) DO UPDATE SET
                    a_name = excluded.a_name,
                    pair_name = excluded.pair_name,
                    a_market = excluded.a_market,
                    pair_market = excluded.pair_market,
                    market_label = excluded.market_label,
                    currency = excluded.currency,
                    is_active = 1,
                    last_seen = excluded.last_seen,
                    updated_at = excluded.updated_at,
                    source = excluded.source
                """,
                (
                    stock_type,
                    row["aCode"],
                    row["pairCode"],
                    row["aName"],
                    row["pairName"],
                    row["aMarket"],
                    row["pairMarket"],
                    row["marketLabel"],
                    row["currency"],
                    now,
                    today,
                    now,
                    source,
                ),
            )

        stale_keys = current_keys - api_keys
        for a_code, pair_code in stale_keys:
            conn.execute(
                """
                UPDATE pair_master
                SET is_active = 0, last_seen = ?, updated_at = ?, source = ?
                WHERE type = ? AND a_code = ? AND pair_code = ?
                """,
                (today, now, f"{source}:removed", stock_type, a_code, pair_code),
            )
            removed += 1

        active_total = conn.execute(
            "SELECT COUNT(1) AS cnt FROM pair_master WHERE type = ? AND is_active = 1",
            (stock_type,),
        ).fetchone()["cnt"]

        conn.execute(
            """
            INSERT INTO pair_sync_log(
                sync_date, type, total_active, added_count, removed_count, updated_count, source, sync_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sync_date, type) DO UPDATE SET
                total_active = excluded.total_active,
                added_count = excluded.added_count,
                removed_count = excluded.removed_count,
                updated_count = excluded.updated_count,
                source = excluded.source,
                sync_time = excluded.sync_time
            """,
            (today, stock_type, int(active_total), int(added), int(removed), int(updated), source, now),
        )

    return {
        "added": added,
        "removed": removed,
        "updated": updated,
    }


def load_dynamic_pairs(force_refresh: bool = False) -> Dict[str, List[dict]]:
    init_pair_db()

    db_ah = _load_active_pairs_from_db("AH")
    db_ab = _load_active_pairs_from_db("AB")
    db_ah_all = _load_pairs_from_db("AH", active_only=False)
    cached_ah = _load_cached_ah_pairs()

    if cached_ah and len(db_ah) < len(cached_ah):
        _sync_pairs_to_db("AH", cached_ah, "local_seed")
        db_ah = _load_active_pairs_from_db("AH")

    synced_today = _has_sync_today("AH") and _has_sync_today("AB")

    if not force_refresh and synced_today and db_ah and db_ab and not _has_suspicious_ah_pairs(db_ah):
        return {
            "ah": db_ah,
            "ab": db_ab,
            "updateTime": now_iso(),
            "source": "local_db",
        }

    try:
        existing_ah_by_h = {str(item.get("hCode") or ""): item for item in db_ah_all}
        existing_ah_by_h.update({str(item.get("hCode") or ""): item for item in cached_ah})
        existing_ah_by_h.update({str(item.get("hCode") or ""): item for item in db_ah})
        existing_ab_by_b = {str(item.get("bCode") or ""): item for item in db_ab}

        ah_rows = fetch_ah_pairs(existing_ah_by_h)
        ab_rows = fetch_ab_pairs(existing_ab_by_b)

        if not ah_rows or not ab_rows:
            raise RuntimeError("pair api returned empty list")

        _sync_pairs_to_db("AH", ah_rows, "tencent+akshare")
        _sync_pairs_to_db("AB", ab_rows, "akshare+sina+smartbox")

        db_ah = _load_active_pairs_from_db("AH")
        db_ab = _load_active_pairs_from_db("AB")

        return {
            "ah": db_ah,
            "ab": db_ab,
            "updateTime": now_iso(),
            "source": "tencent+akshare+local_db",
        }
    except Exception:
        db_ah = _load_active_pairs_from_db("AH")
        db_ab = _load_active_pairs_from_db("AB")
        if db_ah and db_ab:
            return {
                "ah": db_ah,
                "ab": db_ab,
                "updateTime": now_iso(),
                "source": "local_db_fallback",
            }
        raise


def find_ah_pair(a_code: str, pairs: Optional[List[dict]] = None) -> Optional[dict]:
    lookup = pairs if isinstance(pairs, list) else load_dynamic_pairs().get("ah", [])
    target = str(a_code or "").strip()
    for item in lookup:
        if str(item.get("aCode") or "") == target:
            return item
    return None


def find_ab_pair(a_code: str, pairs: Optional[List[dict]] = None) -> Optional[dict]:
    lookup = pairs if isinstance(pairs, list) else load_dynamic_pairs().get("ab", [])
    target = str(a_code or "").strip()
    for item in lookup:
        if str(item.get("aCode") or "") == target:
            return item
    return None



