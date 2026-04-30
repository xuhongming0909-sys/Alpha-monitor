# Alpha Monitor 需求手册

状态：当前生效版本  
日期：2026-04-24

## 1. 文档定位

本文档定义当前正式生效的产品需求，只保留当前版本需要实现和维护的要求。`小额刚兑` 为当前业务功能需求；UI 设计规范为后续页面设计与实现的前置约束。

## 2. 产品边界

- 只使用真实市场数据、真实定期报告和真实接口
- 任一字段抓不到时显示 `--`，不伪造
- 本轮只调整 `小额刚兑` 页的收益结构，不扩展其他模块

## 3. 页面结构

### 3.1 模块位置

- 一级导航数量不变
- `转债套利` 面板内保留：
  - `主页`
  - `小额刚兑`

### 3.2 小额刚兑入选条件

- 仅展示 `price < 100` 的可转债

### 3.3 小额刚兑表格列

固定列顺序为：

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

展示要求：

- `刚兑收益率` 与 `预期耗时` 仍为黄色高亮表头
- `预期耗时` 单元格下方继续展示 `剩余期限`
- `负债敞口` 单元格继续纵向展示：
  - 负债敞口
  - 有息负债
  - 广义现金
- `刚兑年化` 为原有年化收益率字段，仅改名，不删除

## 4. 小额刚兑计算口径

### 4.1 原有口径保留

- `刚兑收益率 = 1 - price / 100`
- `预期耗时 = remainingYears + 0.5`
- `刚兑年化` 继续沿用现有刚兑收益率的年化公式
- `刚兑金额 = remainingSizeYi * 1e8 / holderCount * 82.5%`
- `刚兑总额 = 刚兑金额 * holderCount`
- `负债敞口 = interestBearingDebtYi - broadCashYi`

### 4.2 小额刚兑专用期权价值

- `期权价值` 不能直接复用主页 `optionValue`
- 小额刚兑口径下，纯债价值固定视为 `100`
- 基于该口径重新计算小额刚兑专用期权价值，字段名为 `smallRedemptionOptionValue`

### 4.3 期权年化

- 先计算 `期权收益率 = smallRedemptionOptionValue / price`
- 再按 `remainingYears` 计算 `期权年化`
- `期权年化` 不再使用上一轮的 `(100 + optionValue) / price - 1`

### 4.4 总年化收益率

- `总年化收益率 = 刚兑年化 + 期权年化`

## 5. 数据要求

### 5.1 持有人数

- 来自真实半年报或年报
- 优先最新定期报告
- 最新报告取不到时允许回退最近一次成功解析的定期报告
- 仅在半年报/年报披露窗口更新；新入库标的首次出现时必须抓取一次

### 5.2 财务字段

- `净资产` 来自最新可用定期报告
- `有息负债` 为可明确识别的有息债务合计
- `广义现金` 采用保守口径

## 6. 接口要求

### 6.1 路径

- 保持 `GET /api/market/convertible-bond-arbitrage` 不变

### 6.2 smallRedemption.rows 最少字段

- `holderCount`
- `remainingSizeYi`
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

## 7. 验收要求

### 7.1 页面

- `持有人数` 后紧跟 `剩余规模`
- `刚兑年化` 保留且可展示
- `期权价值` 后出现 `期权年化`
- `期权年化` 后出现 `总年化收益率`
- 不再展示上一轮的 `预期收益率`

### 7.2 推送

- 小额刚兑标的推送不再包含 `刚兑收益率`
- 改为直接推送 `总年化收益率`

### 7.3 公式

- `期权年化` 来源于 `smallRedemptionOptionValue / price`
- `期权年化` 使用 `remainingYears`
- `总年化收益率 = 刚兑年化 + 期权年化`

## 当前补充要求：刷新与推送完整性

- 可转债折价套利 `cbArb` 服务端盘中刷新间隔为 60 秒。
- 可转债折价套利正股实时价格内存缓存 TTL 为 60 秒。
- 页面停留在 `可转债套利` 页时，自动刷新必须主动请求最新 `cbArb` 数据。
- 可转债折价套利独立推送发送前必须强制刷新 `cbArb` 数据，不允许仅复用旧缓存。
- 推送正文必须使用紧凑逐行格式，优先覆盖全部满足条件的标的，降低企业微信长度截断导致的漏看风险。
## 当前补充要求：UI 设计规范先行

- 后续页面设计、React 重做和 UI 验收必须先遵守 `docs/UI_DESIGN.md`。
- `docs/UI_DESIGN.md` 是长期模板性设计规范，不是一次性页面改版方案。
- UI 方向固定为 Bloomberg 终端式金融界面：高密度、数字优先、低装饰。
- 字体策略固定为系统中文字体加等宽数字字体栈，不引入商业字体或外部字体服务。
- 页面主行动必须服务 `发现机会 / 判断风险 / 继续跟踪`。
- 1440px 桌面首屏必须展示核心状态、机会排序和至少一个高密度数据区。
- 任何 UI 代码实现前，必须先按 `docs/UI_DESIGN.md` 的验收清单检查设计方案。
## 当前补充要求：React 金融终端 UI 并行重做

- 默认首页必须迁移为遵守 `docs/UI_DESIGN.md` 的 React + Vite 金融终端 UI。
- 旧 HTML 看板必须保留为 `/legacy`，作为发布后回滚与对照入口。
- 新 UI 首屏必须优先展示系统状态、机会排序和高密度数据表，不展示大 hero 或营销式欢迎区。
- 新 UI 必须使用现有真实 `/api/*` 接口，不允许使用假数据、演示数据或静态占位数据冒充接口结果。
- 本轮不改变业务计算口径、数据抓取规则、推送规则和现有接口含义。

