# Mission: 手机端浏览适配

## 类型
implementation

## 目标
让 Alpha Monitor 网页在手机浏览器上可正常使用，核心解决：
1. 页面被强制 1920px 宽度锁死、无法阅读
2. 表格过宽（1800px+）导致横向滚动体验极差
3. 导航/触控区域太小

## 范围
仅修改 `ui/src/styles.css` 与 `ui/src/App.jsx`（及其拆分出的组件），不涉及 API、数据抓取、推送逻辑。

## 约束
- 遵循 TDD 三环循环
- 垂直切片：每次只做一个行为
- 不改动旧看板 `ui/templates/dashboard_template.html`
- 单文件不超过 1000 行（App.jsx 超标，新增组件必须拆出）
- 所有代码注释用中文

## 影响
- `specs/` 无需变更（纯展示层改动）
- `INDEX.md` 需登记新增组件文件
