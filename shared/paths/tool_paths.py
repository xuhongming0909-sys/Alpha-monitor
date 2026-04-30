"""tools目录引导器。
为抓取层和共享服务补充tools目录到 sys.path，避免在多个模块里重复写路径拼接。"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_scripts_on_path() -> Path:
    """确保tools目录可被 import，并返回目录路径。"""

    scripts_dir = Path(__file__).resolve().parents[2] / "tools"
    scripts_text = str(scripts_dir)
    if scripts_text not in sys.path:
        sys.path.insert(0, scripts_text)
    return scripts_dir

