# Plan: 手机端浏览适配

## 步骤

### 循环1：基础媒体查询（P0）
- RED：写测试 `tests/ui_mobile_media_query.test.js`
- GREEN：修改 `ui/src/styles.css` 添加 `@media (max-width: 768px)`
- 验证：测试通过

### 循环2：概览页手机优化（P1）
- RED：写测试断言概览卡片在手机端垂直堆叠
- GREEN：修改 `styles.css` 中 `.dashboard-grid` 与 `.terminal-grid` 的移动端表现
- 验证：测试通过

### 循环3：转债套利手机卡片视图（P2）
- RED：写测试断言手机端存在卡片视图组件
- GREEN：新增 `ui/src/components/ConvertibleCardList.jsx`，在 App.jsx 中条件渲染
- 验证：测试通过

### 循环4：底部导航栏（P4）
- RED：写测试断言手机端存在底部导航
- GREEN：新增 `ui/src/components/BottomNav.jsx`，在 App.jsx 中条件渲染
- 验证：测试通过

## 验证
```bash
node tests/ui_mobile_media_query.test.js   # ✅ 通过
node tests/ui_mobile_overview.test.js      # ✅ 通过
node tests/ui_mobile_convertible_card.test.js  # ✅ 通过
node tests/ui_mobile_bottom_nav.test.js    # ✅ 通过
```

冒烟测试 `npm run check` 因服务器未本地运行而 fetch failed（预期内，AGENTS.md 禁止本地跑服务）。

## 变更清单
| 文件 | 变更 |
|------|------|
| `ui/src/styles.css` | 新增 `@media (max-width: 768px)`：取消 1920px 锁死、搜索栏全宽、隐藏 brand-subtitle、增大 tab 触控区、底部 padding 防遮挡 |
| `ui/src/App.jsx` | 新增 `useIsMobile` hook；导入 `ConvertibleCardList`、`BottomNav`；`ConvertibleTable` 手机端渲染卡片 |
| `ui/src/components/ConvertibleCardList.jsx` | 新增：转债套利手机卡片视图（名称/价格/溢价率/正股/规模 + 展开详情） |
| `ui/src/components/BottomNav.jsx` | 新增：手机端底部固定导航（概览/转债/AH/LOF/更多） |
| `tests/ui_mobile_*.test.js` (4个) | 新增 TDD 测试 |
| `INDEX.md` | 登记新增组件文件 |

## 风险
- App.jsx 已达 2630 行，新增组件已拆出到独立文件
- 拆出组件后已同步更新 INDEX.md
