#!/usr/bin/env python3
"""Generate an interactive HTML snapshot of the current Markdown backlog."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import re
from pathlib import Path


TASK_START = re.compile(r"^- \[ \] (T-\d{3})\s+(.+)$")
EPIC_START = re.compile(r"^- \[ \] (E-\d{3})\s+(.+)$")
FIELD = re.compile(r"^  - ([A-Za-z][A-Za-z /-]+):\s*(.*)$")
SECTION = re.compile(r"^#{1,6} (.+?)\s*$")


def visible_lines(text: str):
    """Exclude Markdown examples and HTML comments from live records."""
    fence = None
    comment = False
    for line in text.splitlines():
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
            yield output


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_records(text: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    section = "Other"
    current: dict[str, str] | None = None
    epics: list[dict[str, str]] = []
    tasks: list[dict[str, str]] = []
    seen: set[str] = set()
    last_field = None

    def finish() -> None:
        nonlocal current
        if not current:
            return
        if current["id"] in seen:
            raise ValueError(f"Duplicate record: {current['id']}")
        seen.add(current["id"])
        if current["kind"] == "task":
            if current.get("Status", section) != current["section"]:
                raise ValueError(f"Status/section mismatch: {current['id']}")
            tasks.append(current)
        else:
            epics.append(current)
        current = None

    for raw in visible_lines(text):
        match = SECTION.match(raw)
        if match:
            finish()
            section = match.group(1)
            last_field = None
            continue
        task_match = TASK_START.match(raw)
        epic_match = EPIC_START.match(raw)
        if task_match or epic_match:
            finish()
            last_field = None
            if task_match and section not in {"Now", "Next", "Later", "Parked"}:
                raise ValueError(f"Task outside an unfinished-work section: {task_match.group(1)}")
            if epic_match and section != "Epics":
                raise ValueError(f"Epic outside Epics: {epic_match.group(1)}")
            match = task_match or epic_match
            current = {
                "kind": "task" if task_match else "epic",
                "id": match.group(1),
                "name": compact(match.group(2)),
                "section": section,
            }
            continue
        if re.match(r"^- \[[xX]\] ", raw):
            finish()
            last_field = None
            continue
        if current:
            field_match = FIELD.match(raw)
            if field_match:
                last_field = field_match.group(1)
                if last_field in current:
                    raise ValueError(f"Duplicate field {last_field}: {current['id']}")
                current[last_field] = compact(field_match.group(2))
            elif last_field and raw.startswith("    ") and raw.strip():
                current[last_field] = compact(current[last_field] + " " + raw.strip())
    finish()
    return epics, tasks


def coordination_rows(text: str, epics: list[dict[str, str]]) -> str:
    open_ids = {epic["id"] for epic in epics}
    sections: dict[str, list[str]] = {}
    in_coordination = False
    current = None
    for line in visible_lines(text):
        if line.startswith("## "):
            in_coordination = line == "## Epic Coordination"
            current = None
        elif line.startswith("### "):
            current = line[4:].strip() if in_coordination else None
            if current in open_ids:
                if current in sections:
                    raise ValueError(f"Duplicate epic coordination: {current}")
                sections[current] = []
        elif current in sections and line.strip():
            sections[current].append(line)
    return "\n".join(
        "<tr>" + cell(epic["id"], "id") + cell("\n".join(sections.get(epic["id"], [])) or "No coordination recorded.", "coordination") + "</tr>"
        for epic in epics
    )


def marker(record_id: str, label: str) -> str:
    return '<td class="done"><input type="checkbox" data-record="' + html.escape(record_id, quote=True) + '" aria-label="' + html.escape(f"Mark {record_id} {label} reviewed", quote=True) + '"></td>'


def empty_row(columns: int, message: str) -> str:
    return f'<tr><td colspan="{columns}">{html.escape(message)}</td></tr>'


def cell(value: str, class_name: str = "") -> str:
    class_attr = f' class="{class_name}"' if class_name else ""
    return f"<td{class_attr}>{html.escape(value or '—')}</td>"


def task_rows(tasks: list[dict[str, str]]) -> str:
    order = {"Now": 0, "Next": 1, "Parked": 2, "Later": 3, "Other": 4}
    rows = []
    for task in sorted(tasks, key=lambda item: (order.get(item["section"], 9), item["id"])):
        state = task.get("Status", task["section"])
        next_action = task.get("Next Action") or task.get("Resume When") or task.get("Plan Review Notes") or "—"
        rows.append(
            "<tr>"
            + marker(task["id"], "task")
            + cell(task["id"], "id")
            + cell(task["name"])
            + cell(state)
            + cell(task.get("Stage", "—"))
            + cell(task.get("Priority", "—"))
            + cell(task.get("Epic", "—"))
            + cell(task.get("Plan Status", "—"))
            + cell(task.get("Goal", "—"))
            + cell(next_action)
            + "</tr>"
        )
    return "\n".join(rows) or empty_row(10, "No unfinished tasks.")


def plan_rows(tasks: list[dict[str, str]]) -> str:
    rows = []
    for task in sorted(tasks, key=lambda item: item["id"]):
        if not task.get("Plan Reference"):
            continue
        rows.append(
            "<tr>"
            + marker(task["id"], "plan")
            + cell(task["id"], "id")
            + cell(task["name"])
            + cell(task.get("Status", task["section"]))
            + cell(task.get("Stage", "—"))
            + cell(task.get("Plan Status", "—"))
            + cell(task.get("Plan Type", "—"))
            + cell(task.get("Formulation Status", "—"))
            + cell(task.get("Plan Approval Evidence", "—"))
            + cell(task.get("Plan Reference", "—"))
            + "</tr>"
        )
    return "\n".join(rows) or empty_row(10, "No current plans.")


def epic_rows(epics: list[dict[str, str]]) -> str:
    rows = []
    for epic in sorted(epics, key=lambda item: item["id"]):
        rows.append(
            "<tr>"
            + marker(epic["id"], "epic")
            + cell(epic["id"], "id")
            + cell(epic["name"])
            + cell(epic.get("Progress", "—"))
            + cell(epic.get("Formulation Status", "—"))
            + cell(epic.get("Goal", "—"))
            + cell(epic.get("Completion Criteria", "—"))
            + "</tr>"
        )
    return "\n".join(rows) or empty_row(7, "No open epics.")


def render(timestamp: str, source_list: str, snapshot: str, epics: list[dict[str, str]], tasks: list[dict[str, str]], coordination: str) -> str:
    source_list = html.escape(source_list)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Backlog review — {timestamp}</title>
<style>
:root {{ --ink:#18212b; --line:#cbd5df; --head:#173f5f; --muted:#52606d; }}
body {{ margin:36px auto 64px; max-width:1500px; padding:0 28px; font:14px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif; color:var(--ink); }}
h1 {{ margin:0 0 6px; font-size:28px; }} h2 {{ margin:38px 0 8px; font-size:21px; }} p {{ color:var(--muted); }}
.note {{ padding:12px 16px; margin:18px 0; border-left:4px solid #2d6a9f; background:#f4f8fb; color:var(--ink); }}
button {{ margin:8px 0 12px; padding:8px 13px; border:0; border-radius:5px; color:#fff; background:#1769aa; font:inherit; font-weight:600; cursor:pointer; }}
.status {{ margin-left:10px; color:var(--muted); }} table {{ width:100%; border-collapse:collapse; table-layout:fixed; }}
th,td {{ border:1px solid var(--line); padding:9px 10px; vertical-align:top; text-align:left; overflow-wrap:anywhere; }} th {{ background:var(--head); color:#fff; }} tr:nth-child(even) td {{ background:#f8fafb; }}
tr.completed td {{ color:#77828b; background:#e9ecef !important; text-decoration:line-through; }} tr.completed td:first-child,tr.completed td:nth-child(2) {{ text-decoration:none; }}
.done {{ width:42px; text-align:center; }} .id {{ width:7%; font-weight:700; white-space:nowrap; }} input[type=checkbox] {{ width:18px; height:18px; accent-color:#64748b; cursor:pointer; }}
.table-scroll {{ overflow-x:auto; }} table {{ min-width:900px; }} .coordination {{ white-space:pre-wrap; }}
@media (max-width:600px) {{ body {{ margin-top:20px; padding:0 12px; }} }}
@media print {{ button,.status {{ display:none; }} body {{ margin:18px; max-width:none; }} }}
</style></head><body>
<h1>Backlog, epic, and plan review</h1>
<p>Generated: <strong>{html.escape(timestamp)}</strong> · Sources: {source_list}</p>
<div class="note"><strong>Personal review markers:</strong> checking a row turns it gray without changing task completion, acceptance, or the project backlog. Browser-local storage is best-effort; when unavailable, markers last only for this page visit. Use <strong>Copy table</strong> for table-aware applications such as desktop OneNote. This dated snapshot does not authenticate approvals or validate the full governance contract.</div>
<h2>Open epics</h2><button data-copy="epics">Copy table</button><span id="epics-status" class="status" aria-live="polite"></span>
<table id="epics"><thead><tr><th class="done">Reviewed</th><th class="id">ID</th><th>Name</th><th>Progress</th><th>Formulation</th><th>Goal</th><th>Completion criteria</th></tr></thead><tbody>{epic_rows(epics)}</tbody></table>
<h2>Unfinished tasks</h2><button data-copy="tasks">Copy table</button><span id="tasks-status" class="status" aria-live="polite"></span>
<table id="tasks"><thead><tr><th class="done">Reviewed</th><th class="id">ID</th><th>Name</th><th>Status</th><th>Stage</th><th>Priority</th><th>Epic</th><th>Plan status</th><th>Goal</th><th>Next action / resume condition</th></tr></thead><tbody>{task_rows(tasks)}</tbody></table>
<h2>Current plan states (lightweight and detailed)</h2><button data-copy="plans">Copy table</button><span id="plans-status" class="status" aria-live="polite"></span>
<table id="plans"><thead><tr><th class="done">Reviewed</th><th class="id">Task</th><th>Name</th><th>Status</th><th>Stage</th><th>Plan status</th><th>Plan type</th><th>Formulation</th><th>Plan approval evidence</th><th>Plan reference</th></tr></thead><tbody>{plan_rows(tasks)}</tbody></table>
<h2>Open-epic coordination</h2>
<table id="coordination"><thead><tr><th class="id">Epic</th><th>Milestones, next action, and open issues</th></tr></thead><tbody>{coordination or empty_row(2, "No open-epic coordination available.")}</tbody></table>
<script>
function wire(table) {{
  const wrapper=document.createElement('div'); wrapper.className='table-scroll';
  wrapper.tabIndex=0; wrapper.setAttribute('role','region'); wrapper.setAttribute('aria-label',table.id+' table');
  table.before(wrapper); wrapper.append(table);
  table.querySelectorAll('tbody tr').forEach(row=>{{
    const box=row.querySelector('input'); if(!box)return;
    const key='backlog-html-review-{snapshot}-'+table.id+'-'+box.dataset.record;
    try {{ box.checked=localStorage.getItem(key)==='true'; }} catch(_) {{}}
    row.classList.toggle('completed',box.checked);
    box.addEventListener('change',()=>{{
      try {{ localStorage.setItem(key,String(box.checked)); }} catch(_) {{}}
      row.classList.toggle('completed',box.checked);
    }});
  }});
}}
async function copy(id) {{
  const table=document.getElementById(id), status=document.getElementById(id+'-status'), clone=table.cloneNode(true);
  clone.querySelectorAll('input').forEach((box,index)=>box.replaceWith(document.createTextNode(table.querySelectorAll('input')[index].checked?'✓':'')));
  const text=Array.from(clone.rows).map(row=>Array.from(row.cells).map(cell=>cell.textContent.replace(/\\s+/g,' ').trim()).join('\\t')).join('\\n');
  try {{
    if(!navigator.clipboard||!window.ClipboardItem) throw new Error();
    await navigator.clipboard.write([new ClipboardItem({{'text/html':new Blob([clone.outerHTML],{{type:'text/html'}}),'text/plain':new Blob([text],{{type:'text/plain'}})}})]);
    status.textContent='Copied. Paste into your destination application.';
  }} catch(_) {{
    const range=document.createRange(), selection=getSelection(); range.selectNode(table); selection.removeAllRanges(); selection.addRange(range);
    let copied=false; try {{ copied=document.execCommand('copy'); }} catch(_) {{}}
    status.textContent=copied?'Copied. Paste into your destination application.':'Copy unavailable. Table selected; use your browser’s Copy command.';
    if(copied) selection.removeAllRanges();
  }}
}}
document.querySelectorAll('table').forEach(wire);
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',()=>copy(button.dataset.copy)));
</script></body></html>"""


def read_source(root: Path, relative: str, required: bool = True) -> str | None:
    path = root
    for part in Path(relative).parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Source symlinks are not read: {relative}")
    if not path.exists() and not required:
        return None
    if not path.is_file():
        raise ValueError(f"Expected a regular source file: {relative}")
    return path.read_text(encoding="utf-8")


def generate(root: Path, output: Path | None = None) -> Path:
    root = root.resolve()
    backlog_text = read_source(root, "BACKLOG.md")
    executive_text = read_source(root, "plans/000_EXECUTIVE_PLAN.md", required=False)
    epics, tasks = parse_records(backlog_text)
    coordination = coordination_rows(executive_text or "", epics)
    now = dt.datetime.now().astimezone()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z (%z)")
    sources = "BACKLOG.md" + ("; plans/000_EXECUTIVE_PLAN.md" if executive_text is not None else "")
    snapshot = hashlib.sha256((str(root) + backlog_text + (executive_text or "") + now.isoformat()).encode()).hexdigest()[:24]
    output = output or Path("outputs") / f"backlog-review-{now.strftime('%Y%m%d-%H%M%S-%f')}.html"
    if not output.is_absolute():
        output = root / output
    if output.suffix.lower() != ".html":
        raise ValueError("Output must have an .html extension; source documents are never overwritten.")
    if output.exists() or output.is_symlink():
        raise ValueError(f"Output already exists; choose a new filename: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(render(timestamp, sources, snapshot, epics, tasks, coordination))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        output = generate(args.project_root, args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(output)


if __name__ == "__main__":
    main()
