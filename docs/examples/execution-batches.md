# Execution Batch Example

Reference only; adopt using [the registration procedure](../GOVERNANCE_EXTENSIONS.md#adoption-and-ownership).

```md
# Temporary Execution Order

- Basis: user-requested package and dated source snapshot
- Activation Evidence: None; this table proposes ordering only
- Skip Policy: Stop at a blocked row unless the user authorized an independent eligible row
- Refresh When: Source task, prerequisite, approval, or priority changes
- Retire When: The authorized package is complete or the table is replaced

| Order | Existing task/current plan | Planning/implementation/acceptance prerequisites | Executor and work context | Optional model/effort suggestion |
| --- | --- | --- | --- | --- |
| 1 | Exact current link | Read typed prerequisites from the task | Contributor, branch/worktree, owned files | Project-specific recommendation or Unspecified |

Task records own authority and state. Before each row check current plan revision,
confirmation, prerequisites, activation scope, and file ownership. Keep a checkpoint
before switching work. Group compatible work only after respecting dependencies.
Model choices require current availability checks when actually used. This table
does not change a selector, launch agents, approve plans, or authorize parallel writes.
```
