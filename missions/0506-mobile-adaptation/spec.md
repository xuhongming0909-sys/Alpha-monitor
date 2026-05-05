# Mission: 手机端浏览适配

## 类型
implementation

## 目标
所有设备（手机、平板、电脑）统一显示移动端界面，废弃桌面端大表格和 1920px 锁死。核心方向：
1. 默认样式即移动端样式（Mobile-First）
2. 所有模块统一卡片视图，不再区分设备
3. 底部导航全局显示
4. 触控区域全局放大

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
