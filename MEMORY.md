# Memory

**Retention**: max 50 entries. Oldest auto-deleted when exceeded.

**Record only**: decisions, meaningful actions, verification results, memorable failures, next steps.
**Do not**: dump full conversations.

## Entries

### 2026-04-30 | ELODIE workflow migration completed

- Decision: adopt ELODIE workflow structure for AI collaboration
- Action: created `CLAUDE.md`, `specs/` (5 files), `missions/0430-migrate-to-elodie/`, `MEMORY.md`, `config/`, `templates/`
- Action: archived `refactor_docs/001-monitor-refactor/` → `archive/`
- Action: deprecated `AGENTS.md` and `CONSTITUTION.md`
- Verification: `python3 tools/check_plugin_boundaries.py` passes
- Next: use new workflow for subsequent tasks

### 2026-04-30 | 根目录简化

- Decision: 根目录文件过多，需要清理
- Action: 归档 `AGENTS.md` + `CONSTITUTION.md` → `archive/docs-deprecated/`
- Action: 移动 `db_paths.py` → `shared/paths/db_paths.py`，更新 6 个 tools/ 脚本引用
- Action: 移动 `smoke_check.js` → `tests/smoke_check.js`，更新 `package.json`
- Action: 移动 `RUNBOOK.md` → `docs/RUNBOOK.md`
- Action: 删除 `tools/check_constitution_sync.py`（引用已删除的 `.specify/`）
- Action: 更新 `tools/render_mini_swe_task.py` 工作流引用
- Action: 更新 `INDEX.md` 和 `package.json`
- Verification: `python3 tools/check_plugin_boundaries.py` passes, `node tests/smoke_check.js` passes
