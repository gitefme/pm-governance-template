# Repository Guidelines

These instructions apply to the whole repository.

## Project Sources of Truth

- `DESIGN_BRIEF.md`: confirmed product outcomes, principles, and user workflows.
- `PRODUCT_DESIGN.md`: confirmed cross-product information architecture, interaction patterns, UI states, responsive behavior, and accessibility conventions.
- `ARCHITECTURE.md`: confirmed system boundaries, data ownership, and major technical decisions.
- `BACKLOG.md`: unfinished formal tasks, open epics, checkpoints, and WIP guidance.
- `BACKLOG_DONE.md`: completed formal tasks and epics with stable IDs and separate counts.
- `IDEA_INBOX.md` and `IDEA_ARCHIVE.md`: non-formal ideas and their outcomes.
- `plans/`: detailed task plans; start with `plans/000_EXECUTIVE_PLAN.md`.
- `PROJECT_LOG.md`: concise decisions, implementation outcomes, verification, and residual risks.
- `TESTING_PLAN.md`: risk-based verification expectations.
- `WORKFLOW.md`: collaboration lifecycle, authority, and approval gates.
- `README.md`: setup, commands, repository map, and known limitations.

Read only the documents relevant to the current request. Do not bulk-load historical plans or completed tasks.

## Planning and Execution

- Follow governance version 2 in `WORKFLOW.md`; it owns the lifecycle and schemas.
- Keep stable T-### tasks and E-### epics. Several started tasks may be in Now. The configurable WIP advisory limit starts at 3; excess warns without changing truthful task state.
- Keep complete checkpoints on Now tasks: Checkpoint Updated, Completed Work, Remaining Work, Next Action, Open Issues, Executor. Update on meaningful progress and handoff; preserve them when parking/closing. Record Work Context when contributors overlap; agree ownership and integration order. Parallel tracking does not authorize automatic delegation.
- Use Status and Stage as defined in WORKFLOW.md. Implementation and Verification exist only in Now. Interruptions retain their current stage. Resume verification as Verification. Intentional parking requires `Resume When`; blocking requires `Blocked By`. Preserve Resume Stage for parked, previously active confirmed work. Replanning follows the current plan state, never an automatic promotion to Ready.
- Each unfinished task has Revision and Formulation Status with evidence or explicit write-first Storage Authorization. Confirmed plans require Plan Approval Evidence; Now requires Activation Evidence and an assigned executor. Keep formulation review, plan approval, and user acceptance distinct.
- Simple work uses a confirmed embedded lightweight plan; complex work uses a confirmed detailed plan before Ready/Now. Use exactly `draft`, `pending`, `confirmed`, `implemented`, and `superseded`. Keep filename, metadata, task revision, plan reference, and index aligned. Reject duplicate fields and multiple current detailed plans.
- Pending/confirmed detailed plans require a non-empty Design Basis. Material unresolved implementation choices keep the plan draft; a design-study plan may make those decisions its deliverable.
- Classify task dependencies as Planning Prerequisites, Implementation Prerequisites, or Acceptance Prerequisites. Validate existing IDs, acyclic completion dependencies, and the applicable gate before starting or closing work.
- Epic membership lives only in each task's optional Epic field. Epics have milestones and integrated completion criteria, never task stages or executable plans. Epic approval cannot approve or activate child plans. Close with linked evidence only after all members/prerequisites and milestones are complete.
- Keep records, sections, current focus, counts, horizons, and executive summaries consistent. Register adopted optional artifacts and their owners/update triggers in WORKFLOW.md. Keep examples fenced and project registries empty when maintaining this distributable template.
- Pause for meaningful unapproved changes to product scope, architecture, persistent data, security/privacy, dependencies/providers, cost, or destructive behavior. Resolve routine details within existing authorization.

### Durable Formulation Confirmation

Present material new or rewritten project wording for explicit formulation confirmation before storage. Ordinary save/capture requests permit a conversational proposal. Exact user wording, factual observations, verification results, and mechanical updates following confirmed decisions are exempt from a second review.

Explicit write-first authorization permits the named proposal package to be stored as proposed; complete plans are pending and unresolved plans draft. Record the authorization. It does not imply final wording confirmation, plan approval, or activation. Preserve superseded revisions and historical acceptance; changed plans do not inherit approval. Do not ask again to perform an already authorized write.

Keep formulation confirmation, plan approval, and activation separate. A user can explicitly satisfy multiple gates in one instruction; record each without extra permission rounds. Activation applies to identified confirmed work and preserves its actual remaining phase.

### User-Input Grounding

Preserve supplied outcomes, constraints, terminology, exclusions, and decisions. Label material assumptions and recommendations as Codex Additions; never invent User Inputs. Distinguish confirmed targets, marked proposals, implemented behavior, verified results, and remaining acceptance.

## Project Structure and Coding Style

No application structure or toolchain is selected yet. When established, document source, test, asset, and generated-output locations in `README.md` and `ARCHITECTURE.md`. Keep related product surfaces, data adapters, calculations, and tests together. Follow the adopted formatter and linter. Prefer clear domain names; use `PascalCase` for components, `camelCase` for utilities, and lowercase kebab-case for feature folders when those conventions fit the selected language.

## Build, Test, and Development Commands

No application build, run, lint, or test commands exist yet. Do not copy commands from the reference project. Run `python3 -B scripts/docs_check.py` for repository-documentation validation and `python3 -B -m unittest discover -s tests -p 'test_docs_check.py'` for checker tests. When an application toolchain is adopted, establish one canonical command per operation and document it in `README.md` and `TESTING_PLAN.md`.

## Testing Guidelines

Use risk-based verification from `TESTING_PLAN.md`. Add meaningful tests for behavior changes. Documentation-only changes require the documentation checker, checker tests when behavior changes, full readback, and semantic consistency review.

Prepare applicable review handoffs: task/plan, source/target/date, exact actions and expected results, required/optional basis, preparation state, and separate user result. Use synthetic examples for unusual states; preserve earlier accepted evidence unless affected behavior changed. Real browser behavior requires real browser verification. Missing or stale evidence is not a pass. See `docs/OPERATIONS_GUIDE.md`; adopt runtime commands only once an application stack exists.

## Commit and Pull Request Guidelines

Inspect the actual Git root, branch, remote, and dirty state before repository operations. Preserve the destination history, remote identity, and unrelated changes when adopting this template. Use focused commits with concise imperative subjects. Pull requests should explain the outcome, validation performed, linked task or issue, residual risk, and include screenshots for visual changes.

## Security and Configuration

Never commit credentials, `.env` files, private exports, customer data, or generated sensitive content. Use permitted redacted public examples for setting names. Respect denied reads; never inspect secrets through another process to bypass a restriction. Avoid environment dumps, raw runtime configuration, request headers, and unrestricted logs. Use sanitized project-specific diagnostics once implemented.

Use synthetic data and fake providers by default. Live checks need explicit targets, bounded cost, credentials handled internally where permitted, and cleanup. Keep test commands narrowly scoped and environments isolated. Do not import another project's permission profile, absolute-path rules, hooks, or runtime commands. Optional path-only secret checks and hook integration are documented in `docs/OPERATIONS_GUIDE.md`; they do not inspect secret contents or claim content scanning.
