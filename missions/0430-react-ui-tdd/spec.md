# Mission Spec: React UI TDD 改进

**Type**: implementation + review
**Goal**: 让新版 React 终端 UI 达到生产可用，旧版 Dashboard 完整保留
**Scope**: 
- 基础上线准备（build/serve/legacy 路由）
- 模块 Tab 导航 + 各策略详细表格
- 全局搜索 + 列排序
- 自定义监控列表（不只是计数）
- 推送设置入口
**Constraints**:
- 旧版 `dashboard_template.html` 内容不能减少
- 所有展示内容基于真实 API，不用假数据
- 遵循 `docs/UI_DESIGN.md` 终端风格规范
**Impact on formal specs**:
- 更新 `specs/react-terminal-ui.md`（补充模块清单和验收标准）
