# Mission Spec: Migrate to ELODIE Workflow

**Mission**: `0430-migrate-to-elodie`
**Type**: requirements-update
**Created**: 2026-04-30
**Status**: completed
**Input Source**: user request + ELODIE template repo

## Background

Current AI collaboration workflow is heavy:
- `refactor_docs/001-monitor-refactor/` holds 8 files with mixed responsibilities
- `AGENTS.md` is auto-generated + manual additions mixed, duplicates `CONSTITUTION.md`
- No `missions/` directory — tasks have no isolated closure
- No `MEMORY.md` — handoff depends on chat history
- No unified read order for AI sessions

## Goal

Replace the heavy `refactor_docs/` + `AGENTS.md` + `CONSTITUTION.md` combo with ELODIE's lightweight structure. Keep all source code directories unchanged.

## Deliverables

- `CLAUDE.md` — new AI rule entrypoint
- `specs/spec.md` + `specs/*.md` — module-level formal specs
- `missions/` directory with first mission
- `MEMORY.md` — rolling handoff memory
- `config/` — config + secrets placeholder
- `templates/` — reusable document and subagent templates
- Archived old `refactor_docs/`
- Deprecated `AGENTS.md` and `CONSTITUTION.md`

## In Scope

- AI collaboration workflow structure only
- Document migration and reorganization

## Out of Scope

- Source code changes
- Runtime workflow changes
- Technology stack changes

## Constraints

- Each new markdown file must stay under 500 lines
- Do not modify existing template files from ELODIE
- Keep Chinese as non-code documentation language

## Impact on Formal Specs

- Changes formal requirements: `yes`
- If yes, update these files first: `specs/spec.md`

## Assumptions

- User prefers ELODIE structure over current `refactor_docs/` structure
- `CONSTITUTION.md` content should be merged into `CLAUDE.md`, with original kept as reference
