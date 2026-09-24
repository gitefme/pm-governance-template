# Development Workflow

Human-facing contract for project intake, planning, approval, execution, verification, and closure. `AGENTS.md` provides the contributor entry point; this file owns the lifecycle and schemas.

Governance version: 2

## Sources of Truth

- `DESIGN_BRIEF.md`: confirmed product outcomes, principles, exclusions, and workflows.
- `PRODUCT_DESIGN.md`: confirmed cross-product interactions, UI states, responsive behavior, and accessibility.
- `ARCHITECTURE.md`: confirmed system boundaries, data ownership, and technical decisions.
- `BACKLOG.md`: unfinished formal tasks, open epics, checkpoints, and WIP guidance.
- `BACKLOG_DONE.md`: completed tasks and epics, counted separately.
- `IDEA_INBOX.md` and `IDEA_ARCHIVE.md`: informal ideas and their outcomes.
- `plans/000_EXECUTIVE_PLAN.md`: task-plan index, current-work projections, and epic milestones.
- `plans/README.md`: detailed-plan authoring and revision rules.
- `PROJECT_LOG.md`: dated decisions, approval evidence, outcomes, verification, and residual risk.
- `TESTING_PLAN.md`: risk-based verification requirements.
- `README.md`: setup, commands, repository map, and limitations.
- `AGENTS.md`: repository-wide contributor requirements.
- `WORKFLOW.md`: governance authority, lifecycle, and record schemas.

Optional live artifacts must be registered under Optional Artifacts below. Examples under `docs/examples/` and the migration/operations guides are reference material, not adopted project requirements. Template maintenance is recorded separately from the empty project bootstrap in `docs/TEMPLATE_MAINTENANCE.md`.

## Roles and Authority

The user decides product outcomes, priorities, material wording, plan approval, activation, and acceptance requiring product judgement or real-system access. Material changes to scope, architecture, persistent data, privacy/security, providers/dependencies, cost, or destructive behavior require that authority.

Codex inspects relevant evidence, proposes grounded wording, implements authorized scope, resolves routine details, runs proportionate checks, and reports residual risk. Pause for an unapproved material change or significant departure from an approved plan. Existing explicit authorization remains valid within its scope; do not repeatedly request it.

## Three Independent Gates

### 1. Formulation Confirmation

Present new or materially revised Codex-authored project wording and receive explicit confirmation before storing it. A normal request to save or capture permits a proposal in conversation. Exact user wording, factual observations, verification results, and mechanical updates following a confirmed decision are exempt from a second wording review.

An explicit instruction to write proposals first for final review permits storage within the named package. Record its Storage Authorization and use Formulation Status: proposed until confirmed. Complete plans use `pending`; materially unresolved plans use `draft`. This permission does not approve plans or start implementation. It is scoped authorization, not a permanent exception for ordinary save requests.

### 2. Plan Approval

Explicit approval of a complete `pending` plan makes it `confirmed`. Record the approved revision and evidence. Approval alone leaves the task outside Now. A single user instruction may explicitly satisfy more than one gate; record each decision without demanding repeated confirmation. An instruction to implement an unapproved proposal does not by itself establish approval of unspecified material choices.

### 3. Activation

An explicit request to implement or resume identified, confirmed work authorizes execution. New implementation starts in Now + Implementation. Resuming Now + Verification preserves Verification; resuming parked work uses its recorded Resume Stage. Resolve ambiguity only when the intended task or authority cannot be determined from the conversation.

An explicitly named batch may authorize a sequence of confirmed, dependency-eligible tasks. Check eligibility before each task. A blocked row waits; skip to an independent row only if the authorized batch permits it. Epic, roadmap, or batch-table approval alone does not activate child tasks.

## User-Input Grounding

Preserve supplied outcomes, terminology, constraints, exclusions, and decisions. Label material assumptions, recommendations, and unanswered defaults as Codex Additions. Omit User Inputs when none were supplied; never invent them.

## Approval and Revision Records

Every unfinished task and open epic contains these flat fields:

- Revision: a positive integer identifying the current material revision.
- Formulation Status: `proposed` or `confirmed`.
- Formulation Evidence: a dated user instruction or local evidence link for confirmed wording.
- Storage Authorization: required while proposed; identifies the explicit write-first permission and its scope.

Keep the confirmed formulation's evidence when its wording is unchanged. Increase Revision for material task or plan changes; mechanical status/checkpoint updates do not increase it. Invalidate approval of a materially changed plan. A proposed formulation cannot have a confirmed plan, enter Ready/Now, have an In progress epic, or be Done.

Tasks with confirmed or implemented plans also require Plan Approval Evidence naming the approval and revision. Now tasks require Activation Evidence identifying the user instruction or authorized batch and its scope. Evidence is an auditable account, not something the checker can authenticate. Approval for the current plan lives in its task record; detailed plans carry Task Revision as a checked projection. This adds no plan statuses.

Do not use a generic Review Status field on live task/epic records or current plans: formulation, plan approval, execution, and acceptance are different facts. Preserve old labels in explicitly dated historical notes or superseded plans. User acceptance belongs in Verification and linked evidence; technical readiness does not imply acceptance.

Untouched completed history may retain its original schema. On migration, recover unfinished-task authority from actual evidence; missing evidence is an unresolved decision, not permission to invent approval.

## Status and Stage

Status is Now, Next, Later, Parked, or Done. Now contains started implementation or verification; several tasks may remain there between sessions. Next contains unstarted work. Later is deferred queue work. Parked is explicitly deferred or blocked work. Done lives only in BACKLOG_DONE.md.

Stage is Discussion, Plan drafting, Plan review, Ready, Implementation, Verification, or Blocked. Done has no Stage. Implementation and Verification exist only in Now; Now uses only those two stages. Every task is under the section matching its Status. Reject duplicate fields and metadata rather than choosing a value.

Current Focus is the ascending list of every Now task, using `- T-101 — ` followed by its backtick-wrapped stage and a period. With none it reads: No tasks are in `Now`. Planning Horizons lists each unfinished task exactly once. Counts, focus, horizons, and executive summaries are projections of records. Executive plan-review, confirmed-later, and blocked-plan summaries include both lightweight and detailed plans, with sorted unique task IDs.

## Lifecycle and Resumption

| Event | Result |
| --- | --- |
| Formulation confirmed | Queue task at Discussion; no current plan yet |
| Plan prepared | Plan drafting + draft, then Plan review + pending |
| Complete plan approved | Ready + confirmed; activation still required |
| New work activated | Now + Implementation, confirmed plan, assigned executor, full checkpoint |
| Implementation complete | Now + Verification; retain outstanding acceptance |
| Ordinary interruption | Keep the current Now stage; update checkpoint |
| Resume work already in Now | Preserve Implementation or Verification according to remaining work |
| Explicitly defer active work | Parked + Ready, confirmed plan, Resume When, and Resume Stage recording Implementation or Verification |
| Defer unstarted planning/review | Parked with its existing non-active stage and Resume When; draft/pending is not promoted to Ready |
| Genuine blocker | Parked + Blocked + Blocked By; retain plan and checkpoint, and Resume Stage for previously active confirmed work |
| Blocker clears | Restore stage from the current plan: none → Discussion, draft → Plan drafting, pending → Plan review, confirmed → Ready; remove Blocked By |
| Unblocked work awaits activation | Previously started work stays Parked with Resume When; unstarted work returns to Next/Later or intentional Parked |
| Parked confirmed work explicitly resumed | Now + recorded Resume Stage; use Implementation for work that never started |
| Material replan | Preserve evidence and superseded revision; current plan becomes draft/pending and leaves Now; started work stays Parked at the matching stage with Resume When |
| Required verification and acceptance complete | Archive full task at Done and mark its plan implemented |

Clear Resume When and Resume Stage when entering Now. A material replan clears the old Resume Stage because the next phase must be reconsidered when the revised plan is approved. Do not move partly implemented work to Next to reduce WIP. Checkpoints preserve its actual implementation and outstanding acceptance.

## WIP and Checkpoints

BACKLOG.md contains exactly one Work In Progress section with one positive integer WIP advisory limit, initially 3. Count only Now tasks, including Verification. Excess produces a warning, never an automatic status change or a failure based on count alone.

Each Now task has six non-empty fields:

```md
  - Checkpoint Updated: YYYY-MM-DD
  - Completed Work: Observed implementation or verification; None yet is valid.
  - Remaining Work: Unfinished implementation and acceptance.
  - Next Action: First safe resumption action.
  - Open Issues: Blockers, decisions, or pending checks; None known is valid.
  - Executor: Assigned contributor.
```

Use a real calendar date. If any checkpoint field is present, require all six, including outside Now. Keep them when parking and closing. At Done set Remaining Work and Next Action to None. Unassigned is allowed outside Now but must be resolved before execution. Dates are snapshots, not proof that a process is running. Update after meaningful progress, before switching work, at handoff, and on parking/closure. Historical parked/completed records without checkpoints need no speculative backfill.

Work Context optionally records branch, worktree, session, file ownership, and integration order; record it whenever contributors overlap. Agree ownership before editing shared surfaces. Parallel tracking is not permission for automatic delegation or concurrent conflicting writes.

## Typed Prerequisites

Dependencies contains external constraints and explanatory prose. Put task prerequisites in these optional flat fields, each using `None` or a unique comma-separated list such as `T-101, T-102`:

- Planning Prerequisites: tasks that must be Done before drafting the plan.
- Implementation Prerequisites: tasks that must be Done before entering Now.
- Acceptance Prerequisites: tasks that must be Done before closing the task.

Omission means there are no task prerequisites of that type; do not omit an unknown prerequisite to pass validation. A reference to a task in Dependencies must be classified into a typed field. All prerequisite IDs must exist, self-dependencies and cycles across the combined graph are prohibited. All edges require the referenced task to be Done at the stated gate; a partially implemented prerequisite is not a completion edge satisfied.

Planning prerequisites are checked at Plan drafting, Plan review, Ready, Now, and Done. Implementation prerequisites are checked at Now and Done. Acceptance prerequisites are checked at Done. Blocked work can retain a plan while its prerequisites are unresolved. Ready means its plan is confirmed, not that every implementation prerequisite is complete. Informational design exchanges are not completion prerequisites and must be described without creating a false dependency cycle.

## Epics and Milestones

An epic is a bounded outcome with a stable E-### ID. Open epics live under Epics in BACKLOG.md. They have Revision, formulation fields, Progress, Goal, Scope, Scope Exclusions, Completion Criteria, and Coordination Plan. Progress is Planned, In progress, Paused, or Done; Paused requires Resume When. Epics have no task Status/Stage/plan fields and never count toward WIP. An In progress epic may have no Now tasks between child activations.

Each task has at most one optional Epic: E-001 field, the sole membership source. No nested epics or duplicated child records. Standalone tasks remain valid. Use typed prerequisites for cross-epic dependencies. Each child retains its own plan approval and activation gates.

Coordination Plan links to `plans/000_EXECUTIVE_PLAN.md#e-001`. That file has one Epic Coordination section and one `### E-001` block per epic, including archived epics. Each block has exactly one non-empty Next Action, one Open Issues, and at least one milestone:

```md
### E-001

- Next Action: Review the next dependency-eligible child.
- Open Issues: Integrated acceptance remains pending.
- [ ] M1 — First accepted capability. Tasks: T-101.
- [ ] M2 — Combined acceptance. Tasks: T-101, T-102.
```

Milestone IDs are unique local positive numbers. Omit the Tasks suffix while decomposition is pending; do not invent task records. Referenced non-member tasks are external prerequisites. Check a milestone only when every referenced task is Done and the stated acceptance has been verified. Human review checks the evidence; the checker verifies references and completion state. Update coordination after child progress and before selecting the next eligible child.

Close an epic only with at least one member, every member and milestone prerequisite Done, every milestone checked, and verified integrated Completion Criteria. Archive under Completed Epics and a YYYY heading with a checked checkbox, Progress: Done, and Completion Evidence linking to a local log entry or verification document. Retain coordination history and child membership. Completed epic count is independent of task count. Follow-up work gets a new identity.

## Plan States

- `draft`: authorized for storage, incomplete, and non-binding.
- `pending`: complete enough for plan-approval review.
- `confirmed`: approved for its stated revision; activation remains separate.
- `implemented`: completed and verified.
- `superseded`: replaced by a newer revision.

| Task stage | Current plan status |
| --- | --- |
| Discussion | no current plan |
| Plan drafting | draft |
| Plan review | pending |
| Ready, Implementation, Verification | confirmed |
| Blocked | no plan, draft, pending, or confirmed |
| Done | implemented |

Parking and blocking do not themselves change plan status. A task has at most one non-superseded detailed plan. Superseded history remains indexed but cannot be the current Plan Reference. Lightweight plans use Goal, Acceptance, Scope Exclusions, Dependencies, typed prerequisites, and Verification in the task. Complex work uses a linked detailed plan. Both require confirmation before Ready/Now.

## Complex-Plan Design Basis

Every pending or confirmed detailed plan has a non-empty Design Basis. Cover applicable durable sources, confirmed task-specific decisions, unresolved decisions, relevant loading/empty/error/disabled/destructive/success states, and accessibility/responsiveness; otherwise state no product-design effect. Material unresolved implementation decisions keep an implementation plan draft. A confirmed design-study plan may identify those decisions as its output without authorizing their implementation.

Design documents describe the confirmed target, not proof of implementation. Write-first proposals must have a clearly bounded proposed section, storage authority, and unresolved choices. Approved task plans cannot silently replace durable design rules. Record implementation and verification as dated evidence, with their limits.

## Review Handoff and Closure

Before handing over applicable implementation, run the approved technical checks and inspect changed interaction/visual behavior in a real browser. Record source identity (including relevant uncommitted changes), target/environment, date, commands, results, and limits. A commit alone is insufficient when the worktree is dirty. Recheck affected evidence after source or target changes; do not repeatedly rerun unrelated accepted checks without a reason.

A focused handoff states the task/plan, exact page or artifact, action, expected result, and Required/Optional basis. Required acceptance comes from the approved plan; optional exploration adds no gate. Track preparation (Ready, Not prepared, Stopped) separately from user result (Not run, Accepted, Changes requested, Not applicable). A ready example or passing automation does not record user acceptance.

Prepare disposable synthetic examples for unusual failure/recovery states, with direct access instructions, expected results, isolation, lifetime, and scoped cleanup. Check availability before the agreed review. These examples do not qualify live providers, production concurrency, or worker recovery. Handoff does not authorize deployment, real spending, data repair, or permission changes. Documentation-only work uses document checks and readback.

Close only when expected/error behavior, all required technical and user/live checks, prerequisite gates, and affected documentation are complete. Record evidence and residual risk in PROJECT_LOG.md, mark the plan implemented, and move the full record to BACKLOG_DONE.md in the same change. Preserve prior accepted evidence; never infer acceptance from silence, a checklist tick, or automated success alone.

## Optional Artifacts

No optional artifacts adopted.

## Documentation Update Matrix

| Change | Required update |
| --- | --- |
| Product outcome or workflow | DESIGN_BRIEF.md |
| Cross-product UI, accessibility, or responsiveness | `PRODUCT_DESIGN.md` |
| Architecture, ownership, persistence, provider, deployment | ARCHITECTURE.md |
| Task state, revision, authority, prerequisites, checkpoint | BACKLOG.md and executive projections |
| Task closure | BACKLOG_DONE.md, plan/index, counts, PROJECT_LOG.md |
| Epic membership or integrated acceptance | Member records, epic record, executive coordination; archive closed epic |
| Idea or idea outcome | IDEA_INBOX.md or IDEA_ARCHIVE.md |
| Detailed plan or material revision | plans/ and executive index; invalidate changed approval |
| Decision, acceptance, verification, residual risk | PROJECT_LOG.md and owning task; update any registered projection |
| Commands, setup, limitations | README.md and TESTING_PLAN.md where applicable |
| Governance contract | WORKFLOW.md, AGENTS.md, schemas/examples, checker/tests, migration guide |
| Adopt, change, or retire an optional artifact | Optional Artifacts registry, artifact, README.md entry point, affected links |

For an optional artifact, register exactly one row with Artifact, Path, Owner, Inputs, Update When, Retire When. Use a repository-relative Markdown Path link. The registry is its ownership/update matrix; register relevant narrower design sources in PRODUCT_DESIGN.md too. ROADMAP.md, docs/DECISIONS.md, docs/TRACEABILITY.md, docs/REVIEW_HANDOFF.md, and files under plans/temporary/ must be registered when adopted. Other names may be registered explicitly. See [examples and adoption rules](docs/GOVERNANCE_EXTENSIONS.md).
