---
name: lof-backtest-cleanup
type: implementation
---

# LOF 回测链+估值链清理

## 目标
修复 A/B 类 IOPV 估值的核心计算缺陷，清理回测代码和数据文件，统一数据源。

## 修复项

### F1: A类 ETF 涨幅获取 [P0]
- fetcher.py: 新增 _fetch_etf_changes(), 东财 secid=107 昨收+现价算涨幅，腾讯 fallback
- fetcher.py: 每行输出增加 etfChange 字段
- service.py _calc_a: 使用 etfChange 计算 IOPV = NAV * (1 + etf_ret) * fx_ratio

### F2: B类持仓加权收益率 [P1]
- shared/market_service.py get_quotes: 增加 prev_close 字段（腾讯 parts[4]）
- fetcher.py: 持仓股票行情同时获取 prev_close，传 holdingsPrevClose 字段
- service.py _calc_b: 计算 est = NAV * (1 + stock_ratio * Σ(w_i * ret_i)) * fx_ratio

### F3: service.py 回测字段名对齐 [P2]
- 恢复优先读 a_results.json + b_results.json（字段名匹配: maxErr, samplePeriod）
- 删除上轮错误引入的 lof_all_r2_results.json 优先加载

### F4: backtest 重写 [P3]
- 删除现有 backtest.py（无保存、硬编码权重、无config loader）
- 新建 backtest_a.py: 从DB读，输出 a_results.json (dict格式，字段对齐service)
- 新建 backtest_b.py: 从DB读，输出 b_results.json (dict格式，字段对齐service)
- 两个文件从 config.yaml 读基金列表

### F5: 文件清理 [P4]
- 删除 runtime_data/backtest/ 下无用文件:
  all31_etf.json, all31_nav.json, lof13_nav.json, lof13_etf_prices.json
  lof_all_r2_results.json, lof27_r2_results.json, lof_all_r2_report.md
  qdii_backtest_A_output.txt, qdii_backtest_B_output.txt, qdii_holdings.json
- 保留: a_results.json, b_results.json
- 删除 archive/lof_backtest_deprecated/ 整个目录

### F6: nav_updater.py 去硬编码 [P5]
- 从 config.yaml 读基金列表

### F7: stockPosition 兜底值 [P5]
- service.py _calc_b: 兜底从 90.0 改为 None → 返回"仓位缺失"而非假数据

## 不动
- AGENTS.md
- config.yaml（已有 funds 列表，不动）
- 推送逻辑
- UI 组件
- lof_db 模块（保留为回测数据源，明确标记为"回测专用"）
- iopv_calculator.py（不接入主链路，保持回测专用）

## 约束
- 遵循 AGENTS.md TDD: 先写测试行为 → 再实现
- 每步验证文件写入成功
- 代码 < 1000 行，核心注释中文

## 验证标准
- [ ] fetcher.py 输出含 etfChange 字段
- [ ] service.py _calc_a 使用 etf_ret
- [ ] service.py _calc_b 使用持仓加权收益
- [ ] get_quotes 返回 prev_close
- [ ] a_results.json 字段: r2, mae, maxErr, samplePeriod
- [ ] service.py 正确加载回测数据
- [ ] runtime_data/backtest/ 只剩 a_results.json + b_results.json
- [ ] 无硬编码基金列表
