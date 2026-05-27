# Plan

## 步骤

1. [x] 审核每张表的实际读取方，确认有用/无用
2. [x] 删除无用表: funds, iopv_results, update_log
3. [x] 统一保留策略为 90 天（回测需要3个月）
4. [x] 删除 sync_funds()（config.yaml 是唯一真相）
5. [x] 本地测试通过
6. [x] 服务器部署验证通过（4907 行，全部 ≤90 天）
7. [x] systemd timer 已激活（每天 06:30）

## 审核结论

无用表（只写不读）：
- funds: 从未被读取，config.yaml 是真相
- iopv_results: 从未写入，IOPV 实时计算不存储
- update_log: 从未被读取

有用表（被 source.py 或 backtest_v2.py 读取）：
- etf_prices: source.py 查 nav-date 价格 + 回测
- stock_prices: source.py 查 nav-date 价格 + 回测
- fund_nav: 回测 3 个月净值
- fx_rates: 回测 3 个月汇率
- holdings: 回测 + B 类 IOPV 备用

## 数据量变化

改造前: ~23 万行（ETF 从 2001 年至今）
改造后: ~4907 行（全部 ≤90 天）