# Repository Guidelines

These instructions apply to the whole repository.

## Project Sources of Truth

- `DESIGN_BRIEF.md`: confirmed product outcomes, principles, and user workflows.
- `PRODUCT_DESIGN.md`: confirmed cross-product information architecture, interaction patterns, UI states, responsive behavior, and accessibility conventions.
- `ARCHITECTURE.md`: confirmed system boundaries, data ownership, and major technical decisions.
- `BACKLOG.md`: unfinished formal tasks and the single active task.
- `BACKLOG_DONE.md`: completed formal tasks with stable IDs.
- `IDEA_INBOX.md` and `IDEA_ARCHIVE.md`: non-formal ideas and their outcomes.
- `plans/`: detailed task plans; start with `plans/000_EXECUTIVE_PLAN.md`.
- `PROJECT_LOG.md`: concise decisions, implementation outcomes, verification, and residual risks.
- `TESTING_PLAN.md`: risk-based verification expectations.
- `WORKFLOW.md`: collaboration lifecycle, authority, and approval gates.
- `README.md`: setup, commands, repository map, and known limitations.

Read only the documents relevant to the current request. Do not bulk-load historical plans or completed tasks.

## Planning and Execution

- Keep stable `T-###` task IDs and at most one task in `Now`.
- Use `Status` for where work sits and `Stage` for what it needs next; use the values in `WORKFLOW.md`.
- Place every unfinished task under the backlog section matching its `Status`; keep completed count, current focus, and planning horizons as checked projections of task records.
- `Implementation` and `Verification` exist only in `Now`; `Now` uses only those stages.
- Intentionally parked work uses `Status: Parked`, retains an eligible non-active stage, and records `Resume When`. Work unable to proceed uses `Parked + Blocked` and records `Blocked By`.
- Simple work requires a confirmed lightweight plan embedded in its backlog record before entering `Now`. Complex work requires a confirmed linked detailed plan.
- Use only `draft`, `pending`, `confirmed`, `implemented`, and `superseded` as plan statuses.
- Keep the current plan aligned with the stage: none at `Discussion`, `draft` at `Plan drafting`, `pending` at `Plan review`, `confirmed` at `Ready` or active work, and `implemented` only at `Done`. Blocked work may retain no plan or a `draft`, `pending`, or `confirmed` plan.
- A task may have at most one non-superseded detailed plan. Reject duplicate task fields or plan metadata rather than choosing one value.
- Every `pending` or `confirmed` detailed plan includes a non-empty `Design Basis`. When design applies, cover applicable durable sources, task-specific confirmed decisions, open decisions, expected UI states, and accessibility and responsive implications; otherwise state that no product-design effect exists.
- Keep formulation confirmation, plan approval, and activation separate. An explicit request to implement or resume confirmed work is activation and moves it to `Now + Implementation`.
- Pause for meaningful changes to product scope, architecture, persistent data, security/privacy, external dependencies/providers, material cost, or destructive behavior.

### Durable Formulation Confirmation

Before storing new or materially rewritten Codex-authored project wording, present the material formulation to the user and receive explicit confirmation. This includes task scope, acceptance criteria, plans, design rules, workflow rules, assessments, and recorded decisions. A request to save or capture authorizes a proposal for review, not a file write. Exact user wording, factual observations, verification results, and mechanical updates following a confirmed decision are exempt.

Formulation confirmation authorizes storage only. Plan approval is separate and changes a complete plan from `pending` to `confirmed` without starting work. Activation is the later instruction that starts or resumes confirmed work in `Now`.

### User-Input Grounding

Use supplied user inputs as the basis of task and plan proposals. Preserve the requested outcome, constraints, terminology, exclusions, and decisions. Label material assumptions or recommendations separately as `Codex Additions`; never invent `User Inputs`.

## Project Structure and Coding Style

No application structure or toolchain is selected yet. When established, document source, test, asset, and generated-output locations in `README.md` and `ARCHITECTURE.md`. Keep related product surfaces, data adapters, calculations, and tests together. Follow the adopted formatter and linter. Prefer clear domain names; use `PascalCase` for components, `camelCase` for utilities, and lowercase kebab-case for feature folders when those conventions fit the selected language.

## Build, Test, and Development Commands

No application build, run, lint, or test commands exist yet. Do not copy commands from the reference project. Run `python3 -B scripts/docs_check.py` for repository-documentation validation and `python3 -B -m unittest discover -s tests -p 'test_docs_check.py'` for checker tests. When an application toolchain is adopted, establish one canonical command per operation and document it in `README.md` and `TESTING_PLAN.md`.

## Testing Guidelines

Use risk-based verification from `TESTING_PLAN.md`. Add tests with behavior changes, especially for data transformations, loading/error states, user-visible calculations, accessibility, and responsive behavior. Documentation-only changes require the documentation checker, its tests when checker behavior changes, complete readback, and a cross-document consistency check.

## Commit and Pull Request Guidelines

This directory is not currently a Git repository. If version control is initialized, use focused commits with concise imperative subjects, such as `Add revenue summary card`. Pull requests should explain the outcome, validation performed, linked task or issue, residual risk, and include screenshots for visual changes.

## Security and Configuration

Never commit credentials, `.env` files, private exports, customer data, or generated sensitive content. Provide a redacted example file when configuration is introduced. Keep secrets outside browser-visible state and logs unless an approved architecture explicitly requires otherwise.
