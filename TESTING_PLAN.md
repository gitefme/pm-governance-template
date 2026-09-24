# Testing Plan

## Current State

No application code, application test framework, or coverage target exists. Repository governance has a Python 3 standard-library documentation checker and unit tests. Application verification requirements should follow actual project risks rather than assumptions imported from another repository.

Canonical documentation commands:

- Repository check: `python3 -B scripts/docs_check.py`
- Checker tests: `python3 -B -m unittest discover -s tests -p 'test_docs_check.py'`
- All governance-tool tests, including bundled backlog skills: `python3 -B -m unittest discover -s tests -p 'test_*.py'`

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

- Retain all allowed task-stage/plan-state relationships, blocked variants, source ownership, Design Basis, and single-current-plan protections.
- Cover zero/one/multiple Now tasks and mixed Implementation/Verification. Excess WIP warns while the CLI succeeds; invalid configuration fails. Validation does not mutate files.
- Reject partial/blank checkpoints, impossible dates, unassigned Now executors, missing authority evidence, proposed active/approved work, revision mismatch, and improper Resume Stage. Preserve verification on resume, checkpoints on parking/closure, and unchanged historical records.
- Test typed prerequisite syntax, unknown IDs, duplicates, self/cross-type cycles, and each planning/implementation/acceptance gate. Ready plan approval does not waive implementation prerequisites.
- Test bounded epic membership, no nesting/task fields, coordination anchors, paused states, duplicate milestones, external prerequisites, premature closure, linked evidence, and separate counts.
- Reject wrong record sections, duplicate fields/metadata, malformed records, stale focus/horizons/counts/indexes, broken local links/anchors, missing optional artifact ownership, and metadata hidden in fenced examples/comments.
- Verify scoped reads avoid runtime/generated/private trees, env-shaped files, and symlinks. The optional secret-path guard checks Git filenames only and never opens credential files.
- Use synthetic fixture repositories and temporary directories. No network, runtime services, real credentials, browser, or paid providers are needed for governance tests.

## Review Evidence and Acceptance

Bundled skill changes also require frontmatter/instruction review and the all-tools suite. Verify exports exclude examples/comments, preserve current PM v2 records, escape source text, and leave governance files unchanged. Check installation in a temporary project and protect existing skills. Changes to HTML interaction require a real-browser check; clipboard delivery into another application is a separate acceptance claim. See [portable backlog skills](docs/BACKLOG_SKILLS.md).

Use the [portable operations guide](docs/OPERATIONS_GUIDE.md) and [handoff example](docs/examples/review-handoff.md) when applicable. Identify tested source including relevant dirty files, target/environment, timestamp, commands, results, and limits. Invalidate affected claims after source/target changes or a failed/interrupted verification run. Running-deployment parity is a separate observation within authorized scope; source tests cannot establish it.

Prepare disposable synthetic states before requesting manual review. Keep preparation status separate from user outcome, required acceptance linked to approved plans, and optional exploration optional. Preserve prior acceptance unless affected behavior or a justified regression concern changes. Documentation-only changes need no artificial browser exercise. Application-specific runners remain future work until the stack is selected.

## Completion Rule

A task moves to `Done` only after required automated checks pass, necessary manual validation is recorded, affected documentation is current, and residual risk is stated. When an application toolchain is selected, add its canonical commands and any justified coverage expectations here and in `README.md`.
