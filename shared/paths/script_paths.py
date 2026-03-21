"""Shared Python path policy derived from config.yaml."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict

from shared.config.script_config import ROOT_DIR, get_config


def slugify(value: str, fallback: str = "local") -> str:
    """Convert profile-like input into a safe directory slug."""

    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip())
    text = text.strip(".-")
    return text or fallback


def _resolve_from_root(relative_path: str | None, fallback_relative_path: str) -> Path:
    candidate = str(relative_path or "").strip()
    return (ROOT_DIR / (candidate or fallback_relative_path)).resolve()


def get_path_policy() -> Dict[str, Any]:
    """Build runtime path policy from the shared configuration contract."""

    config = get_config()
    storage = config.get("storage", {})
    data_root_dir = _resolve_from_root(storage.get("data_root_dir"), "runtime_data")
    shared_data_dir = _resolve_from_root(storage.get("shared_data_dir"), "runtime_data/shared")
    runtime_profile_dir = _resolve_from_root(storage.get("runtime_profile_dir"), "runtime_data/profiles")
    db_profile = slugify(str(storage.get("db_profile") or "shared"))
    runtime_data_dir = shared_data_dir if db_profile == "shared" else runtime_profile_dir / db_profile

    return {
        "root_dir": ROOT_DIR,
        "data_root_dir": data_root_dir,
        "shared_data_dir": shared_data_dir,
        "runtime_profile_dir": runtime_profile_dir,
        "db_profile": db_profile,
        "runtime_data_dir": runtime_data_dir,
        "runtime_files": storage.get("runtime_files", {}),
    }


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists and return it."""

    path.mkdir(parents=True, exist_ok=True)
    return path


def runtime_file_path(filename: str) -> Path:
    """Return the active runtime file path for a configured filename."""

    policy = get_path_policy()
    target_path = policy["runtime_data_dir"] / filename
    ensure_dir(target_path.parent)
    return target_path


def shared_db_path(filename: str) -> Path:
    """Return a shared database path under the shared runtime data directory."""

    policy = get_path_policy()
    target_path = policy["shared_data_dir"] / filename
    ensure_dir(target_path.parent)
    return target_path
