# mini-SWE-agent 使用教程

这份教程把 `mini-SWE-agent` 放到 Alpha Monitor 的现有工作流里使用，而不是让它绕开仓库规则单独行动。

## 1. 适合怎么用

推荐分工：

- Codex 负责：
  - 读仓库上下文
  - 判断是否要先改 `plan.md` / `REQUIREMENTS.md` / `SPEC.md`
  - 拆任务
  - 复查改动
- `mini-SWE-agent` 负责：
  - 按明确任务做窄范围实现
  - 跑本地校验
  - 汇报改了什么

最适合交给 `mini-SWE-agent` 的任务：

- 只改 `presentation/` 的页面或表格问题
- 只改 `data_fetch/` 的抓取或标准化问题
- 只改 `strategy/` 的局部实现
- 有清晰验证命令的小修复

不建议直接扔给它的任务：

- 需求/契约还没定的改动
- 跨多个层的大重构
- 服务器、密钥、部署、运行时敏感信息相关操作

## 2. 安装

参考官方文档：

- `SWE-agent`: <https://github.com/SWE-agent/SWE-agent>
- `mini-SWE-agent`: <https://github.com/SWE-agent/mini-swe-agent>
- Quickstart: <https://mini-swe-agent.com/latest/quickstart>
- CLI usage: <https://mini-swe-agent.com/latest/usage/mini/>

本机安装：

```powershell
pip install mini-swe-agent
mini-extra config setup
```

建议先用 `confirm` 风格的人机确认模式，不要一开始就追求全自动。

## 3. 仓库内置入口

项目已经内置了一个任务生成器：

```powershell
npm run agent:mini:task -- --help
```

它不会直接启动 `mini-SWE-agent`，只会生成一段适合本仓库的任务文本，自动带上：

- `CONSTITUTION.md` 优先
- `plan.md / REQUIREMENTS.md / SPEC.md` 文档门禁
- 分层边界提醒
- 默认校验命令

## 4. 最常用工作流

### 方式 A：先生成到文件，再交给 mini

```powershell
npm run agent:mini:task -- `
  --task "Fix the dashboard table header alignment issue in presentation only." `
  --scope presentation `
  --output .tmp/mini-presentation-task.md
```

然后把生成内容读出来，作为 `mini` 的任务输入：

```powershell
$task = Get-Content .tmp/mini-presentation-task.md -Raw
mini -t $task
```

### 方式 B：直接管道到变量

```powershell
$task = npm run agent:mini:task -- `
  --task "Fix the dashboard table header alignment issue in presentation only." `
  --scope presentation | Out-String

mini -t $task
```

## 5. 常用示例

### 5.1 只改 `presentation/`

```powershell
npm run agent:mini:task -- `
  --task "Fix the dashboard table header alignment issue in presentation only." `
  --scope presentation `
  --extra-rule "Do not modify data_fetch, strategy, notification, or shared." `
  --output .tmp/mini-presentation-task.md
```

### 5.2 只改 `data_fetch/`

```powershell
npm run agent:mini:task -- `
  --task "Fix the subscription fetch normalization bug for Beijing exchange IPO rows." `
  --scope data_fetch `
  --validate "python data_dispatch.py ipo" `
  --output .tmp/mini-data-fetch-task.md
```

### 5.3 只改 `strategy/`

```powershell
npm run agent:mini:task -- `
  --task "Fix the convertible bond visible-row filtering logic for terminal zero-price rows." `
  --scope strategy `
  --validate "python data_dispatch.py ah" `
  --validate "python data_dispatch.py ab" `
  --output .tmp/mini-strategy-task.md
```

### 5.4 只改文档

```powershell
npm run agent:mini:task -- `
  --task "Draft the plan and contract updates for a new dashboard API field." `
  --scope docs `
  --output .tmp/mini-doc-task.md
```

## 6. 这个仓库里的推荐流程

1. 先让 Codex 判断这次需求是不是会改契约。
2. 如果会改契约，先更新：
   - `refactor_docs/001-monitor-refactor/plan.md`
   - `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
   - `refactor_docs/001-monitor-refactor/SPEC.md`
3. 再用 `npm run agent:mini:task -- ...` 生成窄范围任务。
4. 把生成结果交给 `mini-SWE-agent` 执行。
5. 执行后再回到 Codex 做 diff 复查和整体验证。

## 7. 什么时候不要让 mini 直接开工

如果你还不确定下面这些问题，先不要直接开跑：

- 这是代码问题还是契约问题？
- 该改 `presentation/` 还是其实要动 `strategy/`？
- 这次改动会不会影响 `config.yaml`、API、部署行为？

这类场景先让 Codex做规划，再把明确任务交给 `mini-SWE-agent`。

## 8. 一条推荐命令

你最常用的应该是这一条：

```powershell
npm run agent:mini:task -- `
  --task "Replace this sentence with your exact implementation task." `
  --scope presentation `
  --output .tmp/mini-task.md
```

然后：

```powershell
$task = Get-Content .tmp/mini-task.md -Raw
mini -t $task
```
