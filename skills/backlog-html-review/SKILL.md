---
name: backlog-html-review
description: Generate a dated, interactive HTML review of a project's current unfinished backlog, open epics, and current plan states. Use when the user asks to review or export a backlog for tracking outside the repository.
---

# Backlog HTML Review

Create a read-only review snapshot from the project's current governance records. The output is an HTML file with actual tables, copy buttons, and local checkboxes that gray out completed rows for personal tracking.

## Sources and boundaries

- Read `BACKLOG.md` as the authority for unfinished tasks and open epics.
- Read `plans/000_EXECUTIVE_PLAN.md`, when present, only for coordination of currently open epics. Omit it from the source list when absent.
- Do not infer a task's completion from a plan file, nor alter task, plan, or epic records while preparing the review.
- Do not read secrets, environment files, generated user data, or completed-task history unless the user specifically asks for it.
- State the generation date, time, and source files in the output. Treat the page as a dated snapshot, not a replacement backlog.

## Generate

Resolve the bundled [generator](scripts/generate_backlog_review_html.py) relative to this SKILL.md, wherever this skill was installed. Pass the target project root explicitly. For the copy distributed in this repository, run from the project root:

```sh
python3 -B skills/backlog-html-review/scripts/generate_backlog_review_html.py --project-root .
```

Use Python 3.10 or newer; the generator needs only the standard library, no services or network. Use `--output <path.html>` if the user specifies a destination; relative destinations use the project root. Otherwise the script writes a uniquely timestamped HTML file under `outputs/`. Existing files are never overwritten.

Ignore fenced examples and comments. Preserve multiple Now tasks, lightweight and detailed plan states, formulation status, and approval evidence as separate facts. Report parsing errors rather than silently picking conflicting records. This snapshot does not authenticate approval evidence or replace the governance checker.

Review the generated file for these minimum contents before reporting it: a timestamp, an open-epics table, an unfinished-tasks table, a plan-state table, and interactive checkboxes on populated record rows. Empty tables should explicitly state that no records exist. Report that checkboxes are local personal review markers and do not change repository status.

## Presenting the result

Give the user a clickable link to the HTML file. The **Copy table** button offers HTML and plain-text clipboard formats for table-aware applications, including desktop OneNote. If clipboard access is blocked, select and copy manually. Do not claim a destination application's paste behavior was tested unless it was.

Checkboxes mark personal review only, not task completion or acceptance. Persistence is browser-local and best-effort; blocked browser storage keeps markers in memory for the current page. They are not shared across browsers or machines. Generated snapshots are disposable exports, not live governance artifacts needing registration. Do not add them to version control unless requested.
