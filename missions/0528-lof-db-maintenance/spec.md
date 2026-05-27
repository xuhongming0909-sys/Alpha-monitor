# Mission: LOF数据库服务器部署+自动维护

## 任务类型
实现

## 目标
1. LOF数据库补齐到服务器（git push后服务器拉取即可）
2. 数据更新脚本增加过期数据清理能力
3. 创建独立维护脚本，可被cron/systemd timer调用
4. 服务器配置定时任务，每天自动执行

## 范围
- `data_fetch/lof_db/` — updater 增加 cleanup 能力
- `scripts/lof_maintenance.py` — 独立维护入口（不在根目录）
- `deploy/` — 新增 systemd timer 配置

## 约束
- 服务器路径: /home/ubuntu/Alpha monitor
- 服务器IP: 43.139.35.190
- 保持现有 updater 逻辑不变，只追加 cleanup
- 数据保留策略: NAV 120天, ETF/stock 250天, FX 当年, holdings 最新2季度

## 影响
- 不影响现有 web 服务
- 清理只删过期数据，不删当天数据
