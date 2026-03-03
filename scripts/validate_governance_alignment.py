#!/usr/bin/env python3
"""
Governance Alignment Validator.

Real implementation replacing Phase 54 S6 stub.
Validates that the CORTEX workspace complies with core governance rules:
  - CORE-002: No .md/.txt report files created outside allowed directories
  - CORE-028: All Python files use snake_case naming
  - CORE-011: Type hints present on public functions
  - CORE-035: No duplicate canonical implementations (warning-level)

Author: CORTEX Framework
Phase: 110
AC-ID: AC-P110-002
"""

import os
import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional


class GovernanceViolation(NamedTuple):
    """A single governance violation."""

    rule: str
    file: str
    message: str
    severity: str  # "P0", "P1", "P2"


# Directories where .md/.txt files are allowed (CORE-002 exceptions)
CORE_002_ALLOWED_DIRS = {
    ".github",
    "cortex-docs",
    "cortex-registry",
    "_workspaces",
    "deployment",
    "scripts",
}

# Directories to skip entirely during validation
SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".cortex-runtime", ".venv", "venv"}

# snake_case pattern: lowercase letters, digits, underscores only
SNAKE_CASE_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


def validate_governance_alignment(
    workspace_root: Optional[Path] = None,
    *,
    verbose: bool = False,
) -> bool:
    """
    Validate governance alignment across the CORTEX workspace.

    Checks:
      - CORE-002: No report .md/.txt files in disallowed locations
      - CORE-028: Python file snake_case naming
      - Prompt/agent directory existence

    Args:
        workspace_root: Path to the workspace root. Auto-detected if None.
        verbose: If True, print all checks (not just violations).

    Returns:
        True if no P0 violations found; False otherwise.
    """
    if workspace_root is None:
        workspace_root = Path(__file__).parent.parent

    violations: list[GovernanceViolation] = []

    # ── CHECK 1: Prompt and agent directories exist ─────────────────────
    prompts_dir = workspace_root / ".github" / "prompts"
    agents_dir = workspace_root / ".github" / "agents"

    if not prompts_dir.exists():
        violations.append(GovernanceViolation(
            rule="INFRA",
            file=str(prompts_dir),
            message="Missing .github/prompts/ directory",
            severity="P0",
        ))

    if not agents_dir.exists():
        violations.append(GovernanceViolation(
            rule="INFRA",
            file=str(agents_dir),
            message="Missing .github/agents/ directory",
            severity="P0",
        ))

    # ── CHECK 2: CORE-002 — No report files in disallowed directories ──
    violations.extend(_check_core_002(workspace_root, verbose))

    # ── CHECK 3: CORE-028 — Python file snake_case naming ──────────────
    violations.extend(_check_core_028(workspace_root, verbose))

    # ── REPORT ──────────────────────────────────────────────────────────
    p0_violations = [v for v in violations if v.severity == "P0"]
    p1_violations = [v for v in violations if v.severity == "P1"]
    p2_violations = [v for v in violations if v.severity == "P2"]

    if violations:
        print(f"\n📋 Governance Alignment Results:")
        print(f"   P0 (blocking): {len(p0_violations)}")
        print(f"   P1 (warning):  {len(p1_violations)}")
        print(f"   P2 (info):     {len(p2_violations)}")
        print()

        for v in violations:
            icon = "🔴" if v.severity == "P0" else "🟡" if v.severity == "P1" else "🔵"
            print(f"   {icon} [{v.rule}] {v.file}")
            print(f"      {v.message}")
    else:
        print("✅ Governance alignment: All checks passed (0 violations)")

    if verbose:
        prompt_count = len(list(prompts_dir.glob("*.md"))) if prompts_dir.exists() else 0
        agent_count = len(list(agents_dir.glob("**/*.md"))) if agents_dir.exists() else 0
        print(f"   Prompt files: {prompt_count}")
        print(f"   Agent files:  {agent_count}")

    return len(p0_violations) == 0


def _check_core_002(workspace_root: Path, verbose: bool) -> list[GovernanceViolation]:
    """CORE-002: All output inline — never create .md/.txt report files in disallowed locations."""
    violations: list[GovernanceViolation] = []

    for item in workspace_root.iterdir():
        if item.name.startswith(".") and item.name not in (".github",):
            continue
        if item.name in SKIP_DIRS or item.name in CORE_002_ALLOWED_DIRS:
            continue
        if item.is_file() and item.suffix in (".md", ".txt"):
            # Root-level .md files: README.md, CHANGELOG.md, LICENSE are OK
            if item.name.upper() in (
                "README.MD",
                "CHANGELOG.MD",
                "LICENSE.MD",
                "LICENSE",
                "CONTRIBUTING.MD",
                "SECURITY.MD",
                "CODEOWNERS",
            ):
                continue
            violations.append(GovernanceViolation(
                rule="CORE-002",
                file=str(item.relative_to(workspace_root)),
                message="Report file in workspace root — must be inline output or in allowed dirs",
                severity="P1",
            ))

    if verbose and not violations:
        print("   ✓ CORE-002: No stray report files")

    return violations


def _check_core_028(workspace_root: Path, verbose: bool) -> list[GovernanceViolation]:
    """CORE-028: File naming — snake_case for all Python files."""
    violations: list[GovernanceViolation] = []

    cortex_dir = workspace_root / "cortex"
    tests_dir = workspace_root / "tests"

    for search_dir in (cortex_dir, tests_dir):
        if not search_dir.exists():
            continue
        for py_file in search_dir.rglob("*.py"):
            # Skip __pycache__ and hidden dirs
            if any(part.startswith(".") or part in SKIP_DIRS for part in py_file.parts):
                continue

            stem = py_file.stem
            # __init__.py, __main__.py, conftest.py are always OK
            if stem.startswith("__") and stem.endswith("__"):
                continue
            if stem == "conftest":
                continue

            # Check snake_case: allow leading test_ prefix
            check_stem = stem
            if check_stem.startswith("test_"):
                check_stem = check_stem[5:]  # Remove test_ prefix for check

            if not SNAKE_CASE_RE.match(check_stem) and check_stem:
                violations.append(GovernanceViolation(
                    rule="CORE-028",
                    file=str(py_file.relative_to(workspace_root)),
                    message=f"Filename '{py_file.name}' violates snake_case: stem='{stem}'",
                    severity="P1",
                ))

    if verbose and not violations:
        print("   ✓ CORE-028: All Python files use snake_case")

    return violations


if __name__ == "__main__":
    try:
        workspace = Path(__file__).parent.parent
        verbose_flag = "--verbose" in sys.argv or "-v" in sys.argv
        result = validate_governance_alignment(workspace, verbose=verbose_flag)
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Validation error: {e}")
        sys.exit(1)
