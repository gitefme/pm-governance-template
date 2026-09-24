# Architecture

## Current State

No application code, runtime, language, framework, persistence layer, data provider, or deployment target has been selected. The repository contains governance documents and standard-library validation tools; these do not select an application stack.

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

## Authority and Evidence

Confirmed target rules describe intended behavior, not proof that it exists. Keep implementation status, dated verification, and outstanding acceptance in task records and linked evidence. Under explicit write-first authorization, isolate proposed sections with Formulation Status: proposed, Storage Authorization, and visible open decisions. They do not override confirmed rules. Remove the proposed marker only after confirmation; record the decision and affected revision. A plan's approval does not silently approve unrelated changes to this document.
