---
name: lof-pipeline-fix
type: implementation
---

# LOF 全链修复

## 目标
修复 LOF IOPV 管道6个关键问题：管道断裂、回测结果未加载、数据源不稳定、回测脚本碎片化、基金列表散落、DB无自动调度。

## 范围
- config.yaml：集中基金列表 + 开启 daily_incremental_sync
- strategy/lof_iopv/service.py：修复回测结果加载路径
- data_fetch/lof_iopv/fetcher.py：从 config 读取基金列表 + ETF fallback
- data_fetch/lof_db/nav_updater.py：从 config/DB 读取基金列表
- data_fetch/lof_db/updater.py：接入 data_dispatch.py 调度
- 回测脚本：合并为1个权威版本，输出统一路径
- 删除冗余脚本

## 不动
- AGENTS.md
- 推送 markdown 格式（不在本次范围）
- UI React 组件（数据修复后自动恢复）

## 约束
- 保持服务器兼容（Node.js 调 Python 子进程）
- 不引入新依赖

## 验证
- service.py 能加载回测结果
- config.yaml 是基金列表唯一来源
- DB daily sync 开启
- 回测脚本统一为1个
