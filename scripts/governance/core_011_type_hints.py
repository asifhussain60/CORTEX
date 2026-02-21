#!/usr/bin/env python3
"""CORE-011 Pre-commit Gate — Block commits that introduce public functions without type hints.

Only checks STAGED files (new/modified), not the entire codebase.
Exits non-zero if any new public function is missing return type or argument annotations.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from typing import List, Tuple


def get_staged_python_files() -> List[str]:
    """Return list of staged .py files under cortex/."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
    )
    return [
        f
        for f in result.stdout.strip().splitlines()
        if f.startswith("cortex/") and f.endswith(".py") and "__pycache__" not in f
    ]


def check_type_hints(filepath: str) -> List[Tuple[str, int, str]]:
    """Check a file for public functions missing type hints.

    Args:
        filepath: Path to the Python file.

    Returns:
        List of (filepath, line, function_name) violations.
    """
    violations: List[Tuple[str, int, str]] = []
    try:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        return violations

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("_"):
            continue

        # Check return annotation
        if node.returns is None:
            violations.append((filepath, node.lineno, f"{node.name} — missing return type"))
            continue

        # Check argument annotations (skip self/cls)
        args = node.args.args
        if args and args[0].arg in ("self", "cls"):
            args = args[1:]
        missing = [a.arg for a in args if a.annotation is None]
        if missing:
            violations.append(
                (filepath, node.lineno, f"{node.name} — missing type hints for: {', '.join(missing)}")
            )

    return violations


def main() -> int:
    """Run CORE-011 type hint gate on staged files.

    Returns:
        0 if no violations, 1 if violations found.
    """
    staged = get_staged_python_files()
    if not staged:
        return 0

    all_violations: List[Tuple[str, int, str]] = []
    for filepath in staged:
        all_violations.extend(check_type_hints(filepath))

    if all_violations:
        print("❌ CORE-011: Public functions missing type hints in staged files:")
        for filepath, line, detail in all_violations:
            print(f"  {filepath}:{line} — {detail}")
        print(f"\n  {len(all_violations)} violation(s). Add type hints before committing.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
