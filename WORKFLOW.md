# Development Workflow

Human-facing collaboration contract for task intake, planning, approval, implementation, verification, and closure. `AGENTS.md` contains the detailed execution instructions.

## Sources of Truth

- `DESIGN_BRIEF.md`: product outcomes, principles, and user workflows.
- `PRODUCT_DESIGN.md`: cross-product information architecture, interaction patterns, UI states, responsive behavior, and accessibility conventions.
- `ARCHITECTURE.md`: system boundaries, data ownership, and major technical decisions.
- `BACKLOG.md`: unfinished formal tasks, priority, status, stage, and planning horizons.
- `BACKLOG_DONE.md`: completed formal tasks.
- `IDEA_INBOX.md` and `IDEA_ARCHIVE.md`: informal ideas and their outcomes.
- `plans/`: detailed plans; start with `plans/000_EXECUTIVE_PLAN.md` as the current index.
- `PROJECT_LOG.md`: decisions, outcomes, verification, and residual risk.
- `TESTING_PLAN.md`: risk-based verification.
- `README.md`: setup, commands, repository map, and limitations.
- `AGENTS.md`: repository-wide contributor and execution requirements.

## Roles and Authority

### User Decides

- product outcome, priority, and meaningful scope changes;
- material Codex-authored wording stored in durable project records;
- plan approval and the later activation of confirmed work;
- material architecture, security/privacy, persistent-data, dependency/provider, cost, and destructive-operation choices;
- final acceptance when product judgement or access to real systems is required.

### Codex Does

- inspect relevant files and explain evidence, options, risks, and tradeoffs;
- propose grounded task, plan, design, workflow, and decision wording for review;
- implement approved scope using conservative judgement for routine details;
- run proportionate verification and keep affected documents consistent;
- report changed files, checks, and residual risk.

### Codex Must Pause

Pause before a meaningful change to product scope, approved architecture, security/privacy, persistent data, external dependencies/providers, material cost, or destructive behavior. Also pause before storing an unconfirmed material formulation or making a significant pivot from an approved plan.

## Three Independent Gates

### 1. Formulation Confirmation

Before Codex stores new or materially rewritten project wording based on discussion, it presents the material formulation for explicit confirmation. A request to save or capture permits drafting in the conversation, not writing to files. Confirmation to store wording does not approve a plan or activate implementation.

Exact user wording, factual metadata, verification results, and mechanical updates following a confirmed decision do not require a second wording review.

### 2. Plan Approval

A complete plan is `pending` while awaiting plan approval. Explicit approval changes it to `confirmed` but leaves its task outside `Now` unless the same instruction also clearly requests implementation.

### 3. Activation

Activation starts or resumes a task whose plan is already `confirmed`. “Implement”, “continue”, “resume”, “go on”, or an equivalent explicit request activates the work, moves the task to `Now + Implementation`, and makes it the single active task.

## User-Input Grounding

Use the user's outcome, constraints, terminology, exclusions, and decisions as the proposal basis. Separate material Codex assumptions, defaults, or recommendations under `Codex Additions`. Omit `User Inputs` when none exist.

## Status and Stage

Every unfinished formal task has both fields.

Status describes where the task sits:

- `Now`: the single active task.
- `Next`: queued after active work.
- `Later`: valid work intentionally deferred within the normal queue.
- `Parked`: work intentionally paused or unable to proceed.
- `Done`: completed work stored in `BACKLOG_DONE.md`.

Stage describes what is needed next:

- `Discussion`, `Plan drafting`, `Plan review`, `Ready`, `Implementation`, `Verification`, or `Blocked`.

`Implementation` and `Verification` exist only in `Now`, and `Now` uses only those stages. Intentional parking uses `Parked` with an eligible non-active stage and a non-empty `Resume When`. Blocking uses `Parked + Blocked` with a non-empty `Blocked By`. Done tasks have no stage.

Every unfinished task appears under the `BACKLOG.md` section matching its Status. Completed count, Current Focus, Planning Horizons, and executive-plan summaries are checked projections of task and plan records, not independently editable state. Each task field and each detailed-plan metadata field appears at most once.

## Lifecycle

```text
I-### idea -> discussion -> confirmed T-### formulation
-> Later/Next + Discussion -> Plan drafting -> Plan review
-> confirmed plan + Ready -> activation -> Now + Implementation
-> Now + Verification -> Done -> Backlog Done

Simple work:
confirmed embedded Lightweight Plan -> activation -> Now + Implementation

Complex work:
confirmed linked Detailed Plan -> activation -> Now + Implementation

Intentional parking:
eligible non-active stage -> Parked + same stage + Resume When

Blocked work:
eligible unfinished stage -> Parked + Blocked + Blocked By
```

At most one task may be `Now`. A lightweight plan is embedded in a simple, low-risk task record and comprises its Goal, Acceptance, Scope Exclusions, Dependencies, and Verification. A detailed plan is a separate file linked from a complex task. Either plan must be `confirmed` before `Ready` or `Now`. If active work is intentionally parked, return its stage to `Ready` because active stages cannot exist outside `Now`; record resumption conditions and context in `Resume When` and Notes.

## Plan States

- `draft`: confirmed for storage but incomplete and non-binding.
- `pending`: complete enough for plan-approval review.
- `confirmed`: plan approved and eligible for later activation.
- `implemented`: completed and verified.
- `superseded`: replaced by a newer plan.

Parking and blocking are task states and do not change a plan's status.

The current plan status follows the task stage:

| Task stage | Current plan status |
| --- | --- |
| `Discussion` | no current plan |
| `Plan drafting` | `draft` |
| `Plan review` | `pending` |
| `Ready`, `Implementation`, or `Verification` | `confirmed` |
| `Blocked` | no plan, `draft`, `pending`, or `confirmed` |
| `Done` | `implemented` |

A task has at most one non-`superseded` detailed plan. Superseded plans remain indexed history but cannot be the task's current plan reference. When a blocker clears, restore the stage deterministically: no plan -> `Discussion`; `draft` -> `Plan drafting`; `pending` -> `Plan review`; `confirmed` -> `Ready`.

## Complex-Plan Design Basis

Every `pending` or `confirmed` detailed plan includes a non-empty `Design Basis`. It identifies only the applicable durable sources, task-specific confirmed design decisions, open decisions requiring user confirmation, relevant loading/empty/error/disabled/destructive/success states, and accessibility and responsive implications. Product outcomes and workflows belong in `DESIGN_BRIEF.md`; reusable cross-product UX rules belong in `PRODUCT_DESIGN.md`; technical constraints belong in `ARCHITECTURE.md`; and feature-only decisions remain in the plan unless later confirmed work promotes them to a durable source.

## Close Criteria

Close a task only when expected and error behavior are complete, required checks pass, affected documentation is current, any plan is renamed `implemented`, and `PROJECT_LOG.md` records the outcome and residual risk. Move the full task record from `BACKLOG.md` to `BACKLOG_DONE.md` in the same change.

## Documentation Update Matrix

| Change | Required update |
| --- | --- |
| Product outcome, principle, or user workflow | `DESIGN_BRIEF.md` |
| Cross-product information architecture, interaction pattern, UI state, responsive behavior, or accessibility convention | `PRODUCT_DESIGN.md` |
| System boundary, data ownership, provider, persistence, or deployment | `ARCHITECTURE.md` |
| Task, priority, status, stage, blocker, or horizon | `BACKLOG.md` |
| Completed formal task | move to `BACKLOG_DONE.md` |
| Informal idea or idea outcome | `IDEA_INBOX.md` or `IDEA_ARCHIVE.md` |
| Detailed plan or plan status | `plans/` and executive plan |
| Decision, outcome, verification, or residual risk | `PROJECT_LOG.md` |
| Setup, command, repository map, operation, or limitation | `README.md` |
| Test strategy, command, or coverage expectation | `TESTING_PLAN.md` |
| Collaboration or execution rule | `WORKFLOW.md` and `AGENTS.md` |

`ARCHITECTURE.md` is always included for architecture changes. If the project later adopts a dedicated workspace-design document or another narrower source of truth, add it to the Sources of Truth, `PRODUCT_DESIGN.md` ownership map, and this matrix in the same confirmed change; do not create one speculatively.

## Standard Requests

- `Capture this exact wording as an idea.`
- `Discuss T-000.`
- `Propose durable wording for T-000.`
- `Confirm the wording and store it.`
- `Create a pending plan for T-000.`
- `Approve the plan for T-000 and keep it Ready.`
- `Implement T-000.`
- `Resume T-000.`
- `Verify and close T-000.`
