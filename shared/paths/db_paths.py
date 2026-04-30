# AI-SUMMARY: paths 路径解析：运行时目录与文件路径
# 对应 INDEX.md §9 文件摘要索引

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Database path helpers for runtime data and shared SQLite files."""

from __future__ import annotations

from pathlib import Path

from shared.paths.script_paths import ensure_dir, get_path_policy, runtime_file_path, shared_db_path


_PATH_POLICY = get_path_policy()

BASE_DIR = Path(__file__).resolve().parent
ROOT_DATA_DIR = _PATH_POLICY["data_root_dir"]
STATIC_DATA_DIR = ROOT_DATA_DIR
SHARED_DATA_DIR = _PATH_POLICY["shared_data_dir"]
DB_PROFILE = _PATH_POLICY["db_profile"]
PROFILE_DATA_DIR = (
    SHARED_DATA_DIR if DB_PROFILE == "shared" else _PATH_POLICY["runtime_profile_dir"] / DB_PROFILE
)
RUNTIME_DATA_DIR = _PATH_POLICY["runtime_data_dir"]


__all__ = [
    "BASE_DIR",
    "ROOT_DATA_DIR",
    "STATIC_DATA_DIR",
    "SHARED_DATA_DIR",
    "DB_PROFILE",
    "PROFILE_DATA_DIR",
    "RUNTIME_DATA_DIR",
    "ensure_dir",
    "shared_db_path",
    "runtime_file_path",
]
