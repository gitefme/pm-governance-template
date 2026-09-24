"""Behavioral checks for portable backlog exports and non-overwriting installation."""

import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
GENERATOR = SKILLS / "backlog-html-review" / "scripts" / "generate_backlog_review_html.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


review = load_module("backlog_review", GENERATOR)
installer = load_module("skill_installer", ROOT / "scripts" / "install_skills.py")

BACKLOG = """# Backlog
## Task Template
````md
```md
- [ ] T-000 Ignore backtick example
  - Status: Now
```
````
~~~md
- [ ] T-099 Ignore tilde example
~~~
<!--
## Now
- [ ] T-098 Ignore comment
-->
## Epics
- [ ] E-001 Shared outcome
  - Progress: In progress
  - Formulation Status: confirmed
  - Goal: Combine both tasks
  - Completion Criteria: Integrated review
## Now
- [ ] T-101 First task
  - Status: Now
  - Stage: Implementation
  - Priority: P1
  - Epic: E-001
  - Plan Type: Lightweight
  - Plan Status: confirmed
  - Formulation Status: confirmed
  - Plan Approval Evidence: User approved revision 1 on 2026-09-24
  - Plan Reference: embedded in this task
  - Goal: First line
    continued goal
  - Next Action: Implement remaining scope
- [ ] T-102 Second task
  - Status: Now
  - Stage: Verification
  - Epic: E-001
  - Plan Type: Detailed
  - Plan Status: confirmed
  - Formulation Status: confirmed
  - Plan Reference: [Plan](plans/current.md)
  - Next Action: Verify changes
## Parked
- [ ] T-103 Deferred task
  - Status: Parked
  - Stage: Ready
  - Resume Stage: Verification
  - Resume When: Review target is available
## Next
- [ ] T-104 Proposed task
  - Status: Next
  - Stage: Plan review
  - Formulation Status: proposed
  - Plan Type: Lightweight
  - Plan Status: pending
  - Plan Reference: embedded in this task
## Unrelated Notes
  - Goal: Do not attach this to T-104
"""

EXECUTIVE = """# Executive Plan
## Epic Coordination
### E-001
- Next Action: Verify integration
- Open Issues: Required acceptance pending
- [ ] M1 — Combined result. Tasks: T-101, T-102.
### E-002
- Next Action: Archived epic must not appear
## Detailed Plan Files
Do not include historical plan listings.
"""


class BacklogReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "BACKLOG.md").write_text(BACKLOG, encoding="utf-8")
        (self.root / "plans").mkdir()
        (self.root / "plans" / "000_EXECUTIVE_PLAN.md").write_text(EXECUTIVE, encoding="utf-8")

    def test_empty_template_does_not_export_examples(self):
        epics, tasks = review.parse_records((ROOT / "BACKLOG.md").read_text())
        self.assertEqual((epics, tasks), ([], []))
        (self.root / "BACKLOG.md").write_text((ROOT / "BACKLOG.md").read_text())
        text = review.generate(self.root).read_text()
        self.assertIn("No unfinished tasks.", text)
        self.assertIn("No open epics.", text)
        self.assertIn("No current plans.", text)

    def test_multiple_now_tasks_and_nonactive_records(self):
        epics, tasks = review.parse_records(BACKLOG)
        self.assertEqual([record["id"] for record in epics], ["E-001"])
        self.assertEqual([record["id"] for record in tasks], ["T-101", "T-102", "T-103", "T-104"])
        self.assertEqual(tasks[1]["Stage"], "Verification")
        self.assertEqual(tasks[2]["Resume Stage"], "Verification")
        self.assertEqual(tasks[0]["Goal"], "First line continued goal")
        self.assertNotIn("Goal", tasks[3])

    def test_export_reads_coordination_and_preserves_source_bytes(self):
        before = {path: path.read_bytes() for path in self.root.rglob("*.md")}
        text = review.generate(self.root).read_text()
        self.assertIn("Lightweight", text)
        self.assertIn("Detailed", text)
        self.assertIn("User approved revision 1", text)
        self.assertIn("proposed", text)
        self.assertIn("Verify integration", text)
        self.assertIn("Combined result", text)
        self.assertNotIn("Archived epic must not appear", text)
        self.assertNotIn("historical plan listings", text)
        self.assertNotIn("Review status", text)
        self.assertNotIn("T-000", text)
        self.assertIn("plans/000_EXECUTIVE_PLAN.md", text)
        self.assertEqual(before, {path: path.read_bytes() for path in self.root.rglob("*.md")})

    def test_optional_executive_source_is_not_claimed_when_missing(self):
        (self.root / "plans" / "000_EXECUTIVE_PLAN.md").unlink()
        text = review.generate(self.root).read_text()
        self.assertNotIn("plans/000_EXECUTIVE_PLAN.md", text)
        self.assertIn("No coordination recorded.", text)

    def test_duplicate_fields_ids_and_conflicting_status_fail(self):
        variants = [
            BACKLOG.replace("  - Priority: P1", "  - Priority: P1\n  - Priority: P2"),
            BACKLOG.replace("T-102 Second", "T-101 Second"),
            BACKLOG.replace("T-101 First task\n  - Status: Now", "T-101 First task\n  - Status: Next"),
        ]
        for text in variants:
            with self.subTest(text=text), self.assertRaises(ValueError):
                review.parse_records(text)

    def test_html_escapes_user_text(self):
        (self.root / "BACKLOG.md").write_text(BACKLOG.replace("First task", '<script>alert("unsafe")</script> & task'))
        text = review.generate(self.root).read_text()
        self.assertIn("&lt;script&gt;", text)
        self.assertNotIn('<script>alert("unsafe")', text)

    def test_existing_output_and_source_overwrite_refused(self):
        existing = self.root / "existing.html"
        existing.write_text("keep me")
        for output in (existing, Path("BACKLOG.md")):
            with self.subTest(output=output), self.assertRaises(ValueError):
                review.generate(self.root, output)
        self.assertEqual(existing.read_text(), "keep me")
        self.assertEqual((self.root / "BACKLOG.md").read_text(), BACKLOG)

    def test_relative_output_and_unique_defaults(self):
        chosen = review.generate(self.root, Path("exports/chosen.html"))
        self.assertEqual(chosen, self.root / "exports" / "chosen.html")
        first, second = review.generate(self.root), review.generate(self.root)
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_file() and second.is_file())

    def test_source_symlink_is_not_followed(self):
        original = self.root / "BACKLOG.md"
        original.rename(self.root / "elsewhere.md")
        original.symlink_to(self.root / "elsewhere.md")
        with self.assertRaisesRegex(ValueError, "symlinks"):
            review.generate(self.root)

    def test_plans_directory_symlink_is_not_followed(self):
        (self.root / "plans").rename(self.root / "elsewhere")
        (self.root / "plans").symlink_to(self.root / "elsewhere", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            review.generate(self.root)

    def test_missing_backlog_fails_without_export(self):
        (self.root / "BACKLOG.md").unlink()
        with self.assertRaises(ValueError):
            review.generate(self.root)
        self.assertFalse((self.root / "outputs").exists())

    def test_standalone_copied_skill_runs_from_another_directory(self):
        skill = self.root / "portable skill"
        shutil.copytree(SKILLS / "backlog-html-review", skill)
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(skill / "scripts" / GENERATOR.name), "--project-root", str(self.root)],
            cwd=skill, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(Path(result.stdout.strip()).is_file())


class SkillInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def test_install_preserves_complete_skill_packages(self):
        destinations = installer.install(self.root)
        for destination in destinations:
            for path in (SKILLS / destination.name).rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    self.assertEqual(path.read_bytes(), (destination / path.relative_to(SKILLS / destination.name)).read_bytes())

    def test_conflict_does_not_partially_install_or_overwrite(self):
        existing = self.root / ".agents" / "skills" / "backlog-html-review"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("local customization")
        with self.assertRaisesRegex(ValueError, "already exists"):
            installer.install(self.root)
        self.assertEqual((existing / "SKILL.md").read_text(), "local customization")
        self.assertFalse((existing.parent / "bkl-sh").exists())

    def test_target_symlink_is_not_followed(self):
        elsewhere = self.root / "elsewhere"
        elsewhere.mkdir()
        (self.root / ".agents").symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "ordinary directory"):
            installer.install(self.root)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_installer_cli_from_fresh_copy_and_installed_generator(self):
        template = self.root / "fresh template"
        target = self.root / "target project"
        (template / "scripts").mkdir(parents=True)
        target.mkdir()
        shutil.copytree(SKILLS, template / "skills")
        shutil.copy2(ROOT / "scripts" / "install_skills.py", template / "scripts")
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(template / "scripts" / "install_skills.py"), "--project-root", str(target)],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        (target / "BACKLOG.md").write_text(BACKLOG)
        command = target / ".agents" / "skills" / "backlog-html-review" / "scripts" / GENERATOR.name
        generated = subprocess.run(
            [sys.executable, "-I", "-B", str(command), "--project-root", str(target)],
            cwd=self.root, capture_output=True, text=True,
        )
        self.assertEqual(generated.returncode, 0, generated.stderr)
        self.assertIn("T-101", Path(generated.stdout.strip()).read_text())


if __name__ == "__main__":
    unittest.main()
