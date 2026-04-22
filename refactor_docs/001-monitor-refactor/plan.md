# Alpha Monitor 当前实施计划

日期：2026-04-22

## 1. 本次目标

本轮只处理三个直接问题：

1. 修复首页和配置说明中的中文乱码。
2. 把 `转债市值比` 与抢权配售相关市值口径统一切到 `流通市值`。
3. 把 `转债市值比`、`折价ATR比` 在页面与折价推送中统一改为百分比展示。

## 2. 本次范围

仅修改与本轮目标直接相关的 live 文件：

- `config.yaml`
- `data_fetch/convertible_bond/source.py`
- `data_fetch/cb_rights_issue/source.py`
- `notification/styles/discount_strategy_markdown.js`
- `presentation/dashboard/dashboard_page.js`
- `presentation/templates/dashboard_template.html`
- `tests/convertible_discount.test.js`
- `refactor_docs/001-monitor-refactor/plan.md`
- `refactor_docs/001-monitor-refactor/SPEC.md`
- `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`

## 3. 不在本次范围

- 不改折价买卖阈值与交易时段规则。
- 不改 AH / AB / LOF / 分红 / 事件套利的业务口径。
- 不扩展新的推送渠道或新页面。
- 不清理与本轮无关的历史脏文件。

## 4. 实施步骤

### 4.1 中文文案修复

- 恢复首页固定文案为正常中文。
- 恢复 `config.yaml` 中 `dashboard_module_notes` 与 `事件套利` 模块名称。

验证：

- 本地打开 `/` 时能看到 `股债打新`、`转债套利`、`推送设置`、`定时推送 1`。

### 4.2 市值口径切换

- 可转债套利抓取链改为优先读取 `流通市值` / `f21`。
- 抢权配售抓取链改为优先读取 `流通市值` / `f21`。
- 抢权配售页面列名与文档口径同步为 `流通市值`。

验证：

- 代码中不再把 `总市值` 作为本轮主口径。
- `发行比例` 文档口径改为 `发行规模 / 流通市值`。

### 4.3 百分比展示统一

- 页面表格中的 `转债市值比`、`折价ATR比` 改为百分比。
- 折价独立推送中的同名字段改为百分比。
- 页面摘要、副标题和推送文案保持同一口径。

验证：

- 折价推送示例中显示 `8.000%`、`152.000%` 这类百分数。
- 页面脚本中对应字段改为百分比渲染函数。

## 5. 验证命令

- `node --test tests/convertible_discount.test.js`
- `node --check start_server.js`
- `Invoke-WebRequest http://127.0.0.1:5000/`
- `Invoke-WebRequest http://127.0.0.1:5000/presentation/dashboard/dashboard_page.js`

## 6. 完成标准

- 首页关键中文文案无乱码。
- `转债市值比` 与 `折价ATR比` 在页面和推送里都按百分比展示。
- 可转债套利与抢权配售的市值口径都切为 `流通市值`。
- 本地测试与页面检查通过后再提交和推送部署。
