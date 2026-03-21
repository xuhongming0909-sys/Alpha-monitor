"""运行态state_registry。"""

from __future__ import annotations

from typing import Any

from shared.config.script_config import get_config
from shared.paths.script_paths import runtime_file_path
from shared.runtime.json_store import read_json, write_json


def create_state_registry(config: dict[str, Any] | None = None) -> dict[str, Any]:
    """创建统一的运行态文件注册表。"""

    loaded_config = config or get_config()
    runtime_files = loaded_config.get("storage", {}).get("runtime_files", {})

    def resolve(logical_key: str, fallback_name: str):
        configured = str(runtime_files.get(logical_key) or "").strip()
        return runtime_file_path(configured or fallback_name)

    def read(logical_key: str, fallback_name: str, fallback_value: Any):
        return read_json(resolve(logical_key, fallback_name), fallback_value)

    def write(logical_key: str, fallback_name: str, value: Any):
        return write_json(resolve(logical_key, fallback_name), value)

    return {
        "resolve": resolve,
        "read": read,
        "write": write,
    }

