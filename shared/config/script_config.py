"""Python 侧统一配置读取器。
规则是“配置即合同，密钥可由环境变量注入”，不再对普通业务参数做环境变量兜底。"""

from __future__ import annotations

import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict

import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_FILE = ROOT_DIR / "config.yaml"
ENV_FILE = ROOT_DIR / ".env"

_CONFIG_CACHE: Dict[str, Any] | None = None

SECRET_ENV_PATHS = [
    (("notification", "wecom", "webhook_url"), "WECOM_WEBHOOK_URL"),
    (("notification", "wecom", "push_html_url"), "PUSH_HTML_URL"),
    (("notification", "wecom", "push_html_url"), "ALPHA_MONITOR_HTML_URL"),
    (("strategy", "merger", "deepseek_api_key"), "DEEPSEEK_API_KEY"),
    (("strategy", "merger", "deepseek_base_url"), "DEEPSEEK_BASE_URL"),
    (("data_fetch", "plugins", "convertible_bond", "jisilu_cookie"), "JISILU_COOKIE"),
    (("data_fetch", "plugins", "lof_arbitrage", "jisilu_cookie"), "JISILU_COOKIE"),
    (("data_fetch", "plugins", "lof_arbitrage", "firecrawl_api_url"), "FIRECRAWL_API_URL"),
    (("data_fetch", "plugins", "lof_arbitrage", "firecrawl_api_key"), "FIRECRAWL_API_KEY"),
]


def load_env_file(file_path: Path = ENV_FILE) -> None:
    """把 .env 中尚未注入进进程环境的键补进来。"""

    if not file_path.exists():
        return

    for line in file_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue

        key, raw_value = text.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue

        value = raw_value.strip()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        os.environ[key] = value


def _deep_clone(value: Any) -> Any:
    return deepcopy(value)


def _resolve_env_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _resolve_env_placeholders(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_env_placeholders(item) for item in value]
    if not isinstance(value, str):
        return value

    if value.startswith("${") and value.endswith("}") and value.count("${") == 1:
        env_name = value[2:-1]
        return os.environ.get(env_name, "")

    return re.sub(r"\$\{([A-Z0-9_]+)\}", lambda match: os.environ.get(match.group(1), ""), value)


def _get_at_path(target: Dict[str, Any], path_parts: tuple[str, ...]) -> Any:
    current: Any = target
    for part in path_parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _set_at_path(target: Dict[str, Any], path_parts: tuple[str, ...], value: Any) -> None:
    current = target
    for part in path_parts[:-1]:
        next_value = current.get(part)
        if not isinstance(next_value, dict):
            next_value = {}
            current[part] = next_value
        current = next_value
    current[path_parts[-1]] = value


def _is_missing(value: Any) -> bool:
    return value in (None, "")


def _apply_secret_env(config: Dict[str, Any]) -> Dict[str, Any]:
    for path_parts, env_name in SECRET_ENV_PATHS:
        current = _get_at_path(config, path_parts)
        if not _is_missing(current):
            continue
        env_value = os.environ.get(env_name)
        if _is_missing(env_value):
            continue
        _set_at_path(config, path_parts, env_value)
    return config


def _normalize_python_candidates(config: Dict[str, Any]) -> Dict[str, Any]:
    app_config = config.setdefault("app", {})
    current = app_config.get("python_bin_candidates")
    if not isinstance(current, list):
        current = []

    configured_python = str(app_config.get("python_bin") or "").strip()
    if configured_python:
        app_config["python_bin"] = configured_python
        app_config["python_bin_candidates"] = list(dict.fromkeys([configured_python, *current]))
        return config

    platform_defaults = ["python", "python3"] if os.name == "nt" else ["python3", "python"]
    app_config["python_bin_candidates"] = list(dict.fromkeys([*current, *platform_defaults]))
    return config


def _read_config_file() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    text = CONFIG_FILE.read_text(encoding="utf-8")
    parsed = yaml.safe_load(text) or {}
    if not isinstance(parsed, dict):
        raise ValueError("config.yaml root must be a mapping")
    return parsed


def load_config(*, reload: bool = False) -> Dict[str, Any]:
    """读取、解析并缓存配置。"""

    global _CONFIG_CACHE

    if _CONFIG_CACHE is not None and not reload:
        return _deep_clone(_CONFIG_CACHE)

    load_env_file()
    config = _read_config_file()
    config = _resolve_env_placeholders(config)
    config = _apply_secret_env(config)
    config = _normalize_python_candidates(config)
    _CONFIG_CACHE = config
    return _deep_clone(config)


def get_config() -> Dict[str, Any]:
    """获取当前缓存配置。"""

    return load_config()
