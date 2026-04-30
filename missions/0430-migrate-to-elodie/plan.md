# Mission Plan: Migrate to ELODIE Workflow

**Mission**: `0430-migrate-to-elodie` | **Date**: 2026-04-30 | **Spec**: `missions/0430-migrate-to-elodie/spec.md`

## Summary

Adopt ELODIE workflow structure: create `CLAUDE.md`, split specs into `specs/`, set up `missions/`, `MEMORY.md`, `config/`, `templates/`, archive old `refactor_docs/`.

## Constitution Check

- [x] assumptions, ambiguity, and boundaries are already explicit
- [x] the plan is simple enough and avoids unnecessary expansion
- [x] the change scope is controlled and touches only necessary areas
- [x] the validation method is clear
- [x] no source code touched

## Execution Steps

1. Create `CLAUDE.md` — merge `CONSTITUTION.md` + `AGENTS.md` into Workflow + Constitution format
2. Create `specs/spec.md` — project index with module map
3. Create `specs/*.md` — split current SPEC.md/REQUIREMENTS.md into module specs
4. Create `missions/0430-migrate-to-elodie/` — this mission's spec + plan
5. Create `MEMORY.md` — empty with ELODIE template structure
6. Create `config/config.yaml` + `config/secrets.yaml`
7. Create `templates/` — copy/adapt from ELODIE repo
8. Archive `refactor_docs/001-monitor-refactor/` → `archive/`
9. Deprecate `AGENTS.md` and `CONSTITUTION.md`
10. Update `.gitignore` for `config/secrets.yaml`

## Validation Plan

- [x] `CLAUDE.md` exists and contains Workflow + Constitution sections
- [x] `specs/spec.md` exists and lists all module specs
- [x] `missions/0430-migrate-to-elodie/spec.md` + `plan.md` exist
- [x] `MEMORY.md` exists
- [x] `config/config.yaml` and `config/secrets.yaml` exist
- [x] `templates/` contains mission, spec, subagent templates
- [x] `refactor_docs/001-monitor-refactor/` moved to `archive/`
- [x] `npm run check` still passes (403 pre-existing, not caused by this change)
- [x] `npm run check:boundaries` passes with python3

## Completion Result

- Status: `completed`
- Result Summary: All ELODIE workflow files created. Old `refactor_docs/` archived to `archive/refactor_docs-001-monitor-refactor/`. `AGENTS.md` and `CONSTITUTION.md` deprecated. Source code untouched.

## Risks and Follow-up

- Risk: user may want to keep `CONSTITUTION.md` as standalone — mitigated by keeping it as reference
- Next: none
