# Optional Governance Artifacts

These references help projects adopt only the coordination they need. They are not live project records, approvals, or additional task gates. The canonical contract is [WORKFLOW.md](../WORKFLOW.md).

## Adoption and Ownership

After confirmation or scoped write-first authorization, create the needed live document from an example and register it under WORKFLOW.md → Optional Artifacts. Replace the canonical empty state with the following table, using the actual local Path and owner. Register each document once; its inputs remain authoritative.

```md
| Artifact | Path | Owner | Inputs | Update When | Retire When |
| --- | --- | --- | --- | --- | --- |
| Roadmap | [Roadmap](ROADMAP.md) | Product owner | Confirmed outcomes, tasks, epic milestones | An outcome or transition gate changes | Replaced by an explicitly adopted roadmap |
```

Use the table's Owner, Inputs, Update When, and Retire When as the artifact's maintenance contract. Add a README entry point. Register narrower design-source ownership in PRODUCT_DESIGN.md when relevant. Other filenames are allowed when explicitly registered; the conventional names below and files in plans/temporary/ are checked for missing registration automatically.

Retirement removes the live registration, updates incoming links and entry points, and preserves dated evidence where needed. Historical artifacts must say which snapshot they describe. Do not present a retired snapshot as current state. The checker verifies path/registration integrity, not the truth or freshness of narrative.

## Available Examples

| Capability | Example | Suggested live path | Authority |
| --- | --- | --- | --- |
| Outcome roadmap | [Roadmap](examples/roadmap.md) | ROADMAP.md | Outcome sequence and transition gates; backlog owns status |
| Decision register | [Decisions](examples/decisions.md) | docs/DECISIONS.md | Open choices and dated decisions; update owning durable rule after confirmation |
| Requirement traceability | [Traceability](examples/traceability.md) | docs/TRACEABILITY.md | Coverage projection; original inputs, plans, and verification retain ownership |
| Execution batches | [Batches](examples/execution-batches.md) | plans/temporary/execution-batches.md | Proposed ordering only; task approval and activation remain independent |
| Review handoff | [Handoff](examples/review-handoff.md) | docs/REVIEW_HANDOFF.md | Technical preparation and user-result projection; approved plan owns acceptance |

No optional live artifacts are adopted in the distributable template. Every example is fenced and uses synthetic placeholders. Replace placeholders and validate the adopted files; example status labels do not establish real authorization.
