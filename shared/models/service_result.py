# AI-SUMMARY: 标准响应包装（Python）：成功/错误响应格式
# 对应 INDEX.md §9 文件摘要索引

"""统一服务返回模型。"""

from __future__ import annotations

from typing import Any, Dict

from shared.time.shanghai_time import now_iso


def normalize_error(error: Any) -> str:
    """把异常对象统一转换成人可读文本。"""

    if error is None:
        return "Unknown error"
    if isinstance(error, str):
        return error
    return str(getattr(error, "message", None) or error)


def build_success(data: Any = None, **extra: Any) -> Dict[str, Any]:
    """构造统一成功返回结构。"""

    payload = {
        "success": True,
        "data": data,
        "error": None,
        "updateTime": extra.pop("updateTime", now_iso()),
    }
    payload.update(extra)
    return payload


def build_error(error: Any, data: Any = None, **extra: Any) -> Dict[str, Any]:
    """构造统一失败返回结构。"""

    payload = {
        "success": False,
        "data": data,
        "error": normalize_error(error),
        "updateTime": extra.pop("updateTime", now_iso()),
    }
    payload.update(extra)
    return payload

