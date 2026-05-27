#!/usr/bin/env python3
"""
检查根目录是否有不应存在的临时文件。
根目录只允许：目录（黑名单外）、白名单文件、黑名单扩展名。
"""

import os
import sys
from pathlib import Path

# 允许的根目录文件（白名单）
ALLOWED_FILES = {
    "README.md",
    "CLAUDE.md", "AGENTS.md", "INDEX.md",
    "MEMORY.md",
    "package.json",
    "package-lock.json",
    "requirements.txt",
    "start_server.js",
    "data_dispatch.py",
    "config.yaml",
    ".gitignore",
    ".env.example",
}

# 允许的根目录目录（黑名单外）
ALLOWED_DIRS = {
    "config",
    "data_fetch",
    "docs",
    "presentation",
    "strategy",
    "notification",
    "shared",
    "tools",
    "tests",
    "ui",
    "specs",
    "missions",
    "templates",
    "archive", "scripts", "deploy", "runtime_data",
    "node_modules",
}

# 自动归档的目录（移动到 archive/）
AUTO_ARCHIVE = {
    "ops", "runtime_logs",
}

# 自动归档的文件模式
AUTO_ARCHIVE_PATTERNS = [
    "screenshot",
    "debug_",
    ".log",
    ".png",
]

ROOT = Path(__file__).parent.parent.resolve()


def is_temp_file(name: str) -> bool:
    for p in AUTO_ARCHIVE_PATTERNS:
        if p in name.lower():
            return True
    return False


def archive_file(src: Path, dry_run: bool = False) -> None:
    dest = ROOT / "archive" / src.name
    if dry_run:
        print(f"[DRY] mv {src} -> archive/")
    else:
        import shutil
        shutil.move(str(src), str(dest))
        print(f"moved: {src.name} -> archive/")


def check(dry_run: bool = False) -> bool:
    issues = []

    for item in os.listdir(ROOT):
        path = ROOT / item

        # 跳过白名单
        if item in ALLOWED_FILES:
            continue

        # 跳过允许的目录
        if path.is_dir() and item in ALLOWED_DIRS:
            continue

        # 自动归档的目录
        if item in AUTO_ARCHIVE:
            issues.append(f"dir: {item}/ (auto-archive)")
            if not dry_run:
                dest = ROOT / "archive" / item
                import shutil
                shutil.move(str(path), str(dest))
                print(f"moved: {item}/ -> archive/")
            continue

        # 根目录下的 .gitkeep 等允许
        if item.startswith("."):
            continue

        # 临时文件
        if path.is_file():
            if is_temp_file(item):
                issues.append(f"file: {item} (auto-archive)")
                archive_file(path, dry_run)
            else:
                issues.append(f"file: {item} (unknown)")

    if issues:
        print(f"\n发现 {len(issues)} 个问题:")
        for i in issues:
            print(f"  {i}")
        return False
    else:
        print("根目录干净")
        return True


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    ok = check(dry_run)
    sys.exit(0 if ok else 1)
