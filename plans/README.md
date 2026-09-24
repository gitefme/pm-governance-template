# Durable Plans

Detailed plans for complex formal tasks. Every plan maps to a stable `T-###` task in `BACKLOG.md` or `BACKLOG_DONE.md`. Ideas cannot own plans.

## File Naming

Use:

```text
YYYY-MM-DD-HHMM_T-000_status_short-slug.md
```

Allowed statuses:

- `draft`: authorized for storage but incomplete and non-binding.
- `pending`: complete enough for plan-approval review.
- `confirmed`: plan approved and eligible for later activation.
- `implemented`: completed and verified.
- `superseded`: replaced by a newer plan.

Parking and blocking apply to tasks, not plan statuses.

## Three-Gate Rule

Before writing new or materially revised Codex-authored plan content, present its material wording for formulation confirmation. That confirmation permits storage at the appropriate non-implementation state; it does not approve the plan or activate implementation.

Plan approval changes a complete `pending` plan to `confirmed`. It may remain outside `Now` with `Stage: Ready`. Activation starts new work in `Now + Implementation`; resuming verification retains Verification, and parked work uses its recorded Resume Stage. An explicit user instruction can satisfy multiple gates without repeated permission requests.

Explicit write-first authorization allows the named proposal package to be stored before final formulation review. Mark the task Formulation Status: proposed and record Storage Authorization. Pending means a complete proposal; unresolved material choices keep the plan draft. Follow WORKFLOW.md for approval and revision authority.

## Rules

- Complex work requires a confirmed detailed plan before `Ready` or `Now`.
- Simple, low-risk work requires a confirmed lightweight plan embedded in its backlog record before `Ready` or `Now`.
- A lightweight plan uses the task's Goal, Acceptance, Scope Exclusions, Dependencies, typed prerequisites, and Verification fields and records `Plan Type: Lightweight`, `Plan Status`, and `Plan Reference: embedded in this task`.
- A detailed-plan task records `Plan Type: Detailed`, a synchronized plan status, and a repository-relative Markdown link to the exact plan file.
- Current plan status follows stage: none at `Discussion`, `draft` at `Plan drafting`, `pending` at `Plan review`, `confirmed` at `Ready`, `Implementation`, or `Verification`, and `implemented` at `Done`. `Blocked` may retain no plan or a `draft`, `pending`, or `confirmed` plan.
- Each task has at most one non-`superseded` detailed plan. A superseded plan remains indexed history and cannot be the task's current plan reference.
- Detailed plans contain exactly one Task ID and one Status metadata field. Current plans also carry exactly one positive Task Revision matching their task record; the task owns Formulation Evidence and Plan Approval Evidence.
- Every `pending` or `confirmed` detailed plan contains a non-empty `Design Basis`. Draft plans may add it while design is still being shaped; implemented and superseded history is not rewritten retroactively.
- Several started tasks may remain in `Now`, with full checkpoints and warning-only WIP guidance.
- `Implementation` and `Verification` exist only in `Now`; `Now` uses only those stages.
- Read `plans/000_EXECUTIVE_PLAN.md` first, then only plans relevant to the current task.
- Rename the file when status changes and update the executive index in the same change.
- Intentionally parked tasks retain an eligible non-active stage and record `Resume When`; blocked tasks use `Parked + Blocked` and record `Blocked By`. The linked plan keeps its existing plan status.
- When a blocker clears, restore the stage from plan status: no plan -> `Discussion`, `draft` -> `Plan drafting`, `pending` -> `Plan review`, or `confirmed` -> `Ready`.
- Do not store secrets, private data, or generated sensitive content in plans.

## Plan Contents

Include the task ID, status, task revision, user input basis when supplied, Codex additions, summary, scope and exclusions, implementation changes, interfaces/data/configuration effects, verification, assumptions, risks, and rollback or migration considerations when relevant.

When design applies, use the `Design Basis` to identify applicable durable sources, task-specific confirmed design decisions, open decisions, expected UI states, and accessibility and responsive implications. Material unanswered implementation decisions keep an implementation plan draft; a confirmed design study may make those decisions its deliverable. When design does not apply, state that the task has no product-design effect. Do not list irrelevant documents just to fill the section.

## Material Revisions

Increase the task Revision for materially changed scope or plan content. Preserve the previous detailed plan as superseded, including dated approval and verification evidence. Create one current draft/pending revision, update its Task Revision, clear current Plan Approval Evidence, and synchronize the task reference/index. Move previously started work to Parked with the appropriate planning stage and Resume When; preserve checkpoints and unfinished acceptance.

For a lightweight plan, preserve the old confirmed wording and approval as a dated PROJECT_LOG.md entry before replacing the embedded plan. Lightweight work still needs renewed approval of material changes. Mechanical renames/status changes do not increase Revision. Do not rewrite implemented or superseded history to add new schema fields.

## Epics and Coordination

Epics use the executive plan's Epic Coordination section, not a second task-plan family. Membership is each task's Epic field. Keep milestones, next action, integration issues, and archived coordination history there. Roadmaps and temporary execution tables are optional registered projections; they do not approve or activate tasks.

## Metadata Example

```md
- Task ID: T-101
- Task Revision: 1
- Status: `pending`
```
