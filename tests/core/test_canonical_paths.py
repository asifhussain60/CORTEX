"""
Phase 59-b: Dual Result Family / Dual OperationMode / IOrchestrator Path Tests

CORE-008: Tests written BEFORE implementation.
CORE-035: Single canonical implementation for Result, OperationMode, IOrchestrator.
CORE-011: All functions typed.
CORE-012: All public APIs documented.

GAP-59-02: cortex.core.core.result must re-export from cortex.core.result
GAP-59-03: cortex.core.interfaces.OperationMode must be deleted — use canonical
GAP-59-04: All IOrchestrator imports must use canonical path

AC_START: AC-CANONICAL-PATHS-5902
"""
from __future__ import annotations

import ast
import importlib
import subprocess
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
CORTEX_ROOT = REPO_ROOT / "cortex"


# ---------------------------------------------------------------------------
# GAP-59-02: Dual Result families
# ---------------------------------------------------------------------------
class TestSingleResultFamily:
    """59-b-T1: cortex.core.core.result must re-export from cortex.core.result."""

    def test_core_core_result_imports_from_core_result(self) -> None:
        """cortex.core.core.result must not define its own Ok/Err/Result classes."""
        secondary_path = CORTEX_ROOT / "core" / "core" / "result.py"
        if not secondary_path.exists():
            pytest.skip("cortex/core/core/result.py not found")
        tree = ast.parse(secondary_path.read_text(encoding="utf-8"))
        class_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
        own_result_classes = [
            n for n in class_names
            if n in {"Ok", "Err", "Result", "ResultMeta", "_ResultMeta"}
        ]
        assert not own_result_classes, (
            f"GAP-59-02 | cortex/core/core/result.py still defines its own classes: "
            f"{own_result_classes}. Replace with re-exports from cortex.core.result."
        )

    def test_ok_from_core_core_result_is_same_class_as_core_result(self) -> None:
        """Ok from cortex.core.result must be the same object as from cortex.core.result."""
        secondary_path = CORTEX_ROOT / "core" / "core" / "result.py"
        if not secondary_path.exists():
            pytest.skip("cortex/core/core/ eliminated (Phase 62-A) — test obsolete")
        primary = importlib.import_module("cortex.core.result")
        secondary = importlib.import_module("cortex.core.core.result")
        assert primary.Ok is secondary.Ok, (
            "GAP-59-02 | cortex.core.core.result.Ok and cortex.core.result.Ok "
            "are different classes — secondary must re-export primary."
        )
        assert primary.Err is secondary.Err, (
            "GAP-59-02 | cortex.core.core.result.Err and cortex.core.result.Err "
            "are different classes."
        )
        assert primary.Result is secondary.Result, (
            "GAP-59-02 | cortex.core.core.result.Result and cortex.core.result.Result "
            "are different classes."
        )

    def test_refactoring_orchestrator_has_no_dual_import(self) -> None:
        """RefactoringOrchestrator must not import both CoreOk/CoreErr aliases."""
        refactor_path = CORTEX_ROOT / "orchestrators" / "support" / "refactoring_orchestrator.py"
        if not refactor_path.exists():
            pytest.skip("refactoring_orchestrator.py not found")
        content = refactor_path.read_text(encoding="utf-8")
        assert "CoreOk" not in content, (
            "GAP-59-02 | refactoring_orchestrator.py still uses 'CoreOk' alias — "
            "dual Result import must be removed."
        )
        assert "CoreErr" not in content, (
            "GAP-59-02 | refactoring_orchestrator.py still uses 'CoreErr' alias — "
            "dual Result import must be removed."
        )


# ---------------------------------------------------------------------------
# GAP-59-03: Dual OperationMode
# ---------------------------------------------------------------------------
class TestSingleOperationMode:
    """59-b-T2: Only one OperationMode enum must exist in the codebase."""

    def test_interfaces_py_has_no_own_operation_mode(self) -> None:
        """cortex/core/interfaces.py must not define its own OperationMode."""
        interfaces_path = CORTEX_ROOT / "core" / "interfaces.py"
        if not interfaces_path.exists():
            pytest.skip("cortex/core/interfaces.py not found")
        tree = ast.parse(interfaces_path.read_text(encoding="utf-8"))
        class_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        ]
        assert "OperationMode" not in class_names, (
            "GAP-59-03 | cortex/core/interfaces.py still defines its own OperationMode. "
            "Delete the class and re-export from cortex.core.interfaces.i_orchestrator."
        )

    def test_single_operation_mode_definition_in_codebase(self) -> None:
        """grep 'class OperationMode' in cortex/ must return exactly 1 result."""
        result = subprocess.run(
            ["grep", "-rn", "class OperationMode", str(CORTEX_ROOT), "--include=*.py"],
            capture_output=True,
            text=True,
        )
        matches = [
            line for line in result.stdout.splitlines()
            if "__pycache__" not in line and line.strip()
        ]
        assert len(matches) == 1, (
            f"GAP-59-03 | Expected exactly 1 'class OperationMode' in cortex/; "
            f"found {len(matches)}:\n" + "\n".join(matches)
        )
        # Must be in the canonical location
        assert "i_orchestrator.py" in matches[0], (
            f"GAP-59-03 | The single OperationMode must be in "
            f"cortex/core/interfaces/i_orchestrator.py, not: {matches[0]}"
        )

    def test_operation_mode_importable_from_canonical(self) -> None:
        """OperationMode must be importable from cortex.core.interfaces.i_orchestrator."""
        try:
            from cortex.core.interfaces.i_orchestrator import OperationMode
        except ImportError as exc:
            pytest.fail(
                f"GAP-59-03 | Cannot import OperationMode from canonical path: {exc}"
            )
        assert OperationMode is not None
        # Canonical has: PLANNING, EXECUTION, VALIDATION, RECOVERY, EDUCATIONAL
        canonical_members = {m.name for m in OperationMode}
        expected = {"PLANNING", "EXECUTION", "VALIDATION", "RECOVERY", "EDUCATIONAL"}
        assert expected.issubset(canonical_members), (
            f"GAP-59-03 | Canonical OperationMode missing expected members: "
            f"{expected - canonical_members}"
        )


# ---------------------------------------------------------------------------
# GAP-59-04: IOrchestrator import paths
# ---------------------------------------------------------------------------
class TestSingleIOrchestatorPath:
    """59-b-T3: IOrchestrator must be imported from one canonical path only."""

    CANONICAL_IORCH_PATH = "cortex.core.interfaces.i_orchestrator"
    LEGACY_PATHS = [
        "cortex.core.core.interfaces",
    ]

    def test_planning_orchestrator_uses_canonical_import(self) -> None:
        """PlanningOrchestrator must import from canonical cortex.core.interfaces.i_orchestrator."""
        planning_path = (
            CORTEX_ROOT / "orchestrators" / "domain" / "planning_orchestrator.py"
        )
        if not planning_path.exists():
            pytest.skip("planning_orchestrator.py not found")
        content = planning_path.read_text(encoding="utf-8")
        assert "from cortex.core.interfaces.i_orchestrator" in content or \
               "from cortex.core.interfaces import" in content, (
                   "GAP-59-04 | planning_orchestrator.py does not import from canonical "
                   "cortex.core.interfaces.i_orchestrator path."
               )

    def test_no_file_imports_iorchestrator_from_bare_interfaces(self) -> None:
        """No cortex.* file should import IOrchestrator from cortex.core.interfaces (bare)."""
        result = subprocess.run(
            [
                "grep", "-rn",
                "from cortex.core.interfaces import.*IOrchestrator",
                str(CORTEX_ROOT),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
        )
        matches = [
            line for line in result.stdout.splitlines()
            if "__pycache__" not in line and line.strip()
        ]
        assert not matches, (
            f"GAP-59-04 | {len(matches)} file(s) import IOrchestrator from the "
            f"non-canonical path 'cortex.core.interfaces':\n" + "\n".join(matches)
        )

# AC_COMPLETE: AC-CANONICAL-PATHS-5902 (test file) ✅
