# Plan

## 步骤

1. [ ] 给 schema.py 增加 cleanup 逻辑（按表保留策略删除旧数据）
2. [ ] 修改 updater.py，update_all 后自动 cleanup
3. [ ] 创建 scripts/lof_maintenance.py 独立维护入口
4. [ ] 本地测试维护脚本
5. [ ] 创建 deploy/lof_maintenance.service + deploy/lof_maintenance.timer
6. [ ] Git push
7. [ ] 服务器拉取 + 部署 cron/timer
8. [ ] 验证服务器定时任务

## 验证
- [ ] 本地 run scripts/lof_maintenance.py 成功
- [ ] 检查数据库行数变化（旧数据被清理）
- [ ] 服务器 cron 配置生效
