# Project Backlog

Durable list of unfinished formal work. Create a task only after its material formulation is confirmed. Keep task IDs stable; move completed tasks to `BACKLOG_DONE.md`.

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
  - Plan Type: Lightweight | Detailed
  - Plan Status: draft | pending | confirmed | implemented | superseded
  - Plan Reference: embedded in this task | [plan filename](plans/exact-plan-filename.md)
  - User Inputs: optional; omit when none were provided
  - Codex Additions: optional; identify assumptions and recommendations
  - Goal:
  - Acceptance:
  - Scope Exclusions:
  - Dependencies:
  - Verification:
  - Resume When: required for intentional parking; otherwise omit
  - Blocked By: required for Blocked stage; otherwise omit
  - Notes:
```

Plan fields are absent during `Discussion`. They use `draft` at `Plan drafting`, `pending` at `Plan review`, `confirmed` at `Ready` or active work, and `implemented` only in `BACKLOG_DONE.md`. A blocked task may retain no plan or a `draft`, `pending`, or `confirmed` plan. A lightweight plan is embedded in the task's Goal, Acceptance, Scope Exclusions, Dependencies, and Verification fields. A detailed plan requires an existing repository-relative Markdown link. Plan type is a scope judgement: use Lightweight only for simple, low-risk work and Detailed for complex work.

Place each unfinished task under the heading matching its Status. `Completed task count`, `Current Focus`, and `Planning Horizons` are checked projections: the count equals `BACKLOG_DONE.md`; focus names the sole `Now` task or the canonical empty state; and every unfinished task appears in exactly one planning horizon. Reject duplicate task fields rather than choosing one value. When unblocking, restore the stage from the current plan: none -> `Discussion`, `draft` -> `Plan drafting`, `pending` -> `Plan review`, or `confirmed` -> `Ready`.

## Completed Work

- Registry: `BACKLOG_DONE.md`
- Completed task count: 0

## Current Focus

No task is active. Keep at most one task in `Now`.

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
