# Memory

**Retention**: max 50 entries. Oldest auto-deleted when exceeded.

**Record only**: decisions, meaningful actions, verification results, memorable failures, next steps.
**Do not**: dump full conversations.

## Entries

### 2026-05-06 | 部署最新版本到服务器

- **Decision**: 先把服务器对齐当前最新提交，确保用户能立刻看到最新页面
- **Action**: 服务器执行 `git pull`、`cd ui && npm run build`、`sudo systemctl restart alpha-monitor`
- **Verification**: 公网 `/api/health` 正常，`ui/dist` 新资源 `index-DAsT1b9e.js` / `index-DfyVk25X.css` 仍在使用
- **Action**: 服务器当前分支 `workflow-elodie` 已改为跟踪 `origin/main`
- **Risk**: 服务器工作树有未跟踪 `tools/` 文件，暂不能直接切到 `main`
- **Mission**: `missions/0506-deploy-latest/`

### 2026-05-06 | 全局移动端化（手机优先，所有设备统一）

- **Decision**: 用户主要用手机看网页，要求所有设备（手机/电脑/平板）统一显示移动端界面，废弃桌面端大表格
- **Action**: `styles.css` 改为 Mobile-First — 默认无 1920px 锁死、无 1800px 表格、垂直堆叠布局
- **Action**: 底部导航 `BottomNav` 全局显示，不再依赖屏幕宽度
- **Action**: 新增 `ui/src/components/ConvertibleCardList.jsx` — 转债套利全局卡片视图
- **Action**: 新增 `ui/src/components/AhCardList.jsx` — AH溢价全局卡片视图
- **Action**: 新增 `ui/src/components/LofCardList.jsx` — LOF套利全局卡片视图
- **Fix**: `App.jsx` return 缺少 Fragment 包裹导致 vite build 失败，已修复 `<></>`
- **Deploy**: GitHub push 因网络超时失败（临时），后恢复；服务器通过 expect SSH + 密码部署成功
- **Server**: 43.139.35.190, ubuntu/DellG77588, app_dir: /home/ubuntu/Alpha monitor, systemd: alpha-monitor
- **Verification**: 服务已重启，新资源文件 `index-DAsT1b9e.js` + `index-DfyVk25X.css` 已上线
- **Remaining**: AB溢价、打新/申购、自定义监控、分红提醒、抢权配售、事件套利仍为表格（未卡片化）
- **Mission**: `missions/0506-mobile-adaptation/`

### 2026-05-05 | Server Profile 恢复与 CLI 配置

- **Decision**: 用户要求恢复 SSH 服务器配置文件，并统一放到 config/ 目录
- **Action**: 从 `archive/ops/server_profile.local.yaml` 恢复备份
- **Action**: 移动到 `config/server_profile.local.yaml`，删除 `ops/` 空目录
- **Action**: 更新 `deploy/sync_remote_env_from_profile.py` 中 `PROFILE_PATH` 指向 `config/`
- **Action**: 更新 `.gitignore` 忽略 `config/server_profile.local.yaml`
- **Action**: 修改 `~/.kimi/config.toml` — `default_yolo=true`, `default_caveman=true`
- **Verification**: 文件位置正确，代码引用已更新，gitignore 正确
- **Mission**: `missions/0505-server-profile-config/`

### 2026-04-30 | ES Module修复 + dashboard_page.js拆分

- **Decision**: 服务器启动失败，view_models和routes使用CommonJS但被当作ES Module加载
- **Fix**: ui/routes/*.js → .cjs, ui/dashboard/*.js → .cjs, ui/view_models/*.js → .cjs
- **Fix**: update start_server.js require paths to .cjs
- **Fix**: config.yaml dashboard_entry路径从presentation改为ui/templates
- **Fix**: tool_paths.py tools→scripts目录名修复，config.yaml C++注释→YAML
- **Action**: 拆分 dashboard_page.js → constants.js（提取 UI 常量 ~200 行）
- **Action**: 拆分 source.py → cb_metrics.py（提取计算密集型函数 ~570 行）
- **Action**: 新建 server_config_loader.js（配置读取逻辑 ~300 行）
