# Template Maintenance

This record describes maintenance of the distributable governance template. It is not a task, epic, approval, or product decision for projects initialized from it. Project bootstrap registries and PROJECT_LOG.md remain empty.

## 2026-09-24 — Governance v2 Update

- Authority: The user confirmed the complete twelve-item update proposal and all seven review corrections, then requested updating this project. They explicitly required leaving the reference project untouched and working only on this template.
- Scope: Portable lifecycle, WIP, checkpoints, epics/milestones, write-first review, revision/approval evidence, typed prerequisites, optional coordination examples, prepared handoffs, verification/operations guidance, migration, and checker/test hardening.
- Implementation sequence: Align the core contract and empty schemas; implement checker rules and synthetic regression cases; add optional guides/examples and a filename-only guard; run checks, full readback, and semantic consistency review.
- Boundaries: Preserve empty bootstrap registries and Git identity. Adopt no application stack, feature history, permissions, hooks, deployment, providers, or credentials. No reference-project edits.
- Design basis: Documentation and governance tooling only; no application UI or product scope is selected. Optional examples describe future adoption, not present runtime capabilities.
- Verification: `python3 -B scripts/docs_check.py` passed. `python3 -B -m unittest discover -s tests -p 'test_docs_check.py'` passed all 30 test methods, including the 12 valid and 36 invalid fixture cases plus new scenario subtests. The filename-only tracked-path guard and `git diff --check` passed.
- Portability check: Copied the template into a temporary directory without Git, omitted template-maintenance history using the documented initialization steps, and passed the checker and full test suite there. Live task/epic counts are zero and no detailed project plans exist.
- Semantic review: Read back the affected documents and reviewed source ownership, gates, resumption/replanning, prerequisites, approval evidence, projections, optional artifact boundaries, protected reads, and template neutrality. Required application/runtime evidence is not claimed: no application stack is selected.
- Result: The confirmed portable update is implemented in the template. The reference project was not modified. Optional runtime adapters, external content scanners, hooks, and live project artifacts require later project-specific adoption.
- Recovery: Review/revert this branch's scoped template changes without changing a destination project's history or application state. No persistent application data is involved.

## Approved Package Coverage

| Proposal items | Implemented location |
| --- | --- |
| 1–3: multiple Now tasks, advisory WIP, checkpoints | [Lifecycle and checkpoints](../WORKFLOW.md#lifecycle-and-resumption), backlog schema, checker/tests |
| 4: epics, milestones, evidence, separate counts | [Epics and milestones](../WORKFLOW.md#epics-and-milestones), both registries, executive plan, checker/tests |
| 5: scoped write-first review and preserved revisions | [Approval records](../WORKFLOW.md#approval-and-revision-records), plan guidance, checker/tests |
| 6: batches and ownership | [Batch example](examples/execution-batches.md), workflow activation/checkpoint rules |
| 7–8: roadmap, traceability, decisions | [Optional artifact guide](GOVERNANCE_EXTENSIONS.md), three reusable examples and registration validation |
| 9–10: prepared handoffs and source/target evidence | [Operations guide](OPERATIONS_GUIDE.md), handoff example, workflow/testing rules |
| 11: scoped diagnostics/tests and optional secret hooks | Operations guide and filename-only guard with regression checks; no automatic hook installation |
| 12: versioned migration and validation | [Migration guide](PM_V2_MIGRATION_GUIDE.md), checker and synthetic fixtures/tests |

The review corrections are covered by explicit resume/replan transitions, typed prerequisite gates/cycles, scoped revision authority, optional artifact ownership, anchor/fence validation, portable protected-read behavior, and live Git-state inspection guidance. Historical fixture exceptions preserve closed work; structural validation cannot authenticate the underlying approval or acceptance evidence.
