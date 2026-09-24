---
name: bkl-sh
description: Give a concise, read-only overview of the current project's formal Markdown backlog and, when requested, completed work or idea intake. Use when the user asks for a backlog summary, pending or completed tasks, task overview, priorities, what is queued, what should be next, or captured ideas, and a BACKLOG.md file may exist.
---

# Backlog Short View

Provide an operational summary of the nearest available formal backlog records. Do not modify any file.

## Locate The Backlog

1. Check the current working directory for `BACKLOG.md`.
2. If absent, walk upward through parent directories until finding `BACKLOG.md` or reaching the repository root or filesystem root.
3. Do not search child directories, the home directory, or other projects.
4. If no backlog is found, state that clearly and stop. Do not infer tasks from plans, source code, issues, or commit history.

Treat sibling files by role when they exist:

- `BACKLOG.md`: unfinished formal work and the default source.
- `BACKLOG_DONE.md`: completed formal work; use for completed-task requests or to verify a missing/unclear completed count.
- `IDEA_INBOX.md`: non-formal ideas; read only when the user explicitly asks about ideas.
- `IDEA_ARCHIVE.md`: resolved idea history; read only when explicitly requested.

Read only `BACKLOG.md` by default. Use its declared `Completed task count` without loading the completed registry when the pointer is clear. Do not read plan files, project logs, source files, `.env`, or private session data unless the user separately asks for them.

## Interpret Safely

- Prefer explicit task fields such as `Status`, `Stage`, `Priority`, `Area`, `Blocked By`, and `Notes` when present.
- Support simple Markdown backlogs that use headings and checkbox items even when stable IDs or metadata are absent.
- Distinguish unfinished work from active execution: `Now` holds started implementation or verification; Parked can retain previously started work and checkpoints. Next and Later hold unstarted work. Show every Now task, including Verification.
- Ignore fenced examples and HTML comments. Report conflicting or duplicate fields instead of selecting a value.
- Keep epics separate from tasks and their counts. Show open epic progress when present; epic approval does not approve or activate children.
- Treat a task as complete only when it is in `BACKLOG_DONE.md` with explicit `Status: Done`, or when a legacy unsplit backlog explicitly marks it Done.
- Never treat an `I-###` idea as a formal task, priority commitment, or planning candidate.
- Do not claim a detailed plan exists, is approved, or is implementable unless that information is visible in `BACKLOG.md` itself.
- Do not recommend, prioritize, or alter tasks unless the user explicitly asks what should be next.

## Default Output

Use this compact structure:

```text
Backlog overview

Now
- T-000 Task title - P1 - Implementation

Next
- None selected.

Later: 8 tasks
- T-000 Task title - P2 - Plan review
- T-000 Task title - P3 - Discussion
- ... 6 more

Parked: 1
- T-000 Task title - P1 - Blocked
  Blocked: short visible blocker

Done: 24
```

Rules:

- Show all `Now` and `Next` tasks.
- For `Later` and `Parked`, show at most eight tasks per group in the default view; state the remainder count.
- Include task ID, title, priority, and lifecycle stage when available.
- Include a recorded next action for Now tasks and note excess over the declared WIP advisory limit without proposing status changes.
- Keep formulation status, plan approval, and remaining acceptance distinct. A confirmed plan alone does not make a task eligible to start.
- Show a blocker only for parked tasks and only when it is explicitly recorded.
- Show only the declared completed count for `Done` unless the user asks for completed work. If the count is absent or unclear, count explicit completed records in `BACKLOG_DONE.md`.
- Omit empty sections except `Now` and `Next`, which should explicitly say `None selected.` when empty.
- Preserve the backlog's terminology. Do not invent statuses, priorities, owners, dates, or dependencies.

## Requested Views

When asked, support these expanded views while remaining read-only:

- `all pending`: list every non-Done task.
- `by priority`: group pending tasks by priority.
- `by area`: group pending tasks by area.
- `parked`: show intentionally parked and blocked tasks, preserving Resume When, Resume Stage, and Blocked By when recorded.
- `completed`: read `BACKLOG_DONE.md` and list the requested completed scope; keep full-history output compact unless the user asks for all details.
- `ideas`: read `IDEA_INBOX.md` and list open `I-###` ideas without inventing priority, stage, or promotion readiness. Read `IDEA_ARCHIVE.md` only when requested.
- `what next`: offer up to three candidates based only on explicit priority, blockers, typed prerequisites, active status, and visible plan references. Distinguish the next planning action from execution eligibility. If prerequisite completion cannot be established from the permitted sources, state that it remains unverified. Do not move any task to `Now` or imply activation.

Keep the answer compact unless the user asks for detail.
