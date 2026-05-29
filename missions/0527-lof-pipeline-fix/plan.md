# LOF 全链修复 Plan

## 步骤

1. [x] config.yaml: 集中基金列表 (27只) + daily_incremental_sync=true
2. [x] fetcher.py: 从 config 读取基金列表 + ETF涨跌幅双源获取
3. [x] service.py: 修复回测加载路径 + A类估值加入ETF涨幅
4. [x] nav_updater.py: 从 config 读基金列表
5. [x] holdings_updater.py: 从 config 读B类基金列表
6. [x] etf_updater.py: 从 config 提取 ETF 列表
7. [x] backtest.py: 统一为权威版本，config驱动，输出 lof_all_r2_results.json
8. [x] data_dispatch.py: 新增 lof-db-sync action
9. [x] start_server.js: lofArb.dailySync 接入 lof-db-sync
10. [x] 冗余回测脚本归档 (4个)

## 验证
- config.yaml 是基金列表唯一来源: YES
- daily_incremental_sync 已开启: YES
- 回测结果优先加载 lof_all_r2_results.json: YES
- ETF 涨幅双源 fallback: YES
- A类公式完整 (NAV * ETF涨幅 * 汇率): YES

## 风险
- ETF 腾讯行情格式需服务器验证（本地无Python）
- 需 git push 后服务器重启生效
