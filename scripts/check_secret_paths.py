#!/usr/bin/env python3
"""Optional Git filename guard. Never open files or inspect credential values."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import PurePosixPath


def sensitive_path(name: str) -> bool:
    parts = PurePosixPath(name).parts
    lowered = [part.lower() for part in parts]
    if lowered == [".secrets", ".gitkeep"]:
        return False
    if ".secrets" in lowered:
        return True
    if any(part == ".env" or part.startswith(".env.") for part in lowered[:-1]):
        return True
    filename = lowered[-1] if lowered else ""
    if filename.startswith(".env"):
        return not filename.endswith(".example")
    return PurePosixPath(filename).suffix in {".pem", ".key", ".p12", ".pfx", ".keystore", ".kdbx"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracked", action="store_true", help="check all indexed names instead of staged additions/modifications")
    args = parser.parse_args(argv)
    command = ["git", "ls-files", "--cached", "-z"] if args.tracked else [
        "git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "--no-ext-diff", "-z"
    ]
    result = subprocess.run(command, capture_output=True, check=False)
    if result.returncode:
        print("Cannot inspect Git filenames; run from the intended repository.", file=sys.stderr)
        return 2
    names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    blocked = sorted(name for name in names if name and sensitive_path(name))
    for name in blocked:
        # repr escapes control characters in an adversarial filename.
        print(f"Blocked sensitive filename: {name!r}", file=sys.stderr)
    if blocked:
        return 1
    print("Secret-path check passed (filenames only; content was not scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
