# 任务：拆分超 1000 行文件

## 目标

按 CLAUDE.md §9 文件大小规则，拆分超过 1000 行的核心代码文件。

## 背景

INDEX.md 新增规则：任何代码文件不得超过 1000 行。
扫描发现 3 个文件超标。

## 范围

- `presentation/dashboard/dashboard_page.js` (5666行) → constants.js + dashboard_page.js
- `data_fetch/convertible_bond/source.py` (3085行) → cb_metrics.py + source.py
- `start_server.js` (3247行) → server_config_loader.js + start_server.js

## 完成标准

- 新文件均添加 AI-SUMMARY 注释
- INDEX.md §9 文件索引更新
- 语法检查通过