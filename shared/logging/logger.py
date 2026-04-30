"""统一logger。"""

from __future__ import annotations

from typing import Any

from shared.config.script_config import get_config
from shared.time.shanghai_time import now_iso


LEVEL_ORDER = {
    "debug": 10,
    "info": 20,
    "warn": 30,
    "error": 40,
}


def resolve_logging_config() -> dict[str, Any]:
    """读取日志配置。"""

    config = get_config()
    logging = config.get("logging", {})
    return {
        "level": str(logging.get("level") or "info").lower(),
        "console_enabled": logging.get("console_enabled", True) is not False,
    }


def should_log(target_level: str, current_level: str) -> bool:
    """判断当前级别是否应该输出。"""

    return LEVEL_ORDER.get(target_level, 999) >= LEVEL_ORDER.get(current_level, LEVEL_ORDER["info"])


class Logger:
    """最基础的控制台logger。"""

    def __init__(self, scope: str = "") -> None:
        self.scope = scope
        self.config = resolve_logging_config()

    def _log(self, level: str, *args: Any) -> None:
        if not self.config["console_enabled"]:
            return
        if not should_log(level, self.config["level"]):
            return
        prefix = f"[{now_iso()}] [{level.upper()}]"
        if self.scope:
            prefix += f" [{self.scope}]"
        print(prefix, *args)

    def debug(self, *args: Any) -> None:
        self._log("debug", *args)

    def info(self, *args: Any) -> None:
        self._log("info", *args)

    def warn(self, *args: Any) -> None:
        self._log("warn", *args)

    def error(self, *args: Any) -> None:
        self._log("error", *args)


def create_logger(scope: str = "") -> Logger:
    """创建带作用域的logger。"""

    return Logger(scope)

