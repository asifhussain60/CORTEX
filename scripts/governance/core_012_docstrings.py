#!/usr/bin/env python3
"""CORE-012 Pre-commit Gate — Block commits that introduce public APIs without docstrings.

Only checks STAGED files (new/modified), not the entire codebase.
Exits non-zero if any new public function or class is missing a docstring.
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


def check_docstrings(filepath: str) -> List[Tuple[str, int, str]]:
    """Check a file for public functions/classes missing docstrings.

    Args:
        filepath: Path to the Python file.

    Returns:
        List of (filepath, line, name) violations.
    """
    violations: List[Tuple[str, int, str]] = []
    try:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)
    except (SyntaxError, FileNotFoundError):
        return violations

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            if not ast.get_docstring(node):
                violations.append((filepath, node.lineno, f"class {node.name}"))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_"):
                continue
            if not ast.get_docstring(node):
                violations.append((filepath, node.lineno, f"def {node.name}"))

    return violations


def main() -> int:
    """Run CORE-012 docstring gate on staged files.

    Returns:
        0 if no violations, 1 if violations found.
    """
    staged = get_staged_python_files()
    if not staged:
        return 0

    all_violations: List[Tuple[str, int, str]] = []
    for filepath in staged:
        all_violations.extend(check_docstrings(filepath))

    if all_violations:
        print("❌ CORE-012: Public APIs missing docstrings in staged files:")
        for filepath, line, detail in all_violations:
            print(f"  {filepath}:{line} — {detail}")
        print(f"\n  {len(all_violations)} violation(s). Add docstrings before committing.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
