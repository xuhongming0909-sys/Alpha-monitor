# 计划：拆分超 1000 行文件

## 执行步骤

### Task 14: dashboard_page.js → constants.js
1. 新建 `presentation/dashboard/constants.js`
2. 提取 ENDPOINTS, TAB_SEQUENCE, TABLE_DEFAULTS, TABLE_SEARCH_CONFIG 等常量
3. dashboard_page.js 从 constants.js 导入
4. 验证语法

### Task 13: source.py → cb_metrics.py
1. 新建 `data_fetch/convertible_bond/cb_metrics.py`
2. 提取波动率计算、ATR、理论定价、美式期权二叉树模型等函数
3. source.py 委托给 cb_metrics 模块
4. 验证语法和功能

### Task 15: start_server.js → server_config_loader.js
1. 新建 `server_config_loader.js`
2. 提取配置读取逻辑（PORT, HOST, APP_CONFIG 等）
3. 保留 start_server.js 原样（完全重构依赖过多全局状态）
4. 验证语法

## 验证

- `node -c` / `python3 -m py_compile` 语法检查
- `python3 scripts/add_ai_summary.py` 更新 AI-SUMMARY
- INDEX.md §9 更新文件索引

## 结果

| 文件 | 拆分后行数 |
|------|-----------|
| constants.js | ~200 |
| dashboard_page.js | ~5400 (仍超标但改善) |
| cb_metrics.py | ~570 |
| source.py | ~2770 (仍超标但改善) |
| server_config_loader.js | ~300 |
| start_server.js | ~3200 (未完全重构) |