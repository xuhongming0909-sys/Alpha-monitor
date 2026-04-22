# Alpha Monitor 需求手册

## 1. 文档定位

本文件是当前生效的产品需求合同，面向两类读者：

- 你自己阅读时，应该能直接看懂“现在这个产品到底要表现成什么样”。
- 后续 AI 改代码时，应该能用它判断哪些行为是必须保留的，哪些地方不能擅自改口径。

本文件只保留“当前仍然生效”的需求，不再把历史 phase 变更逐条堆在正文里。

文档分工固定如下：

- `CONSTITUTION.md`：项目最高原则。
- `plan.md`：每一轮为什么改、改哪些文件、验收什么。
- `REQUIREMENTS.md`：产品和业务层面的当前生效要求。
- `SPEC.md`：接口、字段、前端状态、技术实现和更细的计算/实现合同。

如果旧需求被新需求覆盖，以本文件中更靠后的当前口径为准；如果本文件没有展开到字段级技术细节，再看 `SPEC.md`。

---

## 2. 产品目标

Alpha Monitor 的目标固定为：

- 用真实市场数据生成套利监控网页。
- 提供定时推送与独立模块推送。
- 最终交付形态是云端可访问服务，而不是只在本机临时可跑。

本项目默认遵守以下产品原则：

- 只使用真实数据、真实接口、真实文件结果。
- 页面优先服务“看盘”和“决策”，而不是做演示页。
- 改动应尊重现有链路，优先做最小、最短、最可验证的修改。

---

## 3. 当前产品总结构

首页当前固定结构如下：

1. 页面标题：`Alpha Monitor`
2. 顶部状态行
3. 顶部 `股债打新` 今日事项区
4. 主标签页区域
5. 页面底部 `推送设置`

当前主标签页固定为 8 个，顺序固定：

1. `转债套利`
2. `AH溢价`
3. `AB溢价`
4. `LOF套利`
5. `监控套利`
6. `分红提醒`
7. `事件套利`
8. `可转债抢权配售`

页面不得再退回到以下旧表达：

- 标题下方的大段说明文字
- 首页顶部多个大卡片式“市场概况”
- 用演示数据填满页面
- 为展示层单独增加一条重型 dashboard 专用后端链路

页面默认应复用现有接口和缓存元信息，而不是新造平行接口。

---

## 4. 通用页面与交互规则

### 4.1 数据与刷新

- 页面必须优先展示最近一次成功的真实数据。
- 关键行情模块允许先读缓存再后台刷新，但不能长期停留在跨日旧快照。
- `exchangeRate / cbArb / ah / ab` 属于关键行情模块。
- 如果首次加载返回的是缓存结果，前端应在同一会话内触发一次后台重校验。
- 页面分钟级轮询优先读取轻量级状态接口，而不是每次整表重拉。

### 4.2 表格

除明确例外外，主表统一遵守：

- 支持排序
- 支持搜索
- 支持分页
- 每页固定 `50` 条
- 桌面端允许受控横向滚动

以下模块必须使用分页主表：

- `转债套利`
- `AH溢价`
- `AB溢价`
- `LOF套利`
- `监控套利`
- `分红提醒`
- `事件套利`
- `可转债抢权配售`

### 4.3 桌面端与移动端

- 桌面端与移动端必须使用同一套页面结构、模块顺序和字段语义。
- 移动端不再维护单独布局，只允许在相同页面结构下通过横向滚动承载长表。
- 全局字体、表头、按钮、输入框和表格正文不能小到难以阅读。

### 4.4 展示配置

页面应继续通过统一配置读取展示参数，例如：

- `config.yaml > presentation.dashboard_entry`
- `config.yaml > presentation.dashboard_table_ui.*`
- `config.yaml > presentation.dashboard_auto_refresh.*`
- `config.yaml > presentation.dashboard_module_notes.*`

---

## 5. 顶部固定区域

### 5.1 顶部状态行

用途：

- 一行展示全局关键行情状态。

数据来源：

- `/api/market/exchange-rate`
- `/api/market/convertible-bond-arbitrage`

必须显示：

- `HKD/CNY`
- `USD/CNY`
- `十年期国债收益率`
- 最近更新时间

规则：

- 状态行是一整行文字，不再使用大状态卡。
- 若 `treasuryYield10y` 缺失，必须明确显示“暂未返回”。

### 5.2 顶部股债打新

用途：

- 展示今天需要关注的 IPO / 可转债打新事项。

数据来源：

- `/api/market/ipo`
- `/api/market/convertible-bonds`

规则：

- 只显示“今天相关”的事项。
- 表格内混排新股和转债。
- 至少显示：
  - 当前阶段
  - 类型
  - 名称/代码
  - 申购日
  - 中签缴款日
  - 上市日
  - 申购上限
  - 发行价或转股价
- 不再单独显示 `抽签日` 列。
- 页面显示的 `中签缴款日` 一律使用 `lotteryDate`。
- `今日中签缴款` 的阶段判断也一律使用 `lotteryDate`，不得再单独按 `paymentDate` 判断。
- 阶段标签固定为：
  - `今日申购`
  - `今日中签缴款`
  - `今日上市`

### 5.3 页面底部推送设置

用途：

- 让用户直接查看并修改主推送时间。

数据来源：

- `GET /api/push/config`
- `POST /api/push/config`

规则：

- 固定放在页面底部。
- 固定只保留 3 个时间槽。
- 前 2 个时间槽用于常规模块主推送。
- 第 3 个时间槽用于独立推送模块。
- 保存成功后，页面必须直接回写接口返回结果。
- 页面重载后必须继续读取运行时真实配置，不能退回到旧默认值。

---

## 6. 主标签页需求

### 6.1 转债套利

用途：

- 展示可转债与正股的套利相关核心指标。

数据来源：

- `/api/market/convertible-bond-arbitrage`

页面结构固定为：

1. 标题与更新时间
2. 顶部摘要卡
3. 主表
4. 说明文字

顶部摘要卡固定保留 3 组：

- `双低前3`
- `理论溢价前3`
- `低溢价监控`

摘要卡规则：

- `双低前3` 按 `doubleLow` 排名。
- `理论溢价前3` 按 `theoreticalPremiumRate` 排名。
- `低溢价监控` 来自独立折价监控池，不与前两组混用。
- `双低前3` 主值必须明确标注为 `双低值`，同时显示 `现价`。
- `理论溢价前3` 主值必须明确标注为 `理论溢价率`，同时显示 `现价` 和 `理论价`。
- 不允许再把 `双低值 / 理论溢价率` 用裸数字展示成像“现价”的样子。

主表必须支持排序、搜索、分页，并保留当前主要字段族：

- 转债身份：代码、名称
- 正股身份：代码、名称
- 行情：转债价、正股价、涨跌幅
- 转股相关：转股价、转股价值、转股溢价率、双低
- 折价策略：转债市值比、折价ATR比、市场、强赎状态
- 债底与期权：纯债价值、纯债溢价、理论价格、理论溢价率、理论期权价值、隐含期权价值、期权折价率
- 其他：剩余规模、波动率、剩余期限、评级、上市日、转股起始日

当前生效计算口径：

- `转股价值 = stockPrice * 100 / convertPrice`
- `转股溢价率 = (price / convertValue - 1) * 100`
- `双低 = price + premiumRate`
- `纯债溢价率 = (price / pureBondValue - 1) * 100`
- `ATR百分比 = stockAtr20 / stockPrice * 100`
- `转债市值比 = remainingSizeYi / stockMarketValueYi`
- `折价ATR比 = abs(premiumRate) / stockAtr20Pct`

理论定价口径固定为“债底 + 净看涨价差价值”：

- `optionQty = 100 / convertPrice`
- `bondFloorStrike = pureBondValue / optionQty`
- `longCallStrike = max(convertPrice, bondFloorStrike)`
- `shortCallStrike = redeemTriggerPrice`
- `theoreticalPrice = pureBondValue + max(longCallValue - shortCallValue, 0)`

期权相关展示口径：

- `理论期权价值 = theoreticalPrice - pureBondValue`
- `隐含期权价值 = price - pureBondValue`
- `期权折价率 = implicitOptionValue / theoreticalOptionValue - 1`

活跃强赎与终态规则：

- 主表可以显示活跃强赎样本，但必须用名称内风险提示表达，不再做整行高亮。
- 终态、退市、停牌到期失效等非 live 样本不得继续出现在页面可见主表中。
- 顶部 `双低前3 / 理论溢价前3` 必须排除：
  - 活跃强赎样本
  - 终态 / 非 live 样本

独立低溢价监控规则：

- `低溢价监控` 卡片与独立推送沿用独立监控池。
- 本模块顶部摘要卡收口不改变该独立推送的阈值与节奏。
- 运行态为空但样本已落入买入区时，初始化不能静默吞掉真实买入事件。

### 6.2 AH溢价

用途：

- 展示 A/H 溢价排行与分位情况。

数据来源：

- `/api/market/ah`
- 历史样本来自 `runtime_data/shared/premium_history.db`

公式：

- `AH溢价 = (H股人民币价 / A股价 - 1) * 100`
- `H股人民币价 = H股价 * HKD/CNY`
- `价差 = H股人民币价 - A股价`

页面规则：

- 顶部固定显示当前排序口径下的前 3 和后 3。
- 主表固定支持排序、搜索、分页。
- 主表当前核心字段：
  - A股代码
  - A股名称
  - H股代码
  - H股名称
  - A股价
  - H股价
  - H股人民币价
  - 价差
  - 溢价率
  - 近三年分位
  - 样本区间

### 6.3 AB溢价

用途：

- 展示 A/B 溢价排行与分位情况。

数据来源：

- `/api/market/ab`
- 历史样本来自 `runtime_data/shared/premium_history.db`

公式：

- `AB溢价 = (B股人民币价 / A股价 - 1) * 100`
- `B股人民币价 = B股价 * 对应汇率`
- `价差 = B股人民币价 - A股价`

页面规则：

- 布局、排序、分页和 AH 页面保持一致。
- 主表字段与 AH 页面对应，只把 H 股字段替换成 B 股字段。

### 6.4 LOF套利

用途：

- 展示 LOF / QDII 套利数据与监控池。

数据来源：

- `/api/market/lof-arbitrage`
- `GET /api/push/lof-arbitrage-config`
- `POST /api/push/lof-arbitrage-config`

当前页面结构：

1. 标题与说明
2. 顶部两个监控池卡片
3. 分组列表
4. LOF 独立推送卡

当前生效分组合同：

- 可见分组只保留：
  - `指数LOF`
  - `QDII亚洲`
- 默认分组固定为 `index`

规则：

- 顶部卡片只保留 `限购池` 和 `非限池`。
- 列表按当前分组显示 IOPV、溢价率、成交额等字段。
- 独立推送配置固定为单时间槽。
- 当前 LOF 独立推送时间固定收口为 `14:00`。

### 6.5 监控套利

用途：

- 管理用户自定义的并购/换股/现金对价监控项目。

数据来源：

- `GET /api/monitors`
- `POST /api/monitors`
- `DELETE /api/monitors/:id`

页面结构：

1. 顶部新增/编辑表单
2. 实时监控主表

规则：

- 页面必须支持新增监控。
- 页面必须支持编辑已有监控并原地保存。
- 页面必须支持删除监控。
- 补充参数必须直接显示在每个项目下方，不再保留单独的 `详情` 按钮或控制列。
- 文案必须使用真实业务术语，不得使用自造字段名。
- 返回结果应尽量使用最新股价，不能长期沿用旧价格。

当前核心公式：

- `股票腿理论对价 = 收购方股价 * 换股比例 * 安全系数 + 现金对价`
- `股票腿收益率 = (股票腿理论对价 - 目标方现价) / 目标方现价 * 100`
- `现金腿收益率 = (现金对价 - 目标方现价) / 目标方现价 * 100`

### 6.6 分红提醒

用途：

- 展示今日登记日提醒和完整观察列表。

数据来源：

- `/api/dividend?action=refresh`
- `/api/dividend?action=portfolio`

页面结构：

1. 今日登记日提醒
2. 完整观察表

公式：

- `股息率 = 每股分红 / 当前股价 * 100`

规则：

- 顶部优先强调今天登记日的股票。
- 完整观察表继续支持排序、分页。

### 6.7 事件套利

用途：

- 聚合 A 股事件套利、港股私有化、中概私有化和最新公告池。

数据来源：

- `/api/market/event-arbitrage`
- `/api/merger/reports/today`
- `/api/merger/report`
- `/api/merger/report/generate`

当前页面结构：

1. 标题与状态
2. 概览卡片与来源状态
3. 子标签页内容

当前子标签页固定为：

- `A股套利`
- `港股套利`
- `中概私有`
- `港供套利`
- `最新公告`

当前状态要求：

- `港供套利` 可保留入口，但当前可以是待接入/禁用态。
- `最新公告` 必须能展示公告池与匹配状态。
- 有官方公告匹配的行，应继续支持 AI 报告链路。

### 6.8 可转债抢权配售

用途：

- 展示可转债抢权配售机会，并支持独立推送。

数据来源：

- `/api/market/cb-rights-issue`
- `GET /api/push/cb-rights-issue-config`
- `POST /api/push/cb-rights-issue-config`

当前页面结构已经不再使用旧的“摘要卡 + 来源表 + 详情区”模式，而是固定为：

1. 顶部总览条
2. `沪市 / 深市` 两个市场页签
3. 每个市场页签内纵向连续展示三张阶段表：
   - `申购阶段`
   - `埋伏阶段`
   - `等待阶段`

当前阶段划分规则：

- `申购阶段`：`inApplyStage = true`
- `埋伏阶段`：不在申购阶段，且 `progressName` 属于 `上市委通过 / 同意注册 / 注册生效`，同时 `expectedReturnRate > 6%`
- `等待阶段`：其余项目

当前市场划分规则：

- `沪市`：`market = sh`
- `深市`：`market = sz`
- 若市场字段缺失，可按代码前缀补推断：
  - `6* -> sh`
  - `0* / 3* -> sz`

当前生效计算口径：

- `issueScaleYi` 的真实语义来自 `amountYi`
- `issueRatio = issueScaleYi / stockMarketValueYi`
- `placementShares = ceil(rawRequiredShares * 0.6 / 100) * 100`
- `marginRequiredShares = ceil(rawRequiredShares * 0.6 / 50) * 50`
- `requiredFunds = placementShares * stockPrice`
- `marginRequiredFunds = marginRequiredShares * stockPrice`
- `expectedReturnRate = optionValue / requiredFunds * 100`
- `marginReturnRate = optionValue / marginRequiredFunds * 100`
- `expectedPeelReturnRate = expectedReturnRate * (originalFundsBaseline - requiredFunds) / requiredFunds`
- `marginPeelReturnRate = marginReturnRate * (originalFundsBaseline - marginRequiredFunds) / marginRequiredFunds`
- `annualizedReturnRate = (1 + marginPeelReturnRate / 100)^(252 / estimatedApplyTradingDays) - 1`

当前页面列规则：

- 共享核心列保留：
  - 正股代码
  - 正股名称
  - 方案进展
  - 进展公告日
  - 发行规模
  - 总市值
  - 发行比例
  - 原始所需股数
  - 配售股数
  - 转股价
  - 波动率
  - 单位期权价值
  - 期权价值
  - 所需资金
  - 预期收益率
- `股权登记日` 只在 `申购阶段` 显示。
- `沪市` 额外保留：
  - 两融所需股数
  - 两融所需资金
  - 两融收益率
  - 预期收益率去皮
  - 两融收益率去皮
- `深市` 不再显示：
  - 两融所需股数
  - 两融所需资金
  - 两融收益率
  - 预期收益率去皮
  - 两融收益率去皮

当前独立推送规则：

- 只推 `沪市` 项目。
- `深市` 不参与独立推送。
- `申购阶段` 拆为两段推送：
  - `买入提醒`：`recordDate = 今天` 或 `明天` 的沪市项目，分别覆盖股权登记日当天与前一交易日提醒。
  - `卖出提醒`：`applyDate = 今天` 的沪市项目，用于申购日当天提醒卖出。
- `埋伏阶段` 推送所有满足埋伏条件的沪市项目。
- 推送文本使用数据行表达，不再使用旧的摘要卡式标题。
- 推送字段顺序固定把 `发行规模` 放在 `发行比例` 之前：
  - `买入提醒`：`名称 股权登记日 两融所需股数 两融所需资金 发行规模 发行比例 两融收益率去皮`
  - `卖出提醒`：`名称 申购日 两融所需股数 两融所需资金 发行规模 发行比例 两融收益率去皮`
  - `埋伏阶段`：`名称 方案进展 进展公告日 两融所需股数 两融所需资金 发行规模 发行比例 两融收益率去皮`

---

## 7. 接口复用边界

当前 dashboard 应优先复用以下接口，不新增平行重型接口：

- `GET /api/health`
- `GET /api/dashboard/ui-config`
- `GET /api/dashboard/resource-status`
- `GET /api/market/exchange-rate`
- `GET /api/market/ipo`
- `GET /api/market/convertible-bonds`
- `GET /api/market/convertible-bond-arbitrage`
- `GET /api/market/ah`
- `GET /api/market/ab`
- `GET /api/market/lof-arbitrage`
- `GET /api/market/event-arbitrage`
- `GET /api/market/cb-rights-issue`
- `GET /api/monitors`
- `GET /api/dividend`
- `GET /api/push/config`
- `POST /api/push/config`
- `GET /api/push/lof-arbitrage-config`
- `POST /api/push/lof-arbitrage-config`
- `GET /api/push/cb-rights-issue-config`
- `POST /api/push/cb-rights-issue-config`

接口变更边界固定为：

- `strategy / data_fetch` 定义业务含义与计算结果。
- `presentation` 只负责整形、状态管理和展示。
- 若字段含义变化，必须先更新 `REQUIREMENTS.md` 和 `SPEC.md`，再改代码。

---

## 8. 配置边界

所有可变参数仍应集中在 `config.yaml` 或项目统一配置入口中。

后续改动时优先关注以下配置族：

- `presentation.dashboard_entry`
- `presentation.dashboard_table_ui.*`
- `presentation.dashboard_auto_refresh.*`
- `presentation.dashboard_module_notes.*`
- `data_fetch.plugins.*.refresh_interval_ms`
- `strategy.convertible_bond.*`
- `strategy.cb_rights_issue.*`
- `notification.default_full_push_time`
- `notification.enabled_modules`
- `notification.scheduler.*`

不得把新的阈值、分组规则、URL、服务名、端口、推送时间散落硬编码在多个文件中。

---

### 8.1 云端发布链路要求

- 正式发布链路仍然固定为：本地 `git push origin main` -> GitHub Actions -> 服务器拉取更新 -> 健康检查。
- 默认发布模式必须优先使用“自动判断”而不是固定全量部署：
  - 仅当依赖、运行入口、systemd 模板等真正影响运行环境的文件变化时，才执行完整部署。
  - 纯前端、策略、通知文案、文档等常规改动，默认走快速部署。
- 连续多次 push 时，发布系统应自动取消旧的排队/执行中任务，只保留最新一次提交继续部署。
- 服务器端不得在每次部署都无条件执行整仓 `chown -R`、`npm ci`、`pip install -r requirements.txt`。
- 服务器端只有在需要时才刷新 `systemd` 单元并重启服务；纯文档或纯部署脚本更新不应强制重启线上服务。

## 9. 验收要求

### 9.1 页面验收

至少应满足：

- 首页能直接打开并看到真实数据。
- 顶部状态行是一行文字，不再退回旧卡片式结构。
- 顶部 `股债打新` 使用今天事项长表。
- 底部 `推送设置` 可以读取、保存、回显。
- 8 个主标签页都能切换。
- `转债套利 / AH / AB / LOF / 监控 / 分红 / 事件套利 / 可转债抢权配售` 都能正确渲染。
- 分页表统一保持 `50` 条每页。
- `闻泰转债 110081` 这类样本在 `转债套利` 顶部摘要中不会再把 `双低值` 误看成现价。

### 9.2 最小校验命令

实施后至少优先尝试：

- `npm run check`
- `npm run check:boundaries`
- `python data_dispatch.py exchange-rate`
- `python data_dispatch.py ah`
- `python data_dispatch.py ab`

如果本轮改了计算口径，还必须检查是否与 `SPEC.md` 保持一致。

---

## 10. 后续 AI 改代码时必须遵守的要求

## 11. 2026-04-22 可转债折价与定期推送最新口径

本节晚于前文中所有 `ATR系数 / 抛压系数 / 加权折价率` 相关描述，且以本节为当前正式生效口径。

### 11.1 可转债折价页面最新字段

`转债套利` 主表中，折价策略字段改为：

- `转债市值比`
- `折价ATR比`
- `市场`

退役字段：

- `ATR系数`
- `抛压系数`
- `加权折价率`

页面不再展示、排序或摘要使用退役字段。

### 11.2 可转债折价正式计算口径

保留原规则：

- `转股价值 = stockPrice * 100 / convertPrice`
- `转股溢价率 = (price / convertValue - 1) * 100`
- `ATR百分比 = stockAtr20 / stockPrice * 100`
- 买入区间仍按 `premiumRate < buy_threshold`
- 卖出区间仍按 `premiumRate > sell_threshold`

新增正式指标：

- `转债市值比 = 剩余规模 / 正股市值`
- `折价ATR比 = abs(转股溢价率) / ATR百分比`

约束：

- `剩余规模` 使用现有真实字段 `remainingSizeYi`
- `正股市值` 必须来自真实数据链路，不允许伪造或静态估算
- 如 `正股市值` 或 `ATR百分比` 缺失，对应新指标允许为空，但行仍保留

### 11.3 可转债折价推送内容

独立折价推送继续按原有阈值与交易时段规则运行，但推送内容必须改为：

- `可转债代码名称`
- `溢价率`
- `转债市值比`
- `折价ATR比`
- `是否当前为强赎`

其中强赎文案固定为：

- `强赎中`
- `非强赎`

不再输出：

- `加权折价率`
- `ATR系数`
- `抛压系数`

### 11.4 漏推送修复要求

必须排查并修复“昨天建友转债达到 `-2%` 折价却未推送”的同类问题。

本轮至少满足：

- 独立折价策略运行态有独立持久化文件
- 首次初始化不能把真实的新跨阈值事件静默吞掉
- 新买入 / 卖出跨阈值必须按状态穿越规则只触发一次

### 11.5 定期推送最新要求

主摘要定时推送仍是一份报告，但只保留以下 5 个部分，且顺序固定：

1. `今日打新`
2. `可转债机会`
3. `自定义监控`
4. `AH`
5. `AB`

格式要求：

- 各部分标题必须强化显示
- 相邻部分之间必须留空行
- 不再把 `分红提醒`、`事件套利`、其他模块拼进这份定期报告

- 不要把本文件重新写回“历史 phase 堆叠日志”。
- 本文件应始终保持“当前生效需求手册”的形态。
- 新增需求时：
  1. 先改 `plan.md`
  2. 再改本文件
  3. 再改 `SPEC.md`
  4. 最后改代码
- 如果只是历史追踪、排障过程、阶段背景，写到 `plan.md`，不要继续塞回本文件正文。

本文件的长期目标只有两个：

- 让你自己能读懂
- 让后续 AI 不敢乱改
