# 转债套利模块规格

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 范围

本规格定义 `转债套利` 容器页内的正式字段、公式、展示规则和接口合同。
容器页固定包含：
- `主页`
- `小额刚兑`

## 2. 小额刚兑筛选

- 仅展示 `price < 100` 的转债

## 3. 小额刚兑列顺序

1. 转债代码&名称
2. 转债价格&涨跌幅
3. 正股名称&代码
4. 正股价格&涨跌幅
5. 持有人数
6. 剩余规模
7. 刚兑金额
8. 刚兑收益率
9. 预期耗时
10. 刚兑年化
11. 刚兑总额
12. 负债敞口
13. 净资产
14. 期权价值
15. 期权年化
16. 总年化收益率

展示要求：
- `刚兑收益率` 与 `预期耗时` 表头黄色高亮
- `预期耗时` 单元格下方继续展示 `剩余期限`
- `负债敞口` 单元格纵向展示：负债敞口 / 有息负债 / 广义现金
- `刚兑年化` 为原有年化收益率字段，仅改名不删除

## 4. 计算合同

### 4.1 刚兑相关

- `smallRedemptionYield = 1 - price / 100`
- `smallRedemptionExpectedYears = remainingYears + 0.5`
- `smallRedemptionAnnualizedYield = (1 + smallRedemptionYield)^(1 / smallRedemptionExpectedYears) - 1`
- `smallRedemptionAmount = remainingSizeYi * 1e8 / holderCount * 0.825`
- `smallRedemptionTotalAmount = smallRedemptionAmount * holderCount`

### 4.2 小额刚兑专用期权价值

- `smallRedemptionOptionValue` 必须独立于主页 `optionValue`
- 小额刚兑口径下固定：
  - `smallRedemptionBondValue = 100`
  - `optionQty = 100 / convertPrice`
  - `smallRedemptionCallStrike = max(convertPrice, 100 / optionQty)`
- 当前模型下 `100 / optionQty` 与 `convertPrice` 等价，但字段仍按"小额刚兑专用口径重算"输出

### 4.3 期权年化

- `smallRedemptionOptionYield = smallRedemptionOptionValue / price`
- `smallRedemptionOptionAnnualizedYield = (1 + smallRedemptionOptionYield)^(1 / remainingYears) - 1`

### 4.4 总年化收益率

- `smallRedemptionTotalAnnualizedYield = smallRedemptionAnnualizedYield + smallRedemptionOptionAnnualizedYield`

## 5. 缺失值规则

- `holderCount` 为空：
  - `smallRedemptionAmount = null`
  - `smallRedemptionTotalAmount = null`
- `remainingYears` 为空或 `<= 0`：
  - `smallRedemptionExpectedYears = null`
  - `smallRedemptionAnnualizedYield = null`
  - `smallRedemptionOptionAnnualizedYield = null`
  - `smallRedemptionTotalAnnualizedYield = null`
- `smallRedemptionOptionValue` 无法计算：
  - `smallRedemptionOptionYield = null`
  - `smallRedemptionOptionAnnualizedYield = null`
  - `smallRedemptionTotalAnnualizedYield = null`

页面层将空值显示为 `--`。

## 6. 接口合同

### 6.1 路径

- `GET /api/market/convertible-bond-arbitrage`

### 6.2 顶层结构

```json
{
  "success": true,
  "data": [],
  "summary": {},
  "smallRedemption": {
    "rows": [],
    "summary": {},
    "meta": {
      "reportPeriod": "",
      "reportSourceUrl": "",
      "holderCountFallbackUsed": false
    }
  }
}
```

### 6.3 smallRedemption.rows 必需字段

- `remainingYears`
- `remainingSizeYi`
- `holderCount`
- `holderCountReportPeriod`
- `holderCountReportSourceUrl`
- `holderCountFallbackUsed`
- `smallRedemptionYield`
- `smallRedemptionExpectedYears`
- `smallRedemptionAnnualizedYield`
- `smallRedemptionAmount`
- `smallRedemptionTotalAmount`
- `smallRedemptionOptionValue`
- `smallRedemptionOptionYield`
- `smallRedemptionOptionAnnualizedYield`
- `smallRedemptionTotalAnnualizedYield`
- `stockNetAssetsYi`
- `stockInterestBearingDebtYi`
- `stockBroadCashYi`
- `stockNetDebtExposureYi`

## 7. 展示规则

- `刚兑收益率` 与 `预期耗时` 表头继续黄色高亮
- `预期耗时` 单元格显示两行：预期耗时 / 剩余期限
- `负债敞口` 单元格显示三行：负债敞口 / 有息负债 / 广义现金
- `刚兑年化`、`期权年化`、`总年化收益率` 均为独立列

## 8. 推送规则

- 小额刚兑标的独立推送不再输出 `刚兑收益率`
- 改为输出 `总年化收益率`

## 9. 数据要求

- 持有人数优先最新半年报或年报；取不到时回退最近一次成功解析的定期报告
- 新入库标的首次出现时必须抓取一次
- 财务字段继续使用真实报告口径，不伪造

## 10. 刷新与推送完整性

- `data_fetch.plugins.convertible_bond.refresh_interval_ms = 60000`
- `data_fetch.plugins.convertible_bond.spot_cache_ttl_ms = 60000`
- 页面在 `转债套利` 当前页自动刷新时，必须主动请求最新 `cbArb` 数据
- 转债折价套利独立推送发送前必须强制刷新 `cbArb` 数据
- 推送正文使用紧凑逐行格式，候选标的默认全部进入正文；若仍超过企业微信长度限制，由统一发送层截断并保留实时网页入口

## 11. 验证规则

- smallRedemption 表格列顺序符合本规格
- `刚兑年化` 保留
- `期权年化` 与 `总年化收益率` 新增成功
- 推送文案不再输出 `刚兑收益率`
- 推送文案改为输出 `总年化收益率`
- `smallRedemptionOptionYield = smallRedemptionOptionValue / price`
- `smallRedemptionOptionAnnualizedYield` 使用 `remainingYears`
- `smallRedemptionTotalAnnualizedYield = smallRedemptionAnnualizedYield + smallRedemptionOptionAnnualizedYield`
