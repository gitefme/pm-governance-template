# Testing Plan

## Current State

No application code, application test framework, or coverage target exists. Repository governance has a Python 3 standard-library documentation checker and unit tests. Application verification requirements should follow actual project risks rather than assumptions imported from another repository.

Canonical documentation commands:

- Repository check: `python3 -B scripts/docs_check.py`
- Checker tests: `python3 -B -m unittest discover -s tests -p 'test_docs_check.py'`

## Test Selection

| Change type | Required verification |
| --- | --- |
| Documentation only | Run the documentation checker; read back changed files; check links, terminology, templates, and source-of-truth ownership |
| Documentation-checker behavior | Run the repository check and all checker unit tests, including relevant positive and negative fixtures |
| Pure calculation or transformation | Focused unit tests, boundary cases, and the project-wide static check |
| Data source, persistence, or API | Unit tests plus integration tests covering failures, timeouts, malformed data, and privacy boundaries |
| User workflow or visual behavior | Focused browser test plus keyboard, responsive-layout, loading, empty, and error-state checks |
| Shared infrastructure or security | Full relevant suite, regression checks, and explicit residual-risk review |

## Product-Specific Expectations

- Test metric definitions, units, aggregation windows, rounding, missing values, and timezone behavior.
- Test stale, partial, empty, loading, and failed data states.
- Keep fixtures small, deterministic, and free of real private data.
- Mock external providers by default; live tests require explicit approval and safe credentials.
- Do not claim responsive, accessibility, or interaction behavior from source inspection alone.

## Governance-Checker Expectations

- Cover every allowed task-stage and current-plan-status relationship.
- Reject wrong backlog sections, duplicate fields or plan metadata, stale counts/focus/horizons, multiple current detailed plans, and current references to implemented or superseded plans.
- Verify blocked work both before planning and with retained draft, pending, or confirmed plans.

## Completion Rule

A task moves to `Done` only after required automated checks pass, necessary manual validation is recorded, affected documentation is current, and residual risk is stated. When an application toolchain is selected, add its canonical commands and any justified coverage expectations here and in `README.md`.
