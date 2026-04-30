# Alpha Monitor 生效规格说明

状态：当前生效版本  
日期：2026-04-24

## 1. 范围

本规格定义当前 `小额刚兑` 页的正式字段、公式和展示规则，并声明后续 UI 实现必须遵守 `docs/UI_DESIGN.md`。

## 2. 页面规格

### 2.1 模块结构

- `转债套利` 作为容器页，内部固定包含：
  - `主页`
  - `小额刚兑`

### 2.2 小额刚兑筛选

- `price < 100`

### 2.3 小额刚兑列顺序

1. bond identity
2. bond quote
3. stock identity
4. stock quote
5. holderCount
6. remainingSizeYi
7. smallRedemptionAmount
8. smallRedemptionYield
9. smallRedemptionExpectedYears
10. smallRedemptionAnnualizedYield
11. smallRedemptionTotalAmount
12. stockNetDebtExposureYi
13. stockNetAssetsYi
14. smallRedemptionOptionValue
15. smallRedemptionOptionAnnualizedYield
16. smallRedemptionTotalAnnualizedYield

中文展示名固定为：

1. 可转债代码&名称
2. 可转债价格&涨跌幅
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

## 3. 接口合同

### 3.1 路径

- `GET /api/market/convertible-bond-arbitrage`

### 3.2 顶层结构

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

### 3.3 smallRedemption.rows 必需字段

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

## 4. 计算合同

### 4.1 刚兑相关

- `smallRedemptionYield = 1 - price / 100`
- `smallRedemptionExpectedYears = remainingYears + 0.5`
- `smallRedemptionAnnualizedYield = (1 + smallRedemptionYield)^(1 / smallRedemptionExpectedYears) - 1`
- `smallRedemptionAmount = remainingSizeYi * 1e8 / holderCount * 0.825`
- `smallRedemptionTotalAmount = smallRedemptionAmount * holderCount`

说明：

- `smallRedemptionAnnualizedYield` 在页面展示名固定为 `刚兑年化`

### 4.2 小额刚兑专用期权价值

- `smallRedemptionOptionValue` 必须独立于主页 `optionValue`
- 小额刚兑口径下固定：
  - `smallRedemptionBondValue = 100`
  - `optionQty = 100 / convertPrice`
  - `smallRedemptionCallStrike = max(convertPrice, 100 / optionQty)`

在当前模型下：

- `100 / optionQty` 与 `convertPrice` 等价
- 但字段仍按“小额刚兑专用口径重算”输出，不与主页共用

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

页面层将上述空值显示为 `--`。

## 6. 展示规则

- `刚兑收益率` 与 `预期耗时` 表头继续黄色高亮
- `预期耗时` 单元格显示两行：
  - 预期耗时
  - 剩余期限
- `负债敞口` 单元格显示三行：
  - 负债敞口
  - 有息负债
  - 广义现金
- `刚兑年化` 为独立列
- `期权年化` 为独立列
- `总年化收益率` 为独立列

## 7. 推送规则

- 小额刚兑标的的独立推送不再输出 `刚兑收益率`
- 改为输出 `总年化收益率`

## 8. 真实数据规则

- 持有人数优先最新半年报或年报
- 取不到时回退最近一次成功解析的定期报告
- 新入库标的首次出现时必须抓取一次
- 财务字段继续使用真实报告口径，不伪造

## 9. 验证规则

必须覆盖以下检查：

- smallRedemption 表格列顺序符合本规格
- `刚兑年化` 保留
- `期权年化` 与 `总年化收益率` 新增成功
- 推送文案不再输出 `刚兑收益率`
- 推送文案改为输出 `总年化收益率`
- `smallRedemptionOptionYield = smallRedemptionOptionValue / price`
- `smallRedemptionOptionAnnualizedYield` 使用 `remainingYears`
- `smallRedemptionTotalAnnualizedYield = smallRedemptionAnnualizedYield + smallRedemptionOptionAnnualizedYield`

## 当前生效补充规格：刷新与推送完整性

- `data_fetch.plugins.convertible_bond.refresh_interval_ms = 60000`
- `data_fetch.plugins.convertible_bond.spot_cache_ttl_ms = 60000`
- 页面在 `可转债套利` 当前页自动刷新时，必须主动请求最新 `cbArb` 数据。
- 可转债折价套利独立推送发送前必须强制刷新 `cbArb` 数据。
- 推送正文使用紧凑逐行格式，候选标的默认全部进入正文；若仍超过企业微信长度限制，由统一发送层截断并保留实时网页入口。
## 当前生效补充规格：UI 设计规范

- `docs/UI_DESIGN.md` 是 Alpha Monitor 后续页面设计、React 重做和 UI 验收的上游约束。
- 页面 UI 必须采用 Bloomberg 终端式金融界面方向：高密度、数字优先、低装饰。
- UI 实现必须使用系统中文字体与等宽数字字体栈，不引入商业字体或外部字体服务。
- 1440px 桌面首屏必须同时展示系统状态、机会排序和至少一个高密度数据区。
- 表格数字默认右对齐，价格、百分比、金额、代码和时间必须使用等宽数字规则。
- 红、绿、黄只表达数据语义；禁止大 hero、宽松卡片、营销式渐变和低信息密度留白。
- 任何 UI 代码实现前，必须通过 `docs/UI_DESIGN.md` 的验收清单。
## 当前生效补充规格：React 金融终端 UI

- 默认首页 `/` 托管 React + Vite 构建产物，静态产物目录为 `ui/dist`。
- 旧 HTML 看板通过 `/legacy` 保留，继续使用原 `presentation.dashboard_entry` 指向的模板文件。
- React UI 必须消费现有真实接口：`/api/health`、`/api/dashboard/ui-config`、`/api/dashboard/resource-status`、`/api/market/convertible-bond-arbitrage`、`/api/market/ah`、`/api/market/ab`、`/api/market/lof-arbitrage`、`/api/monitors`。
- React UI 首屏必须包含顶部状态栏、机会排序区和高密度表格区。
- 机会排序只能基于接口返回的真实字段生成，不得创建伪造综合分。
- 根项目必须提供 `npm run ui:build` 与 `npm run ui:check`。

