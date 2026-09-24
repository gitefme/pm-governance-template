# Portable Governance v2 Migration

This guide upgrades the Markdown governance system in a destination project. It is stack-independent. [WORKFLOW.md](../WORKFLOW.md) owns the target contract; [plan guidance](../plans/README.md) owns plan authoring. A version marker alone is not evidence that migration is complete.

## Scope and Authority

Obtain confirmation of the target changes and an explicit instruction to migrate. Apply existing session authority without repeated permission requests. Preserve formulation confirmation, plan approval, and activation as separate decisions, even when one explicit instruction supplies all of them. Migration never approves unrelated task plans, activates feature work, or chooses an application stack.

Inspect the destination's actual Git identity, branch, remote, and dirty files. Preserve its history and unrelated changes. Read only relevant permitted documents and checker/tests. Do not read credential files, copy permission profiles, import example task history, or modify a reference project. Do not install hooks, external dependencies, deploy, commit, or push without the applicable task authority.

## Inventory and Baseline

1. Read AGENTS.md, WORKFLOW.md, the unfinished backlog, executive index, plan guidance, README.md, and TESTING_PLAN.md. Inspect archives and current plans only as needed to reconcile references and counts.
2. Inventory task/epic IDs, current statuses/stages, current and superseded plans, historical approvals, outstanding acceptance, and existing Now work. Identify adopted supplemental documents and their actual owners.
3. Run the destination's documented documentation checker and tests. Record pre-existing failures separately. Use permitted read-only Git metadata and scoped diffs; never expose protected contents.
4. If the destination already declares version 2, compare its actual rules and checker with this contract. Missing typed prerequisites, scoped authority, transition rules, or anchor checks are real migration gaps. Do not duplicate sections or treat the marker as a successful no-op.

## Target Records

Apply the complete lifecycle in WORKFLOW.md and the following schema changes together:

| Surface | Required result |
| --- | --- |
| Workflow | Exactly one visible Governance version: 2 marker and Optional Artifacts registry |
| BACKLOG.md | Unique Work In Progress and Epics sections; positive WIP advisory limit initially 3; independent completed task/epic counts |
| Current Focus | Every Now task in ascending ID order as `- T-101 — ` plus backtick-wrapped stage and a period; empty: No tasks are in `Now`. |
| Unfinished task/open epic | Positive Revision; Formulation Status proposed/confirmed; Formulation Evidence when confirmed or Storage Authorization while proposed |
| Approved task plan | Plan Approval Evidence identifying the approved material revision; current detailed plan's Task Revision matches task Revision |
| Now task | Assigned Executor, Activation Evidence, and all six checkpoint fields |
| Parked started confirmed task | Checkpoint plus Resume Stage: Implementation or Verification; Resume When for intentional parking or Blocked By for a genuine blocker |
| Typed prerequisites | Planning Prerequisites, Implementation Prerequisites, Acceptance Prerequisites; optional, with None or unique comma-separated existing T-### IDs |
| Task membership | At most one optional Epic: E-###; membership is owned only here |
| Epic | Progress, Goal, Scope, Scope Exclusions, Completion Criteria, Coordination Plan; no task state/plan fields |
| Executive plan | Open epics summary, unique Epic Coordination section and block per epic, milestones, Next Action, Open Issues; retain existing plan index/projections |
| Completed registry | Separate Completed Tasks and Completed Epics sections, each using YYYY headings; archived epic has linked integrated Completion Evidence |

An open epic uses Progress Planned, In progress, or Paused; Paused requires Resume When. A closed epic is checked with Progress Done. Coordination links use plans/000_EXECUTIVE_PLAN.md#e-001 and a matching `### E-001` block. Milestones use `- [ ] M1 — Acceptance. Tasks: T-101.`; omit the task suffix while decomposition is pending. Require all referenced tasks Done before checking a milestone. Epic closure requires a member, all members/prerequisites Done, all milestones checked, and verified integrated acceptance.

## Preserve Authority and History

Use recorded confirmation and historical plan evidence to populate authority fields; migration is not a new approval. A dated description of the exact preserved approval source is acceptable when a direct conversation link is unavailable. If evidence is absent or contradictory, surface that uncertainty and retain the work outside execution until resolved. Do not silently invent authority to satisfy a checker.

Replace generic current Review Status fields with scoped authority; retain their original dated wording in history. Keep unchanged plan approval. For material changes, increase Revision, preserve the previous plan as superseded, clear current Plan Approval Evidence, and use one new draft/pending plan. Preserve implemented portions and remaining acceptance in the checkpoint. Lightweight revisions preserve their previous wording/evidence in a dated log entry.

Do not backfill untouched implemented/superseded plans or completed records solely to meet new schema fields. Current draft/pending/confirmed detailed plans need one Task Revision matching the task. Keep the five existing plan statuses unchanged. Maintain filename/embedded status/reference/index consistency and one current detailed plan per task.

## Convert State Truthfully

Allow several started Now tasks; do not move started work to Next to reduce WIP. Ordinary interruptions keep the active stage. Resuming verification remains Verification. For explicit deferral of active confirmed work, use Parked + Ready and record the original active phase in Resume Stage. Planning/review deferral preserves its non-active stage.

When replanning started work, use Parked + Plan drafting or Plan review, preserve the checkpoint, and clear the old Resume Stage until the revised plan is approved. On unblock, derive stage from plan status; previously started work awaiting activation remains Parked with Resume When. Never promote a draft/pending plan to Ready just because it was parked.

Backfill all six Now checkpoints from observations. Completed Work may say None yet; Open Issues may say None known. Use an actual calendar date. Keep checkpoint fields together wherever present. On closure Remaining Work and Next Action become None. Never imply that a dated checkpoint proves a contributor is currently running.

## Classify Prerequisites and Projections

Translate task references in Dependencies into typed fields by meaning, not keyword replacement. Planning prerequisites must be Done before plan drafting, implementation prerequisites before Now, and acceptance prerequisites before Done. All IDs must exist, and the combined completion graph must be acyclic. Keep external conditions and explanation in Dependencies. Unknown classification needs a decision; omission means no prerequisite.

Recalculate counts, focus, planning horizons, epic summaries, and plan indexes from records. Do not change underlying state to make a projection pass. Adopt an epic only with its own confirmed formulation or explicit proposal-storage authority. No feature epic or roadmap is required just to migrate.

Register adopted optional artifacts using the six-column schema in [the extension guide](GOVERNANCE_EXTENSIONS.md#adoption-and-ownership). Link to the canonical records instead of duplicating state. Define owner, inputs, update triggers, and retirement before introducing a new coordination surface. Preserve useful historical snapshots with an explicit date and scope.

## Checker and Test Migration

Adapt the destination checker and fixtures without losing legacy protections. Keep validation offline and standard-library-only. Preserve the public validate(root) error-list API. WIP warnings are a separate result, printed by the CLI without causing failure when there are no errors. Validation must never mutate records.

Test zero/one/multiple Now tasks, warning thresholds, complete/partial checkpoints, dates, verification resumption, replanning, typed prerequisite gates and cycles, proposed versus approved scope, revision mismatch, epic membership/closure/external prerequisites, separate counts, duplicate fields, indexes, and historical exemptions. Keep the original valid/invalid lifecycle cases except the superseded single-Now restriction.

Parse metadata outside backtick/tilde fences and HTML comments. Check local Markdown links and section anchors. Bound reads to regular governance sources; skip runtime/generated/private trees and symlinks. Never read a protected target to check a link. Check optional artifact registration and malformed records. Structural checks cannot authenticate user approval, prove semantic completeness, qualify application behavior, or replace human acceptance.

## Verification and Handoff

Run from the destination root:

```sh
python3 -B scripts/docs_check.py
python3 -B -m unittest discover -s tests -p 'test_docs_check.py'
```

Read back every changed document, review the scoped diff, and check one vocabulary, honest task states, preserved IDs/approval/acceptance, accurate projections, bounded epics, clear artifact ownership, and no copied stack/credential/permission assumptions. Rerun only when changes or failures justify it. Record actual results and limits, including pre-existing issues. Do not close migration while required checks are unavailable.

For a distributable template, keep application task/epic/idea registries and PROJECT_LOG.md empty. Use fenced examples and synthetic fixtures. Keep template-maintenance authority and verification in a separate maintenance record, not in the project bootstrap.

## Copyable Request

```text
I confirm the governance v2 contract and authorize its migration in this project.
Preserve our Git identity, stable IDs, existing approvals, historical evidence,
outstanding acceptance, domain rules, and unrelated worktree changes. Work only
in this destination; do not modify reference projects or read protected secrets.

Implement the lifecycle, checkpoints, scoped authority, typed prerequisites,
epics, projections, and validator/tests together. Adopt optional artifacts only
when needed and authorized. Do not approve or activate unrelated work, install
hooks, choose a stack, deploy, commit, or push as part of this migration.
Run offline checks and semantic readback, then report results and limitations.
```
