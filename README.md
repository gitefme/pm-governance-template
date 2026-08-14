# PM Governance Template

Reusable project-management and governance system for a new project. It contains no project scope, task history, completed plans, product decisions, or selected implementation stack.

## Start Here

- Before creating formal work, record the new project's confirmed product direction and open decisions in `DESIGN_BRIEF.md`.
- Record confirmed system boundaries and major technical decisions in `ARCHITECTURE.md` as they are made.
- Read `BACKLOG.md` for unfinished formal work.
- Read `plans/000_EXECUTIVE_PLAN.md` before opening detailed plans.
- Read `WORKFLOW.md` for the task lifecycle and approval gates.
- Read `AGENTS.md` for repository-wide contributor and execution instructions.

## Repository Map

- `ARCHITECTURE.md`: system boundaries and technical decisions.
- `BACKLOG_DONE.md`: completed formal tasks.
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

## Security

Do not store secrets, private datasets, customer exports, or `.env` files in version control. Document configuration using redacted examples.
