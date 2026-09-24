#!/usr/bin/env python3
"""Validate the repository's Markdown governance contract."""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote


PLAN_STATUSES = ("draft", "pending", "confirmed", "implemented", "superseded")
PLAN_STATUS_SET = set(PLAN_STATUSES)
PLAN_STATUS_PATTERN = "|".join(PLAN_STATUSES)
TASK_STATUSES = {"Now", "Next", "Later", "Parked"}
STAGES = {"Discussion", "Plan drafting", "Plan review", "Ready", "Implementation", "Verification", "Blocked"}
ACTIVE_STAGES = {"Implementation", "Verification"}
PLAN_FILENAME_RE = re.compile(
    r"^(?P<stamp>\d{4}-\d{2}-\d{2}-\d{4})_(?P<task>T-\d{3})_"
    rf"(?P<status>{PLAN_STATUS_PATTERN})_"
    r"(?P<slug>[a-z0-9][a-z0-9-]*)\.md$"
)
TASK_RE = re.compile(r"^- \[(?P<checked>[ xX])\] (?P<id>T-\d{3}) (?P<title>.+)$")
EPIC_RE = re.compile(r"^- \[(?P<checked>[ xX])\] (?P<id>E-\d{3}) (?P<title>.+)$")
CHECKPOINT_FIELDS = {"Checkpoint Updated", "Completed Work", "Remaining Work", "Next Action", "Open Issues", "Executor"}
PREREQUISITE_FIELDS = ("Planning Prerequisites", "Implementation Prerequisites", "Acceptance Prerequisites")
FIELD_RE = re.compile(r"^  - (?P<name>[A-Za-z][A-Za-z ]+):(?:\s*(?P<value>.*))?$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
REQUIRED_DOCS = {
    "AGENTS.md",
    "ARCHITECTURE.md",
    "BACKLOG.md",
    "BACKLOG_DONE.md",
    "DESIGN_BRIEF.md",
    "IDEA_ARCHIVE.md",
    "IDEA_INBOX.md",
    "PROJECT_LOG.md",
    "PRODUCT_DESIGN.md",
    "README.md",
    "TESTING_PLAN.md",
    "WORKFLOW.md",
    "plans/000_EXECUTIVE_PLAN.md",
    "plans/README.md",
}
READINESS_FIELDS = {"Goal", "Acceptance", "Scope Exclusions", "Dependencies", "Verification"}
DOCUMENT_CONTRACT = {
    "AGENTS.md": {
        "formulation confirmation",
        "plan approval",
        "activation",
        "`Resume When`",
        "`Blocked By`",
        "`draft`",
        "`pending`",
        "`confirmed`",
        "`implemented`",
        "`superseded`",
    },
    "WORKFLOW.md": {"Resume When", "Blocked By", "Implementation", "Verification", "Design Basis"},
    "BACKLOG.md": {
        "- Plan Type:",
        "- Plan Status:",
        "- Plan Reference:",
        "- Resume When:",
        "- Blocked By:",
        "Completed task count",
        "Current Focus",
        "Planning Horizons",
    },
    "BACKLOG_DONE.md": {"- Plan Type:", "- Plan Status:", "- Plan Reference:"},
    "PRODUCT_DESIGN.md": {"DESIGN_BRIEF.md", "ARCHITECTURE.md", "Design Basis"},
    "plans/README.md": {
        "Resume When",
        "Blocked By",
        "Plan Type: Lightweight",
        "Plan Type: Detailed",
        "Design Basis",
    },
}


@dataclass
class Task:
    source: Path
    line: int
    checked: bool
    task_id: str
    title: str
    section: str
    year: str | None
    fields: dict[str, str]
    field_lines: dict[str, int]
    duplicate_fields: list[tuple[str, int, int]]


@dataclass
class Plan:
    source: Path
    task_id: str
    status: str
    revision: str | None = None


def visible_lines(text: str):
    """Ignore fenced examples and HTML comments; retain original line numbers."""
    fence = None
    comment = False
    for number, line in enumerate(text.splitlines(), 1):
        if fence:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{fence[1]},}}[ \t]*", line):
                fence = None
            continue
        remaining, output = line, ""
        while remaining:
            if comment:
                end = remaining.find("-->")
                if end < 0:
                    break
                remaining, comment = remaining[end + 3:], False
            else:
                start = remaining.find("<!--")
                if start < 0:
                    output += remaining
                    break
                output += remaining[:start]
                remaining, comment = remaining[start + 4:], True
        opening = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", output)
        if opening:
            fence = (opening[1][0], len(opening[1]))
        elif not comment or output:
            yield number, output


def visible_text(text: str) -> str:
    lines = dict(visible_lines(text))
    return "\n".join(lines.get(number, "") for number in range(1, len(text.splitlines()) + 1))


def parse_records(path: Path, pattern=TASK_RE) -> list[Task]:
    lines = list(visible_lines(path.read_text(encoding="utf-8")))
    tasks: list[Task] = []
    index = 0
    section = ""
    year = None
    while index < len(lines):
        number, line = lines[index]
        if line.startswith("## "):
            section = line[3:].strip()
            year = None
            index += 1
            continue
        if line.startswith("### "):
            candidate_year = line[4:].strip()
            year = candidate_year if re.fullmatch(r"\d{4}", candidate_year) else None
            index += 1
            continue
        match = pattern.match(line)
        if not match:
            index += 1
            continue
        fields: dict[str, str] = {}
        field_lines: dict[str, int] = {}
        duplicate_fields: list[tuple[str, int, int]] = []
        cursor = index + 1
        while cursor < len(lines):
            candidate_number, candidate = lines[cursor]
            if re.match(r"^- \[.*\] [TE]-", candidate) or re.match(r"^#{1,6} ", candidate):
                break
            field = FIELD_RE.match(candidate)
            if field:
                name = field.group("name")
                if name in fields:
                    duplicate_fields.append((name, field_lines[name], candidate_number))
                else:
                    fields[name] = (field.group("value") or "").strip()
                    field_lines[name] = candidate_number
            cursor += 1
        tasks.append(
            Task(
                source=path,
                line=number,
                checked=match.group("checked").lower() == "x",
                task_id=match.group("id"),
                title=match.group("title"),
                section=section,
                year=year,
                fields=fields,
                field_lines=field_lines,
                duplicate_fields=duplicate_fields,
            )
        )
        index = cursor
    return tasks


def parse_tasks(path: Path) -> list[Task]:
    return parse_records(path)


def rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def add(issues: list[str], root: Path, path: Path, message: str, line: int | None = None):
    location = rel(root, path)
    if line is not None:
        location += f":{line}"
    issues.append(f"{location}: {message}")


def field_present(task: Task, name: str) -> bool:
    return bool(task.fields.get(name, "").strip())


def parse_plan(path: Path, issues: list[str], root: Path) -> Plan | None:
    filename = PLAN_FILENAME_RE.match(path.name)
    if not filename:
        add(issues, root, path, "detailed plan filename does not follow the required status pattern")
        return None
    text = visible_text(path.read_text(encoding="utf-8"))
    task_matches = list(re.finditer(r"^- Task ID:[ \t]*(.*?)[ \t]*$", text, re.MULTILINE))
    status_matches = list(re.finditer(r"^- Status:[ \t]*(.*?)[ \t]*$", text, re.MULTILINE))
    if not task_matches:
        add(issues, root, path, "missing '- Task ID: T-###' metadata")
    if not status_matches:
        add(issues, root, path, "missing '- Status:' metadata")
    if len(task_matches) > 1:
        line = text.count("\n", 0, task_matches[1].start()) + 1
        add(issues, root, path, "duplicate Task ID metadata", line)
    if len(status_matches) > 1:
        line = text.count("\n", 0, status_matches[1].start()) + 1
        add(issues, root, path, "duplicate Status metadata", line)
    if not task_matches or not status_matches:
        return None
    task_id = task_matches[0].group(1).strip()
    status = status_matches[0].group(1).strip().strip("`")
    if not re.fullmatch(r"T-\d{3}", task_id):
        line = text.count("\n", 0, task_matches[0].start()) + 1
        add(issues, root, path, f"invalid Task ID metadata: {task_id or '<empty>'}", line)
        return None
    if status not in PLAN_STATUS_SET:
        line = text.count("\n", 0, status_matches[0].start()) + 1
        add(issues, root, path, f"invalid Status metadata: {status or '<empty>'}", line)
        return None
    if task_id != filename.group("task"):
        add(issues, root, path, f"embedded task ID {task_id} does not match filename task ID {filename.group('task')}")
    if status != filename.group("status"):
        add(issues, root, path, f"embedded status {status} does not match filename status {filename.group('status')}")
    if status in {"pending", "confirmed"}:
        design_basis = h2_body(text, "Design Basis")
        if design_basis is None:
            add(issues, root, path, f"{status} detailed plan requires a ## Design Basis section")
        elif not design_basis:
            add(issues, root, path, f"{status} detailed plan requires a non-empty ## Design Basis section")
    revisions = re.findall(r"^- Task Revision:[ \t]*(.*?)[ \t]*$", text, re.MULTILINE)
    if status in {"draft", "pending", "confirmed"} or revisions:
        if len(revisions) != 1 or not re.fullmatch(r"[1-9]\d*", revisions[0]):
            add(issues, root, path, "requires exactly one positive Task Revision metadata field")
    if status in {"draft", "pending", "confirmed"} and re.search(r"^- Review Status:", text, re.MULTILINE):
        add(issues, root, path, "current plan must use task authority fields, not generic Review Status")
    return Plan(path, task_id, status, revisions[0] if len(revisions) == 1 else None)


def extract_status_definitions(text: str, start_marker: str) -> set[str]:
    text = visible_text(text)
    start = text.find(start_marker)
    if start < 0:
        return set()
    segment = text[start + len(start_marker) :]
    next_heading = re.search(r"^## ", segment, re.MULTILINE)
    if next_heading:
        segment = segment[: next_heading.start()]
    return set(re.findall(r"^- `([a-z]+)`:", segment, re.MULTILINE))


def markdown_link_target(value: str) -> str | None:
    match = LINK_RE.search(value)
    return match.group(1).split("#", 1)[0] if match else None


def executive_summary_ids(text: str, label: str) -> set[str] | None:
    match = re.search(rf"^- {re.escape(label)}: (.+)\.$", text, re.MULTILINE)
    if not match:
        return None
    value = match.group(1)
    if value == "none":
        return set()
    if not re.fullmatch(r"T-\d{3}(?:, T-\d{3})*", value):
        return None
    ids = value.split(", ")
    return set(ids) if ids == sorted(set(ids)) else None


def h2_body(text: str, heading: str) -> str | None:
    text = visible_text(text)
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if not match:
        return None
    body = text[match.end() :]
    next_heading = re.search(r"^## ", body, re.MULTILINE)
    if next_heading:
        body = body[: next_heading.start()]
    return body.strip()


def validate_task(
    root: Path,
    task: Task,
    issues: list[str],
    plans_by_path: dict[Path, Plan],
):
    label = f"{task.task_id}"
    status = task.fields.get("Status", "")
    stage = task.fields.get("Stage", "")
    is_done_file = task.source.name == "BACKLOG_DONE.md"

    validate_authority(root, task, issues)
    validate_checkpoint(root, task, issues)

    for name, first_line, repeated_line in task.duplicate_fields:
        add(
            issues,
            root,
            task.source,
            f"{label} repeats {name}; first defined on line {first_line}",
            repeated_line,
        )

    for name in {"Priority", "Area", "Source", *READINESS_FIELDS}:
        if not field_present(task, name):
            add(issues, root, task.source, f"{label} has an empty or missing {name} field", task.line)

    if is_done_file:
        if status != "Done" or not task.checked:
            add(issues, root, task.source, f"{label} in BACKLOG_DONE.md must be checked with Status: Done", task.line)
        if "Stage" in task.fields:
            add(issues, root, task.source, f"{label} in BACKLOG_DONE.md must not retain a Stage field", task.line)
        if task.section != "Completed Tasks" or not task.year:
            add(issues, root, task.source, f"{label} must appear under Completed Tasks and a YYYY heading", task.line)
        for conditional in ("Resume When", "Blocked By"):
            if field_present(task, conditional):
                add(issues, root, task.source, f"completed {label} must not retain {conditional}", task.line)
    else:
        if task.checked:
            add(issues, root, task.source, f"unfinished {label} must use an unchecked checkbox", task.line)
        if status not in TASK_STATUSES:
            add(issues, root, task.source, f"{label} has invalid Status: {status or '<missing>'}", task.line)
        elif task.section != status:
            add(issues, root, task.source, f"{label} with Status: {status} must appear under ## {status}", task.line)
        if stage not in STAGES:
            add(issues, root, task.source, f"{label} has invalid Stage: {stage or '<missing>'}", task.line)
        if status == "Now" and stage not in ACTIVE_STAGES:
            add(issues, root, task.source, f"{label} in Now must use Implementation or Verification", task.line)
        if stage in ACTIVE_STAGES and status != "Now":
            add(issues, root, task.source, f"{label} at {stage} must have Status: Now", task.line)
        if stage == "Blocked":
            if status != "Parked":
                add(issues, root, task.source, f"{label} at Blocked must have Status: Parked", task.line)
            if not field_present(task, "Blocked By"):
                add(issues, root, task.source, f"{label} at Blocked requires Blocked By", task.line)
        elif field_present(task, "Blocked By"):
            add(issues, root, task.source, f"{label} may use Blocked By only at Stage: Blocked", task.line)
        if status == "Parked" and stage != "Blocked" and not field_present(task, "Resume When"):
            add(issues, root, task.source, f"intentionally parked {label} requires Resume When", task.line)
        if field_present(task, "Resume When") and not (status == "Parked" and stage != "Blocked"):
            add(issues, root, task.source, f"{label} may use Resume When only for intentional parking", task.line)

    plan_required = is_done_file or stage in {"Plan drafting", "Plan review", "Ready", *ACTIVE_STAGES}
    plan_type = task.fields.get("Plan Type", "")
    plan_status = task.fields.get("Plan Status", "")
    plan_reference = task.fields.get("Plan Reference", "")
    if plan_required:
        for name, value in (("Plan Type", plan_type), ("Plan Status", plan_status), ("Plan Reference", plan_reference)):
            if not value:
                add(issues, root, task.source, f"{label} requires {name} at its current lifecycle stage", task.line)
    elif any((plan_type, plan_status, plan_reference)) and not all((plan_type, plan_status, plan_reference)):
        for name, value in (("Plan Type", plan_type), ("Plan Status", plan_status), ("Plan Reference", plan_reference)):
            if not value:
                add(issues, root, task.source, f"{label} has partial plan metadata and requires {name}", task.line)
    if not plan_required and not any((plan_type, plan_status, plan_reference)):
        return
    if plan_type not in {"Lightweight", "Detailed"}:
        add(issues, root, task.source, f"{label} has invalid Plan Type: {plan_type or '<missing>'}", task.line)
    if plan_status not in PLAN_STATUS_SET:
        add(issues, root, task.source, f"{label} has invalid Plan Status: {plan_status or '<missing>'}", task.line)
    expected_plan_status = {
        "Plan drafting": "draft",
        "Plan review": "pending",
        "Ready": "confirmed",
        "Implementation": "confirmed",
        "Verification": "confirmed",
    }.get(stage)
    if is_done_file:
        expected_plan_status = "implemented"
    if expected_plan_status and plan_status != expected_plan_status:
        add(issues, root, task.source, f"{label} at {stage or 'Done'} requires Plan Status: {expected_plan_status}", task.line)
    if stage == "Discussion":
        add(issues, root, task.source, f"{label} at Discussion must not have current plan metadata", task.line)
    if stage == "Blocked" and plan_status not in {"draft", "pending", "confirmed"}:
        add(issues, root, task.source, f"blocked {label} may reference only a draft, pending, or confirmed plan", task.line)
    if plan_status == "superseded":
        add(issues, root, task.source, f"{label} must not use a superseded plan as its current Plan Reference", task.line)
    if plan_type == "Lightweight":
        if plan_reference != "embedded in this task":
            add(issues, root, task.source, f"lightweight {label} must use 'Plan Reference: embedded in this task'", task.line)
    elif plan_type == "Detailed":
        target = markdown_link_target(plan_reference)
        if not target:
            add(issues, root, task.source, f"detailed {label} requires a Markdown Plan Reference link", task.line)
            return
        target_path = Path(os.path.abspath(task.source.parent / target))
        try:
            target_path.relative_to(root.resolve())
        except ValueError:
            add(issues, root, task.source, f"{label} plan reference escapes the repository: {target}", task.line)
            return
        if not safe_source(root, target_path):
            add(issues, root, task.source, f"{label} plan reference is not a permitted source path: {target}", task.line)
            return
        if not target_path.is_file():
            add(issues, root, task.source, f"{label} plan reference does not exist: {target}", task.line)
            return
        plan = plans_by_path.get(target_path)
        if not plan:
            add(issues, root, task.source, f"{label} plan reference is not a valid detailed plan: {target}", task.line)
            return
        if plan.task_id != task.task_id:
            add(issues, root, task.source, f"{label} references a plan for {plan.task_id}", task.line)
        if plan.status != plan_status:
            add(issues, root, task.source, f"{label} Plan Status {plan_status} does not match referenced plan status {plan.status}", task.line)
        if plan.revision is not None and plan.revision != task.fields.get("Revision"):
            add(issues, root, task.source, f"{label} Task Revision does not match its task Revision", task.line)


def validate_authority(root: Path, record: Task, issues: list[str]):
    fields = record.fields
    epic = record.task_id.startswith("E-")
    historical = record.source.name == "BACKLOG_DONE.md"
    if historical and not any(name in fields for name in ("Revision", "Formulation Status", "Formulation Evidence", "Storage Authorization")):
        return
    def fail(message):
        add(issues, root, record.source, f"{record.task_id} {message}", record.line)
    if not re.fullmatch(r"[1-9]\d*", fields.get("Revision", "")):
        fail("requires a positive Revision")
    formulation = fields.get("Formulation Status")
    if formulation not in {"proposed", "confirmed"}:
        fail("requires Formulation Status: proposed or confirmed")
    if formulation == "confirmed" and not field_present(record, "Formulation Evidence"):
        fail("confirmed formulation requires Formulation Evidence")
    if formulation == "proposed":
        if not field_present(record, "Storage Authorization"):
            fail("proposed formulation requires Storage Authorization")
        if field_present(record, "Formulation Evidence"):
            fail("proposed formulation must not claim current Formulation Evidence")
        if historical or fields.get("Status") == "Now" or fields.get("Stage") == "Ready" or fields.get("Plan Status") in {"confirmed", "implemented"} or (epic and fields.get("Progress") in {"In progress", "Done"}):
            fail("proposed formulation cannot be Ready, active, approved, or completed")
    if "Review Status" in fields:
        fail("use scoped authority fields instead of generic Review Status")
    if not epic:
        approved = fields.get("Plan Status") in {"confirmed", "implemented"}
        if approved and not field_present(record, "Plan Approval Evidence"):
            fail("approved plan requires Plan Approval Evidence for its revision")
        if not approved and field_present(record, "Plan Approval Evidence"):
            fail("unapproved current plan must not retain Plan Approval Evidence")
        if fields.get("Status") == "Now" and not field_present(record, "Activation Evidence"):
            fail("Now requires Activation Evidence")


def validate_checkpoint(root: Path, task: Task, issues: list[str]):
    fields = task.fields
    checkpoint = CHECKPOINT_FIELDS.intersection(fields)
    def fail(message):
        add(issues, root, task.source, f"{task.task_id} {message}", task.line)
    if fields.get("Status") == "Now" or checkpoint:
        for name in sorted(CHECKPOINT_FIELDS):
            if not field_present(task, name):
                fail(f"requires checkpoint field {name}")
        stamp = fields.get("Checkpoint Updated", "")
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp):
                raise ValueError
            date.fromisoformat(stamp)
        except ValueError:
            fail("Checkpoint Updated must be a YYYY-MM-DD calendar date")
        if fields.get("Status") == "Now" and fields.get("Executor", "").strip().lower().startswith("unassigned"):
            fail("Now requires an assigned Executor")
        if fields.get("Status") == "Done":
            for name in ("Remaining Work", "Next Action"):
                if fields.get(name, "").strip().rstrip(".").lower() != "none":
                    fail(f"completed checkpoint requires {name}: None")
    if "Resume Stage" in fields:
        if fields.get("Status") != "Parked" or fields.get("Plan Status") != "confirmed" or fields.get("Stage") not in {"Ready", "Blocked"}:
            fail("Resume Stage is only valid for parked confirmed work at Ready or Blocked")
        if fields["Resume Stage"] not in ACTIVE_STAGES:
            fail("Resume Stage must be Implementation or Verification")
    # Presence is required on parked confirmed work that has a restartable checkpoint.
    if fields.get("Status") == "Parked" and fields.get("Plan Status") == "confirmed" and checkpoint and not field_present(task, "Resume Stage"):
        fail("parked confirmed checkpoint requires Resume Stage")


def validate_prerequisites(root: Path, tasks: list[Task], issues: list[str]):
    by_id = {task.task_id: task for task in tasks}
    graph = {task.task_id: set() for task in tasks}
    for task in tasks:
        fields = task.fields
        def fail(message):
            add(issues, root, task.source, f"{task.task_id} {message}", task.line)
        if fields.get("Status") != "Done" and re.search(r"\bT-\d{3}\b", fields.get("Dependencies", "")):
            fail("task IDs in Dependencies must be classified into typed prerequisites")
        for name in PREREQUISITE_FIELDS:
            if name not in fields:
                continue
            value = fields[name]
            if value == "None":
                continue
            if not re.fullmatch(r"T-\d{3}(?:, T-\d{3})*", value):
                fail(f"{name} must be None or a comma-separated task ID list")
                continue
            ids = value.split(", ")
            if len(ids) != len(set(ids)):
                fail(f"{name} repeats a task ID")
            gated = fields.get("Status") == "Done" or (
                name == "Planning Prerequisites" and fields.get("Stage") in {"Plan drafting", "Plan review", "Ready", *ACTIVE_STAGES}
            ) or (name == "Implementation Prerequisites" and fields.get("Status") == "Now")
            for task_id in ids:
                if task_id not in by_id:
                    fail(f"{name} references unknown task {task_id}")
                    continue
                graph[task.task_id].add(task_id)
                if gated and by_id[task_id].fields.get("Status") != "Done":
                    fail(f"{name} requires {task_id} to be Done at this gate")
    # Iterative DFS avoids recursion limits for large imported task registries.
    visited, active = set(), set()
    for start in sorted(graph):
        if start in visited:
            continue
        stack = [(start, iter(sorted(graph[start])))]
        active.add(start)
        while stack:
            current, children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                active.remove(current)
                visited.add(current)
            elif child in active:
                cycle = [item[0] for item in stack]
                cycle = cycle[cycle.index(child):] + [child]
                add(issues, root, root / "BACKLOG.md", "prerequisite cycle: " + " -> ".join(cycle))
            elif child not in visited:
                active.add(child)
                stack.append((child, iter(sorted(graph[child]))))


def wip_limit(root: Path) -> int | None:
    path = root / "BACKLOG.md"
    if not safe_source(root, path) or not path.is_file():
        return None
    text = visible_text(path.read_text(encoding="utf-8"))
    values = re.findall(r"^- WIP advisory limit: *(.*?) *$", text, re.MULTILINE)
    body = h2_body(text, "Work In Progress") or ""
    if len(values) != 1 or not re.fullmatch(r"[1-9]\d*", values[0]):
        return None
    return int(values[0]) if re.search(rf"^- WIP advisory limit: *{values[0]} *$", body, re.MULTILINE) else None


def collect_warnings(root: Path) -> list[str]:
    root = root.resolve()
    limit = wip_limit(root)
    if limit is None:
        return []
    count = sum(task.fields.get("Status") == "Now" for task in parse_tasks(root / "BACKLOG.md"))
    return [f"BACKLOG.md: {count} tasks in Now exceed WIP advisory limit {limit}; review overlap and priorities."] if count > limit else []


def safe_source(root: Path, path: Path) -> bool:
    """Governance reads never follow symlinks or inspect env/private/runtime trees."""
    try:
        relative = path.absolute().relative_to(root.absolute())
    except ValueError:
        return False
    excluded = {".git", ".secrets", ".venv", "venv", "node_modules", "__pycache__", "tmp", "outputs", "output", "private", "exports", "build", "dist"}
    if ".." in relative.parts or any(part.startswith(".") or ".env" in part.lower() or part in excluded for part in relative.parts):
        return False
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            return False
    return True


def governance_markdown_paths(root: Path):
    for path in sorted(root.glob("*.md")):
        if safe_source(root, path) and path.is_file():
            yield path
    for folder in ("docs", "plans"):
        top = root / folder
        if not safe_source(root, top):
            continue
        for directory, names, files in os.walk(top, followlinks=False):
            names[:] = sorted(name for name in names if safe_source(root, Path(directory) / name))
            for name in sorted(files):
                path = Path(directory) / name
                if path.suffix.lower() == ".md" and safe_source(root, path):
                    yield path


def markdown_anchors(text: str) -> set[str]:
    visible = visible_text(text)
    anchors = set(re.findall(r'<a\s+(?:id|name)=["\']([^"\']+)["\']', visible, re.IGNORECASE))
    used = set(anchors)
    lines = visible.splitlines()
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", line)
        if match:
            title = match[1]
        elif line.strip() and index + 1 < len(lines) and re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", lines[index + 1]):
            title = line.strip()
        else:
            continue
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
        heading = re.sub(r"<[^>]+>", "", heading).lower()
        slug = "".join(char for char in heading if char in "-_ " or char.isalnum() or unicodedata.category(char).startswith("M"))
        slug = slug.replace(" ", "-")
        candidate, number = slug, 0
        while candidate in used:
            number += 1
            candidate = f"{slug}-{number}"
        used.add(candidate)
        anchors.add(candidate)
    return anchors


def link_parts(target: str) -> tuple[str, str]:
    target = target.strip()
    if target.startswith("<"):
        target = target[1:].split(">", 1)[0]
    else:
        target = re.split(r'\s+["\']', target, maxsplit=1)[0]
    file_target, _, fragment = target.partition("#")
    return unquote(file_target), unquote(fragment)


def validate_links(root: Path, issues: list[str]):
    paths = list(governance_markdown_paths(root))
    allowed = {path.resolve() for path in paths}
    anchors = {path.resolve(): markdown_anchors(path.read_text(encoding="utf-8")) for path in paths}
    for path in paths:
        for number, line in visible_lines(path.read_text(encoding="utf-8")):
            for match in LINK_RE.finditer(line):
                target = match[1].strip()
                if not target or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                    continue
                file_target, fragment = link_parts(target)
                raw = path.parent / file_target if file_target else path
                # Normalize '..' before scope checks, but never read the target before checking symlinks.
                normalized = Path(os.path.abspath(raw))
                if not safe_source(root, normalized):
                    add(issues, root, path, f"relative link target is outside permitted source paths: {target}", number)
                    continue
                try:
                    exists = normalized.exists()
                except OSError:
                    exists = False
                if not exists:
                    add(issues, root, path, f"broken relative Markdown link: {target}", number)
                elif fragment:
                    if normalized not in allowed:
                        add(issues, root, path, f"fragment target must be a scoped governance Markdown source: {target}", number)
                    elif fragment not in anchors[normalized]:
                        add(issues, root, path, f"broken Markdown anchor: {target}", number)


def validate_optional_artifacts(root: Path, workflow: str, issues: list[str]):
    path = root / "WORKFLOW.md"
    body = h2_body(workflow, "Optional Artifacts")
    if len(re.findall(r"^## Optional Artifacts$", workflow, re.MULTILINE)) != 1:
        add(issues, root, path, "requires exactly one Optional Artifacts section")
    registered = set()
    sources = set(governance_markdown_paths(root))
    for line in (body or "").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells[0] == "Artifact" or re.fullmatch(r"[-: ]+", cells[0]):
            continue
        if len(cells) != 6 or not all(cells):
            add(issues, root, path, "optional artifact row requires Artifact, Path, Owner, Inputs, Update When, Retire When")
            continue
        match = LINK_RE.fullmatch(cells[1])
        if not match:
            add(issues, root, path, "optional artifact Path requires a local Markdown link")
            continue
        target, fragment = link_parts(match[1])
        target_path = root / target
        if fragment or Path(target).is_absolute() or not safe_source(root, target_path) or not target.endswith(".md") or target_path not in sources:
            add(issues, root, path, f"optional artifact must name an existing scoped Markdown file: {target}")
            continue
        if target in registered:
            add(issues, root, path, f"duplicate optional artifact registration: {target}")
        registered.add(target)
    if body != "No optional artifacts adopted." and not registered:
        add(issues, root, path, "Optional Artifacts requires a complete registry or its canonical empty state")
    if registered and "No optional artifacts adopted." in (body or ""):
        add(issues, root, path, "optional artifact empty state conflicts with registered artifacts")
    candidates = ["ROADMAP.md", "docs/DECISIONS.md", "docs/TRACEABILITY.md", "docs/REVIEW_HANDOFF.md"]
    temporary = root / "plans/temporary"
    if safe_source(root, temporary):
        candidates.extend(rel(root, item) for item in temporary.glob("*.md"))
    for name in candidates:
        if (root / name).is_file() and name not in registered:
            add(issues, root, path, f"adopted optional artifact is not registered: {name}")


def validate_epics(root: Path, tasks: list[Task], executive: str, issues: list[str]):
    backlog, done = root / "BACKLOG.md", root / "BACKLOG_DONE.md"
    epics = parse_records(backlog, EPIC_RE) + parse_records(done, EPIC_RE)
    by_id, members = {}, defaultdict(list)
    for epic in epics:
        label, fields = epic.task_id, epic.fields
        def fail(message):
            add(issues, root, epic.source, f"{label} {message}", epic.line)
        if label in by_id:
            fail("duplicate epic ID")
        by_id[label] = epic
        validate_authority(root, epic, issues)
        for field, _, line in epic.duplicate_fields:
            add(issues, root, epic.source, f"{label} repeats {field}", line)
        for field in ("Progress", "Goal", "Scope", "Scope Exclusions", "Completion Criteria", "Coordination Plan"):
            if not field_present(epic, field):
                fail(f"requires {field}")
        for field in ("Status", "Stage", "Plan Type", "Plan Status", "Plan Reference", "Epic", *PREREQUISITE_FIELDS, *CHECKPOINT_FIELDS):
            if field in fields:
                fail(f"must not have task/nesting field {field}")
        closed = epic.source == done
        if closed:
            if not epic.checked or fields.get("Progress") != "Done" or epic.section != "Completed Epics" or not epic.year:
                fail("must be checked with Progress: Done under Completed Epics and a YYYY heading")
            evidence = LINK_RE.search(fields.get("Completion Evidence", ""))
            if not evidence:
                fail("closure requires local Markdown-linked Completion Evidence")
            else:
                target, _ = link_parts(evidence[1])
                evidence_path = Path(os.path.abspath(epic.source.parent / target))
                evidence_location = rel(root, evidence_path)
                evidence_owner = evidence_location == "PROJECT_LOG.md" or (
                    evidence_location.startswith("docs/") and not evidence_location.startswith("docs/examples/")
                )
                if not target.endswith(".md") or Path(target).is_absolute() or not safe_source(root, evidence_path) or not evidence_path.is_file() or not evidence_owner:
                    fail("closure requires local Markdown-linked Completion Evidence in a log or verification document")
        elif epic.checked or fields.get("Progress") not in {"Planned", "In progress", "Paused"} or epic.section != "Epics":
            fail("requires unchecked open Progress under Epics")
        if fields.get("Progress") == "Paused" and not field_present(epic, "Resume When"):
            fail("Paused requires Resume When")
        if fields.get("Progress") != "Paused" and "Resume When" in fields:
            fail("Resume When is only valid while Paused")
        link = LINK_RE.fullmatch(fields.get("Coordination Plan", ""))
        if not link or link[1] != f"plans/000_EXECUTIVE_PLAN.md#{label.lower()}":
            fail("Coordination Plan must link to its executive-plan anchor")
    for task in tasks:
        if "Epic" not in task.fields:
            continue
        parent = task.fields["Epic"]
        if not re.fullmatch(r"E-\d{3}", parent) or parent not in by_id:
            add(issues, root, task.source, f"{task.task_id} Epic must name one existing E-###", task.line)
        else:
            members[parent].append(task)
    executive_path = root / "plans/000_EXECUTIVE_PLAN.md"
    if len(re.findall(r"^## Epic Coordination$", executive, re.MULTILINE)) != 1:
        add(issues, root, executive_path, "requires exactly one Epic Coordination section")
    body = h2_body(executive, "Epic Coordination") or ""
    blocks = re.findall(r"^### (E-\d{3})[ \t]*\n(.*?)(?=^### |\Z)", body, re.MULTILINE | re.DOTALL)
    counts = Counter(label for label, _ in blocks)
    for label in sorted(set(by_id) | set(counts)):
        if label not in by_id or counts[label] != 1:
            add(issues, root, executive_path, f"{label} needs exactly one coordination block and an epic record")
    tasks_by_id = {task.task_id: task for task in tasks}
    for label, block in blocks:
        def fail(message):
            add(issues, root, executive_path, f"{label} {message}")
        for field in ("Next Action", "Open Issues"):
            values = re.findall(rf"^- {field}: *(.*?) *$", block, re.MULTILINE)
            if len(values) != 1 or not values[0]:
                fail(f"coordination requires exactly one non-empty {field}")
        milestones = re.findall(r"^- \[([ xX])\] (M[1-9]\d*) — (.+)$", block, re.MULTILINE)
        milestone_lines = re.findall(r"^- \[.*\] M.*$", block, re.MULTILINE)
        if not milestones or len(milestones) != len(milestone_lines):
            fail("requires well-formed milestone checkboxes")
        if len({item[1] for item in milestones}) != len(milestones):
            fail("repeats a milestone ID")
        epic = by_id.get(label)
        closed = epic is not None and epic.source == done
        for check, milestone, text in milestones:
            if closed and check.lower() != "x":
                fail(f"closed epic has unchecked milestone {milestone}")
            if "Tasks:" in text and not re.search(r"Tasks: T-\d{3}(?:, T-\d{3})*\.$", text):
                fail(f"{milestone} has malformed Tasks references")
            for task_id in set(re.findall(r"T-\d{3}", text)):
                task = tasks_by_id.get(task_id)
                if task is None:
                    fail(f"{milestone} references unknown task {task_id}")
                elif (closed or check.lower() == "x") and task.fields.get("Status") != "Done":
                    fail(f"{milestone} requires {task_id} to be Done")
        if closed and (not members[label] or any(task.fields.get("Status") != "Done" for task in members[label])):
            fail("closure requires at least one member and all members Done")
    expected = ", ".join(sorted(epic.task_id for epic in epics if epic.source == backlog)) or "none"
    if re.findall(r"^- Open epics: (.+)\.$", executive, re.MULTILINE) != [expected]:
        add(issues, root, executive_path, f"Open epics summary must be: {expected}")
    count = sum(epic.source == done for epic in epics)
    if re.findall(r"^- Completed epic count: *(\d+) *$", visible_text(backlog.read_text(encoding="utf-8")), re.MULTILINE) != [str(count)]:
        add(issues, root, backlog, f"Completed epic count must be {count}, exactly once")


def validate(root: Path) -> list[str]:
    root = root.resolve()
    issues: list[str] = []

    for required in sorted(REQUIRED_DOCS):
        if not safe_source(root, root / required) or not (root / required).is_file():
            add(issues, root, root / required, "required governance document is missing")
    if issues:
        return issues

    workflow = (root / "WORKFLOW.md").read_text(encoding="utf-8")
    plans_readme = (root / "plans/README.md").read_text(encoding="utf-8")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    testing = (root / "TESTING_PLAN.md").read_text(encoding="utf-8")

    workflow = visible_text(workflow)
    if re.findall(r"^Governance version: *(.*?) *$", workflow, re.MULTILINE) != ["2"]:
        add(issues, root, root / "WORKFLOW.md", "requires exactly one unfenced Governance version: 2 marker")
    if wip_limit(root) is None:
        add(issues, root, root / "BACKLOG.md", "requires one positive WIP advisory limit in Work In Progress")
    validate_optional_artifacts(root, workflow, issues)
    workflow_states = extract_status_definitions(workflow, "## Plan States")
    readme_states = extract_status_definitions(plans_readme, "Allowed statuses:")
    if workflow_states != PLAN_STATUS_SET:
        add(issues, root, root / "WORKFLOW.md", f"plan states must be exactly {list(PLAN_STATUSES)}")
    if readme_states != PLAN_STATUS_SET:
        add(issues, root, root / "plans/README.md", f"plan statuses must be exactly {list(PLAN_STATUSES)}")
    for heading in ("### 1. Formulation Confirmation", "### 2. Plan Approval", "### 3. Activation"):
        if heading not in workflow:
            add(issues, root, root / "WORKFLOW.md", f"missing lifecycle gate heading: {heading}")
    if "## Three-Gate Rule" not in plans_readme:
        add(issues, root, root / "plans/README.md", "missing Three-Gate Rule")
    for relative, fragments in DOCUMENT_CONTRACT.items():
        path = root / relative
        text = path.read_text(encoding="utf-8")
        comparison = text.lower() if relative == "AGENTS.md" else text
        for fragment in sorted(fragments):
            expected = fragment.lower() if relative == "AGENTS.md" else fragment
            if expected not in comparison:
                add(issues, root, path, f"governance contract is missing required wording or field: {fragment}")
    workflow_sources = h2_body(workflow, "Sources of Truth")
    workflow_matrix = h2_body(workflow, "Documentation Update Matrix")
    if workflow_sources is None:
        add(issues, root, root / "WORKFLOW.md", "missing Sources of Truth section")
        workflow_sources = ""
    if workflow_matrix is None:
        add(issues, root, root / "WORKFLOW.md", "missing Documentation Update Matrix section")
        workflow_matrix = ""
    for source in REQUIRED_DOCS:
        if source in {"WORKFLOW.md", "plans/README.md"}:
            continue
        if source.endswith(".md") and f"`{source}`" not in workflow_sources and source not in {"IDEA_ARCHIVE.md", "IDEA_INBOX.md"}:
            add(issues, root, root / "WORKFLOW.md", f"Sources of Truth does not reference {source}")
    if "`PRODUCT_DESIGN.md`" not in workflow_matrix:
        add(issues, root, root / "WORKFLOW.md", "Documentation Update Matrix does not reference PRODUCT_DESIGN.md")
    for required_source in (
        "ARCHITECTURE.md",
        "BACKLOG.md",
        "PRODUCT_DESIGN.md",
        "PROJECT_LOG.md",
        "TESTING_PLAN.md",
        "WORKFLOW.md",
    ):
        if f"`{required_source}`" not in agents:
            add(issues, root, root / "AGENTS.md", f"Project Sources of Truth does not reference {required_source}")
    if "`PRODUCT_DESIGN.md`" not in readme:
        add(issues, root, root / "README.md", "Repository Map does not reference PRODUCT_DESIGN.md")
    if (root / "WORKSPACE_DESIGN.md").exists():
        for path, text in ((root / "WORKFLOW.md", workflow), (root / "AGENTS.md", agents)):
            if "`WORKSPACE_DESIGN.md`" not in text:
                add(issues, root, path, "adopted WORKSPACE_DESIGN.md is missing from source-of-truth rules")
    docs_command = "python3 -B scripts/docs_check.py"
    tests_command = "python3 -B -m unittest discover -s tests -p 'test_docs_check.py'"
    for path, text in ((root / "AGENTS.md", agents), (root / "README.md", readme), (root / "TESTING_PLAN.md", testing)):
        if docs_command not in text:
            add(issues, root, path, "canonical documentation-check command is missing")
        if tests_command not in text:
            add(issues, root, path, "canonical checker-test command is missing")

    plan_paths = sorted(
        path for path in (root / "plans").glob("*.md") if path.name not in {"README.md", "000_EXECUTIVE_PLAN.md"}
    )
    plans: list[Plan] = []
    for path in plan_paths:
        if not safe_source(root, path) or not path.is_file():
            add(issues, root, path, "detailed plan is not a permitted regular source file")
            continue
        parsed = parse_plan(path, issues, root)
        if parsed:
            plans.append(parsed)
    plans_by_path = {plan.source.resolve(): plan for plan in plans}

    tasks = parse_tasks(root / "BACKLOG.md") + parse_tasks(root / "BACKLOG_DONE.md")
    seen: dict[str, Task] = {}
    for task in tasks:
        if task.task_id in seen:
            first = seen[task.task_id]
            add(issues, root, task.source, f"duplicate task ID {task.task_id}; first seen in {rel(root, first.source)}:{first.line}", task.line)
        else:
            seen[task.task_id] = task
        validate_task(root, task, issues, plans_by_path)

    now_ids = [task.task_id for task in tasks if task.fields.get("Status") == "Now"]
    validate_prerequisites(root, tasks, issues)
    for plan in plans:
        if plan.status not in PLAN_STATUS_SET:
            add(issues, root, plan.source, f"invalid plan status: {plan.status}")
        if plan.task_id not in seen:
            add(issues, root, plan.source, f"plan task ID {plan.task_id} does not exist in either backlog")

    executive_path = root / "plans/000_EXECUTIVE_PLAN.md"
    executive = visible_text(executive_path.read_text(encoding="utf-8"))
    validate_epics(root, tasks, executive, issues)
    index_re = re.compile(
        rf"^- (T-\d{{3}}) — `({PLAN_STATUS_PATTERN})` — "
        r"\[([^\]]+)\]\(([^)]+)\)$",
        re.MULTILINE,
    )
    indexed: dict[str, tuple[str, str]] = {}
    for match in index_re.finditer(executive):
        task_id, status, label, target = match.groups()
        if label != target:
            add(issues, root, executive_path, f"index label and target differ for {task_id}")
        if target in indexed:
            add(issues, root, executive_path, f"duplicate executive-plan entry for {target}")
        indexed[target] = (task_id, status)
    actual_names = {plan.source.name for plan in plans}
    if set(indexed) != actual_names:
        missing = sorted(actual_names - set(indexed))
        extra = sorted(set(indexed) - actual_names)
        detail = []
        if missing:
            detail.append(f"missing {missing}")
        if extra:
            detail.append(f"extra {extra}")
        add(issues, root, executive_path, "detailed-plan index drift: " + "; ".join(detail))
    for plan in plans:
        entry = indexed.get(plan.source.name)
        if entry and entry != (plan.task_id, plan.status):
            add(issues, root, executive_path, f"index metadata for {plan.source.name} does not match its task ID and status")

    plans_by_task: dict[str, list[Plan]] = defaultdict(list)
    for plan in plans:
        if plan.status != "superseded":
            plans_by_task[plan.task_id].append(plan)
    for task_id, current_plans in plans_by_task.items():
        if len(current_plans) > 1:
            names = ", ".join(plan.source.name for plan in current_plans)
            add(issues, root, root / "plans", f"{task_id} has multiple non-superseded detailed plans: {names}")

    referenced_current_plans: set[Path] = set()
    for task in tasks:
        if task.fields.get("Plan Type") != "Detailed":
            continue
        target = markdown_link_target(task.fields.get("Plan Reference", ""))
        if target:
            candidate = Path(os.path.abspath(task.source.parent / target))
            if safe_source(root, candidate):
                referenced_current_plans.add(candidate)
    for plan in plans:
        if plan.status != "superseded" and plan.source.resolve() not in referenced_current_plans:
            add(issues, root, plan.source, "non-superseded detailed plan is not the current Plan Reference of its task")

    backlog = visible_text((root / "BACKLOG.md").read_text(encoding="utf-8"))
    backlog_done = visible_text((root / "BACKLOG_DONE.md").read_text(encoding="utf-8"))
    done_tasks = [task for task in tasks if task.source.name == "BACKLOG_DONE.md"]
    unfinished_tasks = [task for task in tasks if task.source.name == "BACKLOG.md"]
    backlog_h2_counts = Counter(line[3:].strip() for _, line in visible_lines(backlog) if line.startswith("## "))
    for heading in ("Completed Work", "Current Focus", "Planning Horizons", "Work In Progress", "Epics"):
        if backlog_h2_counts[heading] != 1:
            add(issues, root, root / "BACKLOG.md", f"must contain exactly one ## {heading} section")
    done_h2_counts = Counter(line[3:].strip() for _, line in visible_lines(backlog_done) if line.startswith("## "))
    if done_h2_counts["Completed Tasks"] != 1:
        add(issues, root, root / "BACKLOG_DONE.md", "must contain exactly one ## Completed Tasks section")

    if done_h2_counts["Completed Epics"] != 1:
        add(issues, root, root / "BACKLOG_DONE.md", "must contain exactly one ## Completed Epics section")
    for path in (root / "BACKLOG.md", root / "BACKLOG_DONE.md"):
        record_open = False
        for line_number, line in visible_lines(path.read_text(encoding="utf-8")):
            if re.match(r"^#{1,6} ", line):
                record_open = False
            if TASK_RE.fullmatch(line) or EPIC_RE.fullmatch(line):
                record_open = True
            if FIELD_RE.fullmatch(line) and not record_open:
                add(issues, root, path, "orphan task/epic field outside a record", line_number)
            if re.match(r"^\s*- \[.*\] [TE]-", line) and not (TASK_RE.fullmatch(line) or EPIC_RE.fullmatch(line)):
                add(issues, root, path, "malformed or nested task/epic record", line_number)

    count_matches = re.findall(r"^- Completed task count:\s*(\d+)\s*$", backlog, re.MULTILINE)
    if len(count_matches) != 1:
        add(issues, root, root / "BACKLOG.md", "must contain exactly one Completed task count")
    elif int(count_matches[0]) != len(done_tasks):
        add(issues, root, root / "BACKLOG.md", f"Completed task count must be {len(done_tasks)}")

    focus = h2_body(backlog, "Current Focus")
    active = sorted((task for task in unfinished_tasks if task.fields.get("Status") == "Now"), key=lambda task: task.task_id)
    expected_focus = "\n".join(f"- {task.task_id} — `{task.fields.get('Stage', '')}`." for task in active) or "No tasks are in `Now`."
    if focus != expected_focus:
        add(issues, root, root / "BACKLOG.md", f"Current Focus must be: {expected_focus}")

    horizons = h2_body(backlog, "Planning Horizons")
    unfinished_ids = {task.task_id for task in unfinished_tasks}
    if not unfinished_ids:
        expected_empty = "No planning horizons exist because no unfinished formal tasks remain."
        if horizons != expected_empty:
            add(issues, root, root / "BACKLOG.md", f"Planning Horizons must be: {expected_empty}")
    elif horizons is None:
        add(issues, root, root / "BACKLOG.md", "missing Planning Horizons section")
    else:
        horizon_counts = Counter(re.findall(r"T-\d{3}", horizons))
        for task_id in sorted(unfinished_ids):
            if horizon_counts[task_id] != 1:
                add(issues, root, root / "BACKLOG.md", f"Planning Horizons must list {task_id} exactly once")
        for task_id in sorted(set(horizon_counts) - unfinished_ids):
            add(issues, root, root / "BACKLOG.md", f"Planning Horizons references unknown or completed task {task_id}")

    task_by_id = {task.task_id: task for task in tasks}
    expected_summaries = {
        "`Now`": set(now_ids),
        "Plans awaiting review": {task.task_id for task in tasks if task.fields.get("Plan Status") == "pending"},
        "Confirmed plans stored for later": {
            task.task_id
            for task in tasks
            if task.fields.get("Plan Status") == "confirmed"
            and task.fields.get("Status") != "Now"
            and task.fields.get("Stage") != "Blocked"
            and task.task_id in task_by_id
        },
        "Blocked plans": {
            task.task_id
            for task in tasks
            if task.fields.get("Plan Type") in {"Lightweight", "Detailed"}
            and task.fields.get("Status") == "Parked"
            and task.fields.get("Stage") == "Blocked"
        },
    }
    for label, expected in expected_summaries.items():
        summary_matches = re.findall(rf"^- {re.escape(label)}: (.+)\.$", executive, re.MULTILINE)
        if len(summary_matches) != 1:
            add(issues, root, executive_path, f"must contain exactly one {label} summary")
        actual = executive_summary_ids(executive, label)
        if actual != expected:
            rendered = "none" if not expected else ", ".join(sorted(expected))
            add(issues, root, executive_path, f"{label} summary must be: {rendered}")

    validate_links(root, issues)

    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path, help="repository or fixture root")
    args = parser.parse_args()
    issues = validate(args.root)
    for warning in collect_warnings(args.root):
        print("Warning: " + warning)
    if issues:
        print("Documentation check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Documentation check passed: {args.root.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
