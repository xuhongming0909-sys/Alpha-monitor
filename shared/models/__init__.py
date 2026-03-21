"""通用返回模型。"""

from .service_result import build_error, build_success, normalize_error

__all__ = ["normalize_error", "build_success", "build_error"]

