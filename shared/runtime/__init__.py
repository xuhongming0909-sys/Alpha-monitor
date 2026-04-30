# AI-SUMMARY: runtime 插件初始化模块
# 对应 INDEX.md §9 文件摘要索引

"""运行态状态文件相关工具。"""

from .json_store import clone_fallback, read_json, update_json, write_json

__all__ = ["clone_fallback", "read_json", "write_json", "update_json"]

