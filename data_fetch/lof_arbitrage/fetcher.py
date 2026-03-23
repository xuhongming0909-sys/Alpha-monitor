"""Fetch public LOF/QDII arbitrage snapshots from Jisilu."""

from __future__ import annotations

import os
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

SOURCE_URL_TEMPLATE = "https://www.jisilu.cn/data/qdii/qdii_list/{bucket_code}"

DEFAULT_CATEGORIES = {
    "europe_us": "E",
    "asia": "A",
    "commodity": "C",
}

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.jisilu.cn/data/qdii/",
    "Accept": "application/json,text/plain,*/*",
}


def _plugin_config() -> dict[str, Any]:
    plugin = get_config().get("data_fetch", {}).get("plugins", {}).get("lof_arbitrage", {})
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
                "sourceUrl": SOURCE_URL_TEMPLATE.format(bucket_code=bucket),
                "source": "jisilu_qdii",
                "cookieConfigured": False,
                "authMode": "public",
                "usedLoginEnhancedRows": False,
            }
            for key, bucket in DEFAULT_CATEGORIES.items()
        },
    }


def _read_cache() -> dict[str, Any]:
    cached = _state_registry()["read"]("lof_arbitrage_cache", "lof_arbitrage_cache.json", _cache_fallback())
    return cached if isinstance(cached, dict) else _cache_fallback()


def _write_cache(payload: dict[str, Any]) -> dict[str, Any]:
    return _state_registry()["write"]("lof_arbitrage_cache", "lof_arbitrage_cache.json", payload)


def _create_session(cookie_text: str = "") -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update(REQUEST_HEADERS)
    if cookie_text:
        session.headers["Cookie"] = cookie_text
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


def _read_source_config(source_name: str, plugin_config: dict[str, Any]) -> tuple[bool, str]:
    categories = plugin_config.get("categories", {})
    source_config = categories.get(source_name, {}) if isinstance(categories, dict) else {}
    if not isinstance(source_config, dict):
        source_config = {}
    enabled = bool(source_config.get("enabled", True))
    bucket_code = str(source_config.get("bucket_code") or DEFAULT_CATEGORIES[source_name]).strip().upper()
    return enabled, bucket_code


def _read_cookie(plugin_config: dict[str, Any]) -> str:
    configured = str(plugin_config.get("jisilu_cookie") or "").strip()
    if configured:
        return configured
    return str(os.getenv("JISILU_COOKIE", "")).strip()


def _build_status(
    *,
    item_count: int,
    update_time: str,
    source_url: str,
    bucket_code: str,
    cookie_configured: bool,
    auth_mode: str,
    used_login_enhanced_rows: bool,
    served_from_cache: bool,
    status: str,
    error: str = "",
) -> dict[str, Any]:
    payload = {
        "enabled": True,
        "status": status,
        "itemCount": item_count,
        "updateTime": update_time,
        "source": "jisilu_qdii",
        "sourceUrl": source_url,
        "servedFromCache": served_from_cache,
        "bucketCode": bucket_code,
        "cookieConfigured": cookie_configured,
        "authMode": auth_mode,
        "usedLoginEnhancedRows": used_login_enhanced_rows,
    }
    if error:
        payload["error"] = error
    return payload


def _fetch_source_once(
    session: requests.Session,
    source_url: str,
    timeout_seconds: float,
) -> list[dict[str, Any]]:
    payload = _fetch_json(session, source_url, timeout_seconds)
    return _extract_rows(payload)


def _fetch_source(
    source_name: str,
    bucket_code: str,
    public_session: requests.Session,
    auth_session: requests.Session | None,
    cookie_configured: bool,
    timeout_seconds: float,
    cache_snapshot: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_url = SOURCE_URL_TEMPLATE.format(bucket_code=bucket_code)
    cache_entry = cache_snapshot.get("sources", {}).get(source_name, {}) if isinstance(cache_snapshot, dict) else {}
    auth_error = ""
    try:
        if auth_session is not None:
            try:
                auth_rows = _fetch_source_once(auth_session, source_url, timeout_seconds)
                if auth_rows:
                    return auth_rows, _build_status(
                        item_count=len(auth_rows),
                        update_time=now_iso(),
                        source_url=source_url,
                        bucket_code=bucket_code,
                        cookie_configured=cookie_configured,
                        auth_mode="authenticated",
                        used_login_enhanced_rows=True,
                        served_from_cache=False,
                        status="ok",
                    )
            except Exception as exc:
                auth_error = str(exc)

        public_rows = _fetch_source_once(public_session, source_url, timeout_seconds)
        return public_rows, _build_status(
            item_count=len(public_rows),
            update_time=now_iso(),
            source_url=source_url,
            bucket_code=bucket_code,
            cookie_configured=cookie_configured,
            auth_mode="authenticated_fallback_public" if cookie_configured else "public",
            used_login_enhanced_rows=False,
            served_from_cache=False,
            status="ok" if public_rows else "empty",
            error=auth_error,
        )
    except Exception as exc:
        cached_rows = deepcopy(cache_entry.get("rows", [])) if isinstance(cache_entry, dict) else []
        if cached_rows:
            return cached_rows, _build_status(
                item_count=len(cached_rows),
                update_time=str(cache_entry.get("updateTime") or now_iso()),
                source_url=source_url,
                bucket_code=bucket_code,
                cookie_configured=bool(cache_entry.get("cookieConfigured", cookie_configured)),
                auth_mode=str(cache_entry.get("authMode") or ("authenticated_fallback_public" if cookie_configured else "public")),
                used_login_enhanced_rows=bool(cache_entry.get("usedLoginEnhancedRows")),
                served_from_cache=True,
                status="stale_cache",
                error=auth_error or str(exc),
            )
        return [], _build_status(
            item_count=0,
            update_time=now_iso(),
            source_url=source_url,
            bucket_code=bucket_code,
            cookie_configured=cookie_configured,
            auth_mode="authenticated_fallback_public" if cookie_configured else "public",
            used_login_enhanced_rows=False,
            served_from_cache=False,
            status="error",
            error=auth_error or str(exc),
        )


def fetch_lof_arbitrage_snapshot() -> dict[str, Any]:
    """Fetch raw LOF arbitrage source rows with per-category cache fallback."""

    plugin_config = _plugin_config()
    timeout_seconds = max(float(plugin_config.get("timeout_ms", 30000)) / 1000.0, 3.0)
    cookie_text = _read_cookie(plugin_config)
    cookie_configured = bool(cookie_text)
    cache_snapshot = _read_cache()
    categories = {key: [] for key in DEFAULT_CATEGORIES}
    source_status = {}
    next_cache = _cache_fallback()
    next_cache["updatedAt"] = now_iso()

    with _create_session() as public_session:
        auth_session = _create_session(cookie_text) if cookie_configured else None
        for source_name in DEFAULT_CATEGORIES:
            enabled, bucket_code = _read_source_config(source_name, plugin_config)
            source_url = SOURCE_URL_TEMPLATE.format(bucket_code=bucket_code)
            if not enabled:
                categories[source_name] = []
                source_status[source_name] = {
                    "enabled": False,
                    "status": "disabled",
                    "itemCount": 0,
                    "updateTime": now_iso(),
                    "source": "jisilu_qdii",
                    "sourceUrl": source_url,
                    "servedFromCache": False,
                    "bucketCode": bucket_code,
                    "cookieConfigured": cookie_configured,
                    "authMode": "public",
                    "usedLoginEnhancedRows": False,
                }
                next_cache["sources"][source_name] = {
                    "rows": [],
                    "updateTime": source_status[source_name]["updateTime"],
                    "status": "disabled",
                    "sourceUrl": source_url,
                    "source": "jisilu_qdii",
                    "cookieConfigured": cookie_configured,
                    "authMode": "public",
                    "usedLoginEnhancedRows": False,
                }
                continue

            rows, status = _fetch_source(
                source_name,
                bucket_code,
                public_session,
                auth_session,
                cookie_configured,
                timeout_seconds,
                cache_snapshot,
            )
            categories[source_name] = rows
            source_status[source_name] = status
            next_cache["sources"][source_name] = {
                "rows": deepcopy(rows),
                "updateTime": status.get("updateTime") or now_iso(),
                "status": status.get("status") or "empty",
                "sourceUrl": source_url,
                "source": "jisilu_qdii",
                "cookieConfigured": bool(status.get("cookieConfigured")),
                "authMode": str(status.get("authMode") or "public"),
                "usedLoginEnhancedRows": bool(status.get("usedLoginEnhancedRows")),
            }
        if auth_session is not None:
            auth_session.close()

    cache_snapshot = _write_cache(next_cache)
    served_from_cache = any(bool((source_status.get(key) or {}).get("servedFromCache")) for key in source_status)
    return build_success(
        {
            "categories": categories,
            "sourceStatus": source_status,
        },
        updateTime=now_iso(),
        source="jisilu_qdii",
        cacheTime=cache_snapshot.get("updatedAt") or now_iso(),
        servedFromCache=served_from_cache,
    )
