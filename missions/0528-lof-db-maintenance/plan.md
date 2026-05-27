# Plan

## 步骤

1. [x] 给 schema.py 增加 cleanup_old_data() 按表保留策略删除旧数据
2. [x] 修改 updater.py，update_all 后自动 cleanup + sync_funds
3. [x] 创建 scripts/lof_maintenance.py 独立维护入口
4. [x] 本地测试维护脚本（通过）
5. [x] 创建 deploy/lof_maintenance.service + deploy/lof_maintenance.timer
6. [x] Git push
7. [x] 服务器部署：SCP推送文件 + systemd timer 配置
8. [x] 服务器手动执行验证通过

## 验证结果

- [x] 本地 run scripts/lof_maintenance.py 成功
- [x] 服务器 run 成功: NAV 2400条, ETF 63239条, FX 254条, Holdings 55条
- [x] 清理生效: NAV删601, ETF删74832, stock删94408
- [x] systemd timer 已激活, 每天06:30触发

## 保留策略

| 表 | 保留天数 | 说明 |
|----|----------|------|
| fund_nav | 120天 | 足够回测40交易日 |
| etf_prices | 250天 | 约1年交易日 |
| stock_prices | 250天 | 同上 |
| fx_rates | 当年 | 只保留当前年份 |
| iopv_results | 30天 | 临时计算结果 |

## 风险

- GLD ETF 新浪拉取失败（assignment destination is read-only），不影响其他ETF
- 东方财富 NAV API 在服务器可正常访问