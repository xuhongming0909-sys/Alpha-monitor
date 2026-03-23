"""Fetch public event-arbitrage snapshots from configured sources."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from shared.config.script_config import get_config
from shared.models.service_result import build_success
from shared.runtime.state_registry import create_state_registry
from shared.time.shanghai_time import now_iso


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCE_URLS = {
    "hk_private": "https://www.jisilu.cn/data/taoligu/hk_arbitrage_list/",
    "cn_private": "https://www.jisilu.cn/data/taoligu/cn_arbitrage_list/",
    "a_event": "https://www.jisilu.cn/data/taoligu/astock_arbitrage_list/",
}

DEFAULT_CATEGORIES = ("hk_private", "cn_private", "a_event", "rights_issue")

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.jisilu.cn/data/taoligu/",
    "Accept": "application/json,text/plain,*/*",
}


def _plugin_config() -> dict[str, Any]:
    config = get_config()
    plugin = config.get("data_fetch", {}).get("plugins", {}).get("event_arbitrage", {})
    return plugin if isinstance(plugin, dict) else {}


def _state_registry():
    return create_state_registry(get_config())


def _cache_fallback() -> dict[str, Any]:
    return {
        "updatedAt": "",
        "sources": {
            key: {
                "rows": [],
                "updateTime": "",
                "status": "empty",
                "sourceUrl": SOURCE_URLS.get(key, ""),
                "source": "jisilu",
            }
            for key in DEFAULT_CATEGORIES
        },
    }


def _read_cache() -> dict[str, Any]:
    registry = _state_registry()
    cached = registry["read"]("event_arbitrage_cache", "event_arbitrage_cache.json", _cache_fallback())
    return cached if isinstance(cached, dict) else _cache_fallback()


def _write_cache(payload: dict[str, Any]) -> dict[str, Any]:
    registry = _state_registry()
    return registry["write"]("event_arbitrage_cache", "event_arbitrage_cache.json", payload)


def _create_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update(REQUEST_HEADERS)
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _extract_rows(payload: Any) -> list[dict[str, Any]]:
    rows = payload.get("rows") if isinstance(payload, dict) else []
    normalized = []
    for item in rows or []:
        if not isinstance(item, dict):
            continue
        cell = item.get("cell")
        normalized.append(dict(cell if isinstance(cell, dict) else item))
    return normalized


def _fetch_json(session: requests.Session, url: str, timeout_seconds: float) -> dict[str, Any]:
    try:
        response = session.get(url, timeout=timeout_seconds)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError:
        response = session.get(url, timeout=timeout_seconds, verify=False)
        response.raise_for_status()
        return response.json()


def _read_source_enabled(source_name: str, plugin_config: dict[str, Any]) -> bool:
    sources = plugin_config.get("sources", {})
    if not isinstance(sources, dict):
        return source_name != "rights_issue"
    source_config = sources.get(source_name, {})
    if not isinstance(source_config, dict):
        return source_name != "rights_issue"
    return bool(source_config.get("enabled", source_name != "rights_issue"))


def _build_disabled_status(source_name: str) -> dict[str, Any]:
    return {
        "enabled": False,
        "status": "disabled_no_public_source",
        "itemCount": 0,
        "updateTime": now_iso(),
        "source": "jisilu",
        "sourceUrl": SOURCE_URLS.get(source_name, ""),
        "servedFromCache": False,
    }


def _fetch_source(source_name: str, session: requests.Session, timeout_seconds: float, cache_snapshot: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_url = SOURCE_URLS[source_name]
    cache_entry = cache_snapshot.get("sources", {}).get(source_name, {}) if isinstance(cache_snapshot, dict) else {}
    try:
        payload = _fetch_json(session, source_url, timeout_seconds)
        rows = _extract_rows(payload)
        status = {
            "enabled": True,
            "status": "ok" if rows else "empty",
            "itemCount": len(rows),
            "updateTime": now_iso(),
            "source": "jisilu",
            "sourceUrl": source_url,
            "servedFromCache": False,
        }
        return rows, status
    except Exception as exc:
        cached_rows = deepcopy(cache_entry.get("rows", [])) if isinstance(cache_entry, dict) else []
        if cached_rows:
            return cached_rows, {
                "enabled": True,
                "status": "stale_cache",
                "itemCount": len(cached_rows),
                "updateTime": str(cache_entry.get("updateTime") or now_iso()),
                "source": "jisilu",
                "sourceUrl": source_url,
                "servedFromCache": True,
                "error": str(exc),
            }
        return [], {
            "enabled": True,
            "status": "error",
            "itemCount": 0,
            "updateTime": now_iso(),
            "source": "jisilu",
            "sourceUrl": source_url,
            "servedFromCache": False,
            "error": str(exc),
        }


def fetch_event_arbitrage_snapshot() -> dict[str, Any]:
    """Fetch raw public event-arbitrage payloads with per-source cache fallback."""

    plugin_config = _plugin_config()
    timeout_seconds = max(float(plugin_config.get("timeout_ms", 30000)) / 1000.0, 3.0)
    cache_snapshot = _read_cache()
    categories = {key: [] for key in DEFAULT_CATEGORIES}
    source_status = {}
    next_cache = _cache_fallback()
    next_cache["updatedAt"] = now_iso()

    with _create_session() as session:
        for source_name in DEFAULT_CATEGORIES:
            enabled = _read_source_enabled(source_name, plugin_config)
            if source_name == "rights_issue" and not enabled:
                categories[source_name] = []
                source_status[source_name] = _build_disabled_status(source_name)
                next_cache["sources"][source_name] = {
                    "rows": [],
                    "updateTime": source_status[source_name]["updateTime"],
                    "status": source_status[source_name]["status"],
                    "sourceUrl": SOURCE_URLS.get(source_name, ""),
                    "source": "jisilu",
                }
                continue

            if not enabled:
                categories[source_name] = []
                source_status[source_name] = {
                    "enabled": False,
                    "status": "disabled",
                    "itemCount": 0,
                    "updateTime": now_iso(),
                    "source": "jisilu",
                    "sourceUrl": SOURCE_URLS.get(source_name, ""),
                    "servedFromCache": False,
                }
                next_cache["sources"][source_name] = {
                    "rows": [],
                    "updateTime": source_status[source_name]["updateTime"],
                    "status": source_status[source_name]["status"],
                    "sourceUrl": SOURCE_URLS.get(source_name, ""),
                    "source": "jisilu",
                }
                continue

            rows, status = _fetch_source(source_name, session, timeout_seconds, cache_snapshot)
            categories[source_name] = rows
            source_status[source_name] = status
            next_cache["sources"][source_name] = {
                "rows": deepcopy(rows),
                "updateTime": status.get("updateTime") or now_iso(),
                "status": status.get("status") or "empty",
                "sourceUrl": status.get("sourceUrl") or SOURCE_URLS.get(source_name, ""),
                "source": status.get("source") or "jisilu",
            }

    cache_snapshot = _write_cache(next_cache)
    return build_success(
        {
            "categories": categories,
            "sourceStatus": source_status,
        },
        updateTime=now_iso(),
        source="jisilu",
        cacheTime=cache_snapshot.get("updatedAt") or now_iso(),
    )

