# Alpha Monitor 项目规格索引

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Current Status**: active
**Input Source**: 长期用户需求 / 历史决策 / 已确认需求

## 文档角色

- 本文件定义：项目级目标、边界、模块地图、全局规则
- 本文件不定义：单次任务步骤、临时实现过程、历史讨论

## 项目目标

- 从真实市场数据中发现套利机会，通过网页展示和企业微信推送完成闭环
- 当前最重要目标：React 金融终端 UI 并行重做，旧页面保留 `/legacy` 回滚入口

## 当前阶段

- 阶段：MVP 向扩展过渡
- 当前焦点：React + Vite 金融终端 UI 首屏落地，同时保持现有业务稳定
- 当前非目标：新增套利策略模块、改动业务计算口径、改造数据抓取层

## 模块地图

详细文件级架构见 [`INDEX.md`](/INDEX.md)。

| 模块 | 职责 | 正式规格 | 真实入口 |
| --- | --- | --- | --- |
| 可转债套利 | 转债折价/小额刚兑数据、计算、展示 | `specs/convertible-bond-arbitrage.md` | `data_fetch/convertible_bond/`, `strategy/convertible_bond/`, `presentation/routes/dashboard_routes.js` |
| AH 溢价 | A/H 股溢价监控 | `specs/ah-premium.md` (待建) | `data_fetch/ah_premium/`, `presentation/routes/dashboard_routes.js` |
| AB 溢价 | A/B 股溢价监控 | `specs/ab-premium.md` (待建) | `data_fetch/ab_premium/`, `presentation/routes/dashboard_routes.js` |
| LOF 套利 | LOF 折溢价监控 | `specs/lof-arbitrage.md` (待建) | `data_fetch/lof/`, `presentation/routes/dashboard_routes.js` |
| 合并套利 | 并购重组公告监控 | `specs/merger-arbitrage.md` (待建) | `data_fetch/merger/`, `presentation/routes/dashboard_routes.js` |
| 事件套利 | 事件驱动套利监控 | `specs/event-arbitrage.md` (待建) | `data_fetch/event/`, `presentation/routes/dashboard_routes.js` |
| 股息提醒 | 股息机会跟踪 | `specs/dividend.md` (待建) | `data_fetch/dividend/`, `presentation/routes/dashboard_routes.js` |
| 打新/申购 | IPO、转债申购日历 | `specs/subscription.md` (待建) | `data_fetch/subscription/`, `presentation/routes/dashboard_routes.js` |
| 自定义监控 | 用户自定义套利组合 | `specs/custom-monitor.md` (待建) | `data_fetch/custom_monitor/`, `presentation/routes/dashboard_routes.js` |
| 汇率 | 港币/美元人民币汇率 | `specs/exchange-rate.md` (待建) | `data_fetch/exchange_rate/`, `presentation/routes/dashboard_routes.js` |
| UI 设计 | 全局视觉与交互规范 | `specs/ui-design.md` | `docs/UI_DESIGN.md` |
| React 终端 UI | React + Vite 重做规格 | `specs/react-terminal-ui.md` | `ui/` |
| 项目总览 | 技术栈、结构、通用规则 | `specs/project-overview.md` | `CONSTITUTION.md` (归档参考) |

## 全局规则

- 必须使用真实数据、真实接口、真实文件、真实返回结果
- 任一字段抓不到时显示 `--`，不伪造
- 需求变更时必须先更新 `specs/` 再写代码
- `config.yaml` 是唯一正式配置合同，新增参数先入配置再入代码
- 单次文档不得超过 500 行，超限则拆分模块或压缩内容
- 代码注释使用中文，非代码文档使用中文

## 子规格索引

- `specs/convertible-bond-arbitrage.md`: 可转债套利页面规格、计算合同、接口合同、推送规则
- `specs/ui-design.md`: UI 设计规范引用与补充约束
- `specs/react-terminal-ui.md`: React 金融终端重做范围、接口消费清单、验收标准
- `specs/project-overview.md`: 技术栈、模块职责、数据模型概述、API 合同索引

## 成功标准

- **SC-001**: 所有套利模块数据均来自真实接口，无假数据占位
- **SC-002**: 需求变更时 `specs/` 与代码同步更新
- **SC-003**: 每次非聊天任务产生可追踪的 `missions/` 闭环记录

## 当前追加约束

- React UI 首屏必须使用现有真实 `/api/*` 接口，不得伪造数据
- `小额刚兑` 页收益结构已调整为：刚兑年化 + 期权年化 + 总年化收益率
- 可转债折价套利推送前必须强制刷新 `cbArb` 数据
