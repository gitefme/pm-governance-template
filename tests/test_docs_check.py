import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from scripts.docs_check import validate  # noqa: E402


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
            record = record.replace("  - Plan Status: confirmed\n", "  - Plan Status: implemented\n", 1)
            record = record.replace(
                "2026-08-14-1200_T-101_confirmed_fixture-plan.md",
                "2026-08-14-1200_T-101_implemented_fixture-plan.md",
            )
            backlog = backlog[:start] + "No selected tasks.\n"
            backlog = backlog.replace("- Completed task count: 0", "- Completed task count: 1")
            backlog = backlog.replace(
                "T-101 is the single active task in `Now + Implementation`.",
                "No task is active. Keep at most one task in `Now`.",
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
