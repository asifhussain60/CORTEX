"""
Phase 80-A: MasterOrchestrator Decomposition — RED Tests
=========================================================
AC_START: AC-80-A-RED-2026-02-25

TDD cycle: RED phase — all tests must FAIL before any implementation.
Governs: GAP-80-A-01 (init size), GAP-80-A-02 (legacy delete),
         GAP-80-A-03 (knowledge mixin), GAP-80-A-04 (soft import count)

Run gate:
  python3 scripts/run_tests.py file tests/orchestrators/core/test_master_orchestrator_decomposition.py

All 12 tests must be RED (fail/ImportError) before phase-80-a2 begins.
"""

from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# ── Constants ──────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent.parent.parent
MASTER_FILE = REPO_ROOT / "cortex" / "orchestrators" / "core" / "master_orchestrator.py"
INIT_FILE = REPO_ROOT / "cortex" / "orchestrators" / "core" / "master_orchestrator_init.py"
KNOWLEDGE_MIXIN_FILE = (
    REPO_ROOT / "cortex" / "orchestrators" / "core" / "master_orchestrator_knowledge_mixin.py"
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_master() -> ast.Module:
    """Return parsed AST of master_orchestrator.py."""
    return ast.parse(MASTER_FILE.read_text())


def _get_init_node() -> ast.FunctionDef:
    """Return the AST node for MasterOrchestrator.__init__."""
    tree = _parse_master()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "MasterOrchestrator":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                    return item
    pytest.fail("MasterOrchestrator.__init__ not found in AST")


def _count_soft_imports() -> int:
    """Count module-level try/except ImportError blocks in master_orchestrator.py."""
    src = MASTER_FILE.read_text()
    tree = ast.parse(src)
    count = 0
    # Only count Try nodes at module level (direct children of Module)
    for node in tree.body:
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if (
                    handler.type is not None
                    and isinstance(handler.type, ast.Name)
                    and handler.type.id == "ImportError"
                ):
                    count += 1
    return count


# ══════════════════════════════════════════════════════════════════════════════
# GAP-80-A-01: __init__ size and delegation to MasterOrchestratorInitialiser
# ══════════════════════════════════════════════════════════════════════════════

class TestInitDelegation:
    """
    GAP-80-A-01 — MasterOrchestrator.__init__ must delegate to
    MasterOrchestratorInitialiser rather than containing 700+ lines of wiring.
    """

    def test_init_delegates_to_initialiser(self) -> None:
        """
        MasterOrchestratorInitialiser must be importable from
        cortex.orchestrators.core.master_orchestrator_init.

        RED: file does not exist yet → ImportError
        """
        from cortex.orchestrators.core.master_orchestrator_init import (  # noqa: F401
            MasterOrchestratorInitialiser,
        )

    def test_init_body_line_count(self) -> None:
        """
        __init__ body must contain ≤ 20 AST statements after delegation.
        The 700+ line body must be moved to MasterOrchestratorInitialiser.

        RED: current __init__ has ~140 statements → fails assertion
        """
        init_node = _get_init_node()
        stmt_count = len(init_node.body)
        assert stmt_count <= 20, (
            f"MasterOrchestrator.__init__ has {stmt_count} statements — "
            f"expected ≤ 20 after delegation to MasterOrchestratorInitialiser. "
            f"GAP-80-A-01: extract wiring to wire_all()."
        )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-80-A-02: execute_operation_legacy must be deleted
# ══════════════════════════════════════════════════════════════════════════════

class TestLegacyMethodDeleted:
    """
    GAP-80-A-02 — execute_operation_legacy (750 lines, 0 external callers)
    must be removed. It pre-dates the Stage strategy pattern and is dead weight.
    """

    def test_execute_operation_legacy_deleted(self) -> None:
        """
        MasterOrchestrator must NOT have execute_operation_legacy.

        RED: method still exists → assertion fails
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        assert not hasattr(MasterOrchestrator, "execute_operation_legacy"), (
            "execute_operation_legacy still exists on MasterOrchestrator. "
            "GAP-80-A-02: delete lines 2449–3198 (750 lines, 0 external callers)."
        )

    def test_execute_operation_legacy_no_external_callers(self) -> None:
        """
        Confirms the safety pre-condition: zero external callers.
        This test is always GREEN (it's a static audit, not a runtime assertion).
        It documents the safety evidence for the deletion.
        """
        result = subprocess.run(
            [
                "grep", "-rn", "execute_operation_legacy",
                str(REPO_ROOT / "cortex"),
                str(REPO_ROOT / "tests"),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
        )
        lines = [
            ln for ln in result.stdout.splitlines()
            if "master_orchestrator.py" not in ln
            and "def execute_operation_legacy" not in ln
            and "test_master_orchestrator_decomposition" not in ln
        ]
        assert len(lines) == 0, (
            f"Found {len(lines)} external caller(s) of execute_operation_legacy — "
            f"resolve before deleting:\n" + "\n".join(lines)
        )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-80-A-03: Knowledge methods extracted to MasterOrchestratorKnowledgeMixin
# ══════════════════════════════════════════════════════════════════════════════

class TestKnowledgeMixin:
    """
    GAP-80-A-03 — 12 knowledge/intelligence methods (~620 lines) must be
    extracted from MasterOrchestrator into MasterOrchestratorKnowledgeMixin.
    MasterOrchestrator inherits the mixin, so all callers remain unaffected.
    """

    def test_knowledge_mixin_importable(self) -> None:
        """
        MasterOrchestratorKnowledgeMixin must be importable from
        cortex.orchestrators.core.master_orchestrator_knowledge_mixin.

        RED: file does not exist yet → ImportError
        """
        from cortex.orchestrators.core.master_orchestrator_knowledge_mixin import (  # noqa: F401
            MasterOrchestratorKnowledgeMixin,
        )

    def test_knowledge_methods_on_mixin(self) -> None:
        """
        The following methods must exist on MasterOrchestratorKnowledgeMixin
        (not just on MasterOrchestrator).

        RED: class does not exist yet → ImportError / AttributeError
        """
        from cortex.orchestrators.core.master_orchestrator_knowledge_mixin import (
            MasterOrchestratorKnowledgeMixin,
        )

        required_methods = [
            "has_knowledge_repository",
            "get_knowledge_summary",
            "query_knowledge",
            "get_relevant_knowledge_for_operation",
            "has_business_knowledge_repository",
            "get_business_knowledge_summary",
            "query_business_knowledge",
            "get_relevant_business_knowledge_for_operation",
            "ask_codebase_question",
            "tech_intelligence_get_readiness",
        ]
        missing = [m for m in required_methods if not hasattr(MasterOrchestratorKnowledgeMixin, m)]
        assert not missing, (
            f"MasterOrchestratorKnowledgeMixin missing methods: {missing}. "
            "GAP-80-A-03: move knowledge/intelligence methods to the mixin."
        )

    def test_master_inherits_knowledge_mixin(self) -> None:
        """
        MasterOrchestrator must inherit MasterOrchestratorKnowledgeMixin so
        all 8 existing external callers continue to work without changes.

        RED: mixin file does not exist → ImportError
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        from cortex.orchestrators.core.master_orchestrator_knowledge_mixin import (
            MasterOrchestratorKnowledgeMixin,
        )

        assert issubclass(MasterOrchestrator, MasterOrchestratorKnowledgeMixin), (
            "MasterOrchestrator does not inherit MasterOrchestratorKnowledgeMixin. "
            "Add it to the base class list in master_orchestrator.py."
        )

    def test_query_knowledge_accessible_on_master(self) -> None:
        """
        query_knowledge must remain accessible on a MasterOrchestrator instance
        (via mixin inheritance) — existing callers must not break.

        RED: mixin not yet created → AttributeError
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        assert hasattr(mo, "query_knowledge"), (
            "query_knowledge not accessible on MasterOrchestrator instance. "
            "Inherit MasterOrchestratorKnowledgeMixin."
        )


# ══════════════════════════════════════════════════════════════════════════════
# GAP-80-A-04: Soft import count at module level
# ══════════════════════════════════════════════════════════════════════════════

class TestSoftImportCount:
    """
    GAP-80-A-04 — The 15 module-level try/except ImportError blocks make
    master_orchestrator.py fragile and unpredictable. They must be moved
    inside MasterOrchestratorInitialiser.wire_* methods where they belong.
    Maximum 3 may remain at module level (only for structural imports).
    """

    def test_soft_import_count(self) -> None:
        """
        Module-level try/except ImportError blocks in master_orchestrator.py
        must be ≤ 3 after moving optional imports into wire_* methods.

        RED: current count is 15 → fails assertion
        """
        count = _count_soft_imports()
        assert count <= 3, (
            f"master_orchestrator.py has {count} module-level try/except ImportError blocks. "
            f"Expected ≤ 3. GAP-80-A-04: move optional imports into "
            f"MasterOrchestratorInitialiser.wire_* methods."
        )


# ══════════════════════════════════════════════════════════════════════════════
# Regression Guards — these must stay GREEN through all sub-phases
# ══════════════════════════════════════════════════════════════════════════════

class TestRegressionGuards:
    """
    Zero-blast-radius contract — all existing importers and callers must work
    identically after the decomposition. These tests confirm no regressions.
    """

    def test_master_still_importable(self) -> None:
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        must succeed throughout all sub-phases.

        GREEN from the start — confirms baseline is not broken by test creation.
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator  # noqa: F401

    def test_master_instantiates(self) -> None:
        """
        MasterOrchestrator() must complete without raising any exception.
        This is the primary regression guard for all 72 external importers.

        GREEN from the start — monitors for regressions introduced during refactor.
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        assert mo is not None

    def test_health_check_returns_ok(self) -> None:
        """
        MasterOrchestrator().health_check()['status'] must equal 'ok'.

        GREEN from the start — regression guard on health reporting.
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        result = mo.health_check()
        assert isinstance(result, dict), f"health_check returned {type(result)}, expected dict"
        assert result.get("status") in ("ok", "healthy"), (
            f"health_check returned status={result.get('status')!r}, expected 'ok' or 'healthy'"
        )

    def test_execute_operation_present(self) -> None:
        """
        execute_operation (the real one, not legacy) must remain on MasterOrchestrator.

        GREEN from the start — confirms we don't accidentally delete the wrong method.
        """
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        assert hasattr(MasterOrchestrator, "execute_operation"), (
            "execute_operation missing from MasterOrchestrator — only execute_operation_legacy should be deleted."
        )

    def test_existing_test_suite_collects(self) -> None:
        """
        The existing orchestrators/core test suite must still collect without errors.
        Uses subprocess to avoid import-side-effect contamination.

        GREEN from the start — monitors for collection errors introduced by refactor.
        """
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "tests/orchestrators/core/",
                "--collect-only", "-q",
                "--continue-on-collection-errors",
                "--ignore=tests/orchestrators/core/test_master_orchestrator_decomposition.py",
            ],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        # Accept both 0 (all collected) and exit code 5 (no tests found in subset)
        assert result.returncode in (0, 5), (
            f"Test collection failed (exit {result.returncode}).\n"
            f"STDERR:\n{result.stderr[-1000:]}"
        )
