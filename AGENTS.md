# Alpha monitor Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-23

## Active Technologies

- Node.js `>=18` + Python `3.x`（当前仓库为 Node 服务 + Python 数据调度混合运行） + `express`、`cors`、`yaml`、`akshare`、`pandas`、`requests`、`beautifulsoup4`、`numpy` (001-monitor-refactor)

## Project Structure

```text
data_fetch/
strategy/
presentation/
notification/
shared/
tools/
runtime_data/
refactor_docs/
```

## Commands

npm run check
npm run check:boundaries
python data_dispatch.py exchange-rate
python data_dispatch.py ah
python data_dispatch.py ab

## Code Style

Node.js `>=18` + Python `3.x`（当前仓库为 Node 服务 + Python 数据调度混合运行）: Follow standard conventions

## Recent Changes

- 001-monitor-refactor: Added Node.js `>=18` + Python `3.x`（当前仓库为 Node 服务 + Python 数据调度混合运行） + `express`、`cors`、`yaml`、`akshare`、`pandas`、`requests`、`beautifulsoup4`、`numpy`

<!-- MANUAL ADDITIONS START -->
## Workflow Gate

This repository follows the constitution-first workflow below:

1. Read `CONSTITUTION.md` before starting any task. It is the highest-priority project guidance.
2. Use `/plan` first and write or update `refactor_docs/001-monitor-refactor/plan.md` before entering implementation.
3. Before coding, update the contract documents impacted by the approved plan:
   - `refactor_docs/001-monitor-refactor/REQUIREMENTS.md`
   - `refactor_docs/001-monitor-refactor/SPEC.md`
4. Only implement after the constitution, plan, requirements, and spec are aligned.

If the constitution is amended, update both `CONSTITUTION.md` and `.specify/memory/constitution.md` together.

## Server Profile

For any server login, deployment, environment-variable, or service-restart task:

1. Read `ops/server_profile.local.yaml` first if it exists.
2. Reuse the stored connection and service parameters instead of asking again.
3. If required fields are still blank, ask only for the missing items.
<!-- MANUAL ADDITIONS END -->
