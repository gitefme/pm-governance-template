# Completed Tasks and Epics

Durable registry of formal tasks and epics that passed the closure criteria in `WORKFLOW.md`.

## Rules

- Preserve stable `T-###` IDs and the complete confirmed task record.
- Use a checked checkbox and `Status: Done`; remove the lifecycle stage.
- Preserve plan type and reference, set its status to `implemented`, and record completion date, verification, and residual risk.
- Keep entries grouped by year and ordered newest first.
- Completed tasks do not appear in active planning horizons and cannot be reactivated; create a new confirmed task for follow-up work.

## Completed Task Template

```md
- [x] T-000 Short task title
  - Status: Done
  - Priority:
  - Area:
  - Source:
  - Revision: 1
  - Formulation Status: confirmed
  - Formulation Evidence:
  - Plan Approval Evidence:
  - Activation Evidence: preserve the execution authority
  - Epic: preserve existing membership; otherwise omit
  - Plan Type: Lightweight | Detailed
  - Plan Status: implemented
  - Plan Reference: embedded in this task | [plan filename](plans/exact-plan-filename.md)
  - User Inputs:
  - Codex Additions:
  - Goal:
  - Acceptance:
  - Scope Exclusions:
  - Dependencies:
  - Planning Prerequisites: preserve if present
  - Implementation Prerequisites: preserve if present
  - Acceptance Prerequisites: preserve if present
  - Verification:
  - Checkpoint Updated: YYYY-MM-DD
  - Completed Work:
  - Remaining Work: None
  - Next Action: None
  - Open Issues: residual risk or None known
  - Executor:
  - Work Context: preserve if present
  - Notes: Completed YYYY-MM-DD. Residual risk: none known.
```

## Completed Tasks

No formal tasks have been completed in this project yet.

## Completed Epics

No formal epics have been completed in this project yet.

## Epic Closure Rules

Preserve the complete epic record under Completed Epics and a YYYY heading, with a checked checkbox, Progress: Done, and a local Markdown-linked Completion Evidence entry. Require at least one member, all members and milestone prerequisites Done, every milestone checked, and verified integrated acceptance. Remove Resume When on closure. Keep the executive coordination block and archived child membership. Epics do not increase completed task count; follow-up work gets a new identity.
