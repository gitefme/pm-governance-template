import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.docs_check import (CHECKPOINT_FIELDS, collect_warnings, governance_markdown_paths, main, parse_tasks, validate, visible_text)  # noqa: E402


FIXTURES = Path(__file__).parent / "fixtures"
VALID_FIXTURE = FIXTURES / "valid"
INVALID_CASES = FIXTURES / "invalid_cases.json"
VALID_CASES = FIXTURES / "valid_cases.json"


class DocumentationCheckTests(unittest.TestCase):
    def fixture_copy(self, temporary_root: Path) -> Path:
        target = temporary_root / "repository"
        shutil.copytree(VALID_FIXTURE, target)
        return target

    def apply_case(self, root: Path, case: dict):
        if case.get("complete_task"):
            backlog_path = root / "BACKLOG.md"
            backlog = backlog_path.read_text(encoding="utf-8")
            marker = "- [ ] T-101 Valid fixture task\n"
            start = backlog.index(marker)
            record = backlog[start:]
            record = record.replace(marker, "- [x] T-101 Valid fixture task\n", 1)
            record = record.replace("  - Status: Now\n", "  - Status: Done\n", 1)
            record = record.replace("  - Stage: Implementation\n", "", 1)
            record = re.sub(r"  - Remaining Work: .*", "  - Remaining Work: None", record)
            record = re.sub(r"  - Next Action: .*", "  - Next Action: None", record)
            record = record.replace("  - Plan Status: confirmed\n", "  - Plan Status: implemented\n", 1)
            record = record.replace(
                "2026-08-14-1200_T-101_confirmed_fixture-plan.md",
                "2026-08-14-1200_T-101_implemented_fixture-plan.md",
            )
            backlog = backlog[:start] + "No selected tasks.\n"
            backlog = backlog.replace("- Completed task count: 0", "- Completed task count: 1")
            backlog = backlog.replace(
                "- T-101 — `Implementation`.",
                "No tasks are in `Now`.",
            )
            backlog = backlog.replace(
                "- Near term: T-101 Valid fixture task.",
                "No planning horizons exist because no unfinished formal tasks remain.",
            )
            backlog_path.write_text(backlog, encoding="utf-8")

            done_path = root / "BACKLOG_DONE.md"
            done = done_path.read_text(encoding="utf-8")
            done = done.replace("No completed formal tasks.", f"### 2026\n\n{record.rstrip()}")
            done_path.write_text(done + "\n", encoding="utf-8")

            plan = root / "plans/2026-08-14-1200_T-101_confirmed_fixture-plan.md"
            plan.write_text(
                plan.read_text(encoding="utf-8").replace(
                    "- Status: `confirmed`",
                    "- Status: `implemented`",
                ),
                encoding="utf-8",
            )
            plan.rename(root / "plans/2026-08-14-1200_T-101_implemented_fixture-plan.md")
            executive_path = root / "plans/000_EXECUTIVE_PLAN.md"
            executive = executive_path.read_text(encoding="utf-8")
            executive = executive.replace("- `Now`: T-101.", "- `Now`: none.")
            executive = executive.replace(
                "T-101_confirmed_fixture-plan.md",
                "T-101_implemented_fixture-plan.md",
            ).replace("T-101 — `confirmed`", "T-101 — `implemented`")
            executive_path.write_text(executive, encoding="utf-8")
        for replacement in case.get("replace", []):
            path = root / replacement["path"]
            original = path.read_text(encoding="utf-8")
            self.assertIn(replacement["old"], original, case["name"])
            path.write_text(
                original.replace(replacement["old"], replacement["new"], 1),
                encoding="utf-8",
            )
        for relative, addition in case.get("append", {}).items():
            path = root / relative
            path.write_text(path.read_text(encoding="utf-8") + addition, encoding="utf-8")
        for source, target in case.get("copy", {}).items():
            shutil.copyfile(root / source, root / target)
        for source, target in case.get("rename", {}).items():
            (root / source).rename(root / target)
        for relative in case.get("delete", []):
            (root / relative).unlink()


    def change(self, root, relative, old, new):
        path = root / relative
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1))

    def field(self, root, name, value, filename="BACKLOG.md"):
        path = root / filename
        text, count = re.subn(rf"^  - {re.escape(name)}: .*\n", "" if value is None else f"  - {name}: {value}\n", path.read_text(), flags=re.M)
        self.assertEqual(1, count, name)
        path.write_text(text)

    def add_tasks(self, root, count):
        path = root / "BACKLOG.md"
        text = path.read_text()
        record = text[text.index("- [ ] T-101 Valid fixture task"):]
        record = record.replace("Plan Type: Detailed", "Plan Type: Lightweight")
        record = re.sub(r"  - Plan Reference: .*", "  - Plan Reference: embedded in this task", record)
        record = record.replace("Stage: Implementation", "Stage: Verification")
        for number in range(102, 101 + count):
            text += "\n" + record.replace("T-101", f"T-{number}")
        text = text.replace("- T-101 — `Implementation`.", "- T-101 — `Implementation`." + "".join(f"\n- T-{number} — `Verification`." for number in range(102, 101 + count)))
        text = text.replace("- Near term: T-101 Valid fixture task.", "- Near term: " + ", ".join(f"T-{number}" for number in range(101, 101 + count)) + ".")
        path.write_text(text)
        self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- `Now`: T-101.", "- `Now`: " + ", ".join(f"T-{number}" for number in range(101, 101 + count)) + ".")

    def add_epic(self, root):
        record = """- [ ] E-001 Fixture epic
  - Revision: 1
  - Formulation Status: confirmed
  - Formulation Evidence: Synthetic user confirmation, 2026-09-24.
  - Progress: In progress
  - Goal: Bounded integrated outcome.
  - Scope: Fixture work.
  - Scope Exclusions: Runtime behavior.
  - Completion Criteria: Combined acceptance.
  - Coordination Plan: [Coordination](plans/000_EXECUTIVE_PLAN.md#e-001)"""
        self.change(root, "BACKLOG.md", "No formal epics.", record)
        self.change(root, "BACKLOG.md", "  - Source: test fixture\n", "  - Source: test fixture\n  - Epic: E-001\n")
        self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- Open epics: none.", "- Open epics: E-001.")
        self.change(root, "plans/000_EXECUTIVE_PLAN.md", "No formal epics.", "### E-001\n\n- Next Action: Verify integration.\n- Open Issues: Acceptance pending.\n- [ ] M1 — Integrated acceptance. Tasks: T-101.")

    def archive_epic(self, root):
        text = (root / "BACKLOG.md").read_text()
        record = text.split("## Epics\n\n", 1)[1].split("\n\n## ", 1)[0]
        self.change(root, "BACKLOG.md", record, "No formal epics.")
        record = record.replace("- [ ] E-001", "- [x] E-001").replace("Progress: In progress", "Progress: Done")
        record += "\n  - Completion Evidence: [Acceptance](PROJECT_LOG.md#fixture-acceptance)"
        (root / "PROJECT_LOG.md").write_text("# Project Log\n\n## Fixture acceptance\n\nSynthetic integrated acceptance.\n")
        self.change(root, "BACKLOG_DONE.md", "No completed epics.", "### 2026\n\n" + record)
        self.change(root, "BACKLOG.md", "Completed epic count: 0", "Completed epic count: 1")
        self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- Open epics: E-001.", "- Open epics: none.")

    def test_multiple_now_and_warning_only_wip(self):
        for count in (1, 2, 3, 4):
            with self.subTest(count=count), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary))
                self.add_tasks(root, count)
                before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*.md")}
                self.assertEqual([], validate(root))
                self.assertEqual(count > 3, bool(collect_warnings(root)))
                with patch.object(sys, "argv", ["docs_check.py", str(root)]), patch("sys.stdout", new_callable=io.StringIO) as output:
                    self.assertEqual(0, main())
                    self.assertEqual(count > 3, "Warning:" in output.getvalue())
                self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*.md")})
                self.change(root, "BACKLOG.md", "WIP advisory limit: 3", "WIP advisory limit: 5")
                self.assertEqual([], collect_warnings(root))

    def test_invalid_wip_and_version_markers(self):
        cases = [("BACKLOG.md", "WIP advisory limit: 3", "WIP advisory limit: " + value, "positive WIP") for value in ("0", "-1", "1.5", "three", "", "3\n- WIP advisory limit: 3")]
        cases += [("WORKFLOW.md", "Governance version: 2", value, "unfenced Governance version") for value in ("Governance version: 1", "", "Governance version: 2\nGovernance version: 2", "```md\nGovernance version: 2\n```", "~~~md\nGovernance version: 2\n~~~", "<!--\nGovernance version: 2\n-->")]
        for path, old, new, expected in cases:
            with self.subTest(new=new), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary))
                self.change(root, path, old, new)
                self.assertIn(expected, "\n".join(validate(root)))

    def test_checkpoints_reject_missing_blank_invalid_or_unassigned_values(self):
        cases = [(field, value, "requires checkpoint field " + field) for field in CHECKPOINT_FIELDS for value in (None, "")]
        cases += [("Checkpoint Updated", value, "calendar date") for value in ("2026-02-30", "2026-9-2", "unknown")]
        cases.append(("Executor", "Unassigned", "assigned Executor"))
        for field, value, expected in cases:
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary))
                self.field(root, field, value)
                self.assertIn(expected, "\n".join(validate(root)))

    def test_parking_and_resuming_verification_preserves_phase(self):
        case = next(case for case in json.loads(VALID_CASES.read_text()) if case["name"] == "intentionally parked confirmed task")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            self.apply_case(root, case)
            self.field(root, "Resume Stage", "Verification")
            self.assertEqual([], validate(root))
            self.field(root, "Status", "Now")
            self.field(root, "Stage", "Verification")
            self.field(root, "Resume When", None)
            self.field(root, "Resume Stage", None)
            self.change(root, "BACKLOG.md", "## Parked", "## Now")
            self.change(root, "BACKLOG.md", "No tasks are in `Now`.", "- T-101 — `Verification`.")
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- `Now`: none.", "- `Now`: T-101.")
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "Confirmed plans stored for later: T-101.", "Confirmed plans stored for later: none.")
            self.assertEqual([], validate(root))

    def test_parked_checkpoint_needs_a_valid_resume_stage(self):
        case = next(case for case in json.loads(VALID_CASES.read_text()) if case["name"] == "intentionally parked confirmed task")
        for value in (None, "Ready"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.apply_case(root, case)
                self.field(root, "Resume Stage", value)
                self.assertIn("Resume Stage", "\n".join(validate(root)))

    def test_authority_and_revision_contradictions_fail(self):
        cases = [("Revision", "0", "positive Revision"), ("Revision", "2", "Task Revision does not match"), ("Formulation Status", "unknown", "Formulation Status"), ("Formulation Evidence", None, "Formulation Evidence"), ("Plan Approval Evidence", None, "Plan Approval Evidence"), ("Activation Evidence", None, "Activation Evidence"), ("Formulation Status", "proposed", "cannot be Ready, active, approved")]
        for field, value, expected in cases:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.field(root, field, value)
                self.assertIn(expected, "\n".join(validate(root)))
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            with (root / "BACKLOG.md").open("a") as stream:
                stream.write("  - Review Status: Awaiting final user review\n")
            self.assertIn("generic Review Status", "\n".join(validate(root)))

    def test_explicit_write_first_pending_proposal_is_not_approved(self):
        case = next(case for case in json.loads(VALID_CASES.read_text()) if case["name"] == "pending plan at Plan review")
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.apply_case(root, case)
            self.field(root, "Formulation Status", "proposed")
            self.field(root, "Formulation Evidence", None)
            with (root / "BACKLOG.md").open("a") as stream:
                stream.write("  - Storage Authorization: Synthetic user instruction to prepare this package before review.\n")
            self.assertEqual([], validate(root))
            self.field(root, "Storage Authorization", None)
            self.assertIn("Storage Authorization", "\n".join(validate(root)))

    def test_replanning_preserves_superseded_revision_and_checkpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            plan = root / "plans/2026-08-14-1200_T-101_confirmed_fixture-plan.md"
            old = plan.read_text()
            previous = plan.with_name(plan.name.replace("confirmed", "superseded"))
            previous.write_text(old.replace("`confirmed`", "`superseded`"))
            replacement = plan.with_name("2026-09-24-1200_T-101_draft_revised-plan.md")
            replacement.write_text(old.replace("`confirmed`", "`draft`").replace("Task Revision: 1", "Task Revision: 2"))
            plan.unlink()
            self.field(root, "Revision", "2")
            self.field(root, "Status", "Parked")
            self.field(root, "Stage", "Plan drafting")
            self.field(root, "Plan Status", "draft")
            self.field(root, "Plan Approval Evidence", None)
            self.field(root, "Plan Reference", f"[Revised plan](plans/{replacement.name})")
            self.change(root, "BACKLOG.md", "## Now", "## Parked")
            self.change(root, "BACKLOG.md", "- T-101 — `Implementation`.", "No tasks are in `Now`.")
            with (root / "BACKLOG.md").open("a") as stream:
                stream.write("  - Resume When: Revised plan is approved and activated.\n")
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- `Now`: T-101.", "- `Now`: none.")
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", f"- T-101 — `confirmed` — [{plan.name}]({plan.name})", f"- T-101 — `superseded` — [{previous.name}]({previous.name})\n- T-101 — `draft` — [{replacement.name}]({replacement.name})")
            self.assertEqual([], validate(root))
            self.assertEqual(old.replace("`confirmed`", "`superseded`"), previous.read_text())
            self.assertIn("Completed Work: None yet.", (root / "BACKLOG.md").read_text())

    def test_epic_membership_and_open_coordination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.add_tasks(root, 2); self.add_epic(root)
            self.assertEqual([], validate(root))
            self.assertEqual(2, len(parse_tasks(root / "BACKLOG.md")))
            self.assertEqual([], collect_warnings(root))

    def test_epic_schema_and_milestone_failures(self):
        cases = [
            ("BACKLOG.md", "  - Epic: E-001", "  - Epic: E-999", "one existing E-###"),
            ("BACKLOG.md", "  - Epic: E-001", "  - Epic: E-001, E-002", "one existing E-###"),
            ("BACKLOG.md", "  - Progress: In progress", "  - Progress: In progress\n  - Epic: E-002", "task/nesting field Epic"),
            ("BACKLOG.md", "  - Progress: In progress", "  - Progress: In progress\n  - Status: Now", "task/nesting field Status"),
            ("BACKLOG.md", "  - Progress: In progress", "  - Progress: Paused", "Paused requires Resume When"),
            ("BACKLOG.md", "  - Scope: Fixture work.", "  - Scope:", "E-001 requires Scope"),
            ("BACKLOG.md", "  - Scope: Fixture work.", "  - Scope: Fixture work.\n  - Scope: Contradiction.", "E-001 repeats Scope"),
            ("BACKLOG.md", "#e-001)", "#e-999)", "executive-plan anchor"),
            ("plans/000_EXECUTIVE_PLAN.md", "### E-001", "### E-999", "coordination block"),
            ("plans/000_EXECUTIVE_PLAN.md", "- Next Action: Verify integration.", "- Next Action:", "non-empty Next Action"),
            ("plans/000_EXECUTIVE_PLAN.md", "Tasks: T-101.", "Tasks: T-999.", "unknown task T-999"),
            ("plans/000_EXECUTIVE_PLAN.md", "Tasks: T-101.", "Tasks: T-101 or T-999.", "malformed Tasks"),
            ("plans/000_EXECUTIVE_PLAN.md", "- [ ] M1", "- [x] M1", "requires T-101 to be Done"),
            ("plans/000_EXECUTIVE_PLAN.md", "- [ ] M1", "- [ ] M0", "well-formed milestone"),
            ("plans/000_EXECUTIVE_PLAN.md", "- [ ] M1 — Integrated acceptance. Tasks: T-101.", "- [ ] M1 — First.\n- [ ] M1 — Duplicate.", "repeats a milestone ID"),
        ]
        for path, old, new, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.add_epic(root)
                self.change(root, path, old, new)
                self.assertIn(expected, "\n".join(validate(root)))

    def test_valid_epic_closure_and_premature_closure(self):
        for premature in (False, True):
            with self.subTest(premature=premature), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.add_epic(root)
                if not premature:
                    self.apply_case(root, {"complete_task": True})
                self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- [ ] M1", "- [x] M1")
                self.archive_epic(root)
                issues = validate(root)
                if premature:
                    self.assertIn("all members Done", "\n".join(issues))
                else:
                    self.assertEqual([], issues)
                    self.change(root, "BACKLOG_DONE.md", "#fixture-acceptance", "#missing-evidence")
                    self.assertIn("broken Markdown anchor", "\n".join(validate(root)))

    def test_epic_closure_requires_members_milestones_and_evidence(self):
        cases = [
            ("BACKLOG_DONE.md", "  - Epic: E-001\n", "", "at least one member"),
            ("BACKLOG_DONE.md", "  - Completion Evidence: [Acceptance](PROJECT_LOG.md#fixture-acceptance)", "  - Completion Evidence: asserted", "Markdown-linked Completion Evidence"),
            ("plans/000_EXECUTIVE_PLAN.md", "- [x] M1", "- [ ] M1", "unchecked milestone"),
            ("BACKLOG.md", "Completed epic count: 1", "Completed epic count: 0", "Completed epic count must be 1"),
        ]
        for path, old, new, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.add_epic(root)
                self.apply_case(root, {"complete_task": True})
                self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- [ ] M1", "- [x] M1")
                self.archive_epic(root); self.change(root, path, old, new)
                self.assertIn(expected, "\n".join(validate(root)))

    def test_external_milestone_prerequisite_is_enforced(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.add_tasks(root, 2); self.add_epic(root)
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- [ ] M1 — Integrated acceptance. Tasks: T-101.", "- [x] M1 — External acceptance. Tasks: T-102.")
            self.assertIn("requires T-102 to be Done", "\n".join(validate(root)))

    def test_typed_prerequisite_gates(self):
        for field, must_fail in (("Planning Prerequisites", True), ("Implementation Prerequisites", True), ("Acceptance Prerequisites", False)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.add_tasks(root, 2)
                self.change(root, "BACKLOG.md", "  - Dependencies: None.\n", f"  - Dependencies: None.\n  - {field}: T-102\n")
                errors = validate(root)
                self.assertEqual(must_fail, bool(errors), errors)
                if must_fail:
                    self.assertIn("requires T-102 to be Done at this gate", "\n".join(errors))

    def test_unknown_cyclic_and_untyped_dependencies_fail(self):
        cases = [
            ("  - Implementation Prerequisites: T-999", "unknown task T-999"),
            ("  - Acceptance Prerequisites: T-101", "prerequisite cycle"),
            ("  - Acceptance Prerequisites: T-102, T-102", "repeats a task ID"),
            ("  - Acceptance Prerequisites: T-102 or T-101", "comma-separated task ID list"),
        ]
        for line, expected in cases:
            with self.subTest(line=line), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.add_tasks(root, 2)
                self.change(root, "BACKLOG.md", "  - Dependencies: None.\n", "  - Dependencies: None.\n" + line + "\n")
                self.assertIn(expected, "\n".join(validate(root)))
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.add_tasks(root, 2)
            self.change(root, "BACKLOG.md", "  - Dependencies: None.\n", "  - Dependencies: None.\n  - Acceptance Prerequisites: T-102\n")
            with (root / "BACKLOG.md").open("a") as stream:
                stream.write("  - Planning Prerequisites: T-101\n")
            self.assertIn("prerequisite cycle", "\n".join(validate(root)))
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.field(root, "Dependencies", "T-999 must be complete.")
            self.assertIn("classified into typed prerequisites", "\n".join(validate(root)))

    def test_satisfied_prerequisites_pass_and_acceptance_gates_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.apply_case(root, {"complete_task": True})
            done = root / "BACKLOG_DONE.md"
            self.change(root, "BACKLOG_DONE.md", "  - Dependencies: None.\n", "  - Dependencies: None.\n  - Acceptance Prerequisites: T-999\n")
            self.assertIn("unknown task T-999", "\n".join(validate(root)))
            self.field(root, "Acceptance Prerequisites", "None", "BACKLOG_DONE.md")
            record = done.read_text().split("- [x] T-101", 1)[1].split("\n## ", 1)[0]
            record = "- [ ] T-102" + record
            record = record.replace("Status: Done", "Status: Now\n  - Stage: Implementation").replace("Plan Type: Detailed", "Plan Type: Lightweight").replace("Plan Status: implemented", "Plan Status: confirmed")
            record = re.sub(r"  - Plan Reference: .*", "  - Plan Reference: embedded in this task", record)
            record += "  - Planning Prerequisites: T-101\n  - Implementation Prerequisites: T-101\n"
            record = record.replace("Acceptance Prerequisites: None", "Acceptance Prerequisites: T-101")
            self.change(root, "BACKLOG.md", "No selected tasks.", record)
            self.change(root, "BACKLOG.md", "No tasks are in `Now`.", "- T-102 — `Implementation`.")
            self.change(root, "BACKLOG.md", "No planning horizons exist because no unfinished formal tasks remain.", "- Near term: T-102.")
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- `Now`: none.", "- `Now`: T-102.")
            self.assertEqual([], validate(root))

    def test_plan_metadata_and_fenced_examples_are_not_live(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            path = root / "plans/2026-08-14-1200_T-101_confirmed_fixture-plan.md"
            with path.open("a") as stream:
                stream.write("\n````md\n- Task ID: T-999\n```\n- Status: `draft`\n````\n")
            self.assertEqual([], validate(root))
            self.change(root, str(path.relative_to(root)), "- Task Revision: 1\n", "~~~\n- Task Revision: 1\n~~~\n")
            self.assertIn("positive Task Revision", "\n".join(validate(root)))

    def test_markdown_links_and_anchors(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            (root / "docs").mkdir()
            (root / "docs/Space Name.md").write_text("# Repeated\n\n# Repeated\n\n## Résumé Test\n\n<a id=\"stable\"></a>\n")
            readme = root / "README.md"
            with readme.open("a") as stream:
                stream.write('\n[Repeated](docs/Space%20Name.md#repeated-1)\n[Unicode](docs/Space%20Name.md#résumé-test)\n[Explicit](<docs/Space Name.md#stable>)\n[Local](#fixture-repository)\n')
            self.assertEqual([], validate(root))
            with readme.open("a") as stream:
                stream.write("\n[Missing](docs/Space%20Name.md#missing)\n[Local missing](#missing)\n")
            issues = validate(root)
            self.assertEqual(2, sum("broken Markdown anchor" in issue for issue in issues))

    def test_scanning_is_scoped_and_does_not_follow_private_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            outside = Path(temporary) / "private.md"; outside.write_text("[Broken](missing.md)")
            for relative in ("tmp/report.md", "outputs/report.md", ".secrets/private.md", "node_modules/readme.md"):
                path = root / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("[Broken](missing.md)")
            (root / "docs").mkdir()
            (root / "docs/linked.md").symlink_to(outside)
            (root / "docs/private-tree").symlink_to(outside.parent, target_is_directory=True)
            self.assertEqual([], validate(root))
            self.assertNotIn(root / "docs/linked.md", list(governance_markdown_paths(root)))
            (root / "ARCHITECTURE.md").unlink(); (root / "ARCHITECTURE.md").symlink_to(outside)
            original = Path.read_text
            def guarded(path, *args, **kwargs):
                if path.resolve() == outside:
                    raise AssertionError("followed a private symlink")
                return original(path, *args, **kwargs)
            with patch.object(Path, "read_text", guarded):
                self.assertIn("required governance document is missing", "\n".join(validate(root)))

    def test_optional_artifacts_require_complete_registration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            (root / "ROADMAP.md").write_text("# Roadmap\n\nOutcome projection.\n")
            self.assertIn("not registered: ROADMAP.md", "\n".join(validate(root)))
            row = "| Roadmap | [Roadmap](ROADMAP.md) | Product owner | Confirmed outcomes and tasks | Outcome changes | Replaced |"
            self.change(root, "WORKFLOW.md", "No optional artifacts adopted.", "| Artifact | Path | Owner | Inputs | Update When | Retire When |\n| --- | --- | --- | --- | --- | --- |\n" + row)
            self.assertEqual([], validate(root))
            with (root / "WORKFLOW.md").open("a") as stream:
                stream.write("\n" + row + "\n")
            self.assertIn("duplicate optional artifact", "\n".join(validate(root)))

    def test_legacy_done_history_does_not_need_retroactive_authority(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.apply_case(root, {"complete_task": True})
            for field in ("Revision", "Formulation Status", "Formulation Evidence", "Plan Approval Evidence", "Activation Evidence", *CHECKPOINT_FIELDS):
                self.field(root, field, None, "BACKLOG_DONE.md")
            plan = root / "plans/2026-08-14-1200_T-101_implemented_fixture-plan.md"
            plan.write_text(plan.read_text().replace("- Task Revision: 1\n", ""))
            self.assertEqual([], validate(root))

    def test_secret_guard_reads_git_names_only(self):
        from scripts.check_secret_paths import main as secret_main, sensitive_path
        from subprocess import CompletedProcess
        for name in (".env", "config/.env.production", "secrets/private.pem", ".secrets/token.txt", "keys/key.p12"):
            self.assertTrue(sensitive_path(name), name)
        for name in (".env.example", "deploy/.env.production.example", "src/app.py", ".secrets/.gitkeep"):
            self.assertFalse(sensitive_path(name), name)
        with patch("scripts.check_secret_paths.subprocess.run", return_value=CompletedProcess([], 0, b"src/app.py\0.env\0", b"")) as command, patch.object(Path, "read_text", side_effect=AssertionError("must not read content")), patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(1, secret_main([]))
            self.assertIn("--name-only", command.call_args.args[0])
        with patch("scripts.check_secret_paths.subprocess.run", return_value=CompletedProcess([], 0, b"src/app.py\0", b"")) as command, patch("sys.stdout", new_callable=io.StringIO):
            self.assertEqual(0, secret_main(["--tracked"]))
            self.assertEqual(["git", "ls-files", "--cached", "-z"], command.call_args.args[0])


    def test_unstarted_planning_and_implementation_gates_are_distinct(self):
        cases = json.loads(VALID_CASES.read_text())
        discussion = next(case for case in cases if case["name"] == "discussion without a plan")
        ready = next(case for case in cases if case["name"] == "confirmed plan at Ready")
        for case, field, expected_failure in ((discussion, "Planning Prerequisites", False), (ready, "Planning Prerequisites", True), (ready, "Implementation Prerequisites", False)):
            with self.subTest(case=case["name"], field=field), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.apply_case(root, case)
                text = (root / "BACKLOG.md").read_text()
                record = text[text.index("- [ ] T-101"):].replace("T-101", "T-102")
                # T-102 is an unstarted lightweight prerequisite, not already Done.
                record = re.sub(r"  - Plan Reference: .*", "  - Plan Reference: embedded in this task", record)
                record = record.replace("Plan Type: Detailed", "Plan Type: Lightweight")
                (root / "BACKLOG.md").write_text(text + "\n" + record)
                self.change(root, "BACKLOG.md", "- Near term: T-101 Valid fixture task.", "- Near term: T-101, T-102.")
                self.change(root, "BACKLOG.md", "  - Dependencies: None.\n", "  - Dependencies: None.\n  - " + field + ": T-102\n")
                if case == ready:
                    self.change(root, "plans/000_EXECUTIVE_PLAN.md", "Confirmed plans stored for later: T-101.", "Confirmed plans stored for later: T-101, T-102.")
                issues = validate(root)
                self.assertEqual(expected_failure, bool(issues), issues)
                if expected_failure:
                    self.assertIn("Planning Prerequisites requires T-102 to be Done", "\n".join(issues))

    def test_acceptance_prerequisite_blocks_closure_until_done(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.apply_case(root, {"complete_task": True})
            done = root / "BACKLOG_DONE.md"
            record = "- [ ] T-102" + done.read_text().split("- [x] T-101", 1)[1].split("\n## ", 1)[0]
            record = record.replace("Status: Done", "Status: Next\n  - Stage: Ready").replace("Plan Type: Detailed", "Plan Type: Lightweight").replace("Plan Status: implemented", "Plan Status: confirmed")
            record = re.sub(r"  - Plan Reference: .*", "  - Plan Reference: embedded in this task", record)
            self.change(root, "BACKLOG.md", "## Now\n\nNo selected tasks.", "## Next\n\n" + record)
            self.change(root, "BACKLOG.md", "No planning horizons exist because no unfinished formal tasks remain.", "- Near term: T-102.")
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "Confirmed plans stored for later: none.", "Confirmed plans stored for later: T-102.")
            self.change(root, "BACKLOG_DONE.md", "  - Dependencies: None.\n", "  - Dependencies: None.\n  - Acceptance Prerequisites: T-102\n")
            issues = validate(root)
            self.assertEqual(1, len(issues), issues)
            self.assertIn("Acceptance Prerequisites requires T-102 to be Done", issues[0])

    def test_duplicate_revision_summary_and_orphan_fields_fail(self):
        cases = [
            ("plans/2026-08-14-1200_T-101_confirmed_fixture-plan.md", "- Task Revision: 1\n", "- Task Revision: 1\n- Task Revision: 1\n", "exactly one positive Task Revision"),
            ("plans/000_EXECUTIVE_PLAN.md", "- `Now`: T-101.", "- `Now`: T-101, T-101.", "`Now` summary must be"),
            ("plans/000_EXECUTIVE_PLAN.md", "- `Now`: T-101.", "- `Now`: T-101 or some work.", "`Now` summary must be"),
            ("BACKLOG.md", "## Completed Work", "  - Status: Now\n\n## Completed Work", "orphan task/epic field"),
            ("BACKLOG.md", "- [ ] T-101", "  - [ ] T-101", "malformed or nested"),
        ]
        for path, old, new, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary)); self.change(root, path, old, new)
                self.assertIn(expected, "\n".join(validate(root)))

    def test_epic_pause_duplicate_identity_and_wrong_evidence_owner(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.add_epic(root)
            self.change(root, "BACKLOG.md", "Progress: In progress", "Progress: Paused\n  - Resume When: User resumes this outcome.")
            self.assertEqual([], validate(root))
            self.change(root, "BACKLOG.md", "Progress: Paused", "Progress: Planned")
            self.assertIn("only valid while Paused", "\n".join(validate(root)))
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.add_epic(root)
            body = (root / "BACKLOG.md").read_text().split("## Epics\n\n", 1)[1].split("\n\n## ", 1)[0]
            self.change(root, "BACKLOG.md", body, body + "\n\n" + body)
            self.assertIn("duplicate epic ID", "\n".join(validate(root)))
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary)); self.add_epic(root)
            self.apply_case(root, {"complete_task": True})
            self.change(root, "plans/000_EXECUTIVE_PLAN.md", "- [ ] M1", "- [x] M1")
            self.archive_epic(root)
            self.change(root, "BACKLOG_DONE.md", "PROJECT_LOG.md#fixture-acceptance", "README.md")
            self.assertIn("in a log or verification document", "\n".join(validate(root)))

    def test_setext_heading_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            path = root / "README.md"
            path.write_text(path.read_text() + "\nUnderlined heading\n------------------\n\n[Section](#underlined-heading)\n")
            self.assertEqual([], validate(root))

    def test_valid_fixture_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = self.fixture_copy(Path(temporary))
            self.assertEqual([], validate(root))

    def test_valid_lifecycle_variants_pass(self):
        cases = json.loads(VALID_CASES.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["name"]), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary))
                self.apply_case(root, case)
                self.assertEqual([], validate(root), case["name"])

    def test_invalid_fixtures_fail_for_the_expected_rule(self):
        cases = json.loads(INVALID_CASES.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["name"]), tempfile.TemporaryDirectory() as temporary:
                root = self.fixture_copy(Path(temporary))
                self.apply_case(root, case)
                issues = validate(root)
                rendered = "\n".join(issues)
                self.assertTrue(issues, f"{case['name']} unexpectedly passed")
                self.assertIn(case["expected"], rendered)


if __name__ == "__main__":
    unittest.main()
