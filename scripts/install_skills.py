#!/usr/bin/env python3
"""Copy bundled skills into a project's Codex discovery directory without replacing existing skills."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


SKILL_NAMES = ("bkl-sh", "backlog-html-review")


def install(project_root: Path, source: Path | None = None) -> list[Path]:
    source = source or Path(__file__).resolve().parents[1] / "skills"
    root = project_root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")
    target = root / ".agents" / "skills"
    for directory in (root / ".agents", target):
        if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
            raise ValueError(f"Expected an ordinary directory: {directory}")
    destinations = [target / name for name in SKILL_NAMES]
    # Check the entire request before creating either copy.
    for name, destination in zip(SKILL_NAMES, destinations):
        if not (source / name / "SKILL.md").is_file():
            raise ValueError(f"Missing bundled skill: {name}")
        if destination.exists() or destination.is_symlink():
            raise ValueError(f"Skill already exists; review it before replacing: {destination}")
        if any(path.is_symlink() for path in (source / name, *(source / name).rglob("*"))):
            raise ValueError(f"Bundled skill contains a symlink: {name}")
    for name, destination in zip(SKILL_NAMES, destinations):
        shutil.copytree(source / name, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return destinations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        destinations = install(args.project_root)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for destination in destinations:
        print(destination)


if __name__ == "__main__":
    main()
