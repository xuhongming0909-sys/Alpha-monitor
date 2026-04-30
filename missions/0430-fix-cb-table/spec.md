# Mission Spec: 0430-fix-cb-table

## Type
Implementation

## Goal
修复转债套利主页的标签名称、数据列顺序、缺失字段补充、波动率显示以及分页功能。

## Scope
- UI: `ui/src/App.jsx`
- 可转债套利主表展示逻辑

## Changes
1. Tab 标签名: `转债` → `转债套利`
2. 机会面板过滤标签同步更新
3. 主表列重排为: 转债名称、转债价格、涨跌幅、正股名称、正股价格、转股价格、转股价值、转股溢价率、剩余规模、正股流通市值、转债占比、纯债价值、波动率、期权价值(原理论期权)、理论价值、理论套利空间、到期日、评级、强赎状态、转股状态
4. 波动率显示: 原始值为年化小数(如0.225)，显示时乘以100并带%符号
5. 分页: 每页50条，支持翻页
6. 转股状态: 根据delistDate、convertStartDate、forceRedeemStatus、maturityDate动态推导

## Impact on Specs
无
