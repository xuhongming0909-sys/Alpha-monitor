# T10 IOPV 回测系统 Spec

## 核心公式
predicted_nav = prev_nav * (1 + weighted_return) * fx_ratio
weighted_return = sum(w_i * ret_i) / sum(w_i)  只算有价格的持仓
fx_ratio = fx_now / fx_base

## 数据源(全部即时抓取)
1. 季报持仓: fund_announcement_report_em -> PDF下载 -> 提取前10大
2. 价格: 美股stock_us_daily, 港股stock_hk_daily, A股stock_zh_a_hist
3. NAV: fund_open_fund_info_em
4. 汇率: akshare currency
5. 现金比例: fund_individual_detail_hold_xq -> sp=100-现金

## 市场过滤
只保留 A股/港股/美股，剔除日本/欧洲等
归一化: valid持仓比例放缩到100%

## 文件
- fetch.py - 数据抓取
- calc.py - T10计算
- backtest.py - 回测
- run.py - 主入口
- qreport/ - PDF缓存
