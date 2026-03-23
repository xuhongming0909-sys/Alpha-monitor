#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""检查宪法主文件与镜像文件是否保持同步。"""

from __future__ import annotations

import difflib
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT_DIR / "CONSTITUTION.md"
MIRROR_PATH = ROOT_DIR / ".specify" / "memory" / "constitution.md"


def normalize_text(text: str) -> str:
    """统一换行，避免仅因 CRLF/LF 差异触发误报。"""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.rstrip("\n")


def read_utf8(path: Path) -> str:
    """读取 UTF-8 文本；缺失文件交给上层统一处理。"""

    return path.read_text(encoding="utf-8")


def build_diff_preview(left: str, right: str, *, limit: int = 80) -> str:
    """生成有限长度的 unified diff，方便快速定位漂移位置。"""

    diff_lines = list(
        difflib.unified_diff(
            left.splitlines(),
            right.splitlines(),
            fromfile=str(SOURCE_PATH.relative_to(ROOT_DIR)),
            tofile=str(MIRROR_PATH.relative_to(ROOT_DIR)),
            lineterm="",
        )
    )
    if not diff_lines:
        return ""
    preview = diff_lines[:limit]
    if len(diff_lines) > limit:
        preview.append("... diff truncated ...")
    return "\n".join(preview)


def main() -> int:
    """执行同步校验并输出结果。"""

    missing = [path for path in (SOURCE_PATH, MIRROR_PATH) if not path.exists()]
    if missing:
        for path in missing:
            print(f"[constitution-sync] 缺少文件: {path.relative_to(ROOT_DIR)}", file=sys.stderr)
        return 1

    source_text = normalize_text(read_utf8(SOURCE_PATH))
    mirror_text = normalize_text(read_utf8(MIRROR_PATH))
    if source_text != mirror_text:
        print("[constitution-sync] 宪法文件不同步。", file=sys.stderr)
        preview = build_diff_preview(source_text, mirror_text)
        if preview:
            print(preview, file=sys.stderr)
        return 1

    print("[constitution-sync] 宪法主文件与镜像文件已同步。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
