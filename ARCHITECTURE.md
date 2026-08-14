# Architecture

## Current State

No application code, runtime, language, framework, persistence layer, data provider, or deployment target has been selected. The repository currently contains documentation only.

## Decision Boundaries

Architecture decisions should begin with responsibilities and data movement before selecting tools. Describe these boundaries when they become relevant:

- data ingestion and source ownership;
- validation, transformation, and metric calculation;
- application/domain behavior;
- presentation and interaction;
- persistence, caching, and retention;
- authentication, authorization, privacy, and auditability;
- external integrations, deployment, and observability.

Keep authoritative evidence separate from summaries, derived metrics, and inferred content. Define ownership and failure behavior at each boundary. Credentials and sensitive data must not cross into browser-visible state, logs, or generated artifacts without an explicitly approved requirement.

## Architecture Change Rule

Document a proposed material architecture decision and its tradeoffs before implementation. After approval, update this file with the selected boundary, rationale, consequences, and migration implications. Routine implementation details inside an approved boundary do not need separate approval.
