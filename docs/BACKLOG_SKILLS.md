# Portable Backlog Skills

The repository bundles two complete skill packages under `skills/`. These are reusable tools, not live project records. They contain no personal paths, credentials, paid providers, or runtime configuration. Python helpers require Python 3.10 or newer and use only the standard library.

| Skill | Use | Sources |
| --- | --- | --- |
| [bkl-sh](../skills/bkl-sh/SKILL.md) | Concise read-only backlog summary; requested completed-work or idea views | BACKLOG.md by default; other registries only as described in the skill |
| [backlog-html-review](../skills/backlog-html-review/SKILL.md) | Dated HTML tables with copy buttons and personal review markers | BACKLOG.md and optional open-epic coordination in plans/000_EXECUTIVE_PLAN.md |

## Use After Cloning

From the clone's root, install repository-local discovery copies:

```sh
python3 -B scripts/install_skills.py
```

The installer copies both complete folders into `.agents/skills/` in this project. It does not change global skills or agent configuration and refuses to replace an existing destination. If installation is blocked by your environment, use the direct instructions below; do not change permissions merely to install a skill. To install into another existing project, pass `--project-root /path/to/project`.

Codex discovers repository skills under `.agents/skills`. After installation, use `$bkl-sh` or `$backlog-html-review`, or select the skill through `/skills` in Codex CLI. If discovery has not refreshed, restart Codex. Skills with identical names in user and repository locations are not merged: select the repository copy or explicitly provide its SKILL.md path. This follows the [official skill discovery documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

The tracked `skills/` directories are the distributable sources; installed copies are snapshots. To update an existing installation, compare it with the bundled source and preserve local customizations before replacing it. This template ignores its two local installation folders so they do not become duplicate tracked sources. In another repository, follow that repository's policy for tracking local skills.

## Direct Use Without Installation

Ask the agent to use `skills/bkl-sh/SKILL.md` for a concise backlog overview, or `skills/backlog-html-review/SKILL.md` for an HTML export. These paths avoid ambiguity with older global copies.

The HTML generator also runs without Codex. From the project root:

```sh
python3 -B skills/backlog-html-review/scripts/generate_backlog_review_html.py --project-root .
```

It prints the generated path under `outputs/`. Open that HTML file in a browser. To choose a destination:

```sh
python3 -B skills/backlog-html-review/scripts/generate_backlog_review_html.py --project-root . --output outputs/my-backlog-review.html
```

Relative output paths use the target project root. Existing files are never overwritten. If the skill was installed elsewhere, resolve `scripts/generate_backlog_review_html.py` relative to that skill's own SKILL.md. Copying the entire skill folder is sufficient; the generator imports no template-specific code.

## Snapshot Boundaries

The exporter excludes fenced examples and comments, preserves multiple Now tasks, includes lightweight and detailed plans, and separates formulation status from plan approval evidence. It does not authenticate approval or replace the governance checker. Missing executive coordination is allowed and is not listed as a source.

Checkboxes are personal review markers; they never change repository status or establish acceptance. Storage is browser-local and best-effort. If storage is blocked, the page still works, but markers last only for that visit. New exports have separate marker state.

Copy buttons offer HTML and plain-text tables. Browser permissions and destination applications affect clipboard/paste behavior; a failed automatic copy leaves the table selected for manual copying. No external fonts, scripts, services, or network requests are required by the HTML page.

Generated HTML contains the selected backlog's text. Keep exports local unless sharing them is intended. Snapshots are disposable outputs, not live roadmap or handoff records; they do not need optional-artifact registration. The template ignores its default generated snapshot filenames.

## Validation

Run all governance and bundled-tool regression tests:

```sh
python3 -B -m unittest discover -s tests -p 'test_*.py'
```

The tests exercise source parsing, PM v2 records, non-destructive export, and installation into temporary projects. Browser and destination-application checks are separate from this standard-library suite.
