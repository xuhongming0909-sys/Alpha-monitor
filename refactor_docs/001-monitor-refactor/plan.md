# Alpha Monitor 当前实施计划

日期：2026-04-22

## 1. 本次目标

本轮只处理两类事项：

1. 收缩文档链路：
   - `SPEC.md` 改写为 500 行以内的正式生效文档
   - `plan.md` 只保留本次修改计划
   - 文档治理规则写入 `CONSTITUTION.md`
2. 实施本次已确认的业务修改：
   - 可转债折价功能退役旧因子链，切换到 `转债市值比` 与 `折价ATR比`
   - 排查并修复折价漏推送问题
   - 重写主摘要定时推送的排序与可读性
   - 手机端与电脑端网页统一为同一套布局与信息结构

## 2. 本次范围

仅允许修改以下文件或同职责 live 文档：

- `CONSTITUTION.md`
- `.specify/memory/constitution.md`
- `refactor_docs/001-monitor-refactor/plan.md`
- `refactor_docs/001-monitor-refactor/SPEC.md`
- `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
- `config.yaml`
- `start_server.js`
- `strategy/convertible_bond/service.js`
- `strategy/convertible_bond/discount_runtime_store.js`
- `notification/alerts/event_alert_service.js`
- `notification/styles/discount_strategy_markdown.js`
- `notification/styles/markdown_style.js`
- `presentation/dashboard/dashboard_page.js`
- 必要的最小测试文件

## 3. 不在本次范围

本轮不处理以下事项：

- AH / AB / LOF / 分红 / 事件套利 / 抢权配售本身的计算口径
- 非本轮业务需求引出的界面重构
- 与本轮无关的历史文档清扫
- 与本轮无关的推送链路重写

## 4. 业务目标

### 4.1 可转债折价功能

- 删除旧实时字段：
  - `ATR系数`
  - `抛压系数`
  - `加权折价率`
- 新增并展示：
  - `转债市值比 = 剩余规模 / 正股市值`
  - `折价ATR比 = abs(转股溢价率) / ATR百分比`
- 折价买卖规则保持不变：
  - 买入：`premiumRate < buy_threshold`
  - 卖出：`premiumRate > sell_threshold`

### 4.2 折价推送

- 推送规则保持原有交易时段与阈值逻辑
- 推送内容改为：
  - `可转债代码名称`
  - `溢价率`
  - `转债市值比`
  - `折价ATR比`
  - `是否当前为强赎（强赎中/非强赎）`

### 4.3 漏推送修复

- 排查“昨天建友/健友类转债达到 -2% 却未推送”的同类问题
- 优先检查：
  - `cb_discount_strategy_state.json` 独立运行态是否稳定落盘
  - bootstrap 静默播种是否吞掉真实新跨阈值
  - 状态穿越判定是否因为空状态或重启后重播种而失真

### 4.4 主摘要定时推送

- 仍保留一份报告
- 只保留以下 5 段，顺序固定：
  1. `今日打新`
  2. `可转债机会`
  3. `自定义监控`
  4. `AH`
  5. `AB`
- 标题必须强化，段落之间留空行

## 5. 实施步骤

### 步骤 1：文档治理

- 更新 `CONSTITUTION.md`
- 同步 `.specify/memory/constitution.md`
- 重写 `SPEC.md`
- 保留当前 `REQUIREMENTS.md`，只补本轮生效要求

验证：

- `SPEC.md` 行数 `<= 500`
- `plan.md` 仅描述当前任务
- 两份 constitution 内容一致

### 步骤 2：配置与运行态

- 在 `config.yaml` 明确写入 `cb_discount_strategy_state` 运行态文件
- 删除折价策略已退役的锚点配置
- 确保服务端读取配置后仍能正常启动

验证：

- 配置可被 `start_server.js` 正常读取
- 折价策略运行态文件路径唯一且明确

### 步骤 3：转债折价策略

- 重写 `strategy/convertible_bond/service.js` 中的折价派生逻辑
- 改写排序逻辑、摘要项和信号载荷
- 清理旧字段引用

验证：

- 新字段计算正确
- 旧字段不再参与页面和推送
- 买卖阈值逻辑不变

### 步骤 4：推送链路

- 改写折价推送 Markdown
- 排查并修复漏推送状态机问题
- 改写主摘要 Markdown 排序和可读性

验证：

- 推送文案包含新字段
- 空值显示真实状态，不伪造
- 主摘要只有 5 段且顺序正确

### 步骤 5：页面展示

- 改写可转债主表列定义
- 删除旧列
- 新增 `转债市值比`、`折价ATR比`
- 手机端不再保留独立移动端布局，直接沿用桌面端结构

验证：

- 页面列与推送口径一致
- 表格排序仍可用
- 手机端与桌面端显示同一套模块顺序与字段语义

### 步骤 6：测试与部署

- 补最小自动化测试
- 跑本地校验
- 做真实数据检查与推送检查
- 无误后同步云端并验证健康状态

验证：

- `npm run check`
- `npm run check:boundaries`
- 相关 Node 测试
- 真实接口/缓存数据无明显空值异常
- 云端 `/api/health` 与相关页面正常

## 6. 成功标准

本轮完成必须同时满足：

- `SPEC.md` 控制在 500 行以内，且能单独作为正式阅读文档
- `plan.md` 只保留当前计划
- 可转债折价链不再使用 `ATR系数 / 抛压系数 / 加权折价率`
- 页面和推送都改为新字段
- 折价漏推送问题有明确修复和回归验证
- 主摘要定时推送只保留 5 个部分且顺序正确
- 手机端与桌面端网页不再区分两套业务布局
- 本地验证通过，云端更新后服务可用
