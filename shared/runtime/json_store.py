"""统一的 JSON 运行态读写层。"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from shared.paths.script_paths import ensure_dir


def clone_fallback(value: Any) -> Any:
    """复制兜底值，避免调用方共享可变对象。"""

    return deepcopy(value)


def read_json(file_path: str | Path, fallback_value: Any = None) -> Any:
    """读取 JSON 文件；文件不存在或损坏时返回兜底值副本。"""

    path = Path(file_path)
    try:
      if not path.exists():
          return clone_fallback(fallback_value)
      text = path.read_text(encoding="utf-8")
      return json.loads(text) if text.strip() else clone_fallback(fallback_value)
    except Exception:
      return clone_fallback(fallback_value)


def write_json(file_path: str | Path, data: Any, *, indent: int = 2) -> Any:
    """写入 JSON 文件，并自动创建父目录。"""

    path = Path(file_path)
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding="utf-8")
    return data


def update_json(
    file_path: str | Path,
    fallback_value: Any,
    updater: Callable[[Any], Any],
    *,
    indent: int = 2,
) -> Any:
    """先读再改再写，适合维护运行态状态文件。"""

    current = read_json(file_path, fallback_value)
    next_value = updater(current) if callable(updater) else current
    return write_json(file_path, next_value, indent=indent)

