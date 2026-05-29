# Mission: LOF 全链路代码审查修复
## 执行结果

### 修复清单（18项）

| # | 优先级 | 文件 | 修复内容 | 状态 |
|---|--------|------|----------|------|
| 1 | P0 | calc.py | HKD汇率映射: 美元→港币 | ✅ |
| 2 | P0 | backtest_v2.py | 多币种FX查询(不再硬编码USD) | ✅ |
| 3 | P0 | source.py | KeyError: fund["etf_tickers"]→.get() | ✅ |
| 4 | P1 | source.py | pop污染: .pop()→.get() | ✅ |
| 5 | P1 | service.py | FX基准日期范围限制(+10天) | ✅ |
| 6 | P1 | fx_updater.py | 增量更新(不再全量拉一年) | ✅ |
| 7 | P1 | nav_updater.py | INSERT计数用rowcount | ✅ |
| 8 | P2 | calc.py | 统一calc_iopv函数(A+B类) | ✅ |
| 9 | P1 | etf_updater.py | 动态ETF列表(从fund_classifier) | ✅ |
| 10 | P1 | backtest_v2.py | B类回测优先读DB持仓 | ✅ |
| 11 | P2 | service.py | FX fallback链重构为_resolve_fx_rates | ✅ |
| 12 | P2 | schema.py | 添加db_conn() context manager | ✅ |
| 13 | P1 | service.py | _monitor_pools阈值可配置 | ✅ |
| 14 | P2 | shared/db_context.py | 通用DB context manager | ✅ 新建 |
| 15 | P2 | notification/service.js | 推送条件放宽(无限购+3%, 5%强推) | ✅ |
| 16 | P2 | specs/lof-arbitrage.md | 公式同步(加归一化说明) | ✅ |
| 17 | P2 | scripts/lof_maintenance.py | 错误聚合(不中断) | ✅ |
| 18 | P2 | deploy/sync_server.ps1 | Windows版部署脚本 | ✅ 新建 |

### 测试

- tests/test_lof_calc.py: 14 tests ✅
- tests/test_lof_backtest.py: 3 tests ✅
- tests/test_lof_service.py: 7 tests ✅
- tests/test_data_fetch_structure.py: 7 tests ✅ (无回归)
- 共 31 tests, 全部通过

### 新增文件
- shared/db_context.py — DB context manager
- deploy/sync_server.ps1 — Windows部署脚本
- tests/test_lof_calc.py — calc.py单元测试
- tests/test_lof_backtest.py — backtest单元测试
- tests/test_lof_service.py — service单元测试

### 注意事项
- calc.py中文注释有编码问题(功能不影响，仅注释显示异常)
- #13 #14 (缓存优化) 未实现，属于P3性能优化
- #20 (LofCardList列优先级) 未实现，属于P3 UI优化
