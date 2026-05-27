---
name: lof-backtest-cleanup
type: implementation
---

# LOF 回测链清理 — Spec

## 背景
上一轮修复（0527-lof-pipeline-fix）多轮修改互相覆盖、无验证，实际效果：
- backtest.py 的 save_results 和 config loader 修改丢失
- fetcher.py 的 _fetch_etf_changes 修改丢失
- service.py 回测加载改为读 lof_all_r2_results.json，但该文件字段名(max_err/sample)与service.py读取的字段名(maxErr/samplePeriod)不匹配
- 原始的 a_results.json 和 b_results.json 实际有完整数据，字段名匹配，原来的读取逻辑是对的

## 要修复的问题（确认版）

### P1: 回测脚本 vs service 字段名不对齐
- backtest.py 输出: max_err, tag
- lof_all_r2_results.json 输出: max_err, sample  
- service.py 读取: maxErr, samplePeriod
- a_results.json/b_results.json: maxErr, samplePeriod (正确)

**方案**: backtest.py 输出字段名对齐 service.py 的期望（maxErr, samplePeriod），输出到 a_results.json

### P2: fetcher.py 缺少 ETF 涨幅获取
- A类 IOPV = NAV * (1 + etf_ret) * fx_ratio
- 当前 _calc_a 被简化为只有汇率修正，etf_ret=0
- fetcher.py 不获取也不传递 ETF 涨幅

**方案**: fetcher.py 加 _fetch_etf_changes()，传 etfChange 字段；service.py _calc_a 使用它

### P3: 回测数据源混乱
- backtest.py 从 lof.db 读（但DB数据可能不全/过期）
- lof_all_r2_results.json 来自已归档的 backtest_all.py（直拉API）
- a_results.json/b_results.json 来源不明（可能是 backtest_a_cn.py 的输出）

**方案**: 确定唯一权威数据源 → lof.db。backtest.py 从DB读，输出到 a_results.json

### P4: 基金列表散落
- fetcher.py: QDII_FUNDS 硬编码（上一轮config loader丢失）
- nav_updater.py: A_FUNDS/B_FUNDS 硬编码
- config.yaml: 已有 funds 列表（上一轮添加的仍存在）

**方案**: 所有Python模块从 config.yaml 读基金列表

### P5: 文件清理
- archive/lof_backtest_deprecated/ 有5个已归档文件
- runtime_data/backtest/ 有6个历史文件（all31_etf.json等）

**方案**: 保留必要文件，清理确认无用的

## 不动
- AGENTS.md
- UI 组件
- 推送逻辑
- config.yaml funds 列表（已正确）

## 约束
- 遵循 AGENTS.md: 先出spec → 确认 → 实现 → 验证
- 每个修改验证后交付
- 代码文件 < 1000行
- 核心注释中文

## 输入/输出/边界

### backtest.py
- 输入: lof.db (fund_nav, etf_prices, funds表)
- 输出: runtime_data/backtest/a_results.json (dict格式，字段: r2, mae, maxErr, samplePeriod)
- 边界: 无数据返回 None，样本<10跳过

### fetcher.py
- 输入: config.yaml funds列表, 东财API, 腾讯行情, 集思录
- 输出: 每个基金带 etfChange 字段的dict
- 边界: ETF涨幅获取失败 → etfChange=None → service标记"无ETF数据"

### service.py
- 输入: fetcher payload + a_results.json + b_results.json
- 输出: 含 r2, mae, maxErr, samplePeriod 的估值结果
- 边界: 无回测数据 → 这些字段显示 None → UI显示"--"
