# Project Backlog

Durable list of unfinished formal work. Store a task only after formulation confirmation or scoped write-first authorization; mark an unconfirmed proposal explicitly. Keep task IDs stable; move completed tasks to `BACKLOG_DONE.md`.

## Status and Priority

- Status: `Now`, `Next`, `Later`, or `Parked`; see `WORKFLOW.md` for lifecycle rules.
- Stage: `Discussion`, `Plan drafting`, `Plan review`, `Ready`, `Implementation`, `Verification`, or `Blocked`.
- Priority: `P0` urgent/blocking, `P1` important, `P2` normal, `P3` optional.
- Areas: `Product`, `Architecture`, `Data`, `UI`, `Testing`, `Security`, `Operations`, `Docs`.
- `Implementation` and `Verification` are valid only in `Now`; `Now` uses only those stages.
- Intentional parking uses an eligible non-active stage plus `Resume When`. Blocking uses `Parked + Blocked` plus `Blocked By`.

## Task Template

```md
- [ ] T-000 Short task title
  - Status: Now | Next | Later | Parked
  - Stage: Discussion | Plan drafting | Plan review | Ready | Implementation | Verification | Blocked
  - Priority: P0 | P1 | P2 | P3
  - Area:
  - Source: user request | review finding | bug report | maintenance
  - Revision: 1
  - Formulation Status: proposed | confirmed
  - Formulation Evidence: dated confirmation; required when confirmed
  - Storage Authorization: required while proposed; omit otherwise if not useful
  - Plan Approval Evidence: required for a confirmed plan; identify revision
  - Activation Evidence: required in Now; preserve historical authority afterward
  - Epic: optional existing E-###; otherwise omit
  - Plan Type: Lightweight | Detailed
  - Plan Status: draft | pending | confirmed
  - Plan Reference: embedded in this task | [plan filename](plans/exact-plan-filename.md)
  - User Inputs: optional; omit when none were provided
  - Codex Additions: optional; identify assumptions and recommendations
  - Goal:
  - Acceptance:
  - Scope Exclusions:
  - Dependencies: external constraints and explanation; task IDs go in typed fields
  - Planning Prerequisites: None | T-101, T-102
  - Implementation Prerequisites: None | T-101, T-102
  - Acceptance Prerequisites: None | T-101, T-102
  - Verification:
  - Resume When: required for intentional parking; otherwise omit
  - Blocked By: required for Blocked stage; otherwise omit
  - Resume Stage: Implementation | Verification; for previously active parked confirmed work
  - Checkpoint Updated: YYYY-MM-DD
  - Completed Work:
  - Remaining Work:
  - Next Action:
  - Open Issues:
  - Executor:
  - Work Context: optional; branch/worktree and overlapping ownership
  - Notes:
```

Plan fields are absent during `Discussion`. They use `draft` at `Plan drafting`, `pending` at `Plan review`, `confirmed` at `Ready` or active work, and `implemented` only in `BACKLOG_DONE.md`. A blocked task may retain no plan or a `draft`, `pending`, or `confirmed` plan. A lightweight plan is embedded in the task's Goal, Acceptance, Scope Exclusions, Dependencies, typed prerequisites, and Verification fields. A detailed plan requires an existing repository-relative Markdown link. Plan type is a scope judgement: use Lightweight only for simple, low-risk work and Detailed for complex work.

Place each unfinished task under the heading matching its Status. `Completed task count`, `Current Focus`, and `Planning Horizons` are checked projections: the count equals `BACKLOG_DONE.md`; focus lists all `Now` tasks and stages or the canonical empty state; and every unfinished task appears in exactly one planning horizon. Reject duplicate task fields rather than choosing one value. When unblocking, restore the stage from the current plan: none -> `Discussion`, `draft` -> `Plan drafting`, `pending` -> `Plan review`, or `confirmed` -> `Ready`.

The schema shows conditional fields, not values to paste unchanged. Omit plan fields at Discussion, unused Epic/prerequisite fields, and checkpoints on unstarted tasks. Once any checkpoint field exists, keep all six. Authority and lifecycle details are in [WORKFLOW.md](WORKFLOW.md).

## Work In Progress

- WIP advisory limit: 3

## Epics

No formal epics.

## Epic Template

```md
- [ ] E-001 Bounded outcome
  - Revision: 1
  - Formulation Status: confirmed
  - Formulation Evidence: dated user confirmation of this scope
  - Progress: Planned
  - Goal:
  - Scope:
  - Scope Exclusions:
  - Completion Criteria:
  - Coordination Plan: [E-001 coordination](plans/000_EXECUTIVE_PLAN.md#e-001)
```

A proposed epic instead uses Formulation Status: proposed and Storage Authorization. Paused epics require Resume When. Children retain separate plan approval and activation. Do not create live epics merely to demonstrate the template.

## Completed Work

- Registry: `BACKLOG_DONE.md`
- Completed task count: 0
- Completed epic count: 0

## Current Focus

No tasks are in `Now`.

## Planning Horizons

No planning horizons exist because no unfinished formal tasks remain.

## Now

No selected tasks.

## Next

No queued tasks.

## Later

No deferred tasks.

## Parked

No intentionally parked or blocked tasks.
