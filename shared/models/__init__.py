# AI-SUMMARY: models 插件初始化模块
# 对应 INDEX.md §9 文件摘要索引

"""通用返回模型。"""

from .service_result import build_error, build_success, normalize_error

__all__ = ["normalize_error", "build_success", "build_error"]

