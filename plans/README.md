# Durable Plans

Detailed plans for complex formal tasks. Every plan maps to a stable `T-###` task in `BACKLOG.md` or `BACKLOG_DONE.md`. Ideas cannot own plans.

## File Naming

Use:

```text
YYYY-MM-DD-HHMM_T-000_status_short-slug.md
```

Allowed statuses:

- `draft`: confirmed for storage but incomplete and non-binding.
- `pending`: complete enough for plan-approval review.
- `confirmed`: plan approved and eligible for later activation.
- `implemented`: completed and verified.
- `superseded`: replaced by a newer plan.

Parking and blocking apply to tasks, not plan statuses.

## Three-Gate Rule

Before writing new or materially revised Codex-authored plan content, present its material wording for formulation confirmation. That confirmation permits storage at the appropriate non-implementation state; it does not approve the plan or activate implementation.

Plan approval changes a complete `pending` plan to `confirmed`. It may remain outside `Now` with `Stage: Ready`. A later activation request to implement or resume confirmed work moves the task to `Now + Implementation` automatically.

## Rules

- Complex work requires a confirmed detailed plan before `Ready` or `Now`.
- Simple, low-risk work requires a confirmed lightweight plan embedded in its backlog record before `Ready` or `Now`.
- A lightweight plan uses the task's Goal, Acceptance, Scope Exclusions, Dependencies, and Verification fields and records `Plan Type: Lightweight`, `Plan Status`, and `Plan Reference: embedded in this task`.
- A detailed-plan task records `Plan Type: Detailed`, a synchronized plan status, and a repository-relative Markdown link to the exact plan file.
- Current plan status follows stage: none at `Discussion`, `draft` at `Plan drafting`, `pending` at `Plan review`, `confirmed` at `Ready`, `Implementation`, or `Verification`, and `implemented` at `Done`. `Blocked` may retain no plan or a `draft`, `pending`, or `confirmed` plan.
- Each task has at most one non-`superseded` detailed plan. A superseded plan remains indexed history and cannot be the task's current plan reference.
- Detailed plans contain exactly one Task ID and one Status metadata field.
- Keep at most one task in `Now`.
- `Implementation` and `Verification` exist only in `Now`; `Now` uses only those stages.
- Read `plans/000_EXECUTIVE_PLAN.md` first, then only plans relevant to the current task.
- Rename the file when status changes and update the executive index in the same change.
- Intentionally parked tasks retain an eligible non-active stage and record `Resume When`; blocked tasks use `Parked + Blocked` and record `Blocked By`. The linked plan keeps its existing plan status.
- When a blocker clears, restore the stage from plan status: no plan -> `Discussion`, `draft` -> `Plan drafting`, `pending` -> `Plan review`, or `confirmed` -> `Ready`.
- Do not store secrets, private data, or generated sensitive content in plans.

## Plan Contents

Include the task ID, status, user input basis when supplied, Codex additions, summary, scope and exclusions, implementation changes, interfaces/data/configuration effects, verification, assumptions, risks, and rollback or migration considerations when relevant.
