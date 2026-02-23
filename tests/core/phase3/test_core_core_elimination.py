"""
Phase 62-A RED — cortex.core.core double-nesting elimination tests.

GAP-62-01: All imports must use cortex.core.* (not cortex.core.core.*).
GAP-62-02: cortex/core/core/ directory must not exist after migration.
GAP-62-03: All 113 core/core modules must be importable via cortex.core.* path.

AC-ID: AC-PHASE62-A-001
Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-028 (snake_case)
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
CORTEX_SRC = REPO_ROOT / "cortex"
CORE_CORE_DIR = CORTEX_SRC / "core" / "core"


class TestCoreCoreMigration:
    """GAP-62-01/02/03: cortex.core.core double-nesting must be eliminated."""

    def test_no_cortex_core_core_imports_in_cortex_src(self) -> None:
        """Zero 'from cortex.core.*' imports in cortex/ production source."""
        violations: list[dict] = []
        for py_file in CORTEX_SRC.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            # Skip files inside core/core itself (they can self-reference during migration)
            if "core/core" in str(py_file):
                continue
            try:
                source = py_file.read_text(errors="replace")
            except OSError:
                continue
            try:
                tree = ast.parse(source, filename=str(py_file))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom) and node.module:
                        if node.module.startswith("cortex.core.core"):
                            violations.append({
                                "file": str(py_file.relative_to(REPO_ROOT)),
                                "line": node.lineno,
                                "import": node.module,
                            })
        if violations:
            details = "\n".join(
                f"  {v['file']}:{v['line']} (import {v['import']})"
                for v in violations[:30]
            )
            pytest.fail(
                f"Found {len(violations)} 'from cortex.core.*' imports in cortex/ source.\n"
                f"{details}\n"
                "All imports must use 'from cortex.core.*' — run Phase 62-A migration."
            )

    def test_no_cortex_core_core_imports_in_tests(self) -> None:
        """Zero 'from cortex.core.*' imports in tests/ — tests must use canonical paths."""
        tests_dir = REPO_ROOT / "tests"
        violations: list[dict] = []
        for py_file in tests_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            # Skip this test file itself
            if py_file.name == "test_core_core_elimination.py":
                continue
            try:
                source = py_file.read_text(errors="replace")
            except OSError:
                continue
            if "cortex.core.core" not in source:
                continue
            try:
                tree = ast.parse(source, filename=str(py_file))
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("cortex.core.core"):
                        violations.append({
                            "file": str(py_file.relative_to(REPO_ROOT)),
                            "line": node.lineno,
                            "import": node.module,
                        })
        if violations:
            details = "\n".join(
                f"  {v['file']}:{v['line']} (import {v['import']})"
                for v in violations[:30]
            )
            pytest.fail(
                f"Found {len(violations)} 'from cortex.core.*' imports in tests/.\n"
                f"{details}\n"
                "All test imports must use 'from cortex.core.*'."
            )

    def test_core_core_directory_does_not_exist(self) -> None:
        """cortex/core/core/ directory must not exist after Phase 62-A migration."""
        assert not CORE_CORE_DIR.exists(), (
            f"cortex/core/core/ still exists at {CORE_CORE_DIR}. "
            "Phase 62-A migration must move all files to cortex/core/ and delete the directory."
        )
