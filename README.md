# Alpha Monitor

套利数据监控与推送系统。

## 文档索引

- **工作流规则**: [`CLAUDE.md`](CLAUDE.md)
- **部署运维**: [`RUNBOOK.md`](RUNBOOK.md)
- **项目规格**: [`specs/spec.md`](specs/spec.md)
- **配置合同**: [`config.yaml`](config.yaml)
- **架构说明**: 各模块 `README.md`（`data_fetch/`、`strategy/`、`presentation/`、`notification/`、`shared/`）

## 快速验证

```bash
npm run check            # 冒烟测试
npm run check:boundaries # 插件边界检查
npm run check:constitution # 宪法同步检查
```

## 模块职责

| 目录 | 职责 |
|------|------|
| `data_fetch/` | 数据抓取与标准化 |
| `strategy/` | 业务计算与规则判断 |
| `presentation/` | 页面、API 整形与展示逻辑 |
| `notification/` | 推送配置、格式与调度 |
| `shared/` | 配置、路径、时间、运行态与通用能力 |
