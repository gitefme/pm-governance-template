# PM Governance Template

Reusable project-management and governance system for a new project. Governance version 2 supports epics, multiple started tasks, restartable checkpoints, explicit authority, and typed prerequisites. It contains no project-specific scope or product decisions, no task history or completed plans, and no selected implementation stack.

## Start Here

- Before creating formal work, record the new project's confirmed product direction and open decisions in `DESIGN_BRIEF.md`.
- Record confirmed cross-product interaction, UI-state, responsive, and accessibility conventions in `PRODUCT_DESIGN.md` as they are established.
- Record confirmed system boundaries and major technical decisions in `ARCHITECTURE.md` as they are made.
- Read `BACKLOG.md` for unfinished formal work.
- Read `plans/000_EXECUTIVE_PLAN.md` before opening detailed plans.
- Read `WORKFLOW.md` for the task lifecycle and approval gates.
- Read `AGENTS.md` for repository-wide contributor and execution instructions.

## Repository Map

- `ARCHITECTURE.md`: system boundaries and technical decisions.
- `PRODUCT_DESIGN.md`: cross-product UX and interaction conventions.
- `BACKLOG_DONE.md`: completed formal tasks and epics.
- `IDEA_INBOX.md` / `IDEA_ARCHIVE.md`: informal idea intake and history.
- `PROJECT_LOG.md`: decisions, outcomes, checks, and residual risks.
- `TESTING_PLAN.md`: verification strategy.
- `plans/`: detailed plans tied to formal tasks.

Document application source, tests, assets, generated output, and canonical development commands only after the new project's product shape and toolchain are confirmed.

## Commands

No application development, build, lint, or test commands are configured.

- Documentation check: `python3 -B scripts/docs_check.py`
- Documentation-checker tests: `python3 -B -m unittest discover -s tests -p 'test_docs_check.py'`

These commands use only the Python 3 standard library and do not select an application stack. Add application commands only after their tools and configuration exist in this repository.

## Portable Guides and Optional Integrations

- [Migration guide](docs/PM_V2_MIGRATION_GUIDE.md): update an existing project while preserving its history, approvals, and acceptance.
- [Optional governance artifacts](docs/GOVERNANCE_EXTENSIONS.md): roadmap, decision register, traceability, execution batches, and review handoff examples. No optional live artifacts are adopted initially.
- [Verification and operations](docs/OPERATIONS_GUIDE.md): source/target evidence, prepared synthetic examples, safe diagnostics, and optional hook integration.
- Optional staged filename guard: `python3 -B scripts/check_secret_paths.py`; all indexed names: `python3 -B scripts/check_secret_paths.py --tracked`. It never reads file contents; no hooks or external scanners are installed.
- [Template maintenance](docs/TEMPLATE_MAINTENANCE.md): this template's own change authority and validation, separate from a new project's empty registries.

When adopting, preserve the destination's Git history/remotes and existing files. Copy only the portable material needed; do not bring another project's permissions, credentials, task history, or runtime choices. The maintenance record is template history, not a product requirement; omit it when initializing a new project and remove its entry point and template-maintenance reference from WORKFLOW.md. Keep examples as references until explicitly adopted and registered in WORKFLOW.md.

## Validation Scope

The checker reads regular Markdown files at the root and under docs/ and plans/. It skips private/generated/runtime trees, env-shaped names, and symlinks. It validates record schemas, gates, references, local inline links/heading anchors, optional artifact registration, and projections. It does not authenticate approvals, test application behavior, or establish user acceptance. Fixture repositories are validated independently by the unit suite.

## Security

Do not store secrets, private datasets, customer exports, or `.env` files in version control. Document configuration using redacted examples.
