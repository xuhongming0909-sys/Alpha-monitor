# Mission Plan

## Steps
1. [done] 扫描A/B类残留分布
2. [done] calc.py: rm calc_a_iopv, rename calc_b_iopv->calc_iopv
3. [done] backtest_v2.py: rm backtest_a, rename backtest_b->backtest_fund
4. [done] service.py: rm A branch
5. [done] source.py: rm ETF code + estimation
6. [done] 删除 backtest.py, backtest_t10.py, classifier.py
7. [done] config.yaml: rm estimation fields
8. [done] holdings_updater.py: rm estimation filter
9. [done] INDEX.md: update

## Validation
- [x] 无calc_a_iopv/calc_b_iopv引用
- [x] 无estimation引用(production code)
- [x] 文件语法OK(parens balanced)
- [x] INDEX.md同步

## Results
- 删除3个废弃文件
- 统一公式: IOPV = NAV * (1 + stock_ratio/100 * weighted_ret) * fx_ratio
- 代码行数: calc 98->103, backtest 290->208, service 217->183, source 470->368