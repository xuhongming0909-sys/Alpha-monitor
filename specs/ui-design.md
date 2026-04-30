# UI 设计规范

**Created**: 2026-04-30
**Last Updated**: 2026-04-30
**Status**: active

## 1. 定位

Alpha Monitor 是金融机会监控终端，不是营销官网，也不是装饰型数据大屏。

页面设计必须优先服务三件事：
1. 发现机会
2. 判断风险
3. 继续跟踪

## 2. 视觉基调

采用 Bloomberg 终端式金融界面方向：高密度、数字优先、低装饰、强对齐、强状态反馈。

必须做到：
- 数据比容器更醒目
- 表格比卡片更重要
- 状态比氛围更重要
- 首屏比品牌表达更重要
- 长时间盯盘比第一眼惊艳更重要

禁止：
- 大 hero
- 营销式渐变背景
- 大面积低信息留白
- 为了高级感牺牲数据密度
- 用图片、插画、装饰图形替代真实数据

## 3. 字体规范

### 3.1 字体栈

正文：
```css
font-family: "Microsoft YaHei UI", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif;
```

数字、价格、百分比、金额、代码、时间、表格数值：
```css
font-family: "JetBrains Mono", "SFMono-Regular", Consolas, "Roboto Mono", monospace;
font-variant-numeric: tabular-nums;
```

### 3.2 规则

- 使用系统中文字体与等宽数字字体栈
- 不引入商业字体或外部字体服务
- 表格数字默认右对齐
- 价格、百分比、金额、代码和时间必须使用等宽数字规则

## 4. 色彩规范

- 红、绿、黄只表达数据语义
- 禁止大 hero、宽松卡片、营销式渐变和低信息密度留白

## 5. 布局规范

- 1440px 桌面首屏必须同时展示系统状态、机会排序和至少一个高密度数据区
- 表格为首要信息载体
- 任何 UI 代码实现前，必须通过 `docs/UI_DESIGN.md` 的验收清单

## 6. 上游约束声明

- `docs/UI_DESIGN.md` 是 Alpha Monitor 后续页面设计、React 重做和 UI 验收的上游约束
- UI 实现必须遵守 `docs/UI_DESIGN.md`
- 如需修改设计规范，先更新 `docs/UI_DESIGN.md`，再更新本文件
