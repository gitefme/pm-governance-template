# Review Handoff Example

Reference only; adopt using [the registration procedure](../GOVERNANCE_EXTENSIONS.md#adoption-and-ownership).

```md
# Current Review

- Source: commit plus relevant dirty-file identity, or a scoped public-source digest
- Target: exact environment and running build/artifact
- Checked At: timestamp with timezone
- Technical Evidence: commands, results, artifacts, and limitations
- Source/Target Match: Verified, Mismatch, or Not checked, with evidence

| Task and approved plan | Requirement | Page/artifact, action, expected result | Preparation | User result |
| --- | --- | --- | --- | --- |
| Existing task/current plan link | Required with plan basis, or Optional | Exact reproducible instructions | Ready, Not prepared, or Stopped | Not run, Accepted, Changes requested, or Not applicable |

## Prepared Examples

- Isolation: disposable synthetic data and fake providers, separate from working data.
- Access: direct links and synthetic login instructions; no real secrets in this document.
- Expected states: only those needed by the scheduled review.
- Lifetime: agreed review window; recheck availability before handing over.
- Cleanup: identify and remove only this example's own generated resources.
- Limits: which live-provider, database, worker, or production claims it cannot prove.

Record dated user feedback against its owning task and revision. A ready example
or passing automated check is not user acceptance. Source/target changes invalidate
affected evidence; preserve earlier acceptance unless behavior or a justified
regression concern changed. Required acceptance comes from the plan; optional tours
add no gate. Documentation-only work requires no invented application tour.
```
