#!/usr/bin/env python3
"""Validate the repository's Markdown governance contract."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


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
    "WORKFLOW.md": {"Resume When", "Blocked By", "Implementation", "Verification"},
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
    "plans/README.md": {"Resume When", "Blocked By", "Plan Type: Lightweight", "Plan Type: Detailed"},
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


def visible_lines(text: str):
    """Yield non-fenced lines while preserving original line numbers."""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def parse_tasks(path: Path) -> list[Task]:
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
        match = TASK_RE.match(line)
        if not match:
            index += 1
            continue
        fields: dict[str, str] = {}
        field_lines: dict[str, int] = {}
        duplicate_fields: list[tuple[str, int, int]] = []
        cursor = index + 1
        while cursor < len(lines):
            candidate_number, candidate = lines[cursor]
            if TASK_RE.match(candidate) or candidate.startswith(("## ", "### ")):
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
    text = path.read_text(encoding="utf-8")
    task_matches = list(re.finditer(r"^- Task ID:\s*(.*?)\s*$", text, re.MULTILINE))
    status_matches = list(re.finditer(r"^- Status:\s*(.*?)\s*$", text, re.MULTILINE))
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
    return Plan(path, task_id, status)


def extract_status_definitions(text: str, start_marker: str) -> set[str]:
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
    ids = set(re.findall(r"T-\d{3}", value))
    return ids if ids else None


def h2_body(text: str, heading: str) -> str | None:
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
        target_path = (task.source.parent / target).resolve()
        try:
            target_path.relative_to(root.resolve())
        except ValueError:
            add(issues, root, task.source, f"{label} plan reference escapes the repository: {target}", task.line)
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


def validate(root: Path) -> list[str]:
    root = root.resolve()
    issues: list[str] = []

    for required in sorted(REQUIRED_DOCS):
        if not (root / required).is_file():
            add(issues, root, root / required, "required governance document is missing")
    if issues:
        return issues

    workflow = (root / "WORKFLOW.md").read_text(encoding="utf-8")
    plans_readme = (root / "plans/README.md").read_text(encoding="utf-8")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    readme = (root / "README.md").read_text(encoding="utf-8")
    testing = (root / "TESTING_PLAN.md").read_text(encoding="utf-8")

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
    for source in REQUIRED_DOCS:
        if source in {"WORKFLOW.md", "plans/README.md"}:
            continue
        if source.endswith(".md") and f"`{source}`" not in workflow and source not in {"IDEA_ARCHIVE.md", "IDEA_INBOX.md"}:
            add(issues, root, root / "WORKFLOW.md", f"Sources of Truth does not reference {source}")
    for required_source in ("ARCHITECTURE.md", "BACKLOG.md", "PROJECT_LOG.md", "TESTING_PLAN.md", "WORKFLOW.md"):
        if f"`{required_source}`" not in agents:
            add(issues, root, root / "AGENTS.md", f"Project Sources of Truth does not reference {required_source}")
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
    if len(now_ids) > 1:
        add(issues, root, root / "BACKLOG.md", f"at most one task may be in Now; found {', '.join(now_ids)}")
    for plan in plans:
        if plan.status not in PLAN_STATUS_SET:
            add(issues, root, plan.source, f"invalid plan status: {plan.status}")
        if plan.task_id not in seen:
            add(issues, root, plan.source, f"plan task ID {plan.task_id} does not exist in either backlog")

    executive_path = root / "plans/000_EXECUTIVE_PLAN.md"
    executive = executive_path.read_text(encoding="utf-8")
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
            referenced_current_plans.add((task.source.parent / target).resolve())
    for plan in plans:
        if plan.status != "superseded" and plan.source.resolve() not in referenced_current_plans:
            add(issues, root, plan.source, "non-superseded detailed plan is not the current Plan Reference of its task")

    backlog = (root / "BACKLOG.md").read_text(encoding="utf-8")
    backlog_done = (root / "BACKLOG_DONE.md").read_text(encoding="utf-8")
    done_tasks = [task for task in tasks if task.source.name == "BACKLOG_DONE.md"]
    unfinished_tasks = [task for task in tasks if task.source.name == "BACKLOG.md"]
    backlog_h2_counts = Counter(line[3:].strip() for _, line in visible_lines(backlog) if line.startswith("## "))
    for heading in ("Completed Work", "Current Focus", "Planning Horizons"):
        if backlog_h2_counts[heading] != 1:
            add(issues, root, root / "BACKLOG.md", f"must contain exactly one ## {heading} section")
    done_h2_counts = Counter(line[3:].strip() for _, line in visible_lines(backlog_done) if line.startswith("## "))
    if done_h2_counts["Completed Tasks"] != 1:
        add(issues, root, root / "BACKLOG_DONE.md", "must contain exactly one ## Completed Tasks section")

    count_matches = re.findall(r"^- Completed task count:\s*(\d+)\s*$", backlog, re.MULTILINE)
    if len(count_matches) != 1:
        add(issues, root, root / "BACKLOG.md", "must contain exactly one Completed task count")
    elif int(count_matches[0]) != len(done_tasks):
        add(issues, root, root / "BACKLOG.md", f"Completed task count must be {len(done_tasks)}")

    focus = h2_body(backlog, "Current Focus")
    if len(now_ids) == 1:
        active = next(task for task in unfinished_tasks if task.task_id == now_ids[0])
        expected_focus = f"{active.task_id} is the single active task in `Now + {active.fields.get('Stage', '')}`."
    else:
        expected_focus = "No task is active. Keep at most one task in `Now`."
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
        "Plans awaiting review": {plan.task_id for plan in plans if plan.status == "pending"},
        "Confirmed plans stored for later": {
            task.task_id
            for task in tasks
            if task.fields.get("Plan Type") == "Detailed"
            and task.fields.get("Plan Status") == "confirmed"
            and task.fields.get("Status") != "Now"
            and task.fields.get("Stage") != "Blocked"
            and task.task_id in task_by_id
        },
        "Blocked plans": {
            task.task_id
            for task in tasks
            if task.fields.get("Plan Type") == "Detailed"
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

    for path in root.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for number, line in visible_lines(text):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip()
                if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                file_target = target.split("#", 1)[0]
                if not file_target:
                    continue
                resolved = (path.parent / file_target).resolve()
                if not resolved.exists():
                    add(issues, root, path, f"broken relative Markdown link: {target}", number)

    return sorted(set(issues))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path, help="repository or fixture root")
    args = parser.parse_args()
    issues = validate(args.root)
    if issues:
        print("Documentation check failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print(f"Documentation check passed: {args.root.resolve()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
