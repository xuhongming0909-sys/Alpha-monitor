# Plan: 0430-fix-cb-table

## Steps
1. 确认数据字段可用性 (volatility250, optionValue, theoreticalPrice, pureBondValue, stockMarketValueYi, bondToStockMarketValueRatio, maturityDate, rating, forceRedeemStatus)
2. 修改 TabNav 标签名
3. 修改 OpportunityCommandCenter 过滤标签
4. 重构 ConvertibleTable 的 renderMainTable: 添加 usePagination, 重排列, 补充缺失字段显示, 修复波动率显示
5. 推导转股状态逻辑
6. 构建验证
7. Git 提交并推送

## Verification
- `npx esbuild src/App.jsx --bundle --outfile=/tmp/test.js --format=cjs` 编译通过

## Results
- 编译通过，无报错
- 变更文件: `ui/src/App.jsx`

## Risks
- 转股状态推导依赖日期比较，可能存在时区边界问题（已使用 ISO date string 比较规避）
