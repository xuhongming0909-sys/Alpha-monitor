# LOF 回测链+估值链清理 Plan

## 执行步骤

### F1: A类 ETF 涨幅 [P0] ✅
- market_service.py: get_quotes 增加 prev_close 字段
- fetcher.py: 新增 _fetch_etf_changes() 东财+腾讯双源
- fetcher.py: 每行输出 etfChange 字段
- service.py _calc_a: 已有 etf_ret 逻辑，fetcher 传值后自动生效

### F2: B类持仓加权 [P1] ✅
- fetcher.py: 收集 holdingsPrevClose (持仓股前收价)
- service.py _calc_b: 使用 Σ(w_i * ret_i) 计算加权收益

### F3: 回测字段名对齐 [P2] ✅
- service.py: 只加载 a_results.json + b_results.json (字段匹配)

### F4: 回测脚本重写 [P3] ✅
- 删除 backtest.py (归档)
- 新建 backtest_a.py: 从DB读, 输出 a_results.json, 字段 maxErr/samplePeriod
- 新建 backtest_b.py: 从DB读, 输出 b_results.json, 字段 maxErr/samplePeriod

### F5: 文件清理 [P4] ✅
- runtime_data/backtest/: 只保留 a_results.json + b_results.json
- 归档 10 个无用文件

### F6: nav_updater 去硬编码 [P5] ✅
- 从 config.yaml 读取基金列表

### F7: stockPosition 兜底 [P5] ✅
- _calc_b: 90.0 改为 None → 返回"仓位缺失"

## 验证
- [x] fetcher.py 输出含 etfChange
- [x] fetcher.py 输出含 holdingsPrevClose
- [x] service.py _calc_a 使用 etf_ret
- [x] service.py _calc_b 使用 weighted_ret
- [x] get_quotes 返回 prev_close
- [x] backtest_a.py 字段: maxErr, samplePeriod
- [x] backtest_b.py 字段: maxErr, samplePeriod
- [x] service.py 只加载 a_results + b_results
- [x] runtime_data/backtest/ 只剩 2 个文件
- [x] nav_updater 从 config 读取
- [x] _calc_b 无 90.0 兜底

## 待服务器验证
- ETF 涨幅 API 是否可通（东财 secid=107）
- B类持仓股前收价是否可获取
- git push 后重启
