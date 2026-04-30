# Assistant Rules

Owner: user. AI must not modify this file.

## Purpose

This file defines the stable operating rules for AI inside this repository.
It contains only two top-level sections:

- `Workflow`: how AI should read, record, sync, and close work
- `Constitution`: long-lived rules that should not be broken lightly

# Workflow

## Read Order

At the beginning of every new session, AI must read in this order:

1. this assistant rules file (`CLAUDE.md`)
2. `INDEX.md` (project architecture and file index)
3. `README.md`
4. `specs/spec.md`
5. relevant `specs/*.md`
6. `config/config.yaml`
7. the latest entries in `MEMORY.md`

## Formal Spec Rules

- `specs/spec.md` is the project-level map and index.
- `specs/*.md` hold long-lived module or feature requirements.
- If a task changes formal requirements, AI must update `specs/spec.md` and the affected `specs/*.md` before implementation.
- The top-level spec and sub-specs must not contain conflicting rules.
- `specs/spec.md` owns the project overview, map, index, and global rule summary.
- `specs/*.md` own detailed module or feature content.
- Module specs should prioritize: scope boundaries, object or list definitions, filtering or admission rules, data and field definitions, API contracts, formulas or decision rules, display rules, external output rules, and acceptance rules.
- Any markdown document inside this workflow must stay under 500 lines. If it approaches the limit, split or compress it.

## Mission Rules

- Every non-chat AI task must create a mission.
- Non-chat tasks include implementation, review, analysis, and requirement updates.
- Pure chat, pure concept Q&A, or low-context casual discussion must not create a mission.
- Mission folders live under `missions/`.
- Mission names use `MMDD-short-name`.
- Every mission folder contains only:
  - `spec.md`
  - `plan.md`
- `missions/<name>/spec.md` records task type, goal, scope, constraints, and impact on formal specs.
- `missions/<name>/plan.md` records steps, validation, results, and risks.
- `missions/` keeps only the latest 30 missions. Older missions are deleted directly.
- Review is a mission type, not a separate review document system.

## Memory Rules

- `MEMORY.md` keeps only the latest 50 entries.
- Each entry stays short and serves handoff only.
- Record decisions, meaningful actions, verification results, memorable failures, and next steps only.
- Do not dump full conversations into `MEMORY.md`.

## Subagent Rules

- Here, `agent` means subagent, not business module.
- Parallelizable subtasks may use subagents.
- Document checks, read-only exploration, code review, batch cleanup, and independent verification are good candidates for subagents.
- Repeated tasks with stable inputs and outputs are good candidates for subagents.
- Sidecar tasks that do not block the main thread immediately may be delegated to subagents.
- Do not use subagents for tiny tasks, immediately blocking critical-path work, or work with unclear boundaries.
- Do not let multiple subagents modify the same file or the same responsibility area in parallel.
- Do not split work into subagents just to look more advanced.
- If the same task type appears at least twice and its responsibility, input, and output are stable, a reusable subagent template should be added.
- Subagent templates live under `templates/subagents/`.
- AI may add new subagent templates, but may not modify existing ones.
- When task can be clearly split into 2 to 4 independent, well-bounded subtasks, auto-create subagents. Each subagent gets concrete goal, clear output, limited file scope. Main agent keeps blocking critical-path work. Do not create subagents for tiny tasks, tightly coupled tasks, unclear tasks, or scenarios where multiple subagents edit same file.

## Template Rules

- `templates/` is the only template source.
- AI must not modify any existing template file.
- The assistant rules file does not use a template.
- Templates are reference material, not mandatory text to copy literally.
- AI should adapt templates to the current task, keep only relevant parts, and remove empty sections.
- AI may rewrite using template structure without copying every field, heading, or example literally.
- If a truly new document type appears, AI may add a new template file.
- When creating new markdown or yaml files, AI should reference template structure and fields, but should not apply templates mechanically.
- If existing templates are insufficient, AI may propose template changes but may not change them directly.

## Config Rules

- Non-sensitive configuration lives in `config/config.yaml`.
- Sensitive information lives only in `config/secrets.yaml`.
- `config/secrets.yaml` must be ignored by git.
- Configuration keys must use `snake_case`.
- Markdown must not contain real keys or passwords.
- Existing root `config.yaml` is preserved during transition. New config entries go to `config/config.yaml`.

## Completion Rules

- Verify the actual change.
- Update the current mission files.
- If the task has handoff value, update `MEMORY.md`.
- If requirements changed, sync the formal specs first.
- Prefer existing check commands: `npm run check`, `npm run check:boundaries`, `python data_dispatch.py exchange-rate`, `python data_dispatch.py ah`, `python data_dispatch.py ab`.
- When a task creates new files or moves existing files, update `INDEX.md` to reflect the change.
- When a task changes a module's responsibilities, update both the module spec and `INDEX.md`.

## Non-Goals

- This workflow does not enforce a source-code directory structure.
- This workflow does not require `features/` or any specific implementation layout.

# Constitution

## 1. Think Before Coding

Do not assume. Do not hide confusion. Surface assumptions, ambiguity, and tradeoffs.
If multiple reasonable interpretations exist, list them instead of silently deciding for the user.
If a key point is unclear, stop and clarify.

## 2. Simplicity First

Use the minimum code that solves the problem.
Do not add features beyond the request.
Do not create abstractions for one-off code.
Do not add flexibility or configurability that was not requested.
Do not write error handling for unrealistic hypothetical scenarios.
If 50 lines can solve it, do not write 200.

## 3. Surgical Changes

Change only what is directly related to the current task.
Do not casually improve unrelated code, comments, or formatting.
Do not refactor things that are not broken.
If your change creates orphaned code, clean up the orphaned code caused by your own change.
Every change should trace directly back to the current task.

## 4. Goal-Driven Execution

Every task should define verifiable success criteria before implementation.
Multi-step tasks should be broken into short steps with explicit verification.
Weak goals like "just make it run" are not enough; they should be turned into checkable, reproducible, reviewable outcomes.

## 5. Truth First

Always prefer real data, real interfaces, real files, and real outputs.
If real input is unavailable, clearly expose the limitation, empty state, impact range, or blocker.
Do not use fake data, demo data, placeholder results, or fabricated outputs as if they were real.

## 6. Execute Directly

The user is not a programmer. If AI can independently analyze, modify, configure, run, and verify, it should do so directly.
Ask the user to step in only when permissions, keys, accounts, human judgment, or external resources are truly required.

## 7. Separate Architecture

Different responsibilities should remain separated.
Data fetching, data processing, result calculation, presentation, notifications, storage, and shared capabilities should not remain mixed in the same long-term responsibility unit.
A change in one function should not automatically drag unrelated functions with it.
Shared capabilities should have clear ownership rather than being privately copied and scattered.

Project structure:
- `data_fetch/` = fetch + normalize only
- `strategy/` = business calculation + rule evaluation only
- `presentation/` = page, API shaping, display logic only
- `notification/` = push config, format, schedule only
- `shared/` = config, paths, time, runtime state, common utilities only

Cross-domain logic must sink to `shared/`. No direct plugin-to-plugin coupling.

## 8. Centralize Configuration

All long-lived, behavior-changing parameters must enter a unified configuration entry point.
Do not hardcode paths, thresholds, switches, URLs, account fields, or equivalent settings across multiple places long term.
When adding formal configuration, add it to config first, then allow implementation to use it.

`config.yaml` is the single formal config contract.

## 9. User Ownership

The assistant rules file (`CLAUDE.md`) is user-owned. AI must not modify it.
Existing template files are user-owned. AI must not modify them.
AI may add templates, but if an existing template is insufficient, AI may only propose changes instead of editing it directly.

## 10. Subagent Consolidation

Repeated, well-bounded, independently verifiable work should be consolidated into reusable subagent templates.
Each subagent must keep a single responsibility and must not mix multiple long-term responsibilities.
Subagent templates must define inputs, outputs, execution boundaries, and forbidden areas clearly.
Do not create subagents for one-off, tiny, or immediately solvable main-thread tasks.
When multiple subagents run in parallel, they must not own the same write area or overwrite each other.

## 11. Documentation Language

Non-code documentation in this repository is written in Chinese.
Code comments for core logic must be in Chinese.
