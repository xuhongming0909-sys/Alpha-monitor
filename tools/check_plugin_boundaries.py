#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""检查 data_fetch/ 与 strategy/ 插件是否违反“只能依赖 shared/ 和自身插件”的边界规则。"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Iterable


ROOT_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DOMAINS = ("data_fetch", "strategy")
CHECK_SUFFIXES = {".py", ".js"}
JS_IMPORT_PATTERNS = [
    re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)"""),
    re.compile(r"""from\s+['"]([^'"]+)['"]"""),
    re.compile(r"""import\s+['"]([^'"]+)['"]"""),
]


def iter_plugin_files() -> Iterable[Path]:
    """遍历所有需要检查的插件代码文件。"""

    for domain in PLUGIN_DOMAINS:
        base_dir = ROOT_DIR / domain
        if not base_dir.exists():
            continue
        for path in base_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in CHECK_SUFFIXES:
                continue
            if "__pycache__" in path.parts:
                continue
            yield path


def plugin_scope_for(path: Path) -> tuple[str, str] | None:
    """识别文件属于哪个域和哪个插件。"""

    relative = path.relative_to(ROOT_DIR)
    parts = relative.parts
    if len(parts) < 3:
        return None
    domain, plugin = parts[0], parts[1]
    if domain not in PLUGIN_DOMAINS:
        return None
    return domain, plugin


def is_allowed_module_target(target: str, domain: str, plugin: str) -> bool:
    """判断 Python 绝对导入是否仍在允许范围内。"""

    if not target:
        return True
    if target.startswith("shared."):
        return True
    if target in {"shared"}:
        return True
    if target.startswith(f"{domain}.{plugin}.") or target == f"{domain}.{plugin}":
        return True
    if target.startswith("data_fetch.") or target == "data_fetch":
        return False
    if target.startswith("strategy.") or target == "strategy":
        return False
    if target.startswith("presentation.") or target == "presentation":
        return False
    if target.startswith("notification.") or target == "notification":
        return False
    return True


def resolve_relative_python_import(path: Path, node: ast.ImportFrom) -> str | None:
    """把 Python 相对导入尽量解析成项目相对模块路径。"""

    module_parts = list(path.relative_to(ROOT_DIR).with_suffix("").parts[:-1])
    if node.level > len(module_parts):
        return None
    base_parts = module_parts[: len(module_parts) - node.level]
    if node.module:
        base_parts.extend(node.module.split("."))
    return ".".join(base_parts)


def check_python_file(path: Path, domain: str, plugin: str) -> list[str]:
    """检查 Python 文件中的导入边界。"""

    violations: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = alias.name
                if not is_allowed_module_target(target, domain, plugin):
                    violations.append(f"{path}: import {target}")
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                target = resolve_relative_python_import(path, node)
                if target and not is_allowed_module_target(target, domain, plugin):
                    violations.append(f"{path}: from {'.' * node.level}{node.module or ''}")
            else:
                target = node.module or ""
                if not is_allowed_module_target(target, domain, plugin):
                    violations.append(f"{path}: from {target}")

    return violations


def normalize_js_target(current_path: Path, target: str) -> str:
    """把 JS 导入路径统一转换成项目相对路径文本。"""

    if target.startswith("."):
        resolved = (current_path.parent / target).resolve()
        try:
            return resolved.relative_to(ROOT_DIR).as_posix()
        except ValueError:
            return resolved.as_posix()
    return target.replace("\\", "/")


def is_allowed_js_target(target: str, domain: str, plugin: str) -> bool:
    """判断 JS 导入路径是否越界。"""

    if not target:
        return True
    normalized = target.replace("\\", "/")
    if normalized.startswith("shared/"):
        return True
    if normalized.startswith(f"{domain}/{plugin}/"):
        return True
    if normalized == f"{domain}/{plugin}":
        return True
    if normalized.startswith("data_fetch/"):
        return False
    if normalized.startswith("strategy/"):
        return False
    if normalized.startswith("presentation/"):
        return False
    if normalized.startswith("notification/"):
        return False
    return True


def check_js_file(path: Path, domain: str, plugin: str) -> list[str]:
    """检查 JS 文件中的 require/import 边界。"""

    violations: list[str] = []
    text = path.read_text(encoding="utf-8")

    for pattern in JS_IMPORT_PATTERNS:
        for match in pattern.finditer(text):
            raw_target = match.group(1).strip()
            normalized_target = normalize_js_target(path, raw_target)
            if not is_allowed_js_target(normalized_target, domain, plugin):
                violations.append(f"{path}: import {raw_target}")

    return violations


def main() -> int:
    """执行检查并返回退出码。"""

    violations: list[str] = []

    for path in iter_plugin_files():
        scope = plugin_scope_for(path)
        if not scope:
            continue
        domain, plugin = scope
        if path.suffix == ".py":
            violations.extend(check_python_file(path, domain, plugin))
        elif path.suffix == ".js":
            violations.extend(check_js_file(path, domain, plugin))

    if violations:
        print("插件边界检查失败：")
        for item in violations:
            print(f"- {item}")
        return 1

    print("插件边界检查通过：未发现跨插件非法依赖。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


