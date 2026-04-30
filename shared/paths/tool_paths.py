# AI-SUMMARY: paths 路径解析：运行时目录与文件路径
# 对应 INDEX.md §9 文件摘要索引

"""tools目录引导器。
为抓取层和共享服务补充tools目录到 sys.path，避免在多个模块里重复写路径拼接。"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_scripts_on_path() -> Path:
    """确保scripts目录可被 import，并返回目录路径。"""

    scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
    scripts_text = str(scripts_dir)
    if scripts_text not in sys.path:
        sys.path.insert(0, scripts_text)
    return scripts_dir

