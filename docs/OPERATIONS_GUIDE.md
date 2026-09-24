# Portable Verification and Operations

This template selects no application runtime, provider, browser, database, deployment, or permission profile. Adopt project-specific adapters only when their design and commands exist. [WORKFLOW.md](../WORKFLOW.md#review-handoff-and-closure) owns review and acceptance rules.

## Repeatable Verification

Define one canonical command per adopted operation. Use deterministic synthetic data, fake providers, isolated temporary resources, and a clean child environment that forwards only required settings. Do not inherit paid/live opt-ins, arbitrary test plugins, or broad interpreter paths into offline tests. Record missing tools and failed checks as failures or unavailable evidence, never as success.

Use real browser checks for interaction, keyboard, responsive behavior, and announcements. Isolated UI examples do not verify production locking, queues, worker recovery, provider quality, or billing. Live checks require their own approved target, bounded cost, credential handling, and cleanup. No runtime commands are installed by this guide.

## Evidence and Running Targets

Record public source identity before and after a verification run, including relevant uncommitted files, as well as target/environment, timestamp, command, result, and limitations. Interrupted/failed runs and source changes invalidate the passing claim for the affected scope. If the handoff concerns a running deployment, separately compare applicable deployed source, migrations, and served assets within authorized read access. A source check alone is not a running-target check. Hashes identify evidence; they do not prove functional correctness or permission to read protected files.

Prepare disposable examples with synthetic accounts, isolated storage/queues/session state, fake providers, explicit access instructions, and bounded cleanup. Check the instance's source and availability immediately before review. Stop/remove only identified generated resources; stale PIDs or paths are insufficient authority to kill processes or delete data. Use the [handoff example](examples/review-handoff.md).

## Credentials and Permissions

Inspect permitted redacted examples for setting names. Never bypass denied credential reads, print environment dumps, expanded runtime configuration, raw request headers, or unrestricted logs. Prefer narrowly scoped diagnostics that report presence, readiness, and sanitized errors. An ignore file is a search convention, not a security boundary.

Permission rules, absolute paths, sockets, and saved approvals belong to the destination environment. Do not copy another project's profiles or weaken a sandbox to fix a test. Separate file edits from commands requiring permission; authorize only the necessary operation. Hooks and tooling that internally read secrets must respect the same restrictions as other tools.

## Optional Secret-Path Guard

The standard-library script checks Git filenames only:

```sh
python3 -B scripts/check_secret_paths.py
python3 -B scripts/check_secret_paths.py --tracked
```

The default examines staged additions/modifications/renames; --tracked examines all indexed paths. It rejects env files and common credential/key paths, while allowing redacted `.env*.example` names and `.secrets/.gitkeep`. It does not open those files, detect secrets embedded in source, establish example redaction, or scan Git history. A future content scanner is a separate optional dependency that needs scoped installation/configuration and must honor protected-file restrictions.

No hooks are installed automatically. After inspecting the destination's actual hooks configuration and preserving existing hooks, an authorized maintainer may call the default command from pre-commit and the --tracked command from pre-push. These checks run from the repository root; adapt interpreter invocation to the project's documented environment. The guard is supplemental and can be bypassed by Git users; it is not a security boundary or proof that outgoing history is secret-free.
